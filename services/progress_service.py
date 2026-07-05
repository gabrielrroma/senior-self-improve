from datetime import date, timedelta

from models.settings import (
    DEFAULT_WEEKLY_GOAL_BONUS_POINTS,
    DEFAULT_WEEKLY_GOAL_TASKS,
    MAX_WEEKLY_GOAL_TASKS,
    MIN_WEEKLY_GOAL_TASKS,
)
from .date_utils import format_date, to_int, today_key


ACHIEVEMENTS = (
    {
        "id": "first_task_completed",
        "title": "Primeira tarefa",
        "description": "Concluir a primeira tarefa.",
        "target": 1,
    },
    {
        "id": "seven_day_streak",
        "title": "7 dias seguidos",
        "description": "Manter 7 dias seguidos de meta diaria.",
        "target": 7,
    },
    {
        "id": "hundred_tasks_completed",
        "title": "100 tarefas",
        "description": "Concluir 100 tarefas no historico.",
        "target": 100,
    },
    {
        "id": "first_perfect_week",
        "title": "Semana perfeita",
        "description": "Fechar 7 dias da mesma semana com 100%.",
        "target": 1,
    },
    {
        "id": "five_hundred_points",
        "title": "500 pontos",
        "description": "Acumular 500 pontos totais.",
        "target": 500,
    },
)


def parse_date_key(value):
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def get_week_bounds(value):
    current = parse_date_key(value) or date.today()
    start = current - timedelta(days=current.weekday())
    end = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


def iter_date_keys(start_key, end_key):
    start = parse_date_key(start_key)
    end = parse_date_key(end_key)
    if start is None or end is None or start > end:
        return []

    days = []
    current = start
    while current <= end:
        days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def get_weekly_goal_tasks(gamification):
    goal = to_int(gamification.get("weekly_goal_tasks"), DEFAULT_WEEKLY_GOAL_TASKS)
    return max(MIN_WEEKLY_GOAL_TASKS, min(MAX_WEEKLY_GOAL_TASKS, goal))


def get_weekly_goal_bonus_points(gamification):
    return max(0, to_int(gamification.get("weekly_goal_bonus_points"), DEFAULT_WEEKLY_GOAL_BONUS_POINTS))


def build_weekly_stats(history, archived_days, tasks, current_day, gamification):
    week_start, week_end = get_week_bounds(current_day)
    week_dates = iter_date_keys(week_start, week_end)
    week_date_set = set(week_dates)
    summaries = build_summary_map(history)
    entries = [summaries.get(day, empty_summary(day)) for day in week_dates]

    completed_tasks = sum(entry["completed_tasks"] for entry in entries)
    total_tasks = sum(entry["total_tasks"] for entry in entries)
    points_earned = sum(entry["points_earned"] for entry in entries)
    completion_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    goal_tasks = get_weekly_goal_tasks(gamification)
    goal_progress = int((min(completed_tasks, goal_tasks) / goal_tasks) * 100) if goal_tasks else 0
    bonus_points = get_weekly_goal_bonus_points(gamification)
    current_award = get_weekly_award(gamification, week_start)

    return {
        "week_start": week_start,
        "week_end": week_end,
        "week_label": f"{format_date(week_start)} a {format_date(week_end)}",
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "points_earned": points_earned,
        "completion_percentage": completion_percentage,
        "best_day": build_best_day(entries),
        "top_category": build_top_category(archived_days, tasks, current_day, week_date_set),
        "goal_tasks": goal_tasks,
        "goal_label": f"{completed_tasks}/{goal_tasks} tarefas",
        "goal_progress": goal_progress,
        "goal_complete": completed_tasks >= goal_tasks,
        "bonus_points": bonus_points,
        "bonus_awarded": current_award is not None,
        "bonus_label": f"{bonus_points} pts",
        "days": entries,
    }


def build_summary_map(history):
    summaries = {}
    for raw_entry in history:
        entry = normalize_summary_entry(raw_entry)
        if entry is not None:
            summaries[entry["date"]] = entry
    return summaries


def normalize_summary_entry(raw_entry):
    if not isinstance(raw_entry, dict):
        return None

    entry_date = str(raw_entry.get("date", "")).strip()
    if not entry_date:
        return None

    completed = max(0, to_int(raw_entry.get("completed_tasks")))
    total = max(0, to_int(raw_entry.get("total_tasks")))
    points = max(0, to_int(raw_entry.get("points_earned")))
    percentage = max(0, min(100, to_int(raw_entry.get("completion_percentage"))))

    return {
        "date": entry_date,
        "date_label": format_date(entry_date),
        "completed_tasks": completed,
        "total_tasks": total,
        "points_earned": points,
        "completion_percentage": percentage,
    }


