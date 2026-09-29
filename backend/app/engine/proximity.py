import math
from typing import List, Dict, Optional, Tuple

class SubsurfaceProximityEngine:
    """
    Hybrid Spatial Engine:
    1. Surface Radius Coarse Filter (Haversine distance in meters between wellheads).
    2. True 3D Subsurface Downhole Clearance (3D Euclidean distance between trajectories at equivalent TVDSS).
    3. Structural dip angle uncertainty window predictor.
    """

    @staticmethod
    def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates surface distance in meters between two lat/lon points.
        """
        R = 6371000.0  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @staticmethod
    def latlon_to_meters(surface_lat: float, surface_lon: float, ref_lat: float, ref_lon: float) -> Tuple[float, float]:
        """
        Converts lat/lon to local cartesian coordinates (dx_north, dy_east) in meters relative to reference point.
        """
        dn = SubsurfaceProximityEngine.haversine_distance_m(ref_lat, ref_lon, surface_lat, ref_lon)
        if surface_lat < ref_lat:
            dn = -dn

        de = SubsurfaceProximityEngine.haversine_distance_m(ref_lat, ref_lon, ref_lat, surface_lon)
        if surface_lon < ref_lon:
            de = -de

        return dn, de

    @classmethod
    def compute_3d_distance(
        cls,
        active_point: Dict[str, float], active_surface: Tuple[float, float],
        offset_point: Dict[str, float], offset_surface: Tuple[float, float],
        ref_surface: Tuple[float, float]
    ) -> float:
        """
        Compute absolute 3D Euclidean distance in meters between active bit coordinate
        and an offset well coordinate.
        active_point has 'dx_north', 'dy_east', 'tvdss'
        active_surface is (lat, lon)
        """
        # Convert wellhead surface locations relative to ref_surface
        a_dn_surf, a_de_surf = cls.latlon_to_meters(active_surface[0], active_surface[1], ref_surface[0], ref_surface[1])
        o_dn_surf, o_de_surf = cls.latlon_to_meters(offset_surface[0], offset_surface[1], ref_surface[0], ref_surface[1])

        # Global North, East, TVDSS for active point
        a_N = a_dn_surf + active_point.get('dx_north', 0.0)
        a_E = a_de_surf + active_point.get('dy_east', 0.0)
        a_Z = active_point['tvdss']

        # Global North, East, TVDSS for offset point
        o_N = o_dn_surf + offset_point.get('dx_north', 0.0)
        o_E = o_de_surf + offset_point.get('dy_east', 0.0)
        o_Z = offset_point['tvdss']

        return math.sqrt((a_N - o_N)**2 + (a_E - o_E)**2 + (a_Z - o_Z)**2)

    @classmethod
    def calculate_uncertainty_window(
        cls,
        target_tvdss: float,
        dip_angle_deg: float = 3.5, # Typical Upper Assam shelf formation dip (~3.5 deg SE)
        distance_between_wells_m: float = 500.0
    ) -> Tuple[float, str]:
        """
        Calculates structural depth uncertainty z_delta (m) due to formation dip across offset distance.
        Returns (delta_z_m, formatted_window_str)
        """
        dip_rad = math.radians(dip_angle_deg)
        delta_z = abs(distance_between_wells_m * math.sin(dip_rad)) + 5.0 # 5m base tolerance
        
        window_str = f"±{delta_z:.1f} m (TVDSS: {target_tvdss - delta_z:.1f} to {target_tvdss + delta_z:.1f} m)"
        return delta_z, window_str
