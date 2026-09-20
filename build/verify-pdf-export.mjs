/**
 * Verify the browser PDF export end to end.
 *
 * Serves the repo, opens the smoke fixture in Chromium, generates a PDF with the
 * bundled @hmfw/html-to-pdf, writes it to disk, and reports facts the Python
 * checker then validates (selectable text, page count, size).
 */
import { createServer } from "node:http";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const outFile = resolve(root, "build/artifacts/pdf-smoke.pdf");

const CHROMIUM_CANDIDATES = [
  process.env.PDF_CHROMIUM_PATH,
  "/Users/yanyichen/Library/Mobile Documents/com~apple~CloudDocs/Documents/Easy-Job-Tutor-skills/Easy-Job-Tutor/.pw-browsers/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
].filter(Boolean);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".woff": "font/woff",
  ".css": "text/css; charset=utf-8",
};

function startServer() {
  const server = createServer(async (req, res) => {
    try {
      const url = new URL(req.url, "http://127.0.0.1");
      let path = join(root, decodeURIComponent(url.pathname));
      if (!path.startsWith(root) || !existsSync(path)) {
        res.writeHead(404).end("not found");
        return;
      }
      const body = await readFile(path);
      res.writeHead(200, { "content-type": MIME[extname(path)] || "application/octet-stream" });
      res.end(body);
    } catch (error) {
      res.writeHead(500).end(String(error));
    }
  });
  return new Promise((done) => server.listen(0, "127.0.0.1", () => done(server)));
}

async function main() {
  const browserPath = CHROMIUM_CANDIDATES.find((candidate) => existsSync(candidate));
  const server = await startServer();
  const port = server.address().port;
  const browser = await chromium.launch({ executablePath: browserPath });

  try {
    const page = await browser.newPage({ viewport: { width: 900, height: 1400 } });
    page.on("console", (message) => console.log(`[browser:${message.type()}] ${message.text()}`));
    page.on("pageerror", (error) => console.error(`[browser:error] ${error.message}`));

    await page.goto(`http://127.0.0.1:${port}/build/fixtures/pdf-smoke.html`, { waitUntil: "networkidle" });

    const result = await page.evaluate(async () => {
      const element = document.getElementById("resume");
      const output = await HtmlToPdfLib.htmlToPdf(element, { filename: "resume-smoke", pageSize: "A4" });
      if (!output.success || !output.blob) {
        return { success: false, error: output.error || "no blob returned" };
      }
      const bytes = new Uint8Array(await output.blob.arrayBuffer());
      let binary = "";
      for (let index = 0; index < bytes.length; index += 1) binary += String.fromCharCode(bytes[index]);
      return { success: true, base64: btoa(binary), size: bytes.length };
    });

    if (!result.success) throw new Error(result.error);

    await mkdir(dirname(outFile), { recursive: true });
    await writeFile(outFile, Buffer.from(result.base64, "base64"));
    console.log(`OK wrote ${outFile} (${result.size} bytes)`);
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
