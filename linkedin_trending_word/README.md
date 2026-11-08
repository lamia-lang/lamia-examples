# LinkedIn Trending Word

Every morning, find the one unusual word — and the idea behind it — that is quietly
trending in your LinkedIn feed, so you can weave it into your own post for a shot at
extra reach.

The signal is not a hashtag. It is an ordinary-but-unusual word that suddenly shows up
inside the text of unrelated posts from strangers on the same day. This script hunts for
that word and writes it to a file for the day.

## How it works

1. Logs in to LinkedIn once; the session is remembered for later runs.
2. Opens your home feed and scrolls to load posts.
3. Keeps only posts from **random people** — not your 1st-degree connections, and not
   promoted/ads. Popularity does not matter; what matters is that the post surfaced from
   someone outside your network.
4. Sends the collected post texts to the model, which picks the single unusual word and
   the broader semantic idea shared across them.
5. Writes the result to `output/`.

At least `MIN_RANDOM_POSTS` (default 3) random-people posts must be collected before a
word is produced; otherwise the script asks you to scroll more / run again later.

## Setup

Set your credentials at the top of `find_trending_word.lm`:

```python
LINKEDIN_EMAIL    = "you@example.com"
LINKEDIN_PASSWORD = "your_password"
```

The model chain and browser options live in `config.yaml` and are loaded automatically —
you do not read them from the script.

First login: keep `headless: false` in `config.yaml` so you can clear any 2FA / CAPTCHA
in the visible browser window. After a successful login the session is saved under
`.lamia_sessions/linkedin/` and reused, so later runs skip the login step.

## Running

```bash
lamia find_trending_word.lm
```

Check selectors first if the feed layout seems to have changed:

```bash
lamia tests/check_selectors.lm
```

## Scheduling (daily, in the morning)

```bash
lamia schedule add find_trending_word.lm --at 08:00
lamia schedule list
```

## Output

| File | Contents |
|------|----------|
| `output/today.txt` | Just today's word — the thing to use in your post |
| `output/trending_words.tsv` | A dated log: `date <tab> word <tab> idea` per run |

## Files

```text
linkedin_trending_word/
├── find_trending_word.lm      # Main script: login, collect, analyze, write
├── extract_trending_word.hu   # Prompt: pick the unusual trending word/idea
├── config.yaml                # Model chain + browser options (auto-loaded)
├── tests/
│   └── check_selectors.lm     # Smoke test for the feed selectors
└── output/                    # Generated results (gitignored)
```

## Notes

- Selectors are explicit CSS selectors for LinkedIn's feed DOM. LinkedIn changes its
  markup over time; if collection drops to zero, run the selector smoke test and update
  the selectors in both `tests/check_selectors.lm` and `find_trending_word.lm`.
- Session reuse relies on saved cookies. To force a fresh login:
  `rm -rf .lamia_sessions/linkedin/`.
- Automating LinkedIn is subject to LinkedIn's User Agreement and to 2FA/CAPTCHA/anti-bot
  measures. Use your own account and run responsibly.
