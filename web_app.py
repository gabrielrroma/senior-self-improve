import json
import mimetypes
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from date_utils import format_date, format_day_count, previous_day_key, today_key, today_label, to_int
from progress_service import (
    build_achievement_summary,
    build_achievements_view,
    build_weekly_stats,
    sync_achievements,
    sync_weekly_goal_bonus,
)
from reward_service import (
    can_redeem_reward,
    create_reward,
    delete_reward as delete_reward_item,
    find_reward,
    get_available_points,
    redeem_reward,
    sort_redemptions,
    sort_rewards,
    update_reward,
)
from routine_service import (
    apply_streak_for_summary,
    build_daily_summary,
    build_motivation_message,
    calculate_display_streak,
    carry_pinned_tasks_to_day,
    complete_task,
    create_task,
    default_gamification,
    delete_task,
    find_task,
    get_daily_goal_points,
    get_level_info,
    get_task_points,
    get_visible_tasks,
    is_daily_goal_complete,
    reopen_task,
    reset_streak_if_gap,
    set_task_pinned,
    update_task,
    upsert_archive_day,
    upsert_history_summary,
)
from settings import (
    CATEGORIES,
    FILTERS,
    MAX_DAILY_GOAL_POINTS,
    MAX_WEEKLY_GOAL_TASKS,
    MIN_DAILY_GOAL_POINTS,
    MIN_WEEKLY_GOAL_TASKS,
    PRIORITY_POINTS,
)
from storage import RoutineStorage


ROOT_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT_DIR / "web"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_PROFILE_NAME = "Rotina Diaria"
MAX_PROFILE_NAME_LENGTH = 80
MAX_PROFILE_AVATAR_URL_LENGTH = 500

mimetypes.add_type("image/webp", ".webp")


