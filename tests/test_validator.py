"""Tests for map validator."""

import pytest
from src.optimizer import MapValidator, FortniteSpecs, Severity


def test_valid_map():
    """Test validation of valid map."""
    map_data = {
        "title": "Valid Map",
        "description": "Test map",
        "creator_id": "creator123",
        "props": [],
        "spawn_points": [
            {"id": "spawn1", "position": {"x": 0, "y": 0, "z": 100}},
            {"id": "spawn2", "position": {"x": 100, "y": 100, "z": 100}},
        ],
    }

    validator = MapValidator()
    report = validator.validate(map_data)

    assert report["valid"] == True
    assert report["error_count"] == 0


def test_missing_title():
    """Test validation of map without title."""
    map_data = {
        "description": "Test",
        "creator_id": "creator123",
        "props": [],
        "spawn_points": [],
    }

    validator = MapValidator()
    report = validator.validate(map_data)

    assert report["valid"] == False
    assert any(i["code"] == "MISSING_FIELD" for i in report["issues"])


def test_insufficient_spawns():
    """Test validation with too few spawn points."""
    map_data = {
        "title": "Bad Map",
        "description": "Test",
        "creator_id": "creator123",
        "props": [],
        "spawn_points": [{"id": "spawn1", "position": {"x": 0, "y": 0, "z": 0}}],
    }

    validator = MapValidator()
    report = validator.validate(map_data)

    assert not report["valid"]
    assert any(i["code"] == "INSUFFICIENT_SPAWNS" for i in report["issues"])


def test_no_weapons():
    """Test validation with no weapons."""
    map_data = {
        "title": "No Weapons",
        "description": "Test",
        "creator_id": "creator123",
        "props": [
            {
                "id": "prop1",
                "name": "Building",
                "type": "building",
                "position": {"x": 0, "y": 0, "z": 0},
            }
        ],
        "spawn_points": [
            {"id": "spawn1", "position": {"x": 0, "y": 0, "z": 100}},
            {"id": "spawn2", "position": {"x": 100, "y": 100, "z": 100}},
        ],
    }

    validator = MapValidator()
    report = validator.validate(map_data)

    assert not report["valid"]
    assert any(i["code"] == "NO_WEAPONS" for i in report["issues"])


def test_out_of_bounds():
    """Test validation with out-of-bounds props."""
    map_data = {
        "title": "Out of Bounds",
        "description": "Test",
        "creator_id": "creator123",
        "props": [
            {
                "id": "prop1",
                "name": "Far Away",
                "type": "building",
                "position": {"x": 50000, "y": 50000, "z": 0},  # Out of bounds
            }
        ],
        "spawn_points": [
            {"id": "spawn1", "position": {"x": 0, "y": 0, "z": 100}},
            {"id": "spawn2", "position": {"x": 100, "y": 100, "z": 100}},
        ],
    }

    validator = MapValidator()
    report = validator.validate(map_data)

    assert not report["valid"]
    assert any(i["code"] == "OUT_OF_BOUNDS" for i in report["issues"])
