"""
Playwright tests for the Joukowski Airfoil Potential Flow Visualizer.
Covers desktop layout, mobile layout, controls, and canvas rendering.
"""
import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:3001"

MOBILE_VIEWPORT = {"width": 390, "height": 844}   # iPhone 14-ish
DESKTOP_VIEWPORT = {"width": 1280, "height": 800}


# ---------------------------------------------------------------------------
# Desktop layout
# ---------------------------------------------------------------------------

def test_page_loads(page: Page):
    page.goto(BASE_URL)
    expect(page).to_have_title(re.compile("Joukowski", re.IGNORECASE))


def test_desktop_sidebar_visible(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    sidebar = page.locator("#sidebar")
    expect(sidebar).to_be_visible()


def test_desktop_menu_toggle_hidden(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    # Toggle button should be hidden on desktop
    toggle = page.locator("#menu-toggle")
    expect(toggle).to_be_hidden()


def test_desktop_canvas_visible(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    expect(page.locator("canvas#c")).to_be_visible()


def test_desktop_legend_visible(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    expect(page.locator("#legend")).to_be_visible()


# ---------------------------------------------------------------------------
# Desktop controls
# ---------------------------------------------------------------------------

def test_sliders_present(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    for slider_id in ["alpha", "uinf", "eps", "delta", "nparticles", "trail"]:
        expect(page.locator(f"#{ slider_id }")).to_be_visible()


def test_slider_value_display_updates(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    # Change angle of attack slider and verify display updates
    slider = page.locator("#alpha")
    slider.evaluate("el => { el.value = 10; el.dispatchEvent(new Event('input')); }")
    expect(page.locator("#v-alpha")).to_have_text("10°")


def test_pressure_button_toggles(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    btn = page.locator("#btn-pressure")
    expect(btn).to_have_class(re.compile("active"))
    btn.click()
    expect(btn).not_to_have_class(re.compile("active"))
    btn.click()
    expect(btn).to_have_class(re.compile("active"))


def test_static_lines_button_toggles(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    btn = page.locator("#btn-streamlines")
    expect(btn).not_to_have_class(re.compile("active"))
    btn.click()
    expect(btn).to_have_class(re.compile("active"))


def test_pause_button_toggles(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    btn = page.locator("#btn-pause")
    btn.click()
    expect(btn).to_have_text("Play")
    btn.click()
    expect(btn).to_have_text("Pause")


def test_info_panel_populated(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    # Wait for the animation loop to populate values
    page.wait_for_function("document.getElementById('d-gamma').textContent !== '—'")
    for field_id in ["d-gamma", "d-cl", "d-R", "d-beta"]:
        text = page.locator(f"#{field_id}").inner_text()
        assert text != "—", f"#{field_id} was not populated"


def test_fps_counter_updates(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    page.wait_for_function("document.getElementById('d-fps').textContent !== '—'", timeout=5000)
    fps_text = page.locator("#d-fps").inner_text()
    assert fps_text != "—"
    assert int(fps_text) > 0


# ---------------------------------------------------------------------------
# Mobile layout
# ---------------------------------------------------------------------------

def test_mobile_menu_toggle_visible(page: Page):
    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(BASE_URL)
    expect(page.locator("#menu-toggle")).to_be_visible()


def test_mobile_sidebar_hidden_by_default(page: Page):
    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(BASE_URL)
    # Sidebar should be translated off-screen (not visually visible)
    sidebar = page.locator("#sidebar")
    transform = sidebar.evaluate("el => getComputedStyle(el).transform")
    # translateY(100%) means it's off-screen
    assert transform != "none", "Sidebar should be transformed off-screen by default"
    assert not sidebar.is_visible(), "Sidebar should not be visible by default on mobile"


def test_mobile_toggle_opens_sidebar(page: Page):
    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(BASE_URL)
    toggle = page.locator("#menu-toggle")
    toggle.click()
    # After click sidebar should have 'open' class and be visible
    sidebar = page.locator("#sidebar")
    expect(sidebar).to_have_class(re.compile("open"))
    expect(sidebar).to_be_visible()


def test_mobile_toggle_label_changes(page: Page):
    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(BASE_URL)
    toggle = page.locator("#menu-toggle")
    expect(toggle).to_have_text("⚙ Controls")
    toggle.click()
    expect(toggle).to_have_text("✕ Close")
    toggle.click()
    expect(toggle).to_have_text("⚙ Controls")


def test_mobile_controls_accessible_after_open(page: Page):
    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(BASE_URL)
    page.locator("#menu-toggle").click()
    # All sliders should be interactable once sidebar is open
    for slider_id in ["alpha", "uinf", "eps", "delta"]:
        expect(page.locator(f"#{slider_id}")).to_be_visible()


def test_mobile_canvas_fills_screen(page: Page):
    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(BASE_URL)
    canvas = page.locator("canvas#c")
    box = canvas.bounding_box()
    assert box["width"] == pytest.approx(MOBILE_VIEWPORT["width"], abs=2)


# ---------------------------------------------------------------------------
# Canvas rendering
# ---------------------------------------------------------------------------

def test_canvas_draws_content(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    # Wait for a few frames then check canvas is non-blank
    page.wait_for_timeout(500)
    is_blank = page.evaluate("""() => {
        const c = document.getElementById('c');
        const ctx = c.getContext('2d');
        const data = ctx.getImageData(0, 0, c.width, c.height).data;
        return data.every(v => v === 0);
    }""")
    assert not is_blank, "Canvas should have drawn content"


def test_reset_button_works(page: Page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(BASE_URL)
    page.wait_for_timeout(300)
    page.locator("#btn-reset").click()
    # After reset the info panel should repopulate
    page.wait_for_function("document.getElementById('d-gamma').textContent !== '—'", timeout=3000)
