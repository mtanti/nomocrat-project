#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Extract feature vectors that characterise all the page images in a directory.
'''

import argparse
from nomocrat_project.pages import extract_page_features


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description=(
            'This step 1 to extract a sample of pages.'
            ' Extract feature vectors that characterise all the page images in a directory.'
            ' Feature vectors are extracted using a layer from the Donut transformer (base-sized'
            ' model, fine-tuned on RVL-CDIP).'
        ),
    )
    parser.add_argument(
        'in_pages_path',
        help='The path to the directory containing the pages the featurise.',
    )
    parser.add_argument(
        'out_features_path',
        help='The path to the NumPy file containing the matrix of feature vectors.',
    )
    parser.add_argument(
        'layer',
        choices=[0, 1, 2, 3],
        type=int,
        default=2,
        help='The layer index of the transformer from which to extract features (0-3).',
    )
    parser.add_argument(
        'batch_size',
        type=int,
        default=2,
        help='The number of page images to process at once.',
    )
    parser.add_argument(
        'device',
        default='cpu',
        help='The PyTorch device name to run the transformer on (e.g. cpu or cuda).',
    )
    args = parser.parse_args()

    extract_page_features(
        in_pages_path=args.in_pages_path,
        out_features_path=args.out_features_path,
        layer=args.layer,
        batch_size=args.batch_size,
        device=args.device,
    )


#########################################
if __name__ == '__main__':
    main()
