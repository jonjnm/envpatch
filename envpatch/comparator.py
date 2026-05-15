"""Compare two ProfileResult objects and surface meaningful differences."""

from dataclasses import dataclass, field
from typing import List
from envpatch.profiler import ProfileResult


@dataclass
class ComparisonResult:
    gained_secrets: List[str] = field(default_factory=list)
    lost_secrets: List[str] = field(default_factory=list)
    newly_empty: List[str] = field(default_factory=list)
    no_longer_empty: List[str] = field(default_factory=list)
    gained_urls: List[str] = field(default_factory=list)
    lost_urls: List[str] = field(default_factory=list)
    key_count_delta: int = 0

    def has_concerns(self) -> bool:
        return bool(
            self.gained_secrets
            or self.newly_empty
            or self.lost_urls
        )

    def summary(self) -> str:
        lines = [f"Key count delta : {self.key_count_delta:+d}"]
        if self.gained_secrets:
            lines.append(f"New secret keys : {', '.join(self.gained_secrets)}")
        if self.lost_secrets:
            lines.append(f"Removed secrets : {', '.join(self.lost_secrets)}")
        if self.newly_empty:
            lines.append(f"Newly empty     : {', '.join(self.newly_empty)}")
        if self.no_longer_empty:
            lines.append(f"Filled in       : {', '.join(self.no_longer_empty)}")
        if self.gained_urls:
            lines.append(f"New URL values  : {', '.join(self.gained_urls)}")
        if self.lost_urls:
            lines.append(f"Removed URLs    : {', '.join(self.lost_urls)}")
        if not any([
            self.gained_secrets, self.lost_secrets,
            self.newly_empty, self.no_longer_empty,
            self.gained_urls, self.lost_urls,
        ]):
            lines.append("No structural differences.")
        return "\n".join(lines)


def compare_profiles(base: ProfileResult, target: ProfileResult) -> ComparisonResult:
    """Return a ComparisonResult highlighting structural changes between two profiles."""
    base_secrets = set(base.secret_keys)
    target_secrets = set(target.secret_keys)

    base_empty = set(base.empty_values)
    target_empty = set(target.empty_values)

    base_urls = set(base.url_values)
    target_urls = set(target.url_values)

    return ComparisonResult(
        gained_secrets=sorted(target_secrets - base_secrets),
        lost_secrets=sorted(base_secrets - target_secrets),
        newly_empty=sorted(target_empty - base_empty),
        no_longer_empty=sorted(base_empty - target_empty),
        gained_urls=sorted(target_urls - base_urls),
        lost_urls=sorted(base_urls - target_urls),
        key_count_delta=target.total_keys - base.total_keys,
    )
