"""Tests for infrastructure/logger.py"""

import pytest
import logging
from app.infrastructure.logger import get_logger


class TestLoggerSetup:
    """Test logger setup"""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a logger"""
        log = get_logger(__name__)
        assert log is not None

    def test_get_logger_returns_valid_logger(self):
        """Test get_logger returns valid logger"""
        log = get_logger(__name__)
        # Should have logging methods
        assert hasattr(log, 'info')
        assert hasattr(log, 'error')
        assert hasattr(log, 'warning')
        assert hasattr(log, 'debug')

    def test_get_logger_with_different_names(self):
        """Test get_logger with different module names"""
        log1 = get_logger('module1')
        log2 = get_logger('module2')
        assert log1 is not None
        assert log2 is not None


class TestLoggerUsage:
    """Test logger basic usage"""

    def test_logger_can_log_info(self):
        """Test logger can log info messages"""
        log = get_logger(__name__)
        # Should not raise exception
        log.info("Test info message")
        assert True

    def test_logger_can_log_error(self):
        """Test logger can log error messages"""
        log = get_logger(__name__)
        # Should not raise exception
        log.error("Test error message")
        assert True

    def test_logger_can_log_warning(self):
        """Test logger can log warning messages"""
        log = get_logger(__name__)
        # Should not raise exception
        log.warning("Test warning message")
        assert True

    def test_logger_can_log_debug(self):
        """Test logger can log debug messages"""
        log = get_logger(__name__)
        # Should not raise exception
        log.debug("Test debug message")
        assert True
