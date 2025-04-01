#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Use k-means to extract centroid vectors that would optimally cluster the page feature vectors
extracted using `extract_page_features`.
'''

import argparse
from nomocrat_project.pages import create_page_cluster_centroids


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description=(
            'This is step 2 to extract a sample of pages (following extract_page_features.py).'
            ' Use k-means to extract centroid vectors that would optimally cluster the page feature'
            ' vectors extracted using extract_page_features.py.'
            ' Multiple values of \'k\' are attempted and the one that gives the best silhouette'
            ' score is used.'
            ' The reason why this process does not also perform the clustering is to be able'
            ' to cluster more pages using the same centroids, allowing for the sampling process to'
            ' work on more images.'
        ),
    )
    parser.add_argument(
        'input_features_path',
        help='The path to the (input) NumPy file containing the page feature vectors.',
    )
    parser.add_argument(
        'out_cluster_report_path',
        help=(
            'The path to the (output) text file containing a report about the clustering'
            ' performance.'
        ),
    )
    parser.add_argument(
        'out_estimator_path',
        help='The path to the (output) optimised sklearn k-means estimator Pickle file.',
    )
    parser.add_argument(
        'max_clusters',
        type=int,
        default=20,
        help='The maximum number of clusters to attempt.',
    )
    parser.add_argument(
        'seed',
        type=int,
        default=0,
        help='The random seed to use when clustering.',
    )
    args = parser.parse_args()

    create_page_cluster_centroids(
        in_features_path=args.in_features_path,
        out_cluster_report_path=args.out_cluster_report_path,
        out_estimator_path=args.out_estimator_path,
        max_clusters=args.max_clusters,
        seed=args.seed,
    )


#########################################
if __name__ == '__main__':
    main()
