# VisionLab: Precise 3D Optical & Scheimpflug Analytical Suite 🔭

VisionLab is a high-fidelity machine vision simulation tool designed for optical engineers and researchers. It provides a structured, three-stage analytical approach to modeling camera systems, including precise Gaussian Depth of Field (DOF) calculations and 3D Scheimpflug principle (sensor tilt) visualization.

## 🚀 Core Functionalities

### 1. Hierarchical FOV Modeling
Analyze your optical system through three logical stages:
- **Stage 1 (Theoretical):** Maximum sensor capability based on pixel geometry.
- **Stage 2 (Effective):** Real-world FOV constrained by lens format (Crop Factor logic).
- **Stage 3 (Tilted/Projected):** Advanced Scheimpflug calculation showing the **Keystone Effect** (trapezoidal FOV).

### 2. Gaussian Optical Engine
Unlike standard approximations, this tool implements the exact **Gaussian Near/Far limit formulas**:
- Integrates Hyperfocal distance.
- Uses Nyquist-aware Circle of Confusion ($2 \times$ Pixel Size).
- Correctly models non-linear DOF decay at macro working distances.

### Screenshots
<img width="300" height="157" alt="image" src="https://github.com/user-attachments/assets/08326b37-8086-417f-8c2e-9d8874ee3da0" />
<img width="300" height="158" alt="image" src="https://github.com/user-attachments/assets/32d8e28c-464a-4b2e-a1d6-a06ff427de35" />



### 3. Interactive 3D Visualization
- **Dynamic 3D Plotting:** Real-time rendering of Camera Body, Lens Ring, and Optical Rays.
- **Visual Overlays:** Compare S1 (Cyan Dashed), S2 (Green Solid), and S3 (Red Bold) simultaneously.
- **View Snap-to-Buttons:** Instant Isometric, Top, Side, and Front perspective controls.

## 🛠️ Installation & Usage

1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/yourusername/VisionLab-Pro.git](https://github.com/yourusername/VisionLab-Pro.git)
   cd VisionLab-Pro
