/* Easy Job Tutor 公开 Beta — 同源 vendored Vue 3 全局运行时，无构建步骤。 */
const { createApp, reactive, ref, computed, onMounted, onUnmounted, nextTick } = Vue;

// ── i18n 字典 ──────────────────────────────────────────
const PRIVACY_CONSENT_VERSION = "2026-08-11";
const LOCALES = {
  zh: {
    /* 品牌 / 通用 */
    app_title: "AI 简历优化助手",
    app_subtitle: "JD 关键词覆盖 · 简历原文证据辅助",
    app_audience: "面向在校大学生 / 应届毕业生 · 首版覆盖 AI 产品 / AI Agent 开发 / AI 运营",
    workspace: "工作台",
    dashboard: "工作台",
    /* 侧边栏导航 */
    nav_home: "首页",
    nav_analysis: "分析页",
    nav_gaps: "查漏补缺",
    nav_home_desc: "上传一份 JD 与一份简历",
    nav_analysis_desc: "查看关键词与简历原文证据",
    nav_gaps_desc: "查看差距与补齐建议",
    /* 侧边栏 */
    sidebar_hide: "关闭侧边栏",
    sidebar_collapse: "折叠侧边栏",
    sidebar_expand: "展开侧边栏",
    sidebar_current_mode: "当前模式",
    sidebar_nav: "页面导航",
    sidebar_actions: "快捷操作",
    sidebar_new: "新建分析",
    sidebar_clear: "清空结果",
    sidebar_no_result: "请上传一份 JD 与一份简历",
    sidebar_result_complete: (r) => `${r.role_label || "目标岗位"} · 分析完成`,
    sidebar_result_done: "分析完成",
    /* 分析模式 */
    mode_complete: "完整分析",
    mode_complete_desc: "JD + 简历",
    /* 步骤 */
    step_upload: "上传",
    step_result: "分析结果",
    step_analysis: "关键词与原文证据",
    step_gaps: "查漏补缺",
    /* 步骤 1 */
    upload_title: "上传一份 JD 与一份简历",
    upload_hint: "提交一份岗位 JD 和一份简历，查看关键词覆盖与简历原文证据。",
    upload_jd_label: "岗位 JD（粘贴招聘信息全文）",
    upload_jd_placeholder: "例如：我们正在招聘 AI 产品实习生，负责 LLM 应用产品的需求分析与 0-1 落地……",
    upload_resume_label: "上传简历（PDF / DOCX / TXT）",
    upload_select: "选择文件",
    upload_drag: "将文件拖拽到此处，或点击选择",
    upload_role_label: "目标岗位",
    uploading: "分析中…",
    upload_submit: "分析这份简历",
    error_server: (s) => `服务器返回 HTTP ${s}，请稍后重试。`,
    error_fail: "分析失败，请重试。",
    error_network: "网络请求失败，请检查网络连接后重试。",
    /* 岗位选择 */
    role_auto: "自动识别",
    role_product: "AI 产品",
    role_agent: "AI Agent 开发",
    role_ops: "AI 运营",
    /* 完整分析 */
    match_title: (l) => `关键词与简历原文证据（${l}）`,
    matched_skills: (s) => `已匹配能力：${(s || []).join("、") || "暂无明显命中"}`,
    ledger_title: (n) => `📋 事实台账（${n} 项技能）`,
    ledger_hint: "每个技能的状态追踪：已确认 = 简历原文命中，待确认 = 部分匹配，推断 = 未找到关键词。",
    ledger_skill: "技能",
    ledger_dim: "维度",
    ledger_imp: "重要度",
    ledger_status: "状态",
    ledger_evidence: "证据",
    status_confirmed: "已确认",
    status_pending: "待确认",
    status_infer: "推断",
    resume_opt_title: "针对 JD 优化简历",
    resume_opt_hint: "以下内容只基于简历原文。建议版本中的【待确认】内容需要你补充真实事实后再用于正式简历。",
    resume_opt_target: "JD 关键词",
    resume_opt_missing: "待补充关键词",
    resume_opt_bullets: "Bullet 改写草稿",
    resume_opt_source: "简历原文",
    resume_opt_suggested: "建议版本（待确认）",
    resume_opt_keywords: "关联关键词",
    resume_opt_metric: "量化补充",
    resume_opt_empty: "暂未识别到可直接改写的简历 bullet，请补充项目或经历描述。",
    resume_opt_export: "导出优化简历草稿",
    resume_opt_policy: "事实状态：草稿仅重排已有内容，不会自动补充数字、职责或成果。",
    match_reupload: "重新上传",
    match_view_gaps: (n) => `查看差距（${n} 项）`,
    /* 查漏补缺 */
    gap_title: "查漏补缺",
    gap_hint: "以下能力在岗位 JD 中重要，但你的简历暂未体现，建议优先补齐：",
    gap_resource: (n) => `学习资源：${n} ↗`,
    gap_back: "返回",
    /* 页脚 */
    footer: "JD 关键词覆盖与简历原文证据辅助",
    /* 标签 */
    reanalyze: "重新分析",
  },
};

