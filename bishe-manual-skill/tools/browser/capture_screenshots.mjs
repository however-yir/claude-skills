import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

export function resolveUrl(baseUrl, entryUrl) {
  if (!entryUrl) {
    return baseUrl;
  }
  if (/^https?:\/\//i.test(entryUrl)) {
    return entryUrl;
  }
  if (!baseUrl) {
    throw new Error(`Entry url "${entryUrl}" requires base_url in the plan.`);
  }
  return new URL(entryUrl, baseUrl).toString();
}

export function slugify(label) {
  const normalized = label.replace(/[\\/:*?"<>|]/g, "-").replace(/\s+/g, "-").trim();
  return normalized || "screenshot";
}

export function validatePlan(plan) {
  if (!plan || typeof plan !== "object" || Array.isArray(plan)) {
    throw new Error("Plan must be a JSON object.");
  }

  if (!Array.isArray(plan.entries)) {
    throw new Error("Plan field `entries` must be an array.");
  }

  if (plan.schema_version !== undefined) {
    if (!Number.isInteger(plan.schema_version) || plan.schema_version < 1) {
      throw new Error("Plan field `schema_version` must be a positive integer.");
    }
  }

  const seenFilenames = new Set();
  for (const [index, entry] of plan.entries.entries()) {
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
      throw new Error(`Plan entry at index ${index} must be an object.`);
    }
    if (typeof entry.label !== "string" || entry.label.trim() === "") {
      throw new Error(`Plan entry at index ${index} requires non-empty string field \`label\`.`);
    }
    if (entry.url !== undefined && typeof entry.url !== "string") {
      throw new Error(`Plan entry at index ${index} field \`url\` must be a string.`);
    }
    if (entry.filename !== undefined) {
      if (typeof entry.filename !== "string" || entry.filename.trim() === "") {
        throw new Error(`Plan entry at index ${index} field \`filename\` must be a non-empty string.`);
      }
      if (seenFilenames.has(entry.filename)) {
        throw new Error(`Duplicate entry filename detected: ${entry.filename}`);
      }
      seenFilenames.add(entry.filename);
    }
    if (entry.actions !== undefined && !Array.isArray(entry.actions)) {
      throw new Error(`Plan entry at index ${index} field \`actions\` must be an array.`);
    }
  }

  return plan;
}

export async function waitForEntry(page, entry) {
  if (entry.wait_for_timeout_ms) {
    await page.waitForTimeout(entry.wait_for_timeout_ms);
  }
  if (entry.wait_for_text) {
    await page.getByText(entry.wait_for_text, { exact: false }).first().waitFor({ state: "visible", timeout: entry.timeout_ms ?? 15000 });
  }
  if (entry.wait_for_selector) {
    await page.waitForSelector(entry.wait_for_selector, { state: "visible", timeout: entry.timeout_ms ?? 15000 });
  }
}

export async function applyActions(page, entry) {
  for (const action of entry.actions ?? []) {
    switch (action.type) {
      case "click":
        await page.locator(action.selector).first().click();
        break;
      case "fill":
        await page.locator(action.selector).first().fill(action.value ?? "");
        break;
      case "press":
        await page.locator(action.selector).first().press(action.key);
        break;
      case "wait_for_selector":
        await page.waitForSelector(action.selector, { state: action.state ?? "visible", timeout: action.timeout_ms ?? 15000 });
        break;
      case "wait_for_text":
        await page.getByText(action.text, { exact: false }).first().waitFor({ state: "visible", timeout: action.timeout_ms ?? 15000 });
        break;
      case "wait_for_timeout":
        await page.waitForTimeout(action.timeout_ms ?? 1000);
        break;
      default:
        throw new Error(`Unsupported action type: ${action.type}`);
    }
  }
}

export async function runPlan(plan, absolutePlanPath) {
  validatePlan(plan);
  const outputDir = path.resolve(path.dirname(absolutePlanPath), plan.output_dir ?? "output/doc");
  fs.mkdirSync(outputDir, { recursive: true });

  const browser = plan.cdp_url
    ? await chromium.connectOverCDP(plan.cdp_url)
    : await chromium.launch({ headless: plan.headless !== false });

  const context = plan.cdp_url
    ? browser.contexts()[0]
    : await browser.newContext({
        viewport: plan.viewport ?? { width: 1440, height: 900 },
        ignoreHTTPSErrors: true,
      });

  const page = context.pages()[0] ?? (await context.newPage());
  const imageMap = {};

  try {
    for (const entry of plan.entries ?? []) {
      const targetUrl = resolveUrl(plan.base_url, entry.url);
      await page.goto(targetUrl, { waitUntil: entry.wait_until ?? "networkidle", timeout: entry.timeout_ms ?? 30000 });
      await applyActions(page, entry);
      await waitForEntry(page, entry);

      const filename = entry.filename ?? `${slugify(entry.label)}.png`;
      const outputPath = path.resolve(outputDir, filename);
      const locator = entry.clip_selector ? page.locator(entry.clip_selector).first() : null;

      if (locator) {
        await locator.screenshot({ path: outputPath, type: "png" });
      } else {
        await page.screenshot({ path: outputPath, fullPage: entry.full_page !== false, type: "png" });
      }

      imageMap[entry.label] = outputPath;
      console.log(`CAPTURED\t${entry.label}\t${outputPath}`);
    }
  } finally {
    const imageMapPath = path.resolve(path.dirname(absolutePlanPath), plan.image_map_output ?? "image-map.json");
    fs.writeFileSync(imageMapPath, JSON.stringify(imageMap, null, 2), "utf8");
    console.log(`IMAGE_MAP\t${imageMapPath}`);

    if (plan.cdp_url) {
      await browser.close();
    } else {
      await context.close();
      await browser.close();
    }
  }
}

export async function main(argv = process.argv.slice(2)) {
  const planPath = argv[0];
  if (!planPath) {
    console.error("Usage: node tools/browser/capture_screenshots.mjs <plan.json>");
    return 1;
  }

  const absolutePlanPath = path.resolve(planPath);
  const plan = validatePlan(JSON.parse(fs.readFileSync(absolutePlanPath, "utf8")));
  await runPlan(plan, absolutePlanPath);
  return 0;
}

function isDirectRun() {
  if (!process.argv[1]) {
    return false;
  }
  return path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
}

if (isDirectRun()) {
  main()
    .then((code) => {
      process.exit(code);
    })
    .catch((error) => {
      console.error(error.stack || String(error));
      process.exit(1);
    });
}