class RoutineApiError(Exception):
    def __init__(self, message, status=HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status = status


class RoutineWebState:
    def __init__(self, storage=None):
        self.storage = storage or RoutineStorage()
        self.lock = threading.RLock()
        self.profile = {}
        self.tasks = []
        self.history = []
        self.archived_days = []
        self.gamification = default_gamification()
        self.current_day = today_key()
        self.points_total = 0
        self.points_spent = 0
        self.rewards = []
        self.reward_redemptions = []
        self.load_error = None
        self._load_data()

    def _load_data(self):
        state, error = self.storage.load()
        self.profile = state["profile"]
        self.tasks = state["tasks"]
        self.history = state["history"]
        self.archived_days = state["archived_days"]
        self.gamification = state["gamification"]
        self.current_day = state["current_day"]
        self.points_total = state["points_total"]
        self.points_spent = state["points_spent"]
        self.rewards = state["rewards"]
        self.reward_redemptions = state["reward_redemptions"]
        self.load_error = error
        self.check_day_rollover()

    def _save_data(self):
        self.update_current_day_history()
        progress_messages = self.sync_progress_rewards()
        self._write_data()
        return progress_messages

    def _write_data(self):
        error = self.storage.save(
            self.current_day,
            self.tasks,
            self.history,
            self.archived_days,
            self.gamification,
            self.points_total,
            self.rewards,
            self.reward_redemptions,
            points_spent=self.points_spent,
            profile=self.profile,
        )
        if error:
            raise RoutineApiError(error, HTTPStatus.INTERNAL_SERVER_ERROR)

    def sync_progress_rewards(self):
        weekly_stats = build_weekly_stats(
            self.history,
            self.archived_days,
            self.tasks,
            self.current_day,
            self.gamification,
        )
        self.points_total, weekly_changed, weekly_messages = sync_weekly_goal_bonus(
            self.gamification,
            weekly_stats,
            self.current_day,
            self.points_total,
        )
        display_streak = calculate_display_streak(self.gamification, self.build_daily_summary())
        achievements_changed, achievement_messages = sync_achievements(
            self.gamification,
            self.history,
            self.points_total,
            self.current_day,
            display_streak,
        )
        if weekly_changed or achievements_changed:
            return weekly_messages + achievement_messages
        return []

    def _join_messages(self, *parts):
        messages = []
        for part in parts:
            if not part:
                continue
            if isinstance(part, list):
                messages.extend(str(message) for message in part if message)
            else:
                messages.append(str(part))
        return " ".join(messages)

    def build_profile_view(self):
        name = str(self.profile.get("name", "")).strip()
        avatar_url = str(self.profile.get("avatar_url", "")).strip()
        return {
            **self.profile,
            "name": name,
            "display_name": name or DEFAULT_PROFILE_NAME,
            "avatar_url": avatar_url,
        }

    def build_daily_summary(self, summary_date=None):
        return build_daily_summary(self.tasks, summary_date or self.current_day)

    def update_current_day_history(self):
        self.history = upsert_history_summary(self.history, self.build_daily_summary())

    def check_day_rollover(self):
        today = today_key()
        if self.current_day == today:
            return None

        previous_day = self.current_day
        previous_summary = self.build_daily_summary(previous_day)
        if previous_day == previous_day_key(today):
            streak_messages = [
                message
                for message in (apply_streak_for_summary(self.gamification, previous_summary),)
                if message
            ]
        else:
            streak_messages = [
                message
                for message in (reset_streak_if_gap(self.gamification, previous_day, today),)
                if message
            ]

        self.history = upsert_history_summary(self.history, previous_summary)
        self.archived_days = upsert_archive_day(self.archived_days, previous_day, previous_summary, self.tasks)

        carried_tasks = carry_pinned_tasks_to_day(self.tasks, today)
        self.tasks = carried_tasks
        self.current_day = today
        self.update_current_day_history()

        feedback = f"Novo dia iniciado. Resumo de {format_date(previous_day)} salvo."
        carried_count = len(carried_tasks)
        if carried_count == 1:
            feedback = f"{feedback} 1 missao fixada mantida."
        elif carried_count > 1:
            feedback = f"{feedback} {carried_count} missoes fixadas mantidas."
        if streak_messages:
            feedback = f"{feedback} {' '.join(streak_messages)}"

        progress_messages = self._save_data()
        return self._join_messages(feedback, progress_messages)

    def snapshot(self, selected_filter="Todas", message=None):
        with self.lock:
            selected_filter = selected_filter if selected_filter in FILTERS else "Todas"
            rollover_message = self.check_day_rollover()
            self.update_current_day_history()
            progress_messages = self.sync_progress_rewards()
            if progress_messages:
                self._write_data()
            summary = self.build_daily_summary()
            level_info = get_level_info(self.points_total)
            goal = get_daily_goal_points(self.gamification)
            goal_points = summary["points_earned"]
            goal_progress = int((min(goal_points, goal) / goal) * 100) if goal else 0
            display_streak = calculate_display_streak(self.gamification, summary)
            points_available = get_available_points(self.points_total, self.points_spent)
            weekly_stats = build_weekly_stats(
                self.history,
                self.archived_days,
                self.tasks,
                self.current_day,
                self.gamification,
            )
            achievements = build_achievements_view(
                self.gamification,
                self.history,
                self.points_total,
                display_streak,
            )
            achievement_summary = build_achievement_summary(achievements)

            tasks = []
            for task in get_visible_tasks(self.tasks, selected_filter):
                points = task.get("points_awarded") if task["done"] else get_task_points(task)
                tasks.append(
                    {
                        "id": task["id"],
                        "title": task["title"],
                        "done": task["done"],
                        "priority": task["priority"],
                        "category": task["category"],
                        "pinned": task.get("pinned", False),
                        "created_at": task.get("created_at"),
                        "completed_at": task.get("completed_at"),
                        "created_label": format_date(task.get("created_at")),
                        "completed_label": format_date(task.get("completed_at")),
                        "points": points,
                        "points_label": f"{points} pts",
                        "status_label": "Concluida" if task["done"] else "Pendente",
                    }
                )

            rewards = []
            for reward in sort_rewards(self.rewards):
                rewards.append(
                    {
                        "id": reward["id"],
                        "title": reward["title"],
                        "description": reward.get("description", ""),
                        "image_url": reward.get("image_url", ""),
                        "cost": reward["cost"],
                        "cost_label": f"{reward['cost']} pts",
                        "created_at": reward.get("created_at"),
                        "created_label": format_date(reward.get("created_at")),
                        "can_redeem": can_redeem_reward(reward, self.points_total, self.points_spent),
                    }
                )

            reward_redemptions = []
            for redemption in sort_redemptions(self.reward_redemptions):
                reward_redemptions.append(
                    {
                        "id": redemption["id"],
                        "reward_id": redemption.get("reward_id"),
                        "reward_title": redemption["reward_title"],
                        "cost": redemption["cost"],
                        "cost_label": f"{redemption['cost']} pts",
                        "redeemed_at": redemption["redeemed_at"],
                        "redeemed_label": format_date(redemption["redeemed_at"]),
                    }
                )

            history = []
            for entry in sorted(self.history, key=lambda item: item["date"], reverse=True):
                history.append(
                    {
                        "date": entry["date"],
                        "date_label": format_date(entry["date"]),
                        "completed_tasks": entry["completed_tasks"],
                        "total_tasks": entry["total_tasks"],
                        "points_earned": entry["points_earned"],
                        "completion_percentage": entry["completion_percentage"],
                    }
                )

            return {
                "message": self._join_messages(message or rollover_message or self.load_error, progress_messages)
                or "Pronto",
                "current_day": self.current_day,
                "today_label": today_label(),
                "filters": list(FILTERS),
                "selected_filter": selected_filter,
                "categories": list(CATEGORIES),
                "priorities": list(PRIORITY_POINTS.keys()),
                "priority_points": PRIORITY_POINTS,
                "daily_goal_limits": {
                    "min": MIN_DAILY_GOAL_POINTS,
                    "max": MAX_DAILY_GOAL_POINTS,
                },
                "weekly_goal_limits": {
                    "min": MIN_WEEKLY_GOAL_TASKS,
                    "max": MAX_WEEKLY_GOAL_TASKS,
                },
                "summary": {
                    **summary,
                    "pending_tasks": max(0, summary["total_tasks"] - summary["completed_tasks"]),
                },
                "gamification": {
                    "daily_goal_points": goal,
                    "daily_goal_progress": goal_progress,
                    "daily_goal_label": f"{goal_points}/{goal} pts",
                    "weekly_goal_tasks": weekly_stats["goal_tasks"],
                    "weekly_goal_progress": weekly_stats["goal_progress"],
                    "weekly_goal_label": weekly_stats["goal_label"],
                    "weekly_goal_bonus_points": weekly_stats["bonus_points"],
                    "streak_count": display_streak,
                    "streak_label": format_day_count(display_streak),
                    "best_streak": max(to_int(self.gamification.get("best_streak")), display_streak),
                    "motivation": build_motivation_message(self.gamification, summary),
                },
                "wallet": {
                    "points_total": self.points_total,
                    "points_spent": self.points_spent,
                    "points_available": points_available,
                    "points_available_label": f"{points_available} pts",
                    "points_spent_label": f"{self.points_spent} usados",
                },
                "level": {
                    **level_info,
                    "xp_label": f"{level_info['xp_total']} XP total",
                    "detail_label": (
                        f"{level_info['xp_current']}/{level_info['xp_needed']} "
                        f"para nivel {level_info['level'] + 1}"
                    ),
                },
                "points_total": self.points_total,
                "profile": self.build_profile_view(),
                "tasks": tasks,
                "history": history,
                "weekly_stats": weekly_stats,
                "achievements": achievements,
                "achievement_summary": achievement_summary,
                "rewards": rewards,
                "reward_redemptions": reward_redemptions,
            }

    def update_profile(self, payload):
        with self.lock:
            name = str(payload.get("name", self.profile.get("name", ""))).strip()
            avatar_url = str(payload.get("avatar_url", self.profile.get("avatar_url", ""))).strip()

            if len(name) > MAX_PROFILE_NAME_LENGTH:
                raise RoutineApiError(f"Use um nome com ate {MAX_PROFILE_NAME_LENGTH} caracteres.")
            if len(avatar_url) > MAX_PROFILE_AVATAR_URL_LENGTH:
                raise RoutineApiError(f"Use uma URL de foto com ate {MAX_PROFILE_AVATAR_URL_LENGTH} caracteres.")

            self.profile["name"] = name
            self.profile["avatar_url"] = avatar_url
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages("Perfil atualizado.", progress_messages))

    def add_task(self, payload):
        with self.lock:
            self.check_day_rollover()
            title = str(payload.get("title", "")).strip()
            if not title:
                raise RoutineApiError("Digite uma tarefa primeiro.")

            self.tasks.append(
                create_task(
                    title,
                    payload.get("priority", "Media"),
                    payload.get("category", "Outros"),
                    bool(payload.get("pinned", False)),
                )
            )
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages("Tarefa adicionada.", progress_messages))

    def update_existing_task(self, task_id, payload):
        with self.lock:
            self.check_day_rollover()
            task = self._get_task_or_error(task_id)
            title = str(payload.get("title", "")).strip()
            if not title:
                raise RoutineApiError("Digite uma tarefa primeiro.")

            update_task(task, title, payload.get("priority", "Media"), payload.get("category", "Outros"))
            set_task_pinned(task, bool(payload.get("pinned", False)))
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages("Tarefa atualizada.", progress_messages))

    def complete_existing_task(self, task_id):
        with self.lock:
            self.check_day_rollover()
            task = self._get_task_or_error(task_id)
            if task["done"]:
                return self.snapshot(message="Essa tarefa ja esta concluida.")

            self.points_total, points = complete_task(task, self.points_total)
            message = f"+{points} pontos adicionados."
            if is_daily_goal_complete(self.gamification, self.build_daily_summary()):
                message = f"{message} Meta diaria concluida."
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages(message, progress_messages))

    def reopen_existing_task(self, task_id):
        with self.lock:
            self.check_day_rollover()
            task = self._get_task_or_error(task_id)
            if not task["done"]:
                return self.snapshot(message="Essa tarefa ja esta pendente.")

            self.points_total, points = reopen_task(task, self.points_total)
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages(f"{points} pontos removidos.", progress_messages))

    def toggle_pin_existing_task(self, task_id):
        with self.lock:
            self.check_day_rollover()
            task = self._get_task_or_error(task_id)
            pinned = not task.get("pinned", False)
            set_task_pinned(task, pinned)
            progress_messages = self._save_data()
            if pinned:
                return self.snapshot(
                    message=self._join_messages("Missao fixada. Ela voltara todo dia.", progress_messages)
                )
            return self.snapshot(message=self._join_messages("Missao desafixada.", progress_messages))

    def delete_existing_task(self, task_id):
        with self.lock:
            self.check_day_rollover()
            task = self._get_task_or_error(task_id)
            self.tasks, self.points_total = delete_task(self.tasks, task, self.points_total)
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages("Tarefa excluida.", progress_messages))

    def update_daily_goal(self, payload):
        with self.lock:
            goal = to_int(payload.get("daily_goal_points"), get_daily_goal_points(self.gamification))
            goal = max(MIN_DAILY_GOAL_POINTS, min(MAX_DAILY_GOAL_POINTS, goal))
            self.gamification["daily_goal_points"] = goal
            progress_messages = self._save_data()
            return self.snapshot(
                message=self._join_messages(f"Meta diaria atualizada para {goal} pontos.", progress_messages)
            )

    def update_weekly_goal(self, payload):
        with self.lock:
            goal = to_int(payload.get("weekly_goal_tasks"), self.gamification.get("weekly_goal_tasks"))
            goal = max(MIN_WEEKLY_GOAL_TASKS, min(MAX_WEEKLY_GOAL_TASKS, goal))
            self.gamification["weekly_goal_tasks"] = goal
            progress_messages = self._save_data()
            return self.snapshot(
                message=self._join_messages(f"Meta semanal atualizada para {goal} tarefas.", progress_messages)
            )

    def add_reward(self, payload):
        with self.lock:
            title = str(payload.get("title", "")).strip()
            if not title:
                raise RoutineApiError("Digite o nome da recompensa.")

            cost = self._get_reward_cost_or_error(payload)
            description = str(payload.get("description", "")).strip()
            image_url = str(payload.get("image_url", "")).strip()
            self.rewards.append(create_reward(title, cost, description, image_url))
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages("Recompensa adicionada.", progress_messages))

    def update_existing_reward(self, reward_id, payload):
        with self.lock:
            reward = self._get_reward_or_error(reward_id)
            title = str(payload.get("title", "")).strip()
            if not title:
                raise RoutineApiError("Digite o nome da recompensa.")

            cost = self._get_reward_cost_or_error(payload)
            description = str(payload.get("description", "")).strip()
            image_url = str(payload.get("image_url", "")).strip()
            update_reward(reward, title, cost, description, image_url)
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages("Recompensa atualizada.", progress_messages))

    def delete_existing_reward(self, reward_id):
        with self.lock:
            reward = self._get_reward_or_error(reward_id)
            self.rewards = delete_reward_item(self.rewards, reward)
            progress_messages = self._save_data()
            return self.snapshot(message=self._join_messages("Recompensa excluida.", progress_messages))

    def redeem_existing_reward(self, reward_id):
        with self.lock:
            reward = self._get_reward_or_error(reward_id)
            if not can_redeem_reward(reward, self.points_total, self.points_spent):
                return self.snapshot(message="Pontos disponiveis insuficientes para esse resgate.")

            self.points_spent, redemption = redeem_reward(reward, self.points_spent)
            self.reward_redemptions.append(redemption)
            progress_messages = self._save_data()
            return self.snapshot(
                message=self._join_messages(f"Recompensa resgatada: {reward['title']}.", progress_messages)
            )

    def _get_task_or_error(self, task_id):
        task = find_task(self.tasks, task_id)
        if task is None:
            raise RoutineApiError("A tarefa selecionada nao existe mais.", HTTPStatus.NOT_FOUND)
        return task

    def _get_reward_or_error(self, reward_id):
        reward = find_reward(self.rewards, reward_id)
        if reward is None:
            raise RoutineApiError("A recompensa selecionada nao existe mais.", HTTPStatus.NOT_FOUND)
        return reward

    def _get_reward_cost_or_error(self, payload):
        cost = to_int(payload.get("cost"), 0)
        if cost <= 0:
            raise RoutineApiError("Defina um custo maior que zero.")
        return cost


