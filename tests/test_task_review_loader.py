from pathlib import Path
import tempfile
import unittest

from harbor_marimo.task_reviews import load_task_bundle, read_task_evidence
from harbor_marimo.tasks import TaskDraft, export_task_bundle


ROOT = Path(__file__).resolve().parents[1]


class TaskReviewLoaderTests(unittest.TestCase):
    def test_loads_exported_task_without_executing_task_files(self) -> None:
        draft_path = ROOT / "examples" / "science-task-authoring" / "draft.json"
        draft = TaskDraft.from_dict(__import__("json").loads(draft_path.read_text(encoding="utf-8")))
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / draft.task_name
            export_task_bundle(draft, target, draft_root=draft_path.parent)

            bundle = load_task_bundle(target)

            self.assertEqual(bundle.task_author, draft.metadata.author_name)
            self.assertIn("Bayesian", bundle.instruction)
            self.assertTrue(any(item.path == "tests/test_verifier.py" for item in bundle.files))
            verifier = read_task_evidence(bundle, "tests-test_verifier.py")
            self.assertIn("CHECKS", verifier)
            evidence_keys = {item.key for item in bundle.evidence()}
            self.assertIn("instruction", evidence_keys)
            self.assertIn("solution-solve.sh", evidence_keys)
            self.assertIn("environment-Dockerfile", evidence_keys)

    def test_requires_standard_harbor_task_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                load_task_bundle(temp)


if __name__ == "__main__":
    unittest.main()
