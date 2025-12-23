import json
import subprocess
import sys
from pathlib import Path

def test_cli_smoke_jsonl_runs():
    repo = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        str(repo / "engine.py"),
        "--count", "2",
        "--format", "jsonl",
        "--seed", "7",
    ]
    out = subprocess.check_output(cmd, cwd=str(repo), text=True).strip().splitlines()
    assert len(out) == 2
    obj = json.loads(out[0])
    assert "event_id" in obj and "severity" in obj and "tags" in obj

def test_cli_event_alias_and_preset():
    repo = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        str(repo / "engine.py"),
        "--scene-preset", "dungeon",
        "--event", "hazard_smoke_01",
        "--format", "jsonl",
        "--seed", "1",
    ]
    out = subprocess.check_output(cmd, cwd=str(repo), text=True).strip().splitlines()
    assert len(out) == 1
    obj = json.loads(out[0])
    assert obj["event_id"] == "hazard_smoke_01"
