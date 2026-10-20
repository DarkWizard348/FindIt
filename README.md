# FindIt — College Lost & Found Portal

> A modern, secure, and responsive web portal built for college campuses to help students, faculty, and staff report, track, search, and recover misplaced belongings.

---

## 1. Project Overview

**FindIt** is a dedicated campus lost-and-found portal designed specifically for college environments. Unlike generic public lost-and-found boards, FindIt is tailored to university life: it categorizes items by campus buildings (such as Central Library, Main Canteen, Science Labs, and Sports Complex) and academic categories (ID Cards, Calculators, Textbooks, Water Bottles, Bags, and Keys).

The platform enables students who have misplaced an item to register a detailed lost report, while finders can log discovered items. Both parties can browse, search with partial keywords, filter by building or category, and coordinate item return through campus authorities before updating the status to **Recovered**.

---

## 2. Problem Statement

On busy college campuses, hundreds of personal belongings are misplaced every semester in lecture halls, laboratories, canteens, and sports fields. Traditional methods of recovering items suffer from severe shortcomings:
- **Scattered Unofficial Channels:** Students post frantic messages across WhatsApp groups, Reddit, and Discord, where reports are quickly buried under message floods.
- **Physical Notice Boards:** Paper notices pinned to boards are easily ignored, damaged, or out of date.
- **No Central Tracking:** Campus security and department offices often lack a synchronized digital register of lost vs. handed-over items.
- **Privacy Risks:** Students frequently post their private phone numbers, roll numbers, or personal social media handles on public forums to find their belongings, exposing them to harassment and scams.

---

## 3. Project Objectives

1. **Centralized Campus Hub:** Provide a single, official, and easily accessible digital portal for all lost and found reports across campus.
2. **Fast Discovery via Search & Filters:** Allow students to search by partial keywords (case-insensitive) and filter by specific campus locations, categories, report types, and recovery statuses.
3. **Student Privacy Protection:** Safeguard students by strictly prohibiting the public publishing of phone numbers, student IDs, and private passwords on reports.
4. **Lifecycle Management:** Track items from initial report (`Lost` or `Found`) to handover verification (`Recovered`).
5. **Secure Architecture:** Employ parameterized SQL queries to prevent SQL injection, validate file extensions for safe image uploads, and limit upload sizes.
6. **Robust Testing & Evidence:** Provide an automated pytest suite and a structured Git version control workflow using Git Bash and GitHub for academic evaluation.

---

## 4. Key Features

- **Dynamic Homepage & KPI Dashboard:** Real-time counters showing counts for Lost Items, Found Items, and Recovered Items, accompanied by quick-action buttons and recent report previews.
- **Report Lost Item:** Multi-field form capturing item name, category, campus location, date lost, description, and optional photo upload.
- **Report Found Item:** Parallel form for honest finders to log discovered items with location and date found.
- **Granular Categories:**
  - Electronics
  - Books and Stationery
  - Bags
  - Water Bottles
  - ID Cards
  - Keys
  - Clothing
  - Other
- **Intelligent Search Engine:** Case-insensitive partial matching across item names and descriptions.
- **Multi-Dimensional Filters:** Filter simultaneously by Report Type (`Lost` / `Found`), Category, Campus Location, and Status (`Lost`, `Found`, `Recovered`).
- **Status Lifecycle & Recovery:** Update items to `Recovered` with a single click and confirmation, preventing invalid state changes.
- **Secure Image Uploads:** Supports PNG, JPG, JPEG, and WEBP formats up to 5 MB with unique UUID filenames to prevent file overwrite collisions. Shows a crisp vector placeholder when no image is provided.
- **Responsive & Modern UI:** Crafted with a modern design system (custom CSS properties, glassmorphism navigation, responsive cards, micro-animations, and mobile drawer).

---

## 5. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3, JavaScript (ES6) | Semantic structure, custom design system, mobile menu, live image preview, and flash alerts |
| **Backend** | Python 3.13, Flask 3.1.x, Werkzeug | Web routing, application factory, secure file handling, form processing |
| **Database** | SQLite3 | Lightweight, zero-configuration relational persistence with parameterized SQL queries |
| **Testing** | pytest 8.x | Automated unit and integration testing with isolated temporary test databases |
| **Version Control** | Git & GitHub | Distributed version control via Windows Git Bash |

*Note: In accordance with project instructions, Jenkins and third-party CI/CD automation pipelines are not used.*

---

## 6. Project Folder Structure

