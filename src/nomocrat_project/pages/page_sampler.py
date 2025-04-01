'''
Page sampling related functions.
'''

import os
import pickle
import shutil
import random
from typing import Optional
import numpy as np
import tqdm
from PIL import Image
import torch
from transformers import logging, DonutProcessor, VisionEncoderDecoderModel
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

logging.set_verbosity_error()


##########################################################
def extract_page_features(
    in_pages_path: str,
    out_features_path: str,
    layer: int = 2,
    batch_size: int = 2,
    device: str = 'cpu',
) -> None:
    '''
    Extract feature vectors that characterise all the page images in a directory.
    Feature vectors are extracted using a layer from `the Donut transformer (base-sized model,
    fine-tuned on RVL-CDIP) <https://huggingface.co/naver-clova-ix/donut-base-finetuned-rvlcdip>`_.

    :param in_pages_path: The path to the directory containing the pages the featurise.
    :param out_features_path: The path to the NumPy file containing the matrix of feature vectors.
    :param layer: The layer index of the transformer from which to extract features (0-3).
    :param batch_size: The number of page images to process at once.
    :param device: The PyTorch device name to run the transformer on (e.g. cpu or cuda).
    '''
    print('Extracting page features')
    os.makedirs(os.path.split(out_features_path)[0], exist_ok=True)

    processor = DonutProcessor.from_pretrained(
        'naver-clova-ix/donut-base-finetuned-rvlcdip',
        revision='7b37b46',
    )
    model = VisionEncoderDecoderModel.from_pretrained(
        'naver-clova-ix/donut-base-finetuned-rvlcdip',
        revision='7b37b46',
    )
    model.to(device)

    with torch.no_grad():
        task_prompt = '<s_rvlcdip>'
        decoder_input_ids = processor.tokenizer(
            task_prompt,
            add_special_tokens=False,
            return_tensors='pt',
        ).input_ids
        decoder_input_ids = decoder_input_ids.to(device)

        all_features = list[np.ndarray]()
        fnames = [fname for fname in sorted(os.listdir(in_pages_path)) if fname.endswith('.jpg')]
        for i in tqdm.tqdm(range(0, len(fnames), batch_size)):
            images = list[np.ndarray]()
            for fname in fnames[i:i+batch_size]:
                images.append(
                    np.array(Image.open(os.path.join(in_pages_path, fname)).convert('RGB'))
                )
            pixel_values = processor(images, return_tensors='pt').pixel_values
            pixel_values = pixel_values.to(device)
            batch_features = model(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                output_hidden_states=True,
            ).encoder_hidden_states[layer].mean(dim=1).cpu().numpy()
            all_features.extend(batch_features)

    np.save(out_features_path, all_features, allow_pickle=False)


##########################################################
def create_page_cluster_centroids(
    in_features_path: str,
    out_cluster_report_path: str,
    out_estimator_path: str,
    max_clusters: int = 20,
    seed: int = 0
) -> None:
    '''
    Use k-means to extract centroid vectors that would optimally cluster the page feature vectors
    extracted using `extract_page_features`.
    Multiple values of 'k' are attempted and the one that gives the best silhouette score is used.

    The reason why this function does not also perform the clustering is to be able to cluster
    more pages using the same centroids, allowing for the sampling process to work on more images.

    :param in_features_path: The path to the (input) NumPy file containing the page feature vectors.
    :param out_cluster_report_path: The path to the (output) text file containing a report about the
        clustering performance.
    :param out_estimator_path: The path to the (output) optimised sklearn k-means estimator Pickle
        file.
    :param max_clusters: The maximum number of clusters to attempt.
    :param seed: The random seed to use when clustering.
    '''
    print('Creating cluster centroids')
    os.makedirs(os.path.split(out_cluster_report_path)[0], exist_ok=True)
    os.makedirs(os.path.split(out_estimator_path)[0], exist_ok=True)

    features = np.load(in_features_path)

    with open(out_cluster_report_path, 'w', encoding='utf-8') as f:
        print('Tuning for different numbers of clusters:', file=f)
        best_k: Optional[int] = None
        best_score: Optional[float] = None
        best_kmeans: Optional[KMeans] = None
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=seed)
            cluster_assignments = kmeans.fit_predict(features)
            score = silhouette_score(features, cluster_assignments)
            print(f' - {k: >2d} clusters: silhouette score of {score:.3f}', file=f)
            if best_score is None or score > best_score:
                best_k = k
                best_score = score
                best_kmeans = kmeans
        assert best_k is not None
        assert best_score is not None
        assert best_kmeans is not None
        print('', file=f)
        print(f'Best number of clusters: {best_k}', file=f)
        cluster_assignments = best_kmeans.predict(features)
        print('Cluster sizes are:', [
            (cluster_assignments == cluster_index).sum().tolist()
            for cluster_index in range(best_k)
        ], file=f)
        score = silhouette_score(features, cluster_assignments)
        print(f'Silhoutte score: {score:.3f}', file=f)
        score = davies_bouldin_score(features, cluster_assignments)
        print(f'Davies Bouldin score: {score:.3f}', file=f)
        score = calinski_harabasz_score(features, cluster_assignments)
        print(f'Calinski Harabasz score: {score:.3f}', file=f)

    with open(out_estimator_path, 'wb') as f:
        pickle.dump(best_kmeans, f, protocol=3)


