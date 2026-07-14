# 🚗 Car Data Pipeline

[![Python Tests](https://github.com/AlvinTubtub/car-data-pipeline/actions/workflows/python-tests.yml/badge.svg)](https://github.com/AlvinTubtub/car-data-pipeline/actions/workflows/python-tests.yml)

A Python-based ETL (Extract, Transform, Load) pipeline that cleans, validates, standardizes, and aggregates used car listing data. The project also includes automated unit tests and a Streamlit dashboard for visualizing the processed data.

---

## Features

* Cleans inconsistent car listing data
* Normalizes prices (including USD to PHP conversion)
* Standardizes mileage values
* Generates canonical vehicle fingerprints
* Detects and removes anomalous records
* Aggregates duplicate listings
* Unit tested with Pytest
* Interactive dashboard using Streamlit
* Automated testing with GitHub Actions

---

# Project Structure

```text
car-data-pipeline
│
├── .github
│   └── workflows
│       └── python-tests.yml
│
├── dashboard
│   └── app.py
│
├── src
│   ├── __init__.py
│   └── pipeline.py
│
├── tests
│   └── test_pipeline.py
│
├── generate_data.py
├── dirty_car_listings.csv
├── clean_car_listings.csv
├── requirements.txt
├── pytest.ini
├── pyproject.toml
├── .gitignore
├── README.md
└── LICENSE
```

---

# Requirements

* Python 3.10 or newer
* Git
* Visual Studio Code (recommended)

---

# Clone the Repository

```bash
git clone https://github.com/AlvinTubtub/car-data-pipeline.git
cd car-data-pipeline
```

---

# Windows Setup

## 1. Create a Virtual Environment

```powershell
python -m venv .venv
```

## 2. Activate the Virtual Environment

**Command Prompt**

```cmd
.venv\Scripts\activate
```

**PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

# macOS Setup

## 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

## 2. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

## 3. Upgrade pip

```bash
pip install --upgrade pip
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Generate Sample Data

Generate a fresh sample dataset.

**Windows**

```powershell
python generate_data.py
```

**macOS**

```bash
python3 generate_data.py
```

---

# Run the ETL Pipeline

The pipeline reads the raw dataset, cleans the data, removes anomalies, and creates the final aggregated output.

## Windows

```powershell
python src/pipeline.py ^
-i dirty_car_listings.csv ^
-o clean_car_listings.csv ^
-r 58.0
```

or

```powershell
python src/pipeline.py -i dirty_car_listings.csv -o clean_car_listings.csv -r 58.0
```

## macOS / Linux

```bash
python3 src/pipeline.py \
-i dirty_car_listings.csv \
-o clean_car_listings.csv \
-r 58.0
```

or

```bash
python3 src/pipeline.py -i dirty_car_listings.csv -o clean_car_listings.csv -r 58.0
```

If the pipeline succeeds, you should see output similar to:

```text
Starting pipeline...
Scanning source...
Success.
Output written to clean_car_listings.csv
```

---

# Run the Dashboard

Start the Streamlit dashboard.

## Windows

```powershell
streamlit run dashboard/app.py
```

## macOS

```bash
streamlit run dashboard/app.py
```

Open your browser:

```
http://localhost:8501
```

---

# Run the Unit Tests

The project uses **Pytest**.

Simply run:

```bash
pytest
```

Expected output:

```text
=========================
6 passed
=========================
```

---

# GitHub Actions

Every push or pull request automatically executes the unit tests.

Workflow location:

```text
.github/workflows/python-tests.yml
```

GitHub will display:

* ✅ Passing
* ❌ Failed

inside the **Actions** tab.

---

# Installing New Packages

Whenever you install a new package, update the requirements file.

```bash
pip freeze > requirements.txt
```

Commit the updated file.

---

# Updating the Repository

## Windows

```powershell
git pull
```

## macOS

```bash
git pull
```

---

# Common Commands

Activate virtual environment

Windows

```powershell
.venv\Scripts\activate
```

macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run tests

```bash
pytest
```

Run pipeline

```bash
python src/pipeline.py -i dirty_car_listings.csv -o clean_car_listings.csv -r 58.0
```

Run dashboard

```bash
streamlit run dashboard/app.py
```

Deactivate virtual environment

```bash
deactivate
```

---

# Troubleshooting

## ModuleNotFoundError

If you receive

```text
ModuleNotFoundError
```

ensure that:

* the virtual environment is activated
* dependencies are installed
* `pytest.ini` exists in the project root
* `src/__init__.py` exists

---

## File Not Found

Verify that the input file exists.

```bash
ls *.csv
```

or on Windows

```powershell
dir *.csv
```

---

## Streamlit Not Found

Install dependencies again.

```bash
pip install -r requirements.txt
```

---

## Verify Installation

```bash
pytest
```

Expected:

```text
=========================
6 passed
=========================
```

Then run:

```bash
python src/pipeline.py -i dirty_car_listings.csv -o clean_car_listings.csv -r 58.0
```

Finally:

```bash
streamlit run dashboard/app.py
```

Open:

```
http://localhost:8501
```

If all three commands work successfully, the project has been installed correctly.

---

# Author

**Alvin Tubtub**

GitHub: https://github.com/AlvinTubtub

---

# License

This project is licensed under the MIT License.
