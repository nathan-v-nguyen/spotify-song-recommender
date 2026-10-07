"""Fixed evaluation query set used to compare pipeline runs (see docs/project_spec.md Section 29)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MoodQuery:
    """A mood-string test query and the region of the audio-feature space it's meant to exercise."""
    mood_string: str
    tests: str


@dataclass(frozen=True)
class TrackQuery:
    """A seed-track test query and the region of the audio-feature space it's meant to exercise."""
    spotify_id: str
    name: str
    artist: str
    tests: str


MOOD_QUERIES: list[MoodQuery] = [
    MoodQuery(
        mood_string="loud gym music with lots of energy, feeling good, ready to go",
        tests="happy/energetic quadrant (high valence, high energy)",
    ),
    MoodQuery(
        mood_string="calm happy late night studying music",
        tests="calm/content quadrant (high valence, low energy)",
    ),
    MoodQuery(
        mood_string="sad songs for crying",
        tests="sad quadrant (low valence, low energy)",
    ),
    MoodQuery(
        mood_string="fast music for when im angry",
        tests="angry/tense quadrant (low valence, high energy)",
    ),
    MoodQuery(
        mood_string="rap song",
        tests="high speechiness, low instrumentalness",
    ),
    MoodQuery(
        mood_string="instrumental acoustic music",
        tests="high instrumentalness, high acousticness",
    ),
]


TRACK_QUERIES: list[TrackQuery] = [
    TrackQuery(
        spotify_id="1cKHdTo9u0ZymJdPGSh6nq",
        name="I Was Never There",
        artist="The Weeknd;Gesaffelstein",
        tests="angry/tense quadrant (low valence, high energy)",
    ),
    TrackQuery(
        spotify_id="4h9wh7iOZ0GGn8QVp4RAOB",  
        name="I Ain't Worried",
        artist="OneRepublic",
        tests="happy/energetic quadrant (high valence, high energy)",
    ),
    TrackQuery(
        spotify_id="5e2l2ZAMwHmrkdM4Z6NhAR",  
        name="Again",
        artist="Shiloh Dynasty;Timmies",
        tests="calm/content quadrant (high valence, low energy)",
    ),
    TrackQuery(
        spotify_id="1e3QZ42GsP8cTy5uQ0G7J3",  
        name="Something in the Orange",
        artist="Zach Bryan",
        tests="sad quadrant (low valence, low energy)",
    ),
    TrackQuery(
        spotify_id="4EVO2VDWNVA4DpEqlHpfuZ", 
        name="Flowers",
        artist="Lauren Spencer Smith",
        tests="elevated speechiness",
    ),
    TrackQuery(
        spotify_id="2vWBUC9djv6BtiGlmKiQaH",  
        name="YKWIM?",
        artist="Yot Club",
        tests="high instrumentalness, high acousticness",
    ),
]
