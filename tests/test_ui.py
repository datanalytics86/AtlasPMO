"""Empty Streamlit shell."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_empty_selector_is_in_spanish():
    app = AppTest.from_file(ROOT / "src" / "atlaspmo" / "ui" / "app.py")
    app.run()
    assert app.title[0].value == "AtlasPMO"
    assert app.info[0].value == "El selector queda vacío hasta que haya módulos registrados."
    assert app.exception == []
