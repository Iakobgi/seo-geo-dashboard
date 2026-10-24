import type { CrawledPage, CrawlResult } from "../api/endpoints";
export function pageIssues(page: CrawledPage): string[] {
  const issues: string[] = [];
  if (!page.status_code || page.status_code >= 400) {
    issues.push(
      page.status_code ? `HTTP ${page.status_code}` : "No HTTP response",
    );
    return issues;
  }
  if (!page.title?.trim()) issues.push("Missing title");
  if (!page.meta_description?.trim()) issues.push("Missing description");
  if (!page.h1?.trim()) issues.push("Missing H1");
  if (page.noindex) issues.push("Noindex directive");
  if (page.word_count < 300) issues.push("Under 300 words");
  if (page.load_time !== null && page.load_time > 2)
    issues.push("Response over 2s");
  return issues;
}
export function duplicateUrls(result: CrawlResult): Set<string> {
  return new Set(
    [
      ...Object.values(result.duplicate_titles),
      ...Object.values(result.duplicate_meta_descriptions),
    ].flat(),
  );
}
export function csvCell(value: unknown): string {
  const text = String(value ?? "");
  const safe = /^[=+@\-\t\r]/.test(text.trimStart()) ? "'" + text : text;
  return '"' + safe.replace(/"/g, '""') + '"';
}
export function escapeHtml(value: string): string {
  return value.replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ]!,
  );
}
