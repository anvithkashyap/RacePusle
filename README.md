# RacePusle
RacePulse is an advanced Python-based desktop application that parses, processes, and visualizes Formula 1 telemetry data using the FastF1 API. It provides an interactive environment for motorsport enthusiasts and data analysts to study driver performance in detail.
![Screenshot 2025-07-03 at 10 59 53 AM](https://github.com/user-attachments/assets/c541000d-6e02-4b7f-ad7b-9f684b8f42ef)

---

## 🚀 Features
- ✅ **Single Driver Mode** – Visualize lap telemetry (Speed, Throttle, Brake, Gear)  
- ✅ **Comparison Mode** – Compare up to 5 drivers side-by-side with synchronized telemetry graphs  
- ✅ **Track Map Mode** – View and compare driver racing lines on a 2D interactive circuit map with lap selection  
- ✅ **Session Highlights** – Automatically fetch podium data, pole positions, and circuit info  

---

## 🛠️ Tech Stack
| Component    | Technology |
|--------------|------------|
| Language     | Python 3.x |
| GUI          | PyQt5 |
| Data Source  | [FastF1](https://github.com/theOehrly/Fast-F1) |
| Visualization| Matplotlib |
| Data Handling| Pandas |
| Other        | NumPy, datetime |

---

## 🧑‍💻 Installation & Usage  

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/yourusername/RacePulse.git
cd RacePulse
```

### 2️⃣ Install Dependencies
Ensure you have Python 3.x installed, then run:
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application
```bash
python main.py
```

---

## 🎮 How to Use
1. **Select Mode** – Choose between:
   - **Single Driver Mode** – Analyze telemetry for one driver lap-by-lap.  
   - **Comparison Mode** – Compare up to 5 drivers on multiple telemetry graphs.  
   - **Track Map Mode** – View and compare driver racing lines on an interactive track map with lap selection.
2. **Pick Year & GP** – Select the Formula 1 season and race you wish to analyze.
3. **Load Session** – Click **Load Telemetry** to fetch session data from FastF1.
4. **Choose Driver & Lap** –  
   - In **Single Driver Mode**, pick a driver and lap to view telemetry.  
   - In **Comparison Mode**, configure drivers via the settings dialog.  
   - In **Track Map Mode**, select drivers and laps to overlay their racing lines on the track map.
5. **Interact with Graphs** – Use built-in zoom, drag, and hover features to explore data in detail.

---

## 🚀 Future Enhancements
- 🔥 **Sector Delta Visualization** – Real-time delta comparison for each sector.  
- 🔥 **Export Features** – Save graphs and telemetry data as PNG/CSV.  
- 🔥 **Custom Track Overlays** – More accurate circuit layouts with corners and DRS zones.  
- 🔥 **Cloud Sync** – Store and retrieve telemetry datasets from cloud services.

---

## 🤝 Contributing
I welcome contributions from the community! Here's how you can help:  
1. **Fork** the repository.  
2. **Create a new branch** for your feature/fix.  
3. **Commit** your changes and **push** the branch.  
4. Open a **Pull Request** with a detailed explanation.  

For major changes, please open an **issue** first to discuss what you’d like to improve.  
