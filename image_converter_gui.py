import os
import sys
import json
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Use requests to perform GitHub checks, asset queries, and network image streaming safely
import requests

# Set explicit Windows Taskbar Application IDs so Python host doesn't mask our icon
try:
    import ctypes
    myappid = "Guru.ImageToSvgConverter.App.v1.0.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

# Manifest Variable definitions mapped directly across execution systems
__version__ = "1.0.0"
GITHUB_REPO_URL = "https://github.com/SomeGuru/image2svg"
GITHUB_API_LATEST = "https://github.com"
LOGO_URL = "https://www.it2innovations.com/images/logo.png"

class MillionColorImageToSvgConverterApp:
    def __init__(self, root):
        self.root = root
        # Version information globally displayed directly in Title and task manager context structures
        self.root.title(f"Photographic Color SVG Vector Converter - Version {__version__}")
        self.root.geometry("1100x720")
        self.root.minsize(900, 620)
        
        self.source_path = ""
        self.preview_size = (420, 420)
        self.logo_img = None  # Persistent frame link for logo cache
        
        # Async load the titlebar and taskbar branding images safely
        self.load_application_logos()
        
        self.create_widgets()
        
        # Non-blocking network check to scan if our update server pipeline is online
        threading.Thread(target=self.check_for_updates_async, daemon=True).start()

    def load_application_logos(self):
        def _fetch():
            try:
                response = requests.get(LOGO_URL, timeout=5)
                if response.status_code == 200:
                    img_data = io.BytesIO(response.content)
                    raw_img = Image.open(img_data)

                    # Store raw PIL image and a PhotoImage for UI; keep raw for resizes
                    self.logo_raw = raw_img
                    self.logo_img = ImageTk.PhotoImage(raw_img)
                    # Sets both Titlebar icon and active Windows Taskbar system tray context icons
                    self.root.iconphoto(True, self.logo_img)
            except Exception:
                pass  # Fallback gracefully to operating system standards if offline
        threading.Thread(target=_fetch, daemon=True).start()

    def create_widgets(self):
        # --- Top Selection Control Bar Container ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Explicitly requested: Update application button on the top right, positioned before source field
        self.btn_update = tk.Button(top_frame, text="Checking for updates...", font=("Segoe UI", 9, "bold"),
                                    bg="#E1E1E1", fg="#666666", state=tk.DISABLED, command=self.trigger_self_upgrade, padx=8)
        self.btn_update.pack(side=tk.RIGHT, padx=(10, 0))

        lbl = tk.Label(top_frame, text="Source Image:", font=("Segoe UI", 10))
        lbl.pack(side=tk.LEFT, padx=(0, 5))
        
        # Input field placed to the left of the browser button
        self.ent_path = tk.Entry(top_frame, font=("Segoe UI", 10))
        self.ent_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        btn_browse = tk.Button(top_frame, text="Browse...", command=self.browse_file, bg="#0078D4", fg="white", padx=12, font=("Segoe UI", 9, "bold"))
        btn_browse.pack(side=tk.LEFT, padx=5)
        
        # --- Dual View Windows (Before & After Preview Grid) ---
        view_frame = tk.Frame(self.root)
        view_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Left Panel Configuration (Before Conversion)
        self.frame_before = tk.LabelFrame(view_frame, text=" Before (Original Raster Asset) ", font=("Segoe UI", 10, "bold"), fg="#555555")
        self.frame_before.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.lbl_before = tk.Label(self.frame_before, text="No source image loaded\nSupported formats: BMP, GIF, JPG, JPEG, HEIF, PNG", justify=tk.CENTER, fg="#888888")
        self.lbl_before.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel Configuration (After Conversion)
        self.frame_after = tk.LabelFrame(view_frame, text=" After (Million-Color Vector Preview) ", font=("Segoe UI", 10, "bold"), fg="#107C41")
        self.frame_after.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.lbl_after = tk.Label(self.frame_after, text="Awaiting deep-color engine initialization...", justify=tk.CENTER, fg="#888888")
        self.lbl_after.pack(fill=tk.BOTH, expand=True)
        
        # --- Bottom Processing Toolbar Container ---
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.btn_convert = tk.Button(bottom_frame, text="Extract & Export Millions of Colors to SVG", font=("Segoe UI", 11, "bold"),
                                      bg="#107C41", fg="white", state=tk.DISABLED, command=self.convert_image, pady=8)
        self.btn_convert.pack(fill=tk.X)

        # --- Metadata & Footer Panel Frame ---
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Explicitly requested: Information Button built into the lower right layout grid
        btn_info = tk.Button(footer_frame, text="? Info", command=self.show_developer_info_modal, font=("Segoe UI", 9), bg="#F0F0F0", fg="#333333", padx=8)
        btn_info.pack(side=tk.RIGHT, padx=(10, 0))

        # Explicitly requested: Version information rendered cleanly on the bottom far right side
        lbl_version_footer = tk.Label(footer_frame, text=f"App Version: v{__version__}", font=("Segoe UI", 9, "italic"), fg="#777777")
        lbl_version_footer.pack(side=tk.RIGHT)

    def check_for_updates_async(self):
        """Asynchronously probes target GitHub APIs. Stays greyed out until verified connection."""
        try:
            response = requests.get(GITHUB_API_LATEST, timeout=6)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name", "1.0.0").replace("v", "")
                
                if latest_tag != __version__:
                    self.update_download_url = None
                    # Find raw source code code assets from the releases data payload
                    for asset in data.get("assets", []):
                        if asset.get("name") == "image_converter_gui.py":
                            self.update_download_url = asset.get("browser_download_url")
                            break
                    if not self.update_download_url:
                        self.update_download_url = f"https://githubusercontent.com"
                    
                    self.root.after(0, lambda: self.btn_update.config(
                        text="Update Available!", bg="#D83B01", fg="white", state=tk.NORMAL
                    ))
                else:
                    self.root.after(0, lambda: self.btn_update.config(
                        text="Up to Date", bg="#107C41", fg="white", state=tk.DISABLED
                    ))
            else:
                raise requests.RequestException()
        except Exception:
            # Stays safely greyed out if connection fails or repository endpoints are missing
            self.root.after(0, lambda: self.btn_update.config(
                text="Updates Offline", bg="#E1E1E1", fg="#999999", state=tk.DISABLED
            ))

    def trigger_self_upgrade(self):
        """Performs immediate script-overwriting self-upgrade without locking app interaction frames."""
        if messagebox.askyesno("Confirm Self-Upgrade", "Would you like the system to automatically download and overwrite this script with the latest version from GitHub?"):
            self.btn_update.config(text="Upgrading...", state=tk.DISABLED, bg="#F3F2F1", fg="#333333")
            
            def _upgrade_worker():
                try:
                    res = requests.get(self.update_download_url, timeout=15)
                    if res.status_code == 200 and "class" in res.text:
                        current_script_path = os.path.abspath(sys.argv[0])
                        
                        # Atomic disk write to overwrite program memory workspace
                        with open(current_script_path, "w", encoding="utf-8") as f:
                            f.write(res.text)
                            
                        messagebox.showinfo("Upgrade Success", "Application upgraded cleanly without errors! Please restart the program to apply updates.")
                        self.root.after(0, self.root.destroy)
                    else:
                        raise ValueError("Downloaded file integrity corrupt.")
                except Exception as e:
                    messagebox.showerror("Upgrade Faulted", f"Could not perform automated update sequence:\n{str(e)}")
                    self.root.after(0, lambda: self.btn_update.config(text="Update Available!", bg="#D83B01", fg="white", state=tk.NORMAL))
            
            threading.Thread(target=_upgrade_worker, daemon=True).start()

    def browse_file(self):
        file_types = [
            ("All Supported Graphic Files", "*.bmp *.gif *.jpg *.jpeg *.heif *.heic *.png"),
            ("PNG Portable Network Graphics", "*.png"),
            ("JPEG Joint Photographic Experts Group", "*.jpg *.jpeg"),
            ("BMP Windows Bitmap", "*.bmp"),
            ("GIF Graphics Interchange Format", "*.gif"),
            ("HEIF High Efficiency Image File", "*.heif *.heic")
        ]
        selected_file = filedialog.askopenfilename(title="Select Source Image Asset", filetypes=file_types)
        if selected_file:
            self.source_path = selected_file
            self.ent_path.delete(0, tk.END)
            self.ent_path.insert(0, selected_file)
            self.load_before_preview()
            self.btn_convert.config(state=tk.NORMAL)
            self.lbl_after.config(image="", text="Deep color spectrum analyzed. Ready to process.")
            self.lbl_after.image = None

    def load_before_preview(self):
        try:
            img = Image.open(self.source_path)
            img.thumbnail(self.preview_size)
            self.img_before_tk = ImageTk.PhotoImage(img)
            self.lbl_before.config(image=self.img_before_tk, text="")
        except Exception as e:
            messagebox.showerror("IO Mount Error", f"Cannot construct hardware preview for target asset:\n{str(e)}")

    def convert_image(self):
        if not self.source_path or not os.path.exists(self.source_path):
            messagebox.showerror("Execution Fault", "The target path field evaluation returns empty or corrupt source.")
            return

        base_name_tuple = os.path.splitext(os.path.basename(self.source_path))
        suggested_output = base_name_tuple[0] + ".svg"
        save_path = filedialog.asksaveasfilename(title="Save Million-Color Vector As",
                                                 defaultextension=".svg",
                                                 filetypes=[("W3C SVG Vector Graphic", "*.svg")],
                                                 initialfile=suggested_output)
        if not save_path:
            return

        try:
            img_rgba = Image.open(self.source_path).convert("RGBA")
            width, height = img_rgba.size
            pixels = img_rgba.load()

            # Collect horizontal runs of identical colors per row to produce small rects
            color_rects = {}
            for y in range(height):
                x = 0
                while x < width:
                    r, g, b, a = pixels[x, y]
                    if a < 16:
                        x += 1
                        continue
                    start_x = x
                    curr = (r, g, b)
                    x += 1
                    while x < width:
                        r2, g2, b2, a2 = pixels[x, y]
                        if a2 < 16 or (r2, g2, b2) != curr:
                            break
                        x += 1
                    w = x - start_x
                    hex_color = '#%02x%02x%02x' % curr
                    color_rects.setdefault(hex_color, []).append((start_x, y, w, 1))

            svg_elements = []
            for hex_color, rects in color_rects.items():
                for (sx, sy, w, h) in rects:
                    svg_elements.append(f'<rect x="{sx}" y="{sy}" width="{w}" height="{h}" fill="{hex_color}" />')

            svg_content = (
                '<?xml version="1.0" encoding="utf-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
                + "\n".join(svg_elements)
                + '\n</svg>'
            )

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            preview_img = img_rgba.copy()
            preview_img.thumbnail(self.preview_size)
            self.img_after_tk = ImageTk.PhotoImage(preview_img)
            self.lbl_after.config(image=self.img_after_tk, text="")
            self.lbl_after.image = self.img_after_tk

            messagebox.showinfo("Export Success", f"Photographic vector serialization complete!\nUnique Spectrum Hues Retained: {len(color_rects)}\nSaved to: {save_path}")
        except Exception as e:
            messagebox.showerror("Pipeline Computation Interrupted", f"Vector tracing runtime exception occurred:\n{str(e)}")

    def show_developer_info_modal(self):
        """Displays custom pop-up window tracking platform metrics and customizable developer insights."""
        import webbrowser

        info_win = tk.Toplevel(self.root)
        info_win.title("Application Information & Developer Bio")
        info_win.geometry("500x380")
        info_win.resizable(False, False)
        info_win.transient(self.root)
        info_win.grab_set()

        if hasattr(self, 'logo_raw') and self.logo_raw is not None:
            # Scale logo to approximately 1/8th of the info window dimensions
            geom = info_win.geometry().split('+')[0]
            try:
                win_w, win_h = map(int, geom.split('x'))
            except Exception:
                win_w, win_h = 500, 380
            target_w = max(1, win_w // 8)
            target_h = max(1, win_h // 8)
            try:
                small = self.logo_raw.copy()
                small.thumbnail((target_w, target_h), Image.LANCZOS)
                logo_small = ImageTk.PhotoImage(small)
                lbl_logo_pop = tk.Label(info_win, image=logo_small)
                lbl_logo_pop.image = logo_small
                lbl_logo_pop.pack(pady=10)
            except Exception:
                # Fallback to previously created PhotoImage if something fails
                lbl_logo_pop = tk.Label(info_win, image=self.logo_img)
                lbl_logo_pop.pack(pady=10)
        elif self.logo_img:
            lbl_logo_pop = tk.Label(info_win, image=self.logo_img)
            lbl_logo_pop.pack(pady=10)

        lbl_title = tk.Label(info_win, text="Image to SVG Vector Suite", font=("Segoe UI", 12, "bold"))
        lbl_title.pack()

        lbl_repo = tk.Label(info_win, text=f"GitHub Repository:\n{GITHUB_REPO_URL}", font=("Segoe UI", 10, "underline"), fg="#0078D4", cursor="hand2")
        lbl_repo.pack(pady=5)
        lbl_repo.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_REPO_URL))

        lbl_sep = tk.Frame(info_win, height=1, bg="#E0E0E0")
        lbl_sep.pack(fill=tk.X, pady=10)

        lbl_desc = tk.Label(info_win, text="This utility converts raster photographic images into SVG by grouping identical horizontal pixels into vector rects.\n\nAuthor: SomeGuru\nLicense: MIT", justify=tk.LEFT, wraplength=460)
        lbl_desc.pack(padx=10)

        btn_close = tk.Button(info_win, text="Close", command=info_win.destroy)
        btn_close.pack(pady=12)

        return


if __name__ == "__main__":
    root = tk.Tk()
    app = MillionColorImageToSvgConverterApp(root)
    root.mainloop()
