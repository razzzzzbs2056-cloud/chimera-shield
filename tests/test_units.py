"""Unit consistency."""
import pytest

from src.economic_model.units import Quantity, UnitError, convert_currency, parse_unit, sum_quantities


def test_scale_conversion_million_to_billion():
    assert Quantity(2500.0, "NPR_current_mn").to("NPR_current_bn").value == pytest.approx(2.5)


def test_nepali_numbering_crore_and_arba():
    assert Quantity(1.0, "NPR_current_arba").to("NPR_current_crore").value == pytest.approx(100.0)


def test_adding_across_scales_is_converted():
    total = Quantity(1.0, "USD_current_bn") + Quantity(500.0, "USD_current_mn")
    assert total.unit == "USD_current_bn" and total.value == pytest.approx(1.5)


@pytest.mark.parametrize("a,b", [
    ("NPR_current_mn", "USD_current_mn"),        # currency mismatch
    ("NPR_current_mn", "NPR_const2010_mn"),      # price-basis mismatch
    ("NPR_current_mn", "persons"),               # dimension mismatch
])
def test_incompatible_units_refuse_to_add(a, b):
    with pytest.raises(UnitError):
        Quantity(1.0, a) + Quantity(1.0, b)


def test_period_mismatch_refused():
    with pytest.raises(UnitError):
        Quantity(1.0, "USD_current", "2023") + Quantity(1.0, "USD_current", "2024")


def test_currency_conversion_both_quote_directions():
    npr = Quantity(1330.0, "NPR_current_bn", "2024")
    rate = Quantity(133.0, "NPR_per_USD", "2024")
    usd = convert_currency(npr, rate, "USD")
    assert usd.unit == "USD_current_bn" and usd.value == pytest.approx(10.0)
    back = convert_currency(usd, rate, "NPR")
    assert back.value == pytest.approx(1330.0)


def test_constant_price_conversion_refused():
    with pytest.raises(UnitError):
        convert_currency(Quantity(1.0, "NPR_const2010_bn"), Quantity(100.0, "NPR_per_USD"), "USD")


def test_rate_period_must_match_amount_period():
    with pytest.raises(UnitError):
        convert_currency(Quantity(1.0, "NPR_current", "2023"), Quantity(100.0, "NPR_per_USD", "2024"), "USD")


def test_unknown_unit_rejected():
    with pytest.raises(UnitError):
        parse_unit("dollars")


def test_sum_quantities():
    s = sum_quantities([Quantity(1, "USD_current_bn"), Quantity(2000, "USD_current_mn")], "USD_current_bn")
    assert s.value == pytest.approx(3.0)
