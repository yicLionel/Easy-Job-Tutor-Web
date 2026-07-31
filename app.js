/* AI 简历优化助手 — Vue 3 前端逻辑（无构建步骤，使用 CDN 全局 Vue）。
   集成 Skill 版本功能：Gate 系统、五维评审、事实台账、JD 拆解、简历诊断、多 JD 对比
   中英文 i18n 支持。 */
const { createApp, reactive, ref, computed, watch, onMounted, onUnmounted } = Vue;

// ── i18n 字典 ──────────────────────────────────────────
const LOCALE_KEY = "easy_job_tutor_locale";
const LOCALES = {
  zh: {
    /* 品牌 / 通用 */
    app_title: "AI 简历优化助手",
    app_subtitle: "匹配度分析 · 查漏补缺 · 学习路线 · 面试辅导",
    app_audience: "面向在校大学生 / 应届毕业生 · 首版覆盖 AI 产品 / AI Agent 开发 / AI 运营",
    workspace: "工作台",
    dashboard: "工作台",
    /* 侧边栏导航 */
    nav_home: "首页",
    nav_analysis: "分析页",
    nav_gaps: "查漏补缺",
    nav_learning: "学习路线",
    nav_interview: "模拟面试",
    nav_home_desc: "上传材料与选择分析模式",
    nav_analysis_desc: "查看匹配度与能力分析结果",
    nav_gaps_desc: "查看差距与补齐建议",
    nav_learning_desc: "分阶段学习路线规划",
    nav_interview_desc: "面试问题与回答准备",
    /* 侧边栏 */
    sidebar_hide: "关闭侧边栏",
    sidebar_collapse: "折叠侧边栏",
    sidebar_expand: "展开侧边栏",
    sidebar_current_mode: "当前模式",
    sidebar_nav: "页面导航",
    sidebar_modes: "分析模式",
    sidebar_actions: "快捷操作",
    sidebar_new: "新建分析",
    sidebar_clear: "清空结果",
    sidebar_download: "下载 Markdown",
    sidebar_no_result: "先选择分析模式并上传材料",
    sidebar_result_complete: (r) => `${r.role_label || "目标岗位"} · 匹配度 ${r.overall_score || 0}`,
    sidebar_result_jd: (r) => `${r.jd_analysis?.role_label || "JD 拆解"} · ${r.jd_analysis?.keyword_count || 0} 项要求`,
    sidebar_result_resume: (r) => `简历诊断 · ${r.resume_diagnosis?.issue_count || 0} 个问题`,
    sidebar_result_multi: (r) => `多 JD 对比 · ${r.multi_jd_comparison?.jd_count || 0} 个岗位`,
    sidebar_result_done: "分析完成",
    /* 分析模式 */
    mode_complete: "完整分析",
    mode_complete_desc: "JD + 简历",
    mode_jd: "仅分析 JD",
    mode_jd_desc: "拆解岗位要求",
    mode_resume: "仅诊断简历",
    mode_resume_desc: "简历基线检查",
    mode_multi: "多 JD 对比",
    mode_multi_desc: "一份简历对比多个岗位",
    /* 步骤 */
    step_upload: "上传",
    step_result: "分析结果",
    step_jd_analysis: "JD 拆解分析",
    step_resume_diag: "简历基线诊断",
    step_multi: "多 JD 对比",
    step_match: "匹配度分析",
    step_gaps: "查漏补缺",
    step_learn: "学习路线 & 面试",
    step_sub_1: "上传材料与选择模式",
    step_sub_2: "查看当前分析结果",
    step_sub_3: "查看差距与补齐建议",
    step_sub_4: "学习路线与面试问题",
    /* 步骤 1 */
    upload_title: "选择分析模式",
    upload_hint: "根据你要分析的内容选择模式，系统将自动匹配最佳分析流程。",
    upload_jd_label: "岗位 JD（粘贴招聘信息全文）",
    upload_jd_placeholder: "例如：我们正在招聘 AI 产品实习生，负责 LLM 应用产品的需求分析与 0-1 落地……",
    upload_multi_label: "多个岗位 JD（至少 2 个）",
    upload_add_jd: "+ 添加一个 JD",
    upload_resume_label: "上传简历（PDF / Word / TXT）",
    upload_select: "选择文件",
    upload_drag: "将文件拖拽到此处，或点击选择",
    upload_role_label: "目标岗位",
    uploading: "分析中…",
    upload_submit: "开始分析",
    error_server: (s) => `服务器返回 HTTP ${s}，请稍后重试。`,
    error_fail: "分析失败，请重试。",
    error_network: "网络请求失败，请检查网络连接后重试。",
    /* 岗位选择 */
    role_auto: "自动识别",
    role_product: "AI 产品",
    role_agent: "AI Agent 开发",
    role_ops: "AI 运营",
    /* JD 分析 */
    jd_title: (l) => `JD 拆解分析 · ${l}`,
    jd_required: "核心职责 / 必备要求",
    jd_empty_required: "暂未识别到明确必备要求",
    jd_preferred: "加分项",
    jd_empty_preferred: "暂未识别到加分项",
    jd_tools: "工具 / 技术栈",
    jd_domain: "领域知识",
    jd_soft: "软素质要求",
    jd_hidden: "隐性条件",
    jd_rerun: "重新分析",
    /* 简历诊断 */
    diag_title: "简历基线诊断",
    diag_hint: (n) => `基于简历文本的结构与内容分析（${n} 字）。`,
    diag_sections: "📋 章节检测",
    diag_empty_sections: "未检测到标准章节",
    diag_strengths: "✅ 优势",
    diag_empty_strengths: "暂无明显优势信号",
    diag_issues: (n) => `⚠️ 待改进（${n} 项）`,
    diag_questions: "❓ 需要补充的信息",
    diag_rerun: "重新诊断",
    /* 多 JD 对比 */
    multi_title: "多 JD 对比分析",
    multi_hint: (r) => `同一份简历与 ${r.multi_jd_comparison.jd_count} 个岗位的匹配对比。检测到岗位：${r.multi_jd_comparison.roles_detected.join("、")}`,
    multi_shared: "🔄 共通优势（所有 JD 均命中的能力）",
    multi_dim: "维度",
    multi_score: "匹配度",
    multi_hit: "能力命中",
    multi_gap: "能力差距",
    multi_diff: "📊 差异化要求",
    multi_rerun: "重新分析",
    /* 完整分析 */
    match_title: (l) => `匹配度分析（${l}）`,
    ring_unit: "匹配度",
    score_excellent: "匹配度优秀，竞争力强",
    score_good: "匹配度良好，仍有提升空间",
    score_fair: "匹配度一般，建议重点补齐",
    score_poor: "匹配度偏低，差距较明显",
    matched_skills: (s) => `已匹配能力：${(s || []).join("、") || "暂无明显命中"}`,
    five_dim: "📊 五维评审",
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
    gap_deduction: (s) => `扣分：${s}`,
    match_reupload: "重新上传",
    match_view_gaps: (n) => `查看差距（${n} 项）`,
    /* 查漏补缺 */
    gap_title: "查漏补缺",
    gap_hint: "以下能力在岗位 JD 中重要，但你的简历暂未体现，建议优先补齐：",
    gap_resource: (n) => `学习资源：${n} ↗`,
    gap_back: "返回",
    gap_next: "生成学习路线 & 面试辅导",
    /* 学习路线 + 面试 */
    learn_title: "学习路线 & 面试辅导",
    learn_phases: "📚 分阶段学习路线",
    interview_title: "🎤 面试辅导",
    interview_common: (l) => `通用问题（${l}）`,
    interview_targeted: "针对性追问（基于你的差距）",
    learn_back: "返回",
    learn_download: "下载优化方案（Markdown）",
    learn_restart: "重新开始",
    /* 页脚 */
    footer: "v0.2 · i18n 中英文切换 · 集成 Gate 系统 · 五维评审 · 事实台账 · 多模式分析",
    /* 下载文件 */
    md_filename: (l) => `简历优化方案_${l}.md`,
    /* 标签 */
    reanalyze: "重新分析",
  },

  en: {
    app_title: "AI Resume Optimizer",
    app_subtitle: "Match Analysis · Skill Gaps · Learning Path · Interview Prep",
    app_audience: "For students & fresh graduates · AI Product / AI Agent Dev / AI Operations",
    workspace: "Workbench",
    dashboard: "Dashboard",
    /* Nav */
    nav_home: "Home",
    nav_analysis: "Analysis",
    nav_gaps: "Skill Gaps",
    nav_learning: "Learning Path",
    nav_interview: "Mock Interview",
    nav_home_desc: "Upload materials & select analysis mode",
    nav_analysis_desc: "View match scores & skill analysis",
    nav_gaps_desc: "Review gaps & improvement suggestions",
    nav_learning_desc: "Phased learning roadmap",
    nav_interview_desc: "Interview questions & prep",
    /* Sidebar */
    sidebar_hide: "Close sidebar",
    sidebar_collapse: "Collapse sidebar",
    sidebar_expand: "Expand sidebar",
    sidebar_current_mode: "Current Mode",
    sidebar_nav: "Pages",
    sidebar_modes: "Analysis Modes",
    sidebar_actions: "Quick Actions",
    sidebar_new: "New Analysis",
    sidebar_clear: "Clear Results",
    sidebar_download: "Download Markdown",
    sidebar_no_result: "Select a mode and upload materials first",
    sidebar_result_complete: (r) => `${r.role_label || "Target"} · Score ${r.overall_score || 0}`,
    sidebar_result_jd: (r) => `${r.jd_analysis?.role_label || "JD Analysis"} · ${r.jd_analysis?.keyword_count || 0} requirements`,
    sidebar_result_resume: (r) => `Resume · ${r.resume_diagnosis?.issue_count || 0} issues`,
    sidebar_result_multi: (r) => `Multi-JD · ${r.multi_jd_comparison?.jd_count || 0} roles`,
    sidebar_result_done: "Analysis complete",
    /* Modes */
    mode_complete: "Full Analysis",
    mode_complete_desc: "JD + Resume",
    mode_jd: "JD Only",
    mode_jd_desc: "Break down requirements",
    mode_resume: "Resume Only",
    mode_resume_desc: "Baseline check",
    mode_multi: "Multi-JD",
    mode_multi_desc: "Compare across roles",
    /* Steps */
    step_upload: "Upload",
    step_result: "Results",
    step_jd_analysis: "JD Analysis",
    step_resume_diag: "Resume Diagnosis",
    step_multi: "Multi-JD",
    step_match: "Match Score",
    step_gaps: "Skill Gaps",
    step_learn: "Learning & Interview",
    step_sub_1: "Upload materials & select mode",
    step_sub_2: "View analysis results",
    step_sub_3: "Review gaps & suggestions",
    step_sub_4: "Learning path & interview prep",
    /* Step 1 */
    upload_title: "Select Analysis Mode",
    upload_hint: "Choose a mode based on what you want to analyze. The system will route to the best workflow.",
    upload_jd_label: "Job Description (paste full text)",
    upload_jd_placeholder: "e.g. We are hiring an AI Product Intern, responsible for LLM application product analysis and 0-1 delivery…",
    upload_multi_label: "Multiple Job Descriptions (at least 2)",
    upload_add_jd: "+ Add another JD",
    upload_resume_label: "Upload Resume (PDF / Word / TXT)",
    upload_select: "Select File",
    upload_drag: "Drag & drop here, or click to select",
    upload_role_label: "Target Role",
    uploading: "Analyzing…",
    upload_submit: "Start Analysis",
    error_server: (s) => `Server returned HTTP ${s}, please retry later.`,
    error_fail: "Analysis failed. Please try again.",
    error_network: "Network request failed. Please check your connection.",
    /* Role */
    role_auto: "Auto Detect",
    role_product: "AI Product",
    role_agent: "AI Agent Dev",
    role_ops: "AI Operations",
    /* JD Analysis */
    jd_title: (l) => `JD Analysis · ${l}`,
    jd_required: "Core Responsibilities / Required",
    jd_empty_required: "No clear requirements identified",
    jd_preferred: "Nice to Have",
    jd_empty_preferred: "No preferred items identified",
    jd_tools: "Tools / Technologies",
    jd_domain: "Domain Knowledge",
    jd_soft: "Soft Skills",
    jd_hidden: "Hidden Requirements",
    jd_rerun: "Re-analyze",
    /* Resume Diagnosis */
    diag_title: "Resume Diagnosis",
    diag_hint: (n) => `Structural & content analysis based on resume text (${n} characters).`,
    diag_sections: "📋 Sections Found",
    diag_empty_sections: "No standard sections detected",
    diag_strengths: "✅ Strengths",
    diag_empty_strengths: "No clear strengths detected",
    diag_issues: (n) => `⚠️ Improvements (${n})`,
    diag_questions: "❓ Info Needed",
    diag_rerun: "Re-diagnose",
    /* Multi-JD */
    multi_title: "Multi-JD Comparison",
    multi_hint: (r) => `Comparing 1 resume against ${r.multi_jd_comparison.jd_count} roles. Detected: ${r.multi_jd_comparison.roles_detected.join(", ")}`,
    multi_shared: "🔄 Shared Strengths (matched across all JDs)",
    multi_dim: "Dimension",
    multi_score: "Match Score",
    multi_hit: "Skills Hit",
    multi_gap: "Skill Gaps",
    multi_diff: "📊 Differentiators",
    multi_rerun: "Re-analyze",
    /* Complete */
    match_title: (l) => `Match Analysis · ${l}`,
    ring_unit: "Match",
    score_excellent: "Excellent match, strong competitiveness",
    score_good: "Good match, room for improvement",
    score_fair: "Average match, consider focused improvement",
    score_poor: "Low match, significant gaps",
    matched_skills: (s) => `Matched: ${(s || []).join(", ") || "none"}`,
    five_dim: "📊 Five-Dimension Review",
    ledger_title: (n) => `📋 Fact Ledger (${n} skills)`,
    ledger_hint: "Status tracking: Confirmed = keywords found, Pending = partial match, Inferred = no keywords found.",
    ledger_skill: "Skill",
    ledger_dim: "Dimension",
    ledger_imp: "Importance",
    ledger_status: "Status",
    ledger_evidence: "Evidence",
    status_confirmed: "Confirmed",
    status_pending: "Pending",
    status_infer: "Inferred",
    gap_deduction: (s) => `Deduction: ${s}`,
    match_reupload: "Re-upload",
    match_view_gaps: (n) => `View Gaps (${n})`,
    /* Gap */
    gap_title: "Skill Gaps",
    gap_hint: "These skills are important for the JD but not found in your resume. Prioritize filling them:",
    gap_resource: (n) => `Resource: ${n} ↗`,
    gap_back: "Back",
    gap_next: "Learning Path & Interview",
    /* Learning + Interview */
    learn_title: "Learning Path & Interview Prep",
    learn_phases: "📚 Learning Phases",
    interview_title: "🎤 Interview Prep",
    interview_common: (l) => `General Questions (${l})`,
    interview_targeted: "Targeted Questions (based on gaps)",
    learn_back: "Back",
    learn_download: "Download Plan (Markdown)",
    learn_restart: "Restart",
    /* Footer */
    footer: "v0.2 · i18n EN/CN toggle · Gate system · 5-dim review · Fact ledger · Multi-mode analysis",
    /* Download */
    md_filename: (l) => `resume_plan_${l}.md`,
    /* Shared */
    reanalyze: "Re-analyze",
  },
};

