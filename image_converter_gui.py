import os
import sys
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import requests
import webbrowser

# Try to set an explicit Windows AppUserModelID for proper taskbar icon behavior
try:
    import ctypes
    myappid = "Guru.ImageToSvgConverter.App.v1.0.2"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    pass

__version__ = "1.0.2"
GITHUB_REPO_URL = "https://github.com/SomeGuru/image2svg"
GITHUB_API_LATEST = "https://api.github.com/repos/SomeGuru/image2svg/releases/latest"
LOGO_URL = "https://www.it2innovations.com/images/logo.png"


class MillionColorImageToSvgConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Photographic Color SVG Vector Converter - Version {__version__}")
        self.root.geometry("1100x720")
        self.root.minsize(900, 620)

        self.source_path = ""
        self.preview_size = (420, 420)
        self.logo_raw = None
        self.logo_img = None

        self.load_application_logos()
        self.create_widgets()

        threading.Thread(target=self.check_for_updates_async, daemon=True).start()

    def load_application_logos(self):
        def _fetch():
            try:
                res = requests.get(LOGO_URL, timeout=5)
                if res.status_code == 200:
                    img_data = io.BytesIO(res.content)
                    raw = Image.open(img_data).convert("RGBA")
                    self.logo_raw = raw
                    self.logo_img = ImageTk.PhotoImage(raw)
                    self.root.iconphoto(True, self.logo_img)
            except Exception:
                pass

        threading.Thread(target=_fetch, daemon=True).start()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=15, pady=15)

        self.btn_update = tk.Button(top_frame, text="Checking for updates...", font=("Segoe UI", 9, "bold"),
                                    bg="#E1E1E1", fg="#666666", state=tk.DISABLED, command=self.trigger_self_upgrade, padx=8)
        self.btn_update.pack(side=tk.RIGHT, padx=(10, 0))

        tk.Label(top_frame, text="Source Image:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))

        self.ent_path = tk.Entry(top_frame, font=("Segoe UI", 10))
        self.ent_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Button(top_frame, text="Browse...", command=self.browse_file, bg="#0078D4", fg="white", padx=12, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)

        view_frame = tk.Frame(self.root)
        view_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.frame_before = tk.LabelFrame(view_frame, text=" Before (Original Raster Asset) ", font=("Segoe UI", 10, "bold"), fg="#555555")
        self.frame_before.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.lbl_before = tk.Label(self.frame_before, text="No source image loaded\nSupported formats: BMP, GIF, JPG, JPEG, HEIF, PNG", justify=tk.CENTER, fg="#888888")
        self.lbl_before.pack(fill=tk.BOTH, expand=True)

        self.frame_after = tk.LabelFrame(view_frame, text=" After (Million-Color Vector Preview) ", font=("Segoe UI", 10, "bold"), fg="#107C41")
        self.frame_after.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.lbl_after = tk.Label(self.frame_after, text="Awaiting deep-color engine initialization...", justify=tk.CENTER, fg="#888888")
        self.lbl_after.pack(fill=tk.BOTH, expand=True)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=15, pady=10)

        self.btn_convert = tk.Button(bottom_frame, text="Extract & Export Millions of Colors to SVG", font=("Segoe UI", 11, "bold"),
                                      bg="#107C41", fg="white", state=tk.DISABLED, command=self.convert_image, pady=8)
        self.btn_convert.pack(fill=tk.X)

        footer_frame = tk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Button(footer_frame, text="? Info", command=self.show_developer_info_modal, font=("Segoe UI", 9), bg="#F0F0F0", fg="#333333", padx=8).pack(side=tk.RIGHT, padx=(10, 0))

        tk.Label(footer_frame, text=f"App Version: v{__version__}", font=("Segoe UI", 9, "italic"), fg="#777777").pack(side=tk.RIGHT)

    def check_for_updates_async(self):
        try:
            res = requests.get(GITHUB_API_LATEST, timeout=6)
            if res.status_code == 200:
                data = res.json()
                latest_tag = data.get("tag_name", "1.0.0").replace("v", "")
                if latest_tag != __version__:
                    self.update_download_url = None
                    for asset in data.get("assets", []):
                        if asset.get("name") == "image_converter_gui.py":
                            self.update_download_url = asset.get("browser_download_url")
                            break
                    if not self.update_download_url:
                        self.update_download_url = "https://raw.githubusercontent.com/SomeGuru/image2svg/main/image_converter_gui.py"
                    self.root.after(0, lambda: self.btn_update.config(text="Update Available!", bg="#D83B01", fg="white", state=tk.NORMAL))
                else:
                    self.root.after(0, lambda: self.btn_update.config(text="Up to Date", bg="#107C41", fg="white", state=tk.DISABLED))
            else:
                raise requests.RequestException()
        except Exception:
            self.root.after(0, lambda: self.btn_update.config(text="Updates Offline", bg="#E1E1E1", fg="#999999", state=tk.DISABLED))

    def trigger_self_upgrade(self):
        if not hasattr(self, 'update_download_url') or not self.update_download_url:
            messagebox.showwarning("Upgrade Unavailable", "No update location discovered.")
            return
        if not messagebox.askyesno("Confirm Self-Upgrade", "Download and overwrite this script with the latest version from GitHub?"):
            return

        self.btn_update.config(text="Upgrading...", state=tk.DISABLED)

        def _upgrade():
            try:
                r = requests.get(self.update_download_url, timeout=15)
                if r.status_code == 200 and 'class MillionColorImageToSvgConverterApp' in r.text:
                    current = os.path.abspath(sys.argv[0])
                    with open(current, 'w', encoding='utf-8') as f:
                        f.write(r.text)
                    messagebox.showinfo("Upgrade Success", "Application upgraded. Please restart to apply updates.")
                    self.root.after(0, self.root.destroy)
                else:
                    raise ValueError('Downloaded content invalid')
            except Exception as e:
                messagebox.showerror("Upgrade Faulted", str(e))
                self.root.after(0, lambda: self.btn_update.config(text="Update Available!", bg="#D83B01", fg="white", state=tk.NORMAL))

        threading.Thread(target=_upgrade, daemon=True).start()

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
        info_win = tk.Toplevel(self.root)
        info_win.title("Application Information & Developer Bio")
        info_win.geometry("500x380")
        info_win.resizable(False, False)
        info_win.transient(self.root)
        info_win.grab_set()

        if self.logo_raw is not None:
            try:
                geom = info_win.geometry().split('+')[0]
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

        dev_bio_text = (
            "Enter your personal bio text or developer history notes here. "
            "This software structure has been engineered to process sub-pixel matrix alignments "
            "into native scalable vectors. You can completely customize this space directly "
            "inside the script code fields without breaking UI alignments."
        )

        lbl_bio = tk.Label(info_win, text=dev_bio_text, font=("Segoe UI", 9.5), fg="#333333", justify=tk.LEFT, wraplength=440)
        lbl_bio.pack(padx=25, pady=8, anchor=tk.W)

        btn_close = tk.Button(info_win, text="Close", command=info_win.destroy)
        btn_close.pack(pady=12)


if __name__ == "__main__":
    root = tk.Tk()
    app = MillionColorImageToSvgConverterApp(root)
    root.mainloop()
