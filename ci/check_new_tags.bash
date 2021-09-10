#!/bin/bash

# Find recent python tags from RSS feed
python_tags=$(curl -sSL --retry 3 https://github.com/python/cpython/tags.atom \
  | xmlstarlet sel -t -m _:feed/_:entry -v _:title -n \
  | grep -E '^v3\.[6-8]+\.[0-9]+$' \
  | sort
)
local_tags=$(git tag | sort)
# Find out new tags
comm -23 <(echo "$python_tags") <(echo "$local_tags") | sort -Vr | paste -sd /
