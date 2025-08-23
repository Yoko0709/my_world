import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import expressiveCode from "astro-expressive-code";

// 如果你要用 @astrojs/vercel，需要先安装：
// pnpm add -D @astrojs/vercel
import vercel from "@astrojs/vercel";

export default defineConfig({
  site: "https://your-domain.com", // 改成你自己的域名（可选）
  prefetch: true,
  integrations: [
    react(),
    expressiveCode({
      styleOverrides: {
        codeFontFamily:
          "'MonoLisa', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
      },
    }),
    mdx(),
    sitemap(),
  ],
  trailingSlash: "never",
  adapter: vercel(), // ✅ 用 Vercel adapter
});

