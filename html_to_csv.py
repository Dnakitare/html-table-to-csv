import argparse
from bs4 import BeautifulSoup
import pandas as pd
import re
from fractions import Fraction

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
            cells = tr.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]

            # Skip the row if it is empty
            if all(cell == '' for cell in row_data):
                continue
            
            if row_data:
                data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)
    # print(df)

    # Extract relevant data based on HTML structure
    cleaned_data = []
    lumber_size = None

    for index, row in df.iterrows():
        if len(row) > 1 and 'SKU' in row[1]:
            if 'Sheathing' in row[2]:
                data_row = df.iloc[index + 1]
                lumber_size = data_row[2]
                quantity = data_row[3]
                board_footage = None
                lineal_footage = None
            else:
                if index > 0:  # Previous row is lumber size
                    lumber_size_row = df.iloc[index - 1]
                    lumber_size = lumber_size_row[1]  # Concatenate all items in the lumber size row
                if lumber_size and len(row) >= 8:
                    data_row = df.iloc[index + 1]
                    quantity = data_row[2]
                    if data_row[6] == '':
                        board_footage = data_row[7]
                        lineal_footage = data_row[8]
                    else:
                        board_footage = data_row[6]
                        lineal_footage = data_row[7]
            cleaned_data.append([lumber_size, quantity, board_footage, lineal_footage])

    # Create a new DataFrame from the cleaned data
    clean_df = pd.DataFrame(cleaned_data, columns=['Lumber Size', 'Quantity', 'Board Footage', 'Lineal Footage'])

    print(clean_df)

    # Save to CSV
    clean_df.to_csv(output_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert HTML table to CSV.')
    parser.add_argument('input_file', type=str, help='The HTML file to parse.')
    parser.add_argument('output_file', type=str, help='The CSV file to output.')
    args = parser.parse_args()

    parse_html_to_csv(args.input_file, args.output_file)