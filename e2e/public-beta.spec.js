const fs = require("fs");
const path = require("path");
const { test, expect } = require("@playwright/test");

const FIXTURE_DIR = path.join(__dirname, "..", "tests", "fixtures");
const JD_FIXTURE = path.join(FIXTURE_DIR, "jd.txt");
const RESUME_FIXTURE = path.join(FIXTURE_DIR, "resume.txt");

const deterministicAnalysis = {
  ok: true,
  analysis_id: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  algorithm_version: "evidence-v1",
  knowledge_base_version: "2026-08-11",
  role: {
    id: "ai_product",
    label: "AI 产品",
    confidence: 0.82,
  },
  coverage_summary: {
    known_requirement_count: 2,
    unknown_requirement_count: 0,
    evidenced_count: 2,
    uncertain_count: 0,
    missing_evidence_count: 0,
    keyword_coverage: 100,
  },
  requirements: [
    {
      requirement_id: "ap_user",
      label: "用户研究",
      priority: "required",
      jd_evidence: "必须能够进行用户研究",
      resume_status: "evidenced",
      resume_evidence: ["负责用户访谈并完成 PRD 撰写。"],
      reason: "action_context",
    },
    {
      requirement_id: "ap_ship",
      label: "AI 产品落地",
      priority: "preferred",
      jd_evidence: "推动一个 AI 应用从 0 到 1 上线",
      resume_status: "evidenced",
      resume_evidence: ["推动 AI 应用上线。"],
      reason: "action_context",
    },
  ],
  rewrite_suggestions: [
    {
      suggestion_id: "rw-confirmed",
      source: "负责用户访谈并完成 PRD 撰写。",
      suggested: "负责用户访谈并完成 PRD 撰写。",
      requirement_ids: ["ap_user"],
      fact_status: "confirmed_source_only",
      pending_fields: [],
      default_export: true,
    },
    {
      suggestion_id: "rw-pending",
      source: "推动 AI 应用上线。",
      suggested: "推动 AI 应用上线。",
      requirement_ids: ["ap_ship"],
      fact_status: "pending_confirmation",
      pending_fields: ["metric", "time_range", "personal_contribution"],
      default_export: false,
    },
  ],
  warnings: [],
};

const LONG_REQUIREMENT_LABEL = "L".repeat(500);
const LONG_JD_EVIDENCE = "J".repeat(500);
const LONG_RESUME_EVIDENCE = "R".repeat(500);
const LONG_SUGGESTION_SOURCE = "S".repeat(500);
const LONG_SUGGESTION_DRAFT = "D".repeat(500);

function longTextAnalysis() {
  const response = JSON.parse(JSON.stringify(deterministicAnalysis));
  response.coverage_summary.keyword_coverage = 50;
  response.coverage_summary.evidenced_count = 1;
  response.coverage_summary.uncertain_count = 1;
  response.requirements[0] = {
    ...response.requirements[0],
    label: LONG_REQUIREMENT_LABEL,
    jd_evidence: LONG_JD_EVIDENCE,
    resume_status: "uncertain",
    resume_evidence: [LONG_RESUME_EVIDENCE],
  };
  response.rewrite_suggestions[0] = {
    ...response.rewrite_suggestions[0],
    source: LONG_SUGGESTION_SOURCE,
    suggested: LONG_SUGGESTION_DRAFT,
  };
  return response;
}

async function fillAnalysisForm(page) {
  await page.getByLabel("岗位 JD").fill(fs.readFileSync(JD_FIXTURE, "utf8"));
  await page.getByLabel("上传简历").setInputFiles(RESUME_FIXTURE);
  await page.getByLabel(/我已阅读并同意/).check();
}

async function submitAnalysis(page) {
  await fillAnalysisForm(page);
  await page.getByRole("button", { name: "分析这份简历" }).click();
}

async function downloadMarkdown(page) {
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出已确认草稿" }).click();
  const download = await downloadPromise;
  const downloadPath = await download.path();
  return {
    filename: download.suggestedFilename(),
    content: await fs.promises.readFile(downloadPath, "utf8"),
  };
}

