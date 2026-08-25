import unittest

from acto.tasks import (
    ArtifactContract,
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    VerifierCheck,
    VerifierFixture,
)
from acto.ui import (
    card_style,
    compact_task_instruction,
    product_css,
    review_header_html,
    section_header_html,
    studio_progress_html,
    studio_summary_html,
)


class PresentationUiTests(unittest.TestCase):
    def test_shared_theme_is_restrained_and_responsive(self) -> None:
        css = product_css()

        self.assertIn("--acto-accent: #5654a6", css)
        self.assertIn("max-width: 1180px", css)
        self.assertIn("@media (max-width: 820px)", css)

    def test_progress_marks_only_one_current_step(self) -> None:
        progress = studio_progress_html(3)

        self.assertEqual(progress.count('class="acto-step current"'), 1)
        self.assertIn("Build acceptance checks", progress)
        self.assertEqual(progress.count("Complete"), 2)

    def test_summary_escapes_content_and_reports_readiness(self) -> None:
        draft = TaskDraft.create(
            task_name="safe-summary",
            metadata=TaskMetadata(author_name="Dr <Expert>", domain="statistics"),
            brief=ScientificBrief(
                title="Validate <posterior>",
                instruction="Fit the model.",
                research_context="Supports a scientific decision.",
            ),
            artifacts=(ArtifactContract(path="results/posterior.csv", format="csv"),),
            checks=(
                VerifierCheck(
                    id="result-exists",
                    type="file_exists",
                    artifact="results/posterior.csv",
                ),
            ),
            fixtures=(
                VerifierFixture(
                    name="Known good",
                    source="valid_output",
                    expected_pass=True,
                ),
            ),
        )

        summary = studio_summary_html(draft)

        self.assertIn("Validate &lt;posterior&gt;", summary)
        self.assertIn("Dr &lt;Expert&gt;", summary)
        self.assertIn("Ready for validation", summary)

    def test_headers_escape_dynamic_values(self) -> None:
        section = section_header_html(
            1,
            "Review <task>",
            "Check & cite",
            responsive_grid_item=True,
        )
        review = review_header_html(
            task_name="posterior <review>",
            author="Dr & Expert",
            domain="statistics",
            field="Bayesian inference",
            evidence_count=4,
            prior_review_count=0,
        )

        self.assertIn("Review &lt;task&gt;", section)
        self.assertIn("Check &amp; cite", section)
        self.assertIn("acto-review-grid-item", section)
        self.assertIn("posterior &lt;review&gt;", review)
        self.assertIn("Dr &amp; Expert", review)
        self.assertIn("Awaiting review", review)
        self.assertEqual(card_style()["background"], "#ffffff")

    def test_task_instruction_uses_compact_section_labels(self) -> None:
        instruction = "# Task title\n\n## Scientific context\n\nEvidence matters."

        compact = compact_task_instruction(instruction)

        self.assertNotIn("Task title", compact)
        self.assertIn("**Scientific context**", compact)
        self.assertIn("Evidence matters.", compact)


if __name__ == "__main__":
    unittest.main()
