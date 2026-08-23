import unittest

from harbor_marimo.ui import trial_options, validate_review_submission


class ExpertUiTests(unittest.TestCase):
    def test_trial_options_do_not_expose_technical_trial_names(self) -> None:
        options = trial_options(
            [
                {"trial_id": "trial-1", "trial_name": "internal__name", "primary_reward": 1.0},
                {"trial_id": "trial-2", "trial_name": "other__name", "primary_reward": 0.0},
            ]
        )

        self.assertEqual(list(options), ["Attempt 1 · Verifier passed", "Attempt 2 · Expert attention"])

    def test_follow_up_verdict_requires_reviewer_rationale_and_action(self) -> None:
        errors = validate_review_submission(
            verdict="needs_follow_up",
            reviewer="",
            rationale="",
            follow_up="",
            criteria={"Convergence": ""},
        )

        self.assertEqual(len(errors), 5)


if __name__ == "__main__":
    unittest.main()