```text
FindIt/
├── app.py                  # Main Flask application, routes, and form validation
├── database.py             # SQLite connection management and parameterized queries
├── requirements.txt        # Python package dependencies
├── README.md               # Complete project documentation and guides
├── .gitignore              # Ignores venv, caches, local databases, and uploaded images
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout with navigation, flash alerts, and footer
│   ├── index.html          # Homepage with hero, stats dashboard, and recent cards
│   ├── report_form.html    # Universal form for reporting lost and found items
│   ├── items.html          # Search and multi-filter browsing catalog
│   ├── item_detail.html    # Comprehensive item view and status recovery
│   └── 404.html            # User-friendly 404 error page
│
├── static/                 # Static frontend assets
│   ├── css/
│   │   └── style.css       # Full responsive stylesheet and design system
│   ├── js/
│   │   └── script.js       # Client-side validation, mobile menu, and image preview
│   └── images/
│       ├── logo.svg        # Scalable vector logo for FindIt brand
│       └── placeholder.svg # Fallback vector graphic for items without photos
│
├── uploads/                # Dedicated folder for user-uploaded item photos
│   └── .gitkeep            # Tracks directory in Git while ignoring uploaded files
│
├── tests/                  # Automated test suite
│   ├── conftest.py         # Pytest fixtures for isolated temporary DB and test client
│   └── test_app.py         # 13 automated tests covering all functional requirements
│
└── instance/               # Local runtime folder for SQLite database (findit.sqlite)
    └── .gitkeep
```

---

## 7. Prerequisites

Before running FindIt, ensure you have the following installed on your Windows machine:
1. **Python 3.10+** (Python 3.13 recommended). Verify in terminal:
   ```bash
   python --version
   ```
2. **Git for Windows** (includes Git Bash). Verify:
   ```bash
   git --version
   ```

---

## 8. Windows Installation & Setup Guide

Open **Git Bash** on your Windows computer and execute the following steps:

### Step 1: Navigate to the Project Directory
```bash
cd /c/Users/KASHIF/.gemini/antigravity-ide/scratch/FindIt
```

### Step 2: (Optional but Recommended) Create a Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate
```

### Step 3: Install Required Dependencies
```bash
python -m pip install -r requirements.txt
```

---

## 9. Running the Application

In **Git Bash**, start the local development server:

```bash
python app.py
```

You will see output similar to:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Open your web browser and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 10. Database Initialization & Storage Details

- **Database Engine:** SQLite3.
- **Storage Location:** `instance/findit.sqlite`.
- **Automatic Setup:** The database tables and indices are automatically created upon the first launch through `init_db()` in `database.py`. No manual SQL migrations or separate database setup steps are needed.
- **Table Schema:**
  ```sql
  CREATE TABLE IF NOT EXISTS items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      item_name TEXT NOT NULL,
      category TEXT NOT NULL,
      report_type TEXT NOT NULL CHECK(report_type IN ('Lost', 'Found')),
      location TEXT NOT NULL,
      item_date TEXT NOT NULL,
      description TEXT NOT NULL,
      image_filename TEXT,
      status TEXT NOT NULL CHECK(status IN ('Lost', 'Found', 'Recovered')),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```
- **Indices:** Fast indexing on `status`, `category`, and `created_at DESC` for snappy queries.

---

## 11. Automated Testing with pytest

FindIt includes an isolated automated test suite that executes against temporary SQLite databases without modifying development data.

Run the tests using Git Bash:
```bash
python -m pytest -v
```

### Test Coverage Summary (13 Tests):
1. `test_homepage_loads_successfully`: Verifies status 200, branding, and dashboard stats.
2. `test_create_valid_lost_item_report`: Validates creating a Lost item report and redirecting to detail view.
3. `test_create_valid_found_item_report`: Validates creating a Found item report.
4. `test_required_fields_validation`: Ensures empty name, location, or description return HTTP 400.
5. `test_invalid_category_rejected`: Rejects unauthorized categories.
6. `test_search_partial_and_case_insensitive`: Confirms partial keyword search across titles and descriptions.
7. `test_filters_return_correct_reports`: Verifies filtering by type, category, and location.
8. `test_combined_search_and_filters`: Validates searching and filtering simultaneously.
9. `test_recovered_status_workflow`: Tests marking items as Recovered and prevents invalid transitions.
10. `test_invalid_image_upload_rejected`: Blocks dangerous extensions (`.py`, `.exe`, `.sh`).
11. `test_valid_image_upload_accepted`: Accepts valid PNG/JPG uploads and serves them via `/uploads/<filename>`.
12. `test_nonexistent_item_returns_404`: Verifies custom 404 handler for missing item IDs.
13. `test_invalid_status_database_exception`: Checks that invalid database statuses raise `ValueError`.

---

## 12. Git Workflow & Staged Commits

The application was developed in five discrete, verifiable stages following professional Git commit practices:

| Stage | Commit Hash | Message | Scope & Changes |
| :--- | :--- | :--- | :--- |
| **Stage 1** | `cdd95e8` | `feat: create Flask application and homepage` | Project directory initialization, `.gitignore`, `requirements.txt`, `database.py` schema, `app.py` factory, `templates/base.html`, `templates/index.html`, `templates/404.html`, responsive stylesheet `style.css`, and logo assets. |
| **Stage 2** | `5b6c32a` | `feat: add lost and found report forms` | Created `templates/report_form.html` with dual Lost/Found modes, campus location datalist, category selectors, date bounds, client-side preview, and input validation. |
| **Stage 3** | `03144c0` | `feat: save item reports in SQLite` | Implemented SQLite report persistence, unique image storage, created `templates/item_detail.html` displaying metadata, image gallery, and recovery actions. |
| **Stage 4** | `7438612` | `feat: add search filters and recovery status` | Built `templates/items.html` featuring real-time keyword search, multi-filter selectors, active filter pills, empty search states, and the `/items/<id>/recover` status workflow. |
| **Stage 5** | *(Current)* | `test: add validation tests and improve documentation` | Built pytest test fixtures in `tests/conftest.py`, 13 automated tests in `tests/test_app.py`, and this comprehensive `README.md` guide. |

---

## 13. Connecting to GitHub (Step-by-Step for Windows Git Bash)

Follow these exact steps in Git Bash to connect and push this repository to GitHub:

### Step 1: Create a New Repository on GitHub
1. Log in to [GitHub](https://github.com).
2. Click the **+** icon in the top-right corner and select **New repository**.
3. Repository name: `FindIt-Lost-And-Found` (or `FindIt`).
4. Set visibility to **Public** (or **Private** based on college submission instructions).
5. **Do NOT** check "Add a README file", ".gitignore", or "license" (we already created them locally).
6. Click **Create repository**.

### Step 2: Link Your Local Repository to GitHub
Copy the repository URL from GitHub (e.g., `https://github.com/YOUR_USERNAME/FindIt-Lost-And-Found.git`) and run in Git Bash:
```bash
git remote add origin https://github.com/YOUR_USERNAME/FindIt-Lost-And-Found.git
```

