const state = {
  data: null,
  filter: "Todas",
  editingTaskId: null,
  editingRewardId: null,
  toastTimer: null,
};

const elements = {
  todayLabel: document.querySelector("#todayLabel"),
  completedMetric: document.querySelector("#completedMetric"),
  pendingMetric: document.querySelector("#pendingMetric"),
  progressMetric: document.querySelector("#progressMetric"),
  todayPointsMetric: document.querySelector("#todayPointsMetric"),
  goalMetric: document.querySelector("#goalMetric"),
  levelMetric: document.querySelector("#levelMetric"),
  xpMetric: document.querySelector("#xpMetric"),
  availablePointsMetric: document.querySelector("#availablePointsMetric"),
  spentPointsMetric: document.querySelector("#spentPointsMetric"),
  dayProgressBar: document.querySelector("#dayProgressBar"),
  goalProgressBar: document.querySelector("#goalProgressBar"),
  streakMetric: document.querySelector("#streakMetric"),
  bestStreakMetric: document.querySelector("#bestStreakMetric"),
  motivationText: document.querySelector("#motivationText"),
  taskForm: document.querySelector("#taskForm"),
  formTitle: document.querySelector("#formTitle"),
  taskTitle: document.querySelector("#taskTitle"),
  taskPriority: document.querySelector("#taskPriority"),
  taskCategory: document.querySelector("#taskCategory"),
  taskPinned: document.querySelector("#taskPinned"),
  submitTaskButton: document.querySelector("#submitTaskButton"),
  clearTaskButton: document.querySelector("#clearTaskButton"),
  dailyGoalInput: document.querySelector("#dailyGoalInput"),
  goalForm: document.querySelector("#goalForm"),
  rewardForm: document.querySelector("#rewardForm"),
  rewardFormTitle: document.querySelector("#rewardFormTitle"),
  rewardTitle: document.querySelector("#rewardTitle"),
  rewardCost: document.querySelector("#rewardCost"),
  rewardDescription: document.querySelector("#rewardDescription"),
  submitRewardButton: document.querySelector("#submitRewardButton"),
  clearRewardButton: document.querySelector("#clearRewardButton"),
  filterButtons: document.querySelector("#filterButtons"),
  taskList: document.querySelector("#taskList"),
  historyList: document.querySelector("#historyList"),
  rewardList: document.querySelector("#rewardList"),
  redemptionList: document.querySelector("#redemptionList"),
  storeBalanceMetric: document.querySelector("#storeBalanceMetric"),
  taskTemplate: document.querySelector("#taskTemplate"),
  rewardTemplate: document.querySelector("#rewardTemplate"),
  themeToggle: document.querySelector("#themeToggle"),
  toast: document.querySelector("#toast"),
};

async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message || "Nao foi possivel concluir a acao.");
  }
  return payload;
}

async function loadState(showReadyMessage = false) {
  try {
    const payload = await requestJson(`/api/state?filter=${encodeURIComponent(state.filter)}`);
    state.data = payload;
    render(payload);
    if (showReadyMessage) {
      showToast(payload.message);
    }
  } catch (error) {
    showToast(error.message);
  }
}

function render(data) {
  renderOptions(data);
  renderFilters(data);
  renderSummary(data);
  renderTasks(data.tasks);
  renderHistory(data.history);
  renderRewards(data.rewards, data.wallet);
  renderRedemptions(data.reward_redemptions);
}

function renderOptions(data) {
  fillSelect(elements.taskPriority, data.priorities, "Media");
  fillSelect(elements.taskCategory, data.categories, "Outros");
  elements.dailyGoalInput.min = data.daily_goal_limits.min;
  elements.dailyGoalInput.max = data.daily_goal_limits.max;
  elements.dailyGoalInput.value = data.gamification.daily_goal_points;
}

function fillSelect(select, values, fallback) {
  const current = select.value;
  select.replaceChildren(
    ...values.map((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      return option;
    })
  );
  if (values.includes(current)) {
    select.value = current;
  } else if (values.includes(fallback)) {
    select.value = fallback;
  }
}

function renderFilters(data) {
  elements.filterButtons.replaceChildren(
    ...data.filters.map((filter) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = filter;
      button.classList.toggle("active", filter === state.filter);
      button.addEventListener("click", () => {
        state.filter = filter;
        loadState();
      });
      return button;
    })
  );
}

