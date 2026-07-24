# Snowflake & DBT Module Documentation

## Project
MetricMind – Agentic Semantic BI Engine

## Developer
Lakshmi Poojitha

## Module
Snowflake & DBT

---

# 1. Objective

The objective of this module is to build a reliable and governed data transformation pipeline using Snowflake and dbt. The pipeline prepares clean and validated business data for the Semantic Layer and downstream analytics.

---

# 2. Technology Stack

- Snowflake
- dbt Core 1.12
- SQL
- Git
- GitHub

---

# 3. Snowflake Setup

### Database

METRICMIND_DB

### Schema

RETAIL

### Warehouse

COMPUTE_WH

### Role

CUBE_READ_ROLE

### User

cube_user

---

# 4. Dataset Upload

Dataset:
Global Superstore Dataset

Table Created:

SUPERSTORE

Total Records Loaded:

51290

The dataset was uploaded successfully into Snowflake and verified.

---

# 5. Data Cleaning

A cleaned dataset was created.

Source Table:

SUPERSTORE

↓

Cleaned Table:

SUPERSTORE_CLEANED

Cleaning activities performed:

- Standardized data types
- Removed unnecessary formatting issues
- Verified row count
- Prepared data for dbt transformations

Rows after cleaning:

51290

---

# 6. DBT Project Setup

Configured:

- dbt Project
- profiles.yml
- dbt_project.yml
- Snowflake Connection

Project Structure

```
metricmind_dbt
│
├── models
│   ├── staging
│   └── marts
│
├── macros
├── tests
├── seeds
├── snapshots
└── dbt_project.yml
```

---

# 7. Source Configuration

Created

sources.yml

Source

SUPERSTORE_CLEANED

Database

METRICMIND_DB

Schema

RETAIL

---

# 8. Staging Layer

Model

STG_SUPERSTORE

Materialization

View

Purpose

- Read source data
- Rename columns
- Standardize field names
- Prepare data for marts

---

# 9. Mart Layer

Model

SALES_SUMMARY

Materialization

Table

Purpose

Generate business-ready metrics.

Metrics Generated

- Total Sales
- Total Profit
- Total Quantity
- Total Shipping Cost
- Total Orders

Grouped By

- Region
- Category

---

# 10. DBT Execution

Commands Executed

```bash
dbt clean
dbt parse
dbt run
dbt test
```

Execution Summary

Models Built:

- STG_SUPERSTORE
- SALES_SUMMARY

Data Tests:

8

Passed:

8

Failed:

0

Warnings:

0

---

# 11. Governance Audit

## Row Count Validation

SUPERSTORE_CLEANED

Rows:

51290

↓

STG_SUPERSTORE

Rows:

51290

Result

No data loss observed.

---

## Business Metric Validation

Raw Dataset

SUM(Sales)

12642905.00

↓

Mart Dataset

SUM(total_sales)

12642905.00

Result

Business metrics matched successfully.

---

# 12. Bug Fixes

Completed

- Configured Snowflake connection
- Fixed dbt source configuration
- Configured sources.yml
- Configured schema.yml
- Updated dbt_project.yml
- Removed default example models
- Implemented source() macro
- Implemented ref() macro
- Fixed model dependency issues
- Validated Snowflake objects
- Verified successful execution of all dbt models

---

# 13. GitHub Updates

Completed

- Created DBT project
- Added staging models
- Added mart models
- Added schema files
- Added source configuration
- Updated project configuration
- Pushed all changes to GitHub

Branch

main

---

# 14. Final Deliverables

Completed

- Snowflake Setup
- Dataset Upload
- Data Cleaning
- DBT Configuration
- Source Configuration
- Staging Model
- Mart Model
- DBT Testing
- Governance Audit
- Bug Fixing
- GitHub Integration

---

# 15. Conclusion

The Snowflake and DBT module was successfully implemented for the MetricMind project. The complete data pipeline—from dataset upload and cleaning to transformation, testing, governance validation, and GitHub integration—was completed successfully. The transformed data is now ready for integration with the Cube Semantic Layer and downstream analytics components.
