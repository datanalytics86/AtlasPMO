"""The mutator kills a changed return and lets an equivalent comparison live."""

from __future__ import annotations

from pathlib import Path

from scripts.qa_sabotage import alcance_for, render_report, score_file


def test_sample_kills_a_return_and_keeps_an_equivalent_comparison(tmp_path: Path):
    module = tmp_path / "sample.py"
    module.write_text("def positive(n):\n    return n > 0\n", encoding="utf-8")
    test = tmp_path / "test_sample.py"
    test.write_text(
        "from sample import positive\n\n"
        "def test_positive():\n"
        "    assert positive(1) is True\n"
        "    assert positive(-1) is False\n",
        encoding="utf-8",
    )
    score = score_file(module, [test], limit=10)
    assert score.killed >= 1
    assert score.survived >= 1
    assert module.read_text(encoding="utf-8").startswith("def positive")
    report = render_report(score, module)
    assert "kill_score:" in report
    assert "alcance: muestra" in report
    full = render_report(score, module, alcance="completo", label="sample.py")
    assert "alcance: completo" in full
    assert "C:\\Users" not in full
    assert alcance_for(3, 3) == "completo"
    assert alcance_for(3, 2) == "muestra"
