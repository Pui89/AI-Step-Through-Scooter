"""Regression tests for synthetic motorcycle scenarios only."""
import json
import unittest
from pathlib import Path
from pui89_motorcycle.risk_baseline import classify_scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILE = ROOT / "docs" / "simulation" / "MOTORCYCLE_RISK_SCENARIOS.json"

class MotorcycleScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))["scenarios"]

    def test_expected_states_and_advisory_only_authority(self):
        self.assertGreaterEqual(len(self.scenarios), 10)
        for item in self.scenarios:
            with self.subTest(scenario=item["id"]):
                result = classify_scenario(item["input"])
                self.assertEqual(result["state"], item["expected"])
                self.assertEqual(result["authority"], "ADVISORY_ONLY_NO_ACTUATION")
                self.assertEqual(result["source"], "SYNTHETIC_TEST_INPUT")

    def test_scenario_ids_are_unique(self):
        ids = [item["id"] for item in self.scenarios]
        self.assertEqual(len(ids), len(set(ids)))

    def test_missing_input_degrades(self):
        self.assertEqual(classify_scenario({"surface":"dry"})["state"], "UNKNOWN_DEGRADED")

    def test_no_vehicle_control_fields_are_returned(self):
        for item in self.scenarios:
            result = classify_scenario(item["input"])
            for key in ("throttle", "brake", "steering", "ignition"):
                self.assertNotIn(key, result)


    def test_non_object_observations_degrade_without_exception(self):
        for observation in (None, [], "invalid", 42):
            with self.subTest(observation=observation):
                result = classify_scenario(observation)
                self.assertEqual(result["state"], "UNKNOWN_DEGRADED")
                self.assertEqual(result["authority"], "ADVISORY_ONLY_NO_ACTUATION")

    def test_non_string_surface_degrades_without_exception(self):
        scenario = {
            "surface": ["dry"],
            "traction_estimate": 0.8,
            "visibility_m": 100,
            "obstacle_distance_m": 50,
            "observation_age_ms": 100,
        }
        self.assertEqual(classify_scenario(scenario)["state"], "UNKNOWN_DEGRADED")

    def test_non_finite_numeric_values_degrade(self):
        base = {
            "surface": "dry",
            "traction_estimate": 0.8,
            "visibility_m": 100,
            "obstacle_distance_m": 50,
            "observation_age_ms": 100,
        }
        for field in ("traction_estimate", "visibility_m", "obstacle_distance_m", "observation_age_ms"):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, value=value):
                    result = classify_scenario({**base, field: value})
                    self.assertEqual(result["state"], "UNKNOWN_DEGRADED")
                    self.assertEqual(result["evidence_flags"], [field])

    def test_boolean_numeric_values_degrade(self):
        base = {
            "surface": "dry",
            "traction_estimate": 0.8,
            "visibility_m": 100,
            "obstacle_distance_m": 50,
            "observation_age_ms": 100,
        }
        for field in ("traction_estimate", "visibility_m", "obstacle_distance_m", "observation_age_ms"):
            with self.subTest(field=field):
                self.assertEqual(classify_scenario({**base, field: True})["state"], "UNKNOWN_DEGRADED")

    def test_synthetic_threshold_boundaries_are_deterministic(self):
        base = {
            "surface": "dry",
            "traction_estimate": 0.8,
            "visibility_m": 100,
            "obstacle_distance_m": 50,
            "observation_age_ms": 100,
        }
        cases = (
            ({"obstacle_distance_m": 5}, "CRITICAL"),
            ({"obstacle_distance_m": 5.001}, "WARNING"),
            ({"traction_estimate": 0.1}, "CRITICAL"),
            ({"traction_estimate": 0.1001}, "WARNING"),
            ({"observation_age_ms": 1000}, "NORMAL"),
            ({"observation_age_ms": 1000.001}, "UNKNOWN_DEGRADED"),
            ({"visibility_m": 50}, "NORMAL"),
            ({"visibility_m": 49.999}, "ADVISORY"),
        )
        for overrides, expected in cases:
            with self.subTest(overrides=overrides):
                self.assertEqual(classify_scenario({**base, **overrides})["state"], expected)

if __name__ == "__main__":
    unittest.main()
