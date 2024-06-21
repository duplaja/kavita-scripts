import sqlite3


#################################################
# Configure Here. 
# 
# * You MUST make a backup of your database first, and then stop Kavita before running.
#
# * This assumes you rename the folders while Kavita is stopped. This script could be extended to do so automatically
#
##################################################
#Library Folder
library_folder_name = '' #Example: xianxia

#Pattern is old folder name, new folder name.
folder_dict = {
    'Library-of-Heavens-Path' : 'Library of Heavens Path', 
    'A-Record-of-A-Mortals-Journey-to-Immortality': 'A Record of A Mortals Journey to Immortality',
    'A-Will-Eternal': 'A Will Eternal',
    'Beyond the Timescape - Er Gen': 'Beyond the Timescape',
    'Coiling-Dragon': 'Coiling Dragon',
    'Desolate-Era': 'Desolate Era',
    'Divine-Throme-of-Primordial-Blood': 'Divine Throme of Primordial Blood',
}

def update_partial_string(db_path, old_string, new_string):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        
        # Get all column names for the current table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        for column in columns:
            column_name = column[1]
            
            # Update partial string in the current column
            cursor.execute(f"""
                UPDATE "{table_name}"
                SET "{column_name}" = REPLACE("{column_name}", ?, ?)
                WHERE "{column_name}" LIKE ?
            """, (old_string, new_string, f"%{old_string}%"))

    conn.commit()
    conn.close()

if library_folder_name: 

    for old_path, new_path in folder_dict.items():
        old_path = '/'+library_folder_name+'/'+old_path
        new_path = '/'+library_folder_name'/'+new_path
        
        update_partial_string('kavita.db', old_path, new_path)
