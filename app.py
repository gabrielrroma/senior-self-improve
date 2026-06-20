import json
import os
from datetime import date
from uuid import uuid4
import tkinter as tk
from tkinter import messagebox, ttk


DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")

PRIORITY_POINTS = {
    "Baixa": 5,
    "Media": 10,
    "Alta": 20,
}

PRIORITY_ORDER = {
    "Alta": 0,
    "Media": 1,
    "Baixa": 2,
}

CATEGORIES = (
    "Estudos",
    "Trabalho",
    "Saude",
    "Casa",
    "Lazer",
    "Outros",
)

FILTERS = (
    "Todas",
    "Pendentes",
    "Concluidas",
)

THEMES = {
    "light": {
        "bg": "#edf2f7",
        "surface": "#ffffff",
        "surface_alt": "#f8fafc",
        "border": "#d8dee9",
        "ink": "#172033",
        "muted": "#667085",
        "primary": "#2563eb",
        "primary_dark": "#1d4ed8",
        "success": "#148f4f",
        "danger": "#c43838",
        "low": "#2563eb",
        "medium": "#b7791f",
        "high": "#c43838",
        "selected": "#dbeafe",
        "progress_trough": "#e5e7eb",
        "done_fg": "#8a94a6",
        "done_bg": "#f8fafc",
    },
    "dark": {
        "bg": "#111827",
        "surface": "#1f2937",
        "surface_alt": "#273244",
        "border": "#374151",
        "ink": "#f3f4f6",
        "muted": "#a7b0c0",
        "primary": "#60a5fa",
        "primary_dark": "#3b82f6",
        "success": "#34d399",
        "danger": "#f87171",
        "low": "#93c5fd",
        "medium": "#fbbf24",
        "high": "#fb7185",
        "selected": "#1e3a5f",
        "progress_trough": "#374151",
        "done_fg": "#8792a2",
        "done_bg": "#182131",
    },
}

COLORS = THEMES["light"].copy()


def today_key():
    return date.today().isoformat()


