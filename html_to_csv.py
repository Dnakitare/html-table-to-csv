import argparse
from bs4 import BeautifulSoup
import pandas as pd

def parse_html_to_csv(input_file, output_file):
    # Load HTML content
    with open(input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find data points
    table_rows = soup.find_all('tr')

    # Extract data from each row
    data = []
    for tr in table_rows:
        cells = tr.find_all('td')
        row_data = [cell.text.strip() for cell in cells]

        # Skip the row if it is empty
        if all(cell == '' for cell in row_data):
            continue
        
        if row_data:
            data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(output_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert HTML table to CSV.')
    parser.add_argument('input_file', type=str, help='The HTML file to parse.')
    parser.add_argument('output_file', type=str, help='The CSV file to output.')
    args = parser.parse_args()

    parse_html_to_csv(args.input_file, args.output_file)
    