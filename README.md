# 🚗 Car Data Pipeline

A high-performance Python data pipeline for generating, cleaning, validating, and processing automotive datasets. This project demonstrates an end-to-end ETL (Extract, Transform, Load) workflow using realistic car listing and catalogue data.

---

## 📌 Features

- Generate realistic car listing datasets
- Clean and validate messy automotive data
- Data quality checks and preprocessing
- Automated ETL pipeline
- Unit testing with pytest
- Dashboard support for data visualization
- Easy to extend for larger datasets

---

## 📂 Project Structure

```
car-data-pipeline/
│
├── assets/
│   └── Images and project assets
│
├── dashboard/
│   └── Dashboard application
│
├── src/
│   ├── pipeline.py
│   └── Processing modules
│
├── tests/
│   └── Unit tests
│
├── generate_data.py
├── requirements.txt
├── README.md
├── LICENSE
│
├── dirty_car_listings.csv
├── clean_car_listings.csv
├── dirty_catalogue.csv
└── clean_catalogue.csv
```

---

## ⚙️ Technologies Used

- Python 3.11+
- Pandas
- NumPy
- Pytest
- Streamlit (Dashboard)

---

## 📦 Installation

Clone the repository

```bash
git clone https://github.com/AlvinTubtub/car-data-pipeline.git
```

Go to the project

```bash
cd car-data-pipeline
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Generate Sample Data

```bash
python generate_data.py
```

This generates realistic automotive datasets including:

- Car Listings
- Vehicle Catalogue
- Clean datasets
- Dirty datasets for testing

---

## ▶️ Run the Data Pipeline

```bash
python src/pipeline.py
```

The pipeline performs:

- Data loading
- Data validation
- Missing value handling
- Duplicate removal
- Data transformation
- Clean dataset generation

---

## 🧪 Run Unit Tests

```bash
pytest
```

or

```bash
pytest tests/
```

---

## 📊 Dashboard

If Streamlit is installed:

```bash
streamlit run dashboard/app.py
```

The dashboard provides:

- Dataset preview
- Summary statistics
- Data quality metrics
- Interactive visualizations

---

## 📁 Sample Files

| File | Description |
|-------|-------------|
| dirty_car_listings.csv | Raw car listing dataset |
| clean_car_listings.csv | Cleaned car listing dataset |
| dirty_catalogue.csv | Raw vehicle catalogue |
| clean_catalogue.csv | Cleaned vehicle catalogue |

---

## 📈 Pipeline Workflow

```
Generate Data
      │
      ▼
Raw CSV Files
      │
      ▼
Validation
      │
      ▼
Cleaning
      │
      ▼
Transformation
      │
      ▼
Clean Dataset
      │
      ▼
Dashboard / Analysis
```

---

## 📖 Future Improvements

- Support larger datasets
- Database integration
- Automated scheduling
- Machine learning integration
- Docker deployment
- Cloud storage support

---

## 👤 Author

**Alvin Tubtub**

GitHub:
https://github.com/AlvinTubtub

---

## 📄 License

This project is licensed under the MIT License.
