import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  if (command === "build" && mode === "production") {
    const apiUrl = env.VITE_API_BASE_URL?.trim();
    if (!apiUrl) {
      throw new Error("Set VITE_API_BASE_URL to your deployed backend URL ending in /api before building.");
    }
    const parsed = new URL(apiUrl);
    if (!["http:", "https:"].includes(parsed.protocol) || parsed.search || parsed.hash ||
        !parsed.pathname.replace(/\/+$/, "").endsWith("/api")) {
      throw new Error("VITE_API_BASE_URL must be an HTTP(S) backend URL ending in /api.");
    }
    if (process.env.VERCEL && (parsed.protocol !== "https:" ||
        ["localhost", "127.0.0.1", "[::1]"].includes(parsed.hostname))) {
      throw new Error("Vercel requires a public HTTPS VITE_API_BASE_URL, not localhost.");
    }
  }
  return {
    plugins: [react()],
    test: {
      environment: "jsdom",
      setupFiles: "./src/test/setup.ts",
      globals: true
    }
  };
});
