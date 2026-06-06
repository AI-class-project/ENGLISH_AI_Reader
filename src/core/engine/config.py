from dataclasses import dataclass


@dataclass(frozen=True)
class GENERATE_BATCH_CONFIG:
    PASSAGE_PREFIX_MAX: int = 20
    ATTEMPTS_RATIO_MAX: float = 2.0