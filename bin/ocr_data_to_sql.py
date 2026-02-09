#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Convert the processed OCR data into an SQL file in MySQL format.
'''

import argparse
import json
from nomocrat_project.annotations import OCRData
from nomocrat_project.annotations import convert_to_sql


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description='Convert the processed OCR data into an SQL file in MySQL format.',
    )
    parser.add_argument(
        'input_path',
        help='The path to the JSON file obtained from process_ocr_data.py.',
    )
    parser.add_argument(
        'output_path',
        help='The path to the SQL file (will be created if not exists).',
    )
    args = parser.parse_args()

    with open(args.input_path, 'r', encoding='utf-8') as f:
        data = OCRData(**json.load(f))

    sql = convert_to_sql(
        data=data,
    )

    with open(args.output_path, 'w', encoding='utf-8') as f:
        print(sql, file=f)


#########################################
if __name__ == '__main__':
    main()
