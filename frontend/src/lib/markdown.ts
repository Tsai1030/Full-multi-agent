function escapeHtml(text: string): string {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inlineToHtml(text: string): string {
  let html = escapeHtml(text);
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  return html;
}

const HEADING_RE = /^(#{1,4})\s+(.*)$/;
const UL_RE = /^[-*+]\s+(.*)$/;
const OL_RE = /^\d+[.)]\s+(.*)$/;
const QUOTE_RE = /^>\s?(.*)$/;
const HR_RE = /^(?:-{3,}|\*{3,}|_{3,})$/;

function isBlockStart(line: string): boolean {
  return (
    line === "" ||
    HEADING_RE.test(line) ||
    UL_RE.test(line) ||
    OL_RE.test(line) ||
    QUOTE_RE.test(line) ||
    HR_RE.test(line)
  );
}

/** Converts a constrained markdown subset (headings, lists, quotes, emphasis, links, code, hr) to HTML. */
export function mdToHtml(markdown: string): string {
  if (!markdown) return "";

  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const blocks: string[] = [];

  let list: { type: "ul" | "ol"; items: string[] } | null = null;
  let quote: string[] | null = null;

  const flushList = () => {
    if (!list) return;
    const tag = list.type;
    blocks.push(`<${tag}>${list.items.map((item) => `<li>${inlineToHtml(item)}</li>`).join("")}</${tag}>`);
    list = null;
  };

  const flushQuote = () => {
    if (!quote) return;
    blocks.push(`<blockquote>${quote.map((l) => `<p>${inlineToHtml(l)}</p>`).join("")}</blockquote>`);
    quote = null;
  };

  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();

    if (!line) {
      flushList();
      flushQuote();
      i++;
      continue;
    }

    if (HR_RE.test(line)) {
      flushList();
      flushQuote();
      blocks.push("<hr />");
      i++;
      continue;
    }

    const heading = line.match(HEADING_RE);
    if (heading) {
      flushList();
      flushQuote();
      const level = heading[1].length;
      blocks.push(`<h${level}>${inlineToHtml(heading[2])}</h${level}>`);
      i++;
      continue;
    }

    const quoteLine = line.match(QUOTE_RE);
    if (quoteLine) {
      flushList();
      if (!quote) quote = [];
      quote.push(quoteLine[1]);
      i++;
      continue;
    }
    flushQuote();

    const ul = line.match(UL_RE);
    if (ul) {
      if (!list || list.type !== "ul") {
        flushList();
        list = { type: "ul", items: [] };
      }
      list.items.push(ul[1]);
      i++;
      continue;
    }

    const ol = line.match(OL_RE);
    if (ol) {
      if (!list || list.type !== "ol") {
        flushList();
        list = { type: "ol", items: [] };
      }
      list.items.push(ol[1]);
      i++;
      continue;
    }
    flushList();

    const paragraph = [line];
    i++;
    while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i].trim())) {
      paragraph.push(lines[i].trim());
      i++;
    }
    blocks.push(`<p>${paragraph.map(inlineToHtml).join("<br />")}</p>`);
  }

  flushList();
  flushQuote();

  return blocks.join("\n");
}
