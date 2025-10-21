#!/usr/bin/env python3
"""
Illuminate Media Organizer GUI - Graphical interface for sorting and searching media files.

Copyright (C) 2025  Shiue-Lang Chin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import sys
import os

# Handle imports whether run as module or script
try:
    from media_utils import is_exiftool_installed, get_pictures_directory, get_move_warning_message
    from __version__ import __version__
except ImportError:
    from src.media_utils import is_exiftool_installed, get_pictures_directory, get_move_warning_message
    from src.__version__ import __version__

class MediaOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Illuminate Media Organizer")
        self.root.geometry("750x850")
        self.root.minsize(700, 800)  # Set minimum window size to accommodate all options

        # Track running processes
        self.process_running = False
        self.current_process = None

        # Create main container frame
        main_container = ttk.Frame(root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))

        # Create tabs
        self.sorter_frame = ttk.Frame(self.notebook)
        self.searcher_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.sorter_frame, text="Media Sorter")
        self.notebook.add(self.searcher_frame, text="Media Searcher")


        self.setup_sorter_tab()
        self.setup_searcher_tab()

        # Single exiftool check for both tabs (optimization)
        self.check_exiftool_status()

        # Set up window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_exiftool_status(self):
        """Check exiftool installation once and update both tab statuses."""
        if is_exiftool_installed():
            self.sorter_status_text.set("✓ Ready")
            self.sorter_status_display.config(foreground="green")
            self.searcher_status_text.set("✓ Ready")
            self.searcher_status_display.config(foreground="green")
        else:
            error_msg = "Error: ExifTool not installed properly"
            self.sorter_status_text.set(error_msg)
            self.sorter_status_display.config(foreground="red")
            self.searcher_status_text.set(error_msg)
            self.searcher_status_display.config(foreground="red")

    def setup_sorter_tab(self):
        main_frame = ttk.Frame(self.sorter_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directories", padding=10)
        dir_frame.pack(fill='x', pady=(0, 10))

        # Configure grid weights for responsive resizing
        dir_frame.grid_columnconfigure(1, weight=1)

        # Source directory
        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(dir_frame, textvariable=self.source_var)
        source_entry.grid(row=0, column=1, sticky='ew', padx=(10, 5), pady=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_source).grid(row=0, column=2, pady=(0, 5))

        # Destination directory
        ttk.Label(dir_frame, text="Destination Directory:").grid(row=1, column=0, sticky='w')
        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(dir_frame, textvariable=self.dest_var)
        dest_entry.grid(row=1, column=1, sticky='ew', padx=(10, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_dest).grid(row=1, column=2)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))

        # Configure options frame for responsive layout
        options_frame.grid_columnconfigure(0, weight=1)

        self.copy_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Copy files (instead of moving)", variable=self.copy_var).grid(row=0, column=0, sticky='w', pady=2)

        self.dry_run_var = tk.BooleanVar(value=True)  # Default to checked
        ttk.Checkbutton(options_frame, text="Dry run (simulate without changes)", variable=self.dry_run_var).grid(row=1, column=0, sticky='w', pady=2)

        ttk.Label(options_frame, text="Fallback to file time:").grid(row=2, column=0, sticky='w', pady=(10, 5))
        self.fallback_var = tk.StringVar(value="none")
        fallback_frame = ttk.Frame(options_frame)
        fallback_frame.grid(row=3, column=0, sticky='ew', pady=2)
        ttk.Radiobutton(fallback_frame, text="None", variable=self.fallback_var, value="none").pack(side='left')
        ttk.Radiobutton(fallback_frame, text="Created", variable=self.fallback_var, value="created").pack(side='left', padx=(15, 0))
        ttk.Radiobutton(fallback_frame, text="Modified", variable=self.fallback_var, value="modified").pack(side='left', padx=(15, 0))

        # Status text above button
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=(10, 5))

        self.sorter_status_text = tk.StringVar()
        self.sorter_status_display = ttk.Label(
            status_frame,
            textvariable=self.sorter_status_text,
            anchor='center'
        )
        self.sorter_status_display.pack(fill='x')

        # Status will be set after initial check in __init__
        self.sorter_status_text.set("Checking ExifTool...")
        self.sorter_status_display.config(foreground="gray")

        # Run button - centered
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))

        self.sorter_run_button = ttk.Button(button_frame, text="Run Media Sorter", command=self.run_sorter)
        self.sorter_run_button.pack()

        # Output with expandable functionality
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill='both', expand=True)

        # Configure output frame for proper resizing
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Expandable text header
        self.sorter_expanded = tk.BooleanVar(value=False)
        self.sorter_expand_label = ttk.Label(
            output_frame,
            text="▶ Show Output",
            cursor="pointinghand"
        )
        self.sorter_expand_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.sorter_expand_label.bind("<Button-1>", lambda e: self.toggle_output('sorter'))

        # Output container (initially hidden)
        self.sorter_output_container = ttk.Frame(output_frame, padding=5)
        self.sorter_output = scrolledtext.ScrolledText(self.sorter_output_container, height=12, wrap=tk.WORD)
        self.sorter_output.pack(fill='both', expand=True)

    def setup_searcher_tab(self):
        main_frame = ttk.Frame(self.searcher_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Search directory
        dir_frame = ttk.LabelFrame(main_frame, text="Search Directory", padding=10)
        dir_frame.pack(fill='x', pady=(0, 10))

        # Configure grid weights for responsive resizing
        dir_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="Search in:").grid(row=0, column=0, sticky='w')
        self.search_dir_var = tk.StringVar()
        search_entry = ttk.Entry(dir_frame, textvariable=self.search_dir_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=(10, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_search_dir).grid(row=0, column=2)

        # Filters
        filters_frame = ttk.LabelFrame(main_frame, text="Filters", padding=10)
        filters_frame.pack(fill='x', pady=(0, 10))

        # Configure grid weights for responsive resizing
        filters_frame.grid_columnconfigure(1, weight=1)

        # Year and Month
        ttk.Label(filters_frame, text="Year (e.g., 2022 or 2020-2023):").grid(row=0, column=0, sticky='w', pady=2)
        self.year_var = tk.StringVar()
        year_entry = ttk.Entry(filters_frame, textvariable=self.year_var, width=20)
        year_entry.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)

        ttk.Label(filters_frame, text="Month (e.g., 1 or 3-6):").grid(row=1, column=0, sticky='w', pady=2)
        self.month_var = tk.StringVar()
        month_entry = ttk.Entry(filters_frame, textvariable=self.month_var, width=20)
        month_entry.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)

        # Keywords
        ttk.Label(filters_frame, text="Keywords (space-separated):").grid(row=2, column=0, sticky='w', pady=2)
        self.keywords_var = tk.StringVar()
        keywords_entry = ttk.Entry(filters_frame, textvariable=self.keywords_var)
        keywords_entry.grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=2)

        ttk.Label(filters_frame, text="Keyword match:").grid(row=3, column=0, sticky='w', pady=2)
        self.keyword_match_var = tk.StringVar(value="any")
        keyword_frame = ttk.Frame(filters_frame)
        keyword_frame.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=2)
        ttk.Radiobutton(keyword_frame, text="Any", variable=self.keyword_match_var, value="any").pack(side='left')
        ttk.Radiobutton(keyword_frame, text="All", variable=self.keyword_match_var, value="all").pack(side='left', padx=(15, 0))

        # Rating filters
        rating_frame = ttk.LabelFrame(filters_frame, text="Rating Filters", padding=5)
        rating_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        # Configure rating frame for responsive layout
        rating_frame.grid_columnconfigure(0, weight=1)

        self.rating_type_var = tk.StringVar(value="none")
        ttk.Radiobutton(rating_frame, text="No rating filter", variable=self.rating_type_var, value="none").grid(row=0, column=0, sticky='w', pady=2)

        specific_frame = ttk.Frame(rating_frame)
        specific_frame.grid(row=1, column=0, sticky='ew', pady=2)
        ttk.Radiobutton(specific_frame, text="Specific rating/range:", variable=self.rating_type_var, value="specific").pack(side='left')
        self.rating_var = tk.StringVar()
        ttk.Entry(specific_frame, textvariable=self.rating_var, width=15).pack(side='left', padx=(10, 0))

        ttk.Radiobutton(rating_frame, text="Rejected files (-1)", variable=self.rating_type_var, value="rejected").grid(row=2, column=0, sticky='w', pady=2)
        ttk.Radiobutton(rating_frame, text="Picked files (0-5)", variable=self.rating_type_var, value="picked").grid(row=3, column=0, sticky='w', pady=2)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))

        # Configure options frame for responsive layout
        options_frame.grid_columnconfigure(0, weight=1)

        self.open_dirs_var = tk.BooleanVar(value=True)  # Default to checked
        ttk.Checkbutton(options_frame, text="Open directories containing matched files", variable=self.open_dirs_var).grid(row=0, column=0, sticky='w')

        # Status text above button
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=(10, 5))

        self.searcher_status_text = tk.StringVar()
        self.searcher_status_display = ttk.Label(
            status_frame,
            textvariable=self.searcher_status_text,
            anchor='center'
        )
        self.searcher_status_display.pack(fill='x')

        # Status will be set after initial check in __init__
        self.searcher_status_text.set("Checking ExifTool...")
        self.searcher_status_display.config(foreground="gray")

        # Run button - centered
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))

        self.searcher_run_button = ttk.Button(button_frame, text="Run Media Searcher", command=self.run_searcher)
        self.searcher_run_button.pack()

        # Output with expandable functionality
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill='both', expand=True)

        # Configure output frame for proper resizing
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Expandable text header
        self.searcher_expanded = tk.BooleanVar(value=False)
        self.searcher_expand_label = ttk.Label(
            output_frame,
            text="▶ Show Output",
            cursor="pointinghand"
        )
        self.searcher_expand_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.searcher_expand_label.bind("<Button-1>", lambda e: self.toggle_output('searcher'))

        # Output container (initially hidden)
        self.searcher_output_container = ttk.Frame(output_frame, padding=5)
        self.searcher_output = scrolledtext.ScrolledText(self.searcher_output_container, height=10, wrap=tk.WORD)
        self.searcher_output.pack(fill='both', expand=True)

    def toggle_output(self, tab):
        """Toggle the expanded/collapsed state of output section."""
        if tab == 'sorter':
            expanded = self.sorter_expanded.get()
            if expanded:
                # Collapse
                self.sorter_output_container.grid_forget()
                self.sorter_expand_label.config(text="▶ Show Output")
                self.sorter_expanded.set(False)
            else:
                # Expand
                self.sorter_output_container.grid(row=1, column=0, sticky='nsew')
                self.sorter_expand_label.config(text="▼ Hide Output")
                self.sorter_expanded.set(True)
        elif tab == 'searcher':
            expanded = self.searcher_expanded.get()
            if expanded:
                # Collapse
                self.searcher_output_container.grid_forget()
                self.searcher_expand_label.config(text="▶ Show Output")
                self.searcher_expanded.set(False)
            else:
                # Expand
                self.searcher_output_container.grid(row=1, column=0, sticky='nsew')
                self.searcher_expand_label.config(text="▼ Hide Output")
                self.searcher_expanded.set(True)

    def browse_source(self):
        initial_dir = get_pictures_directory()
        directory = filedialog.askdirectory(
            title="Select Source Directory",
            initialdir=initial_dir
        )
        if directory:
            self.source_var.set(directory)

    def browse_dest(self):
        initial_dir = get_pictures_directory()
        directory = filedialog.askdirectory(
            title="Select Destination Directory",
            initialdir=initial_dir
        )
        if directory:
            self.dest_var.set(directory)

    def browse_search_dir(self):
        initial_dir = get_pictures_directory()
        directory = filedialog.askdirectory(
            title="Select Search Directory",
            initialdir=initial_dir
        )
        if directory:
            self.search_dir_var.set(directory)

    def on_closing(self):
        """Handle window close event with process running check."""
        if self.process_running:
            # Create a custom dialog with clearer options
            dialog = tk.Toplevel(self.root)
            dialog.title("Process Running")
            dialog.geometry("400x200")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")

            # Warning message
            message_frame = ttk.Frame(dialog, padding=20)
            message_frame.pack(fill='both', expand=True)

            warning_label = ttk.Label(
                message_frame,
                text="⚠️ A process is currently running!",
                font=('TkDefaultFont', 12, 'bold')
            )
            warning_label.pack(pady=(0, 10))

            text_label = ttk.Label(
                message_frame,
                text="If you close the window now, the operation may be\ninterrupted and data could be lost.\n\nWhat would you like to do?",
                justify='center'
            )
            text_label.pack(pady=(0, 20))

            # Button frame
            button_frame = ttk.Frame(message_frame)
            button_frame.pack()

            def force_close():
                if self.current_process:
                    try:
                        self.current_process.terminate()
                    except:
                        pass
                dialog.destroy()
                self.root.destroy()

            def cancel_close():
                dialog.destroy()

            # Buttons - centered
            ttk.Button(button_frame, text="Force Close", command=force_close).pack(side='left', padx=(0, 10))
            ttk.Button(button_frame, text="Cancel", command=cancel_close).pack(side='left')

        else:
            # No process running, close normally
            self.root.destroy()

    def run_command_in_thread(self, command, output_widget, status_text_var, status_display_widget, run_button):
        def run():
            try:
                # Set process running state
                self.process_running = True

                # Disable the run button and set status to gray
                run_button.config(state='disabled')
                status_display_widget.config(foreground='gray')

                output_widget.delete(1.0, tk.END)
                output_widget.insert(tk.END, f"Running: {' '.join(command)}\n\n")
                output_widget.update()

                # Update status to show command is starting
                status_text_var.set(f"Starting: {' '.join(command)}")

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )

                # Store current process for potential termination
                self.current_process = process

                for line in process.stdout:
                    output_widget.insert(tk.END, line)
                    output_widget.see(tk.END)
                    output_widget.update()

                    # Update status text with the last non-empty line (keep gray)
                    stripped = line.strip()
                    if stripped:
                        # Truncate very long lines for status display
                        if len(stripped) > 80:
                            stripped = stripped[:77] + "..."
                        status_text_var.set(stripped)

                process.wait()

                # Clear process running state
                self.process_running = False
                self.current_process = None

                # Re-enable button
                run_button.config(state='normal')

                if process.returncode == 0:
                    completion_msg = "✓ Command completed successfully!"
                    output_widget.insert(tk.END, f"\n{completion_msg}")
                    status_text_var.set(completion_msg)
                    # Set status to green for success
                    status_display_widget.config(foreground='green')
                else:
                    error_msg = f"✗ Command failed with return code {process.returncode}"
                    output_widget.insert(tk.END, f"\n{error_msg}")
                    status_text_var.set(error_msg)
                    # Set status to red for errors
                    status_display_widget.config(foreground='red')

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                output_widget.insert(tk.END, f"\n{error_msg}")
                status_text_var.set(error_msg)
                # Set status to red for errors
                status_display_widget.config(foreground='red')
                # Clear process running state on error
                self.process_running = False
                self.current_process = None
                run_button.config(state='normal')

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def run_sorter(self):
        if not self.source_var.get() or not self.dest_var.get():
            messagebox.showerror("Error", "Please select both source and destination directories")
            return

        # Check if using move mode (not copy and not dry run) and confirm
        is_move_mode = not self.copy_var.get() and not self.dry_run_var.get()
        if is_move_mode:
            # Show warning dialog for move operations
            response = messagebox.askokcancel(
                "⚠️ WARNING: MOVE MODE",
                get_move_warning_message() + "\n\nAre you sure you want to continue?",
                icon='warning',
                default='cancel'
            )
            if not response:
                # User cancelled the operation
                return

        # Get the path to media_sorter.py (same directory as this file)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sorter_path = os.path.join(script_dir, "media_sorter.py")
        command = [sys.executable, sorter_path, self.source_var.get(), self.dest_var.get()]

        if self.copy_var.get():
            command.append("--copy")
        if self.dry_run_var.get():
            command.append("--dry-run")
        if self.fallback_var.get() != "none":
            command.extend(["--fallback-to-file-time", self.fallback_var.get()])

        # If user confirmed move operation via GUI, pass --yes flag to skip CLI prompt
        if is_move_mode:
            command.append("--yes")

        self.run_command_in_thread(command, self.sorter_output, self.sorter_status_text, self.sorter_status_display, self.sorter_run_button)

    def run_searcher(self):
        if not self.search_dir_var.get():
            messagebox.showerror("Error", "Please select a search directory")
            return

        # Get the path to media_searcher.py (same directory as this file)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        searcher_path = os.path.join(script_dir, "media_searcher.py")
        command = [sys.executable, searcher_path, self.search_dir_var.get()]

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

        self.run_command_in_thread(command, self.searcher_output, self.searcher_status_text, self.searcher_status_display, self.searcher_run_button)

def main():
    # Check if exiftool is installed before launching the GUI
    if not is_exiftool_installed():
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        result = messagebox.askyesno(
            "ExifTool Not Found",
            "ExifTool is not installed or not in your system's PATH.\n\n"
            "ExifTool is required for both Media Sorter and Media Searcher to work properly.\n"
            "You can download it from: https://exiftool.org/\n\n"
            "Do you want to continue anyway?\n"
            "(The scripts will fail when you try to run them)",
            icon="warning"
        )

        if not result:
            root.destroy()
            return

        root.deiconify()  # Show the main window
    else:
        root = tk.Tk()

    MediaOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()