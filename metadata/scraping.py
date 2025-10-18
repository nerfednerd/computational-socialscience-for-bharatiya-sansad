import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_members_of_the_17th_Lok_Sabha"

# Headers to avoid 403 error
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fetch the page
response = requests.get(url, headers=headers)
response.raise_for_status()

# Parse the HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Find all tables with class 'wikitable'
tables = soup.find_all('table', class_='wikitable')

print(f"Found {len(tables)} tables on the page\n")

def extract_table_with_colspan(table):
    """Extract table data handling colspan and rowspan attributes"""
    rows = []
    
    # Get all rows
    all_rows = table.find_all('tr')
    
    for row_idx, tr in enumerate(all_rows):
        cells = []
        for cell in tr.find_all(['th', 'td']):
            # Get cell text
            text = cell.get_text(strip=True)
            
            # Get colspan value (default 1)
            colspan = int(cell.get('colspan', 1))
            
            # Add the cell value, repeating for colspan
            for _ in range(colspan):
                cells.append(text)
        
        if cells:
            rows.append(cells)
    
    return rows

# Process each table
all_data = []

for idx, table in enumerate(tables, 1):
    print(f"Processing Table {idx}...")
    
    # Extract table data with colspan handling
    table_data = extract_table_with_colspan(table)
    
    if not table_data:
        print(f"  No data found in this table\n")
        continue
    
    # First row as headers
    headers = table_data[0]
    data_rows = table_data[1:]
    
    # Ensure all rows have the same length as headers
    max_cols = len(headers)
    adjusted_rows = []
    
    for row in data_rows:
        if len(row) < max_cols:
            row = row + [''] * (max_cols - len(row))
        elif len(row) > max_cols:
            row = row[:max_cols]
        adjusted_rows.append(row)
    
    # Create DataFrame
    if adjusted_rows:
        df = pd.DataFrame(adjusted_rows, columns=headers)
        
        print(f"  Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Columns: {list(df.columns)}")
        
        # Show first few rows
        print(f"\n  Preview:")
        print(df.head(3).to_string(index=False))
        print("\n")
        
        all_data.append(df)
    else:
        print(f"  No data rows found in this table\n")

# Save combined file
if all_data:
    print(f"\nCombining all {len(all_data)} tables into master CSV...")
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv("lok_sabha_all_members.csv", index=False, encoding='utf-8-sig')
    print(f"✓ Master file saved: lok_sabha_all_members.csv")
    print(f"✓ Total rows: {len(combined_df)}")
    print(f"✓ Total columns: {len(combined_df.columns)}")
else:
    print("\nNo data extracted from tables.")

print("\nScraping completed!")