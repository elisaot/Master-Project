import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET


def extract_annotation_values(eaf_path):
    """Extract all <ANNOTATION_VALUE>...</ANNOTATION_VALUE> texts from an .eaf file."""
    tree = ET.parse(eaf_path)
    root = tree.getroot()

    values = []

    # Look for all <ANNOTATION_VALUE> tags regardless of tier
    for elem in root.findall(".//ANNOTATION_VALUE"):
        if elem.text:
            values.append(elem.text.strip())

    return values


def process_eaf_folder(folder_path):
    """Build a table containing filename, stem, and list of annotation values."""
    data = []

    for file_path in glob.glob(os.path.join(folder_path, "*.eaf")):
        filename = os.path.basename(file_path)
        stem = os.path.splitext(filename)[0]

        values = extract_annotation_values(file_path)

        data.append({"name": filename, "stem": stem, "value": values})

    df = pd.DataFrame(data)
    return df
