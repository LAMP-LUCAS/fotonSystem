import os
from pathlib import Path

docs_dir = Path(os.path.expanduser("~/Documents")) / "FotonSystem"
app_data_dir = Path(os.getenv('APPDATA')) / "FotonSystem"

print(f"Documents Path: {docs_dir}")
print(f"AppData Path: {app_data_dir}")

if docs_dir.exists():
    print(f"FOUND in Documents: {docs_dir}")
else:
    print(f"NOT FOUND in Documents")

if app_data_dir.exists():
    print(f"FOUND in AppData: {app_data_dir}")
else:
    print(f"NOT FOUND in AppData")
