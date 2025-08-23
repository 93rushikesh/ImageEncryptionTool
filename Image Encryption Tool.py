import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import random


original_img = None
encrypted_img_full = None
decrypted_img_full = None
scramble_info = None
PREVIEW_SIZE = (360, 360)


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


def open_image():
    global original_img, encrypted_img_full, decrypted_img_full, scramble_info
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
    if not path:
        return
    try:
        img = Image.open(path).convert("RGB")
        original_img = img
        encrypted_img_full = None
        decrypted_img_full = None
        scramble_info = None
        show_preview(original_img)
        messagebox.showinfo("Loaded", "Image loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open image:\n{e}")

def encrypt_image():
    global original_img, encrypted_img_full, scramble_info
    if original_img is None:
        messagebox.showerror("Error", "Please load an image first!")
        return

    arr = np.array(original_img)
    h, w, c = arr.shape

    
    scramble_info = {"col_perm": None, "row_shifts": [], "row_invert": []}

    
    cols = list(range(w))
    random.shuffle(cols)
    scramble_info["col_perm"] = cols.copy()
    arr = arr[:, cols, :]

   
    row_shifts = []
    for i in range(h):
        shift = random.randint(0, w-1)
        row_shifts.append(shift)
        arr[i] = np.roll(arr[i], shift, axis=0)
    scramble_info["row_shifts"] = row_shifts

    
    invert_rows = []
    for i in range(0, h, random.randint(10, 30)):
        arr[i] = 255 - arr[i]
        invert_rows.append(i)
    scramble_info["row_invert"] = invert_rows

    encrypted_img_full = Image.fromarray(arr)
    show_preview(encrypted_img_full)
    messagebox.showinfo("Encrypted", "Image encrypted successfully!")

def decrypt_image():
    global decrypted_img_full, encrypted_img_full, scramble_info
    if encrypted_img_full is None or scramble_info is None:
        messagebox.showerror("Error", "Please encrypt an image first!")
        return

    arr = np.array(encrypted_img_full)
    h, w, c = arr.shape

    
    for i in scramble_info["row_invert"]:
        arr[i] = 255 - arr[i]

   
    for i, shift in enumerate(scramble_info["row_shifts"]):
        arr[i] = np.roll(arr[i], -shift, axis=0)


    inv_cols = np.argsort(scramble_info["col_perm"])
    arr = arr[:, inv_cols, :]

    decrypted_img_full = Image.fromarray(arr)
    show_preview(decrypted_img_full)
    messagebox.showinfo("Decrypted", "Image decrypted successfully!")

def save_encrypted():
    save_image(encrypted_img_full, "encrypted.png")

def save_decrypted():
    save_image(decrypted_img_full, "decrypted.png")

def clear_all():
    global original_img, encrypted_img_full, decrypted_img_full, scramble_info
    original_img = None
    encrypted_img_full = None
    decrypted_img_full = None
    scramble_info = None
    lbl_image.config(image="")
    lbl_image.image = None


root = tk.Tk()
root.title("🔐 Scratch Image Encryption Tool")
root.geometry("540x680")
root.resizable(False, False)

hdr = tk.Label(root, text="🔐 Scratch Image Encryption Tool", font=("Segoe UI", 14, "bold"))
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
