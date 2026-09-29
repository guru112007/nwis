import pytest
from app.engine.proximity import SubsurfaceProximityEngine

def test_haversine_distance():
    # Surface distance between two nearby coordinates in Assam (~1km apart)
    lat1, lon1 = 27.4850, 95.3400
    lat2, lon2 = 27.4900, 95.3450
    dist = SubsurfaceProximityEngine.haversine_distance_m(lat1, lon1, lat2, lon2)
    assert 600.0 < dist < 900.0

def test_3d_distance_calculation():
    active_pt = {'dx_north': 100.0, 'dy_east': 50.0, 'tvdss': 2000.0}
    offset_pt = {'dx_north': 120.0, 'dy_east': 50.0, 'tvdss': 2000.0}
    ref_surf = (27.485, 95.340)

    dist_3d = SubsurfaceProximityEngine.compute_3d_distance(
        active_point=active_pt, active_surface=ref_surf,
        offset_point=offset_pt, offset_surface=ref_surf,
        ref_surface=ref_surf
    )
    assert abs(dist_3d - 20.0) < 0.1 # 20m difference in north direction

def test_uncertainty_window():
    z_delta, win_str = SubsurfaceProximityEngine.calculate_uncertainty_window(
        target_tvdss=2400.0, dip_angle_deg=3.5, distance_between_wells_m=500.0
    )
    assert z_delta > 5.0
    assert "±" in win_str
