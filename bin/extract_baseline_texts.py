#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Extract text from the pages of the PDFs as indicated in a given pipline data.
The extracted text will serve as a baseline for comparing against the OCR system.
'''

import argparse
import json
from nomocrat_project.annotations import (
    extract_baseline_texts,
    PipelineData,
)


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description=(
            'Extract text from the pages of the PDFs as indicated in a given pipline data.'
            ' The extracted text will serve as a baseline for comparing against the OCR system.'
        ),
    )
    parser.add_argument(
        'docs_dir',
        help='The path to the directory containing the documents. Must be PDFs.',
    )
    parser.add_argument(
        'pipeline_path',
        help=(
            'The path to the JSON file obtained by using generate_pipeline_data_draft.py.'
            ' This is used as a reference for which documents and pages to extract text from.'
        ),
    )
    parser.add_argument(
        'output_path',
        help='The path to the JSON file containing the extracted texts.',
    )
    args = parser.parse_args()

    with open(args.pipeline_path, 'r', encoding='utf-8') as f:
        pipeline_data = PipelineData(**json.load(f))

    data = extract_baseline_texts(
        docs_dir=args.docs_dir,
        pipeline_data=pipeline_data,
    )
    with open(args.output_path, 'w', encoding='utf-8') as f:
        json.dump(
            data.model_dump(mode='json'),
            f,
            ensure_ascii=False,
            indent=4,
        )


#########################################
if __name__ == '__main__':
    main()
