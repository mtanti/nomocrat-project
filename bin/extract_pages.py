#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Extract all the pages from a directory of documents as images.
'''

import argparse
from nomocrat_project.pages import extract_pages


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description='Extract all the pages from a directory of documents as images.',
    )
    parser.add_argument(
        'input_path',
        help='The path to the directory containing the documents (*.pdf, *.docx, *.doc).',
    )
    parser.add_argument(
        'output_path',
        help=(
            'The path to the directory to contain the page images (*.jpg) (will be created if not'
            ' exists).'
        ),
    )
    args = parser.parse_args()

    extract_pages(
        in_docs_dir=args.input_path,
        out_pages_dir=args.output_path,
    )


#########################################
if __name__ == '__main__':
    main()
