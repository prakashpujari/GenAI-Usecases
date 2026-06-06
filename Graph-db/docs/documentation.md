# Introduction
The Mortgage Graph Platform is a web application that provides a risk assessment for mortgage loans. The application uses a graph database to store loan data and calculates risk scores based on various factors, including loan-to-value ratio, debt-to-income ratio, and credit history.

# Application Settings
The application settings are defined in the `app/config/settings.py` file. The settings include the project name, environment, logging level, timezone, and database connection settings.

# Risk Calculation
The risk calculation is performed using the `compute_scores` function, which takes into account various factors, including loan-to-value ratio, debt-to-income ratio, and credit history. The function returns a risk score and a network risk score.

# API Endpoints
The application provides several API endpoints for retrieving loan data and calculating risk scores. The endpoints include:
* `GET /loans/{loan_id}/risk`: Returns the risk assessment for a given loan ID.
* `GET /loans/{loan_id}/explain`: Returns an explanation for the risk assessment for a given loan ID.
* `POST /loans/ingest`: Ingests a loan payload into the database.