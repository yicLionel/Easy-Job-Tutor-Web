/**
 * End-to-end check of the resume PDF feature against the running app.
 *
 * Drives the real UI: analyze a Chinese resume, open the "简历 PDF" page, fill
 * the form, click the one-click export, capture the downloaded file. The Python
 * checker then validates page count, selectable text, and no missing glyphs.
 */
import { writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const baseUrl = process.env.BASE_URL || "http://127.0.0.1:8124";
const outFile = resolve(root, "build/artifacts/app-export.pdf");
const resumeFixture = resolve(root, "build/fixtures/app-resume.txt");

const CHROMIUM_CANDIDATES = [
  process.env.PDF_CHROMIUM_PATH,
  "/Users/yanyichen/Library/Mobile Documents/com~apple~CloudDocs/Documents/Easy-Job-Tutor-skills/Easy-Job-Tutor/.pw-browsers/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
].filter(Boolean);

const JD = "我们招聘 AI Agent 开发实习生。必须熟悉 Python 与 RAG，负责搭建检索增强问答服务、设计后端接口并部署上线；有 FastAPI 项目经验者优先。";
const RESUME = `陈小明
chen@example.com | 138-0000-0000 | 上海

教育背景
某某大学 计算机科学与技术 本科 2022 - 2026

项目经历
使用 Python 与 FastAPI 开发规则分析服务，负责需求分析与接口设计，并部署上线。
搭建检索增强问答流程，邀请 20 名同学试用并收集反馈。

技能
Python、FastAPI、RAG、Git`;

async function main() {
  const browserPath = CHROMIUM_CANDIDATES.find((candidate) => existsSync(candidate));
  const browser = await chromium.launch({ executablePath: browserPath });

  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.on("pageerror", (error) => console.error(`[browser:error] ${error.message}`));
    page.on("console", (message) => {
      if (message.type() === "error") console.log(`[browser:console] ${message.text()}`);
    });

    await page.goto(baseUrl, { waitUntil: "networkidle" });

    await page.locator("textarea").first().fill(JD);
    await page.locator('input[type="file"]').setInputFiles(resumeFixture);
    await page.locator(".actions button.primary").first().click();

    await page.locator(".sidebar-nav-item").filter({ hasText: "简历 PDF" }).waitFor({ timeout: 30000 });
    await page.locator(".sidebar-nav-item").filter({ hasText: "简历 PDF" }).click();

    await page.locator(".resume-sheet").waitFor({ timeout: 15000 });

    await page.getByLabel("姓名", { exact: true }).fill("陈小明");
    await page.getByLabel("邮箱", { exact: true }).fill("chen@example.com");
    await page.getByLabel("电话", { exact: true }).fill("138-0000-0000");
    await page.getByLabel("城市", { exact: true }).fill("上海");
    await page.getByLabel("个人简介", { exact: true }).fill("计算机科学专业应届生，专注检索增强生成与后端服务开发，具备从需求分析到部署上线的项目经验。");
    await page.getByLabel("学校", { exact: true }).fill("某某大学");
    await page.getByLabel("学位 / 专业", { exact: true }).fill("计算机科学与技术 本科");

    await page.locator(".resume-sheet").waitFor();
    await page.waitForTimeout(300);

    const [download] = await Promise.all([
      page.waitForEvent("download", { timeout: 30000 }),
      page.locator(".pdf-actions-bottom button.primary").click(),
    ]);

    await mkdir(dirname(outFile), { recursive: true });
    await download.saveAs(outFile);
    console.log(`OK downloaded ${outFile}`);
    console.log(`suggested filename: ${download.suggestedFilename()}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
