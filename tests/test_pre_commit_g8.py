"""The commit hook runs G8 and stops on a failure."""

from __future__ import annotations

from scripts.hooks.pre_commit_g8 import main
from scripts.qa_gate import Control


def test_pre_commit_rejects_when_g8_fails(monkeypatch):
    monkeypatch.setattr(
        "scripts.hooks.pre_commit_g8.check_g8",
        lambda root: Control("G8", "fail", "leak"),
    )
    assert main() == 1


def test_pre_commit_accepts_when_g8_passes(monkeypatch):
    monkeypatch.setattr(
        "scripts.hooks.pre_commit_g8.check_g8",
        lambda root: Control("G8", "pass", "ok"),
    )
    assert main() == 0
