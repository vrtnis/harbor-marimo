from pathlib import Path
import tempfile
import unittest

from harbor_marimo.tasks import VerifierCheck, evaluate_checks


class DeclarativeVerifierTests(unittest.TestCase):
    def test_numeric_column_checks_distinguish_valid_and_invalid_results(self) -> None:
        checks = (
            VerifierCheck(
                id="chains-converged",
                type="column_max",
                artifact="posterior.csv",
                parameters={"column": "r_hat", "value": 1.01},
            ),
            VerifierCheck(
                id="enough-samples",
                type="column_min",
                artifact="posterior.csv",
                parameters={"column": "ess_bulk", "value": 1000},
            ),
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "posterior.csv"
            path.write_text(
                "parameter,r_hat,ess_bulk\nintercept,1.002,1800\nslope,1.015,900\n",
                encoding="utf-8",
            )

            results = evaluate_checks(temp, checks)

        self.assertEqual([item.passed for item in results], [False, False])
        self.assertEqual(results[0].actual, 1.015)

    def test_json_check_accepts_expected_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "convergence.json"
            path.write_text('{"converged": true}', encoding="utf-8")
            result = evaluate_checks(
                temp,
                (
                    VerifierCheck(
                        id="reported-convergence",
                        type="json_equals",
                        artifact=path.name,
                        parameters={"field": "converged", "value": True},
                    ),
                ),
            )[0]

        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
