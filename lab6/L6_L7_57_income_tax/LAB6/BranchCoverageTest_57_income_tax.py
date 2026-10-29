import pytest
from income_tax import taxable_income, tax_due, refund_status


# taxable_income: income validation and regime branches
def test_negative_income():
    with pytest.raises(ValueError):
        taxable_income(-1, "new", 0)


def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000


def test_old_regime_below_investment_cap():
    assert taxable_income(500000, "old", 100000) == 350000


def test_old_regime_above_investment_cap():
    assert taxable_income(500000, "old", 200000) == 300000


def test_unknown_regime():
    with pytest.raises(ValueError):
        taxable_income(500000, "invalid", 0)


def test_taxable_income_negative_result():
    assert taxable_income(10000, "new", 0) == 0


def test_taxable_income_positive_result():
    assert taxable_income(200000, "new", 0) == 125000


# tax_due: age, exemption, and tax slab branches
def test_negative_taxable_amount():
    with pytest.raises(ValueError):
        tax_due(-1, 30)


def test_age_below_60():
    assert tax_due(600000, 30) == 32500


def test_age_60_to_79():
    assert tax_due(600000, 60) == 22500


def test_age_80_and_above():
    assert tax_due(600000, 80) == 5000


def test_taxable_amount_below_exemption():
    assert tax_due(200000, 30) == 0


def test_taxable_amount_equal_to_exemption():
    assert tax_due(250000, 30) == 0


def test_five_percent_slab_boundary():
    assert tax_due(500000, 30) == 12500


def test_twenty_percent_slab():
    assert tax_due(600000, 30) == 32500


# refund_status: all decision outcomes
def test_refund_on_time():
    assert refund_status(20000, 15000, True) == "refund"


def test_refund_late():
    assert refund_status(20000, 15000, False) == "refund delayed"


def test_balance_due_on_time():
    assert refund_status(10000, 15000, True) == "pay balance"


def test_balance_due_late():
    assert refund_status(10000, 15000, False) == "pay balance with penalty"


def test_exactly_settled():
    assert refund_status(15000, 15000, True) == "settled"