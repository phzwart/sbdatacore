from sbdatacore.dates import *
import pytest
from datetime import datetime

def test_standard_format():
    # Test standard MMDDYY format
    assert convert_mdy("123123") == "2023_12_31"

def test_short_year_format():
    # Test MMDYY format (January 13, 2023)
    assert convert_mdy("11323") == "2023_01_13"

def test_invalid_format():
    # Test invalid format
    assert convert_mdy("1234") == "Invalid format"

def test_ambiguous_date():
    # Test ambiguous date (should choose the year closest to the current year)
    today = datetime.today()
    year_str = str(today.year - 1)[2:]  # Last year
    expected_year = str(today.year - 1)
    assert convert_mdy(f"0101{year_str}") == f"{expected_year}_01_01"

def test_future_date():
    # Test future date (should choose the year closest to the current year)
    today = datetime.today()
    year_str = str(today.year + 1)[2:]  # Next year
    expected_year = str(today.year + 1)
    assert convert_mdy(f"0101{year_str}") == f"{expected_year}_01_01"

def test_edge_case_leap_year():
    # Test edge case for leap year
    assert convert_mdy("022900") == "2000_02_29"

