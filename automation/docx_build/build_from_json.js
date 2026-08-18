const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, BorderStyle, ExternalHyperlink,
} = require("docx");
const fs = require("fs");

const CONTENT_PATH = process.argv[2];
const OUT_PATH = process.argv[3];

const content = JSON.parse(fs.readFileSync(CONTENT_PATH, "utf-8"));
const issue = content.issue;

const INK = "1C1712";
const ACCENT = "B9541F";
const MUTED = "6B5F4D";
const SOURCE = "8A7A5C";

const SECTIONS_ORDER = [
  "Top News", "New Diksha Announcements", "Tirthankar Kalyanak",
  "Jain Festivals / Parva", "Community News",
  "Guru Maharaj Pravesh & Chaturmas Announcements",
  "New Temples & Tirth Renovation", "Jain Tirth News", "Jain Vihar",
  "The Jain Foundation News", "Jain Leadership / Forums",
  "Jain Business & Trade", "Other Community News / Announcements",
];

function rule() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: INK } },
    spacing: { after: 200 },
  });
}
function thinRule() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "D8CDB4" } },
    spacing: { after: 160 },
  });
}
function sectionTitle(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 60 },
    children: [new TextRun({ text, bold: true, size: 30, color: INK, font: "Georgia" })],
  });
}
function itemHeadline(text) {
  return new Paragraph({
    spacing: { before: 120, after: 60 },
    children: [new TextRun({ text, bold: true, size: 25, color: INK, font: "Georgia" })],
  });
}
function locDate(text) {
  return new Paragraph({
    spacing: { after: 40 },
    children: [new TextRun({ text: text.toUpperCase(), bold: true, size: 17, color: ACCENT, font: "Arial" })],
  });
}
function locDateWithLink(text, url) {
  const children = [new TextRun({ text: text.toUpperCase(), bold: true, size: 17, color: ACCENT, font: "Arial" })];
  if (url) {
    children.push(new TextRun({ text: "  →  ", bold: true, size: 17, color: ACCENT, font: "Arial" }));
    children.push(new ExternalHyperlink({
      link: url,
      children: [new TextRun({ text: "READ FULL ARTICLE", bold: true, size: 17, color: "1155CC", underline: {}, font: "Arial" })],
    }));
  }
  return new Paragraph({ spacing: { after: 40 }, children });
}
function bodyText(text) {
  return new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text, size: 21, color: "33291F", font: "Arial" })],
  });
}
function emptyNote(text) {
  return new Paragraph({
    spacing: { after: 200 },
    children: [new TextRun({ text, italics: true, size: 20, color: MUTED, font: "Arial" })],
  });
}
function divider() {
  return new Paragraph({ spacing: { after: 160 }, border: { top: { style: BorderStyle.SINGLE, size: 4, color: "D8CDB4" } } });
}

const children = [];

// Masthead
children.push(
  new Paragraph({
    spacing: { after: 40 },
    children: [new TextRun({ text: (issue.edition || "").toUpperCase(), bold: true, size: 18, color: SOURCE, font: "Arial" })],
  }),
  new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text: issue.title || "Jain Magazine", bold: true, size: 56, color: INK, font: "Georgia" })],
  }),
  new Paragraph({
    spacing: { after: 60 },
    children: [
      new TextRun({ text: `PUBLISHED ${issue.publish_date}`, bold: true, size: 17, color: SOURCE, font: "Arial" }),
      new TextRun({ text: "     •     ", size: 17, color: SOURCE }),
      new TextRun({ text: `COVERAGE: ${issue.coverage_start} — ${issue.coverage_end}`, bold: true, size: 17, color: SOURCE, font: "Arial" }),
    ],
  }),
  rule(),
);

// Sections — a section with no items is omitted entirely (no header, no
// "no news found" note), rather than shown as a visible empty placeholder.
for (const name of SECTIONS_ORDER) {
  const data = content.sections[name];
  if (!data) continue;
  const items = data.items || [];
  if (items.length === 0) continue;
  children.push(sectionTitle(name), thinRule());
  items.forEach((it, idx) => {
    if (idx > 0) children.push(divider());
    children.push(itemHeadline(it.headline || ""));
    children.push(locDateWithLink(`${it.location || ""} · Source: ${it.source || ""} · ${it.date || ""}`, it.url));
    children.push(bodyText(it.body || ""));
  });
}

// Footer
children.push(
  new Paragraph({ spacing: { before: 400 }, border: { top: { style: BorderStyle.SINGLE, size: 6, color: INK } } }),
  new Paragraph({
    spacing: { before: 160, after: 60 },
    children: [new TextRun({ text: issue.title || "Jain Magazine", bold: true, size: 24, color: INK, font: "Georgia" })],
  }),
  new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({
      text: "A publication compiled through AI curation of verified community portals, temple announcements, and recognised Jain news organisations — a sourced synthesis of Jain community news.",
      size: 19, color: "4A4033", font: "Arial",
    })],
  }),
  new Paragraph({
    children: [new TextRun({ text: `© ${(issue.publish_date || "2026").slice(0,4)} ${(issue.title || "JAIN MAGAZINE").toUpperCase()}`, size: 15, color: "A9997A", font: "Arial" })],
  }),
);

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1000, left: 1200, right: 1200 } } },
    children,
  }],
  styles: { default: { document: { run: { font: "Arial", size: 21, color: "33291F" } } } },
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT_PATH, buf);
  console.log("Wrote docx:", buf.length, "bytes ->", OUT_PATH);
});
