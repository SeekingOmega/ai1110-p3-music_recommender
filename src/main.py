"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

from recommender import load_songs, recommend_songs

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- User profiles ---

PROFILES = [
    # Regular profiles
    {
        "name": "User Profile: Pop Enthusiast",
        "description": "Likes upbeat pop with high energy and danceability",
        "prefs": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.80,
            "acousticness": 0.15,
            "valence": 0.85,
            "danceability": 0.82,
            "tempo_bpm": 120.0,
        },
    },
    {
        "name": "User Profile: Study Lofi Listener",
        "description": "Prefers chill lofi for focus sessions, acoustic and slow",
        "prefs": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "acousticness": 0.80,
            "valence": 0.60,
            "danceability": 0.55,
            "tempo_bpm": 75.0,
        },
    },
    {
        "name": "User Profile: Late Night Driver",
        "description": "Cruises to moody synthwave after dark",
        "prefs": {
            "genre": "synthwave",
            "mood": "moody",
            "energy": 0.75,
            "acousticness": 0.15,
            "valence": 0.50,
            "danceability": 0.70,
            "tempo_bpm": 110.0,
        },
    },

    # Adversarial / edge-case profiles
    {
        "name": "EDGE CASE User Profile: High Energy + Melancholic",
        "description": "Conflicting signals — wants intense energy but sad mood. "
                       "No song in the catalog is both melancholic and high-energy.",
        "prefs": {
            "genre": "rock",
            "mood": "melancholic",
            "energy": 0.95,
            "acousticness": 0.10,
            "valence": 0.30,
            "danceability": 0.80,
            "tempo_bpm": 140.0,
        },
    },
    {
        "name": "EDGE CASE User Profile: Non-Existent Genre",
        "description": "Requests k-pop which doesn't exist in the catalog. "
                       "Genre score will be 0 for every song — tests whether "
                       "numerical features alone produce sensible results.",
        "prefs": {
            "genre": "k-pop",
            "mood": "happy",
            "energy": 0.85,
            "acousticness": 0.10,
            "valence": 0.90,
            "danceability": 0.90,
            "tempo_bpm": 125.0,
        },
    },
    {
        "name": "EDGE CASE User Profile: Dead-Center Preferences",
        "description": "Every numerical feature at 0.50 — no strong preference. "
                       "Tests whether the system produces a flat scoring landscape "
                       "where many songs score similarly.",
        "prefs": {
            "genre": "pop",
            "mood": "chill",
            "energy": 0.50,
            "acousticness": 0.50,
            "valence": 0.50,
            "danceability": 0.50,
            "tempo_bpm": 100.0,
        },
    },
]


def print_profile(profile: dict) -> None:
    prefs = profile["prefs"]
    print(f"  Genre: {prefs['genre']}  |  Mood: {prefs['mood']}")
    print(f"  Energy: {prefs['energy']}  |  Acousticness: {prefs['acousticness']}  |  "
          f"Valence: {prefs['valence']}")
    print(f"  Danceability: {prefs['danceability']}  |  Tempo: {prefs['tempo_bpm']} bpm")


def main() -> None:
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))

    for profile in PROFILES:
        print(f"  {profile['name']}")
        print(f"  {profile['description']}")
        print("-" * 70)
        print_profile(profile)
        print("-" * 70)

        recommendations = recommend_songs(profile["prefs"], songs, k=5)

        if not recommendations:
            print("  No songs scored above the minimum threshold.\n")
            continue

        for rank, (song, score, explanation) in enumerate(recommendations, 1):
            print(f"  #{rank}  {song['title']} by {song['artist']}  "
                  f"[{song['genre']}/{song['mood']}]  —  Score: {score:.2f}")
            print(f"       {explanation}")
        
        print("~" * 70)
        print()


if __name__ == "__main__":
    main()
