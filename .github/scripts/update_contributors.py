#!/usr/bin/env python3
"""Auto-update CONTRIBUTORS.md table when an n8n Study Jam submission PR is merged.

This script parses the submissions/ folder to dynamically maintain
a sequential, verified, and conflict-free contributor directory in CONTRIBUTORS.md.

Architect & Infrastructure:
- Dyaksa (@xdyaksa) - Tech Team & Study Jam Lead (https://github.com/xdyaksa)
- Tech Team GDG on Campus Universitas Widyatama (https://github.com/gdgocwidyatama)
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Contributor:
    """Represents a verified contributor entry in the table."""
    name: str
    username: str
    path: str
    status: str = "Verified"

    @property
    def user_link(self) -> str:
        """Formats the username into a clean markdown link."""
        if not self.username or self.username.strip() == "-":
            return "-"
        if self.username.startswith("[@") or (self.username.startswith("[") and "github.com" in self.username):
            return self.username
        clean = self.username.strip().lstrip("@")
        return f"[@{clean}](https://github.com/{clean})" if clean else "-"

    @property
    def path_link(self) -> str:
        """Formats the path into a relative markdown link."""
        if self.path.startswith("["):
            return self.path
        return f"[{self.path}]({self.path})"

    def to_markdown_row(self, index: int) -> str:
        """Returns the formatted markdown table row."""
        return (
            f"| {index} | {self.name} | {self.user_link} | "
            f"{self.path_link} | {self.status} |"
        )


@dataclass
class PRMetadata:
    """Metadata extracted from the GitHub pull_request webhook payload."""
    name: Optional[str] = None
    username: Optional[str] = None
    title: str = ""


# Parsing Utilities

def parse_gitmodules(path: Path) -> Dict[str, Dict[str, str]]:
    """Parses .gitmodules file into a mapping of submodule name -> properties."""
    if not path.is_file():
        return {}

    submodules: Dict[str, Dict[str, str]] = {}
    current_key: Optional[str] = None

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        match = re.match(r'\[submodule\s+"([^"]+)"\]', line)
        if match:
            current_key = match.group(1)
            submodules[current_key] = {}
            continue

        if current_key and "=" in line:
            prop, _, value = line.partition("=")
            submodules[current_key][prop.strip()] = value.strip()

    return submodules


def extract_pr_metadata() -> Optional[PRMetadata]:
    """Reads PR title and description from GITHUB_EVENT_PATH if available."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).is_file():
        return None

    try:
        with open(event_path, "r", encoding="utf-8") as f:
            event = json.load(f)

        pr = event.get("pull_request")
        if not pr:
            return None

        title = pr.get("title", "")
        body = pr.get("body") or ""
        username = pr.get("user", {}).get("login")

        # 1. Try parsing full name from PR description: * **Nama Lengkap**: Dyaksa
        name_match = re.search(
            r"\*\*\s*Nama Lengkap\s*\*\*:\s*([^\r\n<]+)", body, re.IGNORECASE
        )
        name = name_match.group(1).strip() if name_match else None
        if name and (name.startswith("(") and name.endswith(")")):
            name = None

        # 2. Fallback to PR title: "Submission n8n Study Jam - 10121001 - Dyaksa"
        if not name and "-" in title:
            parts = [p.strip() for p in title.split("-")]
            if len(parts) >= 2 and "submission" in parts[0].lower():
                candidate = parts[-1].strip()
                if candidate and not candidate.startswith("<") and not candidate.startswith("["):
                    name = candidate

        return PRMetadata(name=name, username=username, title=title)
    except Exception as err:
        print(f"Notice: Unable to parse PR metadata: {err}", file=sys.stderr)
        return None


