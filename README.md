# ⚽ Football Tactical Pattern Matcher

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Data](https://img.shields.io/badge/Data-World%20Cup%202022-orange?style=for-the-badge)

## 📖 About the Project

**Football Tactical Pattern Matcher** is a specialized desktop application designed to analyze tactical passing patterns from **World Cup 2022** matches. It empowers analysts, coaches, and enthusiasts to go beyond simple statistics and visualize the "shape" of the game.

By processing thousands of match events, this tool helps uncover recurring strategies—from how teams build up play from the back to specific attacking wing movements.

---

## ⚙️ How It Works

The intelligence behind the scenes operates in three clear stages:

### 1. Ingest & Filter 📥
The system reads raw match data (JSON files), filters out noise (fouls, substitutions, stoppages), and extracts clean **"Possession Chains"**—sequences of uninterrupted passes.

### 2. Geometric Analysis 📐
It converts these passing sequences into mathematical vector shapes, effectively allowing the computer to "see" the play geometrically rather than just statistically.

### 3. Discovery 🔍
You can interact with the data in two powerful ways:
* **Search:** Draw a movement on the digital pitch (e.g., *a long ball to the right wing*), and the system will instantly find historical plays that match that exact shape.
* **Pattern Discovery:** The system uses a smart **"Compare & Collect"** algorithm to automatically organize thousands of plays into groups. It picks a play, finds similar ones, groups them, and repeats until all unique tactical patterns are revealed.

---

## 🎚️ Understanding the "Similarity Threshold"

In **Pattern Discovery** mode, you can tune the `Similarity Threshold`. This controls how the AI groups plays based on their **Geometric Difference** (roughly calculated in meters).

| Mode | Value | Description | Best For |
| :--- | :---: | :--- | :--- |
| **Strict** | **Low (~20)** | Groups plays that are almost **identical replays** of each other. | Finding set pieces, kick-off routines, or highly drilled plays. |
| **Flexible** | **High (~60)** | Groups plays that share a **general direction or idea**, even if exact passes vary. | Finding broad trends like "Left Wing Attacks" or "Counter-attacks". |

---

## 🚀 How to Run

To use this application on your local machine:

### 1. Install Dependencies
Make sure you have **Python** installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Start The App
Launch the main interface:
```bash
python gui.py
```

### 3. Data Setup
You will need the FIFA World Cup 2022 dataset.

* **Download here:** [Google Drive Link](https://drive.google.com/drive/folders/1_a_q1e9CXeEPJ3GdCv_3-rNO3gPqacfa)
