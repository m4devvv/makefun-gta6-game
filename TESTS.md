# TESTS — Palmora Bay

## Automated headless playtest (final run: 15/15 PASS)

Tool: Playwright 1.49.1 (Python) + Chromium Headless Shell 131, installed
via `npx playwright install chromium` (no browser was pre-installed on this
machine). Served locally with `python3 -m http.server 8931`, then ran
`playtest.py`. Script: `playtest.py` in this folder.

Results (final run, after all fixes):

```
PASS - start screen visible
PASS - no JS errors on load
PASS - game started (start screen hidden)
PASS - enter car with E (steal)
PASS - stealing raises wanted >=1
PASS - mission 1 completes -> mission 2, cash $200
PASS - mission 2 completes -> mission 3, cash $500
PASS - mission 3 starts with wanted 3
PASS - pause with P shows pause screen
PASS - resume with P hides pause screen
PASS - mission 3 completes on wanted 0 -> cash $1000, all done
PASS - end screen shown
PASS - localStorage save has cash 1000 + mission 3
PASS - reload shows saved-game info
PASS - no JS errors during playtest

15/15 checks passed
```

What the playtest actually did (real keyboard input, not just code review):
walked on foot to the parked car at (560,330), pressed E, drove forward
(player moved from x≈547 to x≈772), teleported the car into the delivery
zone to trigger Mission 1, teleported onto each of the 5 packages for
Mission 2, pressed P twice for pause/resume, and verified the save in
`localStorage` plus the saved-game notice after a page reload.
Mission 3's completion trigger (wanted reaching 0) was verified in the
playtest; the natural decay path was verified separately (see below).

## Wanted-decay check (separate run)

Set the game to Mission 3 (wanted 3), set `lastCrime` 1000 frames in the
past and moved police far away. Wanted decayed 3 → 2 → 1 over ~18 s of
real time. Note: it is slow on foot because police chase back into range
(<420 px) and reset the decay timer — by design, escaping is meant to be
done in a car (top speed 8.5 vs police 6.2) or by breaking line of sight.
Decay tuning was softened after this check: no-crime gate 600 → 360
frames, per-star time 180 → 120 frames.

## Bugs found and fixed during testing

1. **Player spawned inside a building (420,420)** — every move was reverted
   by building collision, so the player could not move at all. Fixed: spawn
   moved to (336,450), on a road.
2. **Delivery zone and packages inside buildings** — delivery was at
   (1950,1650) inside a building block; packages at (500,500) etc. were
   unreachable. Fixed: delivery to (1836,1650) on the 1800 road; all 5
   packages moved onto roads.
3. **Packages collectible before Mission 2** — walking over them during
   Mission 1 pre-collected them. Fixed: collection only counts in Mission 2.
4. **Mission 3 set wanted to 5, not 3** — it added +3 on top of the wanted
   level already earned by stealing. Fixed: Mission 3 now sets wanted to
   exactly 3. Verified in screenshot 04.
5. **HP bar overlapped the "HP 100" text** in the HUD. Fixed: bar moved
   right (x=95), speed text moved to x=185.
6. **Playtest flakiness** — blind keyboard timers failed when headless frame
   rate dipped (~30 fps), leaving the player stuck on a building corner.
   Fixed the *test*, not the game: the walk is now adaptive (moves until
   the position is reached, steps back up if stuck).

## Static checks

- `node --check` on the extracted `<script>` block: OK, no syntax errors.
- `curl http://127.0.0.1:8931/index.html`: HTTP 200, 21,695 bytes.
- No external references in `index.html` (no `http`, no `src=`); no
  Rockstar / commercial-game names, art, or sound. Sound is WebAudio
  oscillator beeps only.

## Screenshots (real, from the headless playtest)

- `screenshots/01-start-screen.png` — title screen with controls
- `screenshots/02-gameplay-on-foot.png` — on foot, city + minimap + HUD
- `screenshots/03-in-car.png` — in a stolen car, WANTED: 1
- `screenshots/04-mission-3-wanted.png` — Mission 3, WANTED: 3
- `screenshots/05-all-missions-done.png` — "ALL MISSIONS DONE!", $1000

Screenshots were inspected visually: HUD, minimap, roads, buildings,
cars, and mission text all render correctly. No screenshots were faked.

## Not tested

- Real-human play balance (mission difficulty, police chase feel) — only
  automated play; a human playthrough is still recommended before
  submitting anywhere.
- Audio output (beeps) — WebAudio calls run without errors, but headless
  Chromium has no speakers to verify by ear.
- Mobile / touch controls — keyboard only, by design.
