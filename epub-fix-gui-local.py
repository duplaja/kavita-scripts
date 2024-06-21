from pathlib import Path
import re
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

###################################################
#
# Modify only the line below
#
###################################################

kavita_root = '' #Modify to set Kavita root, such as: /home/bob/kavita. Leave blank to keep as the directory this script runs in.

###################################################
#
# Stop modifying
#
####################################################


def get_kavita_root():
    
    if kavita_root == '':
        kavita_root = Path().resolve()
    else:
        kavita_root = Path(kavita_root)

    return kavita_root 


def sanitize_folder_name(name):
    # Remove any character that is a valid character in a folder name
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def append_decimal_if_needed(s):
    if '.' not in s:
        s += '.0'
    return s

def get_epub_metadata(epub_path):
    # Command to extract metadata from the epub using Calibre's CLI tool
    cmd = ['ebook-meta', epub_path]
    
    # Run the command and capture the output
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout
    
    # Initialize metadata variables
    title = None
    series_name = None
    series_index = None
    author = None
    
    # Regex patterns
    title_pattern = re.compile(r'^Title\s*:\s*(.+)')
    author_pattern = re.compile(r'^Author\(s\)\s*:\s*([^\[]+)')
    series_pattern = re.compile(r'^Series\s*:\s*([^#]+)(?:#(\d+))?')

    # Parse the output using regex
    for line in output.splitlines():
        if not title:
            title_match = title_pattern.match(line)
            if title_match:
                title = title_match.group(1).strip()
        
        if not author:
            author_match = author_pattern.match(line)
            if author_match:
                author = author_match.group(1).strip()
        
        if not series_name or not series_index:
            series_match = series_pattern.match(line)
            if series_match:
                series_name = series_match.group(1).strip()
                if series_match.group(2):
                    series_index = series_match.group(2).strip()
                else:
                    series_index = None
    
    if series_index:
        series_index = append_decimal_if_needed(series_index)
    
    return title, author,series_name, series_index

def convert_epub(input_file, output_location, author, title, series, series_index):

    # Sanitize the series name for the folder
    sanitized_series = sanitize_folder_name(series)

    # Determine output directory and file paths
    output_dir = sanitized_series

    output_dir_path = Path(output_location+'/'+output_dir)

    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)

    # Extract the original file name and create output file path
    input_filename = Path(input_file).name
    output_file = output_dir_path / input_filename

    cmd = ['ebook-convert', input_file, output_file, '--epub-version=3', '--epub-flatten']

    if author:
        cmd.extend([f'--authors={author}'])
    if title:
        cmd.extend([f'--title={title}'])
    if series:
        cmd.extend([f'--series={series}'])
    if series_index:
        cmd.extend([f'--series-index={series_index}'])
    
    # Execute the conversion command
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Successfully converted {input_file} to {output_file}")
    return

def process_epub():

    if validate_fields():

        show_loading_indicator()

        input_file = input_file_path.get()
        output_location = selected_folder.get()
        author = author_entry.get()
        title = title_entry.get()
        series = series_entry.get()
        series_index = series_index_entry.get()

        convert_epub( input_file, output_location, author, title, series, series_index)

        done_loading_indicator()
    
    else:
        messagebox.showerror("Error", "All fields are required.")

    return


def show_loading_indicator():
    loading_label.config(text="Processing, please wait...")
    loading_label.grid(row=7, column=0, columnspan=3, pady=10)
    app.update_idletasks()


def hide_loading_indicator():
    loading_label.grid_remove()
    app.update_idletasks()

def done_loading_indicator():
    loading_label.config(text="Done Converting. You may choose another epub or Exit.")
    loading_label.grid(row=7, column=0, columnspan=3, pady=10)
    app.update_idletasks()

def update_dropdown():
    # Clear existing options
    dropdown['menu'].delete(0, 'end')
    
    # Get library root directory
    current_dir = get_kavita_root()

    # Populate dropdown with subfolders
    subfolders = sorted([p for p in current_dir.iterdir() if p.is_dir()])
    subfolders.insert(0, "(Kavita / Script Root)")  # Add root at first position

    # Add options to dropdown menu
    for folder in subfolders:
        if folder == "(Kavita / Script Root)":
            dropdown['menu'].add_command(label="(Kavita / Script Root)", command=tk._setit(selected_folder, str(current_dir)))
        else:
            dropdown['menu'].add_command(label=folder.name, command=tk._setit(selected_folder, folder))