test("health endpoint returns ok", async ({ request }) => {
  const response = await request.get("/api/health");
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body).toEqual({ status: "ok" });
});

test("public beta states its limits and requires privacy consent", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("公开 Beta")).toBeVisible();
  await expect(page.getByText("不预测录用结果")).toBeVisible();
  const consent = page.locator("#privacy-consent");
  await expect(consent).not.toBeChecked();
  await expect(page.getByRole("button", { name: "分析这份简历" })).toBeDisabled();
  await expect(page.getByRole("link", { name: "隐私说明" })).toHaveAttribute("href", "/privacy.html");
});

test("public navigation hides deferred features", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("多 JD 对比")).toHaveCount(0);
  await expect(page.getByText("学习路线")).toHaveCount(0);
  await expect(page.getByText("模拟面试")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "EN" })).toHaveCount(0);
});

test("public scope exposes only one JD plus one supported resume", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("仅分析 JD")).toHaveCount(0);
  await expect(page.getByText("仅诊断简历")).toHaveCount(0);
  await expect(page.getByText("多 JD 对比")).toHaveCount(0);
  await expect(page.locator('input[type="file"]')).toHaveAttribute("accept", ".pdf,.docx,.txt");
});

test("user reviews evidence, accepts one suggestion, and exports only accepted work", async ({ page }) => {
  await page.addInitScript(() => {
    const realFetch = window.fetch.bind(window);
    const realSetTimeout = window.setTimeout.bind(window);
    const realClearTimeout = window.clearTimeout.bind(window);
    window.__analysisTransport = {
      fetchUrl: "",
      hasAbortSignal: false,
      timeoutDelay: null,
      timeoutId: null,
      timeoutCleared: false,
    };
    window.fetch = (input, init = {}) => {
      window.__analysisTransport.fetchUrl = String(input);
      window.__analysisTransport.hasAbortSignal = init.signal instanceof AbortSignal;
      return realFetch(input, init);
    };
    window.setTimeout = (callback, delay, ...args) => {
      const id = realSetTimeout(callback, delay, ...args);
      if (delay === 22000) {
        window.__analysisTransport.timeoutDelay = delay;
        window.__analysisTransport.timeoutId = id;
      }
      return id;
    };
    window.clearTimeout = (id) => {
      if (id === window.__analysisTransport.timeoutId) {
        window.__analysisTransport.timeoutCleared = true;
      }
      return realClearTimeout(id);
    };
  });

  await page.goto("/");
  const requestPromise = page.waitForRequest((request) =>
    new URL(request.url()).pathname.startsWith("/api/") && request.method() === "POST"
  );
  await submitAnalysis(page);
  const analysisRequest = await requestPromise;

  expect(new URL(analysisRequest.url()).pathname).toBe("/api/v1/analyses");
  await expect(page.getByRole("heading", { name: "JD 要求与简历证据" })).toBeVisible();
  await expect(page.getByText("关键词覆盖", { exact: true })).toBeVisible();
  await expect(page.getByText("匹配度")).toHaveCount(0);
  await expect(page.getByText("竞争力强")).toHaveCount(0);
  await expect(page.getByText("ATS")).toHaveCount(0);
  await expect(page.getByText("面试准备度")).toHaveCount(0);
  await expect(page.getByText("简历可信度")).toHaveCount(0);
  await expect(page.getByText("学习路线")).toHaveCount(0);
  await expect(page.getByText("面试辅导")).toHaveCount(0);

  const transport = await page.evaluate(() => window.__analysisTransport);
  expect(transport.fetchUrl).toBe("/api/v1/analyses");
  expect(transport.hasAbortSignal).toBe(true);
  expect(transport.timeoutDelay).toBe(22000);
  expect(transport.timeoutCleared).toBe(true);

  const firstSuggestion = page.getByTestId("suggestion-card").first();
  await firstSuggestion.getByRole("button", { name: "接受" }).click();
  const download = await downloadMarkdown(page);
  expect(download.filename).toContain("简历优化草稿");
  expect(download.content).toContain("# JD 定制简历草稿");

  await page.getByRole("button", { name: /^查看差距/ }).click();
  await expect(page.getByRole("heading", { name: "查漏补缺", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "生成学习路线 & 面试辅导" })).toHaveCount(0);
  await expect(page.getByText("学习路线")).toHaveCount(0);
  await expect(page.getByText("面试辅导")).toHaveCount(0);
});

