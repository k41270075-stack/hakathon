"""Инструменты машинного просмотра и сканирования: ключ отдельно, тайлы на месте."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_tile_centre_round_trip():
    scan = _load("scan_tiles")
    lat, lon = 51.1456, 71.3512
    xs, ys = scan.tile_range((lon, lat, lon, lat))
    c_lat, c_lon = scan.tile_center(xs[0] + 0.5, ys[0] + 0.5)
    # Центр тайла z18 не дальше половины тайла (~48 м) от точки.
    assert abs(c_lat - lat) * 111_320 < 60
    assert abs(c_lon - lon) * 111_320 * 0.63 < 60


def test_tile_range_covers_bbox_in_order():
    scan = _load("scan_tiles")
    xs, ys = scan.tile_range((71.30, 51.10, 71.35, 51.15))
    assert xs.start < xs.stop and ys.start < ys.stop
    north, _ = scan.tile_center(xs.start, ys.start)
    south, _ = scan.tile_center(xs.start, ys.stop)
    assert north > south


def test_answer_is_recorded_by_code_not_object(tmp_path, monkeypatch):
    answer = _load("vision_answer")
    monkeypatch.setattr(answer, "ROOT", tmp_path)
    (tmp_path / "data/vision").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["x", "V1234", "dump", "0.8", "россыпь", "мусора"])
    assert answer.main() == 0
    saved = json.loads((tmp_path / "data/vision/answers_eval.json").read_text(encoding="utf-8"))
    assert saved == {"V1234": {"verdict": "landfill", "confidence": 0.8,
                               "note": "россыпь мусора", "reviewer": "claude-vision"}}


def test_answer_rejects_unknown_verdict(tmp_path, monkeypatch):
    answer = _load("vision_answer")
    monkeypatch.setattr(answer, "ROOT", tmp_path)
    (tmp_path / "data/vision").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["x", "V1", "maybe", "0.5"])
    with pytest.raises(KeyError):
        answer.main()


def test_ai_answers_never_enter_human_labels():
    """Ответы ИИ помечены reviewer и не попадают в разметку человека."""
    path = ROOT / "data/vision/answers_eval.json"
    if not path.exists():
        pytest.skip("ответов нет")
    answers = json.loads(path.read_text(encoding="utf-8"))
    assert all(a["reviewer"] == "claude-vision" for a in answers.values())
    labels = (ROOT / "labels_manual.geojson").read_text(encoding="utf-8")
    assert "claude-vision" not in labels
