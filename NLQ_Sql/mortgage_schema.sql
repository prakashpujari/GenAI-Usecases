-- Sample schema for a mortgage application PostgreSQL database

CREATE TABLE applicants (
    applicant_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    ssn VARCHAR(11) UNIQUE,
    email VARCHAR(255),
    phone VARCHAR(20)
);

CREATE TABLE properties (
    property_id SERIAL PRIMARY KEY,
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    value NUMERIC(15,2)
);

CREATE TABLE mortgage_applications (
    application_id SERIAL PRIMARY KEY,
    applicant_id INTEGER REFERENCES applicants(applicant_id),
    property_id INTEGER REFERENCES properties(property_id),
    application_date DATE,
    status VARCHAR(50), -- e.g., 'approved', 'pending', 'rejected'
    loan_amount NUMERIC(15,2),
    interest_rate NUMERIC(5,2),
    term_months INTEGER,
    approval_date DATE
);
