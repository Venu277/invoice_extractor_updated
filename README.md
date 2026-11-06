# Invoice Extractor

A lightweight Python application for extracting structured data from PDF invoices, validating key GST-related checks, storing records in a local database, and generating a monthly business summary report.

This repository is a practical, local-first invoice-processing workflow for small businesses that need to turn uploaded supplier PDFs into organized accounting data without manually retyping every field.

## What the app does

- Upload one or more invoice PDFs from a user dashboard.
- Read text directly from normal PDFs.
- Fall back to OCR for scanned/poor-quality documents when Tesseract and Poppler are available.
- Extract core invoice fields such as:
  - vendor name
  - invoice number
  - invoice date
  - GSTIN
  - subtotal
  - CGST / SGST / IGST
  - total amount
- Validate extracted values and flag issues such as missing required fields, GSTIN format problems, mismatched taxes, and subtotal + GST != total.
- Save records per user in SQLite and avoid duplicate invoice entries based on vendor + invoice number.
- Show a dashboard with invoice totals, monthly trends, and invoice statuses.
- Generate a PDF monthly summary report for the selected period.

## Architecture

The project is intentionally simple and modular:

- `app.py` - Streamlit application entry point and dashboard UI
- `extractor.py` - PDF reading, field extraction, and validation logic
- `processing.py` - orchestration for each uploaded invoice
- `database.py` - user authentication, invoice storage, and SQLite access
- `report.py` - PDF summary generation for monthly reporting
- `tests/` - automated verification for invoice processes and validation behavior
- `data/` - local database storage (`data/invoices.db`)

## How it works

```text
Upload invoice PDF
       |
       v
Extract text from PDF (or OCR fallback)
       |
       v
Parse key invoice fields
       |
       v
Validate GST-related checks
       |
       v
Save to SQLite and show in dashboard
       |
       v
Generate monthly report PDF
```

## Tech stack

- Python 3.11+
- `pdfplumber` and `PyPDF2` for PDF text extraction
- `pytesseract` and `pdf2image` for scanned-document OCR
- SQLite for local storage
- pandas for invoice data handling
- ReportLab for PDF report generation
- pytest for tests

## Repository structure

```text
invoice_extractor-main/
├── app.py                 # Streamlit app
├── extractor.py           # Extraction and validation logic
├── processing.py          # File processing pipeline
├── database.py            # SQLite database layer
├── report.py              # PDF summary report builder
├── requirements.txt       # Python dependencies
├── tests/                 # Unit/integration tests
├── data/                  # SQLite database and generated app data
├── invoices/              # Example input directory
├── output/                # Exported outputs (if used)
├── uploads/               # Uploaded files
├── README.md              # Project documentation
├── README_FRONTEND.md     # Front-end style notes
├── .env.example           # Example environment settings
├── app/                   # Additional app resources
└── docs/                  # Supporting docs
```

## Quick start

### 1) Clone the repository

```bash
git clone https://github.com/Venu277/invoice_extractor_updated.git
cd invoice_extractor_updated
```

### 2) Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Start the app

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## OCR support

The app can extract text from standard PDF files without OCR. For scanned invoices, OCR is enabled if these tools are installed and available on PATH:

- Tesseract OCR
- Poppler

If Tesseract is missing, scanned PDFs may not be processed correctly and the app will usually report that no extractable text was found.

## Data model

Each user has a separate account and can store invoices in SQLite. The invoice table stores fields such as:

- file name
- vendor
- invoice number
- date
- GSTIN
- subtotal
- CGST
- SGST
- IGST
- GST total
- final total
- validation status

Duplicate detection is based on a normalized pair of vendor and invoice number.

## Validation rules

The extractor performs basic GST-oriented checks before marking an invoice as valid. Examples include:

- required fields must be present
- GSTIN format must match the expected pattern
- CGST and SGST should be present together when applicable
- IGST should not coexist with CGST/SGST on the same invoice unless the document format clearly indicates a mixed case
- subtotal + GST should roughly match the total amount

These checks are warnings/validation signals, not legal certification.

## Monthly reporting

The application can build a PDF report for a selected month using the approved invoice data. The report includes:

- summary totals
- GST breakdown
- top vendors
- pass/fail validation counts
- monthly business summary tables

## Running tests

```bash
pytest
```

## Notes and limitations

- This project is designed to be a practical local tool, not a government filing system.
- Extraction relies on regular-expression parsing, so invoice layouts that vary widely from the expected structure may need manual review.
- GST checks are heuristic and should be treated as data validation rather than legal advice.
- For production usage, you may want to move from SQLite to a more robust database and add stronger authentication and deployment controls.

## Contributing

Contributions are welcome. If you want to improve the extraction logic, validation rules, dashboard UX, or reporting, please open an issue or submit a pull request with a clear description of the change.

## Project goal

The project aims to reduce manual data entry for invoice processing by turning PDF invoices into clean, reviewable accounting data that can be stored, validated, and summarized quickly.

## License

Licensed under MIT license
