import pandas as pd

import xml.etree.ElementTree as ET

def parse_test_report(xml_file):
    """
    Parse a generic XML test report and extract test details.

    Args:
        xml_file (str): Path to the XML file.

    Returns:
        pd.DataFrame: DataFrame containing test details in a standardized schema.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    test_data = []

    for testcase in root.iter('testcase'):
        test_name = testcase.attrib.get('name', 'Unknown')
        execution_time = float(testcase.attrib.get('time', 0))
        status = 'passed'
        error_message = None

        # Check for failure or error
        failure = testcase.find('failure')
        error = testcase.find('error')
        if failure is not None:
            status = 'failed'
            error_message = failure.text
        elif error is not None:
            status = 'error'
            error_message = error.text

        test_data.append({
            'test_name': test_name,
            'execution_time': execution_time,
            'status': status,
            'error_message': error_message
        })

    # Convert to pandas DataFrame
    df = pd.DataFrame(test_data)
    return df