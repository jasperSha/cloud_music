import pandas as pd
import numpy as np
import math
import sys


class User:
    def __init__(self, root_ids):
        self.song_set = set() # list of used id's
        root_list = []
        for id in root_ids:
            self.song_set.add(id)
            root_list.append(Node(id))
        self.batch = []
        self.root_list = root_list
        self.root_index = 0
          

    # Updates the user with a new batch of size 2 or max_size from the server
    # Returns the information necessary for knn request: node, k, k_lower
    def request_batch(self, max_size):
        curr_root = self.root_list[self.root_index]
        ratio, request_node = find_top_ratio(curr_root, None, 0, None)
        if ratio == sys.maxsize:  # the selected node has not been used yet
            # self.get_knn(request_node, 2)
            return request_node, 2, request_node.k_lower
        else:
            # self.get_knn(request_node, max_size)
            return request_node, max_size, request_node.k_lower
        return None

    def evaluate_batch(self, like_data):

        # builds cluster interest graph from liked songs and updates nodes appropriately
        ratio, root = find_top_ratio(self.root_list[self.root_index], None, 0, None)
        likes = 0
        for i in range(len(self.batch)):
            if like_data[i] == 1:
                likes += 1
                node = Node(self.batch[i])
                root.add_like()
                root.add_child(node)
                node.add_child(root)
            if like_data[i] == -1:
                root.add_dislike()
            if like_data[i] == 0:
                continue

        # if no songs were liked and the node has been explored before, proceeds to exit the cluster
        if likes == 0 and len(self.batch) > 2:
            top_ratio, top_node = find_top_ratio(self.root_list[self.root_index], None, 0, None)
            self.root_list[self.root_index] = top_node
            return_index = self.root_index
            self.root_index += 1
            return return_index, top_node.song_id

        return None

    def filter_duplicates(self, cur_candidates):
        batch = []
        for song_id in cur_candidates:
            if song_id not in self.song_set:
                batch.append(song_id)
            self.song_set.add(song_id)
        return batch

    def filter_batch(self, request_node, candidates):
        batch = self.filter_duplicates(candidates)
        request_node.k_lower += len(candidates) - len(batch)
        request_node.increment_k_bound(request_node.k_lower)
        self.batch = batch
        return batch


class Node:
    def __init__(self, song_id):
        self.song_id = song_id

        self.k_lower = 0
        self.neighbors = []

        self.likes = 0
        self.dislikes = 0
        self.ratio = sys.maxsize

    def get_id(self):
        return self.song_id

    def get_neighbors(self):
        return self.neighbors

    def add_child(self, child):
        self.neighbors.append(child)

    def add_like(self):
        self.likes += 1
        if self.dislikes != 0:
            self.ratio = self.likes / self.dislikes

    def add_dislike(self):
        self.dislikes += 1
        if self.dislikes != 0:
            self.ratio = self.likes / self.dislikes

    def increment_k_bound(self, k):
        self.k_lower += k

    def get_k_bound(self):
        return self.k_lower

    def get_ratio(self):
        return self.ratio


def find_top_ratio(root, curr_best_node, curr_best_ratio, used_nodes):
    # initial run
    if not used_nodes:
        used_nodes = set()
        used_nodes.add(root)
        curr_best_node = root
        curr_best_ratio = root.ratio

    # evaluates the current node
    if root.ratio > curr_best_ratio and not used_nodes.issuperset({root}):
        curr_best_node = root
        curr_best_ratio = root.ratio
        used_nodes.add(root)

    # evaluates current node's children
    if root.get_neighbors() is not None:
        for child in root.get_neighbors():
            if child.get_ratio() > curr_best_ratio and not used_nodes.issuperset({child}):
                curr_best_node = child
                curr_best_ratio = child.get_ratio()
                used_nodes.add(child)
            # if a child has children, recursively calls the function
            if len(child.get_neighbors()) > 0 and not used_nodes.issuperset({child}):
                ratio, new_best_node = find_top_ratio(child, curr_best_node, curr_best_ratio, used_nodes)
                if ratio > curr_best_ratio:
                    curr_best_node = new_best_node
                    curr_best_ratio = ratio
    return curr_best_ratio, curr_best_node
