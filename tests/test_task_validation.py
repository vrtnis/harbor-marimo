from pathlib import Path
import unittest

from harbor_marimo.tasks import harbor_validation_plan


class HarborTaskValidationTests(unittest.TestCase):
    def test_plan_delegates_environment_and_agents_to_harbor(self) -> None:
        commands = harbor_validation_plan(
            Path("tasks") / "science-task",
            environment="coreweave",
            agents=(("research-agent", "openai/gpt-5.6"),),
        )

        self.assertEqual([item.kind for item in commands], ["oracle", "nop", "agent"])
        self.assertIn("coreweave", commands[0].argv)
        self.assertIn("oracle", commands[0].argv)
        self.assertIn("openai/gpt-5.6", commands[2].argv)


if __name__ == "__main__":
    unittest.main()