def empty_summary(entry_date):
    return {
        "date": entry_date,
        "date_label": format_date(entry_date),
        "completed_tasks": 0,
        "total_tasks": 0,
        "points_earned": 0,
        "completion_percentage": 0,
    }


def build_best_day(entries):
    active_entries = [
        entry
        for entry in entries
        if entry["total_tasks"] > 0 or entry["completed_tasks"] > 0 or entry["points_earned"] > 0
    ]
    if not active_entries:
        return {
            "date": None,
            "date_label": "Sem dados",
            "completed_tasks": 0,
            "points_earned": 0,
            "completion_percentage": 0,
            "label": "Sem dados",
        }

    best = max(
        active_entries,
        key=lambda entry: (
            entry["points_earned"],
            entry["completed_tasks"],
            entry["completion_percentage"],
            entry["date"],
        ),
    )
    completed_label = format_task_count(best["completed_tasks"])

    return {
        "date": best["date"],
        "date_label": best["date_label"],
        "completed_tasks": best["completed_tasks"],
        "points_earned": best["points_earned"],
        "completion_percentage": best["completion_percentage"],
        "label": f"{best['date_label']} - {best['points_earned']} pts, {completed_label}",
    }


def build_top_category(archived_days, tasks, current_day, week_dates):
    category_counts = count_completed_categories(archived_days, tasks, current_day, week_dates)
    if not category_counts:
        return {
            "name": "Sem dados",
            "completed_tasks": 0,
            "label": "Sem dados",
        }

    category, completed = sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return {
        "name": category,
        "completed_tasks": completed,
        "label": f"{category}: {format_task_count(completed)}",
    }


def count_completed_categories(archived_days, tasks, current_day, week_dates):
    counts = {}
    seen_tasks = set()

    def add_tasks(raw_tasks, fallback_date):
        if not isinstance(raw_tasks, list):
            return

        for task in raw_tasks:
            if not isinstance(task, dict) or not task.get("done"):
                continue

            completed_at = str(task.get("completed_at") or fallback_date or "").strip()
            if completed_at not in week_dates:
                continue

            task_id = str(task.get("id") or task.get("title") or "").strip()
            seen_key = (task_id, completed_at)
            if seen_key in seen_tasks:
                continue
            seen_tasks.add(seen_key)

            category = str(task.get("category") or "Outros").strip() or "Outros"
            counts[category] = counts.get(category, 0) + 1

    for archived_day in archived_days:
        if not isinstance(archived_day, dict):
            continue
        archive_date = str(archived_day.get("date", "")).strip()
        add_tasks(archived_day.get("tasks", []), archive_date)

    add_tasks(tasks, current_day)
    return counts


def sync_weekly_goal_bonus(gamification, weekly_stats, current_day, points_total):
    week_start = weekly_stats["week_start"]
    awards = list(gamification.get("weekly_goal_awards", []))
    existing_award = get_weekly_award(gamification, week_start)
    bonus_points = weekly_stats["bonus_points"]
    messages = []

    if weekly_stats["goal_complete"] and existing_award is None and bonus_points > 0:
        awards.append(
            {
                "week_start": week_start,
                "points": bonus_points,
                "awarded_at": current_day or today_key(),
            }
        )
        gamification["weekly_goal_awards"] = sorted(awards, key=lambda award: award["week_start"])
        messages.append(f"Meta semanal concluida. Bonus de {bonus_points} pts recebido.")
        return points_total + bonus_points, True, messages

    if (not weekly_stats["goal_complete"] or bonus_points <= 0) and existing_award is not None:
        removed_points = max(0, to_int(existing_award.get("points"), bonus_points))
        gamification["weekly_goal_awards"] = [
            award for award in awards if award.get("week_start") != week_start
        ]
        messages.append("Bonus semanal removido: meta semanal ficou abaixo do alvo.")
        return max(0, points_total - removed_points), True, messages

    return points_total, False, messages


def get_weekly_award(gamification, week_start):
    for award in gamification.get("weekly_goal_awards", []):
        if isinstance(award, dict) and award.get("week_start") == week_start:
            return award
    return None


