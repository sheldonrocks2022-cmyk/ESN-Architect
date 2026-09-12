from cogs.server import TEMPLATES


def test_all_server_templates_have_channels_and_roles():
    assert set(TEMPLATES) == {"community", "gaming", "creator"}
    for template in TEMPLATES.values():
        assert template["categories"]
        assert template["roles"]
        assert all(channels for channels in template["categories"].values())


def test_templates_do_not_duplicate_category_names():
    for template in TEMPLATES.values():
        categories = list(template["categories"])
        assert len(categories) == len(set(categories))
