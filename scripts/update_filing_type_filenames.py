import os
from PyPDF2 import PdfReader
import csv
import pandas as pd
from datetime import datetime

# Root base folder (assumes this script lives inside pdf_downloader_2025/)
base_dir = os.path.abspath(os.path.dirname(__file__))

# Input and logs directories
input_folder = os.path.join(base_dir, "input")
logs_dir = os.path.join(base_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Load inputs
sec_grp_path = os.path.join(input_folder, "sec-grp-det.csv")
year_url_path = os.path.join(input_folder, "year-url.csv")
sections = pd.read_csv(sec_grp_path)
years = pd.read_csv(year_url_path)["year-url"].astype(str).tolist()

# Build sec-grp-url to filing-typ mapping
sec_grp_map = sections.groupby("sec-grp-url")["filing-typ"].apply(lambda x: list(x.dropna().astype(str).unique())).to_dict()

# Initialize log
log_entries = []
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file_path = os.path.join(logs_dir, f"filing_type_update_log_" + timestamp + ".csv")

# Walk through folder structure inside downloaded_pdfs/<sec-grp-url>/<year-url>
downloads_root = os.path.join(base_dir, "downloaded_pdfs")

for sec_grp_url, filing_types in sec_grp_map.items():
    for year in years:
        folder_path = os.path.join(downloads_root, sec_grp_url, year)
        if not os.path.isdir(folder_path):
            continue

        for file in os.listdir(folder_path):
            if file.endswith(".pdf"):
                full_path = os.path.join(folder_path, file)
                try:
                    with open(full_path, "rb") as f:
                        reader = PdfReader(f)
                        text = reader.pages[0].extract_text().upper() if reader.pages else ""

                    matched_type = next((typ for typ in filing_types if typ.upper() in text), None)

                    if matched_type and matched_type not in file:
                        new_name = file.replace(".pdf", f"_{matched_type}.pdf")
                        new_path = os.path.join(folder_path, new_name)
                        os.rename(full_path, new_path)
                        print(f"✅ Renamed: {file} -> {new_name}")
                        log_entries.append([file, new_name, matched_type])
                    else:
                        log_entries.append([file, file, "NO_MATCH"])

                except Exception as e:
                    log_entries.append([file, file, f"ERROR: {str(e)}"])

# Save log
with open(log_file_path, "w", newline="") as log_csv:
    writer = csv.writer(log_csv)
    writer.writerow(["original_filename", "new_filename", "matched_filing_type"])
    writer.writerows(log_entries)

print(f"📄 Log saved to: {log_file_path}")
