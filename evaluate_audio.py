import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jiwer
from input_fetch_convert import speech_to_text

TRANSFORM = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemovePunctuation(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.ReduceToListOfListOfWords()
])


def load_test_cases(path="evaluation/audio_test_cases.json"):
    with open(path, "r") as f:
        return json.load(f)


def run_audio_eval():
    test_cases = load_test_cases()

    references = []
    hypotheses = []
    results = []

    for case in test_cases:
        with open(case["file"], "rb") as audio_file:
            hypothesis = speech_to_text(audio_file)

        reference = case["reference"]

        sample_wer = jiwer.wer(
            reference,
            hypothesis,
            reference_transform=TRANSFORM,
            hypothesis_transform=TRANSFORM,
        )

        references.append(reference)
        hypotheses.append(hypothesis)
        results.append({
            "file": case["file"],
            "reference": reference,
            "hypothesis": hypothesis,
            "wer": round(sample_wer, 3),
        })

    overall_wer = jiwer.wer(
        references,
        hypotheses,
        reference_transform=TRANSFORM,
        hypothesis_transform=TRANSFORM,
    )

    return results, overall_wer


if __name__ == "__main__":
    results, overall_wer = run_audio_eval()

    for r in results:
        print(f"{r['file']}: WER = {r['wer']}")
        print(f"  reference : {r['reference']}")
        print(f"  hypothesis: {r['hypothesis']}")
        print()

    print(f"Overall WER across {len(results)} clips: {round(overall_wer, 3)}")