def today_label():
    return date.today().strftime("%d/%m/%Y")


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class RoutineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rotina Diaria")
        self.root.geometry("1080x700")
        self.root.minsize(980, 640)
        self.root.configure(bg=COLORS["bg"])

        self.theme_name = "light"
        self.themed_cards = []
        self.tasks = []
        self.points_total = 0
        self.editing_task_id = None

        self.title_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Media")
        self.category_var = tk.StringVar(value="Outros")
        self.filter_var = tk.StringVar(value="Todas")

        self.summary_var = tk.StringVar(value="0 de 0")
        self.progress_var = tk.StringVar(value="0%")
        self.pending_var = tk.StringVar(value="0")
        self.today_points_var = tk.StringVar(value="0")
        self.points_total_var = tk.StringVar(value="0")
        self.feedback_var = tk.StringVar(value="Pronto")
        self.form_title_var = tk.StringVar(value="Nova tarefa")
        self.theme_button_var = tk.StringVar(value="Modo escuro")

        self._configure_styles()
        self._create_ui()
        self._load_data()
        self.refresh()

    def _configure_styles(self):
        if not hasattr(self, "style"):
            self.style = ttk.Style()
            self.style.theme_use("clam")

        style = self.style

        default_font = ("Segoe UI", 10)
        title_font = ("Segoe UI", 22, "bold")
        section_font = ("Segoe UI", 12, "bold")
        metric_font = ("Segoe UI", 20, "bold")

        style.configure(".", font=default_font)
        style.configure("Root.TFrame", background=COLORS["bg"])
        style.configure("Surface.TFrame", background=COLORS["surface"])
        style.configure("Soft.TFrame", background=COLORS["surface_alt"])

        style.configure(
            "Title.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["ink"],
            font=title_font,
        )
        style.configure("Subtitle.TLabel", background=COLORS["bg"], foreground=COLORS["muted"])
        style.configure(
            "Section.TLabel",
            background=COLORS["surface"],
            foreground=COLORS["ink"],
            font=section_font,
        )
        style.configure("CardTitle.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
        style.configure("Metric.TLabel", background=COLORS["surface"], foreground=COLORS["ink"], font=metric_font)
        style.configure("Muted.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
        style.configure("Form.TLabel", background=COLORS["surface"], foreground=COLORS["ink"])
        style.configure("Status.TLabel", background=COLORS["bg"], foreground=COLORS["muted"])

        style.configure(
            "Accent.TButton",
            background=COLORS["primary"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(14, 9),
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["primary_dark"]), ("disabled", COLORS["border"])],
            foreground=[("disabled", COLORS["muted"])],
        )

        style.configure(
            "Neutral.TButton",
            background=COLORS["surface_alt"],
            foreground=COLORS["ink"],
            bordercolor=COLORS["border"],
            padding=(12, 8),
        )
        style.map(
            "Neutral.TButton",
            background=[("active", COLORS["border"]), ("disabled", COLORS["surface_alt"])],
            foreground=[("disabled", COLORS["muted"])],
        )
        style.configure(
            "Danger.TButton",
            background=COLORS["surface_alt"],
            foreground=COLORS["danger"],
            bordercolor=COLORS["border"],
            padding=(12, 8),
        )
        style.map("Danger.TButton", foreground=[("active", COLORS["danger"])])
        style.configure(
            "TEntry",
            fieldbackground=COLORS["surface_alt"],
            foreground=COLORS["ink"],
            bordercolor=COLORS["border"],
            insertcolor=COLORS["ink"],
        )
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["surface_alt"],
            foreground=COLORS["ink"],
            background=COLORS["surface_alt"],
            bordercolor=COLORS["border"],
            arrowcolor=COLORS["muted"],
        )

        style.configure(
            "Routine.Horizontal.TProgressbar",
            background=COLORS["success"],
            troughcolor=COLORS["progress_trough"],
            bordercolor=COLORS["progress_trough"],
            lightcolor=COLORS["success"],
            darkcolor=COLORS["success"],
        )

        style.configure(
            "Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["ink"],
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            padding=(8, 8),
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["selected"])],
            foreground=[("selected", COLORS["ink"])],
        )

    def _create_ui(self):
        shell = ttk.Frame(self.root, style="Root.TFrame")
        shell.pack(fill="both", expand=True, padx=22, pady=18)

        self._create_header(shell)

        content = ttk.Frame(shell, style="Root.TFrame")
        content.pack(fill="both", expand=True, pady=(14, 0))
        content.columnconfigure(0, minsize=310)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content, style="Root.TFrame")
        left.grid(row=0, column=0, sticky="nsew")

        right = ttk.Frame(content, style="Root.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(18, 0))
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self._create_summary_panel(left)
        self._create_task_form(left)
        self._create_task_panel(right)

        status = ttk.Label(shell, textvariable=self.feedback_var, style="Status.TLabel")
        status.pack(anchor="w", pady=(10, 0))

    def _create_header(self, parent):
        header = ttk.Frame(parent, style="Root.TFrame")
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)

        title_area = ttk.Frame(header, style="Root.TFrame")
        title_area.grid(row=0, column=0, sticky="w")

        ttk.Label(title_area, text="Rotina Diaria", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_area,
            text=f"Painel de hoje - {today_label()}",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        self.theme_button = ttk.Button(
            header,
            textvariable=self.theme_button_var,
            style="Neutral.TButton",
            command=self.toggle_theme,
        )
        self.theme_button.grid(row=0, column=1, sticky="e", padx=(0, 10))

        quick = self._card(header, padx=16, pady=12)
        quick.grid(row=0, column=2, sticky="e")

        ttk.Label(quick, text="Progresso", style="CardTitle.TLabel").pack(anchor="e")
        ttk.Label(quick, textvariable=self.progress_var, style="Metric.TLabel").pack(anchor="e")

    def _create_summary_panel(self, parent):
        card = self._card(parent)
        card.pack(fill="x")

        ttk.Label(card, text="Resumo", style="Section.TLabel").pack(anchor="w")

        progress_line = ttk.Frame(card, style="Surface.TFrame")
        progress_line.pack(fill="x", pady=(14, 6))
        ttk.Label(progress_line, textvariable=self.summary_var, style="Muted.TLabel").pack(side="left")
        ttk.Label(progress_line, textvariable=self.progress_var, style="Muted.TLabel").pack(side="right")

        self.progress_bar = ttk.Progressbar(
            card,
            mode="determinate",
            maximum=100,
            style="Routine.Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x")

        metrics = ttk.Frame(card, style="Surface.TFrame")
        metrics.pack(fill="x", pady=(16, 0))
        metrics.columnconfigure((0, 1), weight=1, uniform="metrics")

        self._metric(metrics, "Pendentes", self.pending_var, 0, 0)
        self._metric(metrics, "Pontos hoje", self.today_points_var, 0, 1)
        self._metric(metrics, "Pontos totais", self.points_total_var, 1, 0, columnspan=2)

    def _create_task_form(self, parent):
        card = self._card(parent)
        card.pack(fill="x", pady=(16, 0))

        ttk.Label(card, textvariable=self.form_title_var, style="Section.TLabel").pack(anchor="w")

        ttk.Label(card, text="Tarefa", style="Form.TLabel").pack(anchor="w", pady=(14, 4))
        title_entry = ttk.Entry(card, textvariable=self.title_var)
        title_entry.pack(fill="x", ipady=6)
        title_entry.bind("<Return>", lambda event: self.save_task())
        self.title_entry = title_entry

        fields = ttk.Frame(card, style="Surface.TFrame")
        fields.pack(fill="x", pady=(12, 0))
        fields.columnconfigure((0, 1), weight=1, uniform="form")

        ttk.Label(fields, text="Prioridade", style="Form.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(fields, text="Categoria", style="Form.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))

        priority = ttk.Combobox(
            fields,
            textvariable=self.priority_var,
            values=list(PRIORITY_POINTS.keys()),
            state="readonly",
        )
        priority.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        category = ttk.Combobox(
            fields,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
        )
        category.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 0))

        actions = ttk.Frame(card, style="Surface.TFrame")
        actions.pack(fill="x", pady=(16, 0))

        self.save_button = ttk.Button(
            actions,
            text="Adicionar",
            style="Accent.TButton",
            command=self.save_task,
        )
        self.save_button.pack(side="left", fill="x", expand=True)
        ttk.Button(
            actions,
            text="Limpar",
            style="Neutral.TButton",
            command=self.clear_form,
        ).pack(side="left", padx=(10, 0))

    def _create_task_panel(self, parent):
        toolbar = ttk.Frame(parent, style="Root.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.columnconfigure(0, weight=1)

        ttk.Label(toolbar, text="Tarefas", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        filter_box = ttk.Combobox(
            toolbar,
            textvariable=self.filter_var,
            values=FILTERS,
            state="readonly",
            width=16,
        )
        filter_box.grid(row=0, column=1, sticky="e")
        filter_box.bind("<<ComboboxSelected>>", lambda event: self.refresh())

        table_card = self._card(parent, padx=0, pady=0)
        table_card.grid(row=1, column=0, sticky="nsew")
        table_card.rowconfigure(0, weight=1)
        table_card.columnconfigure(0, weight=1)

        columns = ("status", "task", "priority", "category", "points", "created")
        self.task_tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        headings = {
            "status": "Status",
            "task": "Tarefa",
            "priority": "Prioridade",
            "category": "Categoria",
            "points": "Pontos",
            "created": "Criada em",
        }
        widths = {
            "status": 110,
            "task": 330,
            "priority": 110,
            "category": 120,
            "points": 90,
            "created": 110,
        }

        for key in columns:
            self.task_tree.heading(key, text=headings[key])
            self.task_tree.column(
                key,
                width=widths[key],
                minwidth=80,
                stretch=key == "task",
                anchor="w",
            )

        self.configure_tree_tags()

        self.task_tree.grid(row=0, column=0, sticky="nsew")
        self.task_tree.bind("<<TreeviewSelect>>", lambda event: self.update_action_state())
        self.task_tree.bind("<Double-1>", lambda event: self.toggle_selected_task())

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.task_tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.task_tree.configure(yscrollcommand=scroll.set)

        actions = ttk.Frame(parent, style="Root.TFrame")
        actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        self.complete_button = ttk.Button(
            actions,
            text="Concluir",
            style="Accent.TButton",
            command=self.complete_selected_task,
        )
        self.complete_button.pack(side="left")
        self.reopen_button = ttk.Button(
            actions,
            text="Reabrir",
            style="Neutral.TButton",
            command=self.reopen_selected_task,
        )
        self.reopen_button.pack(side="left", padx=(8, 0))
        self.edit_button = ttk.Button(
            actions,
            text="Editar",
            style="Neutral.TButton",
            command=self.edit_selected_task,
        )
        self.edit_button.pack(side="left", padx=(8, 0))
        self.delete_button = ttk.Button(
            actions,
            text="Excluir",
            style="Danger.TButton",
            command=self.delete_selected_task,
        )
        self.delete_button.pack(side="left", padx=(8, 0))

    def _card(self, parent, padx=18, pady=18):
        frame = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        frame.configure(padx=padx, pady=pady)
        self.themed_cards.append(frame)
        return frame

    def _metric(self, parent, label, variable, row, column, columnspan=1):
        metric = ttk.Frame(parent, style="Surface.TFrame")
        metric.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="ew",
            pady=(0, 12),
            padx=(0, 10),
        )
        ttk.Label(metric, text=label, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(metric, textvariable=variable, style="Metric.TLabel").pack(anchor="w")

    def toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        COLORS.clear()
        COLORS.update(THEMES[self.theme_name])
        self.theme_button_var.set("Modo claro" if self.theme_name == "dark" else "Modo escuro")
        self.apply_theme()

    def apply_theme(self):
        self.root.configure(bg=COLORS["bg"])
        self._configure_styles()

        for card in self.themed_cards:
            card.configure(
                bg=COLORS["surface"],
                highlightbackground=COLORS["border"],
            )

        self.configure_tree_tags()
        self.refresh_task_list()

    def configure_tree_tags(self):
        if not hasattr(self, "task_tree"):
            return

        self.task_tree.tag_configure(
            "done",
            foreground=COLORS["done_fg"],
            background=COLORS["done_bg"],
        )
        self.task_tree.tag_configure("Alta", foreground=COLORS["high"])
        self.task_tree.tag_configure("Media", foreground=COLORS["medium"])
        self.task_tree.tag_configure("Baixa", foreground=COLORS["low"])

    def _load_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)

        if not os.path.exists(DATA_FILE):
            self.tasks = []
            self.points_total = 0
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            self.tasks = []
            self.points_total = 0
            self.feedback_var.set("Nao foi possivel carregar os dados salvos.")
            return

        self.points_total = to_int(data.get("points_total", data.get("points", 0)))
        self.tasks = []

        for raw_task in data.get("tasks", []):
            task = self._normalize_task(raw_task)
            if task is not None:
                self.tasks.append(task)

    def _normalize_task(self, raw_task):
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
        }

    def _save_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        payload = {
            "tasks": self.tasks,
            "points_total": self.points_total,
        }

        temp_file = f"{DATA_FILE}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
            os.replace(temp_file, DATA_FILE)
        except OSError as error:
            messagebox.showerror("Erro", f"Nao foi possivel salvar os dados.\n\n{error}")

    def save_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Aviso", "Digite uma tarefa primeiro.")
            return

        priority = self.priority_var.get()
        category = self.category_var.get()

        if self.editing_task_id is None:
            self.tasks.append(
                {
                    "id": uuid4().hex,
                    "title": title,
                    "done": False,
                    "priority": priority,
                    "category": category,
                    "created_at": today_key(),
                    "completed_at": None,
                    "points_awarded": 0,
                }
            )
            self.feedback_var.set("Tarefa adicionada.")
        else:
            task = self.find_task(self.editing_task_id)
            if task is None:
                messagebox.showwarning("Aviso", "A tarefa selecionada nao existe mais.")
                self.clear_form()
                return

            task["title"] = title
            task["priority"] = priority
            task["category"] = category
            self.feedback_var.set("Tarefa atualizada.")

        self.clear_form()
        self.refresh()
        self._save_data()

    def clear_form(self):
        self.editing_task_id = None
        self.title_var.set("")
        self.priority_var.set("Media")
        self.category_var.set("Outros")
        self.form_title_var.set("Nova tarefa")
        self.save_button.configure(text="Adicionar")
        self.title_entry.focus_set()

    def complete_selected_task(self):
        task = self.get_selected_task()
        if task is None:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir.")
            return

        if task["done"]:
            self.feedback_var.set("Essa tarefa ja esta concluida.")
            return

        points = self.get_task_points(task)
        task["done"] = True
        task["completed_at"] = today_key()
        task["points_awarded"] = points
        self.points_total += points

        self.feedback_var.set(f"+{points} pontos adicionados.")
        self.refresh()
        self._save_data()

    def reopen_selected_task(self):
        task = self.get_selected_task()
        if task is None:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para reabrir.")
            return

        if not task["done"]:
            self.feedback_var.set("Essa tarefa ja esta pendente.")
            return

        points = to_int(task.get("points_awarded"), self.get_task_points(task))
        self.points_total = max(0, self.points_total - points)
        task["done"] = False
        task["completed_at"] = None
        task["points_awarded"] = 0

        self.feedback_var.set(f"{points} pontos removidos.")
        self.refresh()
        self._save_data()

    def toggle_selected_task(self):
        task = self.get_selected_task()
        if task is None:
            return
        if task["done"]:
            self.reopen_selected_task()
        else:
            self.complete_selected_task()

    def edit_selected_task(self):
        task = self.get_selected_task()
        if task is None:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para editar.")
            return

        self.editing_task_id = task["id"]
        self.title_var.set(task["title"])
        self.priority_var.set(task["priority"])
        self.category_var.set(task["category"])
        self.form_title_var.set("Editar tarefa")
        self.save_button.configure(text="Salvar")
        self.title_entry.focus_set()
        self.title_entry.selection_range(0, tk.END)

    def delete_selected_task(self):
        task = self.get_selected_task()
        if task is None:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para excluir.")
            return

        answer = messagebox.askyesno("Confirmar", "Deseja realmente excluir esta tarefa?")
        if not answer:
            return

        if task["done"]:
            points = to_int(task.get("points_awarded"), self.get_task_points(task))
            self.points_total = max(0, self.points_total - points)

        self.tasks = [item for item in self.tasks if item["id"] != task["id"]]
        if self.editing_task_id == task["id"]:
            self.clear_form()

        self.feedback_var.set("Tarefa excluida.")
        self.refresh()
        self._save_data()

    def find_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def get_selected_task(self):
        selected = self.task_tree.selection()
        if not selected:
            return None
        return self.find_task(selected[0])

    def get_task_points(self, task):
        return PRIORITY_POINTS.get(task.get("priority", "Media"), PRIORITY_POINTS["Media"])

    def get_visible_tasks(self):
        selected_filter = self.filter_var.get()
        tasks = list(self.tasks)

        if selected_filter == "Pendentes":
            tasks = [task for task in tasks if not task["done"]]
        elif selected_filter == "Concluidas":
            tasks = [task for task in tasks if task["done"]]

        return sorted(
            tasks,
            key=lambda task: (
                task["done"],
                PRIORITY_ORDER.get(task["priority"], 1),
                task.get("created_at", ""),
                task["title"].lower(),
            ),
        )

    def refresh(self):
        self.refresh_task_list()
        self.refresh_summary()
        self.update_action_state()

    def refresh_task_list(self):
        selected = self.task_tree.selection()
        selected_id = selected[0] if selected else None

        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        for task in self.get_visible_tasks():
            status = "Concluida" if task["done"] else "Pendente"
            points = task.get("points_awarded") if task["done"] else self.get_task_points(task)
            tags = [task["priority"]]
            if task["done"]:
                tags.append("done")

            self.task_tree.insert(
                "",
                tk.END,
                iid=task["id"],
                values=(
                    status,
                    task["title"],
                    task["priority"],
                    task["category"],
                    f"{points} pts",
                    self.format_date(task.get("created_at")),
                ),
                tags=tuple(tags),
            )

        if selected_id and self.task_tree.exists(selected_id):
            self.task_tree.selection_set(selected_id)

    def refresh_summary(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["done"])
        pending = total - completed
        progress = int((completed / total) * 100) if total else 0
        today = today_key()
        today_points = sum(
            to_int(task.get("points_awarded"), self.get_task_points(task))
            for task in self.tasks
            if task["done"] and task.get("completed_at") == today
        )

        self.summary_var.set(f"{completed} de {total} concluidas")
        self.progress_var.set(f"{progress}%")
        self.pending_var.set(str(pending))
        self.today_points_var.set(str(today_points))
        self.points_total_var.set(str(self.points_total))
        self.progress_bar.configure(value=progress)

    def update_action_state(self):
        task = self.get_selected_task()
        state = tk.NORMAL if task else tk.DISABLED

        for button in (
            self.complete_button,
            self.reopen_button,
            self.edit_button,
            self.delete_button,
        ):
            button.configure(state=state)

        if task is None:
            return

        if task["done"]:
            self.complete_button.configure(state=tk.DISABLED)
            self.reopen_button.configure(state=tk.NORMAL)
        else:
            self.complete_button.configure(state=tk.NORMAL)
            self.reopen_button.configure(state=tk.DISABLED)

    def format_date(self, value):
        if not value:
            return "-"
        parts = str(value).split("-")
        if len(parts) != 3:
            return str(value)
        return f"{parts[2]}/{parts[1]}/{parts[0]}"


if __name__ == "__main__":
    try:
        root = tk.Tk()
        RoutineApp(root)
        root.mainloop()
    except Exception:
        import traceback

        traceback.print_exc()
        input("Pressione Enter para encerrar...")
