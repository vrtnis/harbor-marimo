import tempfile
import unittest

from acto.task_reviews import TaskReview, TaskReviewStore


class TaskReviewStoreTests(unittest.TestCase):
    def test_saves_independent_review_as_sidecar(self) -> None:
        review = TaskReview.create(
            task_name="posterior-check",
            task_author="Author",
            reviewer="Reviewer",
            reviewer_role="domain_reviewer",
            verdict="request_changes",
            conflict_declaration="No conflict",
        )
        with tempfile.TemporaryDirectory() as temp:
            store = TaskReviewStore(temp)

            destination = store.save(review)

            self.assertTrue(destination.is_file())
            self.assertEqual(store.list(task_name="posterior-check"), (review,))

    def test_store_refuses_author_approval(self) -> None:
        review = TaskReview.create(
            task_name="posterior-check",
            task_author="Author",
            reviewer="Author",
            reviewer_role="author_validation",
            verdict="approve",
            conflict_declaration="N/A",
        )
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "not independent approval"):
                TaskReviewStore(temp).save(review)


if __name__ == "__main__":
    unittest.main()
