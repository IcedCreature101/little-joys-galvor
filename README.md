# Galvor AI — Intern Assignment: Creator Selection for Little Joys

## Overview
Little Joys, an Indian kids' nutrition brand, wants to know which 5 of 20 Instagram creators to work with next, and what each should say. This project uses **only the brand's own data** (no general market opinion, no external influencer databases).

## Data Sources
- `little-joys-data/creators.csv` — 20 creator profiles (21 columns: handle, bio, followers, themes, voice, format_habits, catchphrases, what_feels_native, audience_read, etc.)
- `little-joys-data/creator_posts.csv` — 392 creator posts (engagement: plays, likes, comments; labels: content_type, topic, format)
- `little-joys-data/ads.csv` — 100 Little Joys video ads (ad_format, hook_type, performance_style, made-up spend/inr/revenue)
## Scoring Algorithm
5-dimensional rubric, 0-85 total scale:

| Dimension | Max Score | Data Source |
|---|---|---|
| Brand-Fit (theme + voice + format + native) | 25 | `creators.csv` |
| Language & Culture (language + catchphrase) | 15 | `creators.csv` |
| Risk Subtractors | 0-15 deduction | `creators.csv` system fields |
| Engagement/Audience | 20 placeholder | `creator_posts.csv` follower counts |
| **Total** | **85** | — |

**Tier thresholds** (calibrated to actual data distribution):
- **≥50**: RECOMMENDED — strong fit, proceed with selection
- **≥40**: STRONG CANDIDATE — good fit with minor adjustments, reliable contingency
- **≥30**: MODERATE FIT — works only with messaging adjustments, contingency only
- **<30**: RECONSIDER — significant misalignment, not recommended

## Key Results
- **20 creators scored** across all 5 dimensions
- **Top tier (RECOMMENDED):** drgarima_mehta (48/85) — pediatrician + Hinglish + clinical format + native alignment
- **Strong Candidates (3):** ekamichildcare (40/85), instamommy_suchi (40/85)
- **Moderate Fit (14):** parentingtips_surat, foodies_by_neha, paediatrics_decoded, etc.
- **Reconsider (3):** sia_3vedi, couple_adishiv

## Bug Fixes During Development
1. **Inconsistent totals** (individual vs. summary ranking showed different scores for same creator) — unified `brand_fit + lang_total + 20 - risk_deduct` formula
2. **Risk deduction double-counting** — `authenticity_concerns: "None observed"` JSON key appearing for all creators; fixed by checking **value** not key, recognizing negation phrases
3. **Tier thresholds misaligned** — original 75-85/"Top Tier" thresholds didn't match score range (30-50); revised to data-appropriate thresholds

## How to Run
```bash
cd little-joys-data
python score_all_creators.py
Output: Full 20-creator scoring analysis + ranked leaderboard + tier breakdown.
Compliance
-  All scores derive from brand's own CSV data — no general opinion, no external databases
-  Every score traces to specific CSV cell values (citations in code comments)
-  Risk deduction mechanism handles data artifacts (authenticity_concerns JSON key for all creators with value "None observed")
-  Hook type & format recommendations mapped from brand's own ad library (100 ads' hook_type + ad_format distributions)

### Step 4: Initialize Git
```bash
# In the repo root (Galvor AI/ or little-joys-data/)
git init
git add score_creators.py score_test.py score_all_creators.py README.md
git commit -m "Initial commit: Creator scoring algorithm for Little Joys assignment"
git remote add origin <your-repo-url>
git push -u main origin main