function renderSummary(data) {
  const summary = data.summary;
  const gamification = data.gamification;
  const level = data.level;
  const wallet = data.wallet;

  elements.todayLabel.textContent = `Painel de hoje - ${data.today_label}`;
  elements.completedMetric.textContent = `${summary.completed_tasks} de ${summary.total_tasks}`;
  elements.pendingMetric.textContent = summary.pending_tasks;
  elements.progressMetric.textContent = `${summary.completion_percentage}%`;
  elements.todayPointsMetric.textContent = summary.points_earned;
  elements.goalMetric.textContent = gamification.daily_goal_label;
  elements.levelMetric.textContent = level.level;
  elements.xpMetric.textContent = level.xp_label;
  elements.availablePointsMetric.textContent = wallet.points_available;
  elements.spentPointsMetric.textContent = wallet.points_spent_label;
  elements.storeBalanceMetric.textContent = wallet.points_available_label;
  elements.streakMetric.textContent = gamification.streak_label;
  elements.bestStreakMetric.textContent = `Melhor: ${gamification.best_streak}`;
  elements.motivationText.textContent = gamification.motivation;
  setMeter(elements.dayProgressBar, summary.completion_percentage);
  setMeter(elements.goalProgressBar, gamification.daily_goal_progress);
}

function setMeter(element, value) {
  element.style.width = `${Math.max(0, Math.min(100, value))}%`;
}

function renderTasks(tasks) {
  const columns = getTaskColumns(tasks);
  elements.taskList.classList.toggle("single-column", columns.length === 1);
  elements.taskList.replaceChildren(...columns.map(renderTaskColumn));
}

function getTaskColumns(tasks) {
  const pending = tasks.filter((task) => !task.done);
  const completed = tasks.filter((task) => task.done);

  if (state.filter === "Pendentes") {
    return [{ key: "pending", title: "Pendentes", tasks: pending }];
  }

  if (state.filter === "Concluidas") {
    return [{ key: "done", title: "Concluidas", tasks: completed }];
  }

  return [
    { key: "pending", title: "Pendentes", tasks: pending },
    { key: "done", title: "Concluidas", tasks: completed },
  ];
}

function renderTaskColumn(column) {
  const section = document.createElement("section");
  section.className = `task-column ${column.key}`;
  section.setAttribute("aria-label", column.title);

  const header = document.createElement("div");
  header.className = "task-column-header";

  const title = document.createElement("h3");
  title.textContent = column.title;

  const count = document.createElement("span");
  count.textContent = column.tasks.length;

  const cards = document.createElement("div");
  cards.className = "task-column-cards";

  if (column.tasks.length) {
    cards.replaceChildren(...column.tasks.map(renderTaskCard));
  } else {
    const empty = document.createElement("div");
    empty.className = "empty-state compact";
    empty.textContent = column.key === "pending" ? "Nenhuma tarefa pendente." : "Nenhuma tarefa concluida.";
    cards.replaceChildren(empty);
  }

  header.append(title, count);
  section.append(header, cards);
  return section;
}

function renderTaskCard(task) {
  const fragment = elements.taskTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".task-card");
  const title = fragment.querySelector("h3");
  const meta = fragment.querySelector(".task-meta");
  const completeButton = fragment.querySelector('[data-action="complete"]');
  const editButton = fragment.querySelector('[data-action="edit"]');
  const pinButton = fragment.querySelector('[data-action="pin"]');
  const deleteButton = fragment.querySelector('[data-action="delete"]');

  card.dataset.id = task.id;
  card.classList.toggle("done", task.done);
  card.classList.toggle("pinned", task.pinned);
  title.textContent = task.title;
  completeButton.textContent = task.done ? "Reabrir" : "Concluir";
  completeButton.dataset.action = task.done ? "reopen" : "complete";
  pinButton.textContent = task.pinned ? "Desafixar" : "Fixar";

  for (const button of [completeButton, editButton, pinButton, deleteButton]) {
    button.dataset.id = task.id;
  }

  meta.replaceChildren(
    metaPill(task.priority, `priority-${task.priority}`),
    metaPill(task.category),
    metaPill(task.points_label),
    metaPill(task.done ? task.completed_label : task.created_label)
  );

  return fragment;
}

