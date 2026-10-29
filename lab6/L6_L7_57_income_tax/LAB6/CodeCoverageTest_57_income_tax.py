import pytest
from income_tax import taxable_income, tax_due, refund_status


def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000


def test_old_regime():
    assert taxable_income(500000, "old", 100000) == 350000


def test_old_regime_investment_cap():
    assert taxable_income(500000, "old", 200000) == 300000


def test_negative_gross_income():
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1, "new", 0)


def test_invalid_regime():
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "other", 0)


def test_negative_taxable_income_returns_zero():
    assert taxable_income(10000, "new", 0) == 0


def test_taxable_income_zero_boundary():
    assert taxable_income(75000, "new", 0) == 0


def test_tax_due_below_exemption():
    assert tax_due(200000, 30) == 0


def test_tax_due_at_exemption():
    assert tax_due(250000, 30) == 0


def test_tax_due_in_five_percent_slab():
    assert tax_due(400000, 30) == 7500


def test_tax_due_in_twenty_percent_slab():
    assert tax_due(600000, 30) == 32500


def test_negative_taxable_amount():
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-1, 30)


def test_refund():
    assert refund_status(20000, 15000, True) == "refund"


def test_delayed_refund():
    assert refund_status(20000, 15000, False) == "refund delayed"


def test_pay_balance():
    assert refund_status(10000, 15000, True) == "pay balance"


def test_pay_balance_with_penalty():
    assert refund_status(10000, 15000, False) == "pay balance with penalty"


def test_settled():
    assert refund_status(15000, 15000, True) == "settled"