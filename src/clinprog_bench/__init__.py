"""ClinProg-Bench: Benchmark for clinical programming tasks."""

from clinprog_bench.schema import TaskSpec
from clinprog_bench.scorers import BaseScorer, Score

__version__ = "0.1.0"

__all__ = ["BaseScorer", "Score", "TaskSpec", "__version__"]
