import os
import shutil
import sqlite3
import random
import string
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("500x400")
        self.root.configure(bg="#2e3f4f")

        # Set up SQLite database
        self.setup_database()

        # Heading
        self.heading = tk.Label(root, text="Organize Files by Extension", font=("Arial", 16, "bold"), bg="#2e3f4f", fg="white")
        self.heading.pack(pady=10)

        # Buttons Frame
        buttons_frame = tk.Frame(root, bg="#2e3f4f")
        buttons_frame.pack(pady=5)
        
        # Select Folder Button
        self.select_button = tk.Button(buttons_frame, text="Select Folder", command=self.select_folder, font=("Arial", 12), bg="#1e88e5", fg="white")
        self.select_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Organize Button
        self.organize_button = tk.Button(buttons_frame, text="Organize Files", command=self.organize_files, state=tk.DISABLED, font=("Arial", 12), bg="#1e88e5", fg="white")
        self.organize_button.grid(row=0, column=1, padx=5, pady=5)

        # Show Info Button
        self.info_button = tk.Button(buttons_frame, text="Show Info", command=self.show_info, font=("Arial", 12), bg="#1e88e5", fg="white")
        self.info_button.grid(row=1, column=0, padx=5, pady=5)

        # Add Extension Button
        self.add_ext_button = tk.Button(buttons_frame, text="Add Extension", command=self.open_add_extension_window, font=("Arial", 12), bg="#1e88e5", fg="white")
        self.add_ext_button.grid(row=1, column=1, padx=5, pady=5)

        # Create Test Case Button
        self.create_test_case_button = tk.Button(buttons_frame, text="Create Test Case", command=self.create_test_case, font=("Arial", 12), bg="#1e88e5", fg="white")
        self.create_test_case_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Folder path label
        self.folder_path_label = tk.Label(root, text="", font=("Arial", 10), fg="white", bg="#2e3f4f")
        self.folder_path_label.pack(pady=5)

        # Selected folder path
        self.folder_path = ""

    def setup_database(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect("file_organizer.db")
        self.cursor = self.conn.cursor()
        # Create table if not exists
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_extensions (
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                extension TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def fetch_extensions(self):
        # Fetch extensions from the database
        self.cursor.execute("SELECT category, extension FROM file_extensions")
        extensions = self.cursor.fetchall()
        
        # Organize fetched extensions into a dictionary
        extension_mapping = {}
        for category, ext in extensions:
            if category not in extension_mapping:
                extension_mapping[category] = []
            extension_mapping[category].append(ext)
        
        # Add default categories if not present
        default_categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'Documents': ['.pdf', '.docx', '.txt', '.doc', '.xls', '.xlsx', '.pptx'],
            'Music': ['.mp3', '.wav', '.aac', '.flac'],
            'Videos': ['.mp4', '.mkv', '.mov', '.avi'],
            'Archives': ['.zip', '.rar', '.tar', '.gz', '.7z'],
            'Scripts': ['.py', '.js', '.html', '.css'],
            'Shortcuts': ['.lnk', '.url', '.webloc']
        }
        for category, exts in default_categories.items():
            if category not in extension_mapping:
                extension_mapping[category] = exts
        
        return extension_mapping

    def select_folder(self):
        # Open dialog to select folder
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_path_label.config(text=f"Selected Folder: {self.folder_path}")
            self.organize_button.config(state=tk.NORMAL)
        else:
            self.folder_path_label.config(text="")
            self.organize_button.config(state=tk.DISABLED)

    def organize_files(self):
        # Fetch extensions from the database
        extension_mapping = self.fetch_extensions()
        
        if not os.path.isdir(self.folder_path):
            messagebox.showerror("Error", "Please select a valid folder.")
            return
        
        # Dictionary to store file counts by category
        file_count = {category: 0 for category in extension_mapping.keys()}
        file_count['Others'] = 0  # For files that don't match any category
        total_files = 0

        # Organize files into folders
        for file in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, file)
            if os.path.isfile(file_path):
                # Find matching folder for the file's extension
                file_extension = os.path.splitext(file)[1].lower()
                folder_name = None
                
                for folder, extensions in extension_mapping.items():
                    if file_extension in extensions:
                        folder_name = folder
                        break
                if not folder_name:
                    folder_name = 'Others'
                
                # Create folder if it doesn't exist
                folder_path = os.path.join(self.folder_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                # Move file to the new folder
                shutil.move(file_path, os.path.join(folder_path, file))
                
                # Increment file count for the folder
                file_count[folder_name] += 1
                total_files += 1

        # Display summary layout
        self.display_summary(file_count, total_files)

    def display_summary(self, file_count, total_files):
        # Create a new window to display the summary
        summary_window = tk.Toplevel(self.root)
        summary_window.title("File Organization Summary")
        summary_window.geometry("500x350")
        summary_window.configure(bg="#2e3f4f")

        # Add summary panel title
        tk.Label(summary_window, text="File Organization Summary", font=("Arial", 14, "bold"), bg="#2e3f4f", fg="white").pack(pady=10)
        
        # Use Treeview for the table layout
        tree = ttk.Treeview(summary_window, columns=("Category", "File Count"), show="headings", height=10)
        tree.heading("Category", text="Category")
        tree.heading("File Count", text="File Count")
        tree.column("Category", width=200, anchor="center")
        tree.column("File Count", width=100, anchor="center")
        
        # Add data to the table
        for category, count in file_count.items():
            tree.insert("", tk.END, values=(category, count))
        
        # Add total file count
        tree.insert("", tk.END, values=("Total Files", total_files))

        # Style Treeview for dark theme
        style = ttk.Style()
        style.configure("Treeview", background="#2e3f4f", foreground="white", rowheight=30, font=("Arial", 12))
        style.configure("Treeview.Heading", background="#1e88e5", foreground="white", font=("Arial", 12, "bold"))
        
        tree.pack(pady=20)

    def create_test_case(self):
        # Allow the user to select the destination path
        test_folder_path = filedialog.askdirectory(title="Select Destination for Test Folder")
        if not test_folder_path:
            return  # User cancelled the selection

        # Create a new folder for the test case
        test_folder = os.path.join(test_folder_path, "Unorganized_Test_Case")
        os.makedirs(test_folder, exist_ok=True)

        # Randomly generate test files with different extensions
        extension_mapping = self.fetch_extensions()
        all_extensions = [ext for extensions in extension_mapping.values() for ext in extensions] + ['.txt', '.mp4', '.jpg']
        
        for _ in range(20):  # Create 20 random files
            file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            ext = random.choice(all_extensions)
            file_path = os.path.join(test_folder, f"{file_name}{ext}")
            with open(file_path, 'w') as f:
                f.write("Test file content")

        messagebox.showinfo("Test Case Created", f"Test case folder created at: {test_folder}")

    def show_info(self):
        # Pop-up window to show information about the user
        info_text = (
            "About User:\n\n"
            "Name: Prasanth\n"
            "Degree: MCA\n"
            "Instructor: Anusree (Python Tutor)"
        )
        messagebox.showinfo("User Information", info_text)

    def open_add_extension_window(self):
        # Open a new window to add an extension
        self.add_ext_window = tk.Toplevel(self.root)
        self.add_ext_window.title("Add New Extension")
        self.add_ext_window.geometry("300x200")
        self.add_ext_window.configure(bg="#3b4d61")

        # Category Label and Entry
        tk.Label(self.add_ext_window, text="Category:", bg="#3b4d61", fg="white").pack(pady=5)
        self.category_entry = tk.Entry(self.add_ext_window)
        self.category_entry.pack(pady=5)

        # Extension Label and Entry
        tk.Label(self.add_ext_window, text="Extension:", bg="#3b4d61", fg="white").pack(pady=5)
        self.extension_entry = tk.Entry(self.add_ext_window)
        self.extension_entry.pack(pady=5)

        # Save Button
        save_button = tk.Button(self.add_ext_window, text="Save", command=self.add_extension, bg="#1e88e5", fg="white")
        save_button.pack(pady=10)

    def add_extension(self):
        # Get category and extension from the entries
        category = self.category_entry.get().strip()
        extension = self.extension_entry.get().strip().lower()
        
        if not category or not extension:
            messagebox.showerror("Error", "Please fill both fields.")
            return
        
        # Insert into database
        self.cursor.execute("INSERT INTO file_extensions (category, extension) VALUES (?, ?)", (category, extension))
        self.conn.commit()

        # Confirmation and close window
        messagebox.showinfo("Success", f"Extension '{extension}' added to category '{category}'.")
        self.add_ext_window.destroy()

# Run the app
root = tk.Tk()
app = FileOrganizerApp(root)
root.mainloop()
