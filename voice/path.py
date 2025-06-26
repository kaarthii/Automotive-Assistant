import subprocess  # For running system-level commands
import os      # For file system navigation and environment variables

# Function to find the path of an executable given a partial keyword
def find_exe_path(app_keyword):
    try:
        # First attempt: use Windows 'where' command to find the application path
        output=subprocess.check_output(f"where {app_keyword}",shell=True,text=True)
        return output.strip().split('\n')[0] # Return the first match
    except subprocess.CalledProcessError:
        # If 'where' fails (e.g., program not in system PATH), do manual search
        search_dirs=[
            r"C:\\Program Files",
            r"C:\\Program Files (x86)",
            os.environ.get("LOCALAPPDATA","")   # Include user's local app data path
        ]
        # Recursively walk through each directory looking for a matching .exe
        for base in search_dirs:
            for root, dirs, files in os.walk(base):
                for file in files:
                    if app_keyword.lower() in file.lower() and file.endswith(".exe"):
                        return os.path.join(root,file)   # Return full path if match found
    # Fallback if no match is found
    return None
