import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Dict

class PatternClusterer:
    def __init__(self, chains: List[Dict]):
        self.chains = chains
        self.feature_matrix = None
        self.labels = None
        self.cluster_data = {}

    def extract_features(self, n_points=10):
        """
        Convert each chain into a fixed-size feature vector.
        We resample the chain to exactly n_points (x,y) coordinates.
        Vector size = n_points * 2.
        """
        features = []
        valid_indices = []
        
        for idx, chain in enumerate(self.chains):
            coords = chain.get('coords')
            if not coords or len(coords) < 2:
                continue
                
            # Convert to numpy
            arr = np.array(coords)
            
            # Simple resampling: Linear interpolation
            # We want to interpolate 'arr' to 'n_points'
            # Calculate cumulative distance to parametrize by length
            dists = np.sqrt(np.sum(np.diff(arr, axis=0)**2, axis=1))
            cum_dist = np.insert(np.cumsum(dists), 0, 0)
            total_len = cum_dist[-1]
            
            if total_len == 0:
                continue
                
            # Create target distances
            target_dists = np.linspace(0, total_len, n_points)
            
            # Interpolate X and Y
            new_xs = np.interp(target_dists, cum_dist, arr[:, 0])
            new_ys = np.interp(target_dists, cum_dist, arr[:, 1])
            
            # Flatten to vector
            vec = np.column_stack((new_xs, new_ys)).flatten()
            features.append(vec)
            valid_indices.append(idx)
            
        self.feature_matrix = np.array(features)
        self.valid_indices = valid_indices
        return self.feature_matrix

    def cluster(self, threshold=40.0):
        """
        Perform Greedy Threshold Clustering (Leader Algorithm).
        1. Pick unassigned item.
        2. Find all items within 'threshold' distance.
        3. Group them.
        4. Repeat.
        """
        if self.feature_matrix is None:
            self.extract_features()
            
        n_samples = len(self.feature_matrix)
        if n_samples == 0:
            return {}
            
        # Calculate pairwise distances (Euclidean)
        # O(N^2), but fast for N < 10000 in numpy
        dist_matrix = cdist(self.feature_matrix, self.feature_matrix, metric='euclidean')
        
        visited = set()
        clusters = {}
        cluster_id = 0
        
        # Sort indices? No, random order is arguably better or standard order.
        # Standard order ensures determinism.
        
        for i in range(n_samples):
            if i in visited:
                continue
                
            # Start new cluster with chain 'i' as the "Leader"
            current_cluster = [self.valid_indices[i]]
            visited.add(i)
            
            # Find neighbors
            # Row i of dist_matrix contains distances to all other points
            # We look for indices j where dist < threshold AND j not in visited
            dists = dist_matrix[i]
            neighbors = np.where(dists < threshold)[0]
            
            for j in neighbors:
                if j not in visited:
                    visited.add(j)
                    current_cluster.append(self.valid_indices[j])
            
            clusters[cluster_id] = current_cluster
            cluster_id += 1
            
        self.cluster_data = clusters
        return clusters

    def get_cluster_representative(self, cluster_id):
        """
        Returns the data of the centroid or a representative chain for visualization.
        For Greedy Clustering, the "Leader" (first element) is the representative.
        Or we can compute the mean.
        """
        if cluster_id not in self.cluster_data:
            return None
            
        indices_in_full_list = self.cluster_data[cluster_id]
        
        if not indices_in_full_list:
            return None
            
        # Return the Leader (first element) of the cluster
        # This is a REAL valid chain, not a computed average.
        leader_idx = indices_in_full_list[0]
        chain = self.chains[leader_idx]
        return chain.get('coords')