def clear_fields(clear_file = True):

    if clear_file:
        input_file_path.set("")
    
    author_entry.delete(0, tk.END)
    title_entry.delete(0, tk.END)
    series_entry.delete(0, tk.END)
    series_index_entry.delete(0, tk.END)
    hide_loading_indicator()

def validate_fields():
    if not input_file_path.get().strip():
        return False
    if not author_entry.get().strip():
        return False
    if not title_entry.get().strip():
        return False
    if not series_entry.get().strip():
        return False
    if not series_index_entry.get().strip():
        return False
    if not selected_folder.get().strip():
        return False
    

    return True


def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
    input_file_path.set(filename)
    if filename:

        clear_fields(False)
        
        stored_title, stored_author, stored_series, stored_series_index = get_epub_metadata(filename)

        if stored_title:
            title = stored_title
        else:
            title = Path(filename).stem

        if stored_author:
            author = stored_author
        else:
            author = 'Unknown'

        if stored_series:
            series = stored_series
        else:
            series = Path(filename).stem

        if stored_series_index:
            series_index = stored_series_index
        else:
            series_index = '1.0'
    
        if title:
            title_entry.insert(0, title)
        if author:
            author_entry.insert(0, author)
        if series:
            series_entry.insert(0, series)
        if series_index:
            series_index_entry.insert(0, series_index)
        

app = tk.Tk()
app.title("Kavita Epub Preparer")

# Style Configuration
style = ttk.Style()

background = '#343A40'
compliment = '#4AC694'
button_text = '#000000'

style.theme_use('clam')  

# Customize the colors and styles
style.configure('TFrame', background=background)
style.configure('TLabel', background=background, foreground=compliment, font=('Helvetica', 12))
style.configure('TButton', background=compliment, foreground=button_text, font=('Helvetica', 12))

app.configure(bg=background)

# Create a frame
frame = ttk.Frame(app, padding="10 10 10 10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

#File Input (epub)
input_file_path = tk.StringVar()
ttk.Label(frame, text="EPUB File:").grid(row=0, column=0, padx=10, pady=5)
ttk.Entry(frame, textvariable=input_file_path, width=50).grid(row=0, column=1, padx=10, pady=5)
ttk.Button(frame, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=5)


current_dir = get_kavita_root()

# Dropdown for Library Root
ttk.Label(frame, text="Library Dir:").grid(row=1, column=0, padx=10, pady=5)
selected_folder = tk.StringVar()
dropdown = ttk.OptionMenu(frame, selected_folder, current_dir)
dropdown.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

ttk.Label(frame, text="Author:").grid(row=2, column=0, padx=10, pady=5)
author_entry = ttk.Entry(frame, width=50)
author_entry.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(frame, text="Title:").grid(row=3, column=0, padx=10, pady=5)
title_entry = ttk.Entry(frame, width=50)
title_entry.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(frame, text="Series:").grid(row=4, column=0, padx=10, pady=5)
series_entry = ttk.Entry(frame, width=50)
series_entry.grid(row=4, column=1, padx=10, pady=5)

ttk.Label(frame, text="Series Index:").grid(row=5, column=0, padx=10, pady=5)
series_index_entry = ttk.Entry(frame, width=50)
series_index_entry.grid(row=5, column=1, padx=10, pady=5)

ttk.Button(frame, text="Process Epub", command=process_epub).grid(row=6, column=0, columnspan=3, pady=10)

# Create the loading indicator
loading_label = ttk.Label(frame, text="")
loading_label.grid(row=7, column=0, columnspan=3, pady=10)
loading_label.grid_remove()  # Hide initially

ttk.Button(frame, text="Clear All", command=clear_fields).grid(row=8, column=0, columnspan=3, pady=10)
ttk.Button(frame, text="Exit", command=app.quit).grid(row=9, column=0, columnspan=3, pady=10)

frame.columnconfigure(1, weight=1)
frame.grid_columnconfigure(1, weight=1)
frame.grid_rowconfigure(2, weight=1)

#Populates Dropdown for main loop
update_dropdown()

app.mainloop()
