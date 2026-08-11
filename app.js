/* Easy Job Tutor 公开 Beta — 同源 vendored Vue 3 全局运行时，无构建步骤。 */
const { createApp, reactive, ref, computed, onMounted, onUnmounted, nextTick } = Vue;

// ── i18n 字典 ──────────────────────────────────────────
const PRIVACY_CONSENT_VERSION = "2026-08-11";
const ANALYSIS_TIMEOUT_MS = 22_000;
const API_ERROR_MESSAGES = Object.freeze({
  PRIVACY_CONSENT_REQUIRED: "请重新确认隐私说明与使用条款后再试。",
  JD_TOO_SHORT: "岗位 JD 至少需要 50 个字符，请补充完整岗位描述后重试。",
  JD_TOO_LONG: "岗位 JD 不能超过 20000 个字符，请删除无关内容后重试。",
  RESUME_REQUIRED: "请上传 PDF、DOCX 或 TXT 简历后再试。",
  FILE_TOO_LARGE: "简历文件不能超过 5 MB。",
  UNSUPPORTED_FILE_TYPE: "请上传 PDF、DOCX 或 TXT 文件。",
  FILE_MIME_MISMATCH: "文件扩展名与 MIME 类型不一致，请重新导出文件后再试。",
  FILE_SIGNATURE_MISMATCH: "文件扩展名与真实类型不一致，请重新选择文件。",
  PDF_TOO_MANY_PAGES: "PDF 简历不能超过 10 页。",
  DOCX_UNCOMPRESSED_TOO_LARGE: "DOCX 解压后内容超过安全限制，请精简文件后再试。",
  DOCX_COMPRESSION_RATIO_TOO_HIGH: "DOCX 文件未通过安全检查，请重新导出后再试。",
  RESUME_TEXT_EMPTY: "没有提取到可用文字，请上传可复制文字的 PDF、DOCX 或 TXT。",
});
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
    sidebar_result_complete: (r) => `${r.role?.label || "目标岗位"} · 分析完成`,
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
    error_timeout: "分析请求超时，请稍后重试。",
    request_id: (id) => `请求编号：${id}`,
    /* 岗位选择 */
    role_auto: "自动识别",
    role_product: "AI 产品",
    role_agent: "AI Agent 开发",
    role_ops: "AI 运营",
    /* 证据分析 */
    evidence_title: "JD 要求与简历证据",
    role_detected: "识别岗位",
    role_confidence: (n) => `规则识别置信度 ${n}%`,
    role_confidence_warning: "此置信度只描述岗位类型的规则匹配，不是录用概率、简历评分或适配度结论。",
    coverage_title: "关键词覆盖",
    coverage_ratio: "覆盖比例",
    coverage_unavailable: "暂不可计算",
    coverage_known: "已识别要求",
    coverage_unknown: "未识别要求",
    coverage_evidenced: "有原文证据",
    coverage_uncertain: "证据不确定",
    coverage_missing: "未找到证据",
    requirement_title: "JD 要求分组",
    priority_required: "必须要求",
    priority_preferred: "加分项",
    priority_unknown: "未分类要求",
    jd_evidence: "JD 原文",
    resume_evidence: "简历原文证据",
    resume_evidence_empty: "未找到可支持该要求的简历原文。",
    status_evidenced: "已有原文证据",
    status_uncertain: "证据不确定",
    status_not_found: "未找到简历证据",
    rewrite_title: "简历改写建议",
    rewrite_hint: "逐条接受、编辑或不采用。系统建议只来自简历原文；待确认事实不会默认导出。",
    rewrite_source: "简历原文",
    rewrite_suggested: "建议草稿",
    rewrite_requirements: "对应要求",
    rewrite_confirmed_facts: "已确认事实",
    rewrite_pending: "待确认字段",
    rewrite_empty: "当前没有基于原文生成的改写建议。",
    decision_accept: "接受",
    decision_edit: "编辑",
    decision_reject: "不采用",
    edit_suggestion: "编辑建议内容",
    confirm_pending_facts: "已确认补充事实真实",
    pending_export_blocked: "这条建议含待确认事实；仅接受不会导出，请编辑并确认真实后再导出。",
    export_title: "导出与反馈",
    export_button: "导出已确认草稿",
    export_sidebar: "快捷导出草稿",
    export_summary: (n) => `将导出 ${n} 条已接受或已编辑内容。`,
    export_pending: (n) => `${n} 条待确认建议当前不会导出。`,
    feedback_prompt: "这次证据分析对你有帮助吗？",
    feedback_helpful: "有帮助",
    feedback_neutral: "一般",
    feedback_unhelpful: "无帮助",
    feedback_thanks: "感谢反馈。反馈不会包含 JD、简历原文或建议文本。",
    match_reupload: "重新上传",
    match_view_gaps: (n) => `查看差距（${n} 项）`,
    /* 查漏补缺 */
    gap_title: "查漏补缺",
    gap_hint: "以下 JD 要求尚无明确简历原文证据。请只补充真实经历，不要为了覆盖关键词新增不存在的事实。",
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
    const requestId = ref("");
    const dragging = ref(false);
    const result = reactive({});
    const suggestionDecisions = reactive({});
    const confirmedPendingFacts = reactive({});
    const feedbackRating = ref("");
    const fileInput = ref(null);
    const menuTrigger = ref(null);
    const privacyConsent = ref(false);
    const isMobile = ref(typeof window !== "undefined" ? window.innerWidth <= 960 : false);
    const sidebarOpen = ref(!isMobile.value);
    const sidebarCollapsed = ref(false);
    let activeAnalysisController = null;
    let analysisRequestGeneration = 0;

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
    const hasResult = computed(() => result.ok === true);

    const currentSteps = computed(() => {
      if (!hasResult.value) {
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
      if (!hasResult.value) return t("sidebar_no_result");
      return t("sidebar_result_complete", result);
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
      if (id === "analysis") return hasResult.value;
      if (id === "gaps") return hasResult.value;
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

    const requirements = computed(() =>
      Array.isArray(result.requirements) ? result.requirements : []
    );
    const rewriteSuggestions = computed(() =>
      Array.isArray(result.rewrite_suggestions) ? result.rewrite_suggestions : []
    );
    const priorityGroups = computed(() => {
      const definitions = [
        { id: "required", label: t("priority_required") },
        { id: "preferred", label: t("priority_preferred") },
        { id: "unknown", label: t("priority_unknown") },
      ];
      return definitions
        .map((group) => ({
          ...group,
          items: requirements.value.filter((item) => {
            if (group.id === "unknown") {
              return !["required", "preferred"].includes(item.priority);
            }
            return item.priority === group.id;
          }),
        }))
        .filter((group) => group.items.length > 0);
    });
    const gapRequirements = computed(() =>
      requirements.value.filter((item) => item.resume_status !== "evidenced")
    );

    const clearReactiveObject = (target) => {
      Object.keys(target).forEach((key) => delete target[key]);
    };

    const initializeSuggestionDecisions = (suggestions) => {
      clearReactiveObject(suggestionDecisions);
      clearReactiveObject(confirmedPendingFacts);
      (suggestions || []).forEach((suggestion) => {
        if (
          suggestion.default_export === true &&
          suggestion.fact_status === "confirmed_source_only"
        ) {
          suggestionDecisions[suggestion.suggestion_id] = {
            decision: "accepted",
            text: suggestion.suggested,
          };
        }
      });
    };

    const setSuggestionDecision = (suggestion, decision) => {
      const current = suggestionDecisions[suggestion.suggestion_id];
      suggestionDecisions[suggestion.suggestion_id] = {
        decision,
        text: current?.text || suggestion.suggested || suggestion.source || "",
      };
      if (decision !== "edited") {
        confirmedPendingFacts[suggestion.suggestion_id] = false;
      }
    };

    const isSuggestionExportable = (suggestion) => {
      const state = suggestionDecisions[suggestion.suggestion_id];
      if (!state || !["accepted", "edited"].includes(state.decision)) return false;
      const text = (state.text || "").trim();
      if (!text) return false;
      if (suggestion.fact_status === "confirmed_source_only") return true;
      if (suggestion.fact_status !== "pending_confirmation") return false;
      return (
        state.decision === "edited" &&
        text !== (suggestion.suggested || "").trim() &&
        confirmedPendingFacts[suggestion.suggestion_id] === true
      );
    };

    const exportableSuggestions = computed(() =>
      rewriteSuggestions.value.filter(isSuggestionExportable)
    );
    const pendingExcludedCount = computed(() =>
      rewriteSuggestions.value.filter(
        (suggestion) =>
          suggestion.fact_status === "pending_confirmation" &&
          !isSuggestionExportable(suggestion)
      ).length
    );

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
      if (targetStep === 1 || hasResult.value) step.value = targetStep;
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

    const showApiError = (data, status) => {
      const code = data?.error_code;
      error.value =
        API_ERROR_MESSAGES[code] ||
        data?.message ||
        (status ? t("error_server", status) : t("error_fail"));
      requestId.value = data?.request_id || "";
    };

    // ── 提交 ──────────────────────────────────────────────────
    const submit = async () => {
      if (loading.value || !canSubmit.value) return;
      const requestGeneration = ++analysisRequestGeneration;
      const controller = new AbortController();
      activeAnalysisController = controller;
      const isActiveRequest = () =>
        analysisRequestGeneration === requestGeneration &&
        activeAnalysisController === controller;
      loading.value = true;
      error.value = "";
      requestId.value = "";
      const timeoutId = window.setTimeout(
        () => controller.abort(),
        ANALYSIS_TIMEOUT_MS
      );
      try {
        const fd = new FormData();
        fd.append("role", form.role);
        fd.append("privacy_consent_version", PRIVACY_CONSENT_VERSION);
        fd.append("jd", form.jd);
        fd.append("resume", form.file);

        const resp = await fetch("/api/v1/analyses", {
          method: "POST",
          body: fd,
          signal: controller.signal,
        });
        const contentType = resp.headers.get("content-type") || "";
        const data = contentType.includes("application/json") ? await resp.json() : null;
        if (!isActiveRequest()) return;
        if (!resp.ok || !data?.ok) {
          showApiError(data, resp.status);
          return;
        }
        clearReactiveObject(result);
        Object.assign(result, data);
        initializeSuggestionDecisions(data.rewrite_suggestions);
        feedbackRating.value = "";
        step.value = 2;
      } catch (e) {
        if (!isActiveRequest()) return;
        error.value = e?.name === "AbortError" ? t("error_timeout") : t("error_network");
      } finally {
        window.clearTimeout(timeoutId);
        if (isActiveRequest()) {
          activeAnalysisController = null;
          loading.value = false;
        }
      }
    };

    const statusLabel = (s) => ({
      evidenced: { text: t("status_evidenced"), cls: "status-evidenced" },
      uncertain: { text: t("status_uncertain"), cls: "status-uncertain" },
      not_found: { text: t("status_not_found"), cls: "status-not-found" },
    }[s] || { text: t("status_not_found"), cls: "status-not-found" });

    const pendingFieldLabel = (field) => ({
      metric: "结果或指标",
      time_range: "时间范围",
      personal_contribution: "个人贡献",
    }[field] || field);

    const requirementLabels = (ids) =>
      (ids || []).map((id) =>
        requirements.value.find((item) => item.requirement_id === id)?.label || id
      );

    const suggestionJdEvidence = (ids) =>
      [...new Set(
        (ids || [])
          .map((id) => requirements.value.find((item) => item.requirement_id === id)?.jd_evidence)
          .filter(Boolean)
      )];

    const warningLabel = (warning) => ({
      KNOWN_REQUIREMENT_COVERAGE_LOW: "当前 JD 中可识别的已知要求较少，请逐条核对下方 JD 原文。",
    }[warning] || "分析结果存在需人工核对的内容。");

    const roleConfidencePercent = computed(() => {
      const value = Number(result.role?.confidence);
      return Number.isFinite(value) ? Math.round(value * 100) : 0;
    });

    // ── 重置 ──────────────────────────────────────────────────
    const reset = () => {
      analysisRequestGeneration += 1;
      activeAnalysisController?.abort();
      activeAnalysisController = null;
      loading.value = false;
      step.value = 1;
      form.jd = ""; form.file = null; form.fileName = ""; form.role = "auto";
      error.value = "";
      requestId.value = "";
      feedbackRating.value = "";
      clearReactiveObject(result);
      clearReactiveObject(suggestionDecisions);
      clearReactiveObject(confirmedPendingFacts);
      if (fileInput.value) fileInput.value.value = "";
      closeSidebar();
    };

    // ── 下载 ──────────────────────────────────────────────────
    const downloadConfirmedDraft = () => {
      let md = "# JD 定制简历草稿\n\n";
      md += "> 本草稿由用户确认的原文与修改组成；请在投递前进行最终人工检查。\n\n";
      md += "## 已确认内容\n\n";
      if (exportableSuggestions.value.length === 0) {
        md += "当前没有可导出的已确认内容。\n";
      } else {
        exportableSuggestions.value.forEach((suggestion) => {
          const text = suggestionDecisions[suggestion.suggestion_id].text.trim();
          md += `- ${text.replace(/\n/g, "\n  ")}\n`;
        });
      }
      const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
      const anchor = document.createElement("a");
      anchor.href = URL.createObjectURL(blob);
      anchor.download = "简历优化草稿.md";
      anchor.click();
      URL.revokeObjectURL(anchor.href);
    };

    const setFeedbackRating = (rating) => {
      feedbackRating.value = rating;
    };

    return {
      // i18n
      t,
      // 状态
      step, loading, error, requestId, dragging, result, fileInput, menuTrigger,
      isMobile, sidebarOpen, sidebarCollapsed, appShellClass,
      sidebarExpanded, sidebarToggleLabel, mobileSidebarHidden,
      currentSteps, availableSteps, currentModeLabel, resultSummary, hasResult,
      // 表单
      roleOptions, form, privacyConsent, canSubmit,
      onFile, onDrop, submit,
      // 结果与用户决定
      priorityGroups, gapRequirements, rewriteSuggestions,
      suggestionDecisions, confirmedPendingFacts,
      exportableSuggestions, pendingExcludedCount,
      statusLabel, pendingFieldLabel, requirementLabels, suggestionJdEvidence,
      warningLabel, roleConfidencePercent, setSuggestionDecision,
      feedbackRating, setFeedbackRating,
      // 动作
      reset, downloadConfirmedDraft, toggleSidebar, closeSidebar, jumpToStep,
      // 页面导航
      navItems, currentPage, isNavEnabled, navigateTo,
    };
  },
}).mount("#app");