function metaPill(text, className) {
  const span = document.createElement("span");
  span.textContent = text;
  if (className) {
    span.classList.add(className);
  }
  return span;
}

function renderHistory(history) {
  if (!history.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "Historico vazio.";
    elements.historyList.replaceChildren(empty);
    return;
  }

  const rows = history.slice(0, 8).map((entry) => {
    const row = document.createElement("div");
    row.className = "history-row";
    row.append(
      textCell(entry.date_label, true),
      textCell(`${entry.completed_tasks}/${entry.total_tasks}`),
      textCell(`${entry.points_earned} pts`),
      textCell(`${entry.completion_percentage}%`)
    );
    return row;
  });
  elements.historyList.replaceChildren(...rows);
}

function renderRewards(rewards, wallet) {
  if (!rewards.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "Nenhuma recompensa cadastrada.";
    elements.rewardList.replaceChildren(empty);
    return;
  }

  const cards = rewards.map((reward) => {
    const fragment = elements.rewardTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".reward-card");
    const title = fragment.querySelector("h3");
    const description = fragment.querySelector(".reward-description");
    const meta = fragment.querySelector(".reward-meta");
    const redeemButton = fragment.querySelector('[data-reward-action="redeem"]');
    const editButton = fragment.querySelector('[data-reward-action="edit"]');
    const deleteButton = fragment.querySelector('[data-reward-action="delete"]');

    card.dataset.id = reward.id;
    title.textContent = reward.title;
    description.textContent = reward.description || "";
    redeemButton.disabled = !reward.can_redeem;
    redeemButton.title = reward.can_redeem ? "Resgatar recompensa" : "Pontos insuficientes";

    for (const button of [redeemButton, editButton, deleteButton]) {
      button.dataset.id = reward.id;
    }

    meta.replaceChildren(
      metaPill(reward.cost_label, "cost-pill"),
      metaPill(reward.can_redeem ? "Disponivel" : `${wallet.points_available} pts disponiveis`),
      metaPill(reward.created_label)
    );

    return fragment;
  });

  elements.rewardList.replaceChildren(...cards);
}

function renderRedemptions(redemptions) {
  if (!redemptions.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "Nenhum resgate ainda.";
    elements.redemptionList.replaceChildren(empty);
    return;
  }

  const rows = redemptions.slice(0, 10).map((redemption) => {
    const row = document.createElement("div");
    row.className = "redemption-row";
    row.append(
      textCell(redemption.reward_title, true),
      textCell(redemption.cost_label),
      textCell(redemption.redeemed_label)
    );
    return row;
  });
  elements.redemptionList.replaceChildren(...rows);
}

function textCell(text, strong = false) {
  const element = document.createElement(strong ? "strong" : "span");
  element.textContent = text;
  return element;
}

function resetTaskForm() {
  state.editingTaskId = null;
  elements.formTitle.textContent = "Nova tarefa";
  elements.submitTaskButton.textContent = "Adicionar";
  elements.taskForm.reset();
  elements.taskPriority.value = "Media";
  elements.taskCategory.value = "Outros";
}

function resetRewardForm() {
  state.editingRewardId = null;
  elements.rewardFormTitle.textContent = "Nova recompensa";
  elements.submitRewardButton.textContent = "Adicionar";
  elements.rewardForm.reset();
  elements.rewardCost.value = "10";
}

function editTask(taskId) {
  const task = state.data.tasks.find((item) => item.id === taskId);
  if (!task) {
    showToast("A tarefa selecionada nao existe mais.");
    return;
  }
  state.editingTaskId = taskId;
  elements.formTitle.textContent = "Editar tarefa";
  elements.submitTaskButton.textContent = "Salvar";
  elements.taskTitle.value = task.title;
  elements.taskPriority.value = task.priority;
  elements.taskCategory.value = task.category;
  elements.taskPinned.checked = task.pinned;
  elements.taskTitle.focus();
}

function editReward(rewardId) {
  const reward = state.data.rewards.find((item) => item.id === rewardId);
  if (!reward) {
    showToast("A recompensa selecionada nao existe mais.");
    return;
  }
  state.editingRewardId = rewardId;
  elements.rewardFormTitle.textContent = "Editar recompensa";
  elements.submitRewardButton.textContent = "Salvar";
  elements.rewardTitle.value = reward.title;
  elements.rewardCost.value = reward.cost;
  elements.rewardDescription.value = reward.description || "";
  elements.rewardTitle.focus();
}

