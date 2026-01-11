#!/usr/bin/env python3
"""
CSV Template Reader
Reusable helper for reading 2-column Field/Value CSV templates.
"""

import csv
from typing import Dict, Optional


def read_field_value_csv(path: str, encoding: str = "utf-8-sig") -> Dict[str, str]:
    """
    Read a 2-column CSV: Field,Value (with header row).
    Trims whitespace around fields and values.
    
    Args:
        path: Path to CSV file
        encoding: File encoding (utf-8-sig handles BOM)
    
    Returns:
        Dictionary mapping field names to values
    
    Example CSV:
        Field,Value
        Customer Name,Acme Corp
        Email,admin@acme.com
    """
    data = {}
    with open(path, newline="", encoding=encoding) as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip header
        for row in reader:
            if not row or len(row) < 2:
                continue
            field, value = row[0].strip(), row[1].strip()
            if field:
                data[field] = value
    return data


def read_multi_column_csv(path: str, key_field: str, encoding: str = "utf-8-sig") -> list[Dict[str, str]]:
    """
    Read a multi-column CSV with headers, returning list of dicts.
    
    Args:
        path: Path to CSV file
        key_field: Optional field to use as unique key validation
        encoding: File encoding
    
    Returns:
        List of dictionaries, one per row
    """
    rows = []
    with open(path, newline="", encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Strip whitespace from all values
            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            rows.append(cleaned)
    return rows


def validate_required_fields(data: Dict[str, str], required_fields: list[str]) -> list[str]:
    """
    Validate that all required fields are present and non-empty.
    
    Args:
        data: Dictionary of field values
        required_fields: List of required field names
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    return errors
