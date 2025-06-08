#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Extract a more useful version of Label Studio's annotations file.
'''

import argparse
import json
from nomocrat_project.annotations import import_ocr_data


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description='Extract a more useful version of Label Studio\'s annotations file.',
    )
    parser.add_argument(
        'input_path',
        help='The path to the file obtained from Label Studio via export -> JSON-min.',
    )
    parser.add_argument(
        'output_path',
        help='The path to the new JSON file.',
    )
    args = parser.parse_args()

    data = import_ocr_data(
        path=args.input_path,
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
