import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QLabel, QListWidgetItem, QMessageBox, QSplitter, QProgressBar,
                             QTabWidget, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os
import time

# Import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import ChainParser
from matcher import PatternMatcher
from clustering import PatternClusterer
from visualizer import Visualizer

class DataLoaderThread(QThread):
    finished = pyqtSignal(object, object) # Matcher, Clusterer
    progress = pyqtSignal(str)

    def run(self):
        try:
            self.progress.emit("Initializing parser...")
            # Paths
            data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cwd = os.getcwd()
            # Determine data path (Parent of the 'code' folder)
            _dir = os.path.dirname(os.path.abspath(__file__))
            possible_data = os.path.dirname(_dir)
            
            # Check if json files exist there, otherwise try CWD
            if any(f.endswith('.json') for f in os.listdir(possible_data)):
                data_path = possible_data
            else:
                data_path = cwd
            
            cache_path = os.path.join(data_path, "chains_cache.pkl")
            
            self.progress.emit(f"Data Path: {data_path}")
            self.progress.emit("Checking cache (parsing metadata)...")
            
            parser = ChainParser(data_path, cache_file=cache_path)
            chains = parser.process_all()
            
            self.progress.emit(f"Loaded {len(chains)} chains. Indexing...")
            matcher = PatternMatcher(chains)
            
            self.progress.emit("Clustering patterns...")
            clusterer = PatternClusterer(chains)
            # Run clustering (lightweight enough?)
            clusterer.extract_features(n_points=10)
            clusterer.cluster(threshold=40)
            
            self.finished.emit(matcher, clusterer)
            
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(None, None)

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#4B823B') # Match pitch color to hide padding
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        self.layout.addWidget(self.canvas)
        
        self.clicks = []
        self.result_chain = None
        
        self.draw()
        self.canvas.mpl_connect('button_press_event', self.on_click)

    def draw(self):
        self.ax.clear()
        Visualizer.draw_pitch(self.ax)
        
        # Draw query
        if self.clicks:
            Visualizer.plot_chain(self.ax, self.clicks, color='red', label='Query', linestyle='--', marker='x')

        # Draw result
        if self.result_chain:
            Visualizer.plot_chain(self.ax, self.result_chain, color='blue', label='Match', linestyle='-')
            self.ax.legend()
            
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == 1: # Left click adding
            self.clicks.append((event.xdata, event.ydata))
            self.draw()

    def clear(self):
        self.clicks = []
        self.result_chain = None
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Tactical Pattern Matcher V2")
        self.resize(1300, 850)
        
        self.matcher = None
        self.clusterer = None
        
        # Main Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Tab 1: Search
        self.tab_search = QWidget()
        self.setup_search_tab()
        self.tabs.addTab(self.tab_search, "Draw & Search")
        
        # Tab 2: Discovery
        self.tab_discovery = QWidget()
        self.setup_discovery_tab()
        self.tabs.addTab(self.tab_discovery, "Pattern Discovery")
        
        # Start loading
        self.start_loading()

    def setup_search_tab(self):
        layout = QHBoxLayout(self.tab_search)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.search_canvas = CanvasWidget()
        left_layout.addWidget(self.search_canvas)
        
        controls = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Query")
        self.btn_clear.clicked.connect(self.search_canvas.clear)
        self.btn_search = QPushButton("Search Patterns")
        self.btn_search.clicked.connect(self.run_search)
        self.btn_search.setEnabled(False)
        
        controls.addWidget(self.btn_clear)
        controls.addWidget(self.btn_search)
        left_layout.addLayout(controls)
        
        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.status_label = QLabel("Initializing...")
        self.progress_bar = QProgressBar()
        
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(QLabel("Top Matches:"))
        
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.show_search_match)
        right_layout.addWidget(self.results_list)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def setup_discovery_tab(self):
        layout = QVBoxLayout(self.tab_discovery)
        
        top_bar = QHBoxLayout()
        
        # Cluster Count Control
        top_bar.addWidget(QLabel("Similarity Threshold:"))
        self.spin_clusters = QSpinBox()
        self.spin_clusters.setRange(5, 200) # Threshold range. 
        self.spin_clusters.setValue(40) # Default Threshold
        self.spin_clusters.setSuffix(" units")
        top_bar.addWidget(self.spin_clusters)
        
        self.btn_recluster = QPushButton("Find Patterns")
        self.btn_recluster.clicked.connect(self.recluster_data)
        top_bar.addWidget(self.btn_recluster)
        
        top_bar.addSpacing(20)
        
        self.cluster_label = QLabel("Found: 0 groups")
        top_bar.addWidget(self.cluster_label)
        top_bar.addSpacing(20)
        
        self.cluster_combo = QComboBox()
        self.cluster_combo.currentIndexChanged.connect(self.load_cluster)
        top_bar.addWidget(QLabel("Select Group:"))
        top_bar.addWidget(self.cluster_combo)
        
        layout.addLayout(top_bar)
        
        content = QHBoxLayout()
        # Canvas
        self.discovery_canvas = CanvasWidget()
        content.addWidget(self.discovery_canvas, stretch=3)
        
        # List of examples in cluster
        right = QWidget()
        r_layout = QVBoxLayout(right)
        r_layout.addWidget(QLabel("Examples in Group:"))
        self.cluster_list = QListWidget()
        self.cluster_list.itemClicked.connect(self.show_discovery_match)
        r_layout.addWidget(self.cluster_list)
        content.addWidget(right, stretch=1)
        
        layout.addLayout(content)

    def start_loading(self):
        self.loader = DataLoaderThread()
        self.loader.progress.connect(self.update_status)
        self.loader.finished.connect(self.on_data_loaded)
        self.loader.start()

    def update_status(self, msg):
        self.status_label.setText(msg)

    def on_data_loaded(self, matcher, clusterer):
        self.progress_bar.hide()
        if matcher and clusterer:
            self.matcher = matcher
            self.clusterer = clusterer
            self.status_label.setText(f"Ready. Loaded {len(self.matcher.chains)} chains.")
            self.btn_search.setEnabled(True)
            
            # Initial clustering with spinbox value
            self.recluster_data()
        else:
            self.status_label.setText("Error loading data.")
            
    def recluster_data(self):
        if not self.clusterer: return
        thresh = self.spin_clusters.value()
        self.status_label.setText(f"Grouping with Threshold {thresh}...")
        QApplication.processEvents()
        
        self.clusterer.cluster(threshold=thresh)
        self.populate_clusters()
        count = len(self.clusterer.cluster_data)
        self.status_label.setText(f"Found {count} distinct groups.")
        self.cluster_label.setText(f"Found: {count} groups")

    def populate_clusters(self):
        self.cluster_combo.clear()
        clusters = self.clusterer.cluster_data # Access the clustered data directly
        
        # Sort by size (largest first)
        sorted_keys = sorted(clusters.keys(), key=lambda k: len(clusters[k]), reverse=True)
        
        for i, cid in enumerate(sorted_keys):
            count = len(clusters[cid])
            self.cluster_combo.addItem(f"Group #{i+1} (ID:{cid}) | Size: {count}", cid)
            
    def load_cluster(self, index):
        if not self.clusterer: return
        cid = self.cluster_combo.currentData()
        if cid is None: return
        
        # Get examples
        indices = self.clusterer.cluster_data[cid]
        
        # Show representative on canvas (Average)
        centroid = self.clusterer.get_cluster_representative(cid)
        if centroid:
            self.discovery_canvas.clicks = centroid # As 'query' (red)
            self.discovery_canvas.result_chain = None
            self.discovery_canvas.draw()
            
        # Populate list
        self.cluster_list.clear()
        # Show top 50 examples to avoid lag
        for i in indices[:50]:
            chain = self.matcher.chains[i]
            match_name = chain.get('match_name', 'Unknown')
            t_id = chain.get('team_id')
            time_str = chain.get('timestamp', '00:00')
            
            item_text = f"{match_name} | {time_str} | Team {t_id}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, chain)
            self.cluster_list.addItem(item)
            
    def run_search(self):
        if not self.matcher: return
        query = self.search_canvas.clicks
        if len(query) < 2:
            QMessageBox.warning(self, "Warning", "Please draw at least 2 points.")
            return
        
        self.status_label.setText("Searching...")
        QApplication.processEvents()
        
        matches = self.matcher.search(query, top_k=15)
        self.status_label.setText(f"Found {len(matches)} matches.")
        
        self.results_list.clear()
        for idx, m in enumerate(matches):
            chain = m['chain_data']
            match_name = chain.get('match_name', 'Unknown')
            t_id = chain.get('team_id')
            time_str = chain.get('timestamp', '00:00')
            dist = m['distance']
            
            # Readable output
            item_text = f"#{idx+1} | {match_name} | {time_str} | Dist: {dist:.1f}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, chain)
            self.results_list.addItem(item)

    def show_search_match(self, item):
        chain = item.data(Qt.ItemDataRole.UserRole)
        self.search_canvas.result_chain = chain.get('coords')
        self.search_canvas.draw()
        
    def show_discovery_match(self, item):
        chain = item.data(Qt.ItemDataRole.UserRole)
        self.discovery_canvas.result_chain = chain.get('coords')
        self.discovery_canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
