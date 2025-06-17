import subprocess
import os

def find_exe_path(app_keyword):
    try:
        output=subprocess.check_output(f"where {app_keyword}",shell=True,text=True)
        return output.strip().split('\n')[0]
    except subprocess.CalledProcessError:
        search_dirs=[
            r"C:\\Program Files",
            r"C:\\Program Files (x86)",
            os.environ.get("LOCALAPPDATA","")
        ]
        for base in search_dirs:
            for root, dirs, files in os.walk(base):
                for file in files:
                    if app_keyword.lower() in file.lower() and file.endswith(".exe"):
                        return os.path.join(root,file)
    return None
