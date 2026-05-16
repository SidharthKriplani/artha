# ARTHA v0 — AI/ML Builder Pain Signal Digest

ARTHA scans AI/ML and Indian tech communities on Reddit for recurring developer pain points, scores them by signal strength, and saves them to a CSV for review.

No API key required. Uses Reddit's public JSON endpoint.

---

## What it does

- Scans 7 subreddits: `r/LocalLLaMA`, `r/MachineLearning`, `r/LanguageModelHacking`, `r/SideProject`, `r/devtools`, `r/developersIndia`, `r/indianstartups`
- Matches posts against 40+ pain keywords (frustration, workaround, gap signals)
- Scores each signal 1–3 based on upvotes, comments, and keyword density
- Appends new results to `data/pain_signals.csv`
- Skips already-seen posts on repeat runs

---

## Setup

```bash
# Install dependency
pip3 install requests

# Run once
python3 digest/scraper.py
```

---

## Output

Results saved to `data/pain_signals.csv` with columns:

| Column | Description |
|---|---|
| `id` | Reddit post ID |
| `date` | Post date |
| `subreddit` | Source community |
| `title` | Post title |
| `url` | Direct link |
| `upvotes` | Score |
| `comments` | Comment count |
| `matched_keywords` | Which pain keywords matched |
| `keyword_count` | Number of matches |
| `score` | Signal strength: 1 (weak) → 3 (high priority) |
| `body_snippet` | First 200 chars of post body |

---

## Run every 2 days (Mac)

Add to crontab to run automatically:

```bash
crontab -e
```

Add this line (runs at 8am every 2 days):
```
0 8 */2 * * cd /Users/ASUS/Documents/GitHub/artha && python3 digest/scraper.py >> data/scraper.log 2>&1
```

---

## Repo structure

```
artha/
├── digest/
│   └── scraper.py        # Main script
├── data/
│   ├── pain_signals.csv  # Output (auto-generated)
│   └── seen_ids.json     # Deduplication log (auto-generated)
├── solutions/            # Open-source solution repos go here
├── requirements.txt
└── README.md
```

---

## Part of the ARTHA project

ARTHA is a community signal intelligence tool that converts AI/ML developer pain into structured open-source solutions.
Built by [@SidharthKriplani](https://github.com/SidharthKriplani)
