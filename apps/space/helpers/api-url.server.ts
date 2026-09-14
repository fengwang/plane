import { env } from "node:process";

// Keep support for deployments that embed a separate API origin in the build.
const buildTimeApiBaseUrl = process.env.VITE_API_BASE_URL;

// Import Node's runtime environment explicitly: Vite replaces process.env with
// build-time public variables, which are empty for same-origin browser builds.
export function getServerApiUrl(path: string, requestUrl: string): string {
  const baseUrl = env.API_BASE_URL || env.VITE_API_BASE_URL || buildTimeApiBaseUrl || new URL(requestUrl).origin;
  return new URL(path, baseUrl).toString();
}
