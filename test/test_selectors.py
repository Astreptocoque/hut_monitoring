#!/usr/bin/env python3
"""
Selector Test Utility
=====================
Test and debug CSS selectors against saved HTML snapshots.
Useful for validating selectors before running the full automation.

Usage:
    python test_selectors.py <html_file>

Example:
    python test_selectors.py "dev files/Hut Reservation Popup Open.html"
"""

import sys
from pathlib import Path
from html.parser import HTMLParser
import re


class SelectorTester(HTMLParser):
    """Simple HTML parser to test CSS selectors."""
    
    def __init__(self):
        super().__init__()
        self.elements = []
        self.current_element = None
        self.in_tbody = False
        self.mat_rows = []
        self.data_rows = []
        self.expansion_rows = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Track tbody context
        if tag == "tbody":
            self.in_tbody = True
            
        # Look for mat-row elements
        if tag == "mat-row":
            attrs_dict['_tag'] = tag
            self.mat_rows.append(attrs_dict)
            
            # Classify as data or expansion row
            if "aria-expanded" in attrs_dict:
                self.data_rows.append(attrs_dict)
            elif "class" in attrs_dict and "expand_row" in attrs_dict.get("class", ""):
                self.expansion_rows.append(attrs_dict)
                
        # Track regular tr elements
        elif tag == "tr" and self.in_tbody:
            attrs_dict['_tag'] = tag
            self.elements.append(attrs_dict)
            
        # Track td elements for cell analysis
        elif tag == "td":
            if "class" in attrs_dict:
                class_list = attrs_dict["class"].split()
                if any("table_row_places" in cls for cls in class_list):
                    print(f"  Found places cell: {attrs_dict}")
                    
    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_tbody = False


def test_selectors(html_file):
    """Parse HTML and test various selectors."""
    
    if not Path(html_file).exists():
        print(f"Error: File not found: {html_file}")
        return False
        
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    print(f"Analyzing: {html_file}")
    print("=" * 70)
    
    # Test 1: Find app-availability-table
    if "<app-availability-table" in html_content:
        print("✓ Found: <app-availability-table> component")
    else:
        print("✗ Missing: <app-availability-table> component")
        return False
    
    # Test 2: Find mat-row elements
    mat_row_count = html_content.count("<mat-row")
    print(f"✓ Found {mat_row_count} <mat-row> elements")
    
    # Test 3: Find mat-rows with aria-expanded
    aria_expanded_pattern = r'<mat-row[^>]*aria-expanded="false"[^>]*>'
    aria_expanded_count = len(re.findall(aria_expanded_pattern, html_content))
    print(f"✓ Found {aria_expanded_count} <mat-row> with aria-expanded='false' (data rows)")
    
    # Test 4: Find expansion rows
    expand_row_pattern = r'<mat-row[^>]*class="[^"]*expand_row[^"]*"[^>]*>'
    expand_row_count = len(re.findall(expand_row_pattern, html_content))
    print(f"✓ Found {expand_row_count} <mat-row> with class='expand_row' (expansion rows)")
    
    # Test 5: Find places cells
    places_cell_pattern = r'<td[^>]*class="[^"]*table_row_places[^"]*"[^>]*>'
    places_count = len(re.findall(places_cell_pattern, html_content))
    print(f"✓ Found {places_count} <td> with class containing 'table_row_places'")
    
    # Test 6: Extract actual numbers from places cells
    print("\nExtracted availability numbers:")
    places_content_pattern = r'<td[^>]*class="[^"]*table_row_places[^"]*"[^>]*>\s*(\d+)'
    numbers = re.findall(places_content_pattern, html_content)
    if numbers:
        print(f"  Places: {numbers}")
    else:
        print("  (No numbers found)")
    
    # Test 7: Parse for dates
    print("\nExtracted dates:")
    date_pattern = r'<span[^>]*>\s*(\d{1,2}\.\d{2}\.\d{4})\s*</span>'
    dates = re.findall(date_pattern, html_content)
    if dates:
        print(f"  Dates found: {dates}")
    else:
        print("  (No dates found)")
    
    # Test 8: Verify data matches
    print(f"\nValidation:")
    if aria_expanded_count == places_count and aria_expanded_count == len(dates):
        print(f"  ✓ Consistent: {aria_expanded_count} data rows with dates and availability")
    else:
        print(f"  ⚠ Mismatch: rows={aria_expanded_count}, places={places_count}, dates={len(dates)}")
    
    print("\n" + "=" * 70)
    print("Selector Summary:")
    print(f"  Primary selector:  mat-row[aria-expanded]")
    print(f"    -> Finds {aria_expanded_count} rows")
    print(f"  Cell selector:     td[class*='table_row_places']")
    print(f"    -> Finds {places_count} cells")
    print(f"  Number extraction: \\d+ from cell content")
    print(f"    -> Extracts: {numbers if numbers else '(none found)'}")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    html_file = sys.argv[1]
    success = test_selectors(html_file)
    sys.exit(0 if success else 1)
