import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES  # ✅ Correct import


class SketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Image-to-Sketch Converter")
        self.root.geometry("1000x600")
        self.root.configure(bg="#2e2e2e")

        self.images = {"original": None, "sketch": None}
        self.image_panels = {}

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#444", foreground="white", padding=6)
        style.map("TButton", background=[("active", "#666")])
        style.configure("TLabel", background="#2e2e2e", foreground="white")

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Open Image", command=self.open_file).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Save Sketch", command=self.save_sketch).pack(
            side="left", padx=5
        )

        # Intensity slider
        self.intensity = tk.IntVar(value=21)
        ttk.Label(button_frame, text="Sketch Intensity").pack(side="left", padx=10)
        self.intensity_slider = ttk.Scale(
            button_frame,
            from_=1,
            to=51,
            value=21,
            orient="horizontal",
            variable=self.intensity,
            command=self.update_sketch,
        )
        self.intensity_slider.pack(side="left")

        # Images Display
        self.canvas_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.original_label = ttk.Label(self.canvas_frame, text="Original Image")
        self.original_label.grid(row=0, column=0, pady=5)

        self.sketch_label = ttk.Label(self.canvas_frame, text="Sketch Image")
        self.sketch_label.grid(row=0, column=1, pady=5)

        self.image_panels["original"] = tk.Label(self.canvas_frame, bg="#1e1e1e")
        self.image_panels["original"].grid(row=1, column=0, padx=10, sticky="nsew")

        self.image_panels["sketch"] = tk.Label(self.canvas_frame, bg="#1e1e1e")
        self.image_panels["sketch"].grid(row=1, column=1, padx=10, sticky="nsew")

        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.columnconfigure(1, weight=1)
        self.canvas_frame.rowconfigure(1, weight=1)

        # ✅ Drag and Drop support with correct constant
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.drop_file)

    def convert_to_sketch(self, img, intensity=21):
        """
        Convert the input image to a pencil sketch effect.
        """
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted_img = cv2.bitwise_not(gray_img)
        blurred_img = cv2.GaussianBlur(
            inverted_img, (int(intensity) | 1, int(intensity) | 1), 0
        )
        inverted_blurred_img = cv2.bitwise_not(blurred_img)
        sketch_img = cv2.divide(gray_img, inverted_blurred_img, scale=256.0)
        return sketch_img

    def open_file(self):
        """
        Open an image file and display original and sketch versions.
        """
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")],
        )
        if file_path:
            self.load_image(file_path)

    def drop_file(self, event):
        """
        Handle drag-and-drop file.
        """
        file_path = event.data.strip("{}")  # clean the path from brackets
        self.load_image(file_path)

    def load_image(self, file_path):
        """
        Load and process the image.
        """
        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("Error", "Failed to load image.")
            return

        self.images["original"] = img
        self.display_image(img, "original")
        self.update_sketch()

    def update_sketch(self, event=None):
        """
        Update sketch image based on intensity slider.
        """
        if self.images["original"] is None:
            return
        sketch_img = self.convert_to_sketch(
            self.images["original"], self.intensity.get()
        )
        self.images["sketch"] = sketch_img
        self.display_image(sketch_img, "sketch")

    def display_image(self, img, img_type):
        """
        Display image on respective panel.
        """
        if img_type == "original":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
        else:
            img_pil = Image.fromarray(img).convert("L")

        img_pil = img_pil.resize((480, 480), Image.Resampling.LANCZOS)

        img_tk = ImageTk.PhotoImage(img_pil)

        panel = self.image_panels[img_type]
        panel.config(image=img_tk)
        panel.image = img_tk  # prevent garbage collection

    def save_sketch(self):
        """
        Save the sketch image.
        """
        if self.images["sketch"] is None:
            messagebox.showerror("Error", "No sketch image to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
        )
        if file_path:
            Image.fromarray(self.images["sketch"]).save(file_path)
            messagebox.showinfo("Success", "Sketch saved successfully!")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SketchApp(root)
    root.mainloop()
