"""Headless playtest for Palmora Bay. Run while http server is on :8931.
Screenshots -> screenshots/, asserts printed as PASS/FAIL."""
import time, sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8931/index.html"
OUT = "/home/hatch/workspace/makefun-gta6-game/screenshots"
errors = []
results = []
def check(name, cond):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), "-", name)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1000, "height": 760})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/01-start-screen.png")
    check("start screen visible", pg.is_visible("#startScreen"))
    check("no JS errors on load", not errors)

    pg.click("#startBtn")
    pg.wait_for_timeout(500)
    check("game started (start screen hidden)", not pg.is_visible("#startScreen"))
    pg.screenshot(path=f"{OUT}/02-gameplay-on-foot.png")

    # Walk to nearest parked car (560,330) from (336,450): up to the road
    # first (y~336), then right along the road to x~560.
    # Adaptive (not blind timers): headless frame rate varies, and the
    # building corner at (386,386) blocks a straight rightward walk.
    def pos():
        return pg.evaluate("() => ({x: window.__game.player.x, y: window.__game.player.y})")
    for _ in range(20):
        if pos()["y"] <= 360: break
        pg.keyboard.down("w"); pg.wait_for_timeout(200); pg.keyboard.up("w")
    for _ in range(30):
        p0 = pos()
        if p0["x"] >= 540: break
        pg.keyboard.down("d"); pg.wait_for_timeout(200); pg.keyboard.up("d")
        if pos()["x"] <= p0["x"] + 1:  # stuck on a corner: step back up onto the road
            pg.keyboard.down("w"); pg.wait_for_timeout(200); pg.keyboard.up("w")
    pg.wait_for_timeout(300)
    pos = pg.evaluate("() => ({x: window.__game.player.x, y: window.__game.player.y})")
    print("player after walk:", pos)
    # nudge closer if needed via teleport-free walk: try E, if not in car, walk more
    pg.keyboard.press("e"); pg.wait_for_timeout(300)
    in_car = pg.evaluate("() => !!window.__game.player.inCar")
    if not in_car:
        # walk a bit more toward car and retry
        pg.keyboard.down("d"); pg.wait_for_timeout(500); pg.keyboard.up("d")
        pg.keyboard.press("e"); pg.wait_for_timeout(300)
        in_car = pg.evaluate("() => !!window.__game.player.inCar")
    check("enter car with E (steal)", in_car)
    check("stealing raises wanted >=1", pg.evaluate("() => window.__game.state.wanted >= 1"))
    pg.screenshot(path=f"{OUT}/03-in-car.png")

    # Drive forward a bit
    pg.keyboard.down("w"); pg.wait_for_timeout(1200); pg.keyboard.up("w")
    moved = pg.evaluate("() => ({x: window.__game.player.x, y: window.__game.player.y})")
    print("player after driving:", moved)

    # Mission 1: teleport car to delivery zone (test the trigger, not the drive)
    pg.evaluate("() => window.__game.teleport(1836, 1650)")
    pg.wait_for_timeout(500)
    check("mission 1 completes -> mission 2, cash $200",
          pg.evaluate("() => window.__game.state.mission === 1 && window.__game.state.cash === 200"))

    # Mission 2: collect 5 packages via teleport
    for pk in range(5):
        pg.evaluate(f"""() => {{
            const pk = window.__game.packages[{pk}];
            window.__game.teleport(pk.x, pk.y);
        }}""")
        pg.wait_for_timeout(250)
    check("mission 2 completes -> mission 3, cash $500",
          pg.evaluate("() => window.__game.state.mission === 2 && window.__game.state.cash === 500"))
    pg.wait_for_timeout(500)
    check("mission 3 starts with wanted 3",
          pg.evaluate("() => window.__game.state.wanted >= 3"))
    pg.screenshot(path=f"{OUT}/04-mission-3-wanted.png")

    # Pause test
    pg.keyboard.press("p"); pg.wait_for_timeout(200)
    check("pause with P shows pause screen", pg.is_visible("#pauseScreen"))
    pg.keyboard.press("p"); pg.wait_for_timeout(200)
    check("resume with P hides pause screen", not pg.is_visible("#pauseScreen"))

    # Mission 3: clear wanted via evaluate (simulate hiding long enough is slow;
    # verify the escape trigger by setting wanted 0 as the decay path would)
    pg.evaluate("() => { window.__game.state.wanted = 0; window.__game.police.length = 0; }")
    pg.wait_for_timeout(500)
    check("mission 3 completes on wanted 0 -> cash $1000, all done",
          pg.evaluate("() => window.__game.state.mission === 3 && window.__game.state.cash === 1000"))
    check("end screen shown", pg.is_visible("#endScreen"))
    pg.screenshot(path=f"{OUT}/05-all-missions-done.png")

    # Save/load: localStorage should hold cash 1000, mission 3
    saved = pg.evaluate("() => JSON.parse(localStorage.getItem('palmora-bay-save-v1'))")
    print("saved:", saved)
    check("localStorage save has cash 1000 + mission 3",
          saved and saved.get("cash") == 1000 and saved.get("mission") == 3)
    # Reload: save info should show
    pg.reload(); pg.wait_for_timeout(600)
    check("reload shows saved-game info",
          "Saved game found" in (pg.inner_text("#saveInfo") or ""))

    print("console/page errors:", errors)
    check("no JS errors during playtest", not errors)
    b.close()

fails = [n for n, ok in results if not ok]
print(f"\n{len(results)-len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
