# TESTS — Palmora Bay

## Automated headless playtest (rebuilt version, run in a recorded session 21 Nov 2026: 15/15 PASS)

Tool: Playwright 1.49.1 (Python) + Chromium Headless Shell 131, installed
via `pip install playwright==1.49.1` (browsers already cached). Served locally
with `python3 -m http.server 8931`, then ran `playtest.py`. Script: `playtest.py` in this folder.

The game was fully re-implemented in a recorded session on 21 Nov 2026
(`game/index.html`, 24,178 bytes) so it can be submitted for gta6-01, whose
rules require the build to happen under recording. Same feature set and same
test hooks as the first version (DOM ids, `window.__game`, save key).

Results (run against the rebuilt game):

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
walked on foot to the parked car at (560,330) — player reached (553.6, 357.2) —
pressed E, drove forward (player moved from x≈554 to x≈849), teleported the
car into the delivery zone to trigger Mission 1, teleported onto each of the
5 packages for Mission 2, pressed P twice for pause/resume, and verified the
save in `localStorage` plus the saved-game notice after a page reload.
Mission 3's completion trigger (wanted reaching 0) was verified in the
playtest; the natural decay path was verified separately (see below).

## Wanted-decay check (separate run, rebuilt version)

Set the game to Mission 3 (wanted 3), set `lastCrime` 1000 frames in the
past and kept police far away (>420 px). Wanted decayed 3 → 2 → 1 → 0 over
~22–25 s of real time and Mission 3 completed naturally with its $500 reward.
No JS errors. (The check script asserted the wrong cash total on its first
run — $1000 instead of $500 for a mission-3-only run — and passed after the
assertion was fixed; the game behaved correctly in both runs.)

## Bugs found and fixed during testing (first build; kept as history)

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

## Static checks (rebuilt version)

- `node --check` on the extracted `<script>` block: OK, no syntax errors.
- `curl http://127.0.0.1:8931/index.html`: HTTP 200, 24,178 bytes.
- No external references in `index.html` (no `http`, no `src=`); no
  Rockstar / commercial-game names, art, or sound. Sound is WebAudio
  oscillator beeps only.
- `MAKEFUN_OUTPUT_DIR=out node main.ts`: writes `out/game/`,
  `out/screenshots/` and `out/dossier.json` (schema makefun/dossier/v1,
  text 24,388 bytes). `main.ts` and `vendor/makefun-game.ts` are byte-identical
  copies of the kit starter files; `LICENSE` is the kit's MIT license.

## Screenshots (real, from the headless playtest of the rebuilt game)

- `screenshots/01-start-screen.png` — title screen with controls
- `screenshots/02-gameplay-on-foot.png` — on foot, city + minimap + HUD
- `screenshots/03-in-car.png` — in a stolen car, WANTED: 1
- `screenshots/04-mission-3-wanted.png` — Mission 3, WANTED: 3

Screenshots were inspected visually: HUD, minimap, roads, buildings,
cars, and mission text all render correctly. No screenshots were faked.
Only 4 screenshots are kept (the bounty cap); the playtest's 5th shot
(all missions done) is deleted after each run.

## Not tested

- Real-human play balance (mission difficulty, police chase feel) — only
  automated play; a human playthrough is still recommended before
  submitting anywhere.
- Audio output (beeps) — WebAudio calls run without errors, but headless
  Chromium has no speakers to verify by ear.
- Mobile / touch controls — keyboard only, by design.
