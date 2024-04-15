import argparse
import json
import os
from datetime import datetime
from xmlutils.xml2csv import xml2csv
from xmlutils.xml2json import xml2json
from xmlutils.xml2sql import xml2sql
import xml.etree.ElementTree as ET

TABLE_NAME="my_existing_table_name"

def xml_to_sql(xml_file, sql_file, table_name):
    # Parse XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Open SQL file for writing
    with open(sql_file, 'w') as file:
        # Helper function to create SQL insert statement
        def create_insert_statement(elem):
            # Extract data from elem (modify according to your XML structure)
            # Example assumes elements are structured as <user><name>...</name><age>...</age><email>...</email></user>
            columns = []
            values = []
            for child in elem:
                columns.append(child.tag)
                values.append(f"'{child.text}'" if isinstance(child.text, str) else child.text)

            columns_str = ', '.join(columns)
            values_str = ', '.join(values)
            return f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});\n"

        # Write a comment or header in SQL file
        file.write(f"-- SQL Insert Statements for table `{table_name}`\n")

        # Iterate over each child of the root and generate an insert statement
        for child in root:
            sql_statement = create_insert_statement(child)
            file.write(sql_statement)
def xml_to_json(xml_file, json_file):
    # Parse XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Helper function to convert XML element to dictionary
    def elem_to_dict(elem):
        d = {elem.tag: {} if elem.attrib else None}
        children = list(elem)
        if children:
            dd = {}
            for dc in map(elem_to_dict, children):
                for k, v in dc.items():
                    if k in dd:
                        dd[k].append(v)
                    else:
                        dd[k] = [v]
            d = {elem.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if elem.text:
            text = elem.text.strip()
            if children or elem.attrib:
                if text:
                    d[elem.tag]['text'] = text
            else:
                d[elem.tag] = text
        return d

    data_dict = elem_to_dict(root)

    # Write JSON file
    with open(json_file, 'w') as f:
        json.dump(data_dict, f, indent=4)
def convert_xml(input_file, output_format, output_file=None):
    # If output_file is not provided, generate one based on the current datetime
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f"{timestamp}.{output_format}"

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Perform the conversion based on the output_format
    if output_format == 'csv':
        converter = xml2csv(input_file, output_file, encoding="utf-8")
        converter.convert(tag="user")  # Assuming 'row' is the repeated element
    elif output_format == 'json':
        xml_to_json(input_file, output_file)
    elif output_format == 'sql':
        xml_to_sql(input_file, output_file, TABLE_NAME)
    else:
        raise ValueError("Unsupported output format. Choose 'csv', 'json', or 'sql'.")

    print(f"File converted to {output_format} and saved as {output_file}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Convert XML to CSV, SQL, or JSON")
    parser.add_argument("input_file", help="Path to the input XML file")
    parser.add_argument("output_format", choices=['csv', 'json', 'sql'], help="Output format: csv, json, or sql")
    parser.add_argument("-o", "--output_file", help="Output file path (optional)")

    args = parser.parse_args()

    # Run the conversion
    convert_xml(args.input_file, args.output_format, args.output_file)

if __name__ == "__main__":
    main()

