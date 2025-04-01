#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Cluster the page images using the centroids extracted by create_page_cluster_controids.
'''

import argparse
from nomocrat_project.pages import cluster_pages_with_existing_centroids


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description=(
            'This is step 3 to extract a sample of pages (following'
            ' create_page_cluster_centroids.py).'
            ' Cluster the page images using the centroids extracted by'
            ' create_page_cluster_controids.py.'
            ' The pages in each cluster are copied into a separate directory.'
        ),
    )
    parser.add_argument(
        'in_features_path',
        help='The path to the NumPy page features file.',
    )
    parser.add_argument(
        'in_pages_dir',
        help='The path to the page images directory.',
    )
    parser.add_argument(
        'in_estimator_path',
        help='The path to the optimised sklearn k-means estimator.',
    )
    parser.add_argument(
        'out_clusters_dir',
        help=(
            'The path to the directory that will contain the clustered pages (will be created if'
            ' not exists).'
        ),
    )
    args = parser.parse_args()

    cluster_pages_with_existing_centroids(
        in_features_path=args.in_features_path,
        in_pages_dir=args.in_pages_dir,
        in_estimator_path=args.in_estimator_path,
        out_clusters_dir=args.out_clusters_dir,
    )


#########################################
if __name__ == '__main__':
    main()
