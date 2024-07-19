"""
Generate a build matrix from GitHub Actions event

- Daily scheduled build -> all versions
- release PR -> release target versions in PR title
- non-release PR -> all versions
- manual workflow -> versions specified as input
"""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
import re
import unittest


@dataclass
class GitHubEvent:
    EVENT_NAME: str
    """Event name for GitHub Actions workflow (github.event_name)"""

    BRANCH_NAME: str
    """Branch name triggers GitHub Actions workflow (github.head_ref or github.ref)"""

    PR_TITLE: str | None = None
    """Pull Request title for GitHub Actions workflow (github.event.pull_request.title)"""


BASE_MATRIX = {
    "3.8": {"os": "windows-2019", "HOST_PYTHON": "3.8"},
    "3.9": {"os": "windows-2019"},
    "3.10": {"os": "windows-2019"},
    "3.11": {"os": "windows-2019"},
    "3.12": {"os": "windows-2019"},
    "3.13": {"os": "windows-2022", "branch": "main"},
}
ALL_VERSIONS = "/".join(BASE_MATRIX.keys())


def to_matrix(event: GitHubEvent) -> list[dict]:
    if event.EVENT_NAME == "schedule":
        tags = ALL_VERSIONS
    elif event.EVENT_NAME == "pull_request":
        if event.BRANCH_NAME == "new_release":
            tags = re.sub(r"^.*New release *", "", event.PR_TITLE)
        else:
            tags = ALL_VERSIONS
    else:
        tags = ""
    tag_list = tags.split("/")

    def convert(tag: str) -> dict:
        minor_version = ".".join(tag.lstrip("v").split(".")[0:2])
        matrix = BASE_MATRIX[minor_version].copy()
        matrix["version"] = tag
        if "branch" not in matrix:
            matrix["branch"] = minor_version
        return matrix

    matrix = [convert(tag) for tag in tag_list]
    return matrix


def main() -> None:
    event = GitHubEvent(
        EVENT_NAME=os.getenv("EVENT_NAME"),
        BRANCH_NAME=os.getenv("BRANCH_NAME"),
        PR_TITLE=os.getenv("PR_TITLE")
    )
    print(json.dumps(event))


if __name__ == "__main__":
    main()


class Test(unittest.TestCase):
    def test_schedule_event(self):
        self.assertSequenceEqual(
            to_matrix(GitHubEvent(**{"EVENT_NAME": "schedule", "BRANCH_NAME": "main"})),
            [
                {"version": "3.8", "os": "windows-2019", "HOST_PYTHON": "3.8", "branch": "3.8"},
                {"version": "3.9", "os": "windows-2019", "branch": "3.9"},
                {"version": "3.10", "os": "windows-2019", "branch": "3.10"},
                {"version": "3.11", "os": "windows-2019", "branch": "3.11"},
                {"version": "3.12", "os": "windows-2019", "branch": "3.12"},
                {"version": "3.13", "os": "windows-2022", "branch": "main"},
            ]
        )

    def test_release_pr(self):
        self.assertSequenceEqual(
            to_matrix(GitHubEvent(**{"EVENT_NAME": "pull_request", "BRANCH_NAME": "new_release", "PR_TITLE": "✨New release v3.10.14/v3.9.19/v3.8.19"})),
            [
                {"version": "v3.10.14", "os": "windows-2019", "branch": "3.10"},
                {"version": "v3.9.19", "os": "windows-2019", "branch": "3.9"},
                {"version": "v3.8.19", "os": "windows-2019", "HOST_PYTHON": "3.8", "branch": "3.8"},
            ]
        )

    def test_non_release_pr(self):
        self.assertSequenceEqual(
            to_matrix(GitHubEvent(**{"EVENT_NAME": "pull_request", "BRANCH_NAME": "feature_branch", "PR_TITLE": "Some feature"})),
            [
                {"version": "3.8", "os": "windows-2019", "HOST_PYTHON": "3.8", "branch": "3.8"},
                {"version": "3.9", "os": "windows-2019", "branch": "3.9"},
                {"version": "3.10", "os": "windows-2019", "branch": "3.10"},
                {"version": "3.11", "os": "windows-2019", "branch": "3.11"},
                {"version": "3.12", "os": "windows-2019", "branch": "3.12"},
                {"version": "3.13", "os": "windows-2022", "branch": "main"},
            ]
        )
