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

    TARGET_VERSIONS: str | None = None
    """Target versions to build on manual workflow (github.event.inputs.target_versions)"""


BASE_MATRIX = {
    "3.8": {"os": "windows-2019", "HOST_PYTHON": "3.8"},
    "3.9": {"os": "windows-2022"},
    "3.10": {"os": "windows-2022"},
    "3.11": {"os": "windows-2022"},
    "3.12": {"os": "windows-2022"},
    "3.13": {"os": "windows-2022"},
    "3.14": {"os": "windows-2022"},
    "3.15": {"os": "windows-2022", "branch": "main"},
}
ALL_VERSIONS = "/".join(["3.10", "3.11", "3.12", "3.13", "3.14", "3.15"])


def to_matrix(event: GitHubEvent) -> list[dict]:
    if event.EVENT_NAME == "pull_request" and event.BRANCH_NAME == "new_release":
        versions = re.sub(r"^.*New release *", "", event.PR_TITLE)
    elif event.EVENT_NAME == "workflow_dispatch":
        versions = event.TARGET_VERSIONS
    else:
        versions = ALL_VERSIONS
    version_list = versions.split("/")

    def convert(version: str) -> dict:
        minor_version = ".".join(version.lstrip("v").split(".")[0:2])
        matrix = BASE_MATRIX[minor_version].copy()
        matrix["version"] = version
        if "branch" not in matrix:
            matrix["branch"] = version if version.startswith("v") else minor_version
        return matrix

    matrix = [convert(version) for version in version_list]
    return matrix


def main() -> None:
    event = GitHubEvent(
        EVENT_NAME=os.getenv("EVENT_NAME"),
        BRANCH_NAME=os.getenv("BRANCH_NAME"),
        PR_TITLE=os.getenv("PR_TITLE"),
        TARGET_VERSIONS=os.getenv("TARGET_VERSIONS")
    )
    print(json.dumps(to_matrix(event)))


if __name__ == "__main__":
    main()


class Test(unittest.TestCase):
    PARAMETERS = {
        "schedule_event": {
            "event": {"EVENT_NAME": "schedule", "BRANCH_NAME": "main"},
            "expected": [
                {"version": "3.10", "os": "windows-2022", "branch": "3.10"},
                {"version": "3.11", "os": "windows-2022", "branch": "3.11"},
                {"version": "3.12", "os": "windows-2022", "branch": "3.12"},
                {"version": "3.13", "os": "windows-2022", "branch": "3.13"},
                {"version": "3.14", "os": "windows-2022", "branch": "3.14"},
                {"version": "3.15", "os": "windows-2022", "branch": "main"},
            ]
        },
        "release_pr": {
            "event": {"EVENT_NAME": "pull_request", "BRANCH_NAME": "new_release", "PR_TITLE": "✨New release v3.10.14/v3.9.19/v3.8.19"},
            "expected": [
                {"version": "v3.10.14", "os": "windows-2022", "branch": "v3.10.14"},
                {"version": "v3.9.19", "os": "windows-2022", "branch": "v3.9.19"},
                {"version": "v3.8.19", "os": "windows-2019", "HOST_PYTHON": "3.8", "branch": "v3.8.19"},
            ]
        },
        "non_release_pr": {
            "event": {"EVENT_NAME": "pull_request", "BRANCH_NAME": "feature_branch", "PR_TITLE": "Some feature"},
            "expected": [
                {"version": "3.10", "os": "windows-2022", "branch": "3.10"},
                {"version": "3.11", "os": "windows-2022", "branch": "3.11"},
                {"version": "3.12", "os": "windows-2022", "branch": "3.12"},
                {"version": "3.13", "os": "windows-2022", "branch": "3.13"},
                {"version": "3.14", "os": "windows-2022", "branch": "3.14"},
                {"version": "3.15", "os": "windows-2022", "branch": "main"},
            ]
        },
        "manual_workflow": {
            "event": {"EVENT_NAME": "workflow_dispatch", "BRANCH_NAME": "main", "TARGET_VERSIONS": "3.10/3.8/3.14"},
            "expected": [
                {"version": "3.10", "os": "windows-2022", "branch": "3.10"},
                {"version": "3.8", "os": "windows-2019", "HOST_PYTHON": "3.8", "branch": "3.8"},
                {"version": "3.14", "os": "windows-2022", "branch": "3.14"},
            ]
        },
        "any_other_event": {
            "event": {"EVENT_NAME": "push", "BRANCH_NAME": "main"},
            "expected": [
                {"version": "3.10", "os": "windows-2022", "branch": "3.10"},
                {"version": "3.11", "os": "windows-2022", "branch": "3.11"},
                {"version": "3.12", "os": "windows-2022", "branch": "3.12"},
                {"version": "3.13", "os": "windows-2022", "branch": "3.13"},
                {"version": "3.14", "os": "windows-2022", "branch": "3.14"},
                {"version": "3.15", "os": "windows-2022", "branch": "main"},
            ]
        }
    }

    def test_events(self):
        for name, param in Test.PARAMETERS.items():
            with self.subTest(msg=name, param=param):
                self.assertSequenceEqual(
                    to_matrix(GitHubEvent(**param["event"])),
                    param["expected"]
                )
