import unittest
import evaluation

class EvaluationTests(unittest.TestCase):
    def test_metrics_are_bounded(self):
        summary, _, agreement = evaluation.evaluate(evaluation.make_demo_judgments(n=80))
        self.assertTrue(summary["accuracy"].between(0, 1).all())
        self.assertGreater(agreement["cohen_kappa"], 0.5)

if __name__ == "__main__":
    unittest.main()
