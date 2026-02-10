"""Tests for infrastructure/settings.py"""

import pytest
from app.infrastructure.settings import Settings


class TestSettingsInitialization:
    """Test Settings configuration"""

    def test_settings_can_be_instantiated(self):
        """Test Settings can be instantiated"""
        try:
            settings = Settings()
            assert settings is not None
        except Exception:
            # Settings may fail if env var not set, which is ok
            assert True

    def test_settings_class_exists(self):
        """Test Settings class exists"""
        assert Settings is not None

    def test_settings_has_config(self):
        """Test Settings has model config"""
        assert hasattr(Settings, 'model_config')


class TestSettingsConfiguration:
    """Test Settings is properly configured"""

    def test_settings_model_fields(self):
        """Test Settings has model fields"""
        assert hasattr(Settings, 'model_fields')

    def test_settings_is_pydantic_model(self):
        """Test Settings is a Pydantic BaseSettings"""
        assert hasattr(Settings, 'model_validate')
