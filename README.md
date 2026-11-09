<div align="center">

# Axion Extract

**Invoice work, ready for review**

Turn invoices and business documents into organized, validated, GST-aware data, built for Indian CAs and finance teams.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-axioninvoiceextractor.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://axioninvoiceextractor.vercel.app/)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com/)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

[**Open the live app**](https://axioninvoiceextractor.vercel.app/) · [Sign up free](https://axioninvoiceextractor.vercel.app/login?tab=signup) · [API docs](https://axioninvoiceextractor.vercel.app/docs) · [Talk to the team](https://axioninvoiceextractor.vercel.app/talk-to-team)

</div>

---

## Live Demo

Axion Extract is deployed on **Vercel** and available at:

**https://axioninvoiceextractor.vercel.app/**

You can create a free account (Starter plan, 25 pages per month) and start processing invoices right away. No local setup is needed.

---

## Overview

Axion Extract replaces manual invoice punching with a review-first workflow. Upload supplier or sales invoices, let the app read and validate them, correct only what is flagged, and export clean data to your books.

The project began as a local-first Streamlit tool and now ships as a hosted product with accounts, workspaces, exports, templates, and plans. The extraction and validation engine is still simple, modular, and runnable on your own machine.

---

## Features

### The core workflow

| Step | What happens |
|------|--------------|
| **1. Upload** | Drag and drop one or more invoice PDFs into your workspace. |
| **2. Extract** | Axion reads supplier, dates, tax details, and line items automatically. |
| **3. Validate** | GSTIN and tax math are checked for issues. |
| **4. Review** | You fix only what is flagged. You stay in control. |
| **5. Export** | Send clean, reviewed data to your books. |

### Integrity and accuracy checks

- **Field-level extraction**: invoice numbers, dates, parties, tax identifiers, totals, and line items.
- **Tax arithmetic checks**: compares line values, tax components (CGST / SGST / IGST), and invoice totals to catch inconsistencies such as `subtotal + GST != total`.
- **GSTIN validation**: validates GSTIN structure and checksum, and surfaces state and tax-split details.
- **Exception flags**: missing or unusual values are brought forward for focused human review.
- **Party consistency**: keeps supplier and customer details organized across invoice records.
- **Duplicate protection**: avoids duplicate entries using a normalized vendor + invoice number pair.
- **OCR fallback**: scanned or poor-quality PDFs are processed with Tesseract and Poppler when available.

### Exports

Reviewed invoices can be exported in formats that fit common accounting workflows:

| Format | Use |
|--------|-----|
| **CSV register** (`.csv`) | Invoice registers for spreadsheets and further analysis |
| **Excel workbook** (`.xlsx`) | Formatted reports and reconciliation |
| **Tally Prime XML** (`.xml`) | Import straight into Tally Prime |

Exports are available to authorized workspace roles.

### Dashboard and reporting

- Invoice totals, monthly trends, and validation statuses at a glance.
- Monthly PDF summary report with totals, GST breakdown, top vendors, and pass/fail validation counts.

### Document categories

| Document type | Status |
|---------------|--------|
| Purchase invoices | Live |
| Sales invoices | Live |
| Expense documents | In testing |
| Credit and debit notes | In testing |
| Bank statements | Coming soon |
| Custom documents | Coming soon |

### Custom invoice templates

Build a template that matches your workflow:

1. **Choose fields**: pick the data points your documents need.
2. **Set rules**: add formats, required values, and checks (for example, GSTIN checksum, required invoice date).
3. **Review results**: run it, then refine with human review.

An example *Purchase invoice template* includes Invoice number (Text, required), Invoice date (Date, required), Supplier GSTIN (GSTIN, checksum), Taxable value (Currency, required), and Line items (Table: HSN, qty, rate). The number of templates depends on your plan.

### API and integrations

- **Axion API**: available by workspace access. [Request access](mailto:axion@xmail.com?subject=Request%20Axion%20API%20access).
- **Interactive API docs**: [Swagger UI](https://axioninvoiceextractor.vercel.app/docs).
- **MCP connections**: planned. Not available yet. [Share your integration needs](mailto:axion@xmail.com?subject=Axion%20MCP%20interest).

### Security and data protection

- **Private workspaces**: business data is scoped to the appropriate workspace.
- **Access controls**: account access is protected by authenticated sign-in.
- **Clear review trail**: extracted data stays visible for checks before you use it.
- **Protected transport**: HTTPS when accessing Axion online.

### Other highlights

- Light and dark mode.
- **Ask Axion AI**: in-app assistant for quick questions.
- Newsletter and product updates via email.
- Business Suite waitlist for upcoming invoice, collections, and reporting tools.

---

## Pricing

| Plan | Price | Page allowance | Best for |
|------|-------|----------------|----------|
| **Starter** | ₹0 / month | Up to 25 pages | Individuals getting started |
| **Professional** | ₹499 / month | Up to 500 pages | Independent CAs and small teams |
| **Business** | ₹1,499 / month | Up to 2,000 pages | Growing finance teams |
| **Enterprise** | Custom | Higher volume | [Contact us](mailto:axion@xmail.com?subject=Axion%20Enterprise%20plan) |

Page limits apply per month. All plans include invoice extraction and review, with reports and exports (plan-dependent).

---

## Frequently Asked Questions

**Does Axion file GST returns automatically?**
No. Axion helps extract, validate, organize, and report invoice data. Review the results and use the relevant filing process for your business.

**Can I correct extracted data?**
Yes. The review step lets you check and correct values before using a record.

**What documents can I process?**
Purchase and sales invoices are live. Credit and debit notes are in testing, and bank statements are coming soon.

---

## Architecture

The project is intentionally modular:

| File | Responsibility |
|------|----------------|
| `app.py` | Application entry point and dashboard UI |
| `extractor.py` | PDF reading, field extraction, and validation logic |
| `processing.py` | Orchestration for each uploaded invoice |
| `database.py` | User authentication, invoice storage, and database access |
| `report.py` | PDF summary generation for monthly reporting |
| `tests/` | Automated tests for processing and validation behavior |
| `data/` | Local database storage (`data/invoices.db`) |

### Processing pipeline

```
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
Save to database and show in dashboard
       |
       v
Export (CSV / Excel / Tally XML) or generate monthly report PDF
```

### Tech stack

- **Python 3.11+**
- **pdfplumber** and **PyPDF2** for PDF text extraction
- **pytesseract** and **pdf2image** for scanned-document OCR
- **SQLite** for local storage
- **pandas** for invoice data handling
- **ReportLab** for PDF report generation
- **pytest** for tests
- **Vercel** for deployment and hosting

### Repository structure

```
invoice_extractor-main/
├── app.py                 # Application entry point
├── extractor.py           # Extraction and validation logic
├── processing.py          # File processing pipeline
├── database.py            # Database layer
├── report.py              # PDF summary report builder
├── requirements.txt       # Python dependencies
├── tests/                 # Unit/integration tests
├── data/                  # Database and generated app data
├── invoices/              # Example input directory
├── output/                # Exported outputs
├── uploads/               # Uploaded files
├── README.md              # Project documentation
├── README_FRONTEND.md     # Front-end style notes
├── .env.example           # Example environment settings
├── app/                   # Additional app resources
└── docs/                  # Supporting docs
```

---

## Deployment

The production app is deployed on **[Vercel](https://vercel.com/)** at
[axioninvoiceextractor.vercel.app](https://axioninvoiceextractor.vercel.app/).

To deploy your own copy:

1. Fork or clone this repository.
2. Import the project into Vercel from your Git provider.
3. Add the environment variables from `.env.example` in **Project Settings → Environment Variables**.
4. Deploy. Every push to your main branch triggers a new production deployment automatically.

> **Note:** Vercel's filesystem is ephemeral. For production use, point the app at a hosted database instead of a local SQLite file, and use external storage for uploaded files.

---

## Run Locally

### 1) Clone the repository

```bash
git clone https://github.com/Venu277/invoice_extractor_updated.git
cd invoice_extractor_updated
```

### 2) Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

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

Then open the local URL shown in the terminal, usually `http://localhost:8501`.

### OCR support

Standard PDFs work without OCR. For scanned invoices, install these and make sure they are on your `PATH`:

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler](https://poppler.freedesktop.org/)

Without Tesseract, scanned PDFs may not be processed and the app will usually report that no extractable text was found.

---

## Data Model

Each user has a separate account and stores invoices in an isolated workspace. An invoice record includes:

- File name
- Vendor
- Invoice number
- Date
- GSTIN
- Subtotal
- CGST, SGST, IGST
- GST total
- Final total
- Validation status

Duplicate detection uses a normalized pair of vendor and invoice number.

---

## Validation Rules

Before marking an invoice as valid, the extractor checks that:

- Required fields are present.
- GSTIN format matches the expected pattern (and checksum where applicable).
- CGST and SGST appear together when applicable.
- IGST does not coexist with CGST/SGST unless the document clearly indicates a mixed case.
- Subtotal + GST roughly matches the total amount.

These checks are validation signals, not legal certification.

---

## Running Tests

```bash
pytest
```

---

## Notes and Limitations

- Axion is a data extraction and validation tool, **not** a government filing system.
- Extraction relies on pattern parsing, so unusual invoice layouts may need manual review. This is why the review step exists.
- GST checks are heuristic and should be treated as data validation, not legal or tax advice.
- Features marked *In testing*, *Coming soon*, or *Planned* (credit/debit notes, bank statements, custom documents, MCP) are not yet generally available.

---

## Roadmap

- Credit and debit note workflows
- Bank statement ingestion
- Custom document extraction
- MCP-compatible integrations
- Axion Business Suite: invoices, collections, reporting, and everyday finance operations ([join the waitlist](mailto:axion@xmail.com?subject=Axion%20Business%20Suite%20waitlist))

---

## Contributing

Contributions are welcome. To improve extraction logic, validation rules, dashboard UX, or reporting, please open an issue or submit a pull request with a clear description of the change.

---

## Contact

- Email: [axion@xmail.com](mailto:axion@xmail.com)
- Web: [axioninvoiceextractor.vercel.app](https://axioninvoiceextractor.vercel.app/)
- Talk to the team: [axioninvoiceextractor.vercel.app/talk-to-team](https://axioninvoiceextractor.vercel.app/talk-to-team)

---

## License

Licensed under the [MIT License](LICENSE).

<div align="center">

© 2026 Axion Technologies Private Limited

</div>
