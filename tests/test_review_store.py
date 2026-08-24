from pathlib import Path
import tempfile
import unittest

from acto.reviews import ExpertReview, JsonReviewStore


class JsonReviewStoreTests(unittest.TestCase):
    def test_save_is_a_round_trip_outside_the_harbor_job(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            job = root / "harbor-job"
            job.mkdir()
            store = JsonReviewStore(root / "reviews")
            review = ExpertReview.create(
                job_id="job/with/slashes",
                trial_id="trial-1",
                domain="financial",
                verdict="approve",
                note="Evidence aligns.",
            )

            destination = store.save(review)

            self.assertFalse(destination.is_relative_to(job))
            self.assertEqual(store.get(review.review_id), review)
            self.assertEqual(store.latest(job_id=review.job_id, trial_id="trial-1"), review)

    def test_saving_an_updated_review_replaces_the_same_record(self):
        with tempfile.TemporaryDirectory() as temp:
            store = JsonReviewStore(temp)
            review = ExpertReview.create(
                job_id="job-1",
                trial_id="trial-1",
                domain="science",
                verdict="needs_follow_up",
            )
            store.save(review)

            updated = review.updated(verdict="reject", note="Convergence failed.")
            store.save(updated)

            self.assertEqual(store.list(job_id="job-1"), (updated,))

    def test_malformed_sidecars_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            malformed = root / "job-1" / "trial-1" / "bad.json"
            malformed.parent.mkdir(parents=True)
            malformed.write_text("not json", encoding="utf-8")

            self.assertEqual(JsonReviewStore(root).list(), ())


if __name__ == "__main__":
    unittest.main()