Verify the remote link:
```bash
git remote -v
```

### Step 3: Push Your Code
```bash
git branch -M main
git push -u origin main
```

### Step 4: Verify Your Commit History
```bash
git log --oneline
```

---

## 14. Screenshot Evidence for College Submission

For your college DevOps and Full-Stack ISE-2 assignment submission, capture the following screenshots and store them in an `evidence/` folder:

1. **Homepage:** `evidence/01_homepage.png` — Showing the FindIt hero section, KPI counters (Lost, Found, Recovered), and recent report cards.
2. **Report Lost Form:** `evidence/02_report_lost_form.png` — Showing the lost item submission form with campus locations and image preview.
3. **Report Found Form:** `evidence/03_report_found_form.png` — Showing the found item report page.
4. **Search & Multi-Filters:** `evidence/04_search_and_filters.png` — Showing search results filtered by campus location (e.g. Central Library) and category (Water Bottles).
5. **Item Details & Recovery:** `evidence/05_item_detail_recovered.png` — Showing an item page marked with the green "Recovered" status badge.
6. **Git Bash History:** `evidence/06_git_log.png` — Showing `git log --oneline` displaying all 5 meaningful commits.
7. **Pytest Results:** `evidence/07_pytest_success.png` — Showing terminal output with all 13 tests passing (100% green).
8. **GitHub Repository:** `evidence/08_github_repo.png` — Showing the repository page on GitHub with all files, commits, and README rendered.

---

## 15. Limitations & Future Scope

While FindIt provides a fully functional lost-and-found solution for campus use, future iterations could introduce:
- **Campus SSO / Student Email Verification:** Integration with college Google Workspace / Microsoft 365 single sign-on to ensure only verified students and staff can post.
- **Automated AI Matching:** Embedding matching algorithms to automatically notify students when a newly reported "Found" item matches a registered "Lost" item.
- **Campus Map Integration:** Interactive SVG map of campus buildings indicating hotspots where items are frequently misplaced or recovered.
- **SMS / Web Push Notifications:** Instant notifications when an item in a student's watched category is reported.

---

## 16. Academic Declaration

This project was built for the **College DevOps and Full-Stack ISE-2 Website Assignment**. It demonstrates full-stack web engineering with Python Flask, SQLite, test-driven validation using pytest, and disciplined version control workflows using Git Bash and GitHub.
