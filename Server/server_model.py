from math import dist
import random
import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import faiss
import glob
import pickle


# example definitions
def gen_root_nodes(original_df):
    set_clusters = int(np.sqrt(original_df.shape[0]))
    raw_data = original_df.drop(original_df.columns[[0, 30, 31, 32]], axis=1)
    cluster_members = [0] * set_clusters
    cluster_loc = []
    cluster_data = original_df.iloc[:, 32]
    best_roots = []
    for i in range(set_clusters):
        cluster_loc.append([0] * (len(raw_data.columns)))
        best_roots.append([0] * (len(raw_data.columns)))

    # sums the location of all songs in each cluster
    for i in range(raw_data.shape[0]):
        cluster_members[cluster_data[i]] += 1
        for j in range(raw_data.shape[1]):
            cluster_loc[cluster_data[i]][j] += raw_data.loc[i][j]

    # location totals / cluster mem count for avg location
    for i in range(set_clusters):
        for j in range(raw_data.shape[1]):
            cluster_loc[i][j] = cluster_loc[i][j] / cluster_members[i]

    return cluster_loc


def load_data(filename):
    metadata = pd.read_csv(filename)
    metadata.drop(columns=['duration'], inplace=True)  # already have duration in frequency measures

    freqs = list(glob.glob('./song_freqs/*.csv'))
    df = pd.concat((pd.read_csv(f) for f in freqs))
    df = df.merge(metadata, how='left', on='id')

    full_df = df.copy()
    full_df.drop(columns=['sr', 'channel'], inplace=True, axis=1)

    # normalize everything besides metadata
    norm_columns = full_df.drop(columns=['id', 'artist', 'title']).columns
    full_df[norm_columns] = (full_df[norm_columns] - full_df[norm_columns].min()) / (
            full_df[norm_columns].max() - full_df[norm_columns].min())

    knn_df = full_df.copy()
    set_clusters = int(np.sqrt(full_df.shape[0]))

    cluster_cols = knn_df.drop(columns=['id', 'artist', 'title']).columns
    kmeans = KMeans(n_clusters=set_clusters, random_state=0).fit(knn_df[cluster_cols])
    knn_df['cluster'] = kmeans.labels_
    return knn_df, cluster_cols


# helper function just for grabbing neighbors df
# @param song_id: string of song id you wish to query neighbors for
# @return contiguous array: corresponding features to perform l2 distance with faiss
def retrieve_features(df, song_id, features):
    value = df[features].loc[df['id'] == song_id]
    return np.asarray(value.to_numpy().astype(np.float32), order='C')


def get_neighbors(knn_df, feature_cols, song_query, k, lower_k):
    # initialize faiss with IndexFlatL2 dimensionality (index for euclidean distances)
    l2_dims = knn_df[feature_cols].shape[1]

    # init index
    index = faiss.IndexFlatL2(l2_dims)

    # convert to float32 --> np array --> contiguous array in memory for indexing (faiss requires this)
    contiguous_embeddings = np.asarray(knn_df[feature_cols].to_numpy().astype(np.float32), order='C')
    index.add(contiguous_embeddings)

    query = retrieve_features(knn_df, song_query, feature_cols)

    D, I = index.search(query, k)

    neighbors = I.flatten()
    neighbors_index = list(neighbors)

    if lower_k:
        final_neighbors = knn_df.iloc[neighbors_index[:k - lower_k]]
    else:
        final_neighbors = knn_df.iloc[neighbors_index]

    return final_neighbors['id']


def find_nearest_songs(original_df, root_locations):
    raw_data = original_df.drop(original_df.columns[[0, 30, 31, 32]], axis=1)
    cluster_data = original_df.iloc[:, 32]
    roots = [None] * len(root_locations)
    best_roots = []
    for i in range(len(root_locations)):
        best_roots.append([0] * (len(raw_data.columns)))

    # finds closest node to center for default root selection using euclidean distance
    for i in range(raw_data.shape[0]):
        cluster_center = root_locations[cluster_data[i]]
        try:
            dist(raw_data.loc[i], cluster_center)
        except ValueError:
            print("raw_data length", i, len(raw_data.loc[i]))
            print("cluster_center", len(cluster_center))
        try:
            dist(best_roots[cluster_data[i]], cluster_center)
        except ValueError:
            print("best roots cluster data length", i, len(best_roots[cluster_data[i]]))
            print("cluster_center", len(cluster_center))
        if dist(raw_data.loc[i], cluster_center) < dist(best_roots[cluster_data[i]], cluster_center):
            best_roots[cluster_data[i]] = raw_data.loc[i]
            roots[cluster_data[i]] = original_df.loc[i][0]

    # returns the id values of the root nodes
    return roots

def save_model(model):
    filehandler = open(b"server_model.obj", "wb")
    pickle.dump(model, filehandler)
    filehandler.close()

def load_model(path):
    file = open(path,'rb')
    model = pickle.load(file)
    file.close()
    return model

def check_model_exists(path):
    return os.path.exists(path)

class Server:
    # rootlist is not a set of nodes or ids. They are points in euclidean space
    def __init__(self, knn_df, learning_rate):
        self.data = knn_df
        self.root_list = gen_root_nodes(knn_df)
        self.learning_rate = learning_rate

    def get_best_roots(self):
        return find_nearest_songs(self.data, self.root_list)

    def update_root(self, song_id, root_index):
        raw_data = self.data.drop(self.data.columns[[0, 30, 31, 32]], axis=1)
        song_location = raw_data.loc[raw_data['id'] == song_id]
        root_location = self.root_list[root_index]
        for i in range(len(root_location)):
            root_location[i] = (song_location[i] - root_location[i]) * self.learning_rate + root_location[i]
        self.root_list[root_index] = root_location
