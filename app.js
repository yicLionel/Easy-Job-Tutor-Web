/* AI 简历优化助手 — Vue 3 前端逻辑（无构建步骤，使用 CDN 全局 Vue）。
   集成 Skill 版本功能：Gate 系统、五维评审、事实台账、JD 拆解、简历诊断、多 JD 对比 */
const { createApp, reactive, ref, computed, watch, onMounted, onUnmounted } = Vue;

createApp({
  setup() {
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

    onUnmounted(() => {
      window.removeEventListener("resize", syncViewport);
    });

    // ── 模式管理（Gate 系统） ─────────────────────────────────
    const analysisMode = ref("complete");

    const modeOptions = [
      { value: "complete", label: "完整分析", desc: "JD + 简历" },
      { value: "jd_only", label: "仅分析 JD", desc: "拆解岗位要求" },
      { value: "resume_only", label: "仅诊断简历", desc: "简历基线检查" },
      { value: "multi_jd", label: "多 JD 对比", desc: "一份简历对比多个岗位" },
    ];

    const showJdInput = computed(() =>
      ["complete", "jd_only"].includes(analysisMode.value)
    );
    const showResumeInput = computed(() =>
      ["complete", "resume_only", "multi_jd"].includes(analysisMode.value)
    );
    const showMultiJdInput = computed(() =>
      analysisMode.value === "multi_jd"
    );

    // 步骤标题（根据分析结果模式自适应）
    const currentSteps = computed(() => {
      if (!result.mode) {
        return ["上传", "分析结果", "", ""];
      }
      switch (result.mode) {
        case "jd_only":
          return ["上传", "JD 拆解分析", "", ""];
        case "resume_only":
          return ["上传", "简历基线诊断", "", ""];
        case "multi_jd":
          return ["上传", "多 JD 对比", "", ""];
        default:
          return ["上传", "匹配度分析", "查漏补缺", "学习路线 & 面试"];
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
      const found = modeOptions.find((item) => item.value === analysisMode.value);
      return found ? found.label : "完整分析";
    });

    const resultSummary = computed(() => {
      if (!result.mode) {
        return "先选择分析模式并上传材料";
      }
      if (result.mode === "complete") {
        return `${result.role_label || "目标岗位"} · 匹配度 ${result.overall_score || 0}`;
      }
      if (result.mode === "jd_only") {
        return `${result.jd_analysis?.role_label || "JD 拆解"} · ${result.jd_analysis?.keyword_count || 0} 项要求`;
      }
      if (result.mode === "resume_only") {
        return `简历诊断 · ${result.resume_diagnosis?.issue_count || 0} 个问题`;
      }
      if (result.mode === "multi_jd") {
        return `多 JD 对比 · ${result.multi_jd_comparison?.jd_count || 0} 个岗位`;
      }
      return "分析完成";
    });

    // ── 表单 ──────────────────────────────────────────────────
    const roleOptions = [
      { value: "auto", label: "自动识别" },
      { value: "ai_product", label: "AI 产品" },
      { value: "ai_agent", label: "AI Agent 开发" },
      { value: "ai_ops", label: "AI 运营" },
    ];

    const form = reactive({ jd: "", role: "auto", file: null, fileName: "" });
    const jdTexts = ref(["", ""]); // 多 JD 模式

    const canSubmit = computed(() => {
      if (analysisMode.value === "complete" || analysisMode.value === "jd_only") {
        return form.jd.trim().length > 10 && (analysisMode.value !== "complete" || form.file);
      }
      if (analysisMode.value === "resume_only") {
        return !!form.file;
      }
      if (analysisMode.value === "multi_jd") {
        return jdTexts.value.every((t) => t.trim().length > 10) && !!form.file;
      }
      return false;
    });

    // 切换模式时重置表单
    watch(analysisMode, () => {
      form.jd = "";
      form.file = null;
      form.fileName = "";
      jdTexts.value = ["", ""];
      error.value = "";
      step.value = 1;
    });

    const closeSidebar = () => {
      if (isMobile.value) sidebarOpen.value = false;
    };

    const toggleSidebar = () => {
      if (isMobile.value) {
        sidebarOpen.value = !sidebarOpen.value;
        return;
      }
      sidebarCollapsed.value = !sidebarCollapsed.value;
    };

    const jumpToStep = (targetStep) => {
      if (targetStep < 1 || targetStep > 4) return;
      if (result.mode === "complete") {
        if (targetStep <= 4) step.value = targetStep;
      } else if (targetStep === 1 || targetStep === 2) {
        step.value = targetStep;
      }
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
    const removeJdField = (i) => {
      if (jdTexts.value.length > 2) jdTexts.value.splice(i, 1);
    };

    // ── 提交分析 ──────────────────────────────────────────────
    const submit = async () => {
      if (!canSubmit.value) return;
      loading.value = true; error.value = "";
      try {
        const fd = new FormData();
        fd.append("mode", analysisMode.value);
        fd.append("role", form.role);

        if (showJdInput.value) {
          fd.append("jd", form.jd);
        } else {
          fd.append("jd", ""); // 占位
        }

        if (showMultiJdInput.value) {
          fd.append("jds", JSON.stringify(jdTexts.value.filter((t) => t.trim())));
          fd.append("jd", ""); // 占位
        }

        if (showResumeInput.value && form.file) {
          fd.append("resume", form.file);
        }

        const resp = await fetch("/api/analyze", { method: "POST", body: fd });
        const contentType = resp.headers.get("content-type") || "";
        const data = contentType.includes("application/json") ? await resp.json() : null;
        if (!resp.ok) {
          error.value = data?.error || `服务器返回 HTTP ${resp.status}，请稍后重试。`;
          return;
        }
        if (!data.ok) { error.value = data.error || "分析失败，请重试。"; return; }
        Object.assign(result, data);
        step.value = 2;
      } catch (e) {
        error.value = "网络请求失败，请检查网络连接后重试。";
      } finally {
        loading.value = false;
      }
    };

    // ── 分数环（完整模式） ────────────────────────────────────
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
      if (s >= 80) return "匹配度优秀，竞争力强";
      if (s >= 60) return "匹配度良好，仍有提升空间";
      if (s >= 40) return "匹配度一般，建议重点补齐";
      return "匹配度偏低，差距较明显";
    });

    // ── 五维评审颜色 ──────────────────────────────────────────
    const dimColor = (score) => {
      if (score >= 80) return "var(--green)";
      if (score >= 60) return "var(--blue)";
      if (score >= 40) return "var(--orange)";
      return "var(--red)";
    };

    // ── 事实台账状态标签 ──────────────────────────────────────
    const statusLabel = (s) => ({
      confirmed: { text: "已确认", cls: "badge-green" },
      pending_confirmation: { text: "待确认", cls: "badge-orange" },
      model_inference: { text: "推断", cls: "badge-gray" },
    }[s] || { text: s, cls: "badge-gray" });

    // ── 重置 ──────────────────────────────────────────────────
    const reset = () => {
      step.value = 1;
      form.jd = ""; form.file = null; form.fileName = ""; form.role = "auto";
      jdTexts.value = ["", ""];
      error.value = "";
      // 清空 result
      Object.keys(result).forEach((k) => delete result[k]);
      closeSidebar();
    };

    // ── 下载 Markdown ─────────────────────────────────────────
    const downloadPlan = () => {
      const r = result;
      let md = `# AI 简历优化方案 · ${r.role_label}\n\n`;
      md += `> 匹配度：**${r.overall_score} / 100**\n\n`;

      // 五维评审
      md += `## 五维评审\n`;
      if (r.five_dim_review) {
        Object.entries(r.five_dim_review).forEach(([key, dim]) => {
          md += `- **${dim.label}**：${dim.score}/100\n  - 证据：${dim.evidence}\n`;
          if (dim.deduction) md += `  - 扣分：${dim.deduction}\n`;
          md += `  - 改进：${dim.improvement}\n`;
        });
      }

      md += `\n## 一、维度评分\n`;
      (r.dimensions || []).forEach((d) => { md += `- ${d.name}：${d.score}\n`; });

      md += `\n## 二、已匹配能力\n${(r.matched_skills || []).join("、") || "暂无明显命中"}\n\n`;
      md += `## 三、查漏补缺（${r.gap_count || 0} 项）\n`;
      (r.gaps || []).forEach((g) => {
        md += `- **${g.label}**（重要度 P${g.importance} · ${g.dim}）：${g.learn}` +
              (g.resource && g.resource.url ? ` 资源：${g.resource.name} ${g.resource.url}` : "") + `\n`;
      });

      if (r.learning_path) {
        md += `\n## 四、学习路线\n${r.learning_path.summary || ""}\n\n`;
        (r.learning_path.phases || []).forEach((ph) => {
          md += `### ${ph.name}\n`;
          (ph.steps || []).forEach((st) => {
            md += `- ${st.skill}（约 ${st.estimate}）：${st.action}` +
                  (st.resource && st.resource.url ? ` 资源：${st.resource.name} ${st.resource.url}` : "") + `\n`;
          });
          md += `\n`;
        });
      }

      if (r.interview) {
        md += `## 五、面试辅导\n### 通用问题\n`;
        (r.interview.base_questions || []).forEach((q) => { md += `- ${q}\n`; });
        if (r.interview.targeted_questions && r.interview.targeted_questions.length) {
          md += `### 针对性追问\n`;
          r.interview.targeted_questions.forEach((q) => { md += `- ${q.question}\n`; });
        }
      }

      const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `简历优化方案_${r.role_label || "分析结果"}.md`;
      a.click();
      URL.revokeObjectURL(a.href);
    };

    return {
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
    };
  },
}).mount("#app");
