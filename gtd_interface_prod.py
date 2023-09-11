import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import filedialog
import json
import os
from datetime import datetime, date
from enum import Enum
import shutil
import webbrowser
import re
import uuid  # 1. Importer la bibliothèque uuid



class PriorityLevel(Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    URGENT = 'Urgent'

class GTDManager:
    def __init__(self, filename='tasks.json'):
        self.filename = filename
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.tasks = json.load(f)
        else:
            self.initialize_empty_tasks()

    def initialize_empty_tasks(self):
        self.tasks = {'inbox': [], 'next_actions': [], 'projects': [], 'waiting': [], 'someday': [], 'completed': []}

    def save_tasks(self):
        with open(self.filename, 'w') as f:
            json.dump(self.tasks, f)

    def add_task(self, task_details, category='inbox'):
        task_details['id'] = str(uuid.uuid4())  # 2. Ajouter un champ 'id' contenant un UUID généré
        self.tasks[category].append(task_details)
        self.save_tasks()

    def move_task(self, old_category, new_category, task_details):
        print(f"Trying to move task from {old_category} to {new_category} with details {task_details}")  # Debugging line

        # Trouver l'index de la tâche correspondante dans la liste de tâches de l'ancienne catégorie
        task_index = None
        for i, task in enumerate(self.tasks[old_category]):
            if all(task.get(k) == v for k, v in task_details.items()):
                task_index = i
                break

        # Si la tâche est trouvée, la déplacer à la nouvelle catégorie
        if task_index is not None:
            task_to_move = self.tasks[old_category].pop(task_index)
            self.tasks[new_category].append(task_to_move)
            self.save_tasks()
            print(f"Successfully moved task.")  # Debugging line
        else:
            print(f"Task not found in {old_category}.")  # Debugging line


# Création de l'instance du gestionnaire GTD
manager = GTDManager()

# Configuration de la fenêtre principale
#root = tk.Tk()
#root.title("Getting Things Done App 2")

# Création du cadre principal
#frame = tk.Frame(root)
#frame.pack(padx=20, pady=10)

# Fonction pour ajouter une tâche
def add_task():
    
    global attached_files

    task_name = task_name_entry.get()
    category = category_var.get()
    due_date = due_date_calendar.get_date()
    priority = priority_var.get()
    description = description_text.get("1.0", tk.END).strip()
    assigned_to = assigned_to_var.get()
    #attached_files = attached_file_var.get()
    
    print(f"Valeur de attached_files: {attached_files}")



    if not all([task_name, category, str(due_date), priority, assigned_to]):
        tk.messagebox.showinfo("Incomplete Information", "All fields must be filled in.")
        return

    try:
        base_directory = os.path.abspath("new_directory_path")  # Votre répertoire existant
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
            print("Création du dossier de base.")

        subdirectory_path, timestamp_str = create_timestamped_subdirectory(base_directory)

        print(f"Valeur de attached_files: {attached_files}")  # Debug

        for file_path in attached_files:
            if not os.path.exists(file_path):
                print(f"Le fichier source {file_path} n'existe pas.")
                continue

            try:
                print(f"Copie de {file_path} à {subdirectory_path}")  # Utilisez subdirectory_path ici
                shutil.copy(file_path, subdirectory_path)  # Utilisez subdirectory_path ici
            except Exception as e:
                print(f"Une erreur s'est produite lors de la copie du fichier: {e}")


        task_details = {
            'name': task_name,
            'due_date': str(due_date),
            'priority': priority,
            'description': description,
            'assigned_to': assigned_to,
            #'attached_file': attached_files,  # Correction ici
            'storage_reference': timestamp_str,  # Ajout de l'horodatage comme référence de stockage
            'created_date': str(datetime.now())
        }

        manager.add_task(task_details, category)
        update_treeview(category)
        
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

    # Vider les champs de saisie
    task_name_entry.delete(0, tk.END)
    description_text.delete("1.0", tk.END)
    category_var.set('inbox')
    due_date_calendar.set_date(date.today())
    priority_var.set('Low')
    assigned_to_var.set('Unassigned')


def list_files_in_directory(directory_path):
    try:
        # Liste tous les fichiers du répertoire
        filenames = os.listdir(directory_path)
        
        # Vous pouvez également filtrer la liste pour inclure uniquement les fichiers et exclure les sous-répertoires
        filenames = [f for f in filenames if os.path.isfile(os.path.join(directory_path, f))]
        
        return filenames
    except Exception as e:
        print(f"Une erreur est survenue lors de la liste des fichiers : {e}")
        return []

# Fonction pour créer un sous-répertoire avec un nom basé sur un horodatage
def create_timestamped_subdirectory(base_directory):
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")  # Convertir en chaîne, format "AAAAMMJJ_HHMMSS"
    subdirectory_name = f"task_{timestamp_str}"
    subdirectory_path = os.path.join(base_directory, subdirectory_name)
    
    if not os.path.exists(subdirectory_path):
        os.makedirs(subdirectory_path)
    
    return subdirectory_path, timestamp_str  # Retourner le chemin et l'horodatage


def choose_file():
    global attached_files
    file_paths = filedialog.askopenfilenames(multiple=True)
    attached_files = file_paths
    print(f"Chemin de fichiers sélectionnés : {attached_files}")  # Debug
    update_attached_files_label(file_paths)


def update_attached_files_label(file_paths):
    
    global attached_files  # Seulement si vous avez l'intention de modifier 'attached_files'

    file_names = [os.path.basename(path) for path in file_paths]
    attached_files_display.config(text="; ".join(file_names))



# Fonction pour mettre à jour l'affichage des tâches
def update_treeview(category):
    global current_tree, current_category_var
    current_tree = treeviews[category]
    current_category_var.set(category)
    for row in current_tree.get_children():
        current_tree.delete(row)
    tasks = manager.tasks[category]
    for task in tasks:
        current_tree.insert("", tk.END, values=(task['name'], task['created_date'], task.get('due_date', 'N/A'), task.get('priority', 'N/A'), task.get('description', 'N/A')))

# Fonction pour déplacer une tâche sélectionnée
def move_selected_task():
    try:
        # Récupérer le frame actuellement sélectionné dans le notebook
        selected_frame = notebook.nametowidget(notebook.select())
        
        # Trouver à quel Treeview ce frame correspond
        selected_tree = [tree for name, tree in treeviews.items() if selected_frame.winfo_children()[0] == tree][0]
        
        print(f"Selected tree: {selected_tree}")  # Debugging line

        # Trouver la catégorie correspondante
        selected_category = [category for category, tree in treeviews.items() if tree == selected_tree][0]
        
        print(f"Selected category: {selected_category}")  # Debugging line

        # Récupérer l'élément sélectionné dans le Treeview
        selected_item = selected_tree.selection()
        
        print(f"Selected item: {selected_item}")  # Debugging line

        # Vérifier si un élément est effectivement sélectionné
        if not selected_item:
            messagebox.showwarning("Warning", "No task selected.")
            return

        # Récupérer les détails de la tâche
        selected_task = selected_tree.item(selected_item[0], 'values')
        task_details = {'name': selected_task[0], 'created_date': selected_task[1], 'due_date': selected_task[2], 'priority': selected_task[3]}
        
        print(f"Task details: {task_details}")  # Debugging line

        # Obtenir la nouvelle catégorie dans laquelle déplacer la tâche
        new_category = move_category_var.get()
        
        print(f"New category: {new_category}")  # Debugging line

        # Déplacer la tâche
        manager.move_task(selected_category, new_category, task_details)
        
        # Mettre à jour les Treeviews
        update_treeview(selected_category)
        update_treeview(new_category)

    except Exception as e:
        print(f"An exception occurred: {e}")  # Debugging line
        messagebox.showerror("Error", f"An error occurred: {e}")

#Fonction pour ouvrir une URL dans le navigateur
def open_url(event, url):
    webbrowser.open(url)

# Fonction pour convertir les index absolu en index ligne/colonne pour Tkinter
def calculate_line_column_index(text, start, end):
    lines = text.split('\n')
    char_count = 0
    for line_number, line in enumerate(lines):
        if char_count + len(line) + 1 > start:  # +1 pour le '\n' à la fin de chaque ligne
            start_column = start - char_count
            end_column = end - char_count
            return f"{line_number + 1}.{start_column}", f"{line_number + 1}.{end_column}"
        char_count += len(line) + 1  # +1 pour le '\n' à la fin de chaque ligne
    return None

# Fonction pour rendre les URLs cliquables
def make_url_clickable(text_widget, url, start_idx, end_idx, tag_name):
    text_widget.tag_add(tag_name, start_idx, end_idx)
    text_widget.tag_configure(tag_name, foreground="blue", underline=1)
    text_widget.tag_bind(tag_name, "<Button-1>", lambda e, url=url: open_url(e, url))
    text_widget.tag_bind(tag_name, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
    text_widget.tag_bind(tag_name, "<Leave>", lambda e: text_widget.config(cursor=""))


def save_changes(task, desc_text):
    updated_description = desc_text.get("1.0", tk.END).strip()
    task['description'] = updated_description
    print("Description mise à jour dans le dictionnaire de tâches.")  # Debug

    try:
        with open('tasks.json', 'w') as f:
            json.dump(manager.tasks, f)
        print("Sauvegarde réussie dans tasks.json.")  # Debug
    except Exception as e:
        print(f"Échec de la sauvegarde dans tasks.json: {e}")  # Debug

def show_task_details(event):
    current_tree = event.widget
    selected_item = current_tree.selection()
    
    if not selected_item:
        return
    selected_item = selected_item[0]
    task_values = current_tree.item(selected_item, 'values')
    task_name, created_date, *_ = task_values

    for category, tasks in manager.tasks.items():
        for task in tasks:
            if task['name'] == task_name and task['created_date'] == created_date:
                details_window = tk.Toplevel()
                details_window.title("Task Details")
                
                title_label = tk.Label(details_window, text=f"Title: {task['name']}")
                title_label.pack()

                due_date_label = tk.Label(details_window, text=f"Due Date: {task.get('due_date', 'N/A')}")
                due_date_label.pack()

                assigned_to_label = tk.Label(details_window, text=f"Assigned to: {task.get('assigned_to', 'N/A')}")
                assigned_to_label.pack()

                desc_text = tk.Text(details_window, wrap=tk.WORD)
                desc_text.pack()
                desc_text.insert(tk.END, task.get('description', ''))

                save_button = tk.Button(details_window, text="Save", command=lambda: save_changes(task, desc_text))
                save_button.pack()

                storage_reference = task.get('storage_reference', '')
                if storage_reference:
                    folder_path = os.path.join(os.path.abspath("new_directory_path"), f"task_{storage_reference}")  # Remplacez "new_directory_path" par le chemin vers votre répertoire de base
                    open_folder_button = tk.Button(details_window, text="Ouvrir le dossier des pièces jointes", 
                                                   command=lambda: webbrowser.open(folder_path))
                    open_folder_button.pack()

                for idx, match in enumerate(re.finditer(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', task.get('description', ''))):
                    print(f"URL trouvée: {match.group()}")  # Debug
                    start, end = match.span()
                    url = match.group()
                    tag_name = f"hyper{idx}"
                    make_url_clickable(desc_text, url, f"1.0 + {start} chars", f"1.0 + {end} chars", tag_name)
                
                break  # Sortir de la boucle dès que la tâche correspondante est trouvée


def filter_due_date():
    selected_category = current_category_var.get()
    if filter_var.get() == 1 and selected_category == 'next_actions':
        tasks = manager.tasks[selected_category]
        filtered_tasks = [task for task in tasks if datetime.strptime(task['due_date'], '%Y-%m-%d').date() <= date.today()]
        update_filtered_treeview(selected_category, filtered_tasks)
    else:
        update_treeview(selected_category)

# Fonction pour mettre à jour l'affichage filtré
def update_filtered_treeview(category, tasks):
    global current_tree
    current_tree = treeviews[category]
    for row in current_tree.get_children():
        current_tree.delete(row)
    for task in tasks:
        current_tree.insert("", tk.END, values=(task['name'], task['created_date'], task.get('due_date', 'N/A'), task.get('priority', 'N/A'), task.get('description', 'N/A')))

# Création du carnet d'onglets# Initialize Tkinter root window
root = tk.Tk()
root.iconbitmap('@g.xbm')
root.title("Getting Things Done App")


# Définir les variables de contrôle Tkinter ici
category_var = tk.StringVar()
category_var.set('inbox')
priority_var = tk.StringVar()
priority_var.set('Low')
assigned_to_var = tk.StringVar()
attached_file_var = tk.StringVar()

# Create a frame for input widgets
input_frame = tk.Frame(root)
input_frame.pack(side=tk.TOP, padx=10, pady=5)

# Labels
task_name_label = tk.Label(input_frame, text="Task Name")
description_label = tk.Label(input_frame, text="Description")
category_label = tk.Label(input_frame, text="Category")
due_date_label = tk.Label(input_frame, text="Due Date")
priority_label = tk.Label(input_frame, text="Priority")
assigned_to_label = tk.Label(input_frame, text="Assigned To")
attached_file_label = tk.Label(input_frame, text="Attached File")
attached_file_button = tk.Button(input_frame, text="Choose File", command=lambda: choose_file())

attached_file_label.grid(row=7, column=0, sticky='w')
attached_file_button.grid(row=7, column=1, sticky='w')

# Task name Entry
task_name_entry = tk.Entry(input_frame, width=50)

# Description Text and its Scrollbar
description_text = tk.Text(input_frame, width=100, height=10)
description_text_scrollbar = tk.Scrollbar(input_frame, orient=tk.VERTICAL, command=description_text.yview)
description_text['yscrollcommand'] = description_text_scrollbar.set

# Category Combobox
category_var = tk.StringVar()
category_var.set('inbox')
category_menu = ttk.Combobox(input_frame, textvariable=category_var, values=list(manager.tasks.keys()), width=20,state='readonly')

# Due Date Entry
due_date_calendar = DateEntry(input_frame, width=20)

# Priority Combobox
priority_var = tk.StringVar()
priority_var.set('Low')
priority_menu = ttk.Combobox(input_frame, textvariable=priority_var, values=['Low', 'Medium', 'High', 'Urgent'], width=20,state='readonly')

# Assigned To Combobox
assigned_to_var = tk.StringVar()
assigned_to_var.set('Unassigned')
assigned_to_menu = ttk.Combobox(input_frame, textvariable=assigned_to_var, values=['Unassigned', 'Me', 'Someone Else'], width=20)


# Add Task Button
add_button = tk.Button(input_frame, text="Add Task", command=lambda: add_task())

# Using grid geometry manager
task_name_label.grid(row=0, column=0, sticky='w')
task_name_entry.grid(row=0, column=1, columnspan=4, sticky='w')

description_label.grid(row=1, column=0, sticky='w')
description_text.grid(row=1, column=1, columnspan=4, sticky='w')
description_text_scrollbar.grid(row=1, column=5, sticky='ns')  # Place it beside description_text

category_label.grid(row=2, column=0, sticky='w')
category_menu.grid(row=2, column=1, sticky='w')

due_date_label.grid(row=3, column=0, sticky='w')
due_date_calendar.grid(row=3, column=1, sticky='w')

priority_label.grid(row=4, column=0, sticky='w')
priority_menu.grid(row=4, column=1, sticky='w')

assigned_to_label.grid(row=5, column=0, sticky='w')
assigned_to_menu.grid(row=5, column=1, sticky='w')

add_button.grid(row=6, column=1, pady=10, sticky='w')

attached_files_display = tk.Label(input_frame, text="")
attached_files_display.grid(row=8, column=1, sticky='w')

##################

# Ceci est la Frame pour le séparateur
separator_frame = tk.Frame(root)
separator_frame.pack(side=tk.TOP, padx=10, pady=5, fill=tk.X)

# Ajoutez le séparateur à sa propre Frame
separator = ttk.Separator(separator_frame, orient="horizontal")
separator.pack(side=tk.TOP, fill=tk.X)


notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, padx=10, pady=5)


# Separate frame for filter and move options
filter_move_frame = tk.Frame(root)
filter_move_frame.pack(side=tk.TOP, padx=10, pady=5)

#filter_var = tk.IntVar(value=1)
#filter_button = tk.Checkbutton(filter_move_frame, text="Filter Due Date", variable=filter_var)
#filter_button.pack(side=tk.LEFT)

filter_var = tk.IntVar(value=1)
filter_button = tk.Checkbutton(filter_move_frame, text="Filter Due Date", variable=filter_var, command=filter_due_date)
filter_button.pack(side=tk.LEFT)

#new_category_var = tk.StringVar()
#new_category_var.set('inbox')
#move_category_menu = ttk.Combobox(filter_move_frame, textvariable=new_category_var, values=list(manager.tasks.keys()))
#move_category_menu.pack(side=tk.LEFT)

#move_button = tk.Button(filter_move_frame, text="Move Task", command=lambda: move_selected_task())
#move_button.pack(side=tk.LEFT)

move_category_var = tk.StringVar()
move_category_var.set('inbox')
move_category_label = tk.Label(filter_move_frame, text="Move to Category:")
move_category_label.pack(side=tk.LEFT)
move_category_menu = ttk.Combobox(filter_move_frame, textvariable=move_category_var, values=list(manager.tasks.keys()),state='readonly')
move_category_menu.pack(side=tk.LEFT)

move_button = tk.Button(filter_move_frame, text="Move Task", command=move_selected_task)
move_button.pack(side=tk.LEFT)



#treeviews = {}
current_tree = None
current_category = None

# Déclaration de la variable pour stocker les chemins de fichiers attachés
attached_files = []

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, padx=10, pady=5)

treeviews = {}
current_tree = None
current_category_var = tk.StringVar()

for category in manager.tasks.keys():
    tab_frame = tk.Frame(notebook)
    notebook.add(tab_frame, text=category)
    tree = ttk.Treeview(tab_frame, columns=("Task", "Created Date", "Due Date", "Priority", "Description"), show="headings")
    tree.heading("#1", text="Task")
    tree.heading("#2", text="Created Date")
    tree.heading("#3", text="Due Date")
    tree.heading("#4", text="Priority")
    tree.heading("#5", text="Description")
    tree.pack(fill=tk.BOTH)
    treeviews[category] = tree
    update_treeview(category)

        
    # Ajoutez la ligne suivante ici pour lier chaque Treeview à la fonction show_task_details
    tree.bind('<Double-1>', show_task_details)

# Boucle principale pour l'interface

root.mainloop()
