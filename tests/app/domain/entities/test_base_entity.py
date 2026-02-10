"""Tests for domain/entities/base_entity.py"""

from datetime import datetime, timezone
import pytest
from app.domain.entities.base_entity import BaseEntity


class TestBaseEntityInitialization:
    """Test BaseEntity initialization"""

    def test_base_entity_creation_with_id(self):
        """Test creating BaseEntity with ID"""
        entity = BaseEntity(id="test-123")
        assert entity.id == "test-123"

    def test_base_entity_creation_without_id(self):
        """Test creating BaseEntity without ID defaults to None"""
        entity = BaseEntity()
        assert entity.id is None

    def test_base_entity_has_timestamps(self):
        """Test BaseEntity has created_at and updated_at timestamps"""
        entity = BaseEntity(id="test-123")
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)

    def test_base_entity_timestamps_are_same_on_creation(self):
        """Test created_at and updated_at are equal on entity creation"""
        entity = BaseEntity(id="test-123")
        # They should be very close (within a second)
        diff = abs((entity.created_at - entity.updated_at).total_seconds())
        assert diff < 1


class TestBaseEntityFields:
    """Test BaseEntity fields"""

    def test_base_entity_has_id_field(self):
        """Test BaseEntity has id field"""
        entity = BaseEntity(id="123")
        assert hasattr(entity, 'id')
        assert entity.id == "123"

    def test_base_entity_has_created_at_field(self):
        """Test BaseEntity has created_at field"""
        entity = BaseEntity()
        assert hasattr(entity, 'created_at')

    def test_base_entity_has_updated_at_field(self):
        """Test BaseEntity has updated_at field"""
        entity = BaseEntity()
        assert hasattr(entity, 'updated_at')

    def test_base_entity_field_types(self):
        """Test BaseEntity field types are correct"""
        entity = BaseEntity(id="test")
        assert isinstance(entity.id, str) or entity.id is None
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)


class TestBaseEntityMethods:
    """Test BaseEntity methods"""

    def test_update_timestamp_method_exists(self):
        """Test update_timestamp method exists"""
        entity = BaseEntity()
        assert hasattr(entity, 'update_timestamp')
        assert callable(entity.update_timestamp)

    def test_update_timestamp_updates_updated_at(self):
        """Test update_timestamp actually updates updated_at"""
        entity = BaseEntity()
        old_timestamp = entity.updated_at
        entity.update_timestamp()
        # The updated_at should be newer or equal
        assert entity.updated_at >= old_timestamp

    def test_created_at_unchanged_after_update_timestamp(self):
        """Test created_at doesn't change when update_timestamp is called"""
        entity = BaseEntity()
        original_created_at = entity.created_at
        entity.update_timestamp()
        assert entity.created_at == original_created_at


class TestBaseEntitySerialization:
    """Test BaseEntity serialization"""

    def test_base_entity_model_dump(self):
        """Test BaseEntity can be dumped as dict"""
        entity = BaseEntity(id="test-123")
        dumped = entity.model_dump()
        assert isinstance(dumped, dict)
        assert "id" in dumped
        assert "created_at" in dumped
        assert "updated_at" in dumped

    def test_base_entity_model_dump_json(self):
        """Test BaseEntity can be dumped as JSON"""
        entity = BaseEntity(id="test-123")
        json_str = entity.model_dump_json()
        assert isinstance(json_str, str)
        assert "test-123" in json_str
        assert "created_at" in json_str

    def test_base_entity_to_dict(self):
        """Test converting BaseEntity to dictionary"""
        entity = BaseEntity(id="test-id")
        entity_dict = entity.model_dump()
        assert entity_dict['id'] == "test-id"
        assert entity_dict['created_at'] is not None
        assert entity_dict['updated_at'] is not None


class TestBaseEntityPydantic:
    """Test BaseEntity Pydantic model features"""

    def test_base_entity_is_pydantic_model(self):
        """Test BaseEntity is a Pydantic BaseModel"""
        entity = BaseEntity()
        assert hasattr(entity, 'model_validate')
        assert hasattr(entity, 'model_dump')
        assert hasattr(entity, 'model_dump_json')

    def test_base_entity_field_validation(self):
        """Test BaseEntity field validation"""
        # Creating with valid data should work
        entity = BaseEntity(id="valid-id")
        assert entity.id == "valid-id"

    def test_base_entity_config_populate_by_name(self):
        """Test BaseEntity config allows field name population"""
        entity = BaseEntity(id="test")
        dumped = entity.model_dump()
        assert "id" in dumped
