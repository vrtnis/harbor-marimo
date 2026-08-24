import json
from pathlib import Path
import tempfile
import unittest

from harbor_marimo.task_reviews import load_task_bundle, result_review_command
from harbor_marimo.tasks import TaskDraft, export_task_bundle


ROOT = Path(__file__).resolve().parents[1]


class TaskReviewHandoffTests(unittest.TestCase):
    def test_handoff_uses_profile_exported_from_same_task(self) -> None:
        draft_path = ROOT / "examples" / "science-task-authoring" / "draft.json"
        draft = TaskDraft.from_dict(json.loads(draft_path.read_text(encoding="utf-8")))
        with tempfile.TemporaryDirectory() as temp:
            task = Path(temp) / draft.task_name
            exported = export_task_bundle(draft, task, draft_root=draft_path.parent)
            bundle = load_task_bundle(task)

            command = result_review_command(bundle, Path(temp) / "harbor-job")

            self.assertEqual(
                command[1:3],
                ("review", str((Path(temp) / "harbor-job").resolve())),
            )
            self.assertEqual(
                Path(command[command.index("--profile") + 1]),
                exported.review_profile_path,
            )


if __name__ == "__main__":
    unittest.main()
