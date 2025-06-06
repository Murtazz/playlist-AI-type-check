import librosa
import numpy as np

feature_ranges = {
    "tempo": (50, 200),
    "rmse": (0.0, 1.0),
    "spectral_centroid": (0.0, 8000),
    "spectral_bandwidth": (0.0, 4000),
    "rolloff": (0.0, 8000),
    "zero_crossing_rate": (0.0, 1.0),
}

def normalize_features(features, feature_ranges):
    normalized = {}
    for key, value in features.items():
        if key in feature_ranges:
            min_val, max_val = feature_ranges[key]
            norm = (value - min_val) / (max_val - min_val)
            normalized[key] = np.clip(norm, 0.0, 1.0)  # Clamp to [0, 1]
        else:
            normalized[key] = value  # Leave unnormalized (optional)
    return normalized


def extract_features_from_file(file_path):
    y, sr = librosa.load(file_path, sr=None)
    raw_features = {
        "tempo": librosa.beat.tempo(y=y, sr=sr)[0],
        "chroma_stft": np.mean(librosa.feature.chroma_stft(y=y, sr=sr)),
        "rmse": np.mean(librosa.feature.rms(y=y)),
        "spectral_centroid": np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
        "spectral_bandwidth": np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)),
        "rolloff": np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
        "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y))
    }
    return normalize_features(raw_features, feature_ranges=feature_ranges)