test("safe export defaults confirmed source only and gates pending edited facts", async ({ page }) => {
  await page.route("**/api/v1/analyses", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(deterministicAnalysis),
    });
  });
  await page.goto("/");
  await submitAnalysis(page);
  await expect(page.getByRole("heading", { name: "JD 要求与简历证据" })).toBeVisible();

  const confirmedCard = page.getByTestId("suggestion-card").filter({
    hasText: "负责用户访谈并完成 PRD 撰写。",
  });
  const pendingCard = page.getByTestId("suggestion-card").filter({
    hasText: "推动 AI 应用上线。",
  });

  const defaultDownload = await downloadMarkdown(page);
  expect(defaultDownload.content).toContain("负责用户访谈并完成 PRD 撰写。");
  expect(defaultDownload.content).not.toContain("推动 AI 应用上线。");

  await pendingCard.getByRole("button", { name: "接受" }).click();
  const acceptedPendingDownload = await downloadMarkdown(page);
  expect(acceptedPendingDownload.content).not.toContain("推动 AI 应用上线。");

  await pendingCard.getByRole("button", { name: "编辑" }).click();
  await pendingCard.getByLabel("编辑建议内容").fill(
    "推动 AI 应用上线，并由 20 名测试用户完成验证。"
  );
  const unconfirmedEditDownload = await downloadMarkdown(page);
  expect(unconfirmedEditDownload.content).not.toContain("20 名测试用户");

  await pendingCard.getByLabel("已确认补充事实真实").check();
  await confirmedCard.getByRole("button", { name: "不采用" }).click();
  const confirmedEditDownload = await downloadMarkdown(page);
  expect(confirmedEditDownload.content).toContain("推动 AI 应用上线，并由 20 名测试用户完成验证。");
  expect(confirmedEditDownload.content).not.toContain("负责用户访谈并完成 PRD 撰写。");
  expect(confirmedEditDownload.content).toContain(
    "> 本草稿由用户确认的原文与修改组成；请在投递前进行最终人工检查。"
  );
});

test("structured analysis errors show mapped guidance and request ID without legacy fallback", async ({ page }) => {
  const requestedPaths = [];
  await page.route("**/api/**", async (route) => {
    const requestPath = new URL(route.request().url()).pathname;
    requestedPaths.push(requestPath);
    if (requestPath === "/api/v1/analyses") {
      await route.fulfill({
        status: 400,
        contentType: "application/json",
        body: JSON.stringify({
          ok: false,
          error_code: "JD_TOO_SHORT",
          message: "岗位 JD 至少 50 个字符。",
          request_id: "req-e2e-jd-short",
          retryable: false,
          supported_action: "请粘贴完整岗位描述。",
        }),
      });
      return;
    }
    await route.continue();
  });

  await page.goto("/");
  await submitAnalysis(page);

  const errorAlert = page.getByTestId("error-alert");
  await expect(errorAlert).toContainText("岗位 JD 至少需要 50 个字符，请补充完整岗位描述后重试。");
  await expect(errorAlert).toContainText("请求编号：req-e2e-jd-short");
  expect(requestedPaths).toEqual(["/api/v1/analyses"]);
});

