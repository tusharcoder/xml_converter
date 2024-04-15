import argparse

import pytest
from unittest.mock import patch, mock_open, call
import xml_converter
import xml.etree.ElementTree as ET


# Sample XML data for testing
sample_xml = """<?xml version="1.0"?>
<root>
    <user>
        <name>John Doe</name>
        <age>30</age>
        <email>john@example.com</email>
    </user>
</root>"""

# Expected SQL output
expected_sql = """-- SQL Insert Statements for table `my_existing_table_name`
INSERT INTO my_existing_table_name (name, age, email) VALUES ('John Doe', '30', 'john@example.com');
"""

# Expected JSON output
expected_json = '''
{
    "root": {
        "user": {
            "name": "John Doe",
            "age": "30",
            "email": "john@example.com"
        }
    }
}
'''

def test_xml_to_sql():
    with patch("builtins.open", mock_open()) as mocked_file:
        with patch("xml.etree.ElementTree.parse") as mocked_parse:
            root = ET.fromstring(sample_xml)
            mocked_parse.return_value.getroot.return_value = root
            xml_converter.xml_to_sql("dummy.xml", "dummy.sql", "my_existing_table_name")
            calls = [
                call("-- SQL Insert Statements for table `my_existing_table_name`\n"),
                call("INSERT INTO my_existing_table_name (name, age, email) VALUES ('John Doe', '30', 'john@example.com');\n")
            ]
            mocked_file().write.assert_has_calls(calls, any_order=True)


import json


def test_xml_to_json():
    with patch("builtins.open", mock_open()) as mocked_file:
        with patch("xml.etree.ElementTree.parse") as mocked_parse:
            root = ET.fromstring(sample_xml)
            mocked_parse.return_value.getroot.return_value = root
            xml_converter.xml_to_json("dummy.xml", "dummy.json")

            # Collect all content written to the file
            written_content = ''.join(args[0] for args, _ in mocked_file().write.call_args_list)

            # Adjust expected JSON to match the output format
            expected_json = '''
            {
                "root": {
                    "user": {
                        "name": "John Doe",
                        "age": "30",
                        "email": "john@example.com"
                    }
                }
            }
            '''
            # Parse both strings into JSON objects
            written_json = json.loads(written_content)
            expected_json = json.loads(expected_json.strip())

            # Assert the JSON objects are equal
            assert written_json == expected_json, "The JSON content does not match the expected output."


def test_convert_xml_unsupported_format():
    with pytest.raises(ValueError):
        xml_converter.convert_xml("dummy.xml", "unsupported", "dummy.unsupported")

def test_main_with_args():
    test_args = ["xml_converter.py", "input.xml", "json"]
    with patch("argparse.ArgumentParser.parse_args") as mock_args:
        mock_args.return_value = argparse.Namespace(input_file="input.xml", output_format="json", output_file=None)
        with patch("xml_converter.convert_xml") as mock_convert:
            xml_converter.main()
            mock_convert.assert_called_once()
