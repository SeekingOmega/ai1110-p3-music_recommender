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


def main() -> None:
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))

    # Example: a user who likes upbeat pop
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "acousticness": 0.80,
        "valence": 0.58,
        "danceability": 0.60,
        "tempo_bpm": 75.0,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Scoring explanation: {explanation}")
        print()


if __name__ == "__main__":
    main()
