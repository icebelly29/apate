"""
SampleDetector is a placeholder class to simulate deepfake prediction logic.
This will be replaced with actual model inference logic.
"""

import random

class SampleDetector:
    def __init__(self):
        self.model_name = "MockModel-v0"

    def predict_frame(self, frame):
        """
        Simulates frame-level prediction.
        Returns a random fake probability.
        """
        return {"real": round(random.uniform(0, 1), 3), "fake": round(random.uniform(0, 1), 3)}

    def predict_video(self, video_path):
        """
        Simulates video-level prediction on 10 frames.
        Returns fake/real scores for each frame and an overall verdict.
        """
        predictions = [self.predict_frame(None) for _ in range(10)]
        avg_fake = sum(p["fake"] for p in predictions) / len(predictions)
        verdict = "FAKE" if avg_fake > 0.5 else "REAL"
        return {"verdict": verdict, "details": predictions}