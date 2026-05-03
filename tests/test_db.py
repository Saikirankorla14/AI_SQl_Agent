"""
tests/test_db.py
Unit tests for the database safety guard (_is_safe_query).
Run with: pytest tests/
"""

import pytest
from agent.db import _is_safe_query


class TestSafeQuery:
    def test_select_allowed(self):
        assert _is_safe_query("SELECT id, name FROM users") is True

    def test_select_with_cte(self):
        assert _is_safe_query("WITH cte AS (SELECT 1) SELECT * FROM cte") is True

    def test_insert_blocked(self):
        assert _is_safe_query("INSERT INTO users VALUES (1, 'bob')") is False

    def test_update_blocked(self):
        assert _is_safe_query("UPDATE users SET name='x' WHERE id=1") is False

    def test_delete_blocked(self):
        assert _is_safe_query("DELETE FROM users WHERE id=1") is False

    def test_drop_blocked(self):
        assert _is_safe_query("DROP TABLE users") is False

    def test_case_insensitive(self):
        assert _is_safe_query("delete from users") is False

    def test_leading_whitespace(self):
        assert _is_safe_query("  SELECT 1") is True
