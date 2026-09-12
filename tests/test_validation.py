from utils.validation import clean_csv, parse_hex_color, safe_slug, valid_http_url


def test_color():
    assert parse_hex_color("#42E8F4") == 0x42E8F4


def test_slug():
    assert safe_slug("My Cool Bot!") == "my-cool-bot"


def test_csv_limit():
    assert len(clean_csv(",".join(str(i) for i in range(30)), 15)) == 15


def test_url_validation():
    assert valid_http_url("https://example.com")
    assert not valid_http_url("javascript:alert(1)")
