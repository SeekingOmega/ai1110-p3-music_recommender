# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example: 

VibeFinder 1.0

> **FindYourMuse 1.0**

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

> FindYourMuse recommends 5 songs for each user profile from a 20-song catalog. It takes a user's preferred genre, mood, energy, acousticness, valence, danceability, and tempo, then scores every song against those preferences. It is a classroom project for exploring how content-based recommenders work. It is not meant for real users or real music catalogs.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

> Each song has 7 features: genre, mood, energy, acousticness, valence, danceability, and tempo. The user tells the system what they prefer for each of those features.

> For genre and mood, it is a simple yes-or-no check. If the song's genre matches what the user wants, it gets full credit. If not, it gets zero. There is no partial credit.

> For the five numerical features, the system uses a bell curve (Gaussian function) to measure how close the song is to what the user wants. A perfect match scores 1.0. The further a song drifts from the user's preferred value, the closer to 0 it scores. This means the system rewards songs that are *close* to your preference, not just songs that are high or low.

> Each feature gets a weight that controls how much it matters. Mood is the heaviest (25%), then energy (20%), then genre (18%), acousticness (15%), valence (10%), danceability (7%), and tempo (5%). The final score is the weighted sum of all seven feature scores.

> After scoring, the system filters out very low-scoring songs, sorts the rest from highest to lowest, then applies a diversity cap: no more than 2 songs from the same genre in the final list. This prevents the results from being all lofi or all pop.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

> The catalog has 20 songs across 10 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, folk) and 16 different moods. The original starter file had 10 songs. I told Claude to add 10 more: 3 new genres (hip-hop, r&b, folk) and 7 songs that repeat existing genres with different moods. This way most genres have at least 2 songs so the diversity cap has real options to work with.

> For the synthetic data, Claude made up the song names, artists, and feature values. The numerical values are designed to cover a wide range — from very quiet acoustic tracks (Deep Water, energy 0.18) to intense high-energy songs (Iron Collapse... wait no, Gym Hero, energy 0.93). The taste this data reflects is mostly Western pop and electronic music. Genres like classical, Latin, and African music are not represented at all.

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

> The system works best when the user's preferred genre and mood exist in the catalog and have multiple songs. The Pop Enthusiast profile got Sunrise City at a near-perfect 1.00. The Study Lofi Listener got Library Rain at 0.99. The Late Night Driver got Night Drive Loop at 0.99. When there is a clear match in the data, the scoring puts it at the top reliably.

> The Gaussian proximity scoring does its job well. It rewards closeness, not extremes. A user who wants energy 0.40 does not get the highest-energy song — they get the song closest to 0.40. This is a better model of real taste than a simple "higher is better" approach.

> The explanation output is a strength too. Every recommendation shows exactly which features contributed how many points. You can look at a result and understand *why* it was recommended. Real systems like Spotify do not show you this.

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

> The system ignores lyrics, language, and cultural context. A song with harmful lyrics scores the same as any other if the numbers match.

> Genre and mood are all-or-nothing. Indie pop and pop get zero credit for each other even though most listeners would consider them similar. This hurts cross-genre discovery.

> Mood and genre together control 43% of the score. If a song misses on both, the most it can score is 0.57. The system is biased toward staying inside your stated genre and mood rather than finding sonically similar music across boundaries.

> The diversity cap (max 2 per genre) forces variety but also blocks songs users actually want. The Pop Enthusiast lost Gym Hero (score 0.68) because two pop songs already filled the cap. The cap does not scale with genre depth — it applies the same flat limit whether a genre has 1 song or 4.

> Hip-hop, r&b, and folk each have only one song. A user who prefers those genres gets mostly off-genre results. The system is not biased against those genres on purpose — the data is just too thin.

> All numerical features use the same sensitivity (sigma = 0.2). A 0.1 gap in tempo normalization is treated the same as a 0.1 gap in valence, even though those mean very different things in real music.

