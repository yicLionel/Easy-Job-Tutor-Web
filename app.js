/* AI 简历优化助手 — Vue 3 前端逻辑（无构建步骤，使用 CDN 全局 Vue）。 */
const { createApp, reactive, ref, computed } = Vue;

createApp({
  setup() {
    const steps = ["上传与匹配", "匹配度分析", "查漏补缺", "学习路线 & 面试"];
    const step = ref(1);
    const loading = ref(false);
    const error = ref("");
    const dragging = ref(false);
    const result = reactive({});
    const fileInput = ref(null);

    const roleOptions = [
      { value: "auto", label: "自动识别" },
      { value: "ai_product", label: "AI 产品" },
      { value: "ai_agent", label: "AI Agent 开发" },
      { value: "ai_ops", label: "AI 运营" },
    ];

    const form = reactive({ jd: "", role: "auto", file: null, fileName: "" });

    const canSubmit = computed(() => form.jd.trim().length > 10 && form.file);

    const onFile = (e) => {
      const f = e.target.files && e.target.files[0];
      if (f) { form.file = f; form.fileName = f.name; error.value = ""; }
    };
    const onDrop = (e) => {
      dragging.value = false;
      const f = e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) { form.file = f; form.fileName = f.name; error.value = ""; }
    };

    const submit = async () => {
      if (!canSubmit.value) return;
      loading.value = true; error.value = "";
      try {
        const fd = new FormData();
        fd.append("jd", form.jd);
        fd.append("role", form.role);
        fd.append("resume", form.file);
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

    // 分数环
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

    const reset = () => {
      step.value = 1;
      form.jd = ""; form.file = null; form.fileName = ""; form.role = "auto";
      error.value = "";
    };

    const downloadPlan = () => {
      const r = result;
      let md = `# AI 简历优化方案 · ${r.role_label}\n\n`;
      md += `> 匹配度：**${r.overall_score} / 100**\n\n`;
      md += `## 一、维度评分\n`;
      r.dimensions.forEach((d) => { md += `- ${d.name}：${d.score}\n`; });
      md += `\n## 二、已匹配能力\n${r.matched_skills.join("、") || "暂无明显命中"}\n\n`;
      md += `## 三、查漏补缺（${r.gap_count} 项）\n`;
      r.gaps.forEach((g) => {
        md += `- **${g.label}**（重要度 P${g.importance} · ${g.dim}）：${g.learn}` +
              (g.resource && g.resource.url ? ` 资源：${g.resource.name} ${g.resource.url}` : "") + `\n`;
      });
      md += `\n## 四、学习路线\n${r.learning_path.summary}\n\n`;
      r.learning_path.phases.forEach((ph) => {
        md += `### ${ph.name}\n`;
        ph.steps.forEach((st) => {
          md += `- ${st.skill}（约 ${st.estimate}）：${st.action}` +
                (st.resource && st.resource.url ? ` 资源：${st.resource.name} ${st.resource.url}` : "") + `\n`;
        });
        md += `\n`;
      });
      md += `## 五、面试辅导\n### 通用问题\n`;
      r.interview.base_questions.forEach((q) => { md += `- ${q}\n`; });
      if (r.interview.targeted_questions.length) {
        md += `### 针对性追问\n`;
        r.interview.targeted_questions.forEach((q) => { md += `- ${q.question}\n`; });
      }
      const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `简历优化方案_${r.role_label}.md`;
      a.click();
      URL.revokeObjectURL(a.href);
    };

    return {
      steps, step, loading, error, dragging, result, fileInput,
      roleOptions, form, canSubmit, onFile, onDrop, submit,
      R, circ, ringColor, scoreWord, reset, downloadPlan,
    };
  },
}).mount("#app");
