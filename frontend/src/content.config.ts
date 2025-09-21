// src/content.config.ts
import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

/* ---------- 共用子 schema ---------- */
const linkItem = z.object({
  href: z.string().url().or(z.string().startsWith("mailto:")),
  label: z.string(),
  icon: z
    .enum(["github", "researchgate", "mail", "outlook", "linkedin", "instagram", "scholar"])
    .optional(),
  ariaLabel: z.string().optional(),
});

const skillItem = z.object({
  name: z.string(),
  tip: z.string().optional(),
});

/* ---------- pages (md/mdx) ---------- */
const pages = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "./src/content/pages" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      description: z.string(),
      datePublished: z.date(),
      dateModified: z.date().optional(),
      img: image().array().optional(),
      imgAlt: z.string().optional(),
      ogImage: image().optional(),
    }),
});

/* ---------- work (md/mdx) ---------- */
const work = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "./src/content/work" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      timeline: z.object({ start: z.string(), end: z.string() }),
      img: z.object({ src: image(), alt: z.string() }).array().optional(),
      video: z.object({ src: z.string(), poster: z.string() }).array().optional(),
      ogImage: image().optional(),
    }),
});

/* ---------- papers (yml) ---------- */
/* 若使用 yml/yaml，请在 astro.config.mjs 启用 @astrojs/yaml：
   import yaml from "@astrojs/yaml";
   export default defineConfig({ integrations: [yaml()] })
*/
const papers = defineCollection({
  loader: glob({ pattern: "**/[^_]*.y{a,}ml", base: "./src/content/papers" }),
  schema: () =>
    z.object({
      title: z.string(),
      datePublished: z.date(),
      description: z.string().optional(),
      url: z.string(),
      features: z.object({ name: z.string(), url: z.string().url() }).array().optional(),
    }),
});

/* ---------- projects (yml) ---------- */
const projects = defineCollection({
  loader: glob({ pattern: "**/[^_]*.y{a,}ml", base: "./src/content/projects" }),
  schema: () =>
    z.object({
      title: z.string(),
      datePublished: z.date(),
      description: z.string().optional(),
      url: z.string(),
      features: z.object({ name: z.string(), url: z.string().url() }).array().optional(),
    }),
});

/* ---------- now (md/mdx) ---------- */
const now = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "./src/content/now" }),
  schema: () =>
    z.object({
      title: z.string().optional(),
      locale: z.enum(["en", "zh"]).optional(),
      draft: z.boolean().default(false).optional(),
      date: z.date().optional(),
    }),
});

/* ---------- now_* (yml) ---------- */
const now_books = defineCollection({
  loader: glob({ pattern: "**/[^_]*.y{a,}ml", base: "./src/content/now/books" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      cover: z.union([image(), z.string()]),
      meta: z.string().optional(),
      note: z.string().optional(),
      href: z.string().url().optional(),
      locale: z.enum(["en", "zh"]).default("en"),
      draft: z.boolean().default(false),
    }),
});

const now_movies = defineCollection({
  loader: glob({ pattern: "**/[^_]*.y{a,}ml", base: "./src/content/now/movies" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      cover: z.union([image(), z.string()]),
      meta: z.string().optional(),
      note: z.string().optional(),
      href: z.string().url().optional(),
      locale: z.enum(["en", "zh"]).default("en"),
      draft: z.boolean().default(false),
    }),
});

const now_music = defineCollection({
  loader: glob({ pattern: "**/[^_]*.y{a,}ml", base: "./src/content/now/music" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      cover: z.union([image(), z.string()]),
      meta: z.string().optional(),
      note: z.string().optional(),
      href: z.string().url().optional(),
      locale: z.enum(["en", "zh"]).default("en"),
      draft: z.boolean().default(false),
    }),
});

const now_feed = defineCollection({
  loader: glob({ pattern: "**/[^_]*.y{a,}ml", base: "./src/content/now/feed" }),
  schema: () =>
    z.object({
      date: z.date(),
      icon: z.string().min(1),
      text: z.string().min(1),
      href: z.string().url().optional(),
      locale: z.enum(["en", "zh"]).default("en"),
      draft: z.boolean().default(false),
    }),
});

/* ---------- about (md/mdx) ---------- */
const about = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "./src/content/about" }),
  schema: ({ image }) =>
    z.object({
      locale: z.enum(["en", "zh"]).default("en"),
      draft: z.boolean().default(false),

      title: z.string().default("ABOUT ME"),
      description: z.string().default("Who I am, what I do, and where to find me."),
      intro: z.string().optional(),

      avatar: z.union([image(), z.string()]).optional(),
      avatarAlt: z.string().optional(),

      // 关键：技能分组 -> 每组是 {name, tip?}[]
      skills: z.record(z.array(skillItem)).optional(),

      experience: z
        .array(
          z.object({
            when: z.string(),
            where: z.string(),
            role: z.string().optional(),
            what: z.string().optional(),
          }),
        )
        .optional(),

      links: z.array(linkItem).optional(),

      updated: z.string().optional(),
    }),
});

/* ---------- 统一导出（只导出一次） ---------- */
export const collections = {
  pages,
  work,
  papers,
  projects,
  now,
  now_books,
  now_movies,
  now_music,
  now_feed,
  about,
};
