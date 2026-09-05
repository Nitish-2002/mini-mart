import { defineConfig, devices } from "@playwright/test";
import { readFileSync } from "fs";
import path from "path";

// Loads backend/.env.e2e's KEY=VALUE lines into a plain object — the
// backend webServer entry below needs them as real process env vars, the
// same file tests/conftest.py's pytest suite loads for its own DB.
function loadEnvFile(filePath: string): Record<string, string> {
  const env: Record<string, string> = {};
  for (const line of readFileSync(filePath, "utf-8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf("=");
    env[trimmed.slice(0, idx)] = trimmed.slice(idx + 1);
  }
  return env;
}

const backendEnv = loadEnvFile(path.resolve(__dirname, "../backend/.env.e2e"));
const FRONTEND_PORT = 3100;
const BACKEND_PORT = 8000;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1, // the singleton Admin account is shared, global state — no parallel journeys
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: `http://localhost:${FRONTEND_PORT}`,
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `uv run uvicorn app.main:app --port ${BACKEND_PORT}`,
      cwd: path.resolve(__dirname, "../backend"),
      env: backendEnv,
      port: BACKEND_PORT,
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: `npm run dev -- --port ${FRONTEND_PORT}`,
      cwd: __dirname,
      env: { NEXT_PUBLIC_API_BASE_URL: `http://localhost:${BACKEND_PORT}` },
      port: FRONTEND_PORT,
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
