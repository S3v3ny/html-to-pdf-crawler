# HTML to PDF Crawler

A focused Python script that extracts text and images from a sequence of pathology teaching pages and renders each page as a PDF.

> This repository is an educational example tailored to the University of Utah WebPath page structure. Use it only on content you are permitted to access, and respect the site's terms, copyright, and rate limits.

## What it does

- Downloads HTML pages from a configured base URL
- Extracts headings, paragraphs, tables, list items, and images
- Keeps images hosted on the same domain
- Generates one PDF per source page
- Skips selected navigation images

## Requirements

- Python 3.9+
- `requests`
- `beautifulsoup4`
- `xhtml2pdf`

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

The current script uses constants and a numeric range in `data.py`:

```python
TARGET_URL = "https://webpath.med.utah.edu"
DELAY = 0

for i in range(199, 261):
    ...
```

Before running it:

1. Confirm that you are allowed to retrieve the target pages.
2. Adjust `TARGET_URL`, the page range, and `DELAY`.
3. Create the output directory:

```bash
mkdir output
```

A non-zero delay is recommended to avoid sending requests too quickly.

## Run

```bash
python data.py
```

Generated PDFs are written to `output/`; downloaded images are cached in `chapter_images/`.

## Limitations

- The extraction rules are tailored to one site's HTML structure.
- URLs and the page range are currently configured in source code.
- Network retries and rate-limit handling are minimal.
- Complex CSS and JavaScript-rendered pages are not supported.
- The script does not currently expose a command-line interface.

## Roadmap

- Add CLI options for URL, range, delay, and output directory
- Add retry/backoff behavior and clearer error reporting
- Preserve more of the original page structure
- Add tests using local HTML fixtures
- Make site-specific extraction rules pluggable

## Related article

Additional background may be available at [gr4ycr4ne.cn](https://gr4ycr4ne.cn/).