createApp({
  setup() {
    // ── i18n ──────────────────────────────────────────────────
    const locale = ref(localStorage.getItem(LOCALE_KEY) || "zh");
    watch(locale, (v) => localStorage.setItem(LOCALE_KEY, v));

    const dict = computed(() => LOCALES[locale.value] || LOCALES.zh);
    const t = (key, ...args) => {
      const val = dict.value[key];
      if (typeof val === "function") return val(...args);
      return val ?? key;
    };
    const toggleLocale = () => { locale.value = locale.value === "zh" ? "en" : "zh"; };

    // ── 基础状态 ──────────────────────────────────────────────
    const step = ref(1);
    const loading = ref(false);
    const error = ref("");
    const dragging = ref(false);
    const result = reactive({});
    const fileInput = ref(null);
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

    // ── 模式管理 ──────────────────────────────────────────────
    const analysisMode = ref("complete");

    const modeOptions = computed(() => [
      { value: "complete", label: t("mode_complete"), desc: t("mode_complete_desc") },
      { value: "jd_only", label: t("mode_jd"), desc: t("mode_jd_desc") },
      { value: "resume_only", label: t("mode_resume"), desc: t("mode_resume_desc") },
      { value: "multi_jd", label: t("mode_multi"), desc: t("mode_multi_desc") },
    ]);

    const showJdInput = computed(() =>
      ["complete", "jd_only"].includes(analysisMode.value)
    );
    const showResumeInput = computed(() =>
      ["complete", "resume_only", "multi_jd"].includes(analysisMode.value)
    );
    const showMultiJdInput = computed(() =>
      analysisMode.value === "multi_jd"
    );

    // 步骤标题
    const currentSteps = computed(() => {
      if (!result.mode) {
        return [t("step_upload"), t("step_result"), "", ""];
      }
      switch (result.mode) {
        case "jd_only":
          return [t("step_upload"), t("step_jd_analysis"), "", ""];
        case "resume_only":
          return [t("step_upload"), t("step_resume_diag"), "", ""];
        case "multi_jd":
          return [t("step_upload"), t("step_multi"), "", ""];
        default:
          return [t("step_upload"), t("step_match"), t("step_gaps"), t("step_learn")];
      }
    });

    const appShellClass = computed(() => ({
      "sidebar-open": sidebarOpen.value,
      "sidebar-collapsed": sidebarCollapsed.value,
      "mobile-shell": isMobile.value,
    }));

    const availableSteps = computed(() =>
      currentSteps.value
        .map((label, index) => ({ step: index + 1, label }))
        .filter((item) => item.label)
    );

    const currentModeLabel = computed(() => {
      const found = modeOptions.value.find((item) => item.value === analysisMode.value);
      return found ? found.label : t("mode_complete");
    });

    const resultSummary = computed(() => {
      if (!result.mode) return t("sidebar_no_result");
      if (result.mode === "complete") return t("sidebar_result_complete", result);
      if (result.mode === "jd_only") return t("sidebar_result_jd", result);
      if (result.mode === "resume_only") return t("sidebar_result_resume", result);
      if (result.mode === "multi_jd") return t("sidebar_result_multi", result);
      return t("sidebar_result_done");
    });

    // ── 切换分析模式 ──────────────────────────────────────────
    const switchMode = (newMode) => {
      if (newMode === analysisMode.value) {
        // 相同模式：只回步骤 1
        step.value = 1;
        closeSidebar();
        return;
      }
      // 不同模式：重置表单 + 切换到新模式
      analysisMode.value = newMode;
      // watch(analysisMode) 已处理 form 清空和 step=1
      closeSidebar();
    };

    // ── 页面导航 ──────────────────────────────────────────────
    // 图标映射：用 emoji 做轻量图标，不额外引入图标库
    const PAGE_ICONS = { home: "🏠", analysis: "📊", gaps: "🔍", learning: "📚", interview: "🎤" };

    const navItems = computed(() => [
      { id: "home", label: t("nav_home"), desc: t("nav_home_desc"), icon: PAGE_ICONS.home, step: 1 },
      { id: "analysis", label: t("nav_analysis"), desc: t("nav_analysis_desc"), icon: PAGE_ICONS.analysis, step: 2 },
      { id: "gaps", label: t("nav_gaps"), desc: t("nav_gaps_desc"), icon: PAGE_ICONS.gaps, step: 3 },
      { id: "learning", label: t("nav_learning"), desc: t("nav_learning_desc"), icon: PAGE_ICONS.learning, step: 4 },
      { id: "interview", label: t("nav_interview"), desc: t("nav_interview_desc"), icon: PAGE_ICONS.interview, step: 4 },
    ]);

    const currentPage = computed(() => {
      const pageMap = { 1: "home", 2: "analysis", 3: "gaps", 4: "learning" };
      return pageMap[step.value] || "home";
    });

    const isNavEnabled = (id) => {
      // 首页永远可用
      if (id === "home") return true;
      // 分析页：必须有分析结果
      if (id === "analysis") return !!result.mode;
      // 查漏补缺、学习路线、模拟面试：仅 complete 模式且结果存在
      if (["gaps", "learning", "interview"].includes(id)) {
        return result.mode === "complete";
      }
      return false;
    };

    const navigateTo = (id) => {
      if (!isNavEnabled(id)) return;
      const item = navItems.value.find((n) => n.id === id);
      if (!item) return;
      // 学习路线和模拟面试都跳 step 4，分别关注不同区域
      if (id === "interview" && item.step === 4) {
        step.value = 4;
        // 等 DOM 渲染后滚动到面试区
        setTimeout(() => {
          const el = document.getElementById("interview-section");
          if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 100);
      } else {
        step.value = item.step;
      }
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
    const jdTexts = ref(["", ""]);

    const canSubmit = computed(() => {
      if (analysisMode.value === "complete" || analysisMode.value === "jd_only") {
        return form.jd.trim().length > 10 && (analysisMode.value !== "complete" || form.file);
      }
      if (analysisMode.value === "resume_only") return !!form.file;
      if (analysisMode.value === "multi_jd") {
        return jdTexts.value.every((t) => t.trim().length > 10) && !!form.file;
      }
      return false;
    });

    watch(analysisMode, () => {
      form.jd = "";
      form.file = null;
      form.fileName = "";
      jdTexts.value = ["", ""];
      error.value = "";
      step.value = 1;
    });

    const closeSidebar = () => { if (isMobile.value) sidebarOpen.value = false; };
    const toggleSidebar = () => {
      if (isMobile.value) { sidebarOpen.value = !sidebarOpen.value; return; }
      sidebarCollapsed.value = !sidebarCollapsed.value;
    };

    const jumpToStep = (targetStep) => {
      if (targetStep < 1 || targetStep > 4) return;
      if (result.mode === "complete") { if (targetStep <= 4) step.value = targetStep; }
      else if (targetStep === 1 || targetStep === 2) { step.value = targetStep; }
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

    const addJdField = () => { jdTexts.value.push(""); };
    const removeJdField = (i) => { if (jdTexts.value.length > 2) jdTexts.value.splice(i, 1); };

    // ── 提交 ──────────────────────────────────────────────────
    const submit = async () => {
      if (!canSubmit.value) return;
      loading.value = true; error.value = "";
      try {
        const fd = new FormData();
        fd.append("mode", analysisMode.value);
        fd.append("role", form.role);
        fd.append("locale", locale.value);
        if (showJdInput.value) { fd.append("jd", form.jd); }
        else { fd.append("jd", ""); }
        if (showMultiJdInput.value) {
          fd.append("jds", JSON.stringify(jdTexts.value.filter((t) => t.trim())));
          fd.append("jd", "");
        }
        if (showResumeInput.value && form.file) { fd.append("resume", form.file); }

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

    // ── 分数环 ────────────────────────────────────────────────
    const R = 80;
    const circ = 2 * Math.PI * R;
    const ringColor = computed(() => {
      const s = result.overall_score || 0;
      if (s >= 80) return "var(--green)";
      if (s >= 60) return "var(--blue)";
      if (s >= 40) return "var(--orange)";
      return "var(--red)";
    });
    const scoreWord = computed(() => {
      const s = result.overall_score || 0;
      if (s >= 80) return t("score_excellent");
      if (s >= 60) return t("score_good");
      if (s >= 40) return t("score_fair");
      return t("score_poor");
    });

    const dimColor = (score) => {
      if (score >= 80) return "var(--green)";
      if (score >= 60) return "var(--blue)";
      if (score >= 40) return "var(--orange)";
      return "var(--red)";
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
      jdTexts.value = ["", ""];
      error.value = "";
      Object.keys(result).forEach((k) => delete result[k]);
      closeSidebar();
    };

    // ── 下载 ──────────────────────────────────────────────────
    const downloadPlan = () => {
      const r = result;
      const L = locale.value === "en" ? "en" : "zh";
      let md = L === "en"
        ? `# AI Resume Optimization Plan · ${r.role_label}\n\n> Score: **${r.overall_score} / 100**\n\n`
        : `# AI 简历优化方案 · ${r.role_label}\n\n> 匹配度：**${r.overall_score} / 100**\n\n`;

      md += L === "en" ? "## Five-Dimension Review\n" : "## 五维评审\n";
      if (r.five_dim_review) {
        Object.entries(r.five_dim_review).forEach(([key, dim]) => {
          md += `- **${dim.label}**：${dim.score}/100\n  - ${L === "en" ? "Evidence" : "证据"}：${dim.evidence}\n`;
          if (dim.deduction) md += `  - ${L === "en" ? "Deduction" : "扣分"}：${dim.deduction}\n`;
          md += `  - ${L === "en" ? "Improvement" : "改进"}：${dim.improvement}\n`;
        });
      }

      md += L === "en" ? "\n## 1. Dimension Scores\n" : "\n## 一、维度评分\n";
      (r.dimensions || []).forEach((d) => { md += `- ${d.name}：${d.score}\n`; });

      md += L === "en" ? `\n## 2. Matched Skills\n${(r.matched_skills || []).join(", ") || "none"}\n\n` : `\n## 二、已匹配能力\n${(r.matched_skills || []).join("、") || "暂无明显命中"}\n\n`;
      md += L === "en" ? `## 3. Skill Gaps (${r.gap_count || 0})\n` : `## 三、查漏补缺（${r.gap_count || 0} 项）\n`;
      (r.gaps || []).forEach((g) => {
        const link = g.resource && g.resource.url ? ` ${L === "en" ? "Resource" : "资源"}：${g.resource.name} ${g.resource.url}` : "";
        md += `- **${g.label}** (P${g.importance} · ${g.dim})：${g.learn}${link}\n`;
      });

      if (r.learning_path) {
        md += L === "en" ? "\n## 4. Learning Path\n" : "\n## 四、学习路线\n";
        md += `${r.learning_path.summary || ""}\n\n`;
        (r.learning_path.phases || []).forEach((ph) => {
          md += `### ${ph.name}\n`;
          (ph.steps || []).forEach((st) => {
            const link = st.resource && st.resource.url ? ` ${L === "en" ? "Resource" : "资源"}：${st.resource.name} ${st.resource.url}` : "";
            md += `- ${st.skill} (${st.estimate})：${st.action}${link}\n`;
          });
          md += "\n";
        });
      }

      if (r.interview) {
        md += L === "en" ? "## 5. Interview Prep\n### General Questions\n" : "## 五、面试辅导\n### 通用问题\n";
        (r.interview.base_questions || []).forEach((q) => { md += `- ${q}\n`; });
        if (r.interview.targeted_questions && r.interview.targeted_questions.length) {
          md += L === "en" ? "### Targeted Questions\n" : "### 针对性追问\n";
          r.interview.targeted_questions.forEach((q) => { md += `- ${q.question}\n`; });
        }
      }

      const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = t("md_filename", r.role_label || "result");
      a.click();
      URL.revokeObjectURL(a.href);
    };

    return {
      // i18n
      locale, t, toggleLocale, dict,
      // 状态
      step, loading, error, dragging, result, fileInput,
      isMobile, sidebarOpen, sidebarCollapsed, appShellClass,
      // 模式
      analysisMode, modeOptions, showJdInput, showResumeInput, showMultiJdInput,
      currentSteps, availableSteps, currentModeLabel, resultSummary,
      // 表单
      roleOptions, form, jdTexts, canSubmit,
      onFile, onDrop, addJdField, removeJdField, submit,
      // 分数环
      R, circ, ringColor, scoreWord,
      // 五维
      dimColor,
      // 台账
      statusLabel,
      // 动作
      reset, downloadPlan, toggleSidebar, closeSidebar, jumpToStep,
      // 页面导航
      navItems, currentPage, isNavEnabled, navigateTo,
      // 模式切换
      switchMode,
    };
  },
}).mount("#app");
