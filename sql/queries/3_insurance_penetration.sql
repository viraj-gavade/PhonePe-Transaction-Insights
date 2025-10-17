-- State-wise insurance totals
CREATE OR REPLACE VIEW view_insurance_state_totals AS
SELECT state,
       SUM(amount) AS total_insurance_amount,
       SUM(count) AS total_insurance_count
FROM aggregated_insurance
GROUP BY state
ORDER BY total_insurance_amount DESC;

-- Quarterly insurance trends
SELECT state, year, quarter,
       SUM(amount) AS total_amount
FROM aggregated_insurance
GROUP BY state, year, quarter
ORDER BY state, year, quarter;
