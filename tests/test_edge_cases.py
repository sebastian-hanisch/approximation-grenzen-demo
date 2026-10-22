"""Randfälle auf App-Ebene: jede Reglerkombination an den Grenzen liefert eine geprüfte Analyse (keine Fehlermeldung der Prüfungen vor der Anzeige)."""

import pytest

import apx_constants as C
import apx_evaluation as ev


@pytest.mark.parametrize("family", list(C.FAMILIES))
@pytest.mark.parametrize("n", [C.N_MIN, 8, C.N_MAX])
def test_extremes_of_the_point_sliders_are_clean(family, n):
    a = ev.analyse(ev.Settings(n=n, family=family))
    assert ev.validation_errors(a) == []
    assert a.opt.cost > 0 and a.chr.cost >= a.opt.cost - 1e-9


@pytest.mark.parametrize("seed", [0, C.SEED_MAX])
def test_seed_bounds(seed):
    assert ev.validation_errors(ev.analyse(ev.Settings(seed=seed))) == []


@pytest.mark.parametrize("rho", C.RHO_OPTIONS)
@pytest.mark.parametrize("p", [C.P_OPTIONS[0], C.P_OPTIONS[-1]])
def test_extremes_of_the_reduction_controls_are_clean(rho, p):
    a = ev.analyse(ev.Settings(rho=rho, p=p))
    assert ev.validation_errors(a) == []
    assert all(r.agrees for r in a.reduction)


@pytest.mark.parametrize("m", [C.M_OPTIONS[0], 2, C.M_OPTIONS[-1]])
def test_extremes_of_m_keep_the_optimum_equal_to_n(m):
    a = ev.analyse(ev.Settings(m=m))
    assert ev.validation_errors(a) == []
    assert all(c >= a.settings.n - 1e-9 for c in a.planted_costs.values())
    if m == 1:                                                                        # alle Kosten 1: jeder Rundweg kostet n
        assert all(abs(c - a.settings.n) < 1e-9 for c in a.planted_costs.values())


def test_the_maximum_instance_has_the_documented_table_size():
    a = ev.analyse(ev.Settings(n=C.N_MAX))
    assert a.opt.cells == 13 * 2 ** 13 == 106496
