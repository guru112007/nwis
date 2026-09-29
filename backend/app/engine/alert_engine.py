import math
from typing import List, Dict, Any, Optional
from app.config import ALERTS_CONFIG, STRATIGRAPHY_CONFIG
from app.engine.proximity import SubsurfaceProximityEngine

class LookAheadAlertEngine:
    """
    3-Tier Look-Ahead Alert Engine for active drilling:
    - L1 Advisory: 50 - 100 m ahead of bit
    - L2 Corridor Warning: 15 - 50 m ahead of bit
    - L3 Critical: 0 - 15 m ahead of bit or real-time anomaly
    """

    def __init__(self):
        self.playbooks = ALERTS_CONFIG.get("playbooks", {})
        self.thresholds = ALERTS_CONFIG.get("tier_thresholds", {
            "L1_advisory_m": 100.0,
            "L2_warning_m": 50.0,
            "L3_critical_m": 15.0
        })

    def get_tier(self, distance_m: float) -> Optional[str]:
        if distance_m <= self.thresholds["L3_critical_m"]:
            return "L3"
        elif distance_m <= self.thresholds["L2_warning_m"]:
            return "L2"
        elif distance_m <= self.thresholds["L1_advisory_m"]:
            return "L1"
        return None

    def calculate_heuristic_risk_score(self, distance_m: float, severity: str, occurrence_count: int = 1) -> float:
        """
        Offset-derived heuristic risk score (0 to 100):
        Distance weight (exponential decay) + Severity base weight + Recurrence count weight.
        """
        severity_weights = {"L1": 30.0, "L2": 60.0, "L3": 90.0}
        base_weight = severity_weights.get(severity, 40.0)

        # Distance decay factor: 1.0 at 0m, ~0.13 at 100m
        distance_decay = math.exp(-distance_m / 50.0)

        # Multi-occurrence boost (max +20 points)
        occurrence_boost = min(20.0, (occurrence_count - 1) * 10.0)

        raw_score = (base_weight * distance_decay) + occurrence_boost
        return round(min(100.0, max(5.0, raw_score)), 1)

    def get_playbook_recommendation(self, category_key: str, tier: str) -> str:
        """
        Retrieves recommended mitigation from playbooks in alerts.yaml.
        """
        category_map = {
            "Severe Mud Loss": "MUD_LOSS",
            "Differential Pipe Sticking": "STUCK_PIPE",
            "Gas Influx / Well Control": "GAS_KICK",
            "Sloughing Shale / Hole Collapse": "WELLBORE_INSTABILITY"
        }
        key = category_map.get(category_key, "STUCK_PIPE")
        pb = self.playbooks.get(key, {})
        return pb.get(tier, "Follow standard well operating procedures and notify driller.")

    def evaluate_active_bit(
        self,
        active_well: Dict[str, Any],
        active_bit_md: float,
        active_bit_tvdss: float,
        current_formation: str,
        offset_wells: List[Dict[str, Any]],
        offset_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluates upcoming offset events ahead of the active bit position.
        Returns list of structured look-ahead alert dictionaries.
        """
        alerts = []
        active_surf = (active_well["surface_lat"], active_well["surface_lon"])

        for event in offset_events:
            offset_well_id = event["well_id"]
            offset_well = next((w for w in offset_wells if w["id"] == offset_well_id), None)
            if not offset_well:
                continue

            offset_surf = (offset_well["surface_lat"], offset_well["surface_lon"])

            # 1. Surface Distance Coarse Filter (Max 5000m radius)
            surface_dist = SubsurfaceProximityEngine.haversine_distance_m(
                active_surf[0], active_surf[1], offset_surf[0], offset_surf[1]
            )
            if surface_dist > 5000.0:
                continue

            # 2. Downhole TVDSS depth distance to event horizon
            event_tvdss = event["tvdss"]
            tvdss_distance_ahead = event_tvdss - active_bit_tvdss

            # We are interested in events that lie ahead of the bit (0 to 100m ahead)
            if 0.0 <= tvdss_distance_ahead <= self.thresholds["L1_advisory_m"]:
                tier = self.get_tier(tvdss_distance_ahead)
                if not tier:
                    continue

                # Compute uncertainty window considering formation dip
                delta_z, uncertainty_str = SubsurfaceProximityEngine.calculate_uncertainty_window(
                    target_tvdss=event_tvdss,
                    dip_angle_deg=3.5,
                    distance_between_wells_m=surface_dist
                )

                risk_score = self.calculate_heuristic_risk_score(
                    distance_m=tvdss_distance_ahead,
                    severity=event.get("severity", tier)
                )

                playbook = self.get_playbook_recommendation(
                    category_key=event["event_category"],
                    tier=tier
                )

                alert_id = f"ALERT-{active_well['id']}-{event['id']}-{int(active_bit_md)}"

                alerts.append({
                    "alert_id": alert_id,
                    "tier": tier,
                    "distance_to_event_m": round(tvdss_distance_ahead, 1),
                    "uncertainty_window_m": uncertainty_str,
                    "active_well_id": active_well["id"],
                    "active_md_m": round(active_bit_md, 1),
                    "active_tvdss_m": round(active_bit_tvdss, 1),
                    "target_formation": event.get("formation", current_formation),
                    "offset_well_id": offset_well_id,
                    "offset_event_id": event["id"],
                    "event_category": event["event_category"],
                    "historical_summary": event["summary"],
                    "mitigation_applied": event["mitigation"],
                    "playbook_recommendation": playbook,
                    "heuristic_risk_score": risk_score,
                    "source_file": event["source_file"],
                    "source_page": event["source_page"],
                    "bbox": event.get("bbox", [100, 150, 500, 300]),
                    "doc_hash": event["doc_hash"],
                    "verified_by_human": event.get("verified_by_human", True),
                    "ocr_confidence": event.get("ocr_confidence", 0.98)
                })

        # Sort alerts by severity tier (L3 -> L2 -> L1) and proximity distance
        tier_rank = {"L3": 1, "L2": 2, "L1": 3}
        alerts.sort(key=lambda a: (tier_rank[a["tier"]], a["distance_to_event_m"]))
        return alerts
