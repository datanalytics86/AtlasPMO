"""pre-push accepts only origin and refs/heads/v2 or refs/heads/v3."""

from __future__ import annotations

from scripts.hooks.pre_push import main
from scripts.qa_gate import Control


def test_pre_push_rejects_a_foreign_remote(monkeypatch):
    monkeypatch.delenv("PRE_COMMIT_REMOTE_NAME", raising=False)
    monkeypatch.delenv("PRE_COMMIT_REMOTE_BRANCH", raising=False)
    code = main(["pre_push.py", "upstream"], "local sha refs/heads/v2 0")
    assert code == 1


def test_pre_push_rejects_another_branch(monkeypatch):
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/main")
    assert main(["pre_push.py"]) == 1


def test_pre_push_rejects_when_g8_fails(monkeypatch):
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/v2")
    monkeypatch.setattr(
        "scripts.hooks.pre_push.check_g8",
        lambda root: Control("G8", "fail", "leak"),
    )
    assert main(["pre_push.py"]) == 1


def test_pre_push_accepts_origin_v2(monkeypatch):
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/v2")
    monkeypatch.setattr(
        "scripts.hooks.pre_push.check_g8",
        lambda root: Control("G8", "pass", "ok"),
    )
    assert main(["pre_push.py"]) == 0


def test_pre_push_accepts_origin_v3(monkeypatch):
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/v3")
    monkeypatch.setattr(
        "scripts.hooks.pre_push.check_g8",
        lambda root: Control("G8", "pass", "ok"),
    )
    assert main(["pre_push.py"]) == 0
