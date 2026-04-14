import csv
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass

# --- Scoring constants (from our design) ---

WEIGHTS = {
    "mood": 0.25,
    "energy": 0.20,
    "genre": 0.18,
    "acousticness": 0.15,
    "valence": 0.10,
    "danceability": 0.07,
    "tempo": 0.05,
}

SIGMA = 0.2
TEMPO_SIGMA = 0.15
TEMPO_NORMALIZER = 200.0
SCORE_THRESHOLD = 0.05
MAX_PER_GENRE = 2


# --- Helpers ---

def gaussian_score(value: float, target: float, sigma: float = SIGMA) -> float:
    """Gaussian proximity: returns 1.0 on perfect match, falls toward 0."""
    return math.exp(-((value - target) ** 2) / (2 * sigma ** 2))


# --- Data classes ---

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_acousticness: float
    target_valence: float
    target_danceability: float
    target_tempo_bpm: float


# --- OOP API ---

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> float:
        scores = {
            "genre": 1.0 if song.genre == user.favorite_genre else 0.0,
            "mood": 1.0 if song.mood == user.favorite_mood else 0.0,
            "energy": gaussian_score(song.energy, user.target_energy),
            "acousticness": gaussian_score(song.acousticness, user.target_acousticness),
            "valence": gaussian_score(song.valence, user.target_valence),
            "danceability": gaussian_score(song.danceability, user.target_danceability),
            "tempo": gaussian_score(
                song.tempo_bpm / TEMPO_NORMALIZER,
                user.target_tempo_bpm / TEMPO_NORMALIZER,
                sigma=TEMPO_SIGMA,
            ),
        }
        return sum(WEIGHTS[k] * scores[k] for k in WEIGHTS)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(
            ((song, self._score_song(user, song)) for song in self.songs),
            key=lambda pair: pair[1],
            reverse=True,
        )
        scored = [(s, sc) for s, sc in scored if sc >= SCORE_THRESHOLD]
        return enforce_diversity_songs(scored, k)

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        parts = []

        # Categorical features
        for feature, song_val, user_val in [
            ("genre", song.genre, user.favorite_genre),
            ("mood", song.mood, user.favorite_mood),
        ]:
            if song_val == user_val:
                parts.append(f"{feature} match (+{WEIGHTS[feature]:.2f})")
            else:
                parts.append(f"{feature} mismatch (+0.00)")

        # Numerical features
        for name, song_val, user_val, sigma in [
            ("energy", song.energy, user.target_energy, SIGMA),
            ("acousticness", song.acousticness, user.target_acousticness, SIGMA),
            ("valence", song.valence, user.target_valence, SIGMA),
            ("danceability", song.danceability, user.target_danceability, SIGMA),
            ("tempo", song.tempo_bpm / TEMPO_NORMALIZER, user.target_tempo_bpm / TEMPO_NORMALIZER, TEMPO_SIGMA),
        ]:
            g = gaussian_score(song_val, user_val, sigma)
            weighted = WEIGHTS[name] * g
            parts.append(f"{name} proximity {g:.2f} (+{weighted:.2f})")

        total = self._score_song(user, song)
        return " | ".join(parts) + f" | total: {total:.2f}"


# --- Diversity enforcement ---

def enforce_diversity_songs(scored: List[Tuple[Song, float]], k: int) -> List[Song]:
    """Apply genre diversity cap to a scored and sorted list of Song objects."""
    result: List[Song] = []
    genre_counts: Dict[str, int] = {}
    for song, _ in scored:
        if genre_counts.get(song.genre, 0) < MAX_PER_GENRE:
            result.append(song)
            genre_counts[song.genre] = genre_counts.get(song.genre, 0) + 1
            if len(result) >= k:
                break
    return result


def enforce_diversity_dicts(scored: List[Tuple[Dict, float, str]], k: int) -> List[Tuple[Dict, float, str]]:
    """Apply genre diversity cap to a scored and sorted list of song dicts."""
    result: List[Tuple[Dict, float, str]] = []
    genre_counts: Dict[str, int] = {}
    for item in scored:
        genre = item[0]["genre"]
        if genre_counts.get(genre, 0) < MAX_PER_GENRE:
            result.append(item)
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
            if len(result) >= k:
                break
    return result


# --- Functional API ---

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    Returns: (total_score, list_of_reason_strings)
    """
    reasons = []

    # Categorical: exact match
    genre_score = 1.0 if song["genre"] == user_prefs["genre"] else 0.0
    mood_score = 1.0 if song["mood"] == user_prefs["mood"] else 0.0

    if genre_score:
        reasons.append(f"genre match (+{WEIGHTS['genre']:.2f})")
    else:
        reasons.append("genre mismatch (+0.00)")

    if mood_score:
        reasons.append(f"mood match (+{WEIGHTS['mood']:.2f})")
    else:
        reasons.append("mood mismatch (+0.00)")

    # Numerical: Gaussian proximity
    scores = {"genre": genre_score, "mood": mood_score}

    for name, song_key, user_key, sigma in [
        ("energy", "energy", "energy", SIGMA),
        ("acousticness", "acousticness", "acousticness", SIGMA),
        ("valence", "valence", "valence", SIGMA),
        ("danceability", "danceability", "danceability", SIGMA),
        ("tempo", "tempo_bpm", "tempo_bpm", TEMPO_SIGMA),
    ]:
        if name == "tempo":
            g = gaussian_score(
                song[song_key] / TEMPO_NORMALIZER,
                user_prefs[user_key] / TEMPO_NORMALIZER,
                sigma,
            )
        else:
            g = gaussian_score(song[song_key], user_prefs[user_key], sigma)

        scores[name] = g
        weighted = WEIGHTS[name] * g
        reasons.append(f"{name} proximity {g:.2f} (+{weighted:.2f})")

    total = sum(WEIGHTS[k] * scores[k] for k in WEIGHTS)
    return total, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    Returns: list of (song_dict, score, explanation_string)
    """
    # Score every song and join reasons into a single explanation string
    scored = [
        (song, score, " | ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Filter by minimum threshold
    scored = [item for item in scored if item[1] >= SCORE_THRESHOLD]

    # Apply diversity cap and return top k
    return enforce_diversity_dicts(scored, k)
