import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox


# GlobaL variables
origin = None
dest = None


# Logging function to console and log file
def main_function(origin, dest):

    # Getting time stamp of the sync process
    time_stamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Create log file path
    log_file_path = os.path.join(os.path.dirname(dest), 'log_file.txt')

    # Opening log file
    with open(log_file_path, 'a') as log_file:
        
        # Function to print both on console and write on log file
        def print_to_console(message):
            print(message)  # Print to console
            log_file.write(message + '\n')  # Write to file
            log_file.flush()  # Ensure immediate writing to file
        
        # Log styling
        print_to_console("############################################ LOG ############################################\n") 
        print_to_console(time_stamp + '\n')

        # Syncing
        copy_and_update_files(origin, dest, print_to_console)
        delete_extra_files(origin, dest, print_to_console)

        # Log styling
        print_to_console('\n')


# Make sure the interval is a valid number
def get_valid_interval():
    while True:
        interval = input("Synchronization interval (hours): ")
        if not interval.isdigit() or int(interval) < 1:
            print("Invalid interval")
        else:
            return int(interval)


# Select directories with dialogue box
def select_folder(type):
    if type == 'origin':
        messagebox.showinfo("Select Folder", "Please select the source folder to be synchronized.")
    else:
        messagebox.showinfo("Select Folder", "Please select the destination where the syncronized folder and log file should be created.")

    # Open a file dialog to select a folder
    folder_selected = filedialog.askdirectory()

    if folder_selected and type == 'origin':
        return folder_selected
    elif folder_selected and type == 'dest':
        return os.path.join(folder_selected, 'BackUp')
    else:
        print("No folder selected")
        return None


# Confirm folder selection
def confirm_folders(source_folder, destination_folder):
    # Create the confirmation message
    message = f"Source folder:\n{source_folder}\n\nDestination folder:\n{destination_folder}\n\nProceed with synchronization? This cannot be undone."

    # Show Yes/No confirmation dialog
    confirm = messagebox.askyesno("Confirm Paths", message)
    
    if confirm:
        print("\nUser confirmed synchronization.\n")
        return True
    else:
        print("\nUser canceled synchronization.\n")
        return False


# Copy new or edited files from origin to dest
def copy_and_update_files(origin, dest, print_to_console): 
    for root, dirs, files in os.walk(origin):
        # Create corresponding directory structure in destination
        relative_path = os.path.relpath(root, origin)  # Get relative path from source

        # Remove . from root directory for readability
        if relative_path == ".":
            relative_path = ""

        dest_path = os.path.join(dest, relative_path)  # Create destination path
        os.makedirs(dest_path, exist_ok=True)  # Ensure the directory exists
        
        for file in files:
            origin_file = os.path.join(root, file)  # Origin file path
            dest_file = os.path.join(dest_path, file)  # Destination file path

            # If the file does not exist in destination or is outdated, copy it
            if not os.path.exists(dest_file):
                shutil.copy2(origin_file, dest_file)
                print_to_console(f"Copied: {origin_file} -> {dest_file}")
            elif os.path.getmtime(origin_file) > os.path.getmtime(dest_file):
                shutil.copy2(origin_file, dest_file)
                print_to_console(f"Updated: {dest_file}")
            else:
                print_to_console(f"Skipped: {dest_file} (up to date)")


# Delete files present in the dest that are no longer present in the origin
def delete_extra_files(origin, dest, print_to_console):
    for root, dirs, files in os.walk(dest):
        # Create corresponding directory structure in destination
        relative_path = os.path.relpath(root, dest)  # Get relative path from source

        # Remove . from root directory for readability
        if relative_path == ".":
            relative_path = ""

        origin_path = os.path.join(origin, relative_path)  # Create origin path

        if not os.path.exists(origin_path):
            # If a directory does not exist in origin, delete it
            shutil.rmtree(root)
            print_to_console(f"Deleted: {root}")
        else: 
            for file in files:
                dest_file = os.path.join(root, file)  # Destination file path
                origin_file = os.path.join(origin_path, file)  # Origin file path

                # If the file does not exist in origin, delete it
                if not os.path.exists(origin_file):
                    os.remove(dest_file)
                    print_to_console(f"Deleted: {dest_file}")


# Syncronize directories
def synchronize():
    global origin, dest

    if origin is None or dest is None:
        origin = select_folder('origin')
        if origin:
            dest = select_folder('dest')
            if dest:
                if not confirm_folders(origin, dest):
                    print("Synchronization canceled.")
                    return
                
    # Perform the actual synchronization if everything checks out
    print(f"Syncing {origin} with {dest}...\n")
    main_function(origin, dest)
    print(f"Synchronization completed. Next one in {interval} hour{'s' if interval > 1 else ''}...")
    
    # Schedule the next sync in 2 hours (7200000 milliseconds)
    root.after(interval * 60 * 60 * 1000, synchronize)


# Get interval input
interval = get_valid_interval()

# Create a Tkinter window
root = tk.Tk()
root.withdraw()  # Hide the root window initially

# Start the first sync immediately and schedule future syncs
synchronize()

# Start the Tkinter event loop
root.mainloop()