def sync_achievements(gamification, history, points_total, current_day, display_streak=None):
    progress = build_achievement_progress(history, gamification, points_total, display_streak)
    unlocked = get_unlocked_achievement_map(gamification)
    messages = []

    for achievement in ACHIEVEMENTS:
        achievement_id = achievement["id"]
        if achievement_id in unlocked:
            continue
        if progress.get(achievement_id, 0) < achievement["target"]:
            continue

        unlocked[achievement_id] = {
            "id": achievement_id,
            "unlocked_at": current_day or today_key(),
        }
        messages.append(f"Conquista desbloqueada: {achievement['title']}.")

    if not messages:
        return False, []

    gamification["unlocked_achievements"] = sorted(unlocked.values(), key=lambda item: item["id"])
    return True, messages


def build_achievements_view(gamification, history, points_total, display_streak=None):
    progress = build_achievement_progress(history, gamification, points_total, display_streak)
    unlocked = get_unlocked_achievement_map(gamification)
    achievements = []

    for achievement in ACHIEVEMENTS:
        achievement_id = achievement["id"]
        target = achievement["target"]
        progress_value = max(0, progress.get(achievement_id, 0))
        progress_percentage = int((min(progress_value, target) / target) * 100) if target else 0
        unlocked_entry = unlocked.get(achievement_id)

        achievements.append(
            {
                **achievement,
                "unlocked": unlocked_entry is not None,
                "unlocked_at": unlocked_entry.get("unlocked_at") if unlocked_entry else None,
                "unlocked_label": format_date(unlocked_entry.get("unlocked_at")) if unlocked_entry else "",
                "progress": progress_value,
                "progress_label": f"{min(progress_value, target)}/{target}",
                "progress_percentage": progress_percentage,
                "status_label": "Desbloqueada" if unlocked_entry else "Bloqueada",
            }
        )

    return achievements


def build_achievement_summary(achievements):
    unlocked_count = sum(1 for achievement in achievements if achievement["unlocked"])
    total_count = len(achievements)
    return {
        "unlocked_count": unlocked_count,
        "total_count": total_count,
        "label": f"{unlocked_count}/{total_count} desbloqueadas",
    }


def build_achievement_progress(history, gamification, points_total, display_streak=None):
    total_completed = get_total_completed_tasks(history)
    best_streak = max(
        to_int(gamification.get("best_streak")),
        to_int(gamification.get("streak_count")),
        to_int(display_streak),
    )

    return {
        "first_task_completed": total_completed,
        "seven_day_streak": best_streak,
        "hundred_tasks_completed": total_completed,
        "first_perfect_week": 1 if has_perfect_week(history) else 0,
        "five_hundred_points": max(0, to_int(points_total)),
    }


def get_total_completed_tasks(history):
    summaries = build_summary_map(history)
    return sum(entry["completed_tasks"] for entry in summaries.values())


def has_perfect_week(history):
    summaries = build_summary_map(history)
    if not summaries:
        return False

    dates = [parse_date_key(entry_date) for entry_date in summaries]
    dates = sorted(entry_date for entry_date in dates if entry_date is not None)
    if not dates:
        return False

    first_week_start = dates[0] - timedelta(days=dates[0].weekday())
    last_week_start = dates[-1] - timedelta(days=dates[-1].weekday())
    current_week_start = first_week_start

    while current_week_start <= last_week_start:
        week_dates = [
            (current_week_start + timedelta(days=offset)).isoformat()
            for offset in range(7)
        ]
        if all(is_perfect_day(summaries.get(day)) for day in week_dates):
            return True
        current_week_start += timedelta(days=7)

    return False


def is_perfect_day(entry):
    return (
        isinstance(entry, dict)
        and entry["total_tasks"] > 0
        and entry["completion_percentage"] >= 100
    )


def get_unlocked_achievement_map(gamification):
    unlocked = {}
    for achievement in gamification.get("unlocked_achievements", []):
        if not isinstance(achievement, dict):
            continue
        achievement_id = str(achievement.get("id", "")).strip()
        if not achievement_id:
            continue
        unlocked[achievement_id] = {
            "id": achievement_id,
            "unlocked_at": str(achievement.get("unlocked_at", today_key())).strip() or today_key(),
        }
    return unlocked


def format_task_count(value):
    value = max(0, to_int(value))
    if value == 1:
        return "1 tarefa"
    return f"{value} tarefas"
