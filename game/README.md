# Palmora Bay — Open-World Crime Game

A standalone, original top-down open-world crime game in the spirit of GTA 6.
One self-contained file: `index.html` (inline CSS + JS, canvas 2D, no external
assets, no network, no content from any commercial game). All art is drawn in
code; all sound is WebAudio beeps.

## How to run

```sh
cd game
python3 -m http.server 8000
# open http://127.0.0.1:8000/index.html
```

Or just double-click `index.html` to open it directly in a browser.
Click **START GAME** (this also enables sound).

## Controls

| Key | Action |
|---|---|
| WASD / Arrow keys | Move on foot; in a car: W gas, S brake/reverse, A/D steer |
| E | Enter / exit the nearest car (stealing a car raises wanted) |
| P | Pause / resume |

## The city

Palmora Bay is a 2400×1800 world: a road grid, buildings with lit windows,
sidewalks, a park, and a beach + water edge on the east side. Traffic cars
drive the roads and pedestrians walk the sidewalks.

## Wanted level (1–5 stars)

- Stealing a car: +1 star. Hitting a pedestrian: +2. Ramming police: +1.
- Police cars spawn and chase you; being rammed by them drains health.
  At 0 HP you wake up at the hospital, wanted cleared.
- Wanted decays when you commit no crime for ~6 seconds **and** stay more
  than ~420 px away from any police car (about 2 s per star after that).
  Hide, or outrun them in a car (top speed beats police).

## Missions

1. **Steal a car & deliver it** — press E near a parked car, drive into the
   yellow zone (bottom-right, on the 1800 road). Reward **$200**.
2. **Collect 5 packages** — green `$` packages on roads around the city,
   on foot or in a car. Reward **$300**.
3. **Escape a 3-star wanted level** — wanted is set to ★★★; survive until
   it decays to 0. Reward **$500**. Total $1,000, then free roam.

## HUD

Cash, wanted stars, health bar, speed, current mission objective, and a
minimap (top-right: orange = you, white = cars, red = police, yellow =
delivery zone, green = packages).

## Save / load

Cash + mission progress auto-save to `localStorage` (`palmora-bay-save-v1`)
on every mission completion. Reopening the game shows the saved progress
on the start screen and continues from it.

## Files

- `game/index.html` — the whole game
- `game/README.md` — this file
- `TESTS.md` — what was tested
- `playtest.py` — automated headless playtest (Playwright + Chromium)
- `screenshots/` — screenshots from the headless playtest
