Health Data Lake & Hybrid Schema Project (Part II)

A lightweight data lake + logical schema for integrating structured & unstructured health data

📌 Overview

This project implements a small-scale health analytics data lake, integrating two real-world public health datasets—BRFSS 2024 and CDC WONDER Provisional Mortality Statistics—and designing a hybrid logical schema that supports both structured and unstructured data.

The goal is to simulate the foundation of an enterprise architecture used by an insurance company to analyze chronic disease risk and build downstream analytical pipelines.

🗂️ Data Lake Architecture

The data lake follows a Raw → Processed organization to ensure reproducibility:

data_lake/
│
├── raw/
│   ├── Raw_data_sources.txt
│   └── (original BRFSS & CDC WONDER files)
│
├── processed/
│   ├── brfss_clean_semantic.csv
│   ├── cdc_wonder_clean.csv
│   └── raw_data_conversion.py
│
└── unstructured/
    └── (future PDFs, clinical notes, external docs)

✨ Key Design Principles

Immutability: Raw data is never modified; processed data can always be regenerated.

Semantic cleaning: Raw BRFSS variables are decoded, renamed, and normalized.

Schema alignment: Processed files map directly to the logical schema entities.

Hybrid readiness: Structure supports PDFs, notes, and other unstructured artifacts.

📊 Data Sources & Processing
1. BRFSS 2024 (Structured Survey Data)

Source: SAS XPT public-use file

301 original variables → curated subset for chronic disease modeling

Standardization & cleanup include:

Decode byte strings

Rename coded variables (e.g., _STATE → state_fips, SEXVAR → gender)

Map categorical codes using BRFSS documentation

Normalize BMI (_BMI5 ÷ 100)

Output: brfss_clean_semantic.csv
→ populates Person, Lifestyle, and HealthOutcome tables.

2. CDC WONDER Provisional Mortality Statistics

Source: state-level weekly mortality file

Cleaned by:

Removing non-essential columns

Normalizing age groups

Converting death counts to integers

Creating consistent state_fips identifiers

Output: cdc_wonder_clean.csv
→ populates StateHealthStats table.

3. Unstructured Data (Hybrid Extension)

Although currently empty, the data lake is designed to ingest:

PDF reports

Clinical guidelines

Text notes

External documents

Metadata will be stored in UnstructuredDataMetadata, enabling hybrid integration.

🗃️ Logical Schema (Relational Model)
Entities
Person
Attribute	Description
sequence_id (PK)	Unique BRFSS respondent
state_fips	Links to StateHealthStats
age	Respondent age
gender	Male/Female
education_level	Education level
income_level	Income category
Lifestyle

(1-to-1 with Person)

| sequence_id (PK, FK) | smoking_status | alcohol_use | heavy_drinker | exercise_status | bmi |

HealthOutcome

(1-to-1 with Person)

| sequence_id (PK, FK) | diabetes_status | heart_disease | stroke_history | flu_shot | pneumonia_shot |

StateHealthStats

| state_fips (PK) | age_group | deaths |

UnstructuredDataMetadata

| file_id (PK) | file_path | file_type | ingestion_ts | linked_sequence_id | linked_state_fips | description |

🔗 Relationships

Person ↔ Lifestyle → 1:1

Person ↔ HealthOutcome → 1:1

Person ↔ StateHealthStats → N:1

UnstructuredDataMetadata ↔ Person → N:0/1

UnstructuredDataMetadata ↔ StateHealthStats → N:0/1

🧹 Normalization & Optimization
✔ 1NF

All attributes atomic

Clean categorical formats

No repeating groups

✔ 2NF

Lifestyle & HealthOutcome decomposed from Person

Eliminates partial dependencies

✔ 3NF

State-level attributes independent from person-level attributes

Unstructured metadata is separated

✔ Hybrid Optimization

Metadata entity bridges structured and unstructured datasets without redundancy.

☁ Cloud Platform Architecture (Azure)

A cloud-native version of the data lake uses Azure Blob Storage:

azure-storage/
│
├── raw/
│   ├── brfss/BRFSS_2024.XPT
│   └── cdc/Provisional Mortality Statistics.xls
│
├── processed/
│   ├── brfss_clean_semantic.csv
│   └── cdc_wonder_clean.csv
│
└── unstructured/
    └── (PDFs, docs, etc.)

Cloud Notes

Azure Data Factory → ingestion

Azure SQL / Synapse → analytics

state_fips = join key

Metadata table supports hybrid integration

📐 ER Diagram Placeholder

(Insert your ERD image here)

[Person]──1:1──[Lifestyle]
   │
   └──1:1──[HealthOutcome]
   │
   └──N:1──[StateHealthStats]
   │
   └──0..N──[UnstructuredDataMetadata]

🚀 How to Reproduce

Place raw datasets in data_lake/raw/

Run:

python data_lake/processed/raw_data_conversion.py


Generated CSVs will appear in data_lake/processed/

Load processed tables into your SQL database following the logical schema

📎 Acknowledgements

BRFSS and CDC WONDER datasets are provided by the U.S. CDC.
