#!/usr/bin/env python3
"""
Unit tests for media_utils module.

Copyright (C) 2025  Shiue-Lang Chin
Licensed under GPL-3.0-or-later
"""

import unittest
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.media_utils import (
    is_media_file,
    parse_date_string,
    parse_range,
    MEDIA_EXTENSIONS
)


class TestIsMediaFile(unittest.TestCase):
    """Test the is_media_file function."""

    def test_image_extensions(self):
        """Test common image file extensions."""
        self.assertTrue(is_media_file('photo.jpg'))
        self.assertTrue(is_media_file('photo.JPG'))  # Case insensitive
        self.assertTrue(is_media_file('image.png'))
        self.assertTrue(is_media_file('picture.heic'))
        self.assertTrue(is_media_file('raw_photo.cr2'))
        self.assertTrue(is_media_file('digital.dng'))

    def test_video_extensions(self):
        """Test common video file extensions."""
        self.assertTrue(is_media_file('video.mp4'))
        self.assertTrue(is_media_file('movie.MOV'))  # Case insensitive
        self.assertTrue(is_media_file('clip.avi'))
        self.assertTrue(is_media_file('recording.mkv'))

    def test_non_media_files(self):
        """Test that non-media files are correctly identified."""
        self.assertFalse(is_media_file('document.txt'))
        self.assertFalse(is_media_file('spreadsheet.xlsx'))
        self.assertFalse(is_media_file('presentation.pptx'))
        self.assertFalse(is_media_file('archive.zip'))
        self.assertFalse(is_media_file('script.py'))

    def test_full_paths(self):
        """Test that function works with full file paths."""
        self.assertTrue(is_media_file('/path/to/photo.jpg'))
        self.assertTrue(is_media_file('/home/user/videos/movie.mp4'))
        self.assertFalse(is_media_file('/documents/report.pdf'))

    def test_no_extension(self):
        """Test files without extensions."""
        self.assertFalse(is_media_file('README'))
        self.assertFalse(is_media_file('Makefile'))


class TestParseDateString(unittest.TestCase):
    """Test the parse_date_string function."""

    def test_basic_datetime(self):
        """Test parsing basic datetime string."""
        result = parse_date_string('2023-10-15 14:30:45')
        expected = datetime(2023, 10, 15, 14, 30, 45)
        self.assertEqual(result, expected)

    def test_subsecond_precision(self):
        """Test parsing datetime with subsecond precision."""
        result = parse_date_string('2023-10-15 14:30:45.123')
        expected = datetime(2023, 10, 15, 14, 30, 45)
        self.assertEqual(result, expected)

        result = parse_date_string('2023-10-15 14:30:45.123456')
        self.assertEqual(result, expected)

    def test_positive_timezone_offset(self):
        """Test parsing datetime with positive timezone offset."""
        result = parse_date_string('2023-10-15 14:30:45+05:00')
        expected = datetime(2023, 10, 15, 14, 30, 45)
        self.assertEqual(result, expected)

        result = parse_date_string('2023-10-15 14:30:45+0000')
        self.assertEqual(result, expected)

    def test_negative_timezone_offset(self):
        """Test parsing datetime with negative timezone offset."""
        result = parse_date_string('2023-10-15 14:30:45-05:00')
        expected = datetime(2023, 10, 15, 14, 30, 45)
        self.assertEqual(result, expected)

        result = parse_date_string('2023-10-15 14:30:45-0800')
        expected = datetime(2023, 10, 15, 14, 30, 45)
        self.assertEqual(result, expected)

    def test_whitespace_handling(self):
        """Test parsing datetime with leading/trailing whitespace."""
        result = parse_date_string('  2023-10-15 14:30:45  ')
        expected = datetime(2023, 10, 15, 14, 30, 45)
        self.assertEqual(result, expected)

        result = parse_date_string('2023-10-15 14:30:45 ')
        self.assertEqual(result, expected)

    def test_edge_cases(self):
        """Test edge cases and special dates."""
        # New Year
        result = parse_date_string('2024-01-01 00:00:00')
        expected = datetime(2024, 1, 1, 0, 0, 0)
        self.assertEqual(result, expected)

        # Leap year
        result = parse_date_string('2024-02-29 12:00:00')
        expected = datetime(2024, 2, 29, 12, 0, 0)
        self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """Test that invalid inputs return None."""
        self.assertIsNone(parse_date_string(''))
        self.assertIsNone(parse_date_string(None))
        self.assertIsNone(parse_date_string('invalid'))
        self.assertIsNone(parse_date_string('2023-13-45 14:30:45'))  # Invalid month
        self.assertIsNone(parse_date_string('not a date'))


class TestParseRange(unittest.TestCase):
    """Test the parse_range function."""

    def test_single_value(self):
        """Test parsing a single value."""
        self.assertEqual(parse_range('2022'), [2022])
        self.assertEqual(parse_range('5'), [5])
        self.assertEqual(parse_range('1'), [1])

    def test_range(self):
        """Test parsing a range."""
        self.assertEqual(parse_range('2020-2023'), [2020, 2021, 2022, 2023])
        self.assertEqual(parse_range('1-5'), [1, 2, 3, 4, 5])
        self.assertEqual(parse_range('10-12'), [10, 11, 12])

    def test_single_item_range(self):
        """Test range where start equals end."""
        self.assertEqual(parse_range('2022-2022'), [2022])
        self.assertEqual(parse_range('5-5'), [5])

    def test_empty_or_none(self):
        """Test empty or None input."""
        self.assertEqual(parse_range(None), [])
        self.assertEqual(parse_range(''), [])

    def test_negative_values(self):
        """Test parsing negative values (for ratings)."""
        self.assertEqual(parse_range('-1'), [-1])


class TestMediaExtensions(unittest.TestCase):
    """Test the MEDIA_EXTENSIONS constant."""

    def test_extensions_are_lowercase(self):
        """Ensure all extensions are lowercase with leading dot."""
        for ext in MEDIA_EXTENSIONS:
            self.assertTrue(ext.startswith('.'), f"Extension {ext} should start with '.'")
            self.assertEqual(ext, ext.lower(), f"Extension {ext} should be lowercase")

    def test_common_formats_included(self):
        """Ensure common media formats are included."""
        # Common image formats
        self.assertIn('.jpg', MEDIA_EXTENSIONS)
        self.assertIn('.png', MEDIA_EXTENSIONS)
        self.assertIn('.heic', MEDIA_EXTENSIONS)

        # Common video formats
        self.assertIn('.mp4', MEDIA_EXTENSIONS)
        self.assertIn('.mov', MEDIA_EXTENSIONS)
        self.assertIn('.avi', MEDIA_EXTENSIONS)

        # RAW formats
        self.assertIn('.cr2', MEDIA_EXTENSIONS)
        self.assertIn('.dng', MEDIA_EXTENSIONS)

    def test_no_duplicates(self):
        """Ensure there are no duplicate extensions."""
        ext_list = list(MEDIA_EXTENSIONS)
        self.assertEqual(len(ext_list), len(set(ext_list)), "MEDIA_EXTENSIONS should not contain duplicates")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
