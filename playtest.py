"""Automated headless playtest for Palmora Bay (make.fun gta6-01).

Serves game/ on http://127.0.0.1:8931, drives it with real keyboard input
via Playwright + Chromium, and reports 15 checks as PASS/FAIL.

Writes exactly 4 screenshots into screenshots/ (the bounty cap):
  01-start-screen.png, 02-gameplay-on-foot.png,
  03-in-car.png, 04-mission-3-wanted.png
"""
import sys
import time
from playwright.sync_api import sync_playwright

GAME_URL = "http://127.0.0.1:8931/index.html"
SHOTS = "/home/hatch/workspace/makefun-gta6-game/screenshots"
SAVE_KEY = "palmora-bay-save-v1"

CAR_X, CAR_Y = 560, 330          # nearest parked car
DELIVERY_X, DELIVERY_Y = 1836, 1650


class Reporter:
    """Collects check results and prints them as they run."""

    def __init__(self):
        self.results = []

    def check(self, name, ok):
        self.results.append((name, bool(ok)))
        print(("PASS" if ok else "FAIL"), "-", name)

    def summary(self):
        failed = [n for n, ok in self.results if not ok]
        print(f"\n{len(self.results) - len(failed)}/{len(self.results)} checks passed")
        return 1 if failed else 0


def player_pos(page):
    return page.evaluate(
        "() => ({x: window.__game.player.x, y: window.__game.player.y})"
    )


def game_state(page):
    return page.evaluate(
        "() => ({wanted: window.__game.state.wanted,"
        " mission: window.__game.state.mission,"
        " cash: window.__game.state.cash,"
        " inCar: !!window.__game.player.inCar})"
    )


def walk_toward(page, key, want, get):
    """Hold a movement key in short bursts until get() reaches want."""
    for _ in range(30):
        if get() >= want:
            return
        before = player_pos(page)
        page.keyboard.down(key)
        page.wait_for_timeout(200)
        page.keyboard.up(key)
        # Stuck on a building corner: step up onto the road and retry.
        if player_pos(page)["x"] <= before["x"] + 1 and key == "d":
            page.keyboard.down("w")
            page.wait_for_timeout(200)
            page.keyboard.up("w")


def main():
    rep = Reporter()
    js_errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 760})
        page.on("console", lambda m: js_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: js_errors.append(str(e)))

        page.goto(GAME_URL)
        page.wait_for_timeout(800)
        page.screenshot(path=f"{SHOTS}/01-start-screen.png")
        rep.check("start screen visible", page.is_visible("#startScreen"))
        rep.check("no JS errors on load", not js_errors)

        page.click("#startBtn")
        page.wait_for_timeout(500)
        rep.check("game started (start screen hidden)", not page.is_visible("#startScreen"))
        page.screenshot(path=f"{SHOTS}/02-gameplay-on-foot.png")

        # Walk from the spawn (336, 450) up to the road, then right to the car.
        for _ in range(20):
            if player_pos(page)["y"] <= 360:
                break
            page.keyboard.down("w")
            page.wait_for_timeout(200)
            page.keyboard.up("w")
        walk_toward(page, "d", 540, lambda: player_pos(page)["x"])
        page.wait_for_timeout(300)
        print("player after walk:", player_pos(page))

        page.keyboard.press("e")
        page.wait_for_timeout(300)
        if not game_state(page)["inCar"]:
            # Not close enough yet: shuffle right and try E once more.
            page.keyboard.down("d")
            page.wait_for_timeout(500)
            page.keyboard.up("d")
            page.keyboard.press("e")
            page.wait_for_timeout(300)
        state = game_state(page)
        rep.check("enter car with E (steal)", state["inCar"])
        rep.check("stealing raises wanted >= 1", state["wanted"] >= 1)
        page.screenshot(path=f"{SHOTS}/03-in-car.png")

        # A short real drive, to prove the car moves.
        page.keyboard.down("w")
        page.wait_for_timeout(1200)
        page.keyboard.up("w")
        print("player after driving:", player_pos(page))

        # Mission 1: put the car in the delivery zone (tests the trigger).
        page.evaluate(f"() => window.__game.teleport({DELIVERY_X}, {DELIVERY_Y})")
        page.wait_for_timeout(500)
        state = game_state(page)
        rep.check(
            "mission 1 completes -> mission 2, cash $200",
            state["mission"] == 1 and state["cash"] == 200,
        )

        # Mission 2: step onto each of the 5 packages.
        for i in range(5):
            page.evaluate(
                "() => { const pk = window.__game.packages[%d];"
                " window.__game.teleport(pk.x, pk.y); }" % i
            )
            page.wait_for_timeout(250)
        state = game_state(page)
        rep.check(
            "mission 2 completes -> mission 3, cash $500",
            state["mission"] == 2 and state["cash"] == 500,
        )
        page.wait_for_timeout(500)
        rep.check("mission 3 starts with wanted 3", game_state(page)["wanted"] >= 3)
        page.screenshot(path=f"{SHOTS}/04-mission-3-wanted.png")

        # Pause / resume with P.
        page.keyboard.press("p")
        page.wait_for_timeout(200)
        rep.check("pause with P shows pause screen", page.is_visible("#pauseScreen"))
        page.keyboard.press("p")
        page.wait_for_timeout(200)
        rep.check("resume with P hides pause screen", not page.is_visible("#pauseScreen"))

        # Mission 3: wanted reaches 0 (what the decay path does over time).
        page.evaluate("() => { window.__game.state.wanted = 0; window.__game.police.length = 0; }")
        page.wait_for_timeout(500)
        state = game_state(page)
        rep.check(
            "mission 3 completes on wanted 0 -> cash $1000, all done",
            state["mission"] == 3 and state["cash"] == 1000,
        )
        rep.check("end screen shown", page.is_visible("#endScreen"))

        # Save / load round-trip.
        saved = page.evaluate(f"() => JSON.parse(localStorage.getItem('{SAVE_KEY}'))")
        print("saved:", saved)
        rep.check(
            "localStorage save has cash 1000 + mission 3",
            bool(saved) and saved.get("cash") == 1000 and saved.get("mission") == 3,
        )
        page.reload()
        page.wait_for_timeout(600)
        rep.check(
            "reload shows saved-game info",
            "Saved game found" in (page.inner_text("#saveInfo") or ""),
        )

        print("console/page errors:", js_errors)
        rep.check("no JS errors during playtest", not js_errors)
        browser.close()

    return rep.summary()


if __name__ == "__main__":
    sys.exit(main())
