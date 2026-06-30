import json
import os
import shutil
from uuid import uuid4

from date_utils import to_int, today_key
from reward_service import normalize_reward_cost, normalize_reward_image_url
from routine_service import build_task_summary, default_gamification, normalize_gamification
from settings import CATEGORIES, DATA_DIR, DATA_FILE, DATA_FILES, PRIORITY_POINTS


SCHEMA_VERSION = 1


class RoutineStorage:
    def __init__(self, data_dir=DATA_DIR, data_file=DATA_FILE, data_files=None):
        self.data_dir = data_dir
        self.data_files = self.build_data_files(data_dir, data_files)

        uses_default_data_file = data_file == DATA_FILE
        if not uses_default_data_file:
            self.data_files["tasks"] = data_file

        self.data_file = self.data_files["tasks"]
        self.legacy_data_file = self.data_file if uses_default_data_file else data_file
        self.loaded_legacy_file = False

    def build_data_files(self, data_dir, data_files):
        default_filenames = {
            key: os.path.basename(path)
            for key, path in DATA_FILES.items()
        }
        files = {
            key: os.path.join(data_dir, filename)
            for key, filename in default_filenames.items()
        }
        if data_files:
            files.update(data_files)
        return files

    def default_profile(self):
        return {
            "name": "",
            "avatar": "spark",
            "avatar_url": "",
            "theme": "system",
            "accent_color": "green",
        }

    def empty_state(self):
        return {
            "profile": self.default_profile(),
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
        self.loaded_legacy_file = False

        has_split_files = any(
            os.path.exists(path)
            for key, path in self.data_files.items()
            if key != "tasks"
        )

        if not has_split_files and os.path.exists(self.legacy_data_file):
            data, error = self.read_json_file(self.legacy_data_file)
            if error:
                return self.empty_state(), "Nao foi possivel carregar os dados salvos."
            if self.is_legacy_payload(data):
                self.loaded_legacy_file = True
                return self.normalize_state(data), None

        return self.load_split_state()

    def load_split_state(self):
        payloads = {}
        failed_files = []

        for key, path in self.data_files.items():
            payload, error = self.read_json_file(path)
            if error:
                failed_files.append(os.path.basename(path))
                payload = {}
            payloads[key] = payload

        tasks_payload = payloads.get("tasks", {})
        legacy_fallback = tasks_payload if self.is_legacy_payload(tasks_payload) else {}
        if legacy_fallback:
            self.loaded_legacy_file = True

        state = self.normalize_state(self.merge_split_payloads(payloads, legacy_fallback))
        if failed_files:
            filenames = ", ".join(failed_files)
            return state, f"Nao foi possivel carregar alguns arquivos de dados: {filenames}."
        return state, None

    def read_json_file(self, path):
        if not os.path.exists(path):
            return {}, None

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}, "load_error"

        if not isinstance(data, (dict, list)):
            return {}, "load_error"

        return data, None

    def merge_split_payloads(self, payloads, legacy_fallback):
        legacy_fallback = self.as_dict(legacy_fallback)
        profile_payload = self.as_dict(payloads.get("profile"))
        tasks_payload = payloads.get("tasks", {})
        rewards_payload = payloads.get("rewards", {})
        history_payload = payloads.get("history", {})
        settings_payload = self.as_dict(payloads.get("settings"))

        tasks_data = self.as_dict(tasks_payload)
        wallet = self.as_dict(profile_payload.get("wallet"))

        settings_data = self.as_dict(settings_payload.get("settings"))
        if not settings_data:
            settings_data = settings_payload

        return {
            "profile": profile_payload.get("profile", legacy_fallback.get("profile", profile_payload)),
            "current_day": tasks_data.get(
                "current_day",
                legacy_fallback.get("current_day", legacy_fallback.get("last_active_date", "")),
            ),
            "tasks": self.section_list(tasks_payload, "tasks", legacy_fallback.get("tasks", [])),
            "history": self.section_list(history_payload, "history", legacy_fallback.get("history", [])),
            "archived_days": self.section_list(
                history_payload,
                "archived_days",
                legacy_fallback.get("archived_days", []),
                allow_raw_list=False,
            ),
            "gamification": settings_data.get("gamification", legacy_fallback.get("gamification", {})),
            "points_total": wallet.get(
                "points_total",
                profile_payload.get(
                    "points_total",
                    legacy_fallback.get("points_total", legacy_fallback.get("points", 0)),
                ),
            ),
            "points_spent": wallet.get(
                "points_spent",
                profile_payload.get("points_spent", legacy_fallback.get("points_spent")),
            ),
            "rewards": self.section_list(rewards_payload, "rewards", legacy_fallback.get("rewards", [])),
            "reward_redemptions": self.section_list(
                rewards_payload,
                "reward_redemptions",
                legacy_fallback.get("reward_redemptions", legacy_fallback.get("redemptions", [])),
                allow_raw_list=False,
            ),
        }

    def is_legacy_payload(self, data):
        if not isinstance(data, dict):
            return False

        legacy_keys = (
            "history",
            "archived_days",
            "gamification",
            "points",
            "points_total",
            "points_spent",
            "rewards",
            "reward_redemptions",
            "redemptions",
        )
        return any(key in data for key in legacy_keys)

    def as_dict(self, value):
        return value if isinstance(value, dict) else {}

    def section_list(self, payload, section, fallback=None, allow_raw_list=True):
        if allow_raw_list and isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and section in payload:
            value = payload.get(section)
            return value if isinstance(value, list) else []
        return fallback if isinstance(fallback, list) else []

    def normalize_state(self, data):
        state = self.empty_state()
        state["profile"] = self.normalize_profile(data.get("profile", {}))
        state["points_total"] = max(0, to_int(data.get("points_total", data.get("points", 0))))
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
        return state

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
        profile=None,
    ):
        os.makedirs(self.data_dir, exist_ok=True)

        backup_error = self.backup_legacy_file_if_needed()
        if backup_error:
            return backup_error

        payloads = {
            "profile": {
                "schema_version": SCHEMA_VERSION,
                "profile": self.normalize_profile(profile or {}),
                "wallet": {
                    "points_total": max(0, to_int(points_total)),
                    "points_spent": max(0, to_int(points_spent)),
                },
            },
            "tasks": {
                "schema_version": SCHEMA_VERSION,
                "current_day": current_day,
                "tasks": tasks,
            },
            "rewards": {
                "schema_version": SCHEMA_VERSION,
                "rewards": rewards or [],
                "reward_redemptions": reward_redemptions or [],
            },
            "history": {
                "schema_version": SCHEMA_VERSION,
                "history": history,
                "archived_days": archived_days,
            },
            "settings": {
                "schema_version": SCHEMA_VERSION,
                "gamification": normalize_gamification(gamification),
            },
        }

        for key, payload in payloads.items():
            error = self.write_json_file(self.data_files[key], payload)
            if error:
                return error

        self.loaded_legacy_file = False
        return None

    def backup_legacy_file_if_needed(self):
        if not self.loaded_legacy_file:
            return None

        if not os.path.exists(self.legacy_data_file):
            return None

        if os.path.abspath(self.legacy_data_file) != os.path.abspath(self.data_files["tasks"]):
            return None

        backup_file = f"{self.legacy_data_file}.legacy.bak"
        if os.path.exists(backup_file):
            return None

        try:
            shutil.copy2(self.legacy_data_file, backup_file)
        except OSError as error:
            return f"Nao foi possivel criar backup do JSON antigo.\n\n{error}"

        return None

    def write_json_file(self, path, payload):
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        temp_file = f"{path}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
            os.replace(temp_file, path)
        except OSError as error:
            return f"Nao foi possivel salvar {os.path.basename(path)}.\n\n{error}"

        return None

    def normalize_profile(self, raw_profile):
        profile = self.default_profile()
        if not isinstance(raw_profile, dict):
            return profile

        name = str(raw_profile.get("name", profile["name"])).strip()
        profile["name"] = name

        avatar_url = str(raw_profile.get("avatar_url", "")).strip()
        legacy_avatar = str(raw_profile.get("avatar", "")).strip()
        if not avatar_url and legacy_avatar.startswith(("http://", "https://", "/", "data:image/")):
            avatar_url = legacy_avatar
        profile["avatar_url"] = avatar_url[:500]

        for key in ("avatar", "theme", "accent_color"):
            value = str(raw_profile.get(key, profile[key])).strip()
            if value:
                profile[key] = value

        return profile

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
            "image_url": normalize_reward_image_url(raw_reward.get("image_url", raw_reward.get("image", ""))),
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
