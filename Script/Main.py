import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import sys

class VisionLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vision Pro | Corrected Master Hierarchy")
        self.root.geometry("1650x980")
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # --- UI Palette ---
        self.bg_dark, self.panel_dark = "#0d1117", "#161b22"
        self.accent_teal, self.accent_purple = "#58a6ff", "#bc8cff" 
        self.error_red, self.border_col = "#f85149", "#30363d"
        self.root.configure(bg=self.bg_dark)
        
        # --- Variables ---
        self.px_x, self.px_y = tk.IntVar(value=5320), tk.IntVar(value=3032)
        self.px_size = tk.DoubleVar(value=2.74) 
        self.f_length = tk.DoubleVar(value=25.0); self.f_stop = tk.DoubleVar(value=4.0)
        self.wd = tk.DoubleVar(value=600.0); self.tilt_deg = tk.DoubleVar(value=35.0) 
        self.sensor_size_inch = tk.DoubleVar(value=1.1); self.lens_size_inch = tk.DoubleVar(value=1.1)
        self.unit_selection = tk.StringVar(value="mm"); self.prev_unit = "mm"
        self.active_config_id = None

        self.setup_styles(); self.setup_ui()
        
        # Bi-Directional Traces
        vars_to_sync = [self.px_x, self.px_y, self.px_size, self.f_length, self.f_stop,
                        self.wd, self.tilt_deg, self.sensor_size_inch, self.lens_size_inch]
        for v in vars_to_sync:
            v.trace_add("write", lambda *a: self.update_all())
            
        self.update_all()

    def on_exit(self):
        plt.close('all'); self.root.quit(); self.root.destroy(); sys.exit()

    def setup_styles(self):
        style = ttk.Style(); style.theme_use('clam')
        style.configure("TFrame", background=self.bg_dark)
        style.configure("TNotebook", background=self.bg_dark, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.panel_dark, foreground="#8b949e", padding=10)
        style.map("TNotebook.Tab", background=[("selected", self.bg_dark)], foreground=[("selected", self.accent_teal)])
        style.configure("Treeview", background="#0d1117", foreground="white", fieldbackground="#0d1117", rowheight=22, font=('Consolas', 8))
        style.configure("Treeview.Heading", background="#21262d", foreground=self.accent_teal, font=('Segoe UI', 9, 'bold'))
        style.configure("Action.TButton", font=('Segoe UI', 8, 'bold'), padding=5)

    def set_view(self, view_type):
        if view_type == "top": self.ax.view_init(elev=90, azim=-90)
        elif view_type == "side": self.ax.view_init(elev=0, azim=-90)
        elif view_type == "front": self.ax.view_init(elev=0, azim=0)
        elif view_type == "iso": self.ax.view_init(elev=30, azim=-45)
        self.canvas.draw()

    def setup_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.tab1, self.tab2 = ttk.Frame(self.tabs), ttk.Frame(self.tabs)
        self.tabs.add(self.tab1, text=" 3D LIVE SIMULATION "); self.tabs.add(self.tab2, text=" ANALYTICAL DATA TABLE ")
        self.tabs.pack(fill=tk.BOTH, expand=True)

        t1_layout = tk.Frame(self.tab1, bg=self.bg_dark, padx=10, pady=10); t1_layout.pack(fill=tk.BOTH, expand=True)
        sidebar = tk.Frame(t1_layout, bg=self.panel_dark, width=420, highlightbackground=self.border_col, highlightthickness=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5); sidebar.pack_propagate(False)

        tk.Label(sidebar, text="SYSTEM CONFIGURATION", bg=self.panel_dark, fg=self.accent_teal, font=('Segoe UI', 11, 'bold'), pady=5).pack()
        inner = tk.Frame(sidebar, bg=self.panel_dark, padx=20); inner.pack(fill=tk.X)

        def make_entry(lbl, var, row):
            tk.Label(inner, text=lbl, bg=self.panel_dark, fg="#c9d1d9", font=('Segoe UI', 8)).grid(row=row, column=0, sticky='w', pady=1)
            tk.Entry(inner, textvariable=var, bg="#0d1117", fg=self.accent_purple, width=12, justify='center').grid(row=row, column=1, sticky='e', pady=1)

        make_entry("Pixels X", self.px_x, 0); make_entry("Pixels Y", self.px_y, 1); make_entry("Pixel Size (µm)", self.px_size, 2)
        make_entry("Focal Length (mm)", self.f_length, 3); make_entry("F-Number", self.f_stop, 4)
        make_entry("Sensor (inch)", self.sensor_size_inch, 5); make_entry("Lens (inch)", self.lens_size_inch, 6)

        tk.Label(inner, text="Units", bg=self.panel_dark, fg=self.accent_teal, font=('Segoe UI', 8, 'bold')).grid(row=7, column=0, sticky='w', pady=5)
        u_box = ttk.Combobox(inner, textvariable=self.unit_selection, values=["mm", "inch", "feet"], width=10, state="readonly")
        u_box.grid(row=7, column=1, sticky='e', pady=5); u_box.bind("<<ComboboxSelected>>", self.handle_unit_conversion)

        tk.Label(sidebar, text="WORKING DISTANCE", bg=self.panel_dark, fg=self.accent_teal, font=('Segoe UI', 8, 'bold'), pady=2).pack()
        wd_f = tk.Frame(sidebar, bg=self.panel_dark); wd_f.pack(fill=tk.X, padx=20)
        self.wd_scale = ttk.Scale(wd_f, from_=10, to=2000, variable=self.wd, orient=tk.HORIZONTAL); self.wd_scale.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Entry(wd_f, textvariable=self.wd, bg="#0d1117", fg="white", width=8, justify='center').pack(side=tk.RIGHT, padx=5)

        tk.Label(sidebar, text="SENSOR TILT (°)", bg=self.panel_dark, fg=self.error_red, font=('Segoe UI', 8, 'bold'), pady=2).pack()
        tilt_f = tk.Frame(sidebar, bg=self.panel_dark); tilt_f.pack(fill=tk.X, padx=20)
        self.tilt_scale = ttk.Scale(tilt_f, from_=0, to=75, variable=self.tilt_deg, orient=tk.HORIZONTAL); self.tilt_scale.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Entry(tilt_f, textvariable=self.tilt_deg, bg="#0d1117", fg="white", width=8, justify='center').pack(side=tk.RIGHT, padx=5)

        v_frame = tk.Frame(sidebar, bg=self.panel_dark, pady=5); v_frame.pack(fill=tk.X)
        vb = tk.Frame(v_frame, bg=self.panel_dark); vb.pack()
        for v in [("TOP", "top"), ("SIDE", "side"), ("FRONT", "front"), ("ISO", "iso")]:
            ttk.Button(vb, text=v[0], width=6, command=lambda x=v[1]: self.set_view(x)).pack(side=tk.LEFT, padx=2)

        self.mini_tree = ttk.Treeview(sidebar, columns=("S1", "S2", "S3"), height=7)
        self.mini_tree.heading("#0", text="Metric"); self.mini_tree.column("#0", width=80)
        self.mini_tree.heading("S1", text="Theo"); self.mini_tree.column("S1", width=95, anchor='center')
        self.mini_tree.heading("S2", text="Eff"); self.mini_tree.column("S2", width=95, anchor='center')
        self.mini_tree.heading("S3", text="Tilt"); self.mini_tree.column("S3", width=95, anchor='center')
        self.mini_tree.pack(fill=tk.X, padx=10, pady=10)
        for m in ["FOV X", "FOV Y", "DOF", "Px/Unit"]: self.mini_tree.insert("", tk.END, text=m, iid=m)

        btns = tk.Frame(sidebar, bg=self.panel_dark, pady=5); btns.pack(fill=tk.X, padx=20)
        ttk.Button(btns, text="ADD CONFIG", style="Action.TButton", command=self.add_to_table).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btns, text="MODIFY", style="Action.TButton", command=self.modify_table).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        plot_frame = tk.Frame(t1_layout, bg=self.bg_dark); plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig = plt.figure(figsize=(14, 10), facecolor=self.bg_dark); self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame); self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        table_container = tk.Frame(self.tab2, bg=self.bg_dark, padx=20, pady=20); table_container.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(table_container, columns=("Parameter"), show='headings'); self.tree.pack(fill=tk.BOTH, expand=True); self.tree.bind("<ButtonRelease-1>", self.on_table_click)
        self.table_map = [
            ("px_x", "Pixels X"), ("px_y", "Pixels Y"), ("px_size", "Pixel Size (µm)"), ("f_length", "Focal Length (mm)"), ("f_stop", "F-Number"), ("unit_val", "Column Unit"), ("wd_val", "WD"), ("tilt_val", "Tilt (°)"),
            ("HEADER_S1", "--- STAGE 1: THEORETICAL ---"), ("fov_xn_orig", "FOV X"), ("fov_yn_orig", "FOV Y"), ("res_n_u", "Resolution"), ("dof_n", "DOF"),
            ("HEADER_S2", "--- STAGE 2: EFFECTIVE ---"), ("px_eff_x", "Effective Pix X"), ("px_eff_y", "Effective Pix Y"), ("fov_xn_eff", "FOV X"), ("fov_yn_eff", "FOV Y"), ("res_eff_u", "Resolution"), ("dof_eff", "DOF"),
            ("HEADER_S3", "--- STAGE 3: TILTED ---"), ("fov_xt", "Center FOV X"), ("fov_yt", "Projected FOV Y"), ("fov_top", "Keystone Top Width"), ("fov_bot", "Keystone Bot Width"), ("res_t_u", "Resolution"), ("dof_t", "DOF")
        ]
        for iid, lbl in self.table_map: self.tree.insert("", tk.END, values=(lbl,), iid=iid)
        ttk.Button(table_container, text="DELETE SELECTED COLUMN", style="Action.TButton", command=self.delete_config).pack(side=tk.RIGHT, pady=5)

    def handle_unit_conversion(self, event):
        factors = {"mm": 1.0, "inch": 25.4, "feet": 304.8}
        val_mm = self.wd.get() * factors[self.prev_unit]
        self.wd.set(round(val_mm / factors[self.unit_selection.get()], 4))
        self.prev_unit = self.unit_selection.get(); self.update_all()

    def get_calculations(self):
        factors = {"mm": 1.0, "inch": 25.4, "feet": 304.8}
        u = self.unit_selection.get(); wd_mm = float(self.wd.get() * factors[u])
        f, ps_um, N = float(self.f_length.get()), float(self.px_size.get()), float(self.f_stop.get())
        ps_mm, t_rad = ps_um/1000.0, np.radians(float(self.tilt_deg.get()))
        coc_mm = (2 * ps_um) / 1000.0
        mag_sys = f / (wd_mm - f) if wd_mm > f else 0.01

        # --- CORRECTED GAUSSIAN DOF MATH ---
        # 1. Hyperfocal Distance
        H = (f**2 / (N * coc_mm)) + f
        # 2. Near and Far focusing limits
        # Prevent division by zero if WD matches Focal Length or Hyperfocal
        if wd_mm > f:
            near_limit = (wd_mm * (H - f)) / (H + wd_mm - 2*f)
            if wd_mm < H:
                far_limit = (wd_mm * (H - f)) / (H - wd_mm)
                dof_final_mm = far_limit - near_limit
            else:
                dof_final_mm = float('inf') # Infinity focus
        else:
            dof_final_mm = 0.0

        eff_f = min(1.0, float(self.lens_size_inch.get() / self.sensor_size_inch.get()))
        f_orig_x, f_orig_y = (float(self.px_x.get()) * ps_um * wd_mm) / (f * 1000.0), (float(self.px_y.get()) * ps_um * wd_mm) / (f * 1000.0)
        f_eff_x, f_eff_y = f_orig_x * eff_f, f_orig_y * eff_f
        
        sx = wd_mm + (f * (1 + mag_sys))
        rot = np.array([[np.cos(t_rad), 0, np.sin(t_rad)], [0, 1, 0], [-np.sin(t_rad), 0, np.cos(t_rad)]])
        def get_pt(sy, sz):
            v = rot @ np.array([0, sy, sz]); v[0] += sx; t_p = -wd_mm / (v[0] - wd_mm); return t_p * v[1]
        sw_eff, sh_eff = (float(self.px_x.get())*ps_mm)*eff_f, (float(self.px_y.get())*ps_mm)*eff_f
        f_top = abs(get_pt(-sw_eff/2, sh_eff/2) * 2); f_bot = abs(get_pt(-sw_eff/2, -sh_eff/2) * 2)

        return {
            "px_x": float(self.px_x.get()), "px_y": float(self.px_y.get()), "px_size": ps_um, "f_length": f, "f_stop": N, "unit_val": u, "wd_val": self.wd.get(), "tilt_val": self.tilt_deg.get(),
            "fov_xn_orig": f_orig_x / factors[u], "fov_yn_orig": f_orig_y / factors[u], "res_n_u": float(self.px_y.get()) / (f_orig_y / factors[u]), "dof_n": dof_final_mm / factors[u],
            "px_eff_x": float(self.px_x.get()) * eff_f, "px_eff_y": float(self.px_y.get()) * eff_f,
            "fov_xn_eff": f_eff_x / factors[u], "fov_yn_eff": f_eff_y / factors[u], "res_eff_u": (float(self.px_y.get()) * eff_f) / (f_eff_y / factors[u]), "dof_eff": dof_final_mm / factors[u],
            "fov_xt": f_eff_x / factors[u], "fov_yt": (f_eff_y / np.cos(t_rad)) / factors[u], "fov_top": f_top / factors[u], "fov_bot": f_bot / factors[u], "res_t_u": (float(self.px_y.get()) * eff_f) / ((f_eff_y/np.cos(t_rad)) / factors[u]), "dof_t": (dof_final_mm / np.cos(t_rad)) / factors[u],
            "sw_mm": float(self.px_x.get())*ps_mm, "sh_mm": float(self.px_y.get())*ps_mm, "wd_mm": wd_mm, "t_rad": t_rad, "mag_sys": mag_sys, "eff_f": eff_f, "u": u
        }

    def update_all(self, event=None):
        try:
            d = self.get_calculations(); u = d['u']
            self.mini_tree.set("FOV X", "S1", f"{d['fov_xn_orig']:.1f}"); self.mini_tree.set("FOV X", "S2", f"{d['fov_xn_eff']:.1f}"); self.mini_tree.set("FOV X", "S3", f"{d['fov_xt']:.1f}")
            self.mini_tree.set("FOV Y", "S1", f"{d['fov_yn_orig']:.1f}"); self.mini_tree.set("FOV Y", "S2", f"{d['fov_yn_eff']:.1f}"); self.mini_tree.set("FOV Y", "S3", f"{d['fov_yt']:.1f}")
            self.mini_tree.set("DOF", "S1", f"{d['dof_n']:.2f}"); self.mini_tree.set("DOF", "S2", f"{d['dof_eff']:.2f}"); self.mini_tree.set("DOF", "S3", f"{d['dof_t']:.2f}")
            self.mini_tree.set("Px/Unit", "S1", f"{d['res_n_u']:.1f}"); self.mini_tree.set("Px/Unit", "S2", f"{d['res_eff_u']:.1f}"); self.mini_tree.set("Px/Unit", "S3", f"{d['res_t_u']:.1f}")
            self.ax.clear(); self.ax.set_facecolor("black"); self.fig.set_facecolor(self.bg_dark)
            wd_mm, sx = d['wd_mm'], d['wd_mm']+(d['f_length']*(1+d['mag_sys']))
            ox_mm, oy_mm = d['fov_xn_orig'] * (25.4 if u=="inch" else 304.8 if u=="feet" else 1.0), d['fov_yn_orig'] * (25.4 if u=="inch" else 304.8 if u=="feet" else 1.0)
            max_dim = max(ox_mm, oy_mm); self.ax.set_xlim(0, sx+60); self.ax.set_ylim(-max_dim/2 * 1.1, max_dim/2 * 1.1); self.ax.set_zlim(-max_dim/2 * 1.1, max_dim/2 * 1.1)
            verts = [[ [sx, -20, -20], [sx+15, -20, -20], [sx+15, 20, -20], [sx, 20, -20] ], [ [sx, -20, 20], [sx+15, -20, 20], [sx+15, 20, 20], [sx, 20, 20] ]]; self.ax.add_collection3d(Poly3DCollection(verts, facecolors='#222', edgecolors='white', alpha=1))
            tr = np.linspace(0, 2*np.pi, 25); self.ax.plot(np.full_like(tr, wd_mm), 15*np.cos(tr), 15*np.sin(tr), color='cyan', linewidth=2)
            rot = np.array([[np.cos(d['t_rad']), 0, np.sin(d['t_rad'])], [0, 1, 0], [-np.sin(d['t_rad']), 0, np.cos(d['t_rad'])]])
            ef = d['eff_f']; tp = []
            corners = [[-d['sw_mm']/2*ef, d['sh_mm']/2*ef], [d['sw_mm']/2*ef, d['sh_mm']/2*ef], [d['sw_mm']/2*ef, -d['sh_mm']/2*ef], [-d['sw_mm']/2*ef, -d['sh_mm']/2*ef]]
            for sy, sz in corners:
                v = rot @ np.array([0, sy, sz]); v[0] += sx; t_p = -wd_mm / (v[0] - wd_mm); tp.append([0, t_p*v[1], t_p*v[2]])
                self.ax.plot([0, wd_mm, v[0]], [t_p*v[1], 0, v[1]], [t_p*v[2], 0, v[2]], color='yellow', alpha=0.3)
            self.ax.plot([0,0,0,0,0], [-ox_mm/2, ox_mm/2, ox_mm/2, -ox_mm/2, -ox_mm/2], [oy_mm/2, oy_mm/2, -oy_mm/2, -oy_mm/2, oy_mm/2], color='cyan', linestyle='--', alpha=0.5, label="S1: Theo.")
            ex_mm, ey_mm = ox_mm * ef, oy_mm * ef; self.ax.plot([0,0,0,0,0], [-ex_mm/2, ex_mm/2, ex_mm/2, -ex_mm/2, -ex_mm/2], [ey_mm/2, ey_mm/2, -ey_mm/2, -ey_mm/2, ey_mm/2], color='#00ff41', linewidth=1, label="S2: Eff.")
            tp.append(tp[0]); tpa = np.array(tp); self.ax.plot(tpa[:,0], tpa[:,1], tpa[:,2], color='#ff3131', linewidth=3, label="S3: Tilted")
            self.ax.set_xlabel("Optical Axis (mm)", color='white'); self.ax.tick_params(colors='white'); self.ax.legend(facecolor='black', labelcolor='white', loc='upper right', fontsize=8); self.canvas.draw()
        except: pass

    def add_to_table(self):
        c_id = "C" + str(len(self.tree['columns'])); cols = list(self.tree["columns"]); cols.append(c_id); self.tree["columns"] = cols
        for i, c in enumerate(cols[1:], 1): self.tree.heading(c, text="Config " + str(i)); self.tree.column(c, width=110, anchor='center')
        self.update_col(c_id)

    def modify_table(self):
        if self.active_config_id: self.update_col(self.active_config_id)

    def on_table_click(self, event):
        col = self.tree.identify_column(event.x)
        if col and int(col[1:]) > 1: self.active_config_id = list(self.tree["columns"])[int(col[1:])-1]

    def update_col(self, col_id):
        d = self.get_calculations(); idx = list(self.tree["columns"]).index(col_id)
        for iid, lbl in self.table_map:
            v_list = list(self.tree.item(iid, "values"))
            while len(v_list) <= idx: v_list.append("")
            if iid in d: v_list[idx] = f"{d[iid]:.4f}" if isinstance(d[iid], float) else str(d[iid])
            self.tree.item(iid, values=tuple(v_list))

    def delete_config(self):
        if self.active_config_id:
            cols = list(self.tree["columns"]); cols.remove(self.active_config_id); self.tree["columns"] = cols; self.active_config_id = None
            for i, c in enumerate(cols[1:], 1): self.tree.heading(c, text="Config " + str(i))

if __name__ == "__main__":
    root = tk.Tk(); app = VisionLabApp(root); root.mainloop()
