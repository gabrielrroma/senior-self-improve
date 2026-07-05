(function () {
  const { useEffect, useMemo, useRef, useState } = React;
  const h = React.createElement;

  const POMODORO_STORAGE_KEY = "rotina-pomodoro-session";
  const ACTIVE_VIEW_KEY = "rotina-active-view";
  const THEME_KEY = "rotina-theme";
  const DEFAULT_PROFILE_NAME = "Rotina Diaria";
  const VIEW_ALIASES = { progress: "profile" };

  const POMODORO_MODES = {
    focus: {
      label: "Foco",
      seconds: 25 * 60,
      nextLabel: "Pausa curta depois",
    },
    short_break: {
      label: "Pausa curta",
      seconds: 5 * 60,
      nextLabel: "Foco depois",
    },
    long_break: {
      label: "Pausa longa",
      seconds: 15 * 60,
      nextLabel: "Foco depois",
    },
  };

  const emptyTaskDraft = {
    title: "",
    priority: "Media",
    category: "Outros",
    pinned: false,
  };

  const emptyRewardDraft = {
    title: "",
    cost: "10",
    description: "",
    image_url: "",
  };

  const emptyData = {
    message: "Carregando...",
    today_label: "Hoje",
    filters: ["Todas", "Pendentes", "Concluidas"],
    selected_filter: "Todas",
    categories: ["Estudos", "Trabalho", "Saude", "Casa", "Lazer", "Outros"],
    priorities: ["Baixa", "Media", "Alta"],
    daily_goal_limits: { min: 5, max: 500 },
    weekly_goal_limits: { min: 1, max: 200 },
    summary: {
      completed_tasks: 0,
      total_tasks: 0,
      pending_tasks: 0,
      points_earned: 0,
      completion_percentage: 0,
    },
    gamification: {
      daily_goal_points: 30,
      daily_goal_progress: 0,
      daily_goal_label: "0/30 pts",
      weekly_goal_tasks: 20,
      weekly_goal_progress: 0,
      weekly_goal_label: "0/20 tarefas",
      weekly_goal_bonus_points: 0,
      streak_count: 0,
      streak_label: "0 dias",
      best_streak: 0,
      motivation: "Comece com uma tarefa simples.",
    },
    wallet: {
      points_total: 0,
      points_spent: 0,
      points_available: 0,
      points_available_label: "0 pts",
      points_spent_label: "0 usados",
    },
    level: {
      level: 1,
      xp_label: "0 XP total",
      detail_label: "XP em progresso",
    },
    profile: {
      name: "",
      display_name: DEFAULT_PROFILE_NAME,
      avatar_url: "",
    },
    tasks: [],
    focus_tasks: [],
    history: [],
    weekly_stats: {
      week_label: "Semana atual",
      completed_tasks: 0,
      points_earned: 0,
      completion_percentage: 0,
      goal_progress: 0,
      goal_label: "0/20 tarefas",
      bonus_label: "0 pts",
      bonus_awarded: false,
      best_day: { label: "Sem dados" },
      top_category: { label: "Sem dados" },
    },
    achievements: [],
    achievement_summary: { label: "0/0 desbloqueadas" },
    rewards: [],
    reward_redemptions: [],
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

  function App() {
    const [data, setData] = useState(null);
    const viewData = data || emptyData;
    const [filter, setFilter] = useState("Todas");
    const [activeView, setActiveViewState] = useState(
      () => normalizeView(localStorage.getItem(ACTIVE_VIEW_KEY) || "routine")
    );
    const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || "light");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [toast, setToast] = useState({ message: "Pronto", visible: false });
    const [taskComposerOpen, setTaskComposerOpen] = useState(false);
    const [taskDraft, setTaskDraft] = useState(emptyTaskDraft);
    const [editingTaskId, setEditingTaskId] = useState("");
    const [rewardDraft, setRewardDraft] = useState(emptyRewardDraft);
    const [editingRewardId, setEditingRewardId] = useState("");
    const [profileDraft, setProfileDraft] = useState({ name: DEFAULT_PROFILE_NAME, avatar_url: "" });
    const [dailyGoalDraft, setDailyGoalDraft] = useState("");
    const [weeklyGoalDraft, setWeeklyGoalDraft] = useState("");
    const [focus, setFocus] = useState(loadFocusSession);
    const toastTimerRef = useRef(null);
    const taskTitleRef = useRef(null);

    useEffect(() => {
      document.documentElement.dataset.theme = theme;
      localStorage.setItem(THEME_KEY, theme);
    }, [theme]);

    useEffect(() => {
      loadState(true, filter);
      return () => {
        window.clearTimeout(toastTimerRef.current);
      };
    }, []);

    useEffect(() => {
      if (!data) {
        return;
      }
      const profile = data.profile || {};
      setProfileDraft({
        name: getProfileDisplayName(profile),
        avatar_url: String(profile.avatar_url || "").trim(),
      });
      setDailyGoalDraft(String(data.gamification?.daily_goal_points ?? ""));
      setWeeklyGoalDraft(String(data.gamification?.weekly_goal_tasks ?? ""));
    }, [data]);

    useEffect(() => {
      localStorage.setItem(POMODORO_STORAGE_KEY, JSON.stringify(focus));
    }, [focus]);

    useEffect(() => {
      const tasks = getFocusTasks(viewData);
      const pendingTasks = tasks.filter((task) => !task.done);
      const selectedTask = tasks.find((task) => task.id === focus.taskId);
      if (!selectedTask || selectedTask.done) {
        const nextTaskId = pendingTasks[0]?.id || "";
        if (nextTaskId !== focus.taskId) {
          setFocus((current) => ({ ...current, taskId: nextTaskId }));
        }
      }
    }, [data, focus.taskId]);

    useEffect(() => {
      if (!focus.isRunning) {
        return undefined;
      }

      const intervalId = window.setInterval(() => {
        setFocus((current) => {
          if (!current.isRunning) {
            return current;
          }
          const applied = applyFocusElapsed(current);
          if (applied.message) {
            window.setTimeout(() => notify(applied.message), 0);
          }
          return applied.focus;
        });
      }, 1000);

      return () => window.clearInterval(intervalId);
    }, [focus.isRunning]);

    useEffect(() => {
      if (taskComposerOpen) {
        window.setTimeout(() => taskTitleRef.current?.focus(), 0);
      }
    }, [taskComposerOpen, editingTaskId]);

    function notify(message) {
      setToast({ message: message || "Pronto", visible: true });
      window.clearTimeout(toastTimerRef.current);
      toastTimerRef.current = window.setTimeout(() => {
        setToast((current) => ({ ...current, visible: false }));
      }, 2600);
    }

    async function loadState(showReadyMessage = false, selectedFilter = filter) {
      setIsLoading(true);
      try {
        const payload = await requestJson(`/api/state?filter=${encodeURIComponent(selectedFilter)}`);
        setData(payload);
        if (showReadyMessage) {
          notify(payload.message);
        }
        return payload;
      } catch (error) {
        notify(error.message);
        return null;
      } finally {
        setIsLoading(false);
      }
    }

    async function mutate(path, options = {}) {
      setIsSaving(true);
      try {
        const payload = await requestJson(path, options);
        await loadState(false, filter);
        notify(payload.message);
        return true;
      } catch (error) {
        notify(error.message);
        return false;
      } finally {
        setIsSaving(false);
      }
    }

    function setActiveView(view) {
      const nextView = normalizeView(view);
      setActiveViewState(nextView);
      localStorage.setItem(ACTIVE_VIEW_KEY, nextView);
    }

    function changeFilter(nextFilter) {
      setFilter(nextFilter);
      loadState(false, nextFilter);
    }

    function openNewTaskComposer() {
      setActiveView("routine");
      setEditingTaskId("");
      setTaskDraft(emptyTaskDraft);
      setTaskComposerOpen(true);
    }

    function closeTaskComposer() {
      setEditingTaskId("");
      setTaskDraft(emptyTaskDraft);
      setTaskComposerOpen(false);
    }

    function editTask(task) {
      setActiveView("routine");
      setEditingTaskId(task.id);
      setTaskDraft({
        title: task.title,
        priority: task.priority || "Media",
        category: task.category || "Outros",
        pinned: Boolean(task.pinned),
      });
      setTaskComposerOpen(true);
    }

    async function submitTask(event) {
      event.preventDefault();
      const payload = {
        title: taskDraft.title.trim(),
        priority: taskDraft.priority || "Media",
        category: taskDraft.category || "Outros",
        pinned: Boolean(taskDraft.pinned),
      };
      if (!payload.title) {
        notify("Digite uma tarefa primeiro.");
        return;
      }

      const path = editingTaskId ? `/api/tasks/${editingTaskId}` : "/api/tasks";
      const method = editingTaskId ? "PUT" : "POST";
      const saved = await mutate(path, { method, body: JSON.stringify(payload) });
      if (saved) {
        closeTaskComposer();
      }
    }

    async function runTaskAction(task, action) {
      if (action === "edit") {
        editTask(task);
        return;
      }
      if (action === "focus") {
        startFocusForTask(task.id);
        return;
      }
      if (action === "delete" && !window.confirm("Excluir esta tarefa?")) {
        return;
      }

      const routes = {
        complete: [`/api/tasks/${task.id}/complete`, "PATCH"],
        reopen: [`/api/tasks/${task.id}/reopen`, "PATCH"],
        pin: [`/api/tasks/${task.id}/pin`, "PATCH"],
        delete: [`/api/tasks/${task.id}`, "DELETE"],
      };
      const route = routes[action];
      if (route) {
        await mutate(route[0], { method: route[1] });
      }
    }

    async function saveProfile(draft = profileDraft) {
      await mutate("/api/profile", {
        method: "PUT",
        body: JSON.stringify({
          name: draft.name.trim(),
          avatar_url: draft.avatar_url.trim(),
        }),
      });
    }

    async function submitProfile(event) {
      event.preventDefault();
      await saveProfile();
    }

    async function submitDailyGoal(event) {
      event.preventDefault();
      await mutate("/api/settings/daily-goal", {
        method: "PUT",
        body: JSON.stringify({ daily_goal_points: dailyGoalDraft }),
      });
    }

    async function submitWeeklyGoal(event) {
      event.preventDefault();
      await mutate("/api/settings/weekly-goal", {
        method: "PUT",
        body: JSON.stringify({ weekly_goal_tasks: weeklyGoalDraft }),
      });
    }

    function editReward(reward) {
      setActiveView("rewards");
      setEditingRewardId(reward.id);
      setRewardDraft({
        title: reward.title,
        cost: String(reward.cost),
        description: reward.description || "",
        image_url: reward.image_url || "",
      });
    }

    function resetRewardForm() {
      setEditingRewardId("");
      setRewardDraft(emptyRewardDraft);
    }

    async function submitReward(event) {
      event.preventDefault();
      const payload = {
        title: rewardDraft.title.trim(),
        cost: rewardDraft.cost,
        description: rewardDraft.description.trim(),
        image_url: rewardDraft.image_url.trim(),
      };
      if (!payload.title) {
        notify("Digite o nome da recompensa.");
        return;
      }

      const path = editingRewardId ? `/api/rewards/${editingRewardId}` : "/api/rewards";
      const method = editingRewardId ? "PUT" : "POST";
      const saved = await mutate(path, { method, body: JSON.stringify(payload) });
      if (saved) {
        resetRewardForm();
      }
    }

    async function runRewardAction(reward, action) {
      if (action === "edit") {
        editReward(reward);
        return;
      }
      if (action === "delete" && !window.confirm("Excluir esta recompensa?")) {
        return;
      }
      const routes = {
        redeem: [`/api/rewards/${reward.id}/redeem`, "PATCH"],
        delete: [`/api/rewards/${reward.id}`, "DELETE"],
      };
      const route = routes[action];
      if (route) {
        await mutate(route[0], { method: route[1] });
      }
    }

    function startFocusSession() {
      const selectedTask = getFocusTasks(viewData).find((task) => task.id === focus.taskId && !task.done);
      if (focus.mode === "focus" && !selectedTask) {
        notify("Escolha uma tarefa pendente para focar.");
        return;
      }

      setFocus((current) => ({
        ...current,
        secondsRemaining: current.secondsRemaining <= 0 ? getFocusModeConfig(current.mode).seconds : current.secondsRemaining,
        isRunning: true,
        lastTick: Date.now(),
      }));
    }

    function pauseFocusSession() {
      setFocus((current) => {
        if (!current.isRunning) {
          return current;
        }
        const applied = applyFocusElapsed(current);
        if (applied.message) {
          window.setTimeout(() => notify(applied.message), 0);
          return applied.focus;
        }
        return {
          ...applied.focus,
          isRunning: false,
          lastTick: null,
        };
      });
    }

    function resetFocusSession() {
      setFocus((current) => ({
        ...current,
        isRunning: false,
        lastTick: null,
        secondsRemaining: getFocusModeConfig(current.mode).seconds,
      }));
    }

    function skipFocusStep() {
      setFocus((current) => {
        const next = finishFocusInterval(current);
        window.setTimeout(() => notify(next.message), 0);
        return next.focus;
      });
    }

    function setFocusMode(mode) {
      if (!POMODORO_MODES[mode]) {
        return;
      }
      setFocus((current) => ({
        ...current,
        mode,
        secondsRemaining: POMODORO_MODES[mode].seconds,
        isRunning: false,
        lastTick: null,
      }));
    }

    function setFocusTask(taskId) {
      setFocus((current) => ({ ...current, taskId }));
    }

    function startFocusForTask(taskId) {
      setFocus((current) => ({
        ...current,
        taskId,
        mode: "focus",
        secondsRemaining: POMODORO_MODES.focus.seconds,
        isRunning: false,
        lastTick: null,
      }));
      setActiveView("focus");
    }

    async function completeFocusTask() {
      const selectedTask = getFocusTasks(viewData).find((task) => task.id === focus.taskId && !task.done);
      if (!selectedTask) {
        return;
      }
      setFocus((current) => ({ ...current, isRunning: false, lastTick: null }));
      await mutate(`/api/tasks/${selectedTask.id}/complete`, { method: "PATCH" });
    }

    const navItems = [
      { view: "routine", id: "routineTab", label: "Painel", icon: "today", controls: "routineView" },
      { view: "focus", id: "focusTab", label: "Foco", icon: "focus", controls: "focusView" },
      { view: "profile", id: "profileTab", label: "Perfil", icon: "profile", controls: "profileView" },
      {
        view: "achievements",
        id: "achievementsTab",
        label: "Conquistas",
        icon: "achievements",
        controls: "achievementsView",
      },
      { view: "rewards", id: "rewardsTab", label: "Recompensas", icon: "rewards", controls: "rewardsView" },
    ];

    const currentThemeLabel = theme === "dark" ? "Claro" : "Escuro";
    const profileName = profileDraft.name || DEFAULT_PROFILE_NAME;
    const wallet = viewData.wallet || emptyData.wallet;
    const summary = viewData.summary || emptyData.summary;
    const gamification = viewData.gamification || emptyData.gamification;
    const level = viewData.level || emptyData.level;
    const weekly = viewData.weekly_stats || emptyData.weekly_stats;
    const focusTasks = getFocusTasks(viewData);

    return h(
      React.Fragment,
      null,
      h(
        "div",
        { className: "app-shell" },
        h(
          "header",
          { className: "app-navbar" },
          h(
            "div",
            { className: "navbar-profile" },
            h(
              "button",
              {
                className: "profile-avatar-button",
                id: "profileAvatarButton",
                type: "button",
                "aria-label": "Abrir perfil",
                onClick: () => setActiveView("profile"),
              },
              h(ProfileAvatar, { name: profileName, avatarUrl: profileDraft.avatar_url })
            ),
            h(
              "div",
              { className: "profile-heading" },
              h("input", {
                className: "profile-name-input",
                id: "profileNameInput",
                name: "name",
                type: "text",
                maxLength: 80,
                "aria-label": "Nome do usuario",
                placeholder: "Seu nome",
                value: profileDraft.name,
                onChange: (event) => setProfileDraft({ ...profileDraft, name: event.target.value }),
                onBlur: () => saveProfile(),
                onKeyDown: (event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    event.currentTarget.blur();
                  }
                },
              }),
              h("p", { className: "eyebrow", id: "todayLabel" }, `Hoje - ${viewData.today_label || "Hoje"}`)
            ),
            h(
              "button",
              {
                className: "ghost-button theme-toggle",
                id: "themeToggle",
                type: "button",
                title: `Alternar para modo ${currentThemeLabel.toLowerCase()}`,
                "aria-label": `Alternar para modo ${currentThemeLabel.toLowerCase()}`,
                onClick: () => setTheme(theme === "dark" ? "light" : "dark"),
              },
              currentThemeLabel
            )
          ),
          h(
            "div",
            { className: "navbar-actions" },
            h(
              "button",
              {
                className: `primary-button navbar-new-task${taskComposerOpen ? " active" : ""}`,
                id: "openTaskComposerButton",
                type: "button",
                onClick: openNewTaskComposer,
              },
              h(Icon, { name: "plus", className: "action-icon" }),
              h("span", null, "Nova tarefa")
            )
          ),
          h(
            "div",
            { className: "nav-section" },
            h("p", { className: "nav-section-label" }, "Espacos"),
            h(
              "nav",
              { className: "main-nav", "aria-label": "Navegacao principal", role: "tablist" },
              navItems.map((item) =>
                h(
                  "button",
                  {
                    key: item.view,
                    className: `nav-tab${activeView === item.view ? " active" : ""}`,
                    id: item.id,
                    type: "button",
                    role: "tab",
                    "aria-selected": activeView === item.view,
                    "aria-current": activeView === item.view ? "page" : undefined,
                    "aria-controls": item.controls,
                    "data-nav-view": item.view,
                    onClick: () => setActiveView(item.view),
                  },
                  h(Icon, { name: item.icon, className: `nav-icon ${item.icon}-icon` }),
                  h("span", null, item.label)
                )
              )
            )
          ),
          h(
            "div",
            { className: "nav-summary" },
            h("p", { className: "nav-section-label" }, "Carteira"),
            h(
              "div",
              { className: "nav-wallet", "aria-label": "Carteira de pontos" },
              h("span", null, "Saldo"),
              h("strong", { id: "availablePointsMetric" }, wallet.points_available_label || "0 pts"),
              h("small", { id: "spentPointsMetric" }, wallet.points_spent_label || "0 usados")
            )
          )
        ),
        h(
          "main",
          null,
          h(RoutineView, {
            active: activeView === "routine",
            data: viewData,
            filter,
            isLoading,
            isSaving,
            taskComposerOpen,
            taskDraft,
            editingTaskId,
            taskTitleRef,
            onFilterChange: changeFilter,
            onTaskDraftChange: setTaskDraft,
            onSubmitTask: submitTask,
            onCloseTaskComposer: closeTaskComposer,
            onTaskAction: runTaskAction,
            summary,
            gamification,
            level,
          }),
          h(FocusView, {
            active: activeView === "focus",
            data: viewData,
            focus,
            tasks: focusTasks,
            isSaving,
            onFocusTaskChange: setFocusTask,
            onFocusModeChange: setFocusMode,
            onStart: startFocusSession,
            onPause: pauseFocusSession,
            onReset: resetFocusSession,
            onSkip: skipFocusStep,
            onCompleteTask: completeFocusTask,
          }),
          h(ProfileView, {
            active: activeView === "profile",
            data: viewData,
            profileDraft,
            dailyGoalDraft,
            weeklyGoalDraft,
            isSaving,
            onProfileDraftChange: setProfileDraft,
            onDailyGoalChange: setDailyGoalDraft,
            onWeeklyGoalChange: setWeeklyGoalDraft,
            onSubmitProfile: submitProfile,
            onSubmitDailyGoal: submitDailyGoal,
            onSubmitWeeklyGoal: submitWeeklyGoal,
            gamification,
            weekly,
          }),
          h(AchievementsView, {
            active: activeView === "achievements",
            data: viewData,
          }),
          h(RewardsView, {
            active: activeView === "rewards",
            data: viewData,
            rewardDraft,
            editingRewardId,
            isSaving,
            onRewardDraftChange: setRewardDraft,
            onSubmitReward: submitReward,
            onResetReward: resetRewardForm,
            onRewardAction: runRewardAction,
          })
        )
      ),
      h(
        "div",
        {
          className: `toast${toast.visible ? " visible" : ""}`,
          id: "toast",
          role: "status",
          "aria-live": "polite",
        },
        toast.message
      )
    );
  }

  function RoutineView(props) {
    const {
      active,
      data,
      filter,
      isLoading,
      isSaving,
      taskComposerOpen,
      taskDraft,
      editingTaskId,
      taskTitleRef,
      onFilterChange,
      onTaskDraftChange,
      onSubmitTask,
      onCloseTaskComposer,
      onTaskAction,
      summary,
      gamification,
      level,
    } = props;

    const columns = useMemo(() => getTaskColumns(data.tasks || [], filter), [data.tasks, filter]);

    return h(
      "section",
      {
        className: `tab-view${active ? " active" : ""}`,
        id: "routineView",
        role: "tabpanel",
        "aria-labelledby": "routineTab",
        "data-view-panel": "routine",
        hidden: !active,
      },
      h(
        "section",
        { className: "dashboard-hero", "aria-labelledby": "routineHeading" },
        h(
          "div",
          { className: "hero-copy" },
          h("span", { className: "hero-label" }, "Rotina diaria"),
          h("h1", { id: "routineHeading" }, "Painel do dia"),
          h(
            "p",
            null,
            isLoading
              ? "Sincronizando suas tarefas e progresso local."
              : "Veja o que precisa de foco agora, acompanhe seus pontos e mantenha a rotina andando sem friccao."
          )
        ),
        h(
          "div",
          { className: "hero-note", "aria-label": "Atalho de uso" },
          h("span", null, "Fluxo sugerido"),
          h("strong", null, "Planejar, concluir, resgatar.")
        )
      ),
      h(
        "section",
        { className: "metrics-grid daily-metrics", "aria-label": "Resumo do dia" },
        h(
          "article",
          { className: "metric-card" },
          h("span", null, "Concluidas"),
          h("strong", id("completedMetric"), `${summary.completed_tasks || 0} de ${summary.total_tasks || 0}`),
          h(Meter, { id: "dayProgressBar", value: summary.completion_percentage || 0 })
        ),
        h(
          "article",
          { className: "metric-card" },
          h("span", null, "Pendentes"),
          h("strong", id("pendingMetric"), summary.pending_tasks || 0),
          h("small", id("progressMetric"), `${summary.completion_percentage || 0}%`)
        ),
        h(
          "article",
          { className: "metric-card" },
          h("span", null, "Pontos hoje"),
          h("strong", id("todayPointsMetric"), summary.points_earned || 0),
          h("small", id("goalMetric"), gamification.daily_goal_label || "0/0 pts")
        ),
        h(
          "article",
          { className: "metric-card accent" },
          h("span", null, "Nivel"),
          h("strong", id("levelMetric"), level.level || 1),
          h("small", id("xpMetric"), level.xp_label || "0 XP total")
        )
      ),
      h(
        "section",
        { className: "workspace-grid" },
        h(
          "aside",
          { className: "side-stack" },
          h(
            "section",
            { className: "tool-panel" },
            h(
              "div",
              { className: "panel-heading" },
              h("h2", null, "Historico"),
              h("span", id("bestStreakMetric"), `Melhor: ${gamification.best_streak || 0}`)
            ),
            h(HistoryList, { history: data.history || [] })
          )
        ),
        h(
          "section",
          { className: "right-stack" },
          h(
            "section",
            { className: "tasks-panel" },
            h(
              "div",
              { className: "task-toolbar" },
              h("h2", null, "Tarefas"),
              h(
                "div",
                { className: "task-toolbar-actions" },
                h(
                  "div",
                  { className: "segmented-control", id: "filterButtons", role: "tablist" },
                  (data.filters || []).map((item) =>
                    h(
                      "button",
                      {
                        key: item,
                        className: item === filter ? "active" : "",
                        type: "button",
                        role: "tab",
                        "aria-selected": item === filter,
                        onClick: () => onFilterChange(item),
                      },
                      item
                    )
                  )
                )
              )
            ),
            h(TaskComposer, {
              data,
              draft: taskDraft,
              editingTaskId,
              isOpen: taskComposerOpen,
              isSaving,
              inputRef: taskTitleRef,
              onChange: onTaskDraftChange,
              onSubmit: onSubmitTask,
              onCancel: onCloseTaskComposer,
            }),
            h(
              "div",
              { className: `task-list${columns.length === 1 ? " single-column" : ""}`, id: "taskList" },
              columns.map((column) =>
                h(TaskColumn, {
                  key: column.key,
                  column,
                  isSaving,
                  onTaskAction,
                })
              )
            )
          )
        )
      )
    );
  }

  function TaskComposer({ data, draft, editingTaskId, isOpen, isSaving, inputRef, onChange, onSubmit, onCancel }) {
    return h(
      "section",
      { className: `task-composer${isOpen ? " open" : ""}`, id: "taskComposer", hidden: !isOpen },
      h(
        "div",
        { className: "panel-heading" },
        h("h2", { id: "formTitle" }, editingTaskId ? "Editar tarefa" : "Nova tarefa"),
        h("button", { className: "ghost-button small", id: "closeTaskComposerButton", type: "button", onClick: onCancel }, "Fechar")
      ),
      h(
        "form",
        { id: "taskForm", autoComplete: "off", onSubmit },
        h(
          "label",
          { className: "field" },
          h("span", null, "Tarefa"),
          h("input", {
            id: "taskTitle",
            ref: inputRef,
            name: "title",
            type: "text",
            maxLength: 120,
            required: true,
            value: draft.title,
            onChange: (event) => onChange({ ...draft, title: event.target.value }),
          })
        ),
        h(
          "div",
          { className: "field-grid" },
          h(SelectField, {
            id: "taskPriority",
            label: "Prioridade",
            name: "priority",
            value: draft.priority,
            values: data.priorities || [],
            onChange: (value) => onChange({ ...draft, priority: value }),
          }),
          h(SelectField, {
            id: "taskCategory",
            label: "Categoria",
            name: "category",
            value: draft.category,
            values: data.categories || [],
            onChange: (value) => onChange({ ...draft, category: value }),
          })
        ),
        h(
          "label",
          { className: "check-field" },
          h("input", {
            id: "taskPinned",
            name: "pinned",
            type: "checkbox",
            checked: Boolean(draft.pinned),
            onChange: (event) => onChange({ ...draft, pinned: event.target.checked }),
          }),
          h("span", null, "Missao fixa")
        ),
        h(
          "div",
          { className: "button-row" },
          h(
            "button",
            { className: "primary-button", id: "submitTaskButton", type: "submit", disabled: isSaving },
            editingTaskId ? "Salvar" : "Adicionar"
          ),
          h("button", { className: "ghost-button", id: "clearTaskButton", type: "button", onClick: onCancel }, "Cancelar")
        )
      )
    );
  }

  function TaskColumn({ column, isSaving, onTaskAction }) {
    return h(
      "section",
      { className: `task-column ${column.key}`, "aria-label": column.title },
      h(
        "div",
        { className: "task-column-header" },
        h("h3", null, column.title),
        h("span", null, column.tasks.length)
      ),
      h(
        "div",
        { className: "task-column-cards" },
        column.tasks.length
          ? column.tasks.map((task) =>
              h(TaskCard, {
                key: task.id,
                task,
                isSaving,
                onAction: onTaskAction,
              })
            )
          : h(
              "div",
              { className: "empty-state compact" },
              column.key === "pending" ? "Nenhuma tarefa pendente." : "Nenhuma tarefa concluida."
            )
      )
    );
  }

  function TaskCard({ task, isSaving, onAction }) {
    const completeAction = task.done ? "reopen" : "complete";
    return h(
      "article",
      {
        className: `task-card${task.done ? " done" : ""}${task.pinned ? " pinned" : ""}`,
        "data-id": task.id,
      },
      h("div", { className: "task-status" }),
      h(
        "div",
        { className: "task-content" },
        h(
          "div",
          { className: "task-title-row" },
          h("h3", null, task.title),
          h("span", { className: "pin-label" }, "Fixa")
        ),
        h(
          "div",
          { className: "task-meta" },
          h(MetaPill, { text: task.priority, className: `priority-${task.priority}` }),
          h(MetaPill, { text: task.category }),
          h(MetaPill, { text: task.points_label }),
          h(MetaPill, { text: task.done ? task.completed_label : task.created_label })
        )
      ),
      h(
        "div",
        { className: "task-actions" },
        h(
          "button",
          {
            className: "primary-button small",
            "data-action": completeAction,
            type: "button",
            disabled: isSaving,
            onClick: () => onAction(task, completeAction),
          },
          task.done ? "Reabrir" : "Concluir"
        ),
        h(
          "button",
          {
            className: "ghost-button small",
            "data-action": "focus",
            type: "button",
            disabled: isSaving || task.done,
            title: task.done ? "Tarefa concluida" : "Abrir no modo foco",
            onClick: () => onAction(task, "focus"),
          },
          "Foco"
        ),
        h("button", { className: "ghost-button small", type: "button", disabled: isSaving, onClick: () => onAction(task, "edit") }, "Editar"),
        h(
          "button",
          {
            className: "ghost-button small",
            "data-action": "pin",
            type: "button",
            disabled: isSaving,
            onClick: () => onAction(task, "pin"),
          },
          task.pinned ? "Desafixar" : "Fixar"
        ),
        h(
          "button",
          {
            className: "danger-button small",
            "data-action": "delete",
            type: "button",
            disabled: isSaving,
            onClick: () => onAction(task, "delete"),
          },
          "Excluir"
        )
      )
    );
  }

  function HistoryList({ history }) {
    if (!history.length) {
      return h("div", { className: "history-list", id: "historyList" }, h("div", { className: "empty-state" }, "Historico vazio."));
    }
    return h(
      "div",
      { className: "history-list", id: "historyList" },
      history.slice(0, 8).map((entry) =>
        h(
          "div",
          { className: "history-row", key: entry.date },
          h("strong", null, entry.date_label),
          h("span", null, `${entry.completed_tasks}/${entry.total_tasks}`),
          h("span", null, `${entry.points_earned} pts`),
          h("span", null, `${entry.completion_percentage}%`)
        )
      )
    );
  }

  function FocusView({ active, data, focus, tasks, isSaving, onFocusTaskChange, onFocusModeChange, onStart, onPause, onReset, onSkip, onCompleteTask }) {
    const pendingTasks = tasks.filter((task) => !task.done);
    const selectedTask = tasks.find((task) => task.id === focus.taskId && !task.done);
    const mode = getFocusModeConfig(focus.mode);
    const progress = Math.round(((mode.seconds - focus.secondsRemaining) / mode.seconds) * 100);
    const isFocusBlocked = focus.mode === "focus" && !selectedTask;
    const completedInRound = focus.mode === "long_break" && focus.completedPomodoros > 0 ? 4 : focus.completedPomodoros % 4;
    const activeRound = Math.min(4, completedInRound + 1);

    return h(
      "section",
      {
        className: `tab-view${active ? " active" : ""}`,
        id: "focusView",
        role: "tabpanel",
        "aria-labelledby": "focusTab",
        "data-view-panel": "focus",
        hidden: !active,
      },
      h(
        "section",
        { className: "focus-workspace" },
        h(
          "section",
          { className: "focus-panel", "aria-labelledby": "focusHeading" },
          h(
            "div",
            { className: "task-toolbar" },
            h("h2", { id: "focusHeading" }, "Modo foco"),
            h("span", { id: "focusCycleMetric" }, formatPomodoroCount(focus.completedPomodoros))
          ),
          h(
            "div",
            { className: "focus-layout" },
            h(
              "section",
              { className: "focus-timer-panel", "aria-label": "Sessao Pomodoro" },
              h(
                "div",
                { className: "focus-setup" },
                h(
                  "label",
                  { className: "field focus-task-field" },
                  h("span", null, "Tarefa em foco"),
                  h(
                    "select",
                    {
                      id: "focusTaskSelect",
                      value: pendingTasks.some((task) => task.id === focus.taskId) ? focus.taskId : "",
                      disabled: !pendingTasks.length,
                      onChange: (event) => onFocusTaskChange(event.target.value),
                    },
                    h("option", { value: "" }, pendingTasks.length ? "Escolha uma tarefa" : "Nenhuma tarefa pendente"),
                    pendingTasks.map((task) => h("option", { key: task.id, value: task.id }, task.title))
                  )
                ),
                h(
                  "div",
                  {
                    className: "segmented-control focus-mode-buttons",
                    id: "focusModeButtons",
                    role: "tablist",
                    "aria-label": "Tipo de ciclo",
                  },
                  Object.keys(POMODORO_MODES).map((key) =>
                    h(
                      "button",
                      {
                        key,
                        className: focus.mode === key ? "active" : "",
                        type: "button",
                        role: "tab",
                        "aria-selected": focus.mode === key,
                        "data-focus-mode": key,
                        onClick: () => onFocusModeChange(key),
                      },
                      POMODORO_MODES[key].label
                    )
                  )
                )
              ),
              h(
                "div",
                { className: "focus-stage", "aria-live": "polite" },
                h("span", { id: "focusStageLabel" }, mode.label),
                h("strong", { id: "focusTimerLabel" }, formatTimer(focus.secondsRemaining)),
                h("span", { id: "focusNextLabel" }, mode.nextLabel)
              ),
              h("div", { className: "focus-progress", "aria-hidden": "true" }, h("span", { id: "focusProgressBar", style: widthStyle(progress) })),
              h(
                "div",
                { className: "focus-controls" },
                h("button", { className: "primary-button", id: "focusStartButton", type: "button", disabled: focus.isRunning || isFocusBlocked, onClick: onStart }, focus.isRunning ? "Rodando" : "Iniciar"),
                h("button", { className: "ghost-button", id: "focusPauseButton", type: "button", disabled: !focus.isRunning, onClick: onPause }, "Pausar"),
                h("button", { className: "ghost-button", id: "focusResetButton", type: "button", disabled: !focus.isRunning && focus.secondsRemaining === mode.seconds, onClick: onReset }, "Resetar"),
                h("button", { className: "ghost-button", id: "focusSkipButton", type: "button", onClick: onSkip }, "Pular")
              )
            ),
            h(
              "aside",
              { className: "focus-task-summary", "aria-live": "polite" },
              h("span", { className: "focus-summary-label" }, "Agora"),
              h("h3", { id: "focusTaskTitle" }, selectedTask ? selectedTask.title : "Escolha uma tarefa"),
              h(
                "div",
                { className: "task-meta", id: "focusTaskMeta" },
                selectedTask
                  ? [
                      h(MetaPill, { key: "priority", text: selectedTask.priority, className: `priority-${selectedTask.priority}` }),
                      h(MetaPill, { key: "category", text: selectedTask.category }),
                      h(MetaPill, { key: "points", text: selectedTask.points_label }),
                    ]
                  : h(MetaPill, { text: "Sem tarefa pendente" })
              ),
              h("button", { className: "primary-button small", id: "focusCompleteTaskButton", type: "button", disabled: isSaving || !selectedTask, onClick: onCompleteTask }, "Concluir tarefa")
            ),
            h(
              "section",
              { className: "focus-rhythm", "aria-label": "Ritmo Pomodoro" },
              h("div", { className: "panel-heading" }, h("h2", null, "Sequencia"), h("span", { id: "focusRoundMetric" }, `${activeRound}/4`)),
              h(
                "div",
                { className: "focus-cycle-dots", id: "focusCycleDots" },
                [1, 2, 3, 4].map((step) =>
                  h(
                    "span",
                    {
                      key: step,
                      className: `focus-cycle-dot${step <= completedInRound ? " done" : ""}${focus.mode === "focus" && step === activeRound ? " active" : ""}`,
                    },
                    step
                  )
                )
              )
            )
          )
        )
      )
    );
  }

  function ProfileView(props) {
    const {
      active,
      data,
      profileDraft,
      dailyGoalDraft,
      weeklyGoalDraft,
      isSaving,
      onProfileDraftChange,
      onDailyGoalChange,
      onWeeklyGoalChange,
      onSubmitProfile,
      onSubmitDailyGoal,
      onSubmitWeeklyGoal,
      gamification,
      weekly,
    } = props;

    return h(
      "section",
      {
        className: `tab-view${active ? " active" : ""}`,
        id: "profileView",
        role: "tabpanel",
        "aria-labelledby": "profileTab",
        "data-view-panel": "profile",
        hidden: !active,
      },
      h(
        "section",
        { className: "profile-workspace" },
        h(
          "aside",
          { className: "side-stack" },
          h(
            "section",
            { className: "tool-panel" },
            h("div", { className: "panel-heading" }, h("h2", null, "Perfil")),
            h(
              "form",
              { id: "profileForm", autoComplete: "off", onSubmit: onSubmitProfile },
              h(TextField, {
                id: "profileFormName",
                label: "Nome",
                name: "name",
                maxLength: 80,
                value: profileDraft.name,
                onChange: (value) => onProfileDraftChange({ ...profileDraft, name: value }),
              }),
              h(TextField, {
                id: "profileAvatarUrl",
                label: "Foto",
                name: "avatar_url",
                maxLength: 500,
                placeholder: "https://... ou /images/perfil.jpg",
                value: profileDraft.avatar_url,
                onChange: (value) => onProfileDraftChange({ ...profileDraft, avatar_url: value }),
              }),
              h("div", { className: "button-row" }, h("button", { className: "primary-button", type: "submit", disabled: isSaving }, "Salvar perfil"))
            )
          ),
          h(
            "section",
            { className: "tool-panel" },
            h("div", { className: "panel-heading" }, h("h2", null, "Meta diaria"), h("strong", { id: "streakMetric" }, gamification.streak_label || "0 dias")),
            h(
              "form",
              { className: "goal-form", id: "goalForm", onSubmit: onSubmitDailyGoal },
              h(NumberField, {
                id: "dailyGoalInput",
                label: "Pontos da meta",
                name: "daily_goal_points",
                step: 5,
                min: data.daily_goal_limits?.min,
                max: data.daily_goal_limits?.max,
                value: dailyGoalDraft,
                onChange: onDailyGoalChange,
              }),
              h("button", { className: "ghost-button", type: "submit", disabled: isSaving }, "Salvar")
            ),
            h(Meter, { id: "goalProgressBar", value: gamification.daily_goal_progress || 0, wide: true }),
            h("p", { className: "support-text", id: "motivationText" }, gamification.motivation || "Comece com uma tarefa simples.")
          ),
          h(
            "section",
            { className: "tool-panel" },
            h("div", { className: "panel-heading" }, h("h2", null, "Meta semanal"), h("strong", { id: "weeklyGoalMetric" }, weekly.goal_label || "0/20 tarefas")),
            h(
              "form",
              { className: "goal-form", id: "weeklyGoalForm", onSubmit: onSubmitWeeklyGoal },
              h(NumberField, {
                id: "weeklyGoalInput",
                label: "Tarefas da meta",
                name: "weekly_goal_tasks",
                step: 1,
                min: data.weekly_goal_limits?.min,
                max: data.weekly_goal_limits?.max,
                value: weeklyGoalDraft,
                onChange: onWeeklyGoalChange,
              }),
              h("button", { className: "ghost-button", type: "submit", disabled: isSaving }, "Salvar")
            ),
            h(Meter, { id: "weeklyGoalProgressBar", value: weekly.goal_progress || 0, wide: true }),
            h("p", { className: "support-text", id: "weeklyBonusText" }, weekly.bonus_awarded ? `Bonus semanal recebido: ${weekly.bonus_label}` : `Bonus semanal: ${weekly.bonus_label || "0 pts"}`)
          )
        ),
        h(
          "section",
          { className: "profile-progress" },
          h(
            "section",
            { className: "progress-panel" },
            h("div", { className: "task-toolbar" }, h("h2", null, "Estatisticas da semana"), h("span", { id: "weekRangeLabel" }, weekly.week_label || "Semana atual")),
            h(
              "section",
              { className: "weekly-metrics-grid", "aria-label": "Estatisticas semanais" },
              h(StatCard, { label: "Concluidas", value: weekly.completed_tasks || 0, idValue: "weeklyCompletedMetric" }),
              h(StatCard, { label: "Pontos", value: weekly.points_earned || 0, idValue: "weeklyPointsMetric" }),
              h(StatCard, { label: "Melhor dia", value: weekly.best_day?.label || "Sem dados", idValue: "weeklyBestDayMetric", wide: true }),
              h(StatCard, { label: "Categoria", value: weekly.top_category?.label || "Sem dados", idValue: "weeklyCategoryMetric", wide: true }),
              h(StatCard, { label: "Taxa semanal", value: `${weekly.completion_percentage || 0}%`, idValue: "weeklyCompletionMetric" })
            )
          )
        )
      )
    );
  }

  function AchievementsView({ active, data }) {
    const achievements = data.achievements || [];
    return h(
      "section",
      {
        className: `tab-view${active ? " active" : ""}`,
        id: "achievementsView",
        role: "tabpanel",
        "aria-labelledby": "achievementsTab",
        "data-view-panel": "achievements",
        hidden: !active,
      },
      h(
        "section",
        { className: "achievements-workspace" },
        h(
          "section",
          { className: "achievements-panel" },
          h("div", { className: "task-toolbar" }, h("h2", null, "Conquistas"), h("span", { id: "achievementSummaryMetric" }, data.achievement_summary?.label || "0/0 desbloqueadas")),
          h(
            "div",
            { className: "achievement-list", id: "achievementList" },
            achievements.length
              ? achievements.map((achievement) => h(AchievementCard, { key: achievement.id || achievement.title, achievement }))
              : h("div", { className: "empty-state" }, "Nenhuma conquista configurada.")
          )
        )
      )
    );
  }

  function AchievementCard({ achievement }) {
    return h(
      "article",
      { className: `achievement-card${achievement.unlocked ? " unlocked" : ""}` },
      h(
        "div",
        { className: "achievement-content" },
        h("h3", null, achievement.title),
        h("p", null, achievement.description),
        h(Meter, { value: achievement.progress_percentage || 0, compact: true }),
        h(
          "div",
          { className: "achievement-meta" },
          h(MetaPill, { text: achievement.status_label, className: achievement.unlocked ? "achievement-unlocked" : "" }),
          h(MetaPill, { text: achievement.progress_label }),
          h(MetaPill, { text: achievement.unlocked_label || "Em progresso" })
        )
      )
    );
  }

  function RewardsView({ active, data, rewardDraft, editingRewardId, isSaving, onRewardDraftChange, onSubmitReward, onResetReward, onRewardAction }) {
    return h(
      "section",
      {
        className: `tab-view${active ? " active" : ""}`,
        id: "rewardsView",
        role: "tabpanel",
        "aria-labelledby": "rewardsTab",
        "data-view-panel": "rewards",
        hidden: !active,
      },
      h(
        "section",
        { className: "rewards-workspace" },
        h(
          "aside",
          { className: "side-stack" },
          h(
            "section",
            { className: "tool-panel" },
            h("div", { className: "panel-heading" }, h("h2", { id: "rewardFormTitle" }, editingRewardId ? "Editar recompensa" : "Nova recompensa")),
            h(
              "form",
              { id: "rewardForm", autoComplete: "off", onSubmit: onSubmitReward },
              h(TextField, {
                id: "rewardTitle",
                label: "Recompensa",
                name: "title",
                maxLength: 120,
                required: true,
                value: rewardDraft.title,
                onChange: (value) => onRewardDraftChange({ ...rewardDraft, title: value }),
              }),
              h(
                "div",
                { className: "field-grid" },
                h(NumberField, {
                  id: "rewardCost",
                  label: "Custo",
                  name: "cost",
                  min: 1,
                  step: 5,
                  required: true,
                  value: rewardDraft.cost,
                  onChange: (value) => onRewardDraftChange({ ...rewardDraft, cost: value }),
                }),
                h(TextField, {
                  id: "rewardDescription",
                  label: "Detalhe",
                  name: "description",
                  maxLength: 160,
                  value: rewardDraft.description,
                  onChange: (value) => onRewardDraftChange({ ...rewardDraft, description: value }),
                })
              ),
              h(TextField, {
                id: "rewardImageUrl",
                label: "Imagem",
                name: "image_url",
                maxLength: 500,
                placeholder: "https://... ou /images/recompensa.jpg",
                value: rewardDraft.image_url,
                onChange: (value) => onRewardDraftChange({ ...rewardDraft, image_url: value }),
              }),
              h(
                "div",
                { className: "button-row" },
                h("button", { className: "primary-button", id: "submitRewardButton", type: "submit", disabled: isSaving }, editingRewardId ? "Salvar" : "Adicionar"),
                h("button", { className: "ghost-button", id: "clearRewardButton", type: "button", onClick: onResetReward }, "Limpar")
              )
            )
          )
        ),
        h(
          "section",
          { className: "rewards-panel" },
          h("div", { className: "task-toolbar" }, h("h2", null, "Loja de recompensas"), h("strong", { id: "storeBalanceMetric" }, data.wallet?.points_available_label || "0 pts")),
          h(
            "div",
            { className: "rewards-layout" },
            h(
              "div",
              { className: "reward-list", id: "rewardList" },
              data.rewards?.length
                ? data.rewards.map((reward) =>
                    h(RewardCard, {
                      key: reward.id,
                      reward,
                      wallet: data.wallet || emptyData.wallet,
                      isSaving,
                      onAction: onRewardAction,
                    })
                  )
                : h("div", { className: "empty-state" }, "Nenhuma recompensa cadastrada.")
            ),
            h(
              "section",
              { className: "redemption-panel", "aria-label": "Historico de resgates" },
              h("div", { className: "panel-heading" }, h("h2", null, "Resgates")),
              h(RedemptionList, { redemptions: data.reward_redemptions || [] })
            )
          )
        )
      )
    );
  }

  function RewardCard({ reward, wallet, isSaving, onAction }) {
    return h(
      "article",
      { className: "reward-card", "data-id": reward.id },
      h(RewardImage, { reward }),
      h(
        "div",
        { className: "reward-content" },
        h("h3", null, reward.title),
        h("p", { className: "reward-description" }, reward.description || ""),
        h(
          "div",
          { className: "reward-meta" },
          h(MetaPill, { text: reward.cost_label, className: "cost-pill" }),
          h(MetaPill, { text: reward.can_redeem ? "Disponivel" : `${wallet.points_available || 0} pts disponiveis` }),
          h(MetaPill, { text: reward.created_label })
        )
      ),
      h(
        "div",
        { className: "reward-actions" },
        h("button", { className: "primary-button small", "data-reward-action": "redeem", type: "button", disabled: isSaving || !reward.can_redeem, title: reward.can_redeem ? "Resgatar recompensa" : "Pontos insuficientes", onClick: () => onAction(reward, "redeem") }, "Resgatar"),
        h("button", { className: "ghost-button small", "data-reward-action": "edit", type: "button", disabled: isSaving, onClick: () => onAction(reward, "edit") }, "Editar"),
        h("button", { className: "danger-button small", "data-reward-action": "delete", type: "button", disabled: isSaving, onClick: () => onAction(reward, "delete") }, "Excluir")
      )
    );
  }

  function RedemptionList({ redemptions }) {
    if (!redemptions.length) {
      return h("div", { className: "redemption-list", id: "redemptionList" }, h("div", { className: "empty-state" }, "Nenhum resgate ainda."));
    }
    return h(
      "div",
      { className: "redemption-list", id: "redemptionList" },
      redemptions.slice(0, 10).map((redemption) =>
        h(
          "div",
          { className: "redemption-row", key: redemption.id },
          h("strong", null, redemption.reward_title),
          h("span", null, redemption.cost_label),
          h("span", null, redemption.redeemed_label)
        )
      )
    );
  }

  function TextField({ id: fieldId, label, name, value, onChange, maxLength, placeholder = "", required = false }) {
    return h(
      "label",
      { className: "field" },
      h("span", null, label),
      h("input", {
        id: fieldId,
        name,
        type: "text",
        maxLength,
        placeholder,
        required,
        value,
        onChange: (event) => onChange(event.target.value),
      })
    );
  }

  function NumberField({ id: fieldId, label, name, value, onChange, min, max, step, required = false }) {
    return h(
      "label",
      { className: "field" },
      h("span", null, label),
      h("input", {
        id: fieldId,
        name,
        type: "number",
        min,
        max,
        step,
        required,
        value,
        onChange: (event) => onChange(event.target.value),
      })
    );
  }

  function SelectField({ id: fieldId, label, name, value, values, onChange }) {
    return h(
      "label",
      { className: "field" },
      h("span", null, label),
      h(
        "select",
        {
          id: fieldId,
          name,
          value,
          onChange: (event) => onChange(event.target.value),
        },
        values.map((item) => h("option", { key: item, value: item }, item))
      )
    );
  }

  function ProfileAvatar({ name, avatarUrl }) {
    const [imageOk, setImageOk] = useState(false);
    useEffect(() => {
      setImageOk(false);
    }, [avatarUrl]);

    return h(
      "span",
      { className: `brand-mark profile-avatar${avatarUrl && imageOk ? " has-image" : ""}`, id: "profileAvatar", "aria-hidden": "true" },
      avatarUrl
        ? h("img", {
            id: "profileAvatarImage",
            alt: "",
            src: avatarUrl,
            hidden: !imageOk,
            onLoad: () => setImageOk(true),
            onError: () => setImageOk(false),
          })
        : null,
      h("span", { id: "profileAvatarInitials" }, getProfileInitials(name))
    );
  }

  function RewardImage({ reward }) {
    const [imageOk, setImageOk] = useState(false);
    useEffect(() => {
      setImageOk(false);
    }, [reward.image_url]);

    return h(
      "div",
      { className: `reward-image${reward.image_url && imageOk ? " has-image" : ""}`, "aria-hidden": "true" },
      reward.image_url
        ? h("img", {
            alt: "",
            loading: "lazy",
            src: reward.image_url,
            hidden: !imageOk,
            onLoad: () => setImageOk(true),
            onError: () => setImageOk(false),
          })
        : null,
      h("span", null, getRewardInitial(reward.title))
    );
  }

  function StatCard({ label, value, idValue, wide = false }) {
    return h("article", { className: `stat-card${wide ? " wide-stat" : ""}` }, h("span", null, label), h("strong", { id: idValue }, value));
  }

  function Meter({ id: meterId, value, wide = false, compact = false }) {
    return h("div", { className: `meter${wide ? " wide" : ""}${compact ? " compact-meter" : ""}` }, h("span", { id: meterId, style: widthStyle(value) }));
  }

  function MetaPill({ text, className = "" }) {
    return h("span", { className }, text || "");
  }

  function Icon({ name, className }) {
    const paths = {
      plus: ["M12 5v14M5 12h14"],
      today: [
        "M8 2v4M16 2v4M4 10h16M6 4h12a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z",
        "m9 15 2 2 4-5",
      ],
      focus: ["circle:12:12:8", "M12 8v4l3 2", "M9 2h6"],
      profile: ["M20 21a8 8 0 0 0-16 0", "circle:12:7:4"],
      achievements: ["M8 21h8M12 17v4", "M7 4h10v5a5 5 0 0 1-10 0V4Z", "M5 5H3v3a4 4 0 0 0 4 4M19 5h2v3a4 4 0 0 1-4 4"],
      rewards: ["M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8", "M2 7h20v5H2zM12 22V7", "M12 7H7.5A2.5 2.5 0 1 1 10 4.5C10 7 12 7 12 7Zm0 0h4.5A2.5 2.5 0 1 0 14 4.5C14 7 12 7 12 7Z"],
    };

    return h(
      "svg",
      { className, "aria-hidden": "true", viewBox: "0 0 24 24" },
      (paths[name] || []).map((path, index) => {
        if (path.startsWith("circle:")) {
          const [, cx, cy, r] = path.split(":");
          return h("circle", { key: index, cx, cy, r });
        }
        return h("path", { key: index, d: path });
      })
    );
  }

  function getTaskColumns(tasks, filter) {
    const pending = tasks.filter((task) => !task.done);
    const completed = tasks.filter((task) => task.done);

    if (filter === "Pendentes") {
      return [{ key: "pending", title: "Pendentes", tasks: pending }];
    }
    if (filter === "Concluidas") {
      return [{ key: "done", title: "Concluidas", tasks: completed }];
    }
    return [
      { key: "pending", title: "Pendentes", tasks: pending },
      { key: "done", title: "Concluidas", tasks: completed },
    ];
  }

  function normalizeView(view) {
    const requestedView = VIEW_ALIASES[view] || view;
    return ["routine", "focus", "profile", "achievements", "rewards"].includes(requestedView)
      ? requestedView
      : "routine";
  }

  function createDefaultFocusSession() {
    return {
      taskId: "",
      mode: "focus",
      secondsRemaining: POMODORO_MODES.focus.seconds,
      isRunning: false,
      completedPomodoros: 0,
      lastTick: null,
    };
  }

  function loadFocusSession() {
    try {
      return normalizeFocusSession(JSON.parse(localStorage.getItem(POMODORO_STORAGE_KEY) || "null"));
    } catch {
      return createDefaultFocusSession();
    }
  }

  function normalizeFocusSession(savedSession) {
    if (!savedSession || typeof savedSession !== "object") {
      return createDefaultFocusSession();
    }

    const mode = POMODORO_MODES[savedSession.mode] ? savedSession.mode : "focus";
    const duration = POMODORO_MODES[mode].seconds;
    let secondsRemaining = Number(savedSession.secondsRemaining);
    let isRunning = Boolean(savedSession.isRunning);

    if (!Number.isFinite(secondsRemaining) || secondsRemaining <= 0 || secondsRemaining > duration) {
      secondsRemaining = duration;
    }

    if (isRunning && Number.isFinite(Number(savedSession.lastTick))) {
      const elapsed = Math.max(0, Math.floor((Date.now() - Number(savedSession.lastTick)) / 1000));
      secondsRemaining = Math.max(0, secondsRemaining - elapsed);
      isRunning = secondsRemaining > 0;
    }

    return {
      taskId: typeof savedSession.taskId === "string" ? savedSession.taskId : "",
      mode,
      secondsRemaining,
      isRunning,
      completedPomodoros: Math.max(0, Number.parseInt(savedSession.completedPomodoros, 10) || 0),
      lastTick: isRunning ? Date.now() : null,
    };
  }

  function applyFocusElapsed(current) {
    const now = Date.now();
    const elapsed = Math.max(0, Math.floor((now - (current.lastTick || now)) / 1000));
    const next = {
      ...current,
      lastTick: now,
      secondsRemaining: Math.max(0, current.secondsRemaining - elapsed),
    };
    if (next.secondsRemaining <= 0) {
      return finishFocusInterval(next);
    }
    return { focus: next, message: "" };
  }

  function finishFocusInterval(current) {
    const finishedMode = current.mode;
    let next = {
      ...current,
      isRunning: false,
      lastTick: null,
    };
    let message = "Ciclo encerrado.";

    if (finishedMode === "focus") {
      const completedPomodoros = current.completedPomodoros + 1;
      const mode = completedPomodoros % 4 === 0 ? "long_break" : "short_break";
      next = {
        ...next,
        completedPomodoros,
        mode,
        secondsRemaining: POMODORO_MODES[mode].seconds,
      };
      message = mode === "long_break" ? "Pomodoro fechado. Pausa longa liberada." : "Pomodoro fechado. Pausa curta liberada.";
    } else {
      next = {
        ...next,
        mode: "focus",
        secondsRemaining: POMODORO_MODES.focus.seconds,
      };
      message = "Pausa encerrada. Hora do foco.";
    }

    return { focus: next, message };
  }

  function getFocusModeConfig(mode) {
    return POMODORO_MODES[mode] || POMODORO_MODES.focus;
  }

  function getFocusTasks(data) {
    return data.focus_tasks || data.tasks || [];
  }

  function formatTimer(totalSeconds) {
    const safeSeconds = Math.max(0, Math.floor(totalSeconds));
    const minutes = String(Math.floor(safeSeconds / 60)).padStart(2, "0");
    const seconds = String(safeSeconds % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
  }

  function formatPomodoroCount(count) {
    return count === 1 ? "1 pomodoro" : `${count} pomodoros`;
  }

  function getProfileDisplayName(profile = {}) {
    const name = String(profile.display_name || profile.name || "").trim();
    return name || DEFAULT_PROFILE_NAME;
  }

  function getProfileInitials(name) {
    const words = String(name || DEFAULT_PROFILE_NAME)
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    const initials = words
      .slice(0, 2)
      .map((word) => word[0])
      .join("");
    return (initials || "RD").toUpperCase();
  }

  function getRewardInitial(title) {
    const normalizedTitle = String(title || "").trim();
    return normalizedTitle ? normalizedTitle[0].toUpperCase() : "?";
  }

  function widthStyle(value) {
    return { width: `${Math.max(0, Math.min(100, Number(value) || 0))}%` };
  }

  function id(value) {
    return { id: value };
  }

  ReactDOM.createRoot(document.getElementById("root")).render(h(App));
})();