createApp({
  setup() {
    // ── i18n ──────────────────────────────────────────────────
    const dict = LOCALES.zh;
    const t = (key, ...args) => {
      const val = dict[key];
      if (typeof val === "function") return val(...args);
      return val ?? key;
    };

    // ── 基础状态 ──────────────────────────────────────────────
    const step = ref(1);
    const loading = ref(false);
    const error = ref("");
    const dragging = ref(false);
    const result = reactive({});
    const fileInput = ref(null);
    const menuTrigger = ref(null);
    const privacyConsent = ref(false);
    const isMobile = ref(typeof window !== "undefined" ? window.innerWidth <= 960 : false);
    const sidebarOpen = ref(!isMobile.value);
    const sidebarCollapsed = ref(false);

    const syncViewport = () => {
      if (typeof window === "undefined") return;
      isMobile.value = window.innerWidth <= 960;
      if (isMobile.value) {
        sidebarOpen.value = false;
        sidebarCollapsed.value = false;
      } else {
        sidebarOpen.value = true;
      }
    };

    onMounted(() => {
      syncViewport();
      window.addEventListener("resize", syncViewport);
    });
    onUnmounted(() => { window.removeEventListener("resize", syncViewport); });

    // 步骤标题
    const currentSteps = computed(() => {
      if (!result.mode) {
        return [t("step_upload"), t("step_result"), ""];
      }
      return [t("step_upload"), t("step_analysis"), t("step_gaps")];
    });

    const appShellClass = computed(() => ({
      "sidebar-open": sidebarOpen.value,
      "sidebar-collapsed": sidebarCollapsed.value,
      "mobile-shell": isMobile.value,
    }));

    const sidebarExpanded = computed(() =>
      isMobile.value ? sidebarOpen.value : !sidebarCollapsed.value
    );

    const mobileSidebarHidden = computed(() =>
      isMobile.value && !sidebarOpen.value
    );

    const sidebarToggleLabel = computed(() => {
      if (isMobile.value) {
        return sidebarOpen.value ? t("sidebar_hide") : t("sidebar_expand");
      }
      return sidebarCollapsed.value ? t("sidebar_expand") : t("sidebar_collapse");
    });

    const availableSteps = computed(() =>
      currentSteps.value
        .map((label, index) => ({ step: index + 1, label }))
        .filter((item) => item.label)
    );

    const currentModeLabel = computed(() => t("mode_complete"));

    const resultSummary = computed(() => {
      if (!result.mode) return t("sidebar_no_result");
      if (result.mode === "complete") return t("sidebar_result_complete", result);
      return t("sidebar_result_done");
    });

    // ── 页面导航 ──────────────────────────────────────────────
    // 图标映射：用 emoji 做轻量图标，不额外引入图标库
    const PAGE_ICONS = { home: "🏠", analysis: "📋", gaps: "🔍" };

    const navItems = computed(() => [
      { id: "home", label: t("nav_home"), desc: t("nav_home_desc"), icon: PAGE_ICONS.home, step: 1 },
      { id: "analysis", label: t("nav_analysis"), desc: t("nav_analysis_desc"), icon: PAGE_ICONS.analysis, step: 2 },
      { id: "gaps", label: t("nav_gaps"), desc: t("nav_gaps_desc"), icon: PAGE_ICONS.gaps, step: 3 },
    ]);

    const currentPage = computed(() => {
      const pageMap = { 1: "home", 2: "analysis", 3: "gaps" };
      return pageMap[step.value] || "home";
    });

    const isNavEnabled = (id) => {
      // 首页永远可用
      if (id === "home") return true;
      // 分析页：必须有分析结果
      if (id === "analysis") return !!result.mode;
      if (id === "gaps") return result.mode === "complete";
      return false;
    };

    const navigateTo = (id) => {
      if (!isNavEnabled(id)) return;
      const item = navItems.value.find((n) => n.id === id);
      if (!item) return;
      step.value = item.step;
      closeSidebar();
    };

    // ── 表单 ──────────────────────────────────────────────────
    const roleOptions = computed(() => [
      { value: "auto", label: t("role_auto") },
      { value: "ai_product", label: t("role_product") },
      { value: "ai_agent", label: t("role_agent") },
      { value: "ai_ops", label: t("role_ops") },
    ]);

    const form = reactive({ jd: "", role: "auto", file: null, fileName: "" });
    const canSubmit = computed(() => {
      return privacyConsent.value && form.jd.trim().length > 10 && !!form.file;
    });

    const closeSidebar = () => { if (isMobile.value) sidebarOpen.value = false; };
    const toggleSidebar = async () => {
      if (isMobile.value) {
        sidebarOpen.value = !sidebarOpen.value;
        if (!sidebarOpen.value) {
          await nextTick();
          menuTrigger.value?.focus();
        }
        return;
      }
      sidebarCollapsed.value = !sidebarCollapsed.value;
    };

    const jumpToStep = (targetStep) => {
      if (targetStep < 1 || targetStep > 3) return;
      if (targetStep === 1 || result.mode === "complete") step.value = targetStep;
      closeSidebar();
    };

    const onFile = (e) => {
      const f = e.target.files && e.target.files[0];
      if (f) { form.file = f; form.fileName = f.name; error.value = ""; }
    };
    const onDrop = (e) => {
      dragging.value = false;
      const f = e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) { form.file = f; form.fileName = f.name; error.value = ""; }
    };

    // ── 提交 ──────────────────────────────────────────────────
    const submit = async () => {
      if (!canSubmit.value) return;
      loading.value = true; error.value = "";
      try {
        const fd = new FormData();
        fd.append("mode", "complete");
        fd.append("role", form.role);
        fd.append("locale", "zh");
        fd.append("privacy_consent_version", PRIVACY_CONSENT_VERSION);
        fd.append("jd", form.jd);
        fd.append("resume", form.file);

        const resp = await fetch("/api/analyze", { method: "POST", body: fd });
        const contentType = resp.headers.get("content-type") || "";
        const data = contentType.includes("application/json") ? await resp.json() : null;
        if (!resp.ok) { error.value = data?.error || t("error_server", resp.status); return; }
        if (!data.ok) { error.value = data.error || t("error_fail"); return; }
        Object.assign(result, data);
        step.value = 2;
      } catch (e) { error.value = t("error_network"); }
      finally { loading.value = false; }
    };

    const statusLabel = (s) => ({
      confirmed: { text: t("status_confirmed"), cls: "badge-green" },
      pending_confirmation: { text: t("status_pending"), cls: "badge-orange" },
      model_inference: { text: t("status_infer"), cls: "badge-gray" },
    }[s] || { text: s, cls: "badge-gray" });

    // ── 重置 ──────────────────────────────────────────────────
    const reset = () => {
      step.value = 1;
      form.jd = ""; form.file = null; form.fileName = ""; form.role = "auto";
      error.value = "";
      Object.keys(result).forEach((k) => delete result[k]);
      closeSidebar();
    };

    // ── 下载 ──────────────────────────────────────────────────
    const downloadOptimizedResume = () => {
      const opt = result.resume_optimization;
      if (!opt) return;
      let md = `# JD 定制简历优化草稿 · ${result.role_label}\n\n> 仅为优化草稿，使用前请确认所有待补充事实。\n\n`;
      md += "## JD 关键词\n";
      md += `${(opt.target_keywords || []).join(", ") || "暂未识别"}\n\n`;
      md += "## 待补充关键词\n";
      md += `${(opt.missing_keywords || []).join(", ") || "无明显缺口"}\n\n`;
      md += "## Bullet 改写草稿\n";
      (opt.bullet_rewrites || []).forEach((item, index) => {
        md += `### ${index + 1}. ${item.suggested_bullet}\n`;
        md += `- 原文：${item.source}\n`;
        md += `- 关联关键词：${(item.matched_keywords || item.matched_skills || []).join(", ")}\n`;
        md += `- 量化补充：${item.quantification_prompt}\n\n`;
      });
      md += "## 量化补充问题\n";
      (opt.quantification_prompts || []).forEach((item) => {
        md += `- ${item.question}\n`;
      });
      md += `\n> ${opt.fact_policy || ""}\n`;
      const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
      const anchor = document.createElement("a");
      anchor.href = URL.createObjectURL(blob);
      anchor.download = "JD定制简历优化草稿.md";
      anchor.click();
      URL.revokeObjectURL(anchor.href);
    };

    return {
      // i18n
      t,
      // 状态
      step, loading, error, dragging, result, fileInput, menuTrigger,
      isMobile, sidebarOpen, sidebarCollapsed, appShellClass,
      sidebarExpanded, sidebarToggleLabel, mobileSidebarHidden,
      currentSteps, availableSteps, currentModeLabel, resultSummary,
      // 表单
      roleOptions, form, privacyConsent, canSubmit,
      onFile, onDrop, submit,
      // 台账
      statusLabel,
      // 动作
      reset, downloadOptimizedResume, toggleSidebar, closeSidebar, jumpToStep,
      // 页面导航
      navItems, currentPage, isNavEnabled, navigateTo,
    };
  },
}).mount("#app");
