#!/usr/bin/env python3
"""Record and query client activity for a bound personal-memory repository."""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from uuid import uuid4


BRANCH = "personal-memory-activity"
REMOTE_REF = f"refs/heads/{BRANCH}"
FETCH_REF = "refs/personal-memory/activity-remote"
DEVICE_REF = "refs/personal-memory/activity-device"
ENABLED_KEY = "personal-memory.activity"
AGENT_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
RECORD_FILE = re.compile(r"([0-9a-f]{32})--([a-z0-9][a-z0-9-]{0,47})\.json")
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TIME_FIELDS = ("last_seen_at", "last_pull_at", "last_update_at")
EVENT_FIELDS = {"pull": "last_pull_at", "update": "last_update_at"}


class ActivityError(Exception):
    pass


class Git:
    def __init__(self, directory):
        self.directory = Path(directory).expanduser().resolve()
        self.environment = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_NAMESPACE"):
            self.environment.pop(key, None)
        self.environment["GIT_TERMINAL_PROMPT"] = "0"

        root = Path(self.run("rev-parse", "--show-toplevel")).resolve()
        remote = self.run("config", "--local", "--get", "personal-memory.remote", missing=True)
        branch = self.run("config", "--local", "--get", "personal-memory.branch", missing=True)
        if root != self.directory or not remote or not branch or branch == BRANCH:
            raise ActivityError("Use a bound personal-memory repository and a separate memory branch.")
        if self.run("remote", "get-url", "--all", "origin") != remote:
            raise ActivityError("The fetch address does not match the memory binding.")
        if self.run("remote", "get-url", "--push", "--all", "origin") != remote:
            raise ActivityError("The push address does not match the memory binding.")

    def run(self, *args, input_text=None, missing=False, index=None):
        environment = self.environment.copy()
        if index is not None:
            environment["GIT_INDEX_FILE"] = str(index)
        try:
            result = subprocess.run(
                ["git", "-C", str(self.directory), "-c", "credential.interactive=never", *args],
                env=environment,
                input=input_text,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ActivityError(f"Git {args[0]} timed out.") from error
        if missing and result.returncode == 1:
            return ""
        if result.returncode:
            raise ActivityError(f"Git {args[0]} failed: {result.stderr.strip() or result.returncode}")
        return result.stdout.rstrip("\n")

    def ref(self, name):
        return self.run("rev-parse", "--verify", "--quiet", name, missing=True)

    def blob(self, content):
        return self.run("hash-object", "-w", "--stdin", input_text=content)


def now_utc():
    return datetime.now(timezone.utc)


def timestamp(value):
    return value.strftime(TIME_FORMAT)


def read_record(text, filename):
    match = RECORD_FILE.fullmatch(filename)
    try:
        record = json.loads(text)
        if (record["device_id"], record["agent"]) != match.groups():
            raise ValueError("client identity differs from filename")
        for field in TIME_FIELDS:
            value = record[field]
            if value is not None:
                if timestamp(datetime.strptime(value, TIME_FORMAT)) != value:
                    raise ValueError("invalid timestamp")
        if record["last_seen_at"] is None:
            raise ValueError("missing last activity time")
        return {key: record[key] for key in ("device_id", "agent", *TIME_FIELDS)}
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise ActivityError(f"Invalid activity entry: {filename}") from error


def combine(record, other):
    merged = record.copy()
    for field in TIME_FIELDS:
        merged[field] = max(record[field] or "", other[field] or "") or None
    return merged


def device_id(git):
    current = git.ref(DEVICE_REF)
    if not current:
        candidate = git.blob(uuid4().hex + "\n")
        try:
            git.run("update-ref", DEVICE_REF, candidate, "0" * len(candidate))
        except ActivityError:
            if not git.ref(DEVICE_REF):
                raise
        current = git.ref(DEVICE_REF)
    value = git.run("cat-file", "blob", current)
    if not re.fullmatch(r"[0-9a-f]{32}", value):
        raise ActivityError("The local activity device ID is invalid.")
    return value


def record_local(git, agent, event):
    device = device_id(git)
    filename = f"{device}--{agent}.json"
    ref = f"refs/personal-memory/activity-local/{agent}"
    moment = timestamp(now_utc())
    record = {"device_id": device, "agent": agent, **dict.fromkeys(TIME_FIELDS)}
    record["last_seen_at"] = moment
    if event in EVENT_FIELDS:
        record[EVENT_FIELDS[event]] = moment

    for _ in range(4):
        previous = git.ref(ref)
        updated = record
        if previous:
            updated = combine(record, read_record(git.run("cat-file", "blob", previous), filename))
        blob = git.blob(json.dumps(updated, sort_keys=True) + "\n")
        try:
            git.run("update-ref", ref, blob, previous or "0" * len(blob))
            return filename, updated
        except ActivityError:
            if git.ref(ref) == previous:
                raise
    raise ActivityError("The local activity record changed repeatedly. Retry the operation.")


def remote_head(git):
    if not git.run("ls-remote", "--refs", "origin", REMOTE_REF):
        return ""
    git.run("fetch", "--no-tags", "--no-write-fetch-head", "origin", f"{REMOTE_REF}:{FETCH_REF}")
    return git.ref(FETCH_REF)


def activity_commit(git, parent, filename, data):
    with TemporaryDirectory(prefix="personal-memory-activity-") as directory:
        index = Path(directory) / "index"
        git.run("read-tree", parent or "--empty", index=index)
        blob = git.blob(json.dumps(data, sort_keys=True) + "\n")
        git.run("update-index", "--add", "--cacheinfo", f"100644,{blob},{filename}", index=index)
        tree = git.run("write-tree", index=index)
    parent_args = ("-p", parent) if parent else ()
    return git.run(
        "-c", "user.name=Personal Memory Activity", "-c", "user.email=activity@example.invalid",
        "commit-tree", "--no-gpg-sign", tree, *parent_args, "-m", "Record memory client activity",
    )


def sync(git, filename, record):
    parent = remote_head(git)
    for _ in range(4):
        updated = record
        if parent and git.run("ls-tree", "--name-only", parent, "--", filename):
            previous = read_record(git.run("show", f"{parent}:{filename}"), filename)
            updated = combine(record, previous)
            if updated == previous:
                return updated
        commit = activity_commit(git, parent, filename, updated)
        try:
            git.run("-c", "remote.origin.mirror=false", "push", "--no-follow-tags", "origin", f"{commit}:{REMOTE_REF}")
            return updated
        except ActivityError:
            latest = remote_head(git)
            if latest == parent:
                raise
            parent = latest
    raise ActivityError("The activity branch changed repeatedly. Retry the operation.")


def status(git, hours):
    head = remote_head(git)
    clients = []
    if head:
        for filename in git.run("ls-tree", "--name-only", "-z", head).split("\0"):
            if RECORD_FILE.fullmatch(filename):
                clients.append(read_record(git.run("show", f"{head}:{filename}"), filename))
    current = now_utc()
    cutoff = timestamp(current - timedelta(hours=hours))
    upper = timestamp(current)
    for record in clients:
        record["active"] = cutoff <= record["last_seen_at"] <= upper
    clients.sort(key=lambda record: record["last_seen_at"], reverse=True)
    active = [record for record in clients if record["active"]]
    devices = {}
    for record in clients:
        device_id = record["device_id"]
        device = devices.get(device_id, {"device_id": device_id, "active": False, **dict.fromkeys(TIME_FIELDS)})
        device = combine(device, record)
        device["active"] = device["active"] or record["active"]
        devices[device_id] = device
    return {
        "activity_window_hours": hours,
        "registered_devices": len(devices),
        "active_devices": sum(device["active"] for device in devices.values()),
        "registered_agents": len(clients),
        "active_agents": len(active),
        "last_pull_at": max((record["last_pull_at"] or "" for record in clients), default="") or None,
        "last_update_at": max((record["last_update_at"] or "" for record in clients), default="") or None,
        "devices": list(devices.values()),
        "clients": clients,
    }


def agent_name(value):
    value = value.lower()
    if not AGENT_ID.fullmatch(value):
        raise argparse.ArgumentTypeError("Use 1–48 letters, numbers or hyphens, starting with a letter or number.")
    return value


def activity_window(value):
    hours = int(value)
    if not 1 <= hours <= 8760:
        raise argparse.ArgumentTypeError("Choose between 1 and 8760 hours.")
    return hours


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_repo = os.environ.get("PERSONAL_MEMORY_DIR") or Path.home() / ".local/share/personal-memory"
    parser.add_argument("--repo", default=default_repo, help="path of the bound memory clone")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("enable").add_argument("--agent", required=True, type=agent_name)
    commands.add_parser("disable")
    record = commands.add_parser("record")
    record.add_argument("--agent", required=True, type=agent_name)
    record.add_argument("--event", required=True, choices=("seen", *EVENT_FIELDS))
    commands.add_parser("status").add_argument("--hours", type=activity_window, default=24)
    args = parser.parse_args()

    try:
        git = Git(args.repo)
        if args.command == "status":
            result = status(git, args.hours)
        elif args.command == "disable":
            git.run("config", "--local", ENABLED_KEY, "false")
            result = {"enabled": False}
        else:
            if args.command == "enable":
                git.run("config", "--local", ENABLED_KEY, "true")
            enabled = git.run("config", "--local", "--bool", "--get", ENABLED_KEY, missing=True) == "true"
            result = {"enabled": enabled}
            if enabled:
                filename, entry = record_local(git, args.agent, getattr(args, "event", "seen"))
                result["entry"] = sync(git, filename, entry)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ActivityError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
