import pytest
import math
from app.engine.mcm import MinimumCurvatureMethod

def test_mcm_vertical_well():
    """
    Test purely vertical well (0 deg inclination).
    MCM should yield exact TVD = MD and North/East = 0.
    """
    stations = [
        {'md': 0.0, 'inc': 0.0, 'az': 0.0},
        {'md': 1000.0, 'inc': 0.0, 'az': 0.0},
        {'md': 2000.0, 'inc': 0.0, 'az': 0.0}
    ]
    trajectory = MinimumCurvatureMethod.compute_full_trajectory(stations, kb_elevation=100.0)
    assert len(trajectory) == 3
    assert trajectory[0]['tvd'] == 0.0
    assert trajectory[1]['tvd'] == 1000.0
    assert trajectory[1]['tvdss'] == 900.0 # TVDSS = 1000 - 100
    assert trajectory[2]['tvd'] == 2000.0
    assert abs(trajectory[2]['dx_north']) < 1e-5
    assert abs(trajectory[2]['dy_east']) < 1e-5

def test_mcm_ratio_factor_zero_dogleg():
    """
    Test zero dogleg angle (beta -> 0).
    Ratio factor Fc should gracefully handle division by zero.
    """
    dn, de, dt = MinimumCurvatureMethod.calculate_interval(
        md1=0.0, inc1=10.0, az1=45.0,
        md2=100.0, inc2=10.0, az2=45.0
    )
    assert dt > 0
    assert dn > 0
    assert de > 0

def test_mcm_interpolation():
    stations = [
        {'md': 0.0, 'inc': 0.0, 'az': 0.0},
        {'md': 1000.0, 'inc': 30.0, 'az': 90.0}
    ]
    trajectory = MinimumCurvatureMethod.compute_full_trajectory(stations, kb_elevation=50.0)
    interp = MinimumCurvatureMethod.interpolate_at_md(trajectory, target_md=500.0)
    assert interp['md'] == 500.0
    assert 0.0 < interp['tvd'] < 500.0
    assert interp['dy_east'] > 0.0