##########################################################
def cluster_pages_with_existing_centroids(
    in_features_path: str,
    in_pages_dir: str,
    in_estimator_path: str,
    out_clusters_dir: str,
) -> None:
    '''
    Cluster the page images using the centroids extracted by `create_page_cluster_controids`.
    The pages in each cluster are copied into a separate directory.

    :param in_features_path: The path to the NumPy page features file.
    :param in_pages_dir: The path to the page images directory.
    :param in_estimator_path: The path to the optimised sklearn k-means estimator.
    :param out_clusters_dir: The path to the directory that will contain the clustered pages (will
        be created if not exists).
    '''
    print('Clustering pages')
    os.makedirs(out_clusters_dir, exist_ok=True)

    features = np.load(in_features_path)
    fnames = sorted(fname for fname in os.listdir(in_pages_dir) if fname.endswith('.jpg'))

    with open(in_estimator_path, 'rb') as f:
        kmeans = pickle.load(f)

    cluster_assignments = kmeans.predict(features)
    item_indexes = np.arange(len(cluster_assignments), dtype=np.int32)
    clusters = [
        [fnames[item_index] for item_index in item_indexes[cluster_assignments == cluster_index]]
        for cluster_index in range(kmeans.n_clusters)
    ]
    for (i, cluster) in enumerate(clusters):
        for fname in cluster:
            os.makedirs(os.path.join(out_clusters_dir, str(i)), exist_ok=True)
            shutil.copy(os.path.join(in_pages_dir, fname), os.path.join(out_clusters_dir, str(i)))


##########################################################
def stratified_sample_clusters(
    in_clusters_dir: str,
    out_samples_dir: str,
    num_samples: int,
    seed: int = 0
) -> None:
    '''
    Create a stratified sample of pages by randomly sampling an equal amount of samples from each
    cluster created using `cluster_pages_with_existing_centroids`.

    Since the cluster sizes can be very imbalanced, simply dividing the desired number of samples
    by the number of clusters and sampling that amount from each cluster might not result in the
    desired number of samples (because some clusters would be smaller than that amount).
    To get around this, the function first searches for the sample-per-cluster amount that will
    result in the total sample size being closest to the desired sample size.

    The function is also designed in such a way that the created sample is extendable such that
    running it again with the same seed and a bigger sample size will result in the previous sample
    plus some extra items added to it (it does not create a completely new random sample).

    :param in_clusters_dir: The path to the directory containing the clustered page images obtained
        using `cluster_pages_with_existing_centroids`.
    :param out_samples_dir: The path to the directory that will contain the sample (unclustered)
        (will be created if not exists).
    :param num_samples: The desired number of samples to extract (the closest possible number of
        samples to this desired amount will be extracted).
    :param seed: The random seed to use to randomly sample pages.
    '''
    print('Creating stratified sample from clusters')
    os.makedirs(out_samples_dir, exist_ok=True)

    clusters = [
        sorted(
            fname
            for fname in os.listdir(os.path.join(in_clusters_dir, cluster_name))
            if fname.endswith('.jpg')
        )
        for cluster_name in os.listdir(in_clusters_dir)
        if os.path.isdir(os.path.join(in_clusters_dir, cluster_name))
    ]

    max_cluster_size = max(len(cluster) for cluster in clusters)
    best_sample_per_cluster_size = max_cluster_size
    last_actual_num_samples: Optional[int] = None
    for sample_per_cluster_size in range(1, max_cluster_size + 1):
        actual_num_samples = 0
        for cluster in clusters:
            actual_num_samples += min(sample_per_cluster_size, len(cluster))
        if actual_num_samples > num_samples and last_actual_num_samples is not None:
            if abs(actual_num_samples - num_samples) < abs(last_actual_num_samples - num_samples):
                best_sample_per_cluster_size = sample_per_cluster_size
            else:
                best_sample_per_cluster_size = sample_per_cluster_size - 1
            break
        last_actual_num_samples = actual_num_samples

    seed_rng = random.Random(seed)
    for (cluster_name, cluster) in enumerate(clusters):
        rng = random.Random(seed_rng.randrange(2**32))
        rng.shuffle(cluster)
        for fname in cluster[:min(best_sample_per_cluster_size, len(cluster))]:
            shutil.copy(
                os.path.join(in_clusters_dir, str(cluster_name), fname),
                os.path.join(out_samples_dir),
            )
