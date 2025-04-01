#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Marc Tanti
#
# This file is part of NOMOCRAT project.
'''
Create a stratified sample of pages by randomly sampling an equal amount of samples from each
cluster created using cluster_pages_with_existing_centroids.
'''

import argparse
from nomocrat_project.pages import stratified_sample_clusters


#########################################
def main(
) -> None:
    '''
    Main function.
    '''
    parser = argparse.ArgumentParser(
        description=(
            'This is step 4 to extract a sample of pages (following'
            ' cluster_pages_with_existing_centroids.py).'
            ' Create a stratified sample of pages by randomly sampling an equal amount of samples'
            ' from each cluster created using cluster_pages_with_existing_centroids.py.'
            ' Since the cluster sizes can be very imbalanced, simply dividing the desired number of'
            ' samples by the number of clusters and sampling that amount from each cluster might'
            ' not result in the desired number of samples (because some clusters would be smaller'
            ' than that amount).'
            ' To get around this, the process first searches for the sample-per-cluster amount'
            ' that will result in the total sample size being closest to the desired sample size.'
            ' The process is also designed in such a way that the created sample is extendable'
            ' such that running it again with the same seed and a bigger sample size will result in'
            ' the previous sample plus some extra items added to it (it does not create a'
            ' completely new random sample).'
        ),
    )
    parser.add_argument(
        'in_clusters_dir',
        help=(
            'The path to the directory containing the clustered page images obtained using'
            ' cluster_pages_with_existing_centroids.py.'
        ),
    )
    parser.add_argument(
        'out_samples_dir',
        help=(
            'The path to the directory that will contain the sample (unclustered) (will be created'
            ' if not exists).'
        ),
    )
    parser.add_argument(
        'num_samples',
        type=int,
        help=(
            'The desired number of samples to extract (the closest possible number of samples to'
            ' this desired amount will be extracted).'
        ),
    )
    args = parser.parse_args()

    stratified_sample_clusters(
        in_clusters_dir=args.in_clusters_dir,
        out_samples_dir=args.out_samples_dir,
        num_samples=args.num_samples,
    )


#########################################
if __name__ == '__main__':
    main()
