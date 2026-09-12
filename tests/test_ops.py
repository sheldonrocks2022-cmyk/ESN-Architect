import os

from cogs.ops import Operations


def test_owner_ids_parsing(monkeypatch):
    monkeypatch.setenv("OWNER_IDS", "123, 456,invalid")
    # Avoid constructing a Discord bot; verify the parsing contract directly.
    class Dummy:
        pass
    cog = Operations(Dummy())
    assert cog.owner_ids() == {123, 456}


def test_missing_owner_ids_is_empty(monkeypatch):
    monkeypatch.delenv("OWNER_IDS", raising=False)
    class Dummy:
        pass
    assert Operations(Dummy()).owner_ids() == set()
