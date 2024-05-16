import argparse
from bs4 import BeautifulSoup
import pandas as pd
import re
from fractions import Fraction
import os

def parse_html_to_csv(input_file):
    # Check that the input file is an HTML file
    if not input_file.endswith('.html'):
        raise ValueError("Input file must be an HTML file")

    # Generate the output file path
    output_file = os.path.splitext(input_file)[0] + '.csv'

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
                    lumber_size = ' '.join(lumber_size_row.dropna())  # Concatenate all items in the lumber size row
                if lumber_size and len(row) >= 8:
                    data_row = df.iloc[index + 1]
                    quantity = data_row[2]
                    if data_row[6] == '':
                        board_footage = data_row[7]
                        lineal_footage = data_row[8]
                    else:
                        board_footage = data_row[6]
                        lineal_footage = data_row[7]
            # trim any leading or trailing whitespace
            lumber_size = lumber_size.strip() if lumber_size else None
            quantity = int(quantity.strip()) if quantity else None
            board_footage = float(board_footage.strip()) if board_footage else None
            lineal_footage = lineal_footage.strip() if lineal_footage else None
            cleaned_data.append([lumber_size, quantity, board_footage, lineal_footage])

    # Create a new DataFrame from the cleaned data
    df = pd.DataFrame(cleaned_data, columns=['Lumber Size', 'Quantity', 'Board Footage', 'Lineal Footage'])

    # Function to convert feet and inches to inches
    def to_inches(lineal_footage):
        # If the measurement is None or empty, treat it as 0 feet 0 inches
        if not lineal_footage:
            return 0
        
        # Split the string into feet and inches parts
        parts = lineal_footage.split("'")
        feet = int(parts[0].strip())
        inches_part = parts[1].strip().replace('"', '')

        # Handle inches and optional fractional inches
        if '-' in inches_part:
            inches, fraction = inches_part.split('-')
            inches = int(inches)
            fractional_inches = float(Fraction(fraction))
        else:
            inches = int(inches_part)
            fractional_inches = 0

        total_inches = feet * 12 + inches + fractional_inches
        return total_inches

    # Function to convert inches back to feet and inches
    def to_feet_and_inches(total_inches):
        feet = total_inches // 12
        inches = total_inches % 12
        return f"{int(feet)}' {inches}\""

    # Convert Lineal Footage to inches for aggregation
    df['Lineal Footage (inches)'] = df['Lineal Footage'].apply(lambda x: to_inches(x) if pd.notnull(x) else 0)

    # Convert Board Footage to float
    df['Board Footage'] = pd.to_numeric(df['Board Footage'], errors='coerce')

    # Aggregate data by Lumber Size
    aggregated_data = df.groupby('Lumber Size').agg({
        'Quantity': 'sum',
        'Board Footage': lambda x: round(x.sum(), 2) if x.dtype == 'float64' else None,
        'Lineal Footage (inches)': lambda x: x.sum() if x.dtype == 'float64' else None
    }).reset_index()

    # Convert aggregated Lineal Footage back to feet and inches
    aggregated_data['Lineal Footage'] = aggregated_data['Lineal Footage (inches)'].apply(to_feet_and_inches)

    # if board footage is 0 or NaN, set it to None
    aggregated_data['Board Footage'] = aggregated_data['Board Footage'].apply(lambda x: None if x == 0 else x)
    # if lineal footage is 0, set it to None
    aggregated_data['Lineal Footage'] = aggregated_data['Lineal Footage'].apply(lambda x: None if x == "0' 0.0\"" else x)

    # Drop the intermediate column
    aggregated_data = aggregated_data.drop(columns=['Lineal Footage (inches)'])

    # Save to CSV
    aggregated_data.to_csv(output_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert HTML table to CSV.')
    parser.add_argument('input_file', type=str, help='The HTML file to parse.')
    args = parser.parse_args()

    parse_html_to_csv(args.input_file)
