# Database Systems Project – Parts I–IV

**Student:** Bruce Zhang
**Course:** Database Systems (Section 001)
**Institution:** New York University

---

## 📌 Project Overview

This repository contains a four-part Database Systems project that incrementally builds a complete data architecture pipeline, starting from enterprise-level conceptual modeling and ending with a physical database implementation and machine learning workflow. Each part is documented in a formal report (located in the `docs/` directory) and supported by schemas, scripts, and configuration files in this repository.

The project is framed around a realistic **insurance / health analytics use case**, emphasizing best practices in:

* Enterprise Data Architecture (EDA)
* Data lake design
* Logical and physical schema design
* Cloud-ready analytics and ML enablement

---

## 🧩 Project Structure

```
.
├── README.md
├── data_lake/
│   ├── raw/
│   ├── processed/
│   └── unstructured/
├── scripts/
│   └── raw_data_conversion.py
├── docs/
│   ├── Part_I_Report.pdf
│   ├── Part_II_Report.pdf
│   ├── Part_III_Report.pdf
│   └── (Part IV Report)
└── schemas/
    ├── logical_schema
    └── physical_schema
```

---

## Part I – Enterprise Data Architecture (Conceptual & Logical Modeling)

**Goal:** Translate unstructured business requirements into a normalized enterprise data model that supports complex insurance operations.

### Key Contributions

* Designed a full **Enterprise Data Architecture (EDA)** using ER modeling principles
* Identified core business entities: `Account`, `Contract`, `Associate`, `Customer`, and related bridge tables
* Resolved complex **many-to-many relationships** using associative entities
* Introduced **temporal modeling** (`EffectiveFrom`, `EffectiveTo`) to support time-varying relationships
* Distinguished **semantic roles** via multiple foreign keys from the same parent entity (e.g., Contract owner vs payer)

### Tools

* Erwin Data Modeler 15.0 (logical + physical configuration)

📄 **Documentation:** See *Part I Report* in `docs/` for full modeling rationale, validation against business cases, and subject-area breakdowns.

---

## Part II – Data Lake & Hybrid Logical Schema Design

**Goal:** Build a small-scale data lake and logical schema integrating structured and unstructured health data for insurance risk analysis.

### Data Lake Design

* Raw → Processed separation to ensure reproducibility
* Integrated two real-world public health datasets:

  * **BRFSS 2024** (individual-level survey data)
  * **CDC WONDER** (state-level mortality statistics)
* Designed for future ingestion of **unstructured data** (PDFs, reports, notes)

### Logical Schema

* Core entities: `Person`, `Lifestyle`, `HealthOutcome`, `StateHealthStats`
* Introduced `UnstructuredDataMetadata` to support hybrid integration
* Fully normalized to **3NF**, with clear PK/FK relationships

📄 **Documentation:** See *Part II Report* and the original Part II README in `docs/` for schema definitions, normalization explanations, and cloud mapping.

---

## Part III – Physical Database Design & Machine Learning Pipeline

**Goal:** Implement a performant physical database schema and demonstrate its use in analytical and ML workflows.

### Physical Design

* Designed indexes to optimize:

  * Join-heavy queries
  * Date range filtering
  * Aggregations for analytics
* Implemented a **materialized view** (`policy_claim_summary`) to accelerate ML feature generation

### Machine Learning Workflow

* Generated a synthetic but semantically realistic insurance dataset (~20,000 records)
* Engineered features from policy, customer, and behavioral data
* Trained and evaluated:

  * Logistic Regression (baseline)
  * Random Forest (nonlinear model)
* Demonstrated realistic performance with meaningful AUC separation

📄 **Documentation:** See *Part III Report* in `docs/` for SQL definitions, indexing strategy, ML results, and evaluation plots.

---
## Part IV – End-to-end Application

Goal: Operationalize the data architecture and machine learning pipeline into a fully functional, end-to-end underwriting application that supports real-time, data-driven decision making.

System Overview

In Part IV, the project transitions from offline analytics to a deployable application layer. A trained machine learning model is embedded within an interactive web application that enables users to submit underwriting requests, receive real-time risk assessments, and persist decisions to an operational datastore.

The system integrates the following components:

Application Layer:
A Streamlit-based web interface for submitting insurance quote or policy update requests and visualizing prediction results.

Machine Learning Layer:
A trained Random Forest classification model serialized as a versioned artifact (joblib) and loaded at runtime to predict claim likelihood.

Data Persistence Layer:
MongoDB Atlas is used as an online operational database to store underwriting decisions, predicted risk scores, and input feature snapshots for auditing and future analysis.

End-to-End Workflow

A user submits an underwriting request through the Streamlit interface.

Input features are validated and aligned with the training schema.

The machine learning model predicts the probability of a future insurance claim.

The probability is mapped to a business-level risk tier (Low, Medium, High).

The system applies decision logic:

Low / Medium risk → automatic approval

High risk → escalation to manual review

The final decision and associated metadata are persisted to MongoDB Atlas.

This workflow demonstrates how enterprise data modeling, physical database design, and machine learning can be integrated into a cohesive, production-style system.


📄 **Documentation:** See *Part IV Report* in `docs/` for architectural synthesis and reflections.

---

## 🚀 How to Reproduce (Core Components)

1. Place raw datasets in:

   ```
   data_lake/raw/
   ```
2. Run preprocessing:

   ```bash
   python scripts/raw_data_conversion.py
   ```
3. Load processed CSVs into your relational database following the logical schema
4. Apply physical indexes and materialized views as defined in Part III

---

## 📎 Notes

* All reports reflect **independent work** completed by the author.
* Datasets are derived from publicly available CDC sources.
* The project is intentionally modular to mirror real-world enterprise data systems.

---

## 📫 Contact

For questions regarding the project structure or design decisions, please refer to the detailed reports in the `docs/` directory.
