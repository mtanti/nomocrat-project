#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Generate a draft pipeline data set showing what the target output should be when transcribing
a whole page.
'''

import argparse
import json
import re
from nomocrat_project.annotations import (
    generate_pipeline_data_draft,
    OCRData,
    LayoutData,
)


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description=(
            'Generate a draft pipeline data set showing what the target output should be when'
            ' transcribing a whole page.'
        ),
    )
    parser.add_argument(
        'ocr_data_path',
        help='The path to the JSON file obtained by using process_ocr_data.py.',
    )
    parser.add_argument(
        'layout_data_path',
        help='The path to the JSON file obtained by using process_layout_data.py.',
    )
    parser.add_argument(
        'output_path',
        help='The path to the new draft data set JSON file.',
    )
    args = parser.parse_args()

    with open(args.ocr_data_path, 'r', encoding='utf-8') as f:
        ocr_data = OCRData(**json.load(f))
    with open(args.layout_data_path, 'r', encoding='utf-8') as f:
        layout_data = LayoutData(**json.load(f))

    data = generate_pipeline_data_draft(
        ocr_data=ocr_data,
        layout_data=layout_data,
    )
    json_output = json.dumps(
        data.model_dump(mode='json'),
        f,
        ensure_ascii=False,
        indent=4,
    )

    # Make all the boxes a single line for easier manipulation.
    reformatted_json_output = re.sub(
        '^                    \\{.*?^                    \\}',
        lambda m: '                    ' + json.dumps(json.loads(m.group(0)), ensure_ascii=False),
        json_output,
        flags=re.DOTALL|re.MULTILINE,
    )

    with open(args.output_path, 'w', encoding='utf-8') as f:
        f.write(reformatted_json_output)


#########################################
if __name__ == '__main__':
    main()
