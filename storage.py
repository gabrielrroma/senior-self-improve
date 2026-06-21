import json
import os
from uuid import uuid4

from date_utils import to_int, today_key
from reward_service import normalize_reward_cost
from routine_service import build_task_summary, default_gamification, normalize_gamification
from settings import CATEGORIES, DATA_DIR, DATA_FILE, PRIORITY_POINTS


class RoutineStorage:
    def __init__(self, data_dir=DATA_DIR, data_file=DATA_FILE):
        self.data_dir = data_dir
        self.data_file = data_file

    def empty_state(self):
        return {
            "tasks": [],
            "history": [],
            "archived_days": [],
            "gamification": default_gamification(),
            "current_day": today_key(),
            "points_total": 0,
            "points_spent": 0,
            "rewards": [],
            "reward_redemptions": [],
        }

    def load(self):
        os.makedirs(self.data_dir, exist_ok=True)

        if not os.path.exists(self.data_file):
            return self.empty_state(), None

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return self.empty_state(), "Nao foi possivel carregar os dados salvos."

        state = self.empty_state()
        state["points_total"] = to_int(data.get("points_total", data.get("points", 0)))
        raw_points_spent = data.get("points_spent")
        state["points_spent"] = max(0, to_int(raw_points_spent, 0))
        state["gamification"] = normalize_gamification(data.get("gamification", {}))
        state["current_day"] = self.infer_saved_day(data)

        for raw_task in data.get("tasks", []):
            task = self.normalize_task(raw_task)
            if task is not None:
                state["tasks"].append(task)

        history_by_date = {}
        for raw_entry in data.get("history", []):
            entry = self.normalize_history_entry(raw_entry)
            if entry is not None:
                history_by_date[entry["date"]] = entry

        state["history"] = sorted(history_by_date.values(), key=lambda entry: entry["date"])

        archived_by_date = {}
        for raw_entry in data.get("archived_days", []):
            entry = self.normalize_archive_entry(raw_entry)
            if entry is not None:
                archived_by_date[entry["date"]] = entry

        state["archived_days"] = sorted(archived_by_date.values(), key=lambda entry: entry["date"])

        rewards_by_id = {}
        for raw_reward in data.get("rewards", []):
            reward = self.normalize_reward(raw_reward)
            if reward is not None:
                rewards_by_id[reward["id"]] = reward

        state["rewards"] = sorted(rewards_by_id.values(), key=lambda reward: (reward["cost"], reward["title"].lower()))

        redemptions_by_id = {}
        for raw_redemption in data.get("reward_redemptions", data.get("redemptions", [])):
            redemption = self.normalize_reward_redemption(raw_redemption)
            if redemption is not None:
                redemptions_by_id[redemption["id"]] = redemption

        state["reward_redemptions"] = sorted(
            redemptions_by_id.values(),
            key=lambda redemption: redemption["redeemed_at"],
        )
        if raw_points_spent is None:
            state["points_spent"] = sum(entry["cost"] for entry in state["reward_redemptions"])
        return state, None

    def save(
        self,
        current_day,
        tasks,
        history,
        archived_days,
        gamification,
        points_total,
        rewards=None,
        reward_redemptions=None,
        points_spent=0,
    ):
        os.makedirs(self.data_dir, exist_ok=True)
        payload = {
            "current_day": current_day,
            "tasks": tasks,
            "history": history,
            "archived_days": archived_days,
            "gamification": gamification,
            "points_total": points_total,
            "points_spent": max(0, to_int(points_spent)),
            "rewards": rewards or [],
            "reward_redemptions": reward_redemptions or [],
        }

        temp_file = f"{self.data_file}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
            os.replace(temp_file, self.data_file)
        except OSError as error:
            return f"Nao foi possivel salvar os dados.\n\n{error}"

        return None

    def infer_saved_day(self, data):
        saved_day = str(data.get("current_day", data.get("last_active_date", ""))).strip()
        if saved_day:
            return saved_day

        task_dates = []
        for raw_task in data.get("tasks", []):
            if not isinstance(raw_task, dict):
                continue
            for key in ("created_at", "completed_at"):
                value = raw_task.get(key)
                if value:
                    task_dates.append(str(value))

        if task_dates:
            return max(task_dates)

        history_dates = [
            str(entry.get("date"))
            for entry in data.get("history", [])
            if isinstance(entry, dict) and entry.get("date")
        ]
        if history_dates:
            return max(history_dates)

        return today_key()

    def normalize_task(self, raw_task):
        if not isinstance(raw_task, dict):
            return None

        title = str(raw_task.get("title", raw_task.get("task", ""))).strip()
        if not title:
            return None

        priority = raw_task.get("priority", "Media")
        if priority not in PRIORITY_POINTS:
            priority = "Media"

        category = raw_task.get("category", "Outros")
        if category not in CATEGORIES:
            category = "Outros"

        done = bool(raw_task.get("done", False))
        awarded = to_int(raw_task.get("points_awarded"), PRIORITY_POINTS[priority] if done else 0)

        return {
            "id": raw_task.get("id") or uuid4().hex,
            "title": title,
            "done": done,
            "priority": priority,
            "category": category,
            "created_at": raw_task.get("created_at") or today_key(),
            "completed_at": raw_task.get("completed_at") if done else None,
            "points_awarded": awarded if done else 0,
            "pinned": bool(raw_task.get("pinned", False)),
        }

    def normalize_history_entry(self, raw_entry):
        if not isinstance(raw_entry, dict):
            return None

        entry_date = str(raw_entry.get("date", "")).strip()
        if not entry_date:
            return None

        completed = max(0, to_int(raw_entry.get("completed_tasks", raw_entry.get("completed", 0))))
        total = max(0, to_int(raw_entry.get("total_tasks", raw_entry.get("total", 0))))
        points = max(0, to_int(raw_entry.get("points_earned", raw_entry.get("points", 0))))

        if "completion_percentage" in raw_entry:
            percentage = to_int(raw_entry.get("completion_percentage"))
        elif total:
            percentage = int((completed / total) * 100)
        else:
            percentage = 0

        percentage = max(0, min(100, percentage))

        return {
            "date": entry_date,
            "completed_tasks": completed,
            "total_tasks": total,
            "points_earned": points,
            "completion_percentage": percentage,
        }

    def normalize_archive_entry(self, raw_entry):
        if not isinstance(raw_entry, dict):
            return None

        entry_date = str(raw_entry.get("date", "")).strip()
        if not entry_date:
            return None

        tasks = []
        for raw_task in raw_entry.get("tasks", []):
            task = self.normalize_task(raw_task)
            if task is not None:
                tasks.append(task)

        raw_summary = raw_entry.get("summary", {})
        if isinstance(raw_summary, dict):
            summary_data = dict(raw_summary)
            summary_data.setdefault("date", entry_date)
            summary = self.normalize_history_entry(summary_data)
        else:
            summary = None

        if summary is None:
            summary = build_task_summary(tasks, entry_date)

        return {
            "date": entry_date,
            "summary": summary,
            "tasks": tasks,
        }

    def normalize_reward(self, raw_reward):
        if not isinstance(raw_reward, dict):
            return None

        title = str(raw_reward.get("title", raw_reward.get("name", ""))).strip()
        if not title:
            return None

        return {
            "id": raw_reward.get("id") or uuid4().hex,
            "title": title,
            "description": str(raw_reward.get("description", "")).strip(),
            "cost": normalize_reward_cost(raw_reward.get("cost", raw_reward.get("points_cost", 10))),
            "created_at": raw_reward.get("created_at") or today_key(),
        }

    def normalize_reward_redemption(self, raw_redemption):
        if not isinstance(raw_redemption, dict):
            return None

        title = str(raw_redemption.get("reward_title", raw_redemption.get("title", ""))).strip()
        if not title:
            return None

        redeemed_at = str(raw_redemption.get("redeemed_at", raw_redemption.get("date", ""))).strip()
        if not redeemed_at:
            redeemed_at = today_key()

        return {
            "id": raw_redemption.get("id") or uuid4().hex,
            "reward_id": raw_redemption.get("reward_id"),
            "reward_title": title,
            "cost": normalize_reward_cost(raw_redemption.get("cost", raw_redemption.get("points_cost", 10))),
            "redeemed_at": redeemed_at,
        }
