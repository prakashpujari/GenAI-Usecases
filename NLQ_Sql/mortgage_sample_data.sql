-- Sample data for mortgage application demo

INSERT INTO applicants (first_name, last_name, date_of_birth, ssn, email, phone) VALUES
('Alice', 'Smith', '1985-04-12', '123-45-6789', 'alice.smith@example.com', '555-1234'),
('Bob', 'Johnson', '1978-09-23', '987-65-4321', 'bob.johnson@example.com', '555-5678');

INSERT INTO properties (address, city, state, zip_code, value) VALUES
('123 Main St', 'Springfield', 'IL', '62704', 250000.00),
('456 Oak Ave', 'Springfield', 'IL', '62704', 320000.00);

INSERT INTO mortgage_applications (applicant_id, property_id, application_date, status, loan_amount, interest_rate, term_months, approval_date) VALUES
(1, 1, '2024-03-01', 'approved', 200000.00, 4.5, 360, CURRENT_DATE - INTERVAL '10 days'),
(2, 2, '2024-02-15', 'pending', 250000.00, 5.0, 180, NULL),
(1, 2, '2024-04-01', 'approved', 300000.00, 4.2, 360, CURRENT_DATE - INTERVAL '20 days');
