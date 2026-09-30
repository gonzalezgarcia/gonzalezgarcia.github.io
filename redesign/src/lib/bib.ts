import fs from "node:fs";
import path from "node:path";
import { load as loadYaml } from "js-yaml";

const REPO_ROOT = path.resolve(process.cwd(), "..");

export interface Paper {
  key: string;
  type: string;
  title: string;
  authors: { first: string; last: string; isSelf: boolean }[];
  venue: string;
  year: string;
  abstract?: string;
  topics: string[];
  award?: string;
  awardName?: string;
  pdf?: string;
  code?: string;
  website?: string;
  doi?: string;
  html?: string;
  isFlare: boolean;
  bibtex: string;
}

const SELF_LAST = "González-García";
const SELF_FIRST = "Carlos";

function stripAccentCommands(s: string): string {
  // Very small subset of LaTeX accent commands used in this bib file.
  return s
    .replace(/\{\\'([a-zA-Z])\}/g, "$1́")
    .replace(/\\'([a-zA-Z])/g, "$1́")
    .replace(/\{\\"([a-zA-Z])\}/g, "$1̈")
    .replace(/\\"([a-zA-Z])/g, "$1̈")
    .replace(/\\textquotedblleft/g, "“")
    .replace(/\\textquotedblright/g, "”")
    .replace(/\\textemdash/g, "—")
    .normalize("NFC")
    .replace(/[{}]/g, "")
    .trim();
}

function parseAuthors(raw: string): Paper["authors"] {
  if (!raw.trim()) return [];
  return raw.split(/\s+and\s+/).map((entry) => {
    const clean = stripAccentCommands(entry).replace(/[*∗†‡§¶‖&^]/g, "");
    const parts = clean.split(",");
    let first: string;
    let last: string;
    if (parts.length === 2) {
      last = parts[0].trim();
      first = parts[1].trim();
    } else {
      const words = clean.trim().split(/\s+/);
      last = words.pop() ?? "";
      first = words.join(" ");
    }
    const isSelf = last.includes(SELF_LAST) && first.includes(SELF_FIRST);
    return { first, last, isSelf };
  });
}

function parseEntry(block: string): Paper | null {
  const headerMatch = block.match(/^@(\w+)\s*\{\s*([^,]+),/s);
  if (!headerMatch) return null;
  const type = headerMatch[1].toLowerCase();
  const key = headerMatch[2].trim();
  const body = block.slice(headerMatch[0].length, block.lastIndexOf("}"));

  const fields: Record<string, string> = {};
  const fieldRegex = /(\w+)\s*=\s*/g;
  let match: RegExpExecArray | null;
  const positions: { name: string; start: number }[] = [];
  while ((match = fieldRegex.exec(body)) !== null) {
    positions.push({ name: match[1].toLowerCase(), start: fieldRegex.lastIndex });
  }
  for (let i = 0; i < positions.length; i++) {
    const { name, start } = positions[i];
    const end = i + 1 < positions.length ? findFieldEnd(body, start, positions[i + 1].start) : body.length;
    let value = body.slice(start, end).trim();
    value = value.replace(/,\s*$/, "").trim();
    if (value.startsWith("{") && value.endsWith("}")) value = value.slice(1, -1);
    if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
    fields[name] = value;
  }

  function findFieldEnd(str: string, start: number, nextFieldStart: number): number {
    // back up from nextFieldStart to the previous top-level comma
    const segment = str.slice(start, nextFieldStart);
    const lastComma = segment.lastIndexOf(",");
    return lastComma === -1 ? nextFieldStart : start + lastComma;
  }

  const title = stripAccentCommands(fields.title ?? "");
  const authors = parseAuthors(fields.author ?? "");
  const venue = stripAccentCommands(
    type === "article" || type === "preprint" ? fields.journal ?? "" : fields.booktitle ?? fields.journal ?? "",
  );
  const topics = (fields.topics ?? "")
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  return {
    key,
    type,
    title,
    authors,
    venue,
    year: fields.year ?? "",
    abstract: fields.abstract ? stripAccentCommands(fields.abstract) : undefined,
    topics,
    award: fields.award,
    awardName: fields.award_name,
    pdf: fields.pdf,
    code: fields.code,
    website: fields.website,
    doi: fields.doi,
    html: fields.html,
    isFlare: (fields.keywords ?? "").includes("flare"),
    bibtex: block.trim().replace(/,\s*$/, ""),
  };
}

function splitEntries(raw: string): string[] {
  const entries: string[] = [];
  const starts: number[] = [];
  const atRegex = /@\w+\s*\{/g;
  let m: RegExpExecArray | null;
  while ((m = atRegex.exec(raw)) !== null) {
    starts.push(m.index);
  }
  for (let i = 0; i < starts.length; i++) {
    const start = starts[i];
    const braceStart = raw.indexOf("{", start);
    let depth = 0;
    let end = braceStart;
    for (let j = braceStart; j < raw.length; j++) {
      if (raw[j] === "{") depth++;
      if (raw[j] === "}") {
        depth--;
        if (depth === 0) {
          end = j;
          break;
        }
      }
    }
    entries.push(raw.slice(start, end + 1));
  }
  return entries;
}

export function loadPapers(): { papers: Paper[]; topicColors: Record<string, string> } {
  const bibDir = path.join(REPO_ROOT, "_bibliography");
  const files = ["preprints.bib", "papers.bib"];
  const papers: Paper[] = [];
  for (const file of files) {
    const filePath = path.join(bibDir, file);
    if (!fs.existsSync(filePath)) continue;
    const raw = fs.readFileSync(filePath, "utf-8");
    const isPreprintFile = file === "preprints.bib";
    for (const block of splitEntries(raw)) {
      const entry = parseEntry(block);
      if (entry) {
        if (isPreprintFile) entry.type = "preprint";
        papers.push(entry);
      }
    }
  }
  papers.sort((a, b) => Number(b.year) - Number(a.year));

  const topicsYamlPath = path.join(REPO_ROOT, "_data", "topics.yml");
  const topicColors: Record<string, string> = {};
  if (fs.existsSync(topicsYamlPath)) {
    const doc = loadYaml(fs.readFileSync(topicsYamlPath, "utf-8")) as { name: string; color: string }[];
    for (const t of doc) topicColors[t.name] = t.color;
  }

  return { papers, topicColors };
}
