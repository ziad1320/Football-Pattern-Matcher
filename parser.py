import json
import os
import pickle
from typing import List, Tuple, Dict, Optional

class ChainParser:
    def __init__(self, data_dir: str, cache_file: str = "chains_cache.pkl"):
        self.data_dir = data_dir
        self.cache_file = cache_file

    def get_player_coordinates(self, event: Dict, player_id: int) -> Optional[Tuple[float, float]]:
        """
        Finds the (x, y) coordinates of a player in a given event.
        Checks both 'homePlayers' and 'awayPlayers'.
        """
        for team_key in ['homePlayers', 'awayPlayers']:
            if team_key in event:
                for player in event[team_key]:
                    if player['playerId'] == player_id:
                        return (player.get('x'), player.get('y'))
        return None

    def parse_file(self, filepath: str) -> List[Dict]:
        """
        Parses a single JSON file and returns a list of possession chains.
        """
        print(f"Parsing {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []

        chains = []
        current_chain = []
        current_team_id = None
        
        # Metadata extraction logic
        # Usually first event captures team names.
        match_name = "Unknown Match"
        if len(data) > 0:
            first = data[0]
            # Try to find team names. 
            # Often gameEvents -> teamName is present.
            # Or we look for a 'lineup' event or 'kickoff'.
            # Based on user view: "teamName": "Netherlands", "homeTeam": true
            # We can scan first few events to find 2 distinct team names.
            
            teams = {} # id -> name
            for evt in data[:100]: # Check first 100 events
                ge = evt.get('gameEvents', {})
                tid = ge.get('teamId')
                tname = ge.get('teamName')
                if tid and tname:
                    teams[tid] = tname
                    if len(teams) >= 2:
                        break
            
            if len(teams) >= 2:
                names = list(teams.values())
                match_name = f"{names[0]} vs {names[1]}"
            elif len(teams) == 1:
                match_name = f"{list(teams.values())[0]} vs Unknown"

        for event in data:
            possession_info = event.get('possessionEvents', {})
            event_type = possession_info.get('possessionEventType')
            
            game_info = event.get('gameEvents', {})
            team_id = game_info.get('teamId')
            
            # Timestamp
            timestamp = possession_info.get('formattedGameClock', '00:00')

            if event_type == 'PA' and team_id is not None:
                passer_id = possession_info.get('passerPlayerId')
                
                if team_id != current_team_id:
                    if len(current_chain) >= 3:
                        chains.append({
                            'team_id': current_team_id,
                            'coords': current_chain,
                            'match_name': match_name,
                            'timestamp': timestamp 
                        })
                    current_chain = []
                    current_team_id = team_id

                if passer_id:
                    coords = self.get_player_coordinates(event, passer_id)
                    if coords and coords[0] is not None and coords[1] is not None:
                        current_chain.append(coords)
            
            elif team_id is not None and team_id != current_team_id:
                 if len(current_chain) >= 3:
                    chains.append({
                        'team_id': current_team_id,
                        'coords': current_chain,
                        'match_name': match_name,
                        'timestamp': timestamp
                    })
                 current_chain = []
                 current_team_id = None

        if len(current_chain) >= 3:
            chains.append({
                'team_id': current_team_id,
                'coords': current_chain,
                'match_name': match_name,
                'timestamp': 'End of Match'
            })
            
        return chains

    def process_all(self):
        """
        Process all JSON files in the data directory and cache the results.
        """
        all_chains = []
        
        # Load from cache if exists
        if os.path.exists(self.cache_file):
            print(f"Loading from cache: {self.cache_file}")
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)

        # Parse valid files
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                full_path = os.path.join(self.data_dir, filename)
                all_chains.extend(self.parse_file(full_path))
        
        print(f"Processed {len(all_chains)} chains.")
        
        # Save to cache
        with open(self.cache_file, 'wb') as f:
            pickle.dump(all_chains, f)
            
        # Export to readable JSON as requested
        json_path = self.cache_file.replace('.pkl', '_exported.json')
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_chains, f, indent=2)
            print(f"Exported readable chains to: {json_path}")
        except Exception as e:
            print(f"Failed to export JSON: {e}")
        
        return all_chains