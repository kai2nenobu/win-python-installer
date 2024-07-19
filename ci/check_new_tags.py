#!/usr/bin/python3
from __future__ import annotations
import re
import sys
import subprocess
from urllib.request import urlopen
from xml.etree import ElementTree
from dataclasses import dataclass


"""
Check new releases for cpython by fetching a cpython tag feed.
If new releases are found, update 'README.md' and print new tag names.
"""


@dataclass
class Tag:
    name: str
    updated: str

    def is_security_version(self) -> bool:
        security_versions = {
            (3, 11): 10,  # 3.11.10 (Plan in PEP 664)
            (3, 10): 12,  # 3.10.12 (Plan in PEP 619)
            (3, 9): 14,  # 3.9.14 (Plan in PEP 596)
            (3, 8): 11,  # 3.8.11
            (3, 7): 9,  # 3.7.9
            (3, 6): 9  # 3.6.9
        }
        major, minor, patch, _ = self.version_tuple()
        security_patch_version = security_versions.get((major, minor), sys.maxsize)
        return patch >= security_patch_version

    def version_tuple(self) -> tuple[int, int, int, str]:
        regex = r'^v(\d+)\.(\d+)\.(\d+)(.*)$'
        m = re.fullmatch(regex, self.name)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4))
        else:
            return (0, 0, 0, '')  # dummy value


def extract_tag(entry: ElementTree.Element) -> Tag:
    """Extract tag info from a tag feed entry"""
    updated = entry.find('{*}updated').text
    title = entry.find('{*}title').text
    return Tag(title, updated)


def update_readme(tag: Tag):
    readme = 'README.md'
    major, minor, patch, _ = tag.version_tuple()
    minor_version = f'{major}.{minor}'
    release_date = tag.updated[:10]
    tag_url = 'https://github.com/kai2nenobu/win-python-installer/releases/tag'
    new_line = f'| {minor_version:>10} | [{minor_version}.{patch}]({tag_url}/{tag.name}) | {release_date} |             |\n'

    readme_lines = []
    # Replace the latest release table
    with open(readme, encoding='utf-8') as f:
        regex = r'^\|\s*{}\s*\|'.format(minor_version)
        for line in f:
            if re.search(regex, line):
                readme_lines.append(new_line)
            else:
                readme_lines.append(line)
    # Write back
    with open(readme, mode='w', encoding='utf-8') as f:
        for line in readme_lines:
            f.write(line)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        tag_feed = 'https://github.com/python/cpython/tags.atom'
        with urlopen(tag_feed) as res:
            body = res.read().decode('utf-8')
    else:
        # Read a feed from a file (for testing purpose)
        test_feed_file = sys.argv[1]
        with open(test_feed_file, mode='rt', encoding='utf-8') as f:
            body = f.read()
    feed = ElementTree.fromstring(body)
    recent_tags = [extract_tag(entry) for entry in feed.findall('{*}entry')]
    # Python security tags
    security_update_tags = [tag for tag in recent_tags if tag.is_security_version()]
    # Local tags
    local_tags = subprocess.check_output(["git", "tag"], encoding='utf-8').strip().split('\n')
    new_tags = [tag for tag in security_update_tags if tag.name not in local_tags]
    for tag in new_tags:
        # Update README contents
        update_readme(tag)
    print('/'.join([tag.name for tag in new_tags]))
