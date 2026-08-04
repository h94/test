import { createReadStream, statSync } from "node:fs";
import { join } from "node:path";
import { lookup } from "mrmime";
import { createError, getRouterParam, sendStream, setResponseHeader } from "h3";

const IMG_DIR = process.env.NUXT_IMG_DIR || "/app/img";
const CACHE_MAX_AGE = 60 * 60 * 24 * 7;

export default defineEventHandler((event) => {
  const path = getRouterParam(event, "path");
  if (!path || path.includes("..")) {
    throw createError({ statusCode: 400, statusMessage: "Bad Request" });
  }

  const filePath = join(IMG_DIR, path);
  let stat;
  try {
    stat = statSync(filePath);
  } catch {
    throw createError({ statusCode: 404, statusMessage: "Not Found" });
  }
  if (!stat.isFile()) {
    throw createError({ statusCode: 404, statusMessage: "Not Found" });
  }

  const contentType = lookup(filePath);
  if (contentType) {
    setResponseHeader(event, "Content-Type", contentType);
  }
  setResponseHeader(
    event,
    "Cache-Control",
    `public, max-age=${CACHE_MAX_AGE}`,
  );

  return sendStream(event, createReadStream(filePath));
});
