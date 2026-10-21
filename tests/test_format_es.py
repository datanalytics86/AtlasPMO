"""es-CL formatting."""

from datetime import date

import pytest

from atlaspmo.ui.format_es import format_date, format_number


def test_thousands_and_decimal_comma():
    assert format_number(1234.5) == "1.234,50"
    assert format_number(1000000.5) == "1.000.000,50"


def test_negative_and_zero_decimals():
    assert format_number(-1234.5) == "-1.234,50"
    assert format_number(1234, decimals=0) == "1.234"


def test_date_is_day_month_year():
    assert format_date(date(2026, 10, 5)) == "05-10-2026"


def test_negative_decimals_rejected():
    with pytest.raises(ValueError, match="decimals"):
        format_number(1, decimals=-1)
