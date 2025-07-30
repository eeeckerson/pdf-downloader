# pdf-downloader

A python project for downloading .pdf filings from a public URL and organizing the folder structure using input files.
Example configuration is setup for Alphabet's IR website. It includes a graphical interface for ease of use. 
---
## Included Files

## Scripts
- `pdf_downloader.py`: The main script for downloading PDFs.
- `gui_launcher.py`: A graphical interface to launch the downloader without using the terminal.
- `update_filing_type_filenames.py`: A script for scanning page 1 from downloaded PDFs and renaming files based on `sec-grp-det.csv`

## Input Files
- `input/base-url.csv`: Base URL input file. Example configuration is for Alphabet's IR website.
- `input/year-url.csv`: Year URL input file. Example configuration is filing years to process from Alphabet's IR website.
- `input/sec-grp-url.csv`: SEC group URL input file. Example configuraton is the SEC groups used for Alphabet's IR website.
- `input/sec-grp-det.csv`: SEC group details input file. Example configuraton is the SEC filing types on Alphabet's IR website.

## Output Files

- Downloaded PDFs will be saved to: `downloaded_pdfs/{section}/{year}/`
  
- Logs:
  - `download_log.txt`: All activity logs.
  - `error_log.txt`: Any download or parse failures.
  - `structured_log.json`: JSON-formatted structured logs.
  - `filing_metadata.csv`: Details extracted from the web page table for each file.

---

# How to Install

- A virtual environment is recommended for running the scripts. An installer script (`setup.sh`) is provided for automated setup of the virtual environment.

## VIRTUAL ENVIRONMENT SETUP (Automated)

1. Place the `setup.sh` file into the same folder as the script files (`pdf_downloader.py`).
2. Open Terminal and navigate to the folder: 

   `cd ~/Downloads/pdf_downloader_2025`

3. Make the setup script executable (only needed once):

   `chmod +x setup.sh`

4. Run the script:

   `./setup.sh`

This will:
- Delete any existing virtual environment
- Create a fresh one using python3
- Activate it
- Install required packages: requests, beautifulsoup4, pandas

## VIRTUAL ENVIRONMENT SETUP (Manual)

If you are using macOS or Linux:

1. Open Terminal
2. Navigate to the bundle directory:
   `cd ~/Downloads/pdf_downloader_2025`

3. Create a virtual environment:
   `python3 -m venv venv`

4. Activate the virtual environment:
   `source venv/bin/activate`

5. Install required packages:
   `pip install requests beautifulsoup4 pandas`

# HOW TO RUN THE DOWNLOADER

## Option 1: Terminal

1. Open Terminal and `cd` into the pdf_downloader_2025 folder.
2. Ensure dependencies are installed:
   ```
   pip install requests beautifulsoup4 pandas
   ```
3. Run the `pdf_downloader.py` script:
   ```
   python3 pdf_downloader.py
   ```
4. Run the `update_filing_type_filenames.py` script:
   ```
   python3 update_filing_type_filenames.py
   ```
5. Deactivate the virtual environment when done:
   ```
   deactivate
   ```
## Option 2: GUI (macOS/Windows)

1. Open Terminal and `cd` into the pdf_downloader_2025 folder.
2. Ensure dependencies are installed:
   ```
   pip install requests beautifulsoup4 pandas
   ```
3. Run the `gui_launcher.py` script:
   ```
   python3 gui_launcher.py
   ```
4. Use file browsers to select:
   - `input/base-url.csv`
   - `input/sec-grp-url.csv`
   - `input/year-url.csv`
     
5. Click Import to begin processing.

6. Run the `update_filing_type_filenames.py` script:
   ```
   python3 update_filing_type_filenames.py
   ```
7. Deactivate the virtual environment when done:
   ```
   deactivate
   ```
Additional design details and use cases are provided within the file: `pdf-downloader-design.pdf`
