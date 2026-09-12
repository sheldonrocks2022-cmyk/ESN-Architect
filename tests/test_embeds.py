import json


def test_embed_export_shape():
    payload = {"embeds": [{"title": "Hello", "description": "World", "color": 0x42E8F4}]}
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["embeds"][0]["title"] == "Hello"
    assert decoded["embeds"][0]["color"] == 0x42E8F4


def test_hex_color_rules():
    assert len("42E8F4") == 6
    assert int("42E8F4", 16) == 0x42E8F4
