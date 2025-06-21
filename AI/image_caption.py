import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import os
import threading
from datetime import datetime
import queue


class ImageCaptioningApp:
    def __init__(self, root, use_dnd=False):
        self.root = root
        self.root.title("🎯 Image Captioning AI - Internship Project")
        self.root.geometry("850x650")
        self.root.minsize(650, 450)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None
        self.model_loading = False
        self.caption_queue = queue.Queue()
        self.current_caption = ""
        self.use_dnd = use_dnd

        self.set_styles()
        self.setup_gui()
        self.load_model_async()

    def set_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        # Button styling
        style.configure("TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=8,
                        background="#007acc",
                        foreground="white")
        style.map("TButton",
                  background=[("active", "#005f99"), ("pressed", "#004b80")],
                  foreground=[("disabled", "#cccccc")])

        # Labels and frames
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Caption.TLabel",
                        font=("Arial", 12, "italic"),
                        background="#f0f9ff",
                        foreground="#0a3d62",
                        padding=8,
                        relief="solid")
        style.configure("History.TLabel", background="#ffffff")
        style.configure("TFrame", background="#e6f2ff")

        # Progressbar
        style.configure("TProgressbar", troughcolor="#d6eaff", bordercolor="#a3d5ff",
                        background="#007acc", lightcolor="#66bfff", darkcolor="#005f99")

        # Root window bg
        self.root.configure(bg="#e6f2ff")

    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.image_label = ttk.Label(self.main_frame,
                                     text="🖼️ No Image Selected",
                                     background="#ffffff",
                                     relief="solid",
                                     borderwidth=2,
                                     anchor="center",
                                     font=("Arial", 11, "italic"),
                                     padding=10)
        self.image_label.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(5, 10))
        self.main_frame.rowconfigure(0, weight=2)
        self.main_frame.columnconfigure(0, weight=1)

        self.caption_var = tk.StringVar(value="Caption will appear here...")
        self.caption_display = ttk.Label(self.main_frame, textvariable=self.caption_var, wraplength=600,
                                         style="Caption.TLabel", anchor="center", justify="center")
        self.caption_display.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        self.progress = ttk.Progressbar(self.main_frame, mode="determinate")
        self.progress.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

        self.history_text = tk.Text(self.main_frame, height=8, wrap="word", bg="#fefefe", font=("Consolas", 10),
                                    state="disabled")
        self.history_text.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)
        self.main_frame.rowconfigure(3, weight=1)

        # History border
        self.history_text.configure(highlightbackground="#cccccc", highlightthickness=1,
                                    relief="solid", bd=1)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.history_text.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.history_text.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="📁 Upload Image(s)", command=self.upload_images).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="💾 Save Captions", command=self.save_captions).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="🧹 Clear History", command=self.clear_history).grid(row=0, column=2, padx=5)

        if self.use_dnd:
            try:
                from tkinterdnd2 import DND_FILES
                self.image_label.drop_target_register(DND_FILES)
                self.image_label.dnd_bind("<<Drop>>", self.handle_drop)
            except ImportError:
                print("tkinterdnd2 not installed. Drag-and-drop disabled.")
                self.use_dnd = False

    def load_model_async(self):
        self.model_loading = True
        self.caption_var.set("🔄 Loading BLIP model (Salesforce)...")
        threading.Thread(target=self.load_model, daemon=True).start()

    def load_model(self):
        try:
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base").to(self.device)
            self.caption_var.set(f"✅ Model loaded on {self.device}. Upload an image!")
        except Exception as e:
            self.caption_var.set(f"❌ Error loading model: {e}")
        finally:
            self.model_loading = False

    def upload_images(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp")]
        paths = filedialog.askopenfilenames(filetypes=filetypes)
        if paths:
            threading.Thread(target=self.process_images, args=(paths,), daemon=True).start()

    def handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        valid_paths = [p for p in paths if p.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
        if valid_paths:
            threading.Thread(target=self.process_images, args=(valid_paths,), daemon=True).start()
        else:
            messagebox.showerror("Error", "⚠️ No valid image files dropped.")

    def process_images(self, paths):
        if self.model_loading:
            messagebox.showwarning("Please wait", "Model is still loading. Please wait.")
            return

        self.progress["maximum"] = len(paths)
        self.progress["value"] = 0
        self.caption_var.set("⏳ Processing images...")

        for i, path in enumerate(paths):
            try:
                image = Image.open(path).convert("RGB")
                inputs = self.processor(image, return_tensors="pt").to(self.device)
                output = self.model.generate(**inputs, max_length=50, num_beams=5)
                caption = self.processor.decode(output[0], skip_special_tokens=True)
                self.current_caption = caption
                self.display_image(image)
                self.caption_var.set(caption)
                self.add_to_history(path, caption)
            except Exception as e:
                error_msg = f"❌ Error processing {os.path.basename(path)}: {e}"
                self.caption_var.set(error_msg)
                self.add_to_history(path, error_msg)
                self.display_image(Image.new("RGB", (400, 300), "gray"))

            self.progress["value"] = i + 1
            self.root.update_idletasks()

        if len(paths) > 1:
            self.caption_var.set(f"✅ Finished processing {len(paths)} image(s).")

    def display_image(self, image):
        image = image.copy()
        image.thumbnail((400, 300))
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        text = self.current_caption or "No caption"
        bg_y = image.height - 30
        draw.rectangle((0, bg_y, image.width, image.height), fill=(0, 0, 0, 128))
        draw.text((10, bg_y + 5), text, font=font, fill=(255, 255, 255))

        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo

    def add_to_history(self, image_path, caption):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {os.path.basename(image_path)}:\n  {caption}\n\n"
        self.history_text.configure(state="normal")
        self.history_text.insert("end", entry)
        self.history_text.configure(state="disabled")
        self.history_text.see("end")
        self.caption_queue.put((image_path, caption))

    def clear_history(self):
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.configure(state="disabled")
        self.caption_queue.queue.clear()
        self.caption_var.set("🧹 History cleared. Upload an image to caption.")

    def save_captions(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                while not self.caption_queue.empty():
                    image_path, caption = self.caption_queue.get()
                    f.write(f"{os.path.basename(image_path)}: {caption}\n")
            messagebox.showinfo("Saved", "💾 Captions saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to save: {e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        app = ImageCaptioningApp(root, use_dnd=True)
    except ImportError:
        root = tk.Tk()
        app = ImageCaptioningApp(root, use_dnd=False)
        print("tkinterdnd2 not installed. Drag-and-drop disabled.")

    app.run()
