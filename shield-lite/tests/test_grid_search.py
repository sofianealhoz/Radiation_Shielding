import pytest
from shield_lite.optimization.grid_search import grid_search

def test_grid_search():
    order = ['lead', 'iron', 'water']
    ranges_mm = {
        'lead': '10,50',
        'iron': '5,30',
        'water': '20,100'
    }
    mu = {'lead': 0.1, 'iron': 0.2, 'water': 0.05}
    rho = {'lead': 11.34, 'iron': 7.87, 'water': 1.0}
    S = 1.0
    Dmax = 1.0
    area_m2 = 1.0
    topk = 5

    result = grid_search(order, ranges_mm, mu, rho, S, Dmax, area_m2, topk)

    assert isinstance(result, dict)
    assert 'thicknesses' in result
    assert 'dose' in result
    assert len(result['thicknesses']) <= topk