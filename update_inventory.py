#!/usr/bin/env python3
"""
Portor Inventory Update Script
Pulls inventory data from Google Sheets and converts to JSON for the HTML frontend.
Designed to run via GitHub Actions at 7:30 AM Eastern daily.
"""

import csv
import json
import urllib.request
import re
from datetime import datetime, timezone
from io import StringIO

# Google Sheet configuration
SHEET_ID = "1AaWJw1UUxlNmU1QjAleMNLg5JvqS_pp5J0qav1HhZEQ"

# Tab configurations: (gid, output_key, display_name)
TABS = [
    ("618370816", "inventory", "Inventory List"),
    # Add Clearance and Closeout tab GIDs here once confirmed
    # ("CLEARANCE_GID", "clearance", "Clearance"),
    # ("CLOSEOUT_GID", "closeout", "Closeout"),
]

# Category mapping to standardize categories to match pricing sheet
CATEGORY_MAP = {
    # Area Light related
    "Area Light": "Area Light",
    "AL2 Shield": "Area Light",
    "Arm Mounts": "Tenons",
    
    # Basic categories
    "Barn Light": "Barn Light", 
    "Bollard": "Bollard",
    "Canopy": "Canopy",
    "Corn Bulb": "Corn Bulb",
    
    # Downlights
    "Downlight": "Downlights",
    
    # Emergency
    "Emergency Light": "Exit & Emergency",
    
    # Flood Light
    "Flood Light": "Flood Light",
    "CLFL1 Flood Light": "Flood Light",
    "High Output Flood Light": "Flood Light",
    "Mini Flood Light": "Flood Light",
    
    # High Bay
    "Linear High Bay": "Linear High Bay",
    "High Bay - Linear": "Linear High Bay",
    "Die-cast Linear High Bay": "Linear High Bay",
    "Twin Lens Linear High Bay": "Linear High Bay",
    "Round High Bay": "Round High Bay",
    "High Bay - Round": "Round High Bay",
    "CLRHF High Bay Round": "Round High Bay",
    
    # Panel
    "Flat Panel": "Flat Panel",
    "Panel - Backlit": "Flat Panel",
    
    # Sports
    "Sports Light": "Sports Light",
    "Sport Light": "Sports Light",
    
    # Stairwell
    "Stairwell": "Stairwell",
    "Stairwell Light": "Stairwell",
    
    # Strip
    "Strip Light": "Strip Light",
    "LS1": "Strip Light",
    
    # Tenons
    "Tenons": "Tenons",
    
    # Troffer
    "Troffer": "Troffer",
    
    # Tubes
    "Tube": "Tube",
    "Tubes": "Tube",
    "LED Module": "Tube",
    
    # Vapor
    "Vapor Seal": "Vapor Seal",
    "CLVS Vapor-Seal": "Vapor Seal",
    "Vaportight": "Vaportight",
    "Vapor Tight Series 2": "Vaportight",
    "CLTP Tri-Proof": "Vaportight",
    
    # Wall Pack
    "Wall Pack": "Wall Pack",
    
    # Wraparound
    "Wraparound": "Wraparound",
    
    # Controls
    "Controls": "Controls",
    "TEELIO": "Controls",
    
    # Accessories
    "Accessories": "Accessories",
}

def map_category(raw_category):
    """Map raw category from sheet to standardized category."""
    return CATEGORY_MAP.get(raw_category, raw_category)

def fetch_sheet_csv(sheet_id, gid):
    """Fetch a Google Sheet tab as CSV."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching sheet (gid={gid}): {e}")
        return None

def parse_inventory_csv(csv_content):
    """Parse the inventory CSV into structured data."""
    reader = csv.reader(StringIO(csv_content))
    rows = list(reader)
    
    # Find the header row - it's the one with "Item# / SKU" in column B (index 1)
    header_row_idx = None
    for i, row in enumerate(rows):
        if len(row) > 1 and ("Item# / SKU" in str(row[1]) or "Item#" in str(row[1])):
            header_row_idx = i
            break
    
    if header_row_idx is None:
        print("Could not find header row")
        return []
    
    # Column mapping based on the sheet structure:
    # Col 0: Category/Subcategory label
    # Col 1: SKU
    # Col 2: Description
    # Col 3: Wattage
    # Col 4: Ontario
    # Col 5: Louisville
    # Col 6: Phoenix
    # Col 7: Dallas
    # Col 8: Chicago
    # Col 9: Total
    # Col 10: Notes
    
    # Parse data rows
    products = []
    current_category = ""
    current_subcategory = ""
    
    for row in rows[header_row_idx + 1:]:
        if len(row) < 2:
            continue
        
        first_col = row[0].strip() if row[0] else ""
        sku_col = row[1].strip() if len(row) > 1 and row[1] else ""
        
        # Skip completely empty rows
        if not first_col and not sku_col:
            continue
        
        # Main category row: has text in first column, nothing meaningful in other columns
        # These are rows like "Area Light", "Bollard", "Barn Light", etc.
        if first_col and not sku_col:
            # Check if remaining columns are mostly empty (main category indicator)
            other_cols_empty = all(not (row[i].strip() if len(row) > i else "") for i in range(2, min(10, len(row))))
            if other_cols_empty:
                current_category = first_col.replace('\n', ' ').strip()
                current_subcategory = ""
                continue
        
        # Subcategory + product row: has text in first column AND SKU in second column
        # These are rows like "Area Light Fixtures, PT-AL2N-150-3CP, ..."
        if first_col and sku_col:
            # The first column is the subcategory
            current_subcategory = first_col.replace('\n', ' ').strip()
        
        # Product row: has SKU (could have empty first column if it's a continuation)
        if sku_col:
            # Build product record with mapped category
            product = {
                'sku': sku_col,
                'description': row[2].strip() if len(row) > 2 else "",
                'wattage': row[3].strip() if len(row) > 3 else "",
                'category': map_category(current_category),
                'subcategory': current_subcategory,
                'ontario': parse_int(row[4] if len(row) > 4 else "0"),
                'louisville': parse_int(row[5] if len(row) > 5 else "0"),
                'phoenix': parse_int(row[6] if len(row) > 6 else "0"),
                'dallas': parse_int(row[7] if len(row) > 7 else "0"),
                'chicago': parse_int(row[8] if len(row) > 8 else "0"),
                'total': parse_int(row[9] if len(row) > 9 else "0"),
                'notes': row[10].strip() if len(row) > 10 else "",
            }
            products.append(product)
    
    return products

def parse_int(value):
    """Parse a string to int, handling commas and empty values."""
    if not value:
        return 0
    # Remove commas and whitespace
    cleaned = re.sub(r'[,\s]', '', str(value))
    try:
        return int(cleaned)
    except ValueError:
        return 0

def main():
    """Main function to fetch and process inventory data."""
    print(f"Starting inventory update at {datetime.now(timezone.utc).isoformat()}")
    
    all_data = {
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'updated_at_pacific': datetime.now(timezone.utc).strftime('%B %d, %Y'),
        'tabs': {}
    }
    
    for gid, key, name in TABS:
        print(f"Fetching {name} (gid={gid})...")
        csv_content = fetch_sheet_csv(SHEET_ID, gid)
        
        if csv_content:
            products = parse_inventory_csv(csv_content)
            all_data['tabs'][key] = {
                'name': name,
                'products': products,
                'count': len(products)
            }
            print(f"  Parsed {len(products)} products")
        else:
            print(f"  Failed to fetch {name}")
    
    # Write JSON output
    output_path = 'inventory_data.json'
    with open(output_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Wrote {output_path}")
    print("Update complete!")

if __name__ == "__main__":
    main()
