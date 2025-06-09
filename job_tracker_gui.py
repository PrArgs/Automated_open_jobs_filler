import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import sys

# ---------------- Google Sheets Setup ----------------
SCOPE = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open("Visual Job Tracker").sheet1

# ---------------- Scraper Function ----------------
def scrape_linkedin(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        job_title = soup.find("h1").text.strip() if soup.find("h1") else ""
        company_tag = soup.find("a", {"data-tracking-control-name": "public_jobs_topcard-org-name"})
        company_name = company_tag.text.strip() if company_tag else ""
        location_tag = soup.find("span", class_="topcard__flavor--bullet")
        location = location_tag.text.strip() if location_tag else ""
        
        return job_title, company_name, location
    except Exception as e:
        print(f"Scraping error: {e}")
        return "", "", ""

# ---------------- Submit Handler ----------------
def submit():
    job_url = entries["Job Link"].get()
    today = datetime.now().strftime("%d/%m/%Y")

    hyperlink_formula = f'=HYPERLINK("{job_url}", "link")'

    row_data = [
        entries["Company Name"].get(),  # Column B
        entries["Job Title"].get(),     # Column C
        entries["Location"].get(),      # Column D
        entries["Recruiter"].get(),     # Column E
        entries["Connections?"].get(),  # Column F
        entries["Email"].get(),         # Column G
        entries["Offered Pay"].get(),   # Column H
        entries["Offered Pay"].get(),   # Column I (duplicate)
        hyperlink_formula,              # Column J - hyperlink only here
        today,                          # Column K
        entries["Status"].get(),        # Column L
        entries["Cover Letter"].get(),  # Column M
        entries["Notes"].get()          # Column N
    ]

    try:
        col_b = sheet.col_values(2)  # Column B = index 2
        next_row = len(col_b) + 1

        cell_range = f'B{next_row}:N{next_row}'
        sheet.update(cell_range, [row_data], value_input_option='USER_ENTERED')

        messagebox.showinfo("Success", f"Job added to row {next_row}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add job: {e}")


# ---------------- Scrape Button Handler ----------------
def autofill():
    url = entries["Job Link"].get()
    job_title, company_name, location = scrape_linkedin(url)
    entries["Job Title"].delete(0, tk.END)
    entries["Company Name"].delete(0, tk.END)
    entries["Location"].delete(0, tk.END)
    entries["Job Title"].insert(0, job_title)
    entries["Company Name"].insert(0, company_name)
    entries["Location"].insert(0, location)

# ---------------- GUI Layout ----------------
root = tk.Tk()
root.title("Job Tracker")

# Bring window to front and focus it:
root.attributes("-topmost", True)
root.update()
root.attributes("-topmost", False)
root.focus_force()

labels = [
    "Company Name", "Job Title", "Location", "Recruiter", "Connections?",
    "Email", "Offered Pay", "Status", "Cover Letter", "Notes", "Job Link"
]
entries = {}

for idx, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=idx, column=0, sticky=tk.W, padx=5, pady=3)
    entry = tk.Entry(root, width=60)
    entry.grid(row=idx, column=1, padx=5, pady=3)
    entries[label] = entry

# Insert URL from command line argument (if provided) into "Job Link" on startup
if len(sys.argv) > 1:
    url_arg = sys.argv[1]
    entries["Job Link"].insert(0, url_arg)

tk.Button(root, text="Autofill from URL", command=autofill, bg="#add8e6").grid(row=len(labels), column=0, padx=5, pady=10)
tk.Button(root, text="Submit to Sheet", command=submit, bg="#90ee90").grid(row=len(labels), column=1, padx=5, pady=10)

root.mainloop()
