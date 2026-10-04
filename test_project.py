import unittest
import evaluation

class EvaluationTests(unittest.TestCase):
    def test_metrics_are_bounded(self):
        summary, _, agreement = evaluation.evaluate(evaluation.make_demo_judgments(n=80))
        self.assertTrue(summary["accuracy"].between(0, 1).all())
        self.assertGreater(agreement["cohen_kappa"], 0.5)

    def test_slices_and_paired_comparisons(self):
        judgments = evaluation.make_demo_judgments(n=80)
        quality = evaluation.validate_judgments(judgments)
        slices = evaluation.slice_scorecard(judgments)
        comparisons = evaluation.paired_model_differences(judgments, draws=200)
        self.assertTrue(quality["complete_model_item_matrix"])
        self.assertTrue(slices["accuracy"].between(0, 1).all())
        self.assertTrue((comparisons["ci_low"] <= comparisons["ci_high"]).all())

if __name__ == "__main__":
    unittest.main()
