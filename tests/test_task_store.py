from pathlib import Path
import tempfile
import unittest

from harbor_marimo.tasks import ScientificBrief, TaskDraft, TaskDraftStore, TaskMetadata


class TaskDraftStoreTests(unittest.TestCase):
    def test_save_update_and_revision_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = TaskDraftStore(temp)
            draft = TaskDraft.create(
                task_name="scientific-task",
                metadata=TaskMetadata(author_name="Expert"),
                brief=ScientificBrief(title="Task", instruction="Produce the result."),
            )
            destination = store.save(draft)
            updated = draft.updated(brief=ScientificBrief(title="Task", instruction="Produce and validate the result."))
            store.save(updated)

            self.assertTrue(destination.is_file())
            self.assertEqual(store.get(draft.draft_id), updated)
            self.assertEqual(store.list(), (updated,))
            self.assertEqual(len(store.revisions(draft.draft_id)), 2)
            self.assertTrue(Path(temp).is_relative_to(Path(temp)))


if __name__ == "__main__":
    unittest.main()
