import tkinter as tk
from tkinter import ttk
import queue
import threading
from src.core.scraper import Scraper
import darkdetect

class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper Regex")
        self.root.geometry("600x450")

        # 📌 Détection du mode système au lancement
        self.dark_mode = darkdetect.isDark()

        # Entrée URL
        self.url_entry = tk.Entry(root, width=50)
        # self.url_entry.insert(0, "Enter an URL...")
        self.create_placeholder(self.url_entry, "Enter an URL...")
        self.url_entry.pack(pady=5)

        # Entrée Regex
        self.regex_entry = tk.Entry(root, width=50)
        self.create_placeholder(self.regex_entry, "Enter a regex...")
        self.regex_entry.pack(pady=5)

        # Mode récursif et regex par défaut
        self.recursive_mode = tk.BooleanVar()
        self.default_regex = tk.BooleanVar()

        tk.Checkbutton(root, text="Recursive search", variable=self.recursive_mode).pack()
        tk.Checkbutton(root, text="Use default regex", variable=self.default_regex).pack()

        # Boutons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.search_button = tk.Button(button_frame, text="Search", command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_search, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Label pour afficher les erreurs
        self.error_label = tk.Label(self.root, text="")
        self.error_label.pack(pady=10)

        # Loader animé (Cercle qui tourne)
        self.canvas = tk.Canvas(root, width=50, height=50, highlightthickness=0)
        self.canvas.pack(pady=5)
        self.arc = self.canvas.create_arc(10, 10, 40, 40, start=0, extent=90, outline="blue", width=5)
        self.animation_angle = 0
        self.animating = False

        # Tableau de résultats
        self.results_list = ttk.Treeview(root, columns=("url", "regex", "match"), show="headings")
        self.results_list.heading("url", text="URL")
        self.results_list.heading("regex", text="Regex Pattern")
        self.results_list.heading("match", text="Matched Regex")
        self.results_list.pack(expand=True, fill="both", pady=10)

        # File d'attente pour récupérer les résultats du Scraper
        self.result_queue = queue.Queue()
        self.stop_event = threading.Event()  # Flag pour arrêter la recherche

    def start_search(self):
        """Lance le scraping dans un thread séparé"""

        self.stop_search()
        self.clear_results()
        self.error_label.config(text="")

        base_url = self.url_entry.get()
        regex = self.regex_entry.get()
        recursive = self.recursive_mode.get()
        default_regex = self.default_regex.get()

        # Activer le loader et le bouton STOP
        self.animating = True
        self.animate_loader()
        self.stop_button.config(state=tk.NORMAL)

        # Réinitialiser l'event STOP
        self.stop_event.clear()

        # Lancer le scraper dans un thread
        self.scraper = Scraper(base_url, regex, recursive, default_regex, self.result_queue, self.stop_event)
        self.scraper_thread = threading.Thread(target=self.scraper.search_regex)
        self.scraper_thread.start()

        # Vérifier la queue régulièrement pour afficher les résultats
        self.check_queue()

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
            self.animating = False  # Arrêter l'animation une fois terminé
            self.stop_button.config(state=tk.DISABLED) # On desactive le bouton stop

    def clear_results(self):
        """Vide le tableau des résultats"""
        for item in self.results_list.get_children():
            self.results_list.delete(item)

    def on_entry_focus_in(self, event):
        """ Supprime le texte du champ lorsqu'on clique dessus """
        if event.widget.get() == event.widget.placeholder_text:
            event.widget.delete(0, tk.END)
            event.widget.config(fg="white")  # Change la couleur du texte en noir

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



""""

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
"""