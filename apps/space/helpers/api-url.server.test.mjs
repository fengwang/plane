import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { getServerApiUrl } from "./api-url.server.ts";

const originalApi = process.env.API_BASE_URL;
const originalViteApi = process.env.VITE_API_BASE_URL;

afterEach(() => {
  for (const [key, value] of [
    ["API_BASE_URL", originalApi],
    ["VITE_API_BASE_URL", originalViteApi],
  ]) {
    if (value === undefined) delete process.env[key];
    else process.env[key] = value;
  }
});

test("server requests use the runtime internal API address", () => {
  process.env.API_BASE_URL = "http://api:8000";
  process.env.VITE_API_BASE_URL = "http://browser.example:17239";
  assert.equal(
    getServerApiUrl("/api/public/anchor/test/meta/", "http://lan:17239/spaces/issues/test"),
    "http://api:8000/api/public/anchor/test/meta/"
  );
});

test("existing development API configuration remains supported", () => {
  delete process.env.API_BASE_URL;
  process.env.VITE_API_BASE_URL = "http://localhost:8000";
  assert.equal(getServerApiUrl("/api/test/", "http://localhost:3002/spaces/"), "http://localhost:8000/api/test/");
});

test("same-origin fallback is an absolute URL", () => {
  delete process.env.API_BASE_URL;
  delete process.env.VITE_API_BASE_URL;
  assert.equal(getServerApiUrl("/api/test/", "http://lan:17239/spaces/issues/test"), "http://lan:17239/api/test/");
});

test("an API origin captured at build time survives an empty runtime environment", async () => {
  delete process.env.API_BASE_URL;
  process.env.VITE_API_BASE_URL = "https://api.example.test";
  const compiled = await import("./api-url.server.ts?build-time-origin");
  delete process.env.VITE_API_BASE_URL;
  assert.equal(
    compiled.getServerApiUrl("/api/test/", "https://spaces.example.test/issues/test"),
    "https://api.example.test/api/test/"
  );
});
