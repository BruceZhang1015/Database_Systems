CREATE SCHEMA insurance;
CREATE TABLE insurance.customer (
    customer_id        SERIAL PRIMARY KEY,
    first_name         VARCHAR(50),
    last_name          VARCHAR(50),
    age                INT CHECK (age >= 0),
    gender             VARCHAR(20),
    marital_status     VARCHAR(20),
    region             VARCHAR(50),
    income             DECIMAL(12,2),
    credit_score       INT CHECK (credit_score BETWEEN 300 AND 850),
    employment_status  VARCHAR(50)
);
CREATE TABLE insurance.policy (
    policy_id         SERIAL PRIMARY KEY,
    customer_id       INT NOT NULL REFERENCES insurance.customer(customer_id),
    policy_type       VARCHAR(50),
    premium           DECIMAL(12,2) NOT NULL,
    coverage_amount   DECIMAL(12,2),
    deductible        DECIMAL(12,2),
    policy_start_date DATE NOT NULL,
    policy_end_date   DATE,
    policy_status     VARCHAR(20)
);
CREATE TABLE insurance.claim (
    claim_id        SERIAL,
    policy_id       INT NOT NULL REFERENCES insurance.policy(policy_id),
    claim_date      DATE NOT NULL,
    claim_amount    DECIMAL(12,2),
    claim_type      VARCHAR(50),
    severity_level  INT CHECK (severity_level BETWEEN 1 AND 5),
    description_text TEXT,
    PRIMARY KEY (claim_id, claim_date)
) PARTITION BY RANGE (claim_date);

CREATE TABLE insurance.claim_2024
    PARTITION OF insurance.claim
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE insurance.claim_2025
    PARTITION OF insurance.claim
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE insurance.behavior_metrics (
    customer_id            INT PRIMARY KEY REFERENCES insurance.customer(customer_id),
    engagement_score       INT CHECK (engagement_score BETWEEN 0 AND 100),
    mobile_app_logins      INT,
    response_time_minutes  INT,
    risk_zone              INT CHECK (risk_zone BETWEEN 1 AND 5)
);
CREATE INDEX idx_policy_customer_id
ON insurance.policy(customer_id);

CREATE INDEX idx_claim_policy_id
ON insurance.claim(policy_id);

CREATE INDEX idx_claim_date
ON insurance.claim(claim_date);

CREATE MATERIALIZED VIEW insurance.daily_claim_summary AS
SELECT
    claim_date,
    COUNT(*)     AS total_claims,
    SUM(claim_amount) AS total_claim_amount
FROM insurance.claim
GROUP BY claim_date;

INSERT INTO insurance.customer
(first_name, last_name, age, gender, marital_status, region, income, credit_score, employment_status)
VALUES
('Alice', 'Chen', 32, 'Female', 'Single', 'New York', 85000.00, 720, 'Employed'),
('Bob', 'Martinez', 45, 'Male', 'Married', 'California', 120000.00, 690, 'Employed'),
('Carol', 'Wong', 29, 'Female', 'Single', 'Texas', 68000.00, 650, 'Self-Employed'),
('Daniel', 'Kim', 52, 'Male', 'Married', 'Illinois', 135000.00, 780, 'Employed'),
('Eva', 'Lopez', 40, 'Female', 'Married', 'Florida', 90000.00, 710, 'Employed'),
('Frank', 'Ng', 37, 'Male', 'Single', 'Washington', 75000.00, 640, 'Unemployed'),
('Grace', 'Patel', 50, 'Female', 'Widowed', 'New Jersey', 100000.00, 770, 'Employed'),
('Henry', 'Smith', 28, 'Male', 'Single', 'Nevada', 60000.00, 610, 'Student'),
('Isabella', 'Rossi', 34, 'Female', 'Married', 'Colorado', 80000.00, 730, 'Employed'),
('Jason', 'Liu', 47, 'Male', 'Married', 'Massachusetts', 110000.00, 690, 'Employed');

INSERT INTO insurance.policy
(customer_id, policy_type, premium, coverage_amount, deductible, policy_start_date, policy_end_date, policy_status)
VALUES
(1, 'Auto', 120.00, 50000, 500, '2023-01-10', NULL, 'Active'),
(2, 'Home', 95.00, 350000, 1000, '2022-05-01', NULL, 'Active'),
(3, 'Auto', 140.00, 60000, 750, '2023-03-15', NULL, 'Active'),
(4, 'Life', 200.00, 250000, 0, '2020-07-20', NULL, 'Active'),
(5, 'Auto', 110.00, 45000, 500, '2022-11-11', NULL, 'Active'),
(6, 'Auto', 175.00, 40000, 1000, '2023-02-01', NULL, 'Active'),
(7, 'Home', 130.00, 500000, 1500, '2021-09-12', NULL, 'Active'),
(8, 'Auto', 105.00, 30000, 500, '2023-05-01', NULL, 'Active'),
(9, 'Health', 220.00, 1000000, 100, '2019-10-01', NULL, 'Active'),
(10, 'Auto', 150.00, 55000, 750, '2023-01-30', NULL, 'Active');

INSERT INTO insurance.claim
(policy_id, claim_date, claim_amount, claim_type, severity_level, description_text)
VALUES
(1, '2024-02-15', 3200.00, 'Collision', 3, 'Rear-end collision at traffic light'),
(1, '2024-06-10', 1500.00, 'Windshield', 1, 'Rock chip cracked windshield'),
(3, '2024-03-21', 8000.00, 'Collision', 4, 'Side impact during lane change'),
(5, '2024-09-01', 2200.00, 'Theft', 2, 'Car stereo stolen overnight'),
(10,'2025-01-12', 5000.00, 'Collision', 3, 'Minor accident in parking lot'),
(2, '2024-05-18', 12000.00, 'Fire', 5, 'Kitchen fire caused structural damage'),
(7, '2024-11-30', 9000.00, 'Water Damage', 4, 'Basement pipe burst due to freezing'),
(9, '2024-04-03', 1500.00, 'Medical', 2, 'Emergency room visit for injury');

INSERT INTO insurance.behavior_metrics
(customer_id, engagement_score, mobile_app_logins, response_time_minutes, risk_zone)
VALUES
(1, 75, 22, 45, 2),
(2, 82, 18, 30, 1),
(3, 60, 5, 120, 3),
(4, 88, 25, 20, 1),
(5, 69, 10, 75, 2),
(6, 40, 2, 180, 4),
(7, 95, 30, 15, 1),
(8, 55, 8, 200, 3),
(9, 78, 17, 40, 2),
(10, 65, 11, 90, 2);

REFRESH MATERIALIZED VIEW insurance.daily_claim_summary;
