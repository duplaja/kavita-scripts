from pathlib import Path
import re
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import requests
import json

########################################################
#
# Change These Settings, as desired.
#
########################################################

#Kavita ODPS url (required, replace with your own)

odps_url = ''  # ex) https://example.com/api/opds/dxxxxxxxxb-3439-46f7-b9cf-xxxxxxxxxx9c

# Whether to send the file to a remote server (using rsync). (required).

send_remote = True  #True or False

# Rsync Configs, only required if send_remote is True

ssh_key = '' #local path to pub key  ex) /home/username/.ssh/id_rsa.pub
ssh_user = ''  #username and address for SSH / rsync.   ex) kavita@example.com

# Path to kavita root folder. Can be local, or your path on remote server.
kavita_base_path = '' # Path or empty string '' to use folder this script runs in. ex) '/sites/example.com/files'

#########################################################
#
# Stop Editing Below Here
#
#########################################################

#Defaults kavita_base_path to directory this program is in, if not set.
if kavita_base_path == '':
    kavita_base_path = str(Path().resolve())

# Calculated from odps_url
base_url = odps_url.split('/api')[0]
api_key = odps_url.split('/opds/')[1]


def kauth():

    auth_url = base_url+'/api/Plugin/authenticate/?apiKey='+api_key+'&pluginName=Kavita_List'

    response = requests.post(auth_url)

    token = response.json()['token']

    return token


def get_kavita_libraries(kavita_token):

    headers = {
        'Authorization': f'Bearer {kavita_token}',
        'accept': "text/plain",
        'Content-Type': "application/json"
    }

    libraries_url = base_url+'/api/Library/libraries'

    response = requests.get(libraries_url, headers=headers)

    libraries = response.json()

    library_dict = {}

    for library in libraries:

        library_name = library['name']
        library_folder = kavita_base_path+library['folders'][0]
        library_dict[library_name] = library_folder

    return library_dict

def scan_kavita_folder(kavita_scan_path):

    kavita_token = kauth()

    file_scan_url = base_url+'/api/Library/scan-folder'

    headers = {
        'Authorization': f'Bearer {kavita_token}',
        'accept': "text/plain",
        'Content-Type': "application/json"
    }

    data = {
        "apiKey": api_key,
        "folderPath": kavita_scan_path,
    }

    response = requests.post(file_scan_url, headers=headers, data=json.dumps(data))

    return



def send_epub_via_rsync(local_path,remote_path):

    # Rsync with --mkpath option
    subprocess.run(['rsync', '-avz', '--mkpath', '--append-verify', '-e', f'ssh -i {ssh_key}', local_path, f'{ssh_user}:{remote_path}'], check=True)

    # Remove the base path
    remote_path_string = str(remote_path)
    relative_path = remote_path_string[len(kavita_base_path):].strip('/')

    # Remove the filename
    dir_path = '/'.join(relative_path.split('/')[:-1])

    kavita_scan_path = '/' + dir_path

    scan_kavita_folder(kavita_scan_path)

    return


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

def convert_epub(input_file, output_location, output_directory, author, title, series, series_index):

    # Determine output directory and file paths
    output_dir = sanitize_folder_name(output_directory)

    output_dir_path = Path(output_location+'/'+output_dir)

    local_output_dir_path = output_dir_path

    # Extract the original file name and create output file path
    input_filename = Path(input_file).name
    output_file = local_output_dir_path / input_filename

    if send_remote:

        local_output_base = Path().resolve()
        local_output_dir_path = Path(f"{local_output_base}/temp/{output_dir}")
        output_file = local_output_dir_path / input_filename


    if not local_output_dir_path.exists():
        local_output_dir_path.mkdir(parents=True)


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
    
    if send_remote:
        
        remote_output_dir_path = Path(f"{output_location}/{output_dir}")
        
        remote_output_file = remote_output_dir_path / input_filename

        print(output_file)
        print(remote_output_file)

        result = send_epub_via_rsync(output_file,remote_output_file)
    
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
        output_directory = series_folder_entry.get()

        convert_epub( input_file, output_location, output_directory, author, title, series, series_index)

        done_loading_indicator()
    
    else:
        messagebox.showerror("Error", "All fields are required.")

    return


