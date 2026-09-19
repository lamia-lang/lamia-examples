# Ad Copy Generator

Batch-generate validated A/B ad copy variants from campaign briefs. Supports Google Search RSAs, Google Display, and Meta ads with platform-specific character limits enforced by Pydantic validation.

## Usage

```bash
lamia generate_variants.lm
```

## What it does

1. Reads campaign briefs from `sample_data/campaigns.csv`
2. Generates 4 variant angles per campaign per platform (benefit, urgency, social proof, question hook)
3. Scores each variant for clarity, brand fit, and CTA strength
4. Exports combined JSON + per-platform CSVs to `output/`
5. Optionally publishes to Meta or Google Ads API when credentials are set

## Output files

| File | Contents |
|------|----------|
| `output/all_variants.json` | All variants across all platforms with full metadata |
| `output/google_search_variants.csv` | Google Search RSA variants — upload-ready for Google Ads |
| `output/google_display_variants.csv` | Google Display variants — upload-ready for Google Ads |
| `output/meta_variants.csv` | Meta ad variants — upload-ready for Meta Ads Manager |

## Social proof placeholders

Social proof variants use placeholder tokens (REVIEW_COUNT, STAR_RATING, USER_COUNT) instead of hallucinated numbers. The marketer fills in real stats before launch. When Lamia adds web search support, the placeholders will be replaced with verified data automatically.

## Project structure

```
ad_copy_generator/
├── generate_variants.lm       # main orchestrator
├── google_search_ad.hu        # Google Search RSA prompt
├── google_display_ad.hu       # Google Display prompt
├── meta_ad.hu                 # Meta ad prompt
├── score_variant.hu           # quality scoring prompt
├── sample_data/
│   └── campaigns.csv          # campaign briefs
├── output/                    # generated variants (JSON + per-platform CSVs)
└── config.yaml                # model chain and brand voice
```

## Optional: publish to ad platforms

Set environment variables to enable direct API publishing:

```bash
export META_ACCESS_TOKEN=your_meta_token
export GOOGLE_ADS_DEVELOPER_TOKEN=your_google_token
```

Without credentials, the script exports files for manual upload.

## Customization

- Add new platforms: create a Pydantic model + `.hu` prompt file
- Add languages: loop over languages in the campaign iteration
- Change scoring: edit `score_variant.hu` or add custom score fields
- Connect to product catalog: replace the CSV with your catalog file
