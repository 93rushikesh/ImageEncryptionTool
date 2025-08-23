import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import random

# ===== Globals =====
original_img = None
encrypted_img_full = None
decrypted_img_full = None
scramble_indices = None
PREVIEW_SIZE = (360, 360)

# ===== Helpers =====
def make_preview(pil_image):
    preview = pil_image.copy()
    preview.thumbnail(PREVIEW_SIZE)
    return ImageTk.PhotoImage(preview)

def show_preview(pil_image):
    tk_img = make_preview(pil_image)
    lbl_image.config(image=tk_img)
    lbl_image.image = tk_img

def save_image(pil_image, suggested_name="image.png"):
    if pil_image is None:
        messagebox.showwarning("Nothing to save", "No image to save.")
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialfile=suggested_name,
        filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg"), ("All Files", "*.*")]
    )
    if save_path:
        pil_image.save(save_path)
        messagebox.showinfo("Saved", f"Saved: {os.path.basename(save_path)}")

# ===== Actions =====
def open_image():
    global original_img, encrypted_img_full, decrypted_img_full, scramble_indices
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
    if not path:
        return
    try:
        img = Image.open(path).convert("RGB")
        original_img = img
        encrypted_img_full = None
        decrypted_img_full = None
        scramble_indices = None
        show_preview(original_img)
        messagebox.showinfo("Loaded", "Image loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open image:\n{e}")

def encrypt_image():
    global original_img, encrypted_img_full, scramble_indices
    if original_img is None:
        messagebox.showerror("Error", "Please load an image first!")
        return
    arr = np.array(original_img)
    h, w, c = arr.shape
    flat = arr.reshape(-1, c)

    # generate scramble order
    scramble_indices = list(range(len(flat)))
    random.shuffle(scramble_indices)

    encrypted_flat = flat[scramble_indices]
    encrypted_arr = encrypted_flat.reshape(h, w, c)
    encrypted_img_full = Image.fromarray(encrypted_arr)

    show_preview(encrypted_img_full)
    messagebox.showinfo("Encrypted", "Image encrypted successfully!")

def decrypt_image():
    global encrypted_img_full, decrypted_img_full, scramble_indices
    if encrypted_img_full is None or scramble_indices is None:
        messagebox.showerror("Error", "Please encrypt an image first!")
        return

    arr = np.array(encrypted_img_full)
    h, w, c = arr.shape
    flat = arr.reshape(-1, c)

    # reverse scramble
    decrypted_flat = np.zeros_like(flat)
    for i, j in enumerate(scramble_indices):
        decrypted_flat[j] = flat[i]

    decrypted_arr = decrypted_flat.reshape(h, w, c)
    decrypted_img_full = Image.fromarray(decrypted_arr)

    show_preview(decrypted_img_full)
    messagebox.showinfo("Decrypted", "Image decrypted back successfully!")

def save_encrypted():
    save_image(encrypted_img_full, "encrypted.png")

def save_decrypted():
    save_image(decrypted_img_full, "decrypted.png")

def clear_all():
    global original_img, encrypted_img_full, decrypted_img_full, scramble_indices
    original_img = None
    encrypted_img_full = None
    decrypted_img_full = None
    scramble_indices = None
    lbl_image.config(image="")
    lbl_image.image = None

# ===== GUI =====
root = tk.Tk()
root.title("Image Encryption Tool")
root.geometry("520x640")
root.resizable(False, False)

hdr = tk.Label(root, text="🔐 Image Encryption Tool", font=("Segoe UI", 14, "bold"))
hdr.pack(pady=(12, 6))

btn_frame = tk.Frame(root)
btn_frame.pack(pady=6)

tk.Button(btn_frame, text="📂 Open Image", width=18, command=open_image).grid(row=0, column=0, padx=6, pady=4)
tk.Button(btn_frame, text="🔒 Encrypt", width=18, command=encrypt_image).grid(row=0, column=1, padx=6, pady=4)
tk.Button(btn_frame, text="🔓 Decrypt", width=18, command=decrypt_image).grid(row=1, column=0, padx=6, pady=4)
tk.Button(btn_frame, text="💾 Save Encrypted", width=18, command=save_encrypted).grid(row=1, column=1, padx=6, pady=4)
tk.Button(btn_frame, text="💾 Save Decrypted", width=18, command=save_decrypted).grid(row=2, column=0, padx=6, pady=4)
tk.Button(btn_frame, text="🧹 Clear All", width=18, command=clear_all).grid(row=2, column=1, padx=6, pady=4)

sep = tk.Frame(root, height=2, bd=1, relief="sunken")
sep.pack(fill="x", padx=10, pady=8)

tk.Label(root, text="Preview:", fg="gray").pack()
lbl_image = tk.Label(root, bd=2, relief="groove", width=360, height=360)
lbl_image.pack(pady=8)

root.mainloop()