async function submitTask(event) {
  event.preventDefault();
  const payload = {
    title: elements.taskTitle.value.trim(),
    priority: elements.taskPriority.value,
    category: elements.taskCategory.value,
    pinned: elements.taskPinned.checked,
  };

  const path = state.editingTaskId ? `/api/tasks/${state.editingTaskId}` : "/api/tasks";
  const method = state.editingTaskId ? "PUT" : "POST";
  await mutate(path, { method, body: JSON.stringify(payload) });
  resetTaskForm();
}

async function submitGoal(event) {
  event.preventDefault();
  await mutate("/api/settings/daily-goal", {
    method: "PUT",
    body: JSON.stringify({
      daily_goal_points: elements.dailyGoalInput.value,
    }),
  });
}

async function submitReward(event) {
  event.preventDefault();
  const payload = {
    title: elements.rewardTitle.value.trim(),
    cost: elements.rewardCost.value,
    description: elements.rewardDescription.value.trim(),
  };

  const path = state.editingRewardId ? `/api/rewards/${state.editingRewardId}` : "/api/rewards";
  const method = state.editingRewardId ? "PUT" : "POST";
  await mutate(path, { method, body: JSON.stringify(payload) });
  resetRewardForm();
}

async function mutate(path, options) {
  try {
    const payload = await requestJson(path, options);
    await loadState();
    showToast(payload.message);
  } catch (error) {
    showToast(error.message);
  }
}

async function handleTaskAction(event) {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }

  const taskId = button.dataset.id;
  const action = button.dataset.action;
  if (action === "edit") {
    editTask(taskId);
    return;
  }

  if (action === "delete" && !window.confirm("Excluir esta tarefa?")) {
    return;
  }

  const routes = {
    complete: [`/api/tasks/${taskId}/complete`, "PATCH"],
    reopen: [`/api/tasks/${taskId}/reopen`, "PATCH"],
    pin: [`/api/tasks/${taskId}/pin`, "PATCH"],
    delete: [`/api/tasks/${taskId}`, "DELETE"],
  };
  const route = routes[action];
  if (!route) {
    return;
  }
  await mutate(route[0], { method: route[1] });
}

async function handleRewardAction(event) {
  const button = event.target.closest("button[data-reward-action]");
  if (!button) {
    return;
  }

  const rewardId = button.dataset.id;
  const action = button.dataset.rewardAction;
  if (action === "edit") {
    editReward(rewardId);
    return;
  }

  if (action === "delete" && !window.confirm("Excluir esta recompensa?")) {
    return;
  }

  const routes = {
    redeem: [`/api/rewards/${rewardId}/redeem`, "PATCH"],
    delete: [`/api/rewards/${rewardId}`, "DELETE"],
  };
  const route = routes[action];
  if (!route) {
    return;
  }
  await mutate(route[0], { method: route[1] });
}

function setupTheme() {
  const savedTheme = localStorage.getItem("rotina-theme") || "light";
  document.documentElement.dataset.theme = savedTheme;
  elements.themeToggle.textContent = savedTheme === "dark" ? "Modo claro" : "Modo escuro";

  elements.themeToggle.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem("rotina-theme", nextTheme);
    elements.themeToggle.textContent = nextTheme === "dark" ? "Modo claro" : "Modo escuro";
  });
}

function showToast(message) {
  elements.toast.textContent = message || "Pronto";
  elements.toast.classList.add("visible");
  window.clearTimeout(state.toastTimer);
  state.toastTimer = window.setTimeout(() => {
    elements.toast.classList.remove("visible");
  }, 2600);
}

elements.taskForm.addEventListener("submit", submitTask);
elements.clearTaskButton.addEventListener("click", resetTaskForm);
elements.goalForm.addEventListener("submit", submitGoal);
elements.rewardForm.addEventListener("submit", submitReward);
elements.clearRewardButton.addEventListener("click", resetRewardForm);
elements.taskList.addEventListener("click", handleTaskAction);
elements.rewardList.addEventListener("click", handleRewardAction);

setupTheme();
resetRewardForm();
loadState(true);
