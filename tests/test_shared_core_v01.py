import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from pui89_motorcycle.risk_baseline import classify_scenario
from pui89_motorcycle.shared_core_v01 import build_motorcycle_v01_records

class MotorcycleSharedCoreV01Tests(unittest.TestCase):
    def make_bundle(self):
        scenario = {
            "surface": "wet",
            "traction_estimate": 0.2,
            "visibility_m": 35,
            "obstacle_distance_m": 12,
            "observation_age_ms": 100,
        }
        result = classify_scenario(scenario)
        return build_motorcycle_v01_records(
            scenario_id="moto-synthetic-001",
            scenario_input=scenario,
            result=result,
            observed_at="2026-11-01T00:00:00Z",
            recorded_at="2026-11-01T00:00:01Z",
        )

    def test_maps_synthetic_result_to_advisory_contracts(self):
        bundle = self.make_bundle()
        self.assertEqual(bundle["observation"]["schema_version"], "0.1.0")
        self.assertEqual(bundle["observation"]["source"]["source_type"], "simulation")
        self.assertEqual(bundle["observation"]["quality"]["status"], "unknown")
        self.assertEqual(bundle["world_state"]["entities"][0]["state"]["state"], "WARNING")
        self.assertEqual(bundle["action_proposal"]["authority"]["mode"], "advisory_only")
        self.assertIs(bundle["action_proposal"]["authority"]["execution_authorized"], False)

    def test_rejects_non_synthetic_and_vehicle_control_output(self):
        scenario = {"surface":"dry"}
        result = classify_scenario(scenario)
        with self.assertRaises(ValueError):
            build_motorcycle_v01_records(scenario_id="x", scenario_input=scenario,
                                         result={**result, "source":"REAL_SENSOR"},
                                         observed_at="2026-11-01T00:00:00Z")
        with self.assertRaises(ValueError):
            build_motorcycle_v01_records(scenario_id="x", scenario_input=scenario,
                                         result={**result, "steering":0.1},
                                         observed_at="2026-11-01T00:00:00Z")


    def test_rejects_invalid_or_timezone_naive_timestamps(self):
        scenario = {"surface": "dry"}
        result = classify_scenario(scenario)
        for timestamp in ("", "not-a-time", "2026-11-01T00:00:00"):
            with self.subTest(timestamp=timestamp):
                with self.assertRaises(ValueError):
                    build_motorcycle_v01_records(
                        scenario_id="moto-invalid-time",
                        scenario_input=scenario,
                        result=result,
                        observed_at=timestamp,
                    )
        with self.assertRaises(ValueError):
            build_motorcycle_v01_records(
                scenario_id="moto-invalid-recorded-time",
                scenario_input=scenario,
                result=result,
                observed_at="2026-11-01T00:00:00Z",
                recorded_at="2026-11-01T00:00:01",
            )

    def test_rejects_non_advisory_authority_and_non_object_inputs(self):
        scenario = {"surface": "dry"}
        result = classify_scenario(scenario)
        with self.assertRaises(ValueError):
            build_motorcycle_v01_records(
                scenario_id="moto-invalid-authority",
                scenario_input=scenario,
                result={**result, "authority": "AUTONOMOUS_CONTROL"},
                observed_at="2026-11-01T00:00:00Z",
            )
        with self.assertRaises(ValueError):
            build_motorcycle_v01_records(
                scenario_id="moto-invalid-input",
                scenario_input=[],
                result=result,
                observed_at="2026-11-01T00:00:00Z",
            )
        with self.assertRaises(ValueError):
            build_motorcycle_v01_records(
                scenario_id="moto-invalid-result",
                scenario_input=scenario,
                result=[],
                observed_at="2026-11-01T00:00:00Z",
            )

    def test_output_records_never_contain_vehicle_control_fields(self):
        bundle = self.make_bundle()
        forbidden = {"throttle", "brake", "steering", "ignition"}

        def collect_keys(value):
            if isinstance(value, dict):
                keys = set(value)
                for nested in value.values():
                    keys.update(collect_keys(nested))
                return keys
            if isinstance(value, list):
                keys = set()
                for nested in value:
                    keys.update(collect_keys(nested))
                return keys
            return set()

        self.assertTrue(forbidden.isdisjoint(collect_keys(bundle)))

    def test_shared_core_schema_required_fields_match(self):
        schema_dir = ROOT / "schemas" / "v0.1"
        bundle = self.make_bundle()
        for key, filename in (
            ("observation","observation.schema.json"),
            ("world_state","world-state.schema.json"),
            ("action_proposal","action-proposal.schema.json"),
        ):
            schema = json.loads((schema_dir / filename).read_text(encoding="utf-8"))
            self.assertEqual(schema["properties"]["schema_version"]["const"], "0.1.0")
            self.assertTrue(set(schema["required"]).issubset(bundle[key].keys()))

if __name__ == "__main__":
    unittest.main()
