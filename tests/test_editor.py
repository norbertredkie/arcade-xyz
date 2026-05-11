"""Tests for map editor."""

import pytest
from src.editor import Map, MapBuilder, PropType, Vector3, Rotation, Prop


def test_create_map():
    """Test map creation."""
    builder = MapBuilder("Test Map", "Test description", "creator123")
    map_obj = builder.build()

    assert map_obj.title == "Test Map"
    assert map_obj.creator_id == "creator123"
    assert len(map_obj.props) == 0


def test_add_prop():
    """Test adding prop to map."""
    builder = MapBuilder("Test", "Desc", "creator123")
    builder.add_prop(
        asset_id="asset_001",
        name="Building",
        prop_type=PropType.BUILDING,
        position=Vector3(100, 100, 0),
    )

    map_obj = builder.build()
    assert len(map_obj.props) == 1
    assert map_obj.props[0].name == "Building"


def test_add_spawn_point():
    """Test adding spawn point."""
    builder = MapBuilder("Test", "Desc", "creator123")
    builder.add_spawn_point(Vector3(0, 0, 100), team="red")

    map_obj = builder.build()
    assert len(map_obj.spawn_points) == 1
    assert map_obj.spawn_points[0].team == "red"


def test_update_prop():
    """Test updating prop position."""
    builder = MapBuilder("Test", "Desc", "creator123")
    builder.add_prop(
        asset_id="asset_001",
        name="Prop",
        prop_type=PropType.DECORATION,
        position=Vector3(0, 0, 0),
    )

    map_obj = builder.build()
    prop_id = map_obj.props[0].id

    # Update position
    map_obj.update_prop(prop_id, {"position": {"x": 100, "y": 100, "z": 0}})

    updated_prop = map_obj.get_prop(prop_id)
    assert updated_prop.position.x == 100
    assert updated_prop.position.y == 100


def test_serialize_map():
    """Test map serialization."""
    builder = MapBuilder("Test", "Desc", "creator123")
    builder.add_prop(
        asset_id="asset_001",
        name="Building",
        prop_type=PropType.BUILDING,
        position=Vector3(100, 100, 0),
    )

    map_obj = builder.build()
    serialized = map_obj.to_dict()

    assert serialized["title"] == "Test"
    assert serialized["creator_id"] == "creator123"
    assert len(serialized["props"]) == 1
    assert serialized["props"][0]["name"] == "Building"
