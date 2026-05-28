# Pinterest Pin Publisher

Pinterest API access has a problem: to publish at scale programmatically, you often need approval as an established business, but when you are still small, odds of approval are lower and manual pin publishing becomes exhausting.

This Lamia script is built for that stage: automate repeatable Pinterest posting from your own image queue while you are still growing.

## How It Works

1. Logs in to Pinterest (once, session is remembered).
2. Reads a queue file to determine which pins to publish next.
3. Uploads each image, fills title/description/link, selects board, then publishes.
4. Advances the queue marker so the next run continues where the previous run stopped.

## Prerequisites

1. Create your target Pinterest board first (the board must already exist before this script runs).
2. Remove example files from `pins/` and place your real pin images in that folder.
3. Update `pin_metadata.json` so each entry maps to an image file in `pins/` with an exact filename match.
4. Update `publish_queue.txt` so files listed under `PUBLISH_START` match your image filenames.
5. Set `PINTEREST_EMAIL`, `PINTEREST_PASSWORD`, and `BOARD` in `publish_pins.lm`.

## File Structure

```text
pinterest_pin_publisher/
├── publish_pins.lm           # Main publishing script
├── pin_metadata.json         # Pin metadata (title, description, link per image)
├── publish_queue.txt         # Queue tracking which pins remain
├── pins/                     # Your pin images (PNG/JPG)
├── tests/
│   └── check_selectors.lm    # Smoke test for Pinterest selectors
└── .lamia_sessions/          # Auto-created after first login
```

## Metadata Format

```json
{
  "pins": [
    {
      "filename": "my-pin.png",
      "title": "Pin Title",
      "description": "Pin description text",
      "link": "https://your-site.com/page"
    }
  ]
}
```

`filename` must exactly match an existing file in `pins/`.

## Queue Format

Everything below `PUBLISH_START` is published in order. After each successful publish, the marker advances.

```text
PUBLISH_START
my-pin-1.png
my-pin-2.png
my-pin-3.png
```

## Running Publisher

```bash
lamia --file publish_pins.lm
```

Each run publishes 5-10 pins (randomized). Schedule with cron if needed.

## Smoke Testing Selectors

Pinterest changes UI selectors over time. Before a production run, execute:

```bash
lamia --file tests/check_selectors.lm
```

This test checks that required input/button selectors still exist and does not publish pins.

## Session Management

On first run, Lamia logs in and stores cookies in `.lamia_sessions/pinterest/`. Future runs reuse the saved session unless cookies expire.

To force fresh login:

```bash
rm -rf .lamia_sessions/pinterest/
```

## Notes

- Board name is case-sensitive and must match Pinterest exactly.
- Random delays mimic human behavior.
- Script relies on stable selector patterns (`starts-with(@id, ...)`) for dynamic Pinterest elements.
