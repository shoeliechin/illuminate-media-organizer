#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import sys
import os

class MediaOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Organizer")
        self.root.geometry("800x700")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.sorter_frame = ttk.Frame(self.notebook)
        self.searcher_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.sorter_frame, text="Media Sorter")
        self.notebook.add(self.searcher_frame, text="Media Searcher")

        self.setup_sorter_tab()
        self.setup_searcher_tab()

    def setup_sorter_tab(self):
        main_frame = ttk.Frame(self.sorter_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directories", padding=10)
        dir_frame.pack(fill='x', pady=(0, 10))

        # Source directory
        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(dir_frame, textvariable=self.source_var, width=60)
        source_entry.grid(row=0, column=1, padx=(10, 5), pady=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_source).grid(row=0, column=2, pady=(0, 5))

        # Destination directory
        ttk.Label(dir_frame, text="Destination Directory:").grid(row=1, column=0, sticky='w')
        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(dir_frame, textvariable=self.dest_var, width=60)
        dest_entry.grid(row=1, column=1, padx=(10, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_dest).grid(row=1, column=2)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))

        self.copy_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Copy files (instead of moving)", variable=self.copy_var).grid(row=0, column=0, sticky='w')

        self.dry_run_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Dry run (simulate without changes)", variable=self.dry_run_var).grid(row=1, column=0, sticky='w')

        ttk.Label(options_frame, text="Fallback to file time:").grid(row=2, column=0, sticky='w', pady=(10, 0))
        self.fallback_var = tk.StringVar(value="none")
        fallback_frame = ttk.Frame(options_frame)
        fallback_frame.grid(row=3, column=0, sticky='w')
        ttk.Radiobutton(fallback_frame, text="None", variable=self.fallback_var, value="none").pack(side='left')
        ttk.Radiobutton(fallback_frame, text="Created", variable=self.fallback_var, value="created").pack(side='left', padx=(10, 0))
        ttk.Radiobutton(fallback_frame, text="Modified", variable=self.fallback_var, value="modified").pack(side='left', padx=(10, 0))

        # Run button
        ttk.Button(main_frame, text="Run Media Sorter", command=self.run_sorter).pack(pady=10)

        # Output
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding=10)
        output_frame.pack(fill='both', expand=True)

        self.sorter_output = scrolledtext.ScrolledText(output_frame, height=15)
        self.sorter_output.pack(fill='both', expand=True)

    def setup_searcher_tab(self):
        main_frame = ttk.Frame(self.searcher_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Search directory
        dir_frame = ttk.LabelFrame(main_frame, text="Search Directory", padding=10)
        dir_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(dir_frame, text="Search in:").grid(row=0, column=0, sticky='w')
        self.search_dir_var = tk.StringVar()
        search_entry = ttk.Entry(dir_frame, textvariable=self.search_dir_var, width=60)
        search_entry.grid(row=0, column=1, padx=(10, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_search_dir).grid(row=0, column=2)

        # Filters
        filters_frame = ttk.LabelFrame(main_frame, text="Filters", padding=10)
        filters_frame.pack(fill='x', pady=(0, 10))

        # Year and Month
        ttk.Label(filters_frame, text="Year (e.g., 2022 or 2020-2023):").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.year_var = tk.StringVar()
        ttk.Entry(filters_frame, textvariable=self.year_var, width=20).grid(row=0, column=1, sticky='w', padx=(10, 0), pady=(0, 5))

        ttk.Label(filters_frame, text="Month (e.g., 1 or 3-6):").grid(row=1, column=0, sticky='w', pady=(0, 5))
        self.month_var = tk.StringVar()
        ttk.Entry(filters_frame, textvariable=self.month_var, width=20).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(0, 5))

        # Keywords
        ttk.Label(filters_frame, text="Keywords (space-separated):").grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.keywords_var = tk.StringVar()
        ttk.Entry(filters_frame, textvariable=self.keywords_var, width=40).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(0, 5))

        ttk.Label(filters_frame, text="Keyword match:").grid(row=3, column=0, sticky='w', pady=(0, 5))
        self.keyword_match_var = tk.StringVar(value="any")
        keyword_frame = ttk.Frame(filters_frame)
        keyword_frame.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=(0, 5))
        ttk.Radiobutton(keyword_frame, text="Any", variable=self.keyword_match_var, value="any").pack(side='left')
        ttk.Radiobutton(keyword_frame, text="All", variable=self.keyword_match_var, value="all").pack(side='left', padx=(10, 0))

        # Rating filters
        rating_frame = ttk.LabelFrame(filters_frame, text="Rating Filters", padding=5)
        rating_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        self.rating_type_var = tk.StringVar(value="none")
        ttk.Radiobutton(rating_frame, text="No rating filter", variable=self.rating_type_var, value="none").grid(row=0, column=0, sticky='w')
        ttk.Radiobutton(rating_frame, text="Specific rating/range:", variable=self.rating_type_var, value="specific").grid(row=1, column=0, sticky='w')
        self.rating_var = tk.StringVar()
        ttk.Entry(rating_frame, textvariable=self.rating_var, width=15).grid(row=1, column=1, padx=(10, 0))
        ttk.Radiobutton(rating_frame, text="Rejected files (-1)", variable=self.rating_type_var, value="rejected").grid(row=2, column=0, sticky='w')
        ttk.Radiobutton(rating_frame, text="Picked files (0-5)", variable=self.rating_type_var, value="picked").grid(row=3, column=0, sticky='w')

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))

        self.open_dirs_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Open directories containing matched files", variable=self.open_dirs_var).pack(anchor='w')

        # Run button
        ttk.Button(main_frame, text="Run Media Searcher", command=self.run_searcher).pack(pady=10)

        # Output
        output_frame = ttk.LabelFrame(main_frame, text="Search Results", padding=10)
        output_frame.pack(fill='both', expand=True)

        self.searcher_output = scrolledtext.ScrolledText(output_frame, height=12)
        self.searcher_output.pack(fill='both', expand=True)

    def browse_source(self):
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_var.set(directory)

    def browse_dest(self):
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.dest_var.set(directory)

    def browse_search_dir(self):
        directory = filedialog.askdirectory(title="Select Search Directory")
        if directory:
            self.search_dir_var.set(directory)

    def run_command_in_thread(self, command, output_widget):
        def run():
            try:
                output_widget.delete(1.0, tk.END)
                output_widget.insert(tk.END, f"Running: {' '.join(command)}\n\n")
                output_widget.update()

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )

                for line in process.stdout:
                    output_widget.insert(tk.END, line)
                    output_widget.see(tk.END)
                    output_widget.update()

                process.wait()

                if process.returncode == 0:
                    output_widget.insert(tk.END, "\n✓ Command completed successfully!")
                else:
                    output_widget.insert(tk.END, f"\n✗ Command failed with return code {process.returncode}")

            except Exception as e:
                output_widget.insert(tk.END, f"\nError: {str(e)}")

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def run_sorter(self):
        if not self.source_var.get() or not self.dest_var.get():
            messagebox.showerror("Error", "Please select both source and destination directories")
            return

        command = [sys.executable, "media_sorter.py", self.source_var.get(), self.dest_var.get()]

        if self.copy_var.get():
            command.append("--copy")
        if self.dry_run_var.get():
            command.append("--dry-run")
        if self.fallback_var.get() != "none":
            command.extend(["--fallback-to-file-time", self.fallback_var.get()])

        self.run_command_in_thread(command, self.sorter_output)

    def run_searcher(self):
        if not self.search_dir_var.get():
            messagebox.showerror("Error", "Please select a search directory")
            return

        command = [sys.executable, "media_searcher.py", self.search_dir_var.get()]

        if self.year_var.get():
            command.extend(["--year", self.year_var.get()])
        if self.month_var.get():
            command.extend(["--month", self.month_var.get()])
        if self.keywords_var.get():
            keywords = self.keywords_var.get().split()
            command.extend(["--keyword"] + keywords)
            command.extend(["--keyword-match", self.keyword_match_var.get()])

        rating_type = self.rating_type_var.get()
        if rating_type == "specific" and self.rating_var.get():
            command.extend(["--rating", self.rating_var.get()])
        elif rating_type == "rejected":
            command.append("--rejected")
        elif rating_type == "picked":
            command.append("--picked")

        if self.open_dirs_var.get():
            command.append("--open-dirs")

        self.run_command_in_thread(command, self.searcher_output)

def main():
    root = tk.Tk()
    app = MediaOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()