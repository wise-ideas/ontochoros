from ontopoiesis.cli_ui import DEFAULT_MAX_ROWS, format_violation_rows


def test_format_violation_rows_uses_default_limit() -> None:
    rows = [{"uid": str(index)} for index in range(DEFAULT_MAX_ROWS + 1)]

    rendered = format_violation_rows(rows)

    assert "query returned 6 violation row(s)" in rendered
    assert "1 more, run with -vv to show all" in rendered
    assert "5" not in rendered


def test_format_violation_rows_zero_limit_shows_verbosity_hint() -> None:
    rendered = format_violation_rows([{"uid": "broken"}], max_rows=0)

    assert "query returned 1 violation row(s)" in rendered
    assert "run with -v to see a sample" in rendered
    assert "broken" not in rendered


def test_format_violation_rows_without_limit_shows_all_rows() -> None:
    rendered = format_violation_rows([{"uid": "one"}, {"uid": "two"}], max_rows=None)

    assert "one" in rendered
    assert "two" in rendered
    assert "run with" not in rendered
