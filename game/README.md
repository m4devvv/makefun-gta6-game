# Palmora Bay

An original top-down open-world crime game in the spirit of GTA 6, built
for the make.fun "Make GTA 6" bounty. Everything here is made from scratch:
one file, `index.html`, with inline CSS and JavaScript on a canvas 2D
renderer. No libraries, no downloaded assets, no network requests, and
nothing borrowed from any commercial game — the city, the cars, the people
and the sounds are all drawn or synthesized in code.

## Play it

```sh
cd game
python3 -m http.server 8000
# then open http://127.0.0.1:8000/index.html
```

You can also open `index.html` straight from disk. Click **START GAME**
(the click also unlocks sound).

## Controls

- **WASD / arrow keys** — walk on foot. In a car: W accelerates, S brakes
  and reverses, A/D steer.
- **E** — get into (or out of) the nearest car. Taking a car that is not
  yours is a crime: the wanted level goes up.
- **P** — pause and resume.

## The city

Palmora Bay is a 2400×1800 map: a grid of roads with sidewalks, buildings
with lit windows, a park, and a beach with water along the east edge.
Traffic cars cruise the roads and pedestrians stroll the sidewalks, so
the streets feel alive whether you are walking or driving.

## Wanted level — 1 to 5 stars

Crime attracts the police, and the police fight back:

- Steal a car: +1 star. Hit a pedestrian: +2. Ram a police car: +1.
- Police cars spawn and chase you, and their rams drain your health.
  Reach 0 HP and you wake up at the hospital with a clean slate.
- If you stop committing crimes and keep every police car more than
  ~420 px away, the heat fades — roughly one star every 2 seconds after
  about 6 seconds of quiet. Hide in the park, or outrun them: a stolen
  car's top speed beats a police cruiser's.

## Missions — $1,000 total

1. **Grand theft delivery** — press E next to a parked car, then drive it
   into the yellow zone on the south-east road. Pays **$200**.
2. **Package run** — pick up 5 green `$` packages scattered on the roads,
   on foot or by car. Pays **$300**.
3. **Hot escape** — the wanted level jumps to 3 stars. Survive until it
   decays back to 0. Pays **$500**.

Finish all three and the game opens up into free roam.

## On screen

The HUD shows cash, wanted stars, a health bar, your speed, and the
current objective. The minimap (top-right) marks you in orange, traffic
in white, police in red, the delivery zone in yellow, and packages in
green.

## Saving

Every completed mission auto-saves cash and mission progress to
`localStorage` under `palmora-bay-save-v1`. Reopen the game and the start
screen tells you a save was found — your progress is right where you
left it.

## Repo layout

- `game/index.html` — the entire game
- `game/README.md` — this file
- `TESTS.md` — what the automated playtest checks
- `playtest.py` — the headless Playwright playtest (15 checks)
- `screenshots/` — 4 screenshots taken by the playtest (the first is the cover)
- `main.ts` — hands `game/` and `screenshots/` to the make.fun grader
- `vendor/makefun-game.ts` — the kit's dossier library, unchanged
