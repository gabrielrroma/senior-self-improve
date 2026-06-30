from uuid import uuid4

from date_utils import format_day_count, previous_day_key, to_int, today_key
from settings import (
    CATEGORIES,
    DEFAULT_DAILY_GOAL_POINTS,
    DEFAULT_WEEKLY_GOAL_BONUS_POINTS,
    DEFAULT_WEEKLY_GOAL_TASKS,
    MAX_DAILY_GOAL_POINTS,
    MAX_WEEKLY_GOAL_TASKS,
    MIN_DAILY_GOAL_POINTS,
    MIN_WEEKLY_GOAL_TASKS,
    PRIORITY_ORDER,
    PRIORITY_POINTS,
    XP_PER_LEVEL,
)


def default_gamification():
    return {
        "daily_goal_points": DEFAULT_DAILY_GOAL_POINTS,
        "weekly_goal_tasks": DEFAULT_WEEKLY_GOAL_TASKS,
        "weekly_goal_bonus_points": DEFAULT_WEEKLY_GOAL_BONUS_POINTS,
        "weekly_goal_awards": [],
        "unlocked_achievements": [],
        "streak_count": 0,
        "best_streak": 0,
        "last_streak_date": None,
    }


def normalize_gamification(raw_gamification):
    if not isinstance(raw_gamification, dict):
        raw_gamification = {}

    goal = to_int(raw_gamification.get("daily_goal_points"), DEFAULT_DAILY_GOAL_POINTS)
    goal = max(MIN_DAILY_GOAL_POINTS, min(MAX_DAILY_GOAL_POINTS, goal))

    weekly_goal = to_int(raw_gamification.get("weekly_goal_tasks"), DEFAULT_WEEKLY_GOAL_TASKS)
    weekly_goal = max(MIN_WEEKLY_GOAL_TASKS, min(MAX_WEEKLY_GOAL_TASKS, weekly_goal))

    weekly_bonus = max(
        0,
        to_int(raw_gamification.get("weekly_goal_bonus_points"), DEFAULT_WEEKLY_GOAL_BONUS_POINTS),
    )

    streak_count = max(0, to_int(raw_gamification.get("streak_count")))
    best_streak = max(streak_count, to_int(raw_gamification.get("best_streak")))
    last_streak_date = raw_gamification.get("last_streak_date") or None
    if last_streak_date is not None:
        last_streak_date = str(last_streak_date)

    return {
        "daily_goal_points": goal,
        "weekly_goal_tasks": weekly_goal,
        "weekly_goal_bonus_points": weekly_bonus,
        "weekly_goal_awards": normalize_weekly_goal_awards(raw_gamification.get("weekly_goal_awards", [])),
        "unlocked_achievements": normalize_unlocked_achievements(
            raw_gamification.get("unlocked_achievements", raw_gamification.get("achievements", []))
        ),
        "streak_count": streak_count,
        "best_streak": best_streak,
        "last_streak_date": last_streak_date,
    }


def normalize_weekly_goal_awards(raw_awards):
    if not isinstance(raw_awards, list):
        return []

    awards_by_week = {}
    for raw_award in raw_awards:
        if not isinstance(raw_award, dict):
            continue

        week_start = str(raw_award.get("week_start", "")).strip()
        if not week_start:
            continue

        points = max(0, to_int(raw_award.get("points"), DEFAULT_WEEKLY_GOAL_BONUS_POINTS))
        awarded_at = str(raw_award.get("awarded_at", week_start)).strip() or week_start
        awards_by_week[week_start] = {
            "week_start": week_start,
            "points": points,
            "awarded_at": awarded_at,
        }

    return sorted(awards_by_week.values(), key=lambda award: award["week_start"])


def normalize_unlocked_achievements(raw_achievements):
    if not isinstance(raw_achievements, list):
        return []

    achievements_by_id = {}
    for raw_achievement in raw_achievements:
        if isinstance(raw_achievement, dict):
            achievement_id = str(raw_achievement.get("id", "")).strip()
            unlocked_at = str(raw_achievement.get("unlocked_at", today_key())).strip() or today_key()
        else:
            achievement_id = str(raw_achievement).strip()
            unlocked_at = today_key()

        if not achievement_id:
            continue

        achievements_by_id[achievement_id] = {
            "id": achievement_id,
            "unlocked_at": unlocked_at,
        }

    return sorted(achievements_by_id.values(), key=lambda achievement: achievement["id"])


def create_task(title, priority, category, pinned=False):
    if priority not in PRIORITY_POINTS:
        priority = "Media"

    if category not in CATEGORIES:
        category = "Outros"

    return {
        "id": uuid4().hex,
        "title": title,
        "done": False,
        "priority": priority,
        "category": category,
        "created_at": today_key(),
        "completed_at": None,
        "points_awarded": 0,
        "pinned": bool(pinned),
    }


def update_task(task, title, priority, category):
    task["title"] = title
    task["priority"] = priority if priority in PRIORITY_POINTS else "Media"
    task["category"] = category if category in CATEGORIES else "Outros"


def set_task_pinned(task, pinned):
    task["pinned"] = bool(pinned)


def carry_pinned_tasks_to_day(tasks, day):
    pinned_tasks = []

    for task in tasks:
        if not task.get("pinned", False):
            continue

        next_task = dict(task)
        next_task["done"] = False
        next_task["created_at"] = day
        next_task["completed_at"] = None
        next_task["points_awarded"] = 0
        next_task["pinned"] = True
        pinned_tasks.append(next_task)

    return pinned_tasks


def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def get_task_points(task):
    return PRIORITY_POINTS.get(task.get("priority", "Media"), PRIORITY_POINTS["Media"])


