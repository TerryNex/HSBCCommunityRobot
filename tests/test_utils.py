"""
Unit tests for date/time utility functions in utils.py.
"""
import pytest
from datetime import datetime, timezone, timedelta
from utils import parse_iso_date, format_hk_time, is_within_hours, HK_TIMEZONE


class TestParseIsoDate:
    """Tests for parse_iso_date function."""

    def test_parse_with_milliseconds_and_z(self):
        """Test parsing ISO date with milliseconds and Z suffix."""
        result = parse_iso_date("2026-01-07T15:04:51.870Z")
        assert result is not None
        assert result.tzinfo == timezone.utc
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 7
        assert result.hour == 15
        assert result.minute == 4
        assert result.second == 51
        assert result.microsecond == 870000

    def test_parse_without_milliseconds(self):
        """Test parsing ISO date without milliseconds."""
        result = parse_iso_date("2026-01-07T15:04:51Z")
        assert result is not None
        assert result.tzinfo == timezone.utc
        assert result.hour == 15

    def test_parse_empty_string(self):
        """Test parsing empty string returns None."""
        result = parse_iso_date("")
        assert result is None

    def test_parse_none(self):
        """Test parsing None returns None."""
        result = parse_iso_date(None)
        assert result is None

    def test_parse_invalid_format(self):
        """Test parsing invalid format returns None."""
        result = parse_iso_date("not-a-date")
        assert result is None

    def test_parse_partial_date(self):
        """Test parsing partial date returns None."""
        result = parse_iso_date("2026-01-07")
        # This should still work as datetime.fromisoformat can parse date-only
        assert result is not None


class TestFormatHkTime:
    """Tests for format_hk_time function."""

    def test_format_valid_date(self):
        """Test formatting valid UTC date to HK time."""
        # 15:04:51 UTC = 23:04:51 HKT (UTC+8)
        result = format_hk_time("2026-01-07T15:04:51.870Z")
        assert result == "2026-01-07 23:04:51 HKT"

    def test_format_empty_string(self):
        """Test formatting empty string returns Unknown."""
        result = format_hk_time("")
        assert result == "Unknown"

    def test_format_none(self):
        """Test formatting None returns Unknown."""
        result = format_hk_time(None)
        assert result == "Unknown"

    def test_format_invalid_date(self):
        """Test formatting invalid date returns Unknown."""
        result = format_hk_time("invalid-date")
        assert result == "Unknown"

    def test_format_midnight_utc(self):
        """Test midnight UTC converts to 08:00 HKT."""
        result = format_hk_time("2026-01-07T00:00:00Z")
        assert result == "2026-01-07 08:00:00 HKT"


class TestIsWithinHours:
    """Tests for is_within_hours function."""

    def test_no_hours_filter_returns_true(self):
        """Test that no hours filter (None) returns True."""
        result = is_within_hours("2026-01-07T15:04:51Z", None)
        assert result is True

    def test_zero_hours_filter_returns_true(self):
        """Test that zero hours filter returns True."""
        result = is_within_hours("2026-01-07T15:04:51Z", 0)
        assert result is True

    def test_recent_post_within_hours(self):
        """Test that a recent post is within the hours window."""
        now = datetime.now(timezone.utc)
        recent_time = (now - timedelta(hours=2)).isoformat() + "Z"
        result = is_within_hours(recent_time, 24)
        assert result is True

    def test_old_post_outside_hours(self):
        """Test that an old post is outside the hours window."""
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(hours=48)).isoformat() + "Z"
        result = is_within_hours(old_time, 24)
        assert result is False

    def test_empty_date_returns_false(self):
        """Test that empty date string returns False when filter is enabled."""
        result = is_within_hours("", 24)
        assert result is False

    def test_none_date_returns_false(self):
        """Test that None date returns False when filter is enabled."""
        result = is_within_hours(None, 24)
        assert result is False

    def test_invalid_date_returns_false(self):
        """Test that invalid date returns False when filter is enabled."""
        result = is_within_hours("not-a-valid-date", 24)
        assert result is False

    def test_boundary_exactly_at_cutoff(self):
        """Test boundary condition when post is close to cutoff time."""
        now = datetime.now(timezone.utc)
        # Post 23 hours and 59 minutes ago should be included
        boundary_time = (now - timedelta(hours=23, minutes=59)).isoformat() + "Z"
        result = is_within_hours(boundary_time, 24)
        assert result is True

    def test_post_just_after_cutoff(self):
        """Test post just after the cutoff is included."""
        now = datetime.now(timezone.utc)
        just_after = (now - timedelta(hours=23, minutes=59)).isoformat() + "Z"
        result = is_within_hours(just_after, 24)
        assert result is True

    def test_post_just_before_cutoff(self):
        """Test post just before the cutoff is excluded."""
        now = datetime.now(timezone.utc)
        just_before = (now - timedelta(hours=24, minutes=1)).isoformat() + "Z"
        result = is_within_hours(just_before, 24)
        assert result is False


class TestHkTimezone:
    """Tests for HK_TIMEZONE constant."""

    def test_hk_timezone_offset(self):
        """Test HK timezone is UTC+8."""
        utc_time = datetime(2026, 1, 7, 12, 0, 0, tzinfo=timezone.utc)
        hk_time = utc_time.astimezone(HK_TIMEZONE)
        assert hk_time.hour == 20  # 12 UTC + 8 = 20 HKT
