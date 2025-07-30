import os
import requests
import hashlib
import time
import csv
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime

# Setup paths
input_folder = "input"
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Load data
base_url = pd.read_csv(os.path.join(input_folder, "base-url.csv"))["base-url"][0]
sections = pd.read_csv(os.path.join(input_folder, "sec-grp-url.csv"))["sec-grp-url"]
years = pd.read_csv(os.path.join(input_folder, "year-url.csv"))["year-url"]

# Output and log files
download_root = "downloaded_pdfs"
log_file = os.path.join(log_folder, "download_log.txt")
error_log_file = os.path.join(log_folder, "error_log.txt")
json_log_file = os.path.join(log_folder, "structured_log.json")
metadata_file = "filing_metadata.csv"

# Optional date filter
date_filter = None

# Structured logging setup
structured_log = []
if not os.path.exists(metadata_file):
    with open(metadata_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filing date", "filing type", "filing description", "file name", "year-url", "sec-grp-url"])

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def log_error(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(error_log_file, "a") as f:
        f.write(f"{timestamp} {message}\n")
    structured_log.append({"timestamp": timestamp, "status": "error", "message": message})

def log_json(status, message, context=None):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    entry = {"timestamp": timestamp, "status": status, "message": message}
    if context:
        entry.update(context)
    structured_log.append(entry)

def get_file_hash(content):
    return hashlib.md5(content).hexdigest()

successes = []
failures = []

for section in sections:
    for year in years:
        section_url = f"{base_url}{section}/{year}"
        log(f"🔍 Processing: {section_url}")
        log_json("info", f"Processing section/year", {"section-url": section, "year-url": year, "url": section_url})

        try:
            response = requests.get(section_url)
            response.raise_for_status()
        except Exception as e:
            msg = f"❌ Failed to load {section_url}: {e}"
            log(msg)
            log_error(msg)
            failures.append(section_url)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        pdf_links = [urljoin(section_url, link['href']) for link in links if link['href'].lower().endswith(".pdf")]

        save_path = os.path.join(download_root, section, str(year))
        os.makedirs(save_path, exist_ok=True)

        
        for pdf_url in pdf_links:
            filing_date, filing_type, filing_description = "", "", ""
            for row in soup.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 3 and row.find("a") and os.path.basename(pdf_url) in row.text:
                    filing_date = cols[0].get_text(strip=True).replace("/", "-")
                    filing_type = cols[1].get_text(strip=True).replace(" ", "_")
                    filing_description = cols[2].get_text(strip=True).replace(" ", "_").replace("/", "-")
                    break
    
            filename = os.path.basename(pdf_url)
                    # Create filename with metadata
            meta_name = f"{filing_date}_{filing_type}_{section}_{year}_{filename}" if filing_date else f"{section}_{year}_{filename}"
            file_path = os.path.join(save_path, meta_name)

            attempt = 0
            while attempt < 3:
                try:
                    log(f"⬇️ Checking {pdf_url}")
                    pdf_response = requests.get(pdf_url)
                    pdf_response.raise_for_status()
                    new_content = pdf_response.content
                    new_hash = get_file_hash(new_content)

                    if date_filter:
                        last_modified = pdf_response.headers.get("Last-Modified")
                        if last_modified:
                            modified_time = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
                            if modified_time.date() < datetime.strptime(date_filter, "%Y-%m-%d").date():
                                msg = f"⏩ Skipped (older than {date_filter}): {file_path}"
                                log(msg)
                                log_json("skipped", msg)
                                break

                    if os.path.exists(file_path):
                        with open(file_path, "rb") as existing_file:
                            existing_hash = get_file_hash(existing_file.read())
                        if existing_hash == new_hash:
                            msg = f"🔁 Skipped (already exists and identical): {file_path}"
                            log(msg)
                            log_json("skipped", msg)
                            break
                        else:
                            msg = f"♻️ Updating changed file: {file_path}"
                            log(msg)
                            log_json("updated", msg)
                    else:
                        msg = f"✅ Saving new file: {file_path}"
                        log(msg)
                        log_json("downloaded", msg)

                    with open(file_path, "wb") as f:
                        f.write(new_content)
                    successes.append(pdf_url)

                    for row in soup.find_all("tr"):
                        cols = row.find_all("td")
                        if len(cols) >= 3 and row.find("a") and filename in row.text:
                            filing_date = cols[0].get_text(strip=True)
                            filing_type = cols[1].get_text(strip=True)
                            filing_description = cols[2].get_text(strip=True)
                            with open(metadata_file, "a", newline="") as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow([filing_date, filing_type, filing_description, meta_name, year, section])  # File name now includes year and section
                            break
                    break

                except Exception as e:
                    attempt += 1
                    msg = f"⚠️ Attempt {attempt} failed for {pdf_url}: {e}"
                    log(msg)
                    log_error(msg)
                    if attempt == 3:
                        msg = f"❌ Failed to download after 3 attempts: {pdf_url}"
                        log(msg)
                        log_error(msg)
                        log_json("error", msg, {"url": pdf_url})
                        failures.append(pdf_url)
                    time.sleep(2)
                time.sleep(1)

log("✅ Script complete.")
log(f"Total Successes: {len(successes)}")
log(f"Total Failures: {len(failures)}")

# Save structured log
with open(json_log_file, "w") as jf:
    json.dump(structured_log, jf, indent=2)
