from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import hashlib, base64
from Crypto.Cipher import AES
from pymongo import MongoClient
from PIL import Image, ImageTk
from Crypto.Util.Padding import pad, unpad

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['image_encryptor_db']
users = db['users']

# Function to load background images
def load_bg_image(window, image_path):
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((window.winfo_screenwidth(), window.winfo_screenheight()), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(bg_image)

    canvas = Canvas(window, width=window.winfo_screenwidth(), height=window.winfo_screenheight())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")
    return canvas, bg_image

# -----------------------
# Encryption Method
# -----------------------
def encrypt(imagename, password):
    try:
        plaintext = []
        plaintextstr = ""
        im = Image.open(imagename)
        pix = im.load()
        width, height = im.size

        for y in range(height):
            for x in range(width):
                plaintext.append(pix[x, y])

        for pixel in plaintext:
            plaintextstr += "".join([str(value + 100) for value in pixel])

        plaintextstr += f"h{height}hw{width}w"
        padded_plaintext = pad(plaintextstr.encode('utf-8'), AES.block_size)

        iv = b'This is an IV456'
        obj = AES.new(password, AES.MODE_CBC, iv)
        ciphertext = obj.encrypt(padded_plaintext)

        cipher_name = imagename + ".crypt"
        with open(cipher_name, 'wb') as f:
            f.write(base64.b64encode(ciphertext))

        messagebox.showinfo("Success", f"Image encrypted successfully!\nFile Path: {os.path.abspath(cipher_name)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# -----------------------
# Decryption Method
# -----------------------
def decrypt(ciphername, password):
    try:
        with open(ciphername, 'rb') as f:
            ciphertext = base64.b64decode(f.read())

        iv = b'This is an IV456'
        obj = AES.new(password, AES.MODE_CBC, iv)
        decrypted = unpad(obj.decrypt(ciphertext), AES.block_size).decode('utf-8').replace("n", "")

        height = int(decrypted.split("h")[1])
        width = int(decrypted.split("w")[1])
        decrypted = decrypted.replace(f"h{height}h", "").replace(f"w{width}w", "")

        pixels = [(int(decrypted[i:i+3]) - 100,
                   int(decrypted[i+3:i+6]) - 100,
                   int(decrypted[i+6:i+9]) - 100)
                  for i in range(0, len(decrypted), 9)]

        pixels = pixels[:width * height]  # Only the number of pixels matching the image size

        new_image = Image.new("RGB", (width, height))
        new_image.putdata(pixels)

        decrypted_image_path = "decrypted_image.png"
        new_image.save(decrypted_image_path)
        new_image.show()

        messagebox.showinfo("Success", f"Image decrypted successfully!\nFile Path: {os.path.abspath(decrypted_image_path)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# -----------------------
# User Authentication
# -----------------------
def create_account(email, username, password):
    if users.find_one({"username": username}):
        messagebox.showerror("Error", "Username already exists.")
    else:
        users.insert_one({"email": email, "username": username, "password": password})
        messagebox.showinfo("Success", "Account created successfully!")

def login(username, password):
    user = users.find_one({"username": username})
    if user and user["password"] == password:
        messagebox.showinfo("Success", "Login successful!")
        open_main_app()
    else:
        messagebox.showerror("Error", "Invalid credentials.")

# -----------------------
# Main App Window
# -----------------------
def open_main_app():
    root.destroy()
    main_app = Tk()
    main_app.title("Image Security System")
    main_app.geometry('800x600')

    # Load background image
    canvas, bg_image = load_bg_image(main_app, "encryption-bg-1.png")

    # Style settings for neon effects
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12, 'bold'), foreground='#00FFCC', background='#0F0F0F',
                    borderwidth=2, relief="raised", padding=10)

    style.configure('TLabel', font=('Helvetica', 14, 'bold'), foreground='#00FFCC')

    # Add labels and buttons
    Label(canvas, text="Enter Password:", font=("Helvetica", 16, "bold"), fg="#00FFCC", bg="#222").place(x=300, y=200)
    password_entry = Entry(main_app, show="*", width=20, font=("Helvetica", 16))
    canvas.create_window(450, 240, window=password_entry)

    encrypt_btn = ttk.Button(main_app, text="Encrypt", command=lambda: image_open(password_entry))
    canvas.create_window(350, 300, window=encrypt_btn)

    decrypt_btn = ttk.Button(main_app, text="Decrypt", command=lambda: cipher_open(password_entry))
    canvas.create_window(500, 300, window=decrypt_btn)

    footer = Label(canvas, text="Image Security System v1.0", font=("Helvetica", 10, "bold"), fg="#00FFCC", bg="#222")
    canvas.create_window(400, 560, window=footer)

    main_app.mainloop()

def image_open(password_entry):
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password.")
        return
    hashed_password = hashlib.sha256(password.encode()).digest()
    filename = filedialog.askopenfilename()
    encrypt(filename, hashed_password)

def cipher_open(password_entry):
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password.")
        return
    hashed_password = hashlib.sha256(password.encode()).digest()
    filename = filedialog.askopenfilename()
    decrypt(filename, hashed_password)

# -----------------------
# Login Page
# -----------------------
def login_page():
    global root
    root = Tk()
    root.title("Login")
    root.geometry('800x600')

    # Load background image
    canvas, bg_image = load_bg_image(root, "encryption-bg-1.png")

    # Header label
    header = Label(root, text="Login", font=("Helvetica", 24, "bold"), pady=20, fg="#00FFCC", bg="#222")
    canvas.create_window(400, 50, window=header)

    # Username and Password Fields
    Label(root, text="Username:", font=("Helvetica", 16, "bold"), fg="#00FFCC",bg="#222").place(x=200, y=150)
    username_entry = Entry(root, width=30, font=("Helvetica", 14))
    canvas.create_window(400, 190, window=username_entry)

    Label(root, text="Password:", font=("Helvetica", 16, "bold"), fg="#00FFCC",bg="#222").place(x=200, y=230)
    password_entry = Entry(root, show="*", width=30, font=("Helvetica", 14))
    canvas.create_window(400, 270, window=password_entry)

    # Login button
    login_btn = ttk.Button(root, text="Login", command=lambda: login(username_entry.get(), password_entry.get()))
    canvas.create_window(400, 330, window=login_btn)

    # Create Account button
    create_account_btn = ttk.Button(root, text="Create New Account", command=lambda: create_account_page())
    canvas.create_window(400, 380, window=create_account_btn)

    footer = Label(canvas, text="Don't have an account? Create one.", font=("Helvetica", 10), fg="#00FFCC",bg="#222")
    canvas.create_window(400, 430, window=footer)

    root.mainloop()

# -----------------------
# Create Account Page
# Create Account Page
def create_account_page():
    root.destroy()  # Close the current window (Login Page)
    create_acc = Tk()
    create_acc.title("Create Account")
    create_acc.geometry('800x600')

    # Load background image
    canvas, bg_image = load_bg_image(create_acc, "encryption-bg-1.png")

    header = Label(create_acc, text="Create Account", font=("Helvetica", 24, "bold"), pady=20, fg="#00FFCC", bg="#222")
    canvas.create_window(400, 50, window=header)

    # Email Entry
    Label(create_acc, text="Email:", font=("Helvetica", 16, "bold"), fg="#00FFCC", bg="#222").place(x=200, y=150)
    email_entry = Entry(create_acc, width=30, font=("Helvetica", 14))
    canvas.create_window(400, 190, window=email_entry)

    # Username Entry
    Label(create_acc, text="Username:", font=("Helvetica", 16, "bold"), fg="#00FFCC", bg="#222").place(x=200, y=230)
    username_entry = Entry(create_acc, width=30, font=("Helvetica", 14))
    canvas.create_window(400, 270, window=username_entry)

    # Password Entry
    Label(create_acc, text="Password:", font=("Helvetica", 16, "bold"), fg="#00FFCC", bg="#222").place(x=200, y=310)
    password_entry = Entry(create_acc, show="*", width=30, font=("Helvetica", 14))
    canvas.create_window(400, 350, window=password_entry)

    # Create Account Button
    create_btn = ttk.Button(
        create_acc, 
        text="Create Account", 
        command=lambda: create_account(email_entry.get(), username_entry.get(), password_entry.get())
    )
    canvas.create_window(400, 410, window=create_btn)

    # Login Button - To Go Back to Login Page
    login_btn = ttk.Button(
        create_acc, 
        text="Login", 
        command=lambda: go_to_login(create_acc)  # Transition to Login Page
    )
    canvas.create_window(400, 460, window=login_btn)

    footer = Label(canvas, text="Image Security System v1.0", font=("Helvetica", 10, "bold"), fg="#00FFCC", bg="#222")
    canvas.create_window(400, 560, window=footer)

    create_acc.mainloop()

# Function to Transition Back to Login Page
def go_to_login(current_window):
    current_window.destroy()  # Close the current window (Create Account Page)
    login_page()  # Open the Login Page

# Start the login page
login_page()