def make_handler(app_state):
    class RoutineRequestHandler(BaseHTTPRequestHandler):
        server_version = "RotinaDiariaWeb/1.0"

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/state":
                query = parse_qs(parsed.query)
                selected_filter = query.get("filter", ["Todas"])[0]
                self._send_json(app_state.snapshot(selected_filter=selected_filter))
                return

            self._serve_static(parsed.path)

        def do_POST(self):
            self._handle_api_mutation()

        def do_PUT(self):
            self._handle_api_mutation()

        def do_PATCH(self):
            self._handle_api_mutation()

        def do_DELETE(self):
            self._handle_api_mutation()

        def log_message(self, format_value, *args):
            print(f"{self.address_string()} - {format_value % args}")

        def _handle_api_mutation(self):
            parsed = urlparse(self.path)
            parts = [part for part in parsed.path.strip("/").split("/") if part]

            try:
                payload = self._read_json()
                if parts == ["api", "tasks"] and self.command == "POST":
                    self._send_json(app_state.add_task(payload), HTTPStatus.CREATED)
                    return

                if parts == ["api", "rewards"] and self.command == "POST":
                    self._send_json(app_state.add_reward(payload), HTTPStatus.CREATED)
                    return

                if parts == ["api", "profile"] and self.command == "PUT":
                    self._send_json(app_state.update_profile(payload))
                    return

                if len(parts) == 3 and parts[:2] == ["api", "tasks"]:
                    task_id = parts[2]
                    if self.command == "PUT":
                        self._send_json(app_state.update_existing_task(task_id, payload))
                        return
                    if self.command == "DELETE":
                        self._send_json(app_state.delete_existing_task(task_id))
                        return

                if len(parts) == 4 and parts[:2] == ["api", "tasks"] and self.command == "PATCH":
                    task_id = parts[2]
                    action = parts[3]
                    if action == "complete":
                        self._send_json(app_state.complete_existing_task(task_id))
                        return
                    if action == "reopen":
                        self._send_json(app_state.reopen_existing_task(task_id))
                        return
                    if action == "pin":
                        self._send_json(app_state.toggle_pin_existing_task(task_id))
                        return

                if len(parts) == 3 and parts[:2] == ["api", "rewards"]:
                    reward_id = parts[2]
                    if self.command == "PUT":
                        self._send_json(app_state.update_existing_reward(reward_id, payload))
                        return
                    if self.command == "DELETE":
                        self._send_json(app_state.delete_existing_reward(reward_id))
                        return

                if len(parts) == 4 and parts[:2] == ["api", "rewards"] and self.command == "PATCH":
                    reward_id = parts[2]
                    action = parts[3]
                    if action == "redeem":
                        self._send_json(app_state.redeem_existing_reward(reward_id))
                        return

                if parts == ["api", "settings", "daily-goal"] and self.command == "PUT":
                    self._send_json(app_state.update_daily_goal(payload))
                    return

                if parts == ["api", "settings", "weekly-goal"] and self.command == "PUT":
                    self._send_json(app_state.update_weekly_goal(payload))
                    return

                raise RoutineApiError("Rota nao encontrada.", HTTPStatus.NOT_FOUND)
            except RoutineApiError as error:
                self._send_json({"message": error.message}, error.status)
            except json.JSONDecodeError:
                self._send_json({"message": "JSON invalido."}, HTTPStatus.BAD_REQUEST)
            except Exception as error:
                self._send_json({"message": f"Erro inesperado: {error}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

        def _read_json(self):
            length = int(self.headers.get("Content-Length", "0") or 0)
            if length <= 0:
                return {}
            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise RoutineApiError("O corpo da requisicao precisa ser um objeto JSON.")
            return payload

        def _serve_static(self, request_path):
            if request_path in ("", "/"):
                request_path = "/index.html"

            web_root = WEB_DIR.resolve()
            requested = (web_root / request_path.lstrip("/")).resolve()
            try:
                requested.relative_to(web_root)
            except ValueError:
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            if requested.is_dir():
                requested = requested / "index.html"

            if not requested.exists() or not requested.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            content_type = mimetypes.guess_type(str(requested))[0] or "application/octet-stream"
            content = requested.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def _send_json(self, payload, status=HTTPStatus.OK):
            content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    return RoutineRequestHandler


class RotinaHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def create_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    app_state = RoutineWebState()
    handler = make_handler(app_state)
    last_error = None

    for candidate_port in range(port, port + 50):
        try:
            server = RotinaHTTPServer((host, candidate_port), handler)
            server.app_state = app_state
            return server
        except OSError as error:
            last_error = error

    raise OSError(f"Nao foi possivel iniciar o servidor local: {last_error}")


def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT, open_browser=True):
    server = create_server(host, port)
    url = f"http://{host}:{server.server_port}/"
    print(f"Rotina Diaria web rodando em {url}")
    print("Pressione Ctrl+C para encerrar.")

    if open_browser:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
