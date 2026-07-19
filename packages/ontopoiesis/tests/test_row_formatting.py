from ontopoiesis.cli_ui import DEFAULT_MAX_ROWS, format_violation_rows


def test_format_violation_rows_uses_default_limit() -> None:
    # Distinctive uid values so the "hidden row" assertion cannot collide
    # with digits appearing elsewhere in the message (counts, limits).
    rows = [{"uid": f"row-{index}"} for index in range(DEFAULT_MAX_ROWS + 1)]

    rendered = format_violation_rows(rows)

    assert f"query returned {DEFAULT_MAX_ROWS + 1} violation row(s)" in rendered
    assert "1 more, run with -vv to show all" in rendered
    assert f"row-{DEFAULT_MAX_ROWS - 1}" in rendered
    assert f"row-{DEFAULT_MAX_ROWS}" not in rendered


def test_format_violation_rows_zero_limit_shows_verbosity_hint() -> None:
    rendered = format_violation_rows([{"uid": "row-broken"}], max_rows=0)

    assert "query returned 1 violation row(s)" in rendered
    assert "run with -v to see a sample" in rendered
    assert "row-broken" not in rendered


def test_format_violation_rows_without_limit_shows_all_rows() -> None:
    rendered = format_violation_rows([{"uid": "row-one"}, {"uid": "row-two"}], max_rows=None)

    assert "row-one" in rendered
    assert "row-two" in rendered
    assert "run with" not in rendered
