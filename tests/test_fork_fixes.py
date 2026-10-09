"""Regression tests for the fitzyracing-rouge fork (360 Bench).

The first group fails on rouge 1.0.1 and passes on the fork. The second group pins behaviour
that must stay exactly as in 1.0.1.
"""
import os
import tempfile
from unittest import TestCase

from rouge import FilesRouge, Rouge

METRICS = ["rouge-1", "rouge-2", "rouge-3", "rouge-l"]
ZERO = {"r": 0.0, "p": 0.0, "f": 0.0}


class WhitespaceSegmentTest(TestCase):
    """Upstream #77 / PR #78: a whitespace-only segment between periods became a '' token."""

    def test_disjoint_texts_with_blank_segment_score_zero(self):
        # 1.0.1: rouge-1 f = 0.25 although the texts share no word.
        scores = Rouge(metrics=METRICS).get_scores("the cat. . dog", "a bird. . fish")[0]
        for metric in METRICS:
            self.assertEqual(scores[metric], ZERO, metric)

    def test_trailing_space_after_period_scores_zero(self):
        # 1.0.1: rouge-1 f = 0.5 for 'cat. ' vs 'dog. '.
        scores = Rouge().get_scores("cat. ", "dog. ")[0]
        for metric in Rouge.DEFAULT_METRICS:
            self.assertEqual(scores[metric], ZERO, metric)

    def test_blank_hypothesis_does_not_match_blank_segment_in_reference(self):
        # An empty LLM generation used to share the '' token with a reference that has a
        # space after its final period.
        scores = Rouge().get_scores(" ", "The cat sat. ")[0]
        for metric in Rouge.DEFAULT_METRICS:
            self.assertEqual(scores[metric], ZERO, metric)

    def test_raw_overlap_has_no_empty_token(self):
        scores = Rouge(raw_results=True).get_scores("cat. ", "dog. ")[0]
        for metric in Rouge.DEFAULT_METRICS:
            self.assertEqual(scores[metric]["overlap"], 0, metric)
        self.assertEqual(scores["rouge-1"]["hyp"], 1)
        self.assertEqual(scores["rouge-1"]["ref"], 1)

    def test_blank_segments_do_not_change_scores(self):
        cases = [
            ("the cat sat on the mat", "the cat was on the mat"),
            ("the cat sat. the dog ran", "a cat sat. the dog ran away"),
            ("cat", "dog"),
        ]
        for exclusive in (True, False):
            for avg in (False, True):
                scorer = Rouge(metrics=METRICS, exclusive=exclusive, return_lengths=True)
                for hyp, ref in cases:
                    expected = scorer.get_scores(hyp, ref, avg=avg)
                    for pad in (". ", ".\t.\n", ".\u00a0", ". . "):
                        self.assertEqual(scorer.get_scores(hyp + pad, ref, avg=avg), expected)
                        self.assertEqual(scorer.get_scores(hyp, ref + pad, avg=avg), expected)
                        self.assertEqual(scorer.get_scores(hyp + pad, ref + pad, avg=avg), expected)

    def test_files_rouge_with_trailing_whitespace(self):
        with tempfile.TemporaryDirectory() as d:
            hyp_path = os.path.join(d, "hyp.txt")
            ref_path = os.path.join(d, "ref.txt")
            with open(hyp_path, "w") as f:
                f.write("cat. \n")
            with open(ref_path, "w") as f:
                f.write("dog. \t\n")
            for avg in (False, True):
                self.assertEqual(FilesRouge().get_scores(hyp_path, ref_path, avg=avg),
                                 Rouge().get_scores("cat", "dog", avg=avg))


class LongSentenceTest(TestCase):
    """Upstream PR #69 (merged on master, never released): RecursionError in ROUGE-L."""

    def test_rouge_l_long_sentence_no_recursion_error(self):
        words = " ".join("w%d" % (i % 50) for i in range(3000))
        scores = Rouge(metrics=["rouge-l"]).get_scores(words, words)[0]["rouge-l"]
        self.assertAlmostEqual(scores["f"], 1.0, places=6)


class UnchangedBehaviourTest(TestCase):
    """These pass on rouge 1.0.1 too and must keep passing."""

    def test_pinned_scores_from_1_0_1(self):
        scores = Rouge().get_scores(
            "the cat was found under the bed. it was asleep",
            "the cat was under the bed. the cat slept")[0]
        self.assertEqual(scores, PINNED)

    def test_whitespace_only_text_is_scored_as_before(self):
        # Not an error (unlike ""), so evaluation loops over model outputs keep running.
        self.assertEqual(Rouge().get_scores(" ", "cat")[0]["rouge-1"], ZERO)
        self.assertEqual(Rouge().get_scores(" . ", "cat")[0]["rouge-1"], ZERO)
        self.assertAlmostEqual(Rouge().get_scores(" ", " ")[0]["rouge-1"]["f"], 1.0, places=6)

    def test_empty_text_still_raises(self):
        for hyp, ref in (("", "cat"), (".", "cat")):
            with self.assertRaises(ValueError):
                Rouge().get_scores(hyp, ref)
        with self.assertRaises(ValueError):
            Rouge().get_scores("cat", "")


PINNED = {
    "rouge-1": {"r": 0.8333333333333334, "p": 0.625, "f": 0.7142857093877552},
    "rouge-2": {"r": 0.5714285714285714, "p": 0.4444444444444444, "f": 0.4999999950781251},
    "rouge-l": {"r": 0.8333333333333334, "p": 0.625, "f": 0.7142857093877552},
}
