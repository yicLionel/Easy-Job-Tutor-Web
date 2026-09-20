/**
 * Bundle @hmfw/html-to-pdf into a single same-origin browser script.
 *
 * The app has no framework build step (Vue arrives as a global script), so the
 * PDF engine is emitted as one IIFE that exposes `window.HtmlToPdfLib`.
 */
import { build } from "esbuild";
import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const outfile = resolve(root, "vendor/html-to-pdf.browser.js");

await mkdir(dirname(outfile), { recursive: true });

await build({
  entryPoints: [resolve(here, "pdf-entry.js")],
  outfile,
  bundle: true,
  format: "iife",
  globalName: "HtmlToPdfLib",
  platform: "browser",
  target: "es2020",
  legalComments: "none",
  logLevel: "info",
});

console.log(`Wrote ${outfile}`);
