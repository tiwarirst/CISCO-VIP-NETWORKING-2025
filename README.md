# CISCO-VIP-NETWORKING-2025
# 🛰️ Auto Topology Generation & Network Simulation Tool

# CISCO-VIP-NETWORKING-2025
# 🛰️ Network Topology Generator & Simulator

[![GitHub](https://img.shields.io/github/license/tiwarirst/CISCO-VIP-NETWORKING-2025)](https://github.com/tiwarirst/CISCO-VIP-NETWORKING-2025/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/tiwarirst/CISCO-VIP-NETWORKING-2025)](https://github.com/tiwarirst/CISCO-VIP-NETWORKING-2025/commits/main)

A comprehensive network automation tool that parses Cisco device configurations, generates interactive topology visualizations, validates network setups, and simulates various network scenarios including fault conditions.

## 🌟 Features

### 🔹 Network Configuration Parser
- Automatically parses Cisco device configurations (Routers, Switches, PCs)
- Extracts interface details, routing protocols, VLANs, and IP addressing
- Identifies device relationships and network hierarchy

### 🔹 Topology Visualization
- Generates interactive HTML network topology maps
- Visualizes device connections and relationships
- Provides detailed device information on hover/click

---

## 📖 Overview

This project automates the end-to-end process of network topology creation and simulation. It parses router, switch, and endpoint configurations, constructs a hierarchical topology, validates configuration compliance with industry best practices, and tests performance through detailed simulations.

## 🔧 Project Structure

```
📦 CISCO-VIP-NETWORKING-2025
┣ 📂 src/                      # Source code
┃ ┣ 📜 cisco_parser.py         # Configuration file parser
┃ ┣ 📜 day1_stimulation.py     # Day 1 simulation logic
┃ ┣ 📜 day2_testing.py         # Day 2 testing scenarios
┃ ┣ 📜 main_integration.py     # Main application entry point
┃ ┣ 📜 network_validator.py    # Network validation logic
┃ ┣ 📜 simulation_engine.py    # Core simulation engine
┃ ┣ 📜 topology_builder.py     # Network topology construction
┃ ┣ 📜 topology_renderer.py    # Topology visualization
┃ ┣ 📜 traffic_analyzer.py     # Traffic analysis module
┃ ┗ 📜 _init_.py              # Package initialization
┣ 📂 configs/                  # Network device configurations
┃ ┣ 📜 PC1.txt - PC6.txt      # PC configurations
┃ ┣ 📜 R1.txt - R3.txt        # Router configurations
┃ ┗ 📜 S1.txt - S3.txt        # Switch configurations
┣ 📂 comprehensive_reports/    # Generated reports and visualizations
┣ 📜 .gitignore               # Git ignore file
┗ 📜 README.md                # Project documentation
```

---

### 🔹 Network Validation
- Checks for configuration compliance
- Identifies duplicate IP addresses
- Validates VLAN configurations
- Verifies gateway assignments
- Detects MTU mismatches
- Identifies potential network loops

### 🔹 Simulation Engine
- Day 1 Operations:
  - Device initialization
  - Protocol convergence
  - Network stability testing
- Day 2 Operations:
  - Fault injection testing
  - Recovery analysis
  - Performance monitoring
  - Load balancing verification

## � Project Structure

```
📦 CISCO-VIP-NETWORKING-2025
┣ 📂 src/                      # Source code
┃ ┣ 📜 cisco_parser.py         # Configuration file parser
┃ ┣ 📜 day1_stimulation.py     # Day 1 simulation logic
┃ ┣ 📜 day2_testing.py         # Day 2 testing scenarios
┃ ┣ 📜 main_integration.py     # Main application entry point
┃ ┣ 📜 network_validator.py    # Network validation logic
┃ ┣ 📜 simulation_engine.py    # Core simulation engine
┃ ┣ 📜 topology_builder.py     # Network topology construction
┃ ┣ 📜 topology_renderer.py    # Topology visualization
┃ ┣ 📜 traffic_analyzer.py     # Traffic analysis module
┃ ┗ � _init_.py              # Package initialization
┣ 📂 configs/                  # Network device configurations
┃ ┣ 📜 PC1.txt - PC6.txt      # PC configurations
┃ ┣ 📜 R1.txt - R3.txt        # Router configurations
┃ ┗ 📜 S1.txt - S3.txt        # Switch configurations
┣ 📂 comprehensive_reports/    # Generated reports and visualizations
┣ 📜 .gitignore               # Git ignore file
┗ 📜 README.md                # Project documentation
```

---

## � Getting Started

### Prerequisites
- Python 3.9+
- Git
- Network configuration files (sample configs provided)

### Installation

1. Clone the repository
```bash
git clone https://github.com/tiwarirst/CISCO-VIP-NETWORKING-2025.git
cd CISCO-VIP-NETWORKING-2025
```

2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install required packages
```bash
pip install -r requirements.txt
```

---

### Usage

1. Place your network device configurations in the `configs/` directory
   - Router configs: R*.txt
   - Switch configs: S*.txt
   - PC configs: PC*.txt

2. Run the main application
```bash
python src/main_integration.py
```

3. View the results in `comprehensive_reports/` directory
   - Network topology visualization (HTML)
   - Configuration validation report
   - Simulation results and analysis

## 📊 Sample Output

The tool generates comprehensive HTML reports containing:
- Interactive network topology
- Device configuration analysis
- Validation results
- Simulation outcomes
- Performance metrics

---

### 2️⃣ Generate Network Topology
python main.py --generate-topology
<img width="749" height="152" alt="Screenshot 2025-08-15 191126" src="https://github.com/user-attachments/assets/beecd60b-dd91-49a3-9d1a-46d44b7657cf" />


text
**Outputs:**
- `reports/network_topology_<timestamp>.html` (Interactive Graph)
- JSON topology data
<img width="1882" height="1026" alt="Screenshot 2025-08-15 191304" src="https://github.com/user-attachments/assets/ffcead03-7036-4600-b7a0-d1fc4c633929" />


### 3️⃣ Validate Configurations
python main.py --validate-config
<img width="783" height="358" alt="Screenshot 2025-08-15 191607" src="https://github.com/user-attachments/assets/7416fb3d-ea9b-4977-b7a8-9cb8f0589fc7" />


### 4️⃣ Run Simulations

**Day-1 Simulation:**
python main.py --simulate --day 1

<img width="614" height="248" alt="Screenshot 2025-08-15 192035" src="https://github.com/user-attachments/assets/3be98565-cf60-4121-b99c-9d2e08b31be0" />


**Day-2 Simulation (Fault Tests):**
python main.py --simulate --day 2

<img width="921" height="412" alt="Screenshot 2025-08-15 192113" src="https://github.com/user-attachments/assets/0dbe2e9a-31d0-4e72-b232-49d8a3440219" />

---

### 5️⃣ Pause / Resume Simulation
python main.py --pause
python main.py --resume

<img width="725" height="650" alt="Screenshot 2025-08-15 192152" src="https://github.com/user-attachments/assets/194c8f98-01f8-450c-b14f-0dae3c578f67" />


---

## 📊 Example Output

<img width="1882" height="1026" alt="Screenshot 2025-08-15 191304" src="https://github.com/user-attachments/assets/5123fe89-16dc-4c0e-bcd9-dd197bd5af74" />


- **Network Bring-Up**
  - ✔ All devices up and stable
  - ✔ ARP tables populated
  - ✔ OSPF/BGP neighbors formed

- **Day-2 Tests**
  - Total tests: 31
  - Pass: 85
  - Fail: 10
  - Warnings: 5
  - Example Fault Injection:
    - Broken link R1 ↔ R2 → Network uptime maintained
    - Broken link R1 ↔ S1 → Automatic path adaptation

- **Reports Generated:**
  - JSON detailed analysis
  - Interactive HTML topology
  - Per-node simulation logs

---

## ✅ Cisco Internship Compliance

✔ Hierarchical topology creation  
✔ Bandwidth analysis/capacity verification  
✔ Load-balancing strategy recommendation  
✔ Missing component detection  
✔ Configuration checks & duplicate IP detection  
✔ VLAN & gateway validation  
✔ Routing protocol recommendations  
✔ MTU mismatch and network loop detection  
✔ Day-1 & Day-2 scenario execution  
✔ Fault injection testing & recovery analysis  
✔ Pause/Resume live simulation  
✔ Multithreaded architecture with IPC  

---

---

## 🚀 Usage

### 1️⃣ Prepare Configuration Files
Place device configs in the `Config/` directory.  
Sample configs are available here:  
[Google Drive - Input Configs](https://drive.google.com/drive/folders/1IpQ6TzIeMt7BoVMD8mypGwCoBCGKeIBG?usp=drive_link)

---

### 2️⃣ Generate Network Topology
**Outputs:**
- `reports/network_topology_<timestamp>.html` (Interactive Graph)
- JSON topology data

---

### 3️⃣ Validate Configurations

---

### 4️⃣ Run Simulations

**Day-1 Simulation:**

**Day-2 Simulation (Fault Tests):**

---

### 5️⃣ Pause / Resume Simulation

---

## 📊 Example Output

- **Network Bring-Up**
  - ✔ All devices up and stable
  - ✔ ARP tables populated
  - ✔ OSPF/BGP neighbors formed

- **Day-2 Tests**
  - Total tests: 31
  - Pass: 85
  - Fail: 10
  - Warnings: 5
  - Example Fault Injection:
    - Broken link R1 ↔ R2 → Network uptime maintained
    - Broken link R1 ↔ S1 → Automatic path adaptation

- **Reports Generated:**
  - JSON detailed analysis
  - Interactive HTML topology
  - Per-node simulation logs

---


## 🛠️ Development

### Testing
```bash
python -m pytest tests/
```

### Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## � Author

**Rishu Tiwari**
- GitHub: [@tiwarirst](https://github.com/tiwarirst)
 

---




