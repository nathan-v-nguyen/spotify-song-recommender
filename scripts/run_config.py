"""Run configurations for the offline eval — one frozen RunConfig per MLflow run, selectable by name."""

from dataclasses import asdict, dataclass
from functools import partial
from typing import Callable

from app.models import Track
from app.ranker import ranker_a, ranker_b


@dataclass(frozen=True)
class RunConfig:
  ''' Everything that defines one evaluation run; the single source of truth for what executes and what is logged '''
  run_name: str
  ranker: str                              # "A" (cosine on 9 features) or "B" (cosine on 8 features + popularity boost)
  popularity_weight: float | None = None   # boost weight; only meaningful for ranker B
  popularity_target: int = 75              # popularity slot of the mood query vector; used in Annoy retrieval for BOTH rankers
  candidate_pool_size: int = 500           # n passed to get_candidates (query-time)
  n_trees: int = 50                        # describes the built index (scripts/build_index.py builds with 50); not changeable at eval time

  def __post_init__(self) -> None:
    ''' Rejects configs that contradict themselves, so a mislabeled run cannot be created '''
    if self.ranker not in ("A", "B"):
      raise ValueError(f"{self.run_name}: ranker must be 'A' or 'B', got {self.ranker!r}")
    if self.ranker == "A" and self.popularity_weight is not None:
      raise ValueError(f"{self.run_name}: ranker A does not use popularity_weight")
    if self.ranker == "B" and self.popularity_weight is None:
      raise ValueError(f"{self.run_name}: ranker B requires popularity_weight")


def build_ranker(config: RunConfig) -> Callable[..., list[tuple[Track, float]]]:
  ''' Turns a config's ranker label into the callable that actually runs '''
  if config.ranker == "A":
    return ranker_a
  return partial(ranker_b, popularity_weight=config.popularity_weight)


def config_params(config: RunConfig) -> dict[str, str | int | float]:
  ''' Returns the config as MLflow params (run_name is the run's name, not a param; None is logged as "N/A") '''
  return {
    key: "N/A" if value is None else value
    for key, value in asdict(config).items()
    if key != "run_name"
  }


_RUN_LIST: list[RunConfig] = [
  RunConfig("baseline", "A"),
  RunConfig("boost-w0.05", "B", popularity_weight=0.05),
  RunConfig("boost-w0.1", "B", popularity_weight=0.1),
  RunConfig("boost-w0.2", "B", popularity_weight=0.2),
  RunConfig("boost-w0.5", "B", popularity_weight=0.5),
  RunConfig("boost-w0.2-pool2000", "B", popularity_weight=0.2, candidate_pool_size=2000),
]

RUNS: dict[str, RunConfig] = {config.run_name: config for config in _RUN_LIST}

if len(RUNS) != len(_RUN_LIST):
  raise ValueError("Duplicate run_name in _RUN_LIST")
