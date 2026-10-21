"""AppTest of one synthetic load. The baseline is not associated here."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "atlaspmo" / "ui" / "app.py"
FIXTURE = ROOT / "tests" / "fixtures" / "synthetic" / "minimal.xer"


def test_localhost_config_disables_usage_stats() -> None:
    text = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert 'address = "localhost"' in text
    assert "gatherUsageStats = false" in text


def test_load_run_and_show_approximations() -> None:
    app = AppTest.from_file(APP)
    app.run()
    assert app.exception == []
    joined = " ".join(item.value for item in app.caption)
    assert "baseline no se asocia" in joined
    app.file_uploader[0].upload("minimal.xer", FIXTURE.read_bytes()).run()
    assert app.exception == []
    assert any("actividades" in item.value for item in app.markdown)
    app.multiselect[0].set_value(["Calidad (DCMA y GAO)"]).run()
    app.button[0].click().run()
    assert app.exception == []
    assert app.subheader[0].value == "quality"
    assert len(app.caption) > 2
    assert len(app.download_button) == 1
