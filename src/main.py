"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from recommender import load_songs, recommend_songs

PROJECT_ROOT = Path(__file__).resolve().parent.parent

console = Console()

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


def build_profile_panel(profile: dict) -> Panel:
    """Build a rich Panel displaying the user profile."""
    prefs = profile["prefs"]
    body = (
        f"[dim]{profile['description']}[/dim]\n"
        f"\n"
        f"  Genre: [bold]{prefs['genre']}[/bold]        "
        f"Mood: [bold]{prefs['mood']}[/bold]\n"
        f"  Energy: [bold]{prefs['energy']}[/bold]       "
        f"Acousticness: [bold]{prefs['acousticness']}[/bold]    "
        f"Valence: [bold]{prefs['valence']}[/bold]\n"
        f"  Danceability: [bold]{prefs['danceability']}[/bold]  "
        f"Tempo: [bold]{prefs['tempo_bpm']} bpm[/bold]"
    )
    return Panel(body, title=f"[bold]{profile['name']}[/bold]", border_style="cyan")


def build_rec_table(recommendations: list) -> Table:
    """Build a rich Table of the top recommendations."""
    table = Table(show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("#", justify="right", style="bold", width=3)
    table.add_column("Title", min_width=18)
    table.add_column("Artist", min_width=14)
    table.add_column("Genre / Mood", min_width=14)
    table.add_column("Score", justify="right", style="bold green", width=6)

    for rank, (song, score, _) in enumerate(recommendations, 1):
        table.add_row(
            str(rank),
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            f"{score:.2f}",
        )
    return table


def format_breakdown(explanation: str) -> Text:
    """Parse the pipe-separated explanation into colored rich Text."""
    text = Text()
    parts = [p.strip() for p in explanation.split("|")]

    for i, part in enumerate(parts):
        if "mismatch" in part:
            text.append(part, style="dim red")
        elif "match" in part:
            text.append(part, style="bold green")
        else:
            # Numerical — color by weighted contribution
            try:
                weighted = float(part.split("+")[1].rstrip(")"))
                if weighted >= 0.15:
                    text.append(part, style="green")
                elif weighted >= 0.05:
                    text.append(part, style="yellow")
                else:
                    text.append(part, style="dim")
            except (IndexError, ValueError):
                text.append(part)

        if i < len(parts) - 1:
            text.append("  |  ")

    return text


def main() -> None:
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))

    for profile in PROFILES:
        console.print()
        console.print(build_profile_panel(profile))

        recommendations = recommend_songs(profile["prefs"], songs, k=5)

        if not recommendations:
            console.print("  [dim]No songs scored above the minimum threshold.[/dim]\n")
            continue

        console.print(build_rec_table(recommendations))

        # Score breakdowns
        console.print("\n[bold]  Score Breakdowns[/bold]")
        for rank, (song, score, explanation) in enumerate(recommendations, 1):
            line = Text()
            line.append(f"  #{rank} ", style="bold")
            line.append(f"{song['title']}", style="bold cyan")
            line.append(f"  ({score:.2f})", style="green")
            console.print(line)

            breakdown = format_breakdown(explanation)
            padded = Text("      ")
            padded.append_text(breakdown)
            console.print(padded)

        console.print()


if __name__ == "__main__":
    main()
