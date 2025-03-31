import tkinter as tk
import queue
from tkinter import ttk, filedialog
import csv
import threading
from src.core.scraper import Scraper
from src.core.utils import RegexUtils

class AnimatedLoader:
    """
    Classe pour gérer un loader animé en forme de cercle.
    """
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=60, height=60, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.arc = self.canvas.create_arc(10, 10, 50, 50, start=0, extent=270, outline="royalblue", width=5, style=tk.ARC)
        self.angle = 0
        self.animating = False

    def start(self):
        """Démarre l'animation du loader."""
        self.animating = True
        self.animate()

    def stop(self):
        """Arrête l'animation du loader."""
        self.animating = False

    def animate(self):
        """Met à jour l'angle du loader pour créer l'animation."""
        if self.animating:
            self.angle = (self.angle + 15) % 360
            self.canvas.itemconfig(self.arc, start=self.angle)
            self.canvas.after(50, self.animate)

class WebScraperApp:
    """
    Application GUI pour effectuer du web scraping avec des expressions régulières.
    """
    def __init__(self, root):
        """
        Initialise l'interface utilisateur et les composants de l'application.

        Args:
            root (tk.Tk): Fenêtre principale de l'application.
        """
        self.root = root
        self.root.title("Regurl")
        self.root.geometry("1500x1200")

        # Champ d'entrée pour l'URL
        self.url_entry = tk.Entry(root, width=50, font=("Arial", 10))
        self.create_placeholder(self.url_entry, "Enter an URL...")
        self.url_entry.pack(pady=5)

        # Champ d'entrée pour la regex
        self.regex_entry = tk.Entry(root, width=50, font=("Arial", 10))
        self.create_placeholder(self.regex_entry, "Enter a regex...")
        self.regex_entry.pack(pady=5)

        # Mode récursif
        self.recursive_mode = tk.BooleanVar()
        tk.Checkbutton(root, text="On all website", variable=self.recursive_mode).pack(pady=5)

        # Options de regex prédéfinies
        options_frame = tk.Frame(root)
        options_frame.pack(pady=5)

        master_var = tk.BooleanVar()
        master_chk = tk.Checkbutton(options_frame, text="Default REGEX", variable=master_var)
        master_chk.pack(anchor="w", pady=(5, 0))

        frame_options = tk.Frame(options_frame)
        frame_options.pack(anchor="w", pady=(0, 5))
        frame_options.pack_forget()  # Caché par défaut

        self.valeurs_associees = list(RegexUtils().get_all_keys())
        self.vars_checkboxes = {}

        # Création dynamique des cases à cocher
        for cle in self.valeurs_associees:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(frame_options, text=cle, variable=var)
            chk.pack(anchor="w")
            self.vars_checkboxes[cle] = var

        # Fonction pour afficher/masquer les options
        def toggle_options():
            if master_var.get():
                frame_options.pack(anchor="w", pady=(0, 5))
                for var in self.vars_checkboxes.values():
                    var.set(True)
            else:
                frame_options.pack_forget()
                for var in self.vars_checkboxes.values():
                    var.set(False)

        master_var.trace_add("write", lambda *_: toggle_options())

        # Boutons principaux
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.search_button = tk.Button(button_frame, text="Search", command=self.start_search)
        self.search_button.grid(row=0, column=0, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_results)
        self.clear_button.grid(row=0, column=1, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_search, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)

        self.export_button = tk.Button(button_frame, text="Export CSV", command=self.export_to_csv)
        self.export_button.grid(row=0, column=3, padx=5)

        # Label pour afficher les erreurs
        self.error_label = tk.Label(self.root, text="", foreground="red")
        self.error_label.pack(pady=10)

        # Loader animé
        self.loader = AnimatedLoader(root)

        # Style pour le tableau des résultats
        style = ttk.Style()
        style.configure("Treeview", rowheight=40, background="#ccffcc", fieldbackground="#ccffcc")

        # Tableau des résultats
        self.results_list = ttk.Treeview(root, columns=("url", "regex", "match"), show="headings", height=8, style="Treeview")
        self.results_list.heading("url", text="URL")
        self.results_list.heading("regex", text="Regex Pattern")
        self.results_list.heading("match", text="Matched Regex")
        self.results_list.pack(expand=True, fill="both", pady=10)

        # File d'attente pour les résultats
        self.result_queue = queue.Queue()
        self.stop_event = threading.Event()

    def start_search(self):
        """
        Démarre le scraping dans un thread séparé.
        """
        self.stop_search()
        self.clear_results()
        self.error_label.config(text="")

        base_url = self.url_entry.get()
        regex = self.regex_entry.get()
        recursive = self.recursive_mode.get()

        if not self.loader.animating:
            self.loader.start()

        self.stop_button.config(state=tk.NORMAL)
        self.stop_event.clear()

        selections = [
            RegexUtils().PREDEFINED_PATTERNS[cle] for cle, var in self.vars_checkboxes.items() if var.get()
        ]
        self.scraper = Scraper(base_url, regex, recursive, self.result_queue, self.stop_event, selections)

        self.scraper_thread = threading.Thread(target=self.scraper.search_regex)
        self.scraper_thread.start()

        self.check_queue()

    def export_to_csv(self):
        """
        Exporte les résultats dans un fichier CSV.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
        filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
        if not file_path:
            return
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Regex Pattern", "Matched Regex"])
            for item in self.results_list.get_children():
                writer.writerow(self.results_list.item(item)['values'])

    def stop_search(self):
        """
        Demande l'arrêt du scraper.
        """
        self.stop_button.config(state=tk.DISABLED)
        self.stop_event.set()
        if hasattr(self, "scraper_thread") and self.scraper_thread.is_alive():
            self.scraper_thread.join()

    def check_queue(self):
        """
        Vérifie la file d'attente pour afficher les résultats et gère la fin du scraping.
        """
        try:
            while not self.result_queue.empty():
                result = self.result_queue.get_nowait()
                if 'error' in result:
                    self.error_label.config(text=result['error'], fg="red")
                else:
                    self.results_list.insert("", "end", values=(result['url'], result['regex'], result['match']))
        except queue.Empty:
            pass

        if self.scraper_thread.is_alive():
            self.root.after(500, self.check_queue)
        else:
            self.loader.stop()
            self.stop_button.config(state=tk.DISABLED)

    def clear_results(self):
        """
        Vide le tableau des résultats.
        """
        for item in self.results_list.get_children():
            self.results_list.delete(item)

    def on_entry_focus_in(self, event):
        """
        Supprime le texte du champ lorsqu'on clique dessus.
        """
        if event.widget.get() == event.widget.placeholder_text:
            event.widget.delete(0, tk.END)
            event.widget.config(fg="black")

    def on_entry_focus_out(self, event):
        """
        Remet le placeholder si le champ est vide.
        """
        if not event.widget.get():
            event.widget.insert(0, event.widget.placeholder_text)
            event.widget.config(fg="gray")

    def create_placeholder(self, entry, placeholder):
        """
        Ajoute un placeholder à un champ Entry.

        Args:
            entry (tk.Entry): Champ d'entrée.
            placeholder (str): Texte du placeholder.
        """
        entry.placeholder_text = placeholder
        entry.insert(0, placeholder)
        entry.config(fg="gray")

        entry.bind("<FocusIn>", self.on_entry_focus_in)
        entry.bind("<FocusOut>", self.on_entry_focus_out)