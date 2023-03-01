#!/usr/bin/python3
import sys

def main() -> None:
    import json

    versions = sys.argv[1]
    version_matrix = [
        {"version": v, "branch": "main" if v == "3.12" else v, "os": "windows-2019"}
        for v in versions.split("/")
    ]
    print(f"BUILD_MATRIX={json.dumps(version_matrix)}")


if __name__ == '__main__':
    main()
