#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Convert the processed layout data into an HTML file for easy visualisation.
'''

import argparse
import json
from nomocrat_project.annotations import LayoutData
from nomocrat_project.annotations import visualise_layout_as_html


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description='Convert the processed layout data into an HTML file for easy visualisation.',
    )
    parser.add_argument(
        'input_path',
        help='The path to the JSON file obtained from process_layout_data.py.',
    )
    parser.add_argument(
        'pages_path',
        help='The path to the directory containing the page images that were annotated.',
    )
    parser.add_argument(
        'output_path',
        help=(
            'The path to the directory to contain the HTML file and images (will be created if not'
            ' exists).'
        ),
    )
    args = parser.parse_args()

    with open(args.input_path, 'r', encoding='utf-8') as f:
        data = LayoutData(**json.load(f))

    visualise_layout_as_html(
        pages_path=args.pages_path,
        data=data,
        output_path=args.output_path,
    )


#########################################
if __name__ == '__main__':
    main()
