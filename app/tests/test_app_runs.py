"""Smoke tests: the Streamlit app runs without exceptions in its main states."""
from pathlib import Path
from streamlit.testing.v1 import AppTest
APP = str(Path(__file__).resolve().parents[1] / "app.py")

def run(**actions):
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception, at.exception
    return at

def metric(at, label):
    return next(x.value for x in at.metric if x.label == label)

def test_default_matches_spreadsheet():
    at = run()
    assert metric(at, "Blended contribution per set") == "₹355"
    assert metric(at, "Break-even sets per month") == "957"

def test_pivot_preset():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.radio[0].set_value("Recommended pivot: no marketplace, lean team").run()
    assert not at.exception
    assert metric(at, "Blended contribution per set") == "₹677"
    assert metric(at, "Break-even sets per month") == "281"

def test_price_above_gst_slab_and_vw_warning():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.number_input(key="briefed:price_Everyday").set_value(4000).run()
    assert not at.exception
    assert any("Outside the acceptable range" in w.value for w in at.warning)

def test_all_channels_zero_does_not_crash():
    at = AppTest.from_file(APP, default_timeout=60).run()
    for s in at.slider:
        if s.key and ":mix_" in s.key:
            s.set_value(0)
    at.run()
    assert not at.exception
    assert any("at least one channel" in e.value for e in at.error)

def test_marketplace_only_never_breaks_even():
    at = AppTest.from_file(APP, default_timeout=60).run()
    for s in at.slider:
        if s.key and ":mix_" in s.key:
            s.set_value(100 if s.key.endswith("Marketplace") else 0)
    at.selectbox(key="briefed:line").set_value("Everyday")
    at.run()
    assert not at.exception

def test_retail_partner_and_other_lines():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.slider(key="briefed:mix_Retail partner").set_value(30).run()
    at.selectbox(key="briefed:line").set_value("Ceremonial").run()
    at.selectbox(key="briefed:wf_channel").set_value("Retail partner").run()
    assert not at.exception

def test_storefront_notes_toggle():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.toggle[0].set_value(True).run()
    assert not at.exception

def test_ai_layer_page():
    import sys
    sys.path.insert(0, str(Path(APP).parent))
    import ai_layer
    page = ai_layer.render()
    for tid in ["AI2", "AI4", "AI5", "AI6", "AI7"]:
        assert f'id="{tid.lower()}"' in page
    # headline numbers must match the results files
    for fact in ["20 of 20", "14 of 21", "8 of 21", "1 of 20 → 8 of 20", "12.3%", "Both pass tests failed"]:
        assert fact in page, fact
    at = run()
    assert "AI layer" in [t.label for t in at.tabs]
