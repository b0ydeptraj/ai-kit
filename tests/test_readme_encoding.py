from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SWITCHER = "[English](README.md) | [Tiếng Việt](README.vi.md)"
MOJIBAKE_MARKERS = ("Ã", "Â", "áº", "á»", "Ä", "Æ", "â€", "â†", "�")


def test_readmes_are_valid_utf8_without_bom_or_mojibake() -> None:
    for readme_name in ("README.md", "README.vi.md"):
        data = (ROOT / readme_name).read_bytes()
        text = data.decode("utf-8")
        first_line = text.splitlines()[0]

        assert not data.startswith(b"\xef\xbb\xbf"), readme_name
        assert first_line == EXPECTED_SWITCHER, readme_name
        assert not any(marker in text for marker in MOJIBAKE_MARKERS), readme_name
