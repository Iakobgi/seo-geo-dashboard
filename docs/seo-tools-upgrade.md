# Local SEO tools upgrade

Reviewed the public Seobility website and its website audit, competitor analysis, and snippet generator pages. The most practical additions to the current app are multi-page technical checks, comparison of saved audits, and a metadata editor. These reuse existing backend capabilities and need no new paid data provider.

## Implemented

- **Site crawl** (`/site-crawl`): up to 20 linked pages, same-site traversal, robots.txt handling, missing metadata/H1 checks, duplicate title and description groups, failed URLs, indexing directives, response times, search/filter, and CSV export. Each request is limited to 150 seconds. Results are temporary and are not saved as audits.
- **Compare audits** (`/compare`): select and swap saved snapshots, view SEO/GEO score differences, compare content metrics and metadata, and inspect findings unique to each snapshot. Different-page comparisons are labeled. Finding differences are not claimed as verified fixes.
- **Search snippet editor** (`/snippet`): load saved metadata, edit title and description, preview desktop/mobile truncation, and export escaped title/meta/canonical HTML. Preview and length guidance are illustrative; the editor does not publish changes to a website.

No migrations are required. No live rankings, backlinks, continuous uptime monitoring, or AI citation measurements are invented. Those would need separate provider and scheduling work.

## Verification

- `cd frontend; npm run build`
- `cd frontend; npm run test:tools`
- `cd backend; python -m pytest tests/ -q` (with `PYTHONPATH=.`)
- Browser checks in a separate local SQLite workspace: real one-page and five-page crawls, duplicate filtering, CSV export, saved-snapshot comparison and swapping, snippet import/edit/export, and mobile navigation/layout.

The isolated preview uses temporary labeled test snapshots. Live account data was not modified. No push or deployment was performed.

## References

- https://www.seobility.net/en/
- https://www.seobility.net/en/website-audit/
- https://www.seobility.net/en/seo-competitor-analysis-tools/
- https://www.seobility.net/en/serp-snippet-generator/
