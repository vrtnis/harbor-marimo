from pathlib import Path
import tomllib
import unittest

from harbor_marimo import load
from acto.domains.microarchitecture import (
    MicroarchitectureAdapter,
    microarchitecture_findings,
    microarchitecture_glossary,
    parse_microarchitecture_metrics,
    preview_microarchitecture_artifact,
)
from acto.profiles import load_review_profile


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "microarchitecture-modeling"
TASK = EXAMPLE / "microarch-modeling"
PROFILE = EXAMPLE / "microarch-modeling.review-profile.json"
JOB = EXAMPLE / "demo_data" / "harbor_job"


class MicroarchitectureDomainTests(unittest.TestCase):
    def test_pinned_task_remains_a_standard_harbor_task(self) -> None:
        config = tomllib.loads((TASK / "task.toml").read_text(encoding="utf-8"))

        self.assertEqual(config["schema_version"], "1.3")
        self.assertEqual(
            config["task"]["name"],
            "terminal-bench-science/microarch-modeling",
        )
        self.assertEqual(config["artifacts"], ["/root/model.onnx"])
        self.assertTrue((TASK / "environment" / "Dockerfile").is_file())
        self.assertTrue((TASK / "solution" / "solve.py").is_file())
        self.assertTrue((TASK / "tests" / "test_model.py").is_file())

    def test_profile_selects_microarchitecture_adapter(self) -> None:
        profile = load_review_profile(PROFILE)

        self.assertEqual(profile.domain_adapter, "microarchitecture")
        self.assertEqual(len(profile.acceptance_criteria), 5)
        self.assertIn("Top-1 normalized simple regret", profile.glossary)
        self.assertNotIn("R-hat", microarchitecture_glossary(profile))

    def test_parser_reads_python_or_json_metric_objects(self) -> None:
        metrics = parse_microarchitecture_metrics(
            "captured output: {'ipc_mape': 0.09, "
            "'mean_workload_kendall_tau': 0.625, 'top_1_regret': 0.0175}"
        )

        self.assertIsNotNone(metrics)
        self.assertAlmostEqual(metrics.ipc_mape or 0, 0.09)
        self.assertAlmostEqual(metrics.top_1_regret or 0, 0.0175)

    def test_adapter_applies_profile_to_reference_fixture(self) -> None:
        bundle = load(JOB)
        profile = load_review_profile(PROFILE)
        adapter = MicroarchitectureAdapter(profile)

        view = adapter.build_view(bundle, trial_id="microarchitecture-reference")

        self.assertTrue(adapter.supports(bundle))
        self.assertEqual(view.domain, "microarchitecture")
        self.assertEqual(view.title, "CPU Microarchitecture Model Evaluation")
        self.assertEqual(view.evidence[0].label, "IPC surrogate model")
        self.assertEqual(view.metadata["verifier_metrics"]["ipc_mape"], 0.0909)

    def test_stored_metrics_become_three_threshold_findings(self) -> None:
        findings = microarchitecture_findings(
            load(JOB), trial_id="microarchitecture-reference"
        )

        self.assertEqual(len(findings), 3)
        self.assertTrue(all(item.severity == "positive" for item in findings))
        self.assertIn("Workload ranking", {item.label.split(" meets")[0] for item in findings})

    def test_onnx_preview_hashes_but_does_not_load_the_graph(self) -> None:
        artifact = load(JOB).tables()["artifacts"][0]

        preview = preview_microarchitecture_artifact(artifact)

        self.assertEqual(preview.kind, "model")
        self.assertIn("SHA-256", preview.text or "")
        self.assertIn("does not load or execute", preview.text or "")


if __name__ == "__main__":
    unittest.main()
