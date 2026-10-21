"""AppTest of one synthetic load. The baseline is not associated here."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from test_cpm import _link, _load, _task

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
    joined = " ".join(item.value for item in app.caption)
    assert "no hay Gantt" in joined
    assert "No hay avance parcial" in joined
    assert any(item.label == "Resultados" for item in app.tabs)
    labels = {item.label for item in app.download_button}
    assert labels == {
        "Exportar Excel",
        "Exportar PDF",
        "Exportar Parquet",
        "Exportar manifiesto",
    }


def test_mode_b_shows_the_cpm_gantt(tmp_path: Path) -> None:
    _load(tmp_path, [_task("1", "A", "8"), _task("2", "B", "16")], [_link("1", "1", "2")])
    app = AppTest.from_file(APP)
    app.run()
    app.file_uploader[0].upload("chain.xer", (tmp_path / "case.xer").read_bytes()).run()
    app.multiselect[0].set_value(["Ruta crítica (modo B)"]).run()
    app.button[0].click().run()
    assert app.exception == []
    assert app.get("plotly_chart")
    assert "No recalcula fechas" in " ".join(item.value for item in app.caption)


def test_quality_profile_is_sent() -> None:
    app = AppTest.from_file(APP)
    app.run()
    app.selectbox[0].set_value("contratista").run()
    app.file_uploader[0].upload("minimal.xer", FIXTURE.read_bytes()).run()
    app.multiselect[0].set_value(["Calidad (DCMA y GAO)"]).run()
    app.button[0].click().run()
    assert app.exception == []
    joined = " ".join(item.value for item in app.caption)
    assert "Perfil registrado: contratista" in joined


def test_library_stores_the_quality_index(tmp_path: Path) -> None:
    app = AppTest.from_file(APP)
    app.run()
    app.file_uploader[0].upload("minimal.xer", FIXTURE.read_bytes()).run()
    app.multiselect[0].set_value(["Calidad (DCMA y GAO)"]).run()
    app.button[0].click().run()
    app.text_input[1].set_value(str(tmp_path / "lib.duckdb")).run()
    app.button[2].click().run()
    assert app.exception == []
    joined = " ".join(item.value for item in app.caption)
    assert "Puntos de quality_index: 1" in joined


def test_batch_ranks_one_synthetic(tmp_path: Path) -> None:
    (tmp_path / "minimal.xer").write_bytes(FIXTURE.read_bytes())
    app = AppTest.from_file(APP)
    app.run()
    app.text_input[0].set_value(str(tmp_path)).run()
    app.button[1].click().run()
    assert app.exception == []
    rendered = " ".join(str(item.value) for item in app.dataframe)
    assert "minimal.xer" in rendered
