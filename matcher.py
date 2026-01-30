import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from typing import List, Dict, Tuple

class PatternMatcher:
    def __init__(self, chains: List[Dict]):
        """
        Initialize with the database of possession chains.
        chains: List of dicts, where each dict has at least 'coords' key: [(x,y), ...]
        """
        self.chains = chains

    def normalize_sequence(self, seq: List[Tuple[float, float]]) -> np.ndarray:
        """
        Optional: Normalize sequence by translating start to (0,0) or other normalization.
        For football tactical patterns, relative geometry matters.
        Simple translation to origin (0,0) helps comparing shapes regardless of pitch location?
        
        However, the user might want "Defense to Right Back" (location specific).
        If strict location matters, NO normalization.
        User prompt: "Defense to Right Back to Striker". This implies specific zones.
        So we should prob match on ABSOLUTE coordinates.
        But maybe we should handle direction of play?
        StatsBomb data usually normalizes play direction (Left to Right) or similar?
        In PFF/StatsBomb, usually home team plays L->R?
        
        Let's assume absolute coordinates for now.
        Inputs might need cast to float.
        """
        arr = np.array(seq)
        if arr.shape[0] == 0:
            return np.zeros((0, 2))
        return arr

    def search(self, query: List[Tuple[float, float]], top_k: int = 5) -> List[Dict]:
        """
        Search for the top_k most similar chains to the query.
        """
        if not query:
            return []

        query_arr = self.normalize_sequence(query)
        
        results = []
        
        for idx, chain in enumerate(self.chains):
            chain_coords = chain.get('coords')
            if not chain_coords or len(chain_coords) < 1:
                continue
                
            chain_arr = self.normalize_sequence(chain_coords)
            
            # fastdtw computes the distance and the path
            try:
                distance, path = fastdtw(query_arr, chain_arr, dist=euclidean)
                
                # We save the result
                results.append({
                    'chain_idx': idx,
                    'distance': distance,
                    'chain_data': chain
                })
            except Exception as e:
                # Handle potential shape mismatches or numerical errors
                continue
        
        # Sort by distance (lower is better)
        results.sort(key=lambda x: x['distance'])
        
        return results[:top_k]

if __name__ == "__main__":
    # verification test
    # Mock data
    mock_chains = [
        {'coords': [(0,0), (10,10), (20,20)]},
        {'coords': [(0,0), (10,0), (20,0)]}, # Flat
        {'coords': [(0,0), (5,5), (20,20)]}, # Similar to first
    ]
    
    matcher = PatternMatcher(mock_chains)
    query = [(0,0), (10,10), (20,20)]
    
    print("Testing Matcher...")
    top_matches = matcher.search(query, top_k=3)
    
    for i, m in enumerate(top_matches):
        print(f"{i+1}. Distance: {m['distance']}, Chain: {m['chain_data']['coords']}")
