Football Tactical Pattern Matcher ⚽📊
About the Project
This desktop application is a specialized tool designed to analyze tactical passing patterns from World Cup 2022 matches. It allows analysts, coaches, and enthusiasts to go beyond simple statistics and visualize the "shape" of the game.

By processing thousands of match events, the application helps you uncover recurring strategies, such as how teams build up play from the back or specific attacking wing movements.

How It Works
The intelligence behind the scenes works in three simple stages:

Ingest & Filter: The system reads raw match data (JSON files), filters out noise (like fouls or substitutions), and extracts clean "Possession Chains"—sequences of uninterrupted passes.
Geometric Analysis: It converts these passing sequences into mathematical shapes, allowing the computer to "see" the play.
Discovery: You can interact with the data in two ways:
Search: Draw a movement on the pitch (e.g., a long ball to the right wing), and the system will instantly find historical plays that match that exact shape.
Pattern Discovery: The system uses a smart "Compare & Collect" algorithm to automatically organize thousands of plays into groups. It picks a play, finds all others that look like it, groups them together, and repeats until all patterns are found.
Understanding the "Similarity Threshold"
In "Pattern Discovery" mode, you can tune the Similarity Threshold. This controls how the AI groups plays:

What is it? It represents the Geometric Difference between plays (roughly in meters).
Strict (Low Value, e.g., 20): The AI will only group plays that are almost identical replays of each other. Use this to find set pieces or very drilled routines.
Flexible (High Value, e.g., 60): The AI will group plays that share a general direction or idea, even if the exact passes vary. Use this to find broad trends like "Left Wing Attacks".
How to Run
To use this application on your local machine:

Install Dependencies: Make sure you have Python installed, then run:

pip install -r requirements.txt
Start the App: Launch the main interface:

python code/gui.py
Data: Ensure your JSON event data files are located in the Event Data folder. The application will automatically scan and process them.
