import json
import os
import tkinter as tk
from tkinter import messagebox

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")


class RoutineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rotina Diaria")
        self.root.geometry("520x420")
        self.root.resizable(False, False)

        self.tasks = []
        self.points = 0

        self._create_ui()
        self._load_data()

    def _create_ui(self):
        top = tk.Frame(self.root, pady=10)
        top.pack(fill="x")

        self.task_entry = tk.Entry(top, width=40)
        self.task_entry.pack(side="left", padx=(10, 5), expand=True, fill="x")
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        tk.Button(top, text="Adicionar", command=self.add_task).pack(side="left", padx=(0, 10))

        points_frame = tk.Frame(self.root)
        points_frame.pack(fill="x")

        tk.Label(points_frame, text="Pontos:", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
        self.points_var = tk.StringVar(value="0")
        tk.Label(points_frame, textvariable=self.points_var, font=("Arial", 12)).pack(side="left")

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(list_frame, height=15)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self.root, pady=10)
        btn_frame.pack()

        tk.Button(btn_frame, text="Concluir", command=self.complete_task).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remover", command=self.remove_task).pack(side="left", padx=5)

    def _load_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.tasks = data.get("tasks", [])
                    self.points = data.get("points", 0)
            except (json.JSONDecodeError, OSError):
                self.tasks = []
                self.points = 0

        self.refresh_list()

    def _save_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump({"tasks": self.tasks, "points": self.points}, file, ensure_ascii=False, indent=2)

    def add_task(self):
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("Aviso", "Digite uma tarefa primeiro.")
            return

        self.tasks.append({"task": task, "done": False})
        self.task_entry.delete(0, tk.END)
        self.refresh_list()
        self._save_data()

    def complete_task(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir.")
            return

        index = selected[0]
        task = self.tasks[index]
        if task["done"]:
            messagebox.showinfo("Info", "Essa tarefa ja esta concluida.")
            return

        task["done"] = True
        self.points += 10
        self.refresh_list()
        self._save_data()

    def remove_task(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")
            return

        index = selected[0]
        del self.tasks[index]
        self.refresh_list()
        self._save_data()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for item in self.tasks:
            status = "v" if item["done"] else "o"
            self.listbox.insert(tk.END, f"{status} {item['task']}")

        self.points_var.set(str(self.points))


if __name__ == "__main__":
    try:
        root = tk.Tk()
        RoutineApp(root)
        root.mainloop()
    except Exception:
        import traceback
        traceback.print_exc()
        input("Pressione Enter para encerrar...")