test("populated mobile results wrap long API evidence and suggestions without losing content", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/v1/analyses", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(longTextAnalysis()),
    });
  });

  await page.goto("/");
  await submitAnalysis(page);
  await expect(page.getByTestId("analysis-result")).toBeVisible();

  const requirementCard = page.getByTestId("requirement-card").first();
  const suggestionCard = page.getByTestId("suggestion-card").first();
  const jdEvidence = requirementCard.locator(".evidence-block blockquote");
  const resumeEvidence = requirementCard.locator(".evidence-list li");
  const source = suggestionCard.locator(".suggestion-block").first().locator("p");
  const draft = suggestionCard.locator(".suggested-block p");

  await expect(requirementCard.locator(".requirement-head > strong")).toHaveText(LONG_REQUIREMENT_LABEL);
  await expect(jdEvidence).toHaveText(LONG_JD_EVIDENCE);
  await expect(resumeEvidence).toHaveText(LONG_RESUME_EVIDENCE);
  await expect(source).toHaveText(LONG_SUGGESTION_SOURCE);
  await expect(draft).toHaveText(LONG_SUGGESTION_DRAFT);

  const resultMetrics = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    richText: Array.from(document.querySelectorAll(
      ".requirement-head > strong, .evidence-block blockquote, .evidence-list li, " +
      ".suggestion-block p, .suggestion-context dd"
    )).map((element) => ({
      clientWidth: element.clientWidth,
      scrollWidth: element.scrollWidth,
      overflowX: getComputedStyle(element).overflowX,
    })),
  }));
  expect(resultMetrics.scrollWidth).toBeLessThanOrEqual(resultMetrics.clientWidth);
  expect(resultMetrics.richText.length).toBeGreaterThan(0);
  for (const metric of resultMetrics.richText) {
    expect(metric.scrollWidth).toBeLessThanOrEqual(metric.clientWidth);
    expect(metric.overflowX).not.toBe("hidden");
  }
  expect(await source.evaluate((element) => {
    const style = getComputedStyle(element);
    return element.getBoundingClientRect().height > Number.parseFloat(style.lineHeight) * 2;
  })).toBe(true);

  await page.getByRole("button", { name: /^查看差距/ }).click();
  const gapBody = page.locator(".gap-body");
  await expect(gapBody).toContainText(LONG_REQUIREMENT_LABEL);
  await expect(gapBody).toContainText(LONG_JD_EVIDENCE);
  await expect(gapBody).toContainText(LONG_RESUME_EVIDENCE);
  const gapMetrics = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    richText: Array.from(document.querySelectorAll(".gap-body, .gap-body p, .gap-body li"))
      .map((element) => ({
        clientWidth: element.clientWidth,
        scrollWidth: element.scrollWidth,
        overflowX: getComputedStyle(element).overflowX,
      })),
  }));
  expect(gapMetrics.scrollWidth).toBeLessThanOrEqual(gapMetrics.clientWidth);
  for (const metric of gapMetrics.richText) {
    expect(metric.scrollWidth).toBeLessThanOrEqual(metric.clientWidth);
    expect(metric.overflowX).not.toBe("hidden");
  }
});