> If this were a real product, it would create a filter bubble. Users only see songs that match their stated preferences. There is no way to discover something unexpected. It would also disadvantage new or niche artists whose genres are underrepresented in the catalog.

> This system doesn't learn from user feedback. If you skip a recommendation, the system does not update your profile or adjust future suggestions. Real recommenders use feedback loops to improve over time, but this one is static.

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

> I tested 6 user profiles: 3 regular and 3 adversarial edge cases.

> The 3 regular profiles (Pop Enthusiast, Study Lofi Listener, Late Night Driver) each got a top result scoring 0.99–1.00. The recommendations matched my expectations. The Pop user got pop songs. The Lofi user got lofi and ambient songs. The synthwave user got synthwave and moody rock.

> The 3 edge cases tested what happens when the system is stressed:
> - **High Energy + Melancholic** asked for a combination that does not exist in the catalog. The top score dropped to 0.69 and no song matched the mood. The system did not crash or give random results — it just gave the closest it could find.
> - **Non-Existent Genre (k-pop)** gave every song a 0 on genre. Mood match became the deciding factor. The system still produced reasonable results based on numerical features alone.
> - **Dead-Center Preferences (all values at 0.50)** produced a flat scoring landscape. The top 5 scores compressed into a narrow 0.45–0.71 range. Many songs scored similarly, which makes sense — if you have no strong preference, lots of songs are equally okay.

> I also ran 2 default automated tests with pytest. One checks that recommendations come back sorted by score. The other checks that explanations are non-empty strings. Both pass.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

> - **Smarter diversity cap.** Instead of a flat 2-per-genre limit, scale the cap based on how many songs exist in each genre and how strongly the user prefers that genre. A lofi lover with 4 lofi songs in the catalog should be allowed more than 2.
> - **Partial genre matching.** Instead of all-or-nothing, give partial credit for related genres. Indie pop and pop should score maybe 0.7 against each other, not 0.0.
> - **Per-feature sigma.** Tune sigma separately for each feature based on how much it varies in the catalog. Tempo needs a wider sigma than valence.
> - **Context-aware profiles.** Let users have multiple profiles (study mode, workout mode, chill mode) instead of one fixed taste profile.
> - **Feedback loop.** Track which recommendations users accept or skip, and update preferences over time.
> - **Bigger catalog.** 20 songs is too few. A catalog of 200+ songs would make the diversity cap and scoring much more meaningful.
> - **Lyric and language features.** Add features for lyric sentiment, language, and theme so the system can understand what a song is about, not just how it sounds.

---

## 9. Personal Reflection

A few sentences about what you learned:

- What was your biggest learning moment during this project?
> Designing the Gaussian scoring was a big learning moment. I had to think carefully about how to reward closeness rather than just high values. 
> Learning how real-world recommenders work was very interesting. 

- How did using AI tools help you, and when did you need to double-check them?
> I used AI to help design the scoring logic and to generate synthetic data. It was helpful for brainstorming and filling in AI system knowledge gaps, but I had to double-check the math of the Gaussian function and make sure the generated songs made sense within the catalog.

- What surprised you about how simple algorithms can still "feel" like recommendations?
> My system is relatively more complex than the assignment instructions suggested. However, even this is simple compared to real-world recommenders. And the thing that surprised me the most is how a song can be embedded in a multi-dimensional feature space and scored based on proximity to user preferences, and that can create a meaningful recommendation experience. Even without understanding lyrics or cultural context, the system can surface songs that "feel right" based on audio features alone. Math in AI never ceases to amaze me in how many different complex concepts it can model, and in this case, how it can model something as subjective as music taste.

- What would you try next if you extended this project?
> I would try implementing a smarter diversity cap that scales with genre depth and user preference strength. I would also add feedback loops so the system can learn from user interactions over time. Finally, I would expand the catalog to include more songs and genres for a richer recommendation experience.