def show_loading_indicator():
    loading_label.config(text="Processing, please wait...")
    loading_label.grid(row=9, column=0, columnspan=3, pady=10)
    app.update_idletasks()


def hide_loading_indicator():
    loading_label.grid_remove()
    app.update_idletasks()

def done_loading_indicator():
    loading_label.config(text="Done Converting. You may choose another epub or Exit.")
    loading_label.grid(row=9, column=0, columnspan=3, pady=10)
    app.update_idletasks()

def update_dropdown():
    # Clear existing options
    dropdown['menu'].delete(0, 'end')
    
    # Get library root directory
    current_dir = Path(kavita_base_path)

    kavita_token = kauth()
    libraries = get_kavita_libraries(kavita_token)

    dropdown['menu'].add_command(label="(Kavita Root)", command=tk._setit(selected_folder, str(current_dir)))

    for library_name, library_path in libraries.items():
        
        dropdown['menu'].add_command(label=library_name, command=tk._setit(selected_folder, library_path))


def clear_fields(clear_file = True):

    if clear_file:
        input_file_path.set("")
    
    series_folder_entry.delete(0,tk.END)
    author_entry.delete(0, tk.END)
    title_entry.delete(0, tk.END)
    series_entry.delete(0, tk.END)
    series_index_entry.delete(0, tk.END)
    hide_loading_indicator()

def validate_fields():
    if not input_file_path.get().strip():
        return False
    if not series_folder_entry.get().strip():
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
            series_folder_entry.insert(0, series)
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


current_dir = Path(kavita_base_path)

# Dropdown for Library Root
ttk.Label(frame, text="Library Folder\n(Output Path):").grid(row=1, column=0, padx=10, pady=5)
selected_folder = tk.StringVar()
dropdown = ttk.OptionMenu(frame, selected_folder, current_dir)
dropdown.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

ttk.Label(frame, text="Series Folder\n(Output Dir):").grid(row=2, column=0, padx=10, pady=5)
series_folder_entry = ttk.Entry(frame, width=50)
series_folder_entry.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(frame, text="Epub Metadata", font=('Helvetica', 16)).grid(row=3, column=0, columnspan=3, padx=10, pady=10)

ttk.Label(frame, text="Author:").grid(row=4, column=0, padx=10, pady=5)
author_entry = ttk.Entry(frame, width=50)
author_entry.grid(row=4, column=1, padx=10, pady=5)

ttk.Label(frame, text="Title:").grid(row=5, column=0, padx=10, pady=5)
title_entry = ttk.Entry(frame, width=50)
title_entry.grid(row=5, column=1, padx=10, pady=5)

ttk.Label(frame, text="Series:").grid(row=6, column=0, padx=10, pady=5)
series_entry = ttk.Entry(frame, width=50)
series_entry.grid(row=6, column=1, padx=10, pady=5)

ttk.Label(frame, text="Series Index:").grid(row=7, column=0, padx=10, pady=5)
series_index_entry = ttk.Entry(frame, width=50)
series_index_entry.grid(row=7, column=1, padx=10, pady=5)

ttk.Button(frame, text="Process Epub", command=process_epub).grid(row=8, column=0, columnspan=3, pady=10)

# Create the loading indicator
loading_label = ttk.Label(frame, text="")
loading_label.grid(row=9, column=0, columnspan=3, pady=10)
loading_label.grid_remove()  # Hide initially

ttk.Button(frame, text="Clear All", command=clear_fields).grid(row=10, column=0, columnspan=3, pady=10)

frame.columnconfigure(1, weight=1)
frame.grid_columnconfigure(1, weight=1)
frame.grid_rowconfigure(2, weight=1)

#Populates Dropdown for main loop
update_dropdown()

app.mainloop()
