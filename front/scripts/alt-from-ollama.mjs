#!/usr/bin/env node
/**
 * alt-from-ollama.mjs
 *
 * Generate descriptive `alt` text for an image using a local Ollama vision model.
 *
 *   Default model:        gemma4:e2b
 *   Apple Silicon default: gemma4:e2b-mlx
 *   Override:              OLLAMA_MODEL=<tag>
 *   Custom server:         OLLAMA_URL=http://host:port  (default http://localhost:11434)
 *
 * Usage:
 *   node alt-from-ollama.mjs path/to/image.jpg
 *   node alt-from-ollama.mjs path/to/image.jpg "context hint"
 *   node alt-from-ollama.mjs https://example.com/photo.jpg
 *
 * Output:
 *   One line of alt text on stdout, 125 characters max.
 *   The literal token `EMPTY` (no quotes) signals a purely decorative image;
 *   callers emit `alt="" role="presentation" aria-hidden="true"`.
 *
 * Requires Node 18+ (built-in `fetch`). No npm install needed.
 */

import { readFile } from "node:fs/promises";
import { arch, platform } from "node:os";
import { argv, exit, stderr, stdout } from "node:process";

const OLLAMA_URL  = process.env.OLLAMA_URL  ?? "http://localhost:11434";
const DEFAULT_BASE = process.env.OLLAMA_MODEL_BASE ?? "gemma4:e2b";

function pickDefaultModel() {
  if (process.env.OLLAMA_MODEL) return process.env.OLLAMA_MODEL;
  const isAppleSilicon = platform() === "darwin" && arch() === "arm64";
  return isAppleSilicon ? `${DEFAULT_BASE}-mlx` : DEFAULT_BASE;
}
const MODEL = pickDefaultModel();

const PROMPT =
  "Write alt text for this image, 125 characters or fewer. " +
  "Describe meaning, not pixels. " +
  "Do NOT start with 'image of', 'picture of', or 'photo of'. " +
  "Avoid guessing race, gender, age, or mood. " +
  "If the image is purely decorative (texture, ornament, divider), reply with the single literal word EMPTY. " +
  "If the image is mostly text, include the readable text verbatim. " +
  "Reply with the alt text only, no quotes, no prefix.";

async function loadImageBase64(src) {
  if (/^https?:\/\//i.test(src)) {
    const res = await fetch(src);
    if (!res.ok) throw new Error(`Fetch ${src}: HTTP ${res.status}`);
    const buf = Buffer.from(await res.arrayBuffer());
    return buf.toString("base64");
  }
  const buf = await readFile(src);
  return buf.toString("base64");
}

export async function describe(src, context = "") {
  const image = await loadImageBase64(src);
  const prompt = context ? `${PROMPT} Context: ${context}` : PROMPT;

  let body;
  try {
    const res = await fetch(`${OLLAMA_URL}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL,
        prompt,
        images: [image],
        stream: false,
        options: { temperature: 0.2, num_predict: 80 },
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} from ${OLLAMA_URL}`);
    body = await res.json();
  } catch (err) {
    stderr.write(
      `Could not reach Ollama at ${OLLAMA_URL}: ${err.message}\n` +
      "Is it running? Try `ollama serve` in another terminal,\n" +
      "or run `bash front/scripts/install-alt-ai.sh` (macOS / Linux)\n" +
      "        / `powershell -File front/scripts/install-alt-ai.ps1` (Windows).\n"
    );
    exit(2);
  }

  let text = (body.response ?? "").trim();
  // Strip surrounding quotes if the model added them.
  if (text.length >= 2 && text[0] === text.at(-1) && (text[0] === '"' || text[0] === "'")) {
    text = text.slice(1, -1).trim();
  }
  // Hard cap at 125 chars, cut at a word boundary.
  if (text.length > 125) {
    const cut = text.slice(0, 125).split(" ").slice(0, -1).join(" ");
    text = cut.replace(/[,.;:]+$/, "") + "…";
  }
  return text;
}

async function main() {
  if (argv.length < 3) {
    stderr.write(
      "Usage: node alt-from-ollama.mjs <image-path-or-url> [context]\n"
    );
    exit(1);
  }
  const src = argv[2];
  const ctx = argv[3] ?? "";
  const text = await describe(src, ctx);
  stdout.write(text + "\n");
}

// Run only if invoked directly.
const invoked = import.meta.url === `file://${argv[1]}` ||
                import.meta.url.endsWith(argv[1]);
if (invoked) {
  main().catch((err) => {
    stderr.write(`${err.message}\n`);
    exit(1);
  });
}