def extract_metadata_from_markdown(path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extracts Name and GitHub username directly from a submission .md file."""
    try:
        text = path.read_text(encoding="utf-8")
        name_match = re.search(r"[-*]\s*\*\*Nama Lengkap\*\*:\s*([^\r\n<]+)", text, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else None
        if name and (name.startswith("[") and name.endswith("]")):
            name = None

        user_match = re.search(r"[-*]\s*\*\*Username GitHub\*\*:\s*([^\r\n<]+)", text, re.IGNORECASE)
        username = user_match.group(1).strip() if user_match else None
        if username and (username.startswith("[@username") or "@username-anda" in username):
            username = None

        return name, username
    except Exception as err:
        print(f"Notice: Unable to read markdown {path}: {err}", file=sys.stderr)
        return None, None


def format_name_from_path(path_str: str) -> str:
    """Converts filename/slug (e.g. '10121001_Dyaksa.md') into Title Case ('Dyaksa')."""
    stem = Path(path_str).stem
    # Remove leading NIM if present (digits followed by underscore or dash)
    stem = re.sub(r"^\d+[-_]", "", stem)
    words = stem.replace("_", "-").split("-")
    return " ".join(word.capitalize() for word in words if word)


def extract_username_from_url(url: str) -> str:
    """Extracts GitHub username from HTTPS or SSH Git clone URL."""
    match = re.search(r"github\.com[/:]([^/]+)/", url)
    return match.group(1) if match else ""


# Markdown Table Handling

TABLE_HEADER_REGEX = re.compile(
    r"(\|[\t ]*No[\t ]*\|[\t ]*Nama Lengkap[\t ]*\|[\t ]*Username GitHub[\t ]*\|"
    r"[\t ]*(?:Berkas Submission|Path Submodule|Path Submission)[\t ]*\|[\t ]*Status Verifikasi[\t ]*\|[\t ]*\n"
    r"\|[ \-:\t|]+\|[\t ]*\n)",
    re.IGNORECASE,
)


def parse_contributors_markdown(
    content: str,
) -> Tuple[str, List[Contributor], str]:
    """Splits CONTRIBUTORS.md into (prefix, existing_entries, suffix)."""
    match = TABLE_HEADER_REGEX.search(content)
    if not match:
        raise ValueError("Could not locate contributors table in CONTRIBUTORS.md")

    prefix = content[: match.end()]
    rest = content[match.end() :]

    table_lines: List[str] = []
    suffix_lines: List[str] = []
    in_table = True

    for line in rest.splitlines(keepends=True):
        if in_table:
            if line.strip().startswith("|"):
                table_lines.append(line.strip())
            else:
                in_table = False
                suffix_lines.append(line)
        else:
            suffix_lines.append(line)

    contributors: List[Contributor] = []
    for line in table_lines:
        cols = [col.strip() for col in line.split("|")]
        # Cols: [empty, No, Nama, Username, Path, Status, empty]
        if len(cols) >= 6:
            no, name, username, path_raw, status = (
                cols[1], cols[2], cols[3], cols[4], cols[5]
            )

            # Ignore placeholder template rows
            if "Nama Kamu" in name or "(Nomor)" in no or "Nama Lengkap Anda" in name:
                continue

            path_match = re.search(r"\[([^\]]+)\]", path_raw)
            clean_path = path_match.group(1) if path_match else path_raw

            contributors.append(
                Contributor(
                    name=name,
                    username=username,
                    path=clean_path,
                    status=status,
                )
            )

    suffix_text = "".join(suffix_lines).strip()
    return prefix, contributors, suffix_text


# Main Synchronization Logic

def sync_contributors(root: Path) -> bool:
    """Synchronizes CONTRIBUTORS.md with submission markdown files and directories."""
    gitmodules_path = root / ".gitmodules"
    contributors_path = root / "CONTRIBUTORS.md"

    if not contributors_path.is_file():
        print(f"Error: {contributors_path} does not exist.", file=sys.stderr)
        return False

    content = contributors_path.read_text(encoding="utf-8")
    prefix, entries, suffix = parse_contributors_markdown(content)

    registered_paths: Set[str] = {entry.path for entry in entries}
    pr_meta = extract_pr_metadata()

    # 1. Scan submissions/ directory for .md submission files and folders
    submissions_dir = root / "submissions"
    if submissions_dir.is_dir():
        for item in sorted(submissions_dir.iterdir()):
            if item.name.startswith("."):
                continue

            sub_path = f"submissions/{item.name}"
            if sub_path in registered_paths:
                continue

            name: Optional[str] = None
            username: Optional[str] = None

            if item.is_file() and item.suffix.lower() == ".md":
                md_name, md_user = extract_metadata_from_markdown(item)
                name = md_name
                username = md_user

            if not name and pr_meta and pr_meta.name:
                name = pr_meta.name
            if not name:
                name = format_name_from_path(sub_path)

            if not username and pr_meta and pr_meta.username:
                username = pr_meta.username
            if not username:
                username = "-"

            entries.append(
                Contributor(
                    name=name,
                    username=username,
                    path=sub_path,
                    status="Verified",
                )
            )
            registered_paths.add(sub_path)

    # 2. Process git submodules defined in .gitmodules (if any remain)
    submodules = parse_gitmodules(gitmodules_path)
    for sub_name, props in submodules.items():
        sub_path = props.get("path", sub_name)
        if sub_path in registered_paths:
            continue

        url = props.get("url", "")
        username = (
            pr_meta.username
            if (pr_meta and pr_meta.username)
            else extract_username_from_url(url)
        )
        name = (
            pr_meta.name
            if (pr_meta and pr_meta.name)
            else format_name_from_path(sub_path)
        )

        entries.append(
            Contributor(
                name=name,
                username=username,
                path=sub_path,
                status="Verified",
            )
        )
        registered_paths.add(sub_path)

    # 3. Build formatted markdown output
    rows = [
        entry.to_markdown_row(idx)
        for idx, entry in enumerate(entries, start=1)
    ]
    if rows:
        table_body = "\n".join(rows) + "\n\n"
    else:
        table_body = "\n"

    new_content = f"{prefix}{table_body}{suffix}\n"

    if new_content == content:
        print("CONTRIBUTORS.md is already up to date.")
        return False

    contributors_path.write_text(new_content, encoding="utf-8")
    print(f"Success: Updated CONTRIBUTORS.md with {len(entries)} contributor(s).")
    return True


def main() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    has_changes = sync_contributors(root)
    sys.exit(0 if has_changes or True else 1)


if __name__ == "__main__":
    main()
