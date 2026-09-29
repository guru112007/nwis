import math
from typing import List, Dict, Tuple, Optional

class MinimumCurvatureMethod:
    """
    Directional survey calculation using Minimum Curvature Method (MCM).
    Handles edge case where dogleg angle beta approaches 0.
    """

    @staticmethod
    def calculate_dogleg_angle(inc1_deg: float, az1_deg: float, inc2_deg: float, az2_deg: float) -> float:
        """
        Calculate 3D dogleg angle beta in radians between two survey stations.
        """
        I1 = math.radians(inc1_deg)
        I2 = math.radians(inc2_deg)
        A1 = math.radians(az1_deg)
        A2 = math.radians(az2_deg)

        cos_beta = math.cos(I2 - I1) - (math.sin(I1) * math.sin(I2) * (1.0 - math.cos(A2 - A1)))
        # Clamp to [-1, 1] to prevent domain errors due to floating point precision
        cos_beta = max(-1.0, min(1.0, cos_beta))
        return math.acos(cos_beta)

    @classmethod
    def calculate_interval(
        cls,
        md1: float, inc1: float, az1: float,
        md2: float, inc2: float, az2: float
    ) -> Tuple[float, float, float]:
        """
        Calculate (delta_north, delta_east, delta_tvd) for an interval between two stations.
        """
        d_md = md2 - md1
        if d_md <= 0:
            return 0.0, 0.0, 0.0

        I1 = math.radians(inc1)
        I2 = math.radians(inc2)
        A1 = math.radians(az1)
        A2 = math.radians(az2)

        beta = cls.calculate_dogleg_angle(inc1, az1, inc2, az2)

        # Ratio factor Fc
        if abs(beta) < 1e-6:
            Fc = 1.0
        else:
            Fc = (2.0 / beta) * math.tan(beta / 2.0)

        d_north = (d_md / 2.0) * (math.sin(I1) * math.cos(A1) + math.sin(I2) * math.cos(A2)) * Fc
        d_east  = (d_md / 2.0) * (math.sin(I1) * math.sin(A1) + math.sin(I2) * math.sin(A2)) * Fc
        d_tvd   = (d_md / 2.0) * (math.cos(I1) + math.cos(I2)) * Fc

        return d_north, d_east, d_tvd

    @classmethod
    def compute_full_trajectory(cls, stations: List[Dict[str, float]], kb_elevation: float) -> List[Dict[str, float]]:
        """
        Computes TVD, TVDSS, North, East for a list of survey stations sorted by MD.
        Input station dict keys: 'md', 'inc', 'az'
        Returns list with keys: 'md', 'inc', 'az', 'tvd', 'tvdss', 'dx_north', 'dy_east'
        """
        if not stations:
            return []

        sorted_stations = sorted(stations, key=lambda s: s['md'])
        results = []

        # Base surface point at MD=0
        if sorted_stations[0]['md'] > 0:
            sorted_stations.insert(0, {'md': 0.0, 'inc': 0.0, 'az': 0.0})

        current_tvd = 0.0
        current_north = 0.0
        current_east = 0.0

        results.append({
            'md': sorted_stations[0]['md'],
            'inc': sorted_stations[0]['inc'],
            'az': sorted_stations[0]['az'],
            'tvd': 0.0,
            'tvdss': -kb_elevation, # TVDSS = TVD - KB
            'dx_north': 0.0,
            'dy_east': 0.0
        })

        for i in range(1, len(sorted_stations)):
            s1 = sorted_stations[i-1]
            s2 = sorted_stations[i]

            dn, de, dt = cls.calculate_interval(
                s1['md'], s1['inc'], s1['az'],
                s2['md'], s2['inc'], s2['az']
            )

            current_north += dn
            current_east += de
            current_tvd += dt
            tvdss = current_tvd - kb_elevation

            results.append({
                'md': s2['md'],
                'inc': s2['inc'],
                'az': s2['az'],
                'tvd': current_tvd,
                'tvdss': tvdss,
                'dx_north': current_north,
                'dy_east': current_east
            })

        return results

    @classmethod
    def interpolate_at_md(cls, computed_trajectory: List[Dict[str, float]], target_md: float) -> Dict[str, float]:
        """
        Linearly/MCM interpolates position parameters (TVD, TVDSS, Inc, Az, North, East)
        at exact target_md.
        """
        if not computed_trajectory:
            return {'md': target_md, 'tvd': 0.0, 'tvdss': 0.0, 'inc': 0.0, 'az': 0.0, 'dx_north': 0.0, 'dy_east': 0.0}

        if target_md <= computed_trajectory[0]['md']:
            return computed_trajectory[0]

        if target_md >= computed_trajectory[-1]['md']:
            return computed_trajectory[-1]

        # Find interval
        for i in range(1, len(computed_trajectory)):
            s1 = computed_trajectory[i-1]
            s2 = computed_trajectory[i]

            if s1['md'] <= target_md <= s2['md']:
                factor = (target_md - s1['md']) / (s2['md'] - s1['md']) if s2['md'] > s1['md'] else 0.0

                inc_interp = s1['inc'] + factor * (s2['inc'] - s1['inc'])
                az_interp = s1['az'] + factor * (s2['az'] - s1['az'])

                # MCM calculation for exact interpolation
                dn, de, dt = cls.calculate_interval(
                    s1['md'], s1['inc'], s1['az'],
                    target_md, inc_interp, az_interp
                )

                tvd = s1['tvd'] + dt
                tvdss = s1['tvdss'] + dt
                north = s1['dx_north'] + dn
                east = s1['dy_east'] + de

                return {
                    'md': target_md,
                    'inc': inc_interp,
                    'az': az_interp,
                    'tvd': tvd,
                    'tvdss': tvdss,
                    'dx_north': north,
                    'dy_east': east
                }

        return computed_trajectory[-1]
