from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_language_switcher_is_valid_utf8_without_mojibake() -> None:
    data = (ROOT / "README.md").read_bytes()
    text = data.decode("utf-8")
    first_line = text.splitlines()[0]

    assert not data.startswith(b"\xef\xbb\xbf")
    assert first_line == "[English](README.md) | [Tiếng Việt](README.vi.md)"
    assert "Tiáº" not in text