def complete_task(task, points_total):
    points = get_task_points(task)
    task["done"] = True
    task["completed_at"] = today_key()
    task["points_awarded"] = points
    return points_total + points, points


def reopen_task(task, points_total):
    points = to_int(task.get("points_awarded"), get_task_points(task))
    task["done"] = False
    task["completed_at"] = None
    task["points_awarded"] = 0
    return max(0, points_total - points), points


def delete_task(tasks, task, points_total):
    if task["done"]:
        points = to_int(task.get("points_awarded"), get_task_points(task))
        points_total = max(0, points_total - points)

    return [item for item in tasks if item["id"] != task["id"]], points_total


def get_daily_goal_points(gamification):
    return max(
        MIN_DAILY_GOAL_POINTS,
        min(MAX_DAILY_GOAL_POINTS, to_int(gamification.get("daily_goal_points"), DEFAULT_DAILY_GOAL_POINTS)),
    )


def get_level_info(points_total):
    xp_total = max(0, points_total)
    level = (xp_total // XP_PER_LEVEL) + 1
    xp_current = xp_total % XP_PER_LEVEL
    xp_needed = XP_PER_LEVEL
    progress = int((xp_current / xp_needed) * 100) if xp_needed else 0

    return {
        "xp_total": xp_total,
        "level": level,
        "xp_current": xp_current,
        "xp_needed": xp_needed,
        "xp_to_next": xp_needed - xp_current,
        "progress": progress,
    }


def is_daily_goal_complete(gamification, summary):
    return summary["points_earned"] >= get_daily_goal_points(gamification)


def calculate_display_streak(gamification, summary):
    streak_count = max(0, to_int(gamification.get("streak_count")))
    last_streak_date = gamification.get("last_streak_date")

    if last_streak_date == summary["date"]:
        return streak_count

    if not is_daily_goal_complete(gamification, summary):
        return streak_count if last_streak_date == previous_day_key(summary["date"]) else 0

    if last_streak_date == previous_day_key(summary["date"]):
        return streak_count + 1

    return 1


def build_motivation_message(gamification, summary):
    goal = get_daily_goal_points(gamification)

    if summary["total_tasks"] == 0:
        return "Comece com uma tarefa simples para abrir o dia."

    if summary["points_earned"] >= goal:
        return "Meta diaria concluida. Agora e manter o ritmo."

    if summary["completion_percentage"] == 0:
        return "O primeiro passo ainda esta na mesa. Escolha uma tarefa pequena."

    if summary["completion_percentage"] >= 100:
        return "Dia completo. Belo fechamento de rotina."

    if summary["completion_percentage"] >= 50:
        return "Metade do caminho passou. Mais uma tarefa aproxima a meta."

    return "Bom comeco. Cada conclusao empurra o dia para frente."


def apply_streak_for_summary(gamification, summary):
    goal_complete = is_daily_goal_complete(gamification, summary)
    previous_streak = max(0, to_int(gamification.get("streak_count")))
    last_streak_date = gamification.get("last_streak_date")

    if not goal_complete:
        if previous_streak > 0:
            gamification["streak_count"] = 0
            return "Streak perdida: a meta diaria nao foi concluida."
        return None

    if last_streak_date == summary["date"]:
        return None

    if last_streak_date == previous_day_key(summary["date"]):
        next_streak = previous_streak + 1
    else:
        next_streak = 1

    gamification["streak_count"] = next_streak
    gamification["best_streak"] = max(to_int(gamification.get("best_streak")), next_streak)
    gamification["last_streak_date"] = summary["date"]
    return f"Streak atual: {format_day_count(next_streak)}."


def reset_streak_if_gap(gamification, previous_day, current_day):
    if previous_day == previous_day_key(current_day):
        return None

    if to_int(gamification.get("streak_count")) <= 0:
        return None

    gamification["streak_count"] = 0
    return "Streak perdida: houve dia sem registro."


def build_task_summary(tasks, summary_date):
    total = len(tasks)
    completed = sum(1 for task in tasks if task["done"])
    points_earned = sum(
        to_int(task.get("points_awarded"), get_task_points(task))
        for task in tasks
        if task["done"] and task.get("completed_at") == summary_date
    )
    percentage = int((completed / total) * 100) if total else 0

    return {
        "date": summary_date,
        "completed_tasks": completed,
        "total_tasks": total,
        "points_earned": points_earned,
        "completion_percentage": percentage,
    }


def build_daily_summary(tasks, current_day):
    return build_task_summary(tasks, current_day)


def upsert_history_summary(history, summary):
    history_by_date = {}

    for entry in history:
        history_by_date[entry["date"]] = entry

    history_by_date[summary["date"]] = summary
    return sorted(history_by_date.values(), key=lambda entry: entry["date"])


def upsert_archive_day(archived_days, archive_date, summary, tasks):
    archived_by_date = {}

    for entry in archived_days:
        archived_by_date[entry["date"]] = entry

    archived_by_date[archive_date] = {
        "date": archive_date,
        "summary": summary,
        "tasks": [dict(task) for task in tasks],
    }
    return sorted(archived_by_date.values(), key=lambda entry: entry["date"])


def get_visible_tasks(tasks, selected_filter):
    visible_tasks = list(tasks)

    if selected_filter == "Pendentes":
        visible_tasks = [task for task in visible_tasks if not task["done"]]
    elif selected_filter == "Concluidas":
        visible_tasks = [task for task in visible_tasks if task["done"]]

    return sorted(
        visible_tasks,
        key=lambda task: (
            task["done"],
            not task.get("pinned", False),
            PRIORITY_ORDER.get(task["priority"], 1),
            task.get("created_at", ""),
            task["title"].lower(),
        ),
    )
