import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from src.core.scraper import Scraper
from src.core.regex_utils import RegexUtils

class TkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper")
        self.create_widgets()
        self.results = []

    def create_widgets(self):
        # URL Entry
        tk.Label(self.root, text="URL:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5)

        # Regex Entry
        tk.Label(self.root, text="Regex (Optional):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.regex_entry = tk.Entry(self.root, width=50)
        self.regex_entry.grid(row=1, column=1, padx=10, pady=5)

        # Predefined Regex Dropdown
        tk.Label(self.root, text="Or choose predefined regex:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.regex_var = tk.StringVar(value="")
        self.regex_dropdown = ttk.Combobox(self.root, textvariable=self.regex_var, values=list(RegexUtils.PREDEFINED_PATTERNS.keys()))
        self.regex_dropdown.grid(row=2, column=1, padx=10, pady=5)

        # Analyze Button
        self.analyze_button = tk.Button(self.root, text="Analyze", command=self.analyze)
        self.analyze_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Results Table
        self.results_tree = ttk.Treeview(self.root, columns=("Result"), show="headings", height=10)
        self.results_tree.heading("Result", text="Results")
        self.results_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Export Button
        self.export_button = tk.Button(self.root, text="Export to CSV", command=self.export_csv)
        self.export_button.grid(row=5, column=0, columnspan=2, pady=10)

    def analyze(self):
        url = self.url_entry.get()
        regex = self.regex_entry.get() or RegexUtils.get_pattern(self.regex_var.get())
        if not url:
            messagebox.showerror("Error", "URL is required")
            return

        scraper = Scraper(url)
        self.results = scraper.scrape(url, regex)

        for result in self.results:
            self.results_tree.insert("", "end", values=(result,))

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results to export")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Results"])
                for result in self.results:
                    writer.writerow([result])
            messagebox.showinfo("Success", "Results exported successfully!")
