from pathlib import Path
import tempfile
import unittest

from harbor_marimo.tasks import ArtifactContract, ArtifactField, inspect_artifact_contract


class TaskArtifactContractTests(unittest.TestCase):
    def test_reports_missing_csv_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "results" / "posterior.csv"
            path.parent.mkdir()
            path.write_text("parameter,mean\nintercept,1.2\n", encoding="utf-8")
            contract = ArtifactContract(
                path="results/posterior.csv",
                format="csv",
                fields=(
                    ArtifactField("parameter"),
                    ArtifactField("r_hat", "number"),
                ),
            )

            issues = inspect_artifact_contract(root, contract)

        self.assertEqual([item.code for item in issues], ["missing_field"])
        self.assertIn("r_hat", issues[0].message)

    def test_accepts_matching_json_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "result.json"
            path.write_text('{"converged": true}', encoding="utf-8")

            issues = inspect_artifact_contract(
                root,
                ArtifactContract(
                    path="result.json",
                    format="json",
                    fields=(ArtifactField("converged", "boolean"),),
                ),
            )

        self.assertEqual(issues, ())


if __name__ == "__main__":
    unittest.main()