test("clearing an in-flight analysis aborts and invalidates its delayed response", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.addInitScript(() => {
    const realFetch = window.fetch.bind(window);
    window.__clearRequestLifecycle = { hasSignal: false, signalAborted: false };
    window.fetch = (input, init = {}) => {
      if (String(input) === "/api/v1/analyses") {
        window.__clearRequestLifecycle.hasSignal = init.signal instanceof AbortSignal;
        init.signal?.addEventListener("abort", () => {
          window.__clearRequestLifecycle.signalAborted = true;
        });
      }
      return realFetch(input, init);
    };
  });

  let markDelayedResponseAttempted;
  const delayedResponseAttempted = new Promise((resolve) => {
    markDelayedResponseAttempted = resolve;
  });
  await page.route("**/api/v1/analyses", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 350));
    markDelayedResponseAttempted();
    void route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(deterministicAnalysis),
    }).catch(() => {});
  });

  await page.goto("/");
  await page.evaluate(() => {
    window.__analysisResultEverVisible = false;
    const recordVisibility = () => {
      const result = document.querySelector('[data-testid="analysis-result"]');
      if (result && result.getClientRects().length > 0) {
        window.__analysisResultEverVisible = true;
      }
    };
    new MutationObserver(recordVisibility).observe(document.body, {
      attributes: true,
      childList: true,
      subtree: true,
    });
  });

  await fillAnalysisForm(page);
  const requestStarted = page.waitForRequest("**/api/v1/analyses");
  await page.getByRole("button", { name: "分析这份简历" }).click();
  await requestStarted;
  await expect(page.getByTestId("loading-status")).toHaveText("分析中…");
  await page.getByRole("button", { name: "清空结果" }).click();

  await delayedResponseAttempted;
  await page.waitForTimeout(100);
  const lifecycle = await page.evaluate(() => ({
    hasSignal: window.__clearRequestLifecycle.hasSignal,
    signalAborted: window.__clearRequestLifecycle.signalAborted,
    resultCount: document.querySelectorAll('[data-testid="analysis-result"]').length,
    resultEverVisible: window.__analysisResultEverVisible,
  }));
  expect(lifecycle).toEqual({
    hasSignal: true,
    signalAborted: true,
    resultCount: 0,
    resultEverVisible: false,
  });
  await expect(page.getByTestId("analysis-result")).toHaveCount(0);
  await expect(page.getByTestId("error-alert")).toHaveCount(0);
  await expect(page.getByTestId("loading-status")).toHaveText("分析这份简历");
});

test("390px shell has no page overflow and sidebar starts closed", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const metrics = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    sidebarTransform: getComputedStyle(document.querySelector(".sidebar")).transform
  }));
  expect(metrics.scrollWidth).toBeLessThanOrEqual(metrics.clientWidth);
  expect(metrics.sidebarTransform).not.toBe("none");
});

test("core form is keyboard-addressable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByLabel("岗位 JD")).toBeVisible();
  await expect(page.getByLabel("上传简历")).toBeAttached();
  await expect(page.getByLabel(/我已阅读并同意/)).toBeAttached();
});

test("sidebar focus follows mobile drawer visibility and desktop collapse", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  const sidebar = page.getByTestId("sidebar");
  const sidebarToggle = page.locator(".sidebar-toggle");
  const menu = page.locator(".menu-trigger");
  const homeNavigation = page.getByRole("button", { name: /首页/ });
  const clearResults = page.getByRole("button", { name: "清空结果" });

  await page.keyboard.press("Tab");
  await expect(menu).toBeFocused();
  expect(await menu.evaluate((element) => element.getBoundingClientRect().left)).toBeGreaterThanOrEqual(0);
  expect(await sidebar.evaluate((element) => element.inert)).toBe(true);
  await expect(sidebar).toHaveAttribute("aria-hidden", "true");

  await menu.click();
  expect(await sidebar.evaluate((element) => element.inert)).toBe(false);
  await expect(sidebar).toHaveAttribute("aria-hidden", "false");
  await expect(sidebar).toHaveCSS("transform", "matrix(1, 0, 0, 1, 0, 0)");
  await page.keyboard.press("Shift+Tab");
  await expect(clearResults).toBeFocused();
  expect(await clearResults.evaluate((element) => element.getBoundingClientRect().left)).toBeGreaterThanOrEqual(0);

  await sidebarToggle.click();
  expect(await sidebar.evaluate((element) => element.inert)).toBe(true);
  await expect(sidebar).toHaveAttribute("aria-hidden", "true");
  await expect(menu).toBeFocused();
  expect(await menu.evaluate((element) => element.getBoundingClientRect().left)).toBeGreaterThanOrEqual(0);

  await page.setViewportSize({ width: 1280, height: 720 });
  await expect(sidebar).toHaveAttribute("aria-hidden", "false");
  expect(await sidebar.evaluate((element) => element.inert)).toBe(false);
  await menu.click();
  await page.keyboard.press("Shift+Tab");
  await expect(homeNavigation).toBeFocused();
  expect(await homeNavigation.evaluate((element) => element.getBoundingClientRect().left)).toBeGreaterThanOrEqual(0);
});
