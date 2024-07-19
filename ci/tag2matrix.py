"""
Convert CPython tags to a build matrix for GitHub Actions
"""
from __future__ import annotations


import json
import sys
import unittest


BASE_MATRIX = {
    "3.8": {"os": "windows-2019", "HOST_PYTHON": "3.8"},
    "3.9": {"os": "windows-2019"},
    "3.10": {"os": "windows-2019"},
    "3.11": {"os": "windows-2019"},
}

def to_matrix(tags: str) -> list[dict]:
    tag_list = tags.split("/")

    def convert(tag: str) -> dict:
        minor_version = ".".join(tag.lstrip("v").split(".")[0:2])
        matrix = BASE_MATRIX[minor_version].copy()
        matrix["tag"] = tag
        return matrix

    matrix = [convert(tag) for tag in tag_list]
    return matrix


def main() -> None:
    print(json.dumps(to_matrix(sys.argv[1])))


if __name__ == "__main__":
    main()


class Test(unittest.TestCase):
    def test_tags(self):
        self.assertSequenceEqual(
            to_matrix("v3.10.14/v3.9.19/v3.8.19/v3.11.10"),
            [
                {"tag": "v3.10.14", "os": "windows-2019"},
                {"tag": "v3.9.19", "os": "windows-2019"},
                {"tag": "v3.8.19", "os": "windows-2019", "HOST_PYTHON": "3.8"},
                {"tag": "v3.11.10", "os": "windows-2019"},
            ]
        )

    def test_single_tag(self):
        self.assertSequenceEqual(
            to_matrix("v3.8.19"),
            [
                {"tag": "v3.8.19", "os": "windows-2019", "HOST_PYTHON": "3.8"},
            ]
        )

    def test_branches(self):
        self.assertSequenceEqual(
            to_matrix("3.8/3.9/3.10"),
            [
                {"tag": "3.8", "os": "windows-2019", "HOST_PYTHON": "3.8"},
                {"tag": "3.9", "os": "windows-2019"},
                {"tag": "3.10", "os": "windows-2019"},
            ]
        )
