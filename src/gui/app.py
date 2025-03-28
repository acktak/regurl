import tkinter as tk
import queue
from tkinter import ttk, filedialog
import csv
import threading
from src.core.scraper import Scraper
import darkdetect
import math

class AnimatedLoader:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=60, height=60, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.arc = self.canvas.create_arc(10, 10, 50, 50, start=0, extent=270, outline="royalblue", width=5, style=tk.ARC)
        self.angle = 0
        self.animating = False

    def start(self):
        self.animating = True
        self.animate()

    def stop(self):
        self.animating = False

    def animate(self):
        if self.animating:
            self.angle = (self.angle + 15) % 360
            self.canvas.itemconfig(self.arc, start=self.angle)
            self.canvas.after(50, self.animate)

class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper Regex")
        self.root.geometry("600x450")

        # 📌 Détection du mode système au lancement
        #self.dark_mode = darkdetect.isDark()

        # Entrée URL
        self.url_entry = tk.Entry(root, width=50, font=("Arial", 10))
        # self.url_entry.insert(0, "Enter an URL...")
        self.create_placeholder(self.url_entry, "Enter an URL...")
        self.url_entry.pack(pady=5)

        # Entrée Regex
        self.regex_entry = tk.Entry(root, width=50, font=("Arial", 10))
        self.create_placeholder(self.regex_entry, "Enter a regex...")
        self.regex_entry.pack(pady=5)

        # Mode récursif 
        self.recursive_mode = tk.BooleanVar()
        tk.Checkbutton(root, text="Recursive search", variable=self.recursive_mode).pack(pady=5)
        
        # Liste déroulante pour sélectionner une regex par défaut
        self.regex_options = {"Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                              "Téléphone": r"\+?[0-9]{1,4}?[-.\s]?\(?[0-9]{1,3}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}",
                              "Date": r"\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}\b"}
        
        self.regex_var = tk.StringVar()
        self.regex_dropdown = ttk.Combobox(root, textvariable=self.regex_var, values=list(self.regex_options.keys()),width=22)
        self.regex_dropdown.set("Select a predefined regex")
        self.regex_dropdown.pack(pady=25)
        self.regex_dropdown.bind("<<ComboboxSelected>>", self.set_regex)

        # Boutons
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

        #loader
        self.loader = AnimatedLoader(root)
        style = ttk.Style()
        style.configure("Treeview", background="#ccffcc", fieldbackground="#ccffcc")  # Vert clair
        # Tableau de résultats avec fond vert clair
        self.results_list = ttk.Treeview(root, columns=("url", "regex", "match"), show="headings", height=8, style="Treeview")
        self.results_list.heading("url", text="URL")
        self.results_list.heading("regex", text="Regex Pattern")
        self.results_list.heading("match", text="Matched Regex")
        self.results_list.pack(expand=True, fill="both", pady=10)

        # File d'attente pour récupérer les résultats du Scraper
        self.result_queue = queue.Queue()
        self.stop_event = threading.Event()  # Flag pour arrêter la recherche

    def set_regex(self, event):
        """ Met à jour le champ regex avec la regex sélectionnée """
        selected_regex = self.regex_var.get()
        if selected_regex in self.regex_options:
            self.regex_entry.delete(0, tk.END)
            self.regex_entry.insert(0, self.regex_options[selected_regex])

    def start_search(self):
        """Lance le scraping dans un thread séparé"""

        self.stop_search()
        self.clear_results()
        self.error_label.config(text="")

        base_url = self.url_entry.get()
        regex = self.regex_entry.get()
        recursive = self.recursive_mode.get()

        # loader
        self.loader.start()
        self.stop_button.config(state=tk.NORMAL)

        # Réinitialiser l'event STOP
        self.stop_event.clear()

        # Lancer le scraper dans un thread
        self.scraper = Scraper(base_url, regex, recursive, self.result_queue, self.stop_event)
        self.scraper_thread = threading.Thread(target=self.scraper.search_regex)
        self.scraper_thread.start()

        # Vérifier la queue régulièrement pour afficher les résultats
        self.check_queue()

    def export_to_csv(self):
        """ Exporte les résultats dans un fichier CSV """
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
        """Demande l'arrêt du scraper"""
        self.stop_event.set()  # Signale au scraper de s'arrêter
        self.stop_button.config(state=tk.DISABLED)  # Désactiver le bouton Stop

    def animate_loader(self):
        """Fait tourner le cercle du loader"""
        if self.animating:
            self.animation_angle = (self.animation_angle + 10) % 360
            self.canvas.itemconfig(self.arc, start=self.animation_angle)
            self.root.after(50, self.animate_loader)  # Rafraîchit toutes les 50ms

    def check_queue(self):
        """Vérifie la queue et met à jour l'interface avec les nouveaux résultats"""
        try:
            while not self.result_queue.empty():
                result = self.result_queue.get_nowait()
                if 'error' in result:
                    # Afficher l'erreur dans le label d'erreur
                    self.error_label.config(text=result['error'], fg="red")
                else:
                    self.results_list.insert("", "end", values=(result['url'], result['regex'], result['match']))
        except queue.Empty:
            pass

        # Vérifier si le thread est toujours en cours
        if self.scraper_thread.is_alive():
            self.root.after(500, self.check_queue)
        else:
            self.loader.stop()  # Arrêter le loader quand la recherche est finie
            self.stop_button.config(state=tk.DISABLED)
            
    def clear_results(self):
        """Vide le tableau des résultats"""
        for item in self.results_list.get_children():
            self.results_list.delete(item)

    def on_entry_focus_in(self, event):
        """ Supprime le texte du champ lorsqu'on clique dessus """
        if event.widget.get() == event.widget.placeholder_text:
            event.widget.delete(0, tk.END)
            event.widget.config(fg="black")  # Change la couleur du texte en noir

    def on_entry_focus_out(self, event):
        """ Remet le placeholder si le champ est vide """
        if not event.widget.get():
            event.widget.insert(0, event.widget.placeholder_text)
            event.widget.config(fg="gray")  # Change la couleur du texte en gris

    def create_placeholder(self, entry, placeholder):
        """ Ajoute un placeholder à un champ Entry """
        entry.placeholder_text = placeholder
        entry.insert(0, placeholder)
        entry.config(fg="gray")  # Texte en gris

        entry.bind("<FocusIn>", self.on_entry_focus_in)
        entry.bind("<FocusOut>", self.on_entry_focus_out)