import pandas as pd
import pytest

from athletic_pandas import algorithms


@pytest.fixture
def power():
    return pd.Series(range(100))

class TestAlgorithms:
    def test_mean_max_power(self, power):
        mmp = algorithms.mean_max_power(power)
        assert mmp.iloc[0] == 99.0
        assert mmp.iloc[10] == 94.0
        assert mmp.iloc[-1] == 49.5

    def test_mean_max_bests(self, power):
        bests = algorithms.mean_max_bests(power, 3, 3)

        assert len(bests) == 3
        assert isinstance(bests[0], algorithms.DataPoint)
        assert bests[0].index == 99
        assert bests[0].value == 98.0
        assert bests[2].index == 91
        assert bests[2].value == 90.0

    def test_weighted_average_power(self, power):
        wap = algorithms.weighted_average_power(power)

        assert wap == 59.45534981958064

    def test_power_per_kg(self, power):
        ppkg = algorithms.power_per_kg(power, 80.0)

        assert len(ppkg) == len(power)
        assert ppkg.iloc[0] == 0.0
        assert ppkg.iloc[50] == 0.625
        assert ppkg.iloc[-1] == 1.2375

    def test_tau_w_prime_balance(self, power):
        tau = algorithms._tau_w_prime_balance(power, cp=25)
        assert tau == 800.25855844756802

    def test_tau_w_prime_balance_with_untill(self, power):
        tau = algorithms._tau_w_prime_balance(power, cp=25, untill=15)
        assert tau == 825.08702566864781

    @pytest.mark.parametrize("test_input,expected", [
        (dict(tau_dynamic=False, tau_value=None), [800.25855844756802]*2),
        (dict(tau_dynamic=True, tau_value=None), [862.0, 800.25855844756802]),
        (dict(tau_dynamic=False, tau_value=100), [100, 100, 100]),
    ])
    def test_get_tau_method(self, power, test_input, expected):

        tau_method = algorithms._get_tau_method(power, cp=25, **test_input)
        assert tau_method(0) == expected[0]
        assert tau_method(99) == expected[1]

    @pytest.mark.parametrize("test_input,expected", [
        (dict(tau_dynamic=False, tau_value=None), 750.62138952915984),
        (dict(tau_dynamic=True, tau_value=None), 750.62138952915984),
        (dict(tau_dynamic=False, tau_value=100), 909.61894732869769),
    ])
    def test_w_prime_balance_waterworth(self, power, test_input, expected):
        w_bal = algorithms.w_prime_balance_waterworth(power, cp=25,
            w_prime=2000, **test_input)
        assert w_bal.iloc[75] == expected

    @pytest.mark.parametrize("test_input,expected", [
        (dict(tau_dynamic=False, tau_value=None), 800.6213895291603),
        (dict(tau_dynamic=True, tau_value=None), 800.6213895291603),
        (dict(tau_dynamic=False, tau_value=100), 959.61894732869769),
    ])
    def test_w_prime_balance_skiba(self, power, test_input, expected):
        w_bal = algorithms.w_prime_balance_skiba(power, cp=25,
            w_prime=2000, **test_input)
        assert w_bal.iloc[75] == expected

    def test_w_prime_balance_froncioni(self, power):
        w_bal = algorithms.w_prime_balance_froncioni(power, cp=25,
            w_prime=2000)
        assert w_bal.iloc[75] == 725.0

    @pytest.mark.parametrize("test_input,expected", [
        (dict(), 1678.2237332738489),
        (dict(algorithm='waterworth'), 1678.2237332738489),
        (dict(algorithm='waterworth', tau_value=500), 1680.1356439412966),
        (dict(algorithm='waterworth', tau_dynamic=True), 1678.2237332738489),
        (dict(algorithm='skiba'), 1703.2237332738489),
        (dict(algorithm='skiba', tau_value=500), 1705.1356439412966),
        (dict(algorithm='skiba', tau_dynamic=True), 1703.2237332738489),
        (dict(algorithm='froncioni'), 1675.0),
    ])
    def test_w_prime_balance(self, power, test_input, expected):
        w_bal = algorithms.w_prime_balance(power, cp=25, w_prime=2000,
            **test_input)
        assert w_bal.iloc[50] == expected
