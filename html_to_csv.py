import argparse
from bs4 import BeautifulSoup
import pandas as pd

def parse_html_to_csv(input_file, output_file):
    # Load HTML content
    with open(input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all tables
    tables = soup.find_all('table')

    # Extract data from each table
    data = []
    for table in tables:
        table_rows = table.find_all('tr')
        for tr in table_rows:
            cells = tr.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]

            # Skip the row if it is empty
            if all(cell == '' for cell in row_data):
                continue
            
            if row_data:
                data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Cleaning and restructuring the DataFrame
    cleaned_data = []
    for index, row in df.iterrows():
        if len(row) > 1 and row[1]:  # Check if the second column exists and has data
            lumber_size = row[1]
            if index + 1 < len(df):
                follow_row = df.iloc[index + 1]  # The row right after the lumber size contains the data
                
                # Extract specific columns, assuming the structure of follow_row is consistent
                quantity = follow_row[2] if len(follow_row) > 2 else None
                board_footage = follow_row[6] if len(follow_row) > 6 else None
                lineal_footage = follow_row[7] if len(follow_row) > 7 else None
                
                cleaned_data.append([lumber_size, quantity, board_footage, lineal_footage])

    # Create a new DataFrame from the cleaned data
    clean_df = pd.DataFrame(cleaned_data, columns=['Lumber Size', 'Quantity', 'Board Footage', 'Lineal Footage'])

    # Save to CSV
    clean_df.to_csv(output_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert HTML table to CSV.')
    parser.add_argument('input_file', type=str, help='The HTML file to parse.')
    parser.add_argument('output_file', type=str, help='The CSV file to output.')
    args = parser.parse_args()

    parse_html_to_csv(args.input_file, args.output_file)
