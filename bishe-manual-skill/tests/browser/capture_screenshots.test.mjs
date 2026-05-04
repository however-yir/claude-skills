import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  applyActions,
  main,
  resolveUrl,
  slugify,
  validatePlan,
  waitForEntry,
} from "../../tools/browser/capture_screenshots.mjs";

function createMockPage() {
  const calls = [];

  const makeLocator = (selector) => ({
    first() {
      return {
        async click() {
          calls.push(["click", selector]);
        },
        async fill(value) {
          calls.push(["fill", selector, value]);
        },
        async press(key) {
          calls.push(["press", selector, key]);
        },
      };
    },
  });

  return {
    calls,
    locator(selector) {
      return makeLocator(selector);
    },
    async waitForSelector(selector, options) {
      calls.push(["waitForSelector", selector, options.state, options.timeout]);
    },
    getByText(text) {
      return {
        first() {
          return {
            async waitFor(options) {
              calls.push(["waitForText", text, options.state, options.timeout]);
            },
          };
        },
      };
    },
    async waitForTimeout(timeoutMs) {
      calls.push(["waitForTimeout", timeoutMs]);
    },
  };
}

test("resolveUrl handles absolute, relative and missing base url", () => {
  assert.equal(resolveUrl("http://127.0.0.1:3000", "/dashboard"), "http://127.0.0.1:3000/dashboard");
  assert.equal(resolveUrl("http://127.0.0.1:3000", "https://example.com"), "https://example.com");
  assert.equal(resolveUrl("http://127.0.0.1:3000", ""), "http://127.0.0.1:3000");

  assert.throws(() => resolveUrl("", "/dashboard"), /requires base_url/);
});

test("slugify sanitizes illegal filename characters", () => {
  assert.equal(slugify("系统 首页"), "系统-首页");
  assert.equal(slugify("a/b:c*d?e\"f<g>h|i"), "a-b-c-d-e-f-g-h-i");
  assert.equal(slugify(""), "screenshot");
});

test("applyActions executes actions in order", async () => {
  const page = createMockPage();
  const entry = {
    actions: [
      { type: "click", selector: "#submit" },
      { type: "fill", selector: "#username", value: "alice" },
      { type: "press", selector: "#username", key: "Enter" },
      { type: "wait_for_selector", selector: "#done", state: "visible", timeout_ms: 4321 },
      { type: "wait_for_text", text: "完成", timeout_ms: 2000 },
      { type: "wait_for_timeout", timeout_ms: 500 },
    ],
  };

  await applyActions(page, entry);

  assert.deepEqual(page.calls, [
    ["click", "#submit"],
    ["fill", "#username", "alice"],
    ["press", "#username", "Enter"],
    ["waitForSelector", "#done", "visible", 4321],
    ["waitForText", "完成", "visible", 2000],
    ["waitForTimeout", 500],
  ]);
});

test("applyActions throws for unsupported action type", async () => {
  const page = createMockPage();
  await assert.rejects(
    () => applyActions(page, { actions: [{ type: "unknown_action" }] }),
    /Unsupported action type/,
  );
});

test("waitForEntry applies timeout/text/selector waits", async () => {
  const page = createMockPage();

  await waitForEntry(page, {
    wait_for_timeout_ms: 123,
    wait_for_text: "加载完成",
    wait_for_selector: "#ready",
    timeout_ms: 3210,
  });

  assert.deepEqual(page.calls, [
    ["waitForTimeout", 123],
    ["waitForText", "加载完成", "visible", 3210],
    ["waitForSelector", "#ready", "visible", 3210],
  ]);
});

test("main returns 1 when plan path is missing", async () => {
  const exitCode = await main([]);
  assert.equal(exitCode, 1);
});

test("main rejects invalid plan schema before browser launch", async () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "capture-plan-"));
  const planPath = path.join(tmpDir, "invalid-plan.json");
  fs.writeFileSync(planPath, JSON.stringify({ base_url: "http://127.0.0.1:3000" }), "utf8");

  await assert.rejects(
    () => main([planPath]),
    /entries/,
  );
});

test("validatePlan rejects missing entries field", () => {
  assert.throws(
    () => validatePlan({ base_url: "http://127.0.0.1:3000" }),
    /entries/,
  );
});

test("validatePlan rejects duplicate filenames", () => {
  assert.throws(
    () =>
      validatePlan({
        entries: [
          { label: "A", filename: "same.png", actions: [] },
          { label: "B", filename: "same.png", actions: [] },
        ],
      }),
    /Duplicate entry filename/,
  );
});

test("waitForEntry propagates selector wait errors", async () => {
  const page = createMockPage();
  page.waitForSelector = async () => {
    throw new Error("selector timeout");
  };

  await assert.rejects(
    () =>
      waitForEntry(page, {
        wait_for_selector: "#missing",
      }),
    /selector timeout/,
  );
});
