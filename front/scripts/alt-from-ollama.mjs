#!/usr/bin/env node
/**
 * alt-from-ollama.mjs
 *
 * Generate descriptive `alt` text for an image using a local Ollama vision model.
 *
 *   Default model:            gemma4:e2b
 *   MLX-capable hardware:     gemma4:e2b-mlx  (selected automatically)
 *   Override:                 OLLAMA_MODEL=<tag>
 *   Custom server:            OLLAMA_URL=http://host:port  (default http://localhost:11434)
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
  const isMlxCapable = platform() === "darwin" && arch() === "arm64";
  return isMlxCapable ? `${DEFAULT_BASE}-mlx` : DEFAULT_BASE;
}
const MODEL = pickDefaultModel();

// BCP-47 language tag → display name + native-language instruction fragment.
// Pass `--lang fr` / `--lang en` / `--lang es` / …, or set ALT_LANG.
// Default: detect from LANG / LC_ALL, fall back to English.
const LANG_INSTRUCTIONS = {
  en: { name: "English",   line: "Write the alt text in English." },
  fr: { name: "French",    line: "Rédige le texte alternatif en français." },
  es: { name: "Spanish",   line: "Escribe el texto alternativo en español." },
  de: { name: "German",    line: "Schreibe den Alt-Text auf Deutsch." },
  it: { name: "Italian",   line: "Scrivi il testo alternativo in italiano." },
  pt: { name: "Portuguese",line: "Escreva o texto alternativo em português." },
  nl: { name: "Dutch",     line: "Schrijf de alternatieve tekst in het Nederlands." },
  ar: { name: "Arabic",    line: "اكتب النص البديل باللغة العربية." },
  ja: { name: "Japanese",  line: "代替テキストを日本語で書いてください。" },
  zh: { name: "Chinese",   line: "用中文写替代文本。" },
};

function detectLang() {
  if (process.env.ALT_LANG) return process.env.ALT_LANG.toLowerCase().slice(0, 2);
  const sys = (process.env.LC_ALL || process.env.LANG || "en").toLowerCase();
  return sys.slice(0, 2);
}

function promptFor(lang) {
  const i18n = LANG_INSTRUCTIONS[lang] ?? LANG_INSTRUCTIONS.en;
  return (
    `${i18n.line} ` +
    "Write alt text for this image, 125 characters or fewer. " +
    "Describe meaning, not pixels. " +
    "Do NOT start with 'image of', 'picture of', or 'photo of' (or the equivalent in your language). " +
    "Avoid guessing race, gender, age, or mood. " +
    "If the image is purely decorative (texture, ornament, divider), reply with the single literal word EMPTY. " +
    "If the image is mostly text, include the readable text verbatim. " +
    "Reply with the alt text only, no quotes, no prefix."
  );
}

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

export async function describe(src, context = "", lang = detectLang()) {
  const image = await loadImageBase64(src);
  const base = promptFor(lang);
  const prompt = context ? `${base} Context: ${context}` : base;

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
      "or run the installer for your shell:\n" +
      "  bash front/scripts/install-alt-ai.sh   (Bash)\n" +
      "  powershell -File front/scripts/install-alt-ai.ps1   (PowerShell)\n"
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

function parseArgs(args) {
  const out = { src: null, ctx: "", lang: null };
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--lang" || a === "-l") {
      out.lang = (args[++i] ?? "").toLowerCase().slice(0, 2) || null;
    } else if (a.startsWith("--lang=")) {
      out.lang = a.slice(7).toLowerCase().slice(0, 2) || null;
    } else {
      positional.push(a);
    }
  }
  out.src = positional[0] ?? null;
  out.ctx = positional[1] ?? "";
  return out;
}

async function main() {
  const { src, ctx, lang } = parseArgs(argv.slice(2));
  if (!src) {
    stderr.write(
      "Usage: node alt-from-ollama.mjs [--lang <bcp47>] <image-path-or-url> [context]\n" +
      "  --lang en|fr|es|de|it|pt|nl|ar|ja|zh   (defaults to ALT_LANG or LANG)\n"
    );
    exit(1);
  }
  const text = await describe(src, ctx, lang ?? detectLang());
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
