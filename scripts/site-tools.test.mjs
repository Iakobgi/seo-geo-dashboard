import test from 'node:test';
import assert from 'node:assert/strict';
import { csvCell, escapeHtml, pageIssues, duplicateUrls } from '../frontend/src/utils/siteTools.ts';

test('CSV export quotes delimiters and neutralizes spreadsheet formulas', () => {
  assert.equal(csvCell('A,"B"\nC'), '"A,""B""\nC"');
  for (const text of ['=HYPERLINK("bad")', '+SUM(1,1)', '-1+2', '@SUM(1)', '  =SUM(1)']) {
    assert.ok(csvCell(text).startsWith('"\''), text);
  }
});

test('metadata export escapes markup and attribute boundaries', () => {
  const payload = '\"><script>alert(1)</script>&\'';
  const escaped = escapeHtml(payload);
  assert.ok(!escaped.includes('<script>'));
  assert.ok(!escaped.includes('"'));
  assert.ok(escaped.includes('&quot;'));
  assert.ok(escaped.includes('&lt;script&gt;'));
  assert.ok(escaped.includes('&amp;'));
});

test('crawl review distinguishes failed requests and deduplicates metadata groups', () => {
  const failed = {status_code:500,title:null,meta_description:null,h1:null,noindex:false,word_count:0,load_time:0};
  assert.deepEqual(pageIssues(failed), ['HTTP 500']);
  const urls=duplicateUrls({duplicate_titles:{Title:['https://example.com/a','https://example.com/b']},duplicate_meta_descriptions:{Description:['https://example.com/a','https://example.com/c']}});
  assert.equal(urls.size,3);
});
