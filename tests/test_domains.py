from pathlib import Path
import unittest

from acto.domains import DomainEvidence, DomainRegistry, DomainView
from acto.profiles import ReviewCriterion


class ExampleAdapter:
    name = "Example"
    label = "Example domain"

    def supports(self, bundle) -> bool:
        return True

    def build_view(self, bundle, *, trial_id=None) -> DomainView:
        return DomainView(
            domain=self.name.lower(),
            title=self.label,
            summary="Example summary",
            question="Is the output acceptable?",
            criteria=(ReviewCriterion(id="valid", label="Output is valid"),),
            evidence=(
                DomainEvidence(
                    key="artifact-1",
                    label="Output",
                    kind="file",
                    job_id="job-1",
                    trial_id=trial_id or "trial-1",
                    path=Path("output.txt"),
                    description="Primary output",
                    review_guidance="Check the contents.",
                    technical_label="workspace/output.txt",
                ),
            ),
        )


class DomainRegistryTests(unittest.TestCase):
    def test_adapter_lookup_is_case_insensitive(self):
        registry = DomainRegistry([ExampleAdapter()])

        self.assertEqual(registry.names(), ("example",))
        self.assertEqual(registry.get("EXAMPLE").label, "Example domain")

    def test_domain_view_carries_expert_guidance(self):
        view = ExampleAdapter().build_view(None)

        self.assertEqual(view.question, "Is the output acceptable?")
        self.assertEqual(view.criteria[0].id, "valid")
        self.assertEqual(view.evidence[0].technical_label, "workspace/output.txt")

    def test_duplicate_registration_requires_explicit_replacement(self):
        registry = DomainRegistry([ExampleAdapter()])

        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register(ExampleAdapter())

        registry.register(ExampleAdapter(), replace=True)

    def test_unknown_domain_lists_available_choices(self):
        registry = DomainRegistry([ExampleAdapter()])

        with self.assertRaisesRegex(KeyError, "example"):
            registry.get("science")


if __name__ == "__main__":
    unittest.main()
