-- State-wise quarterly transaction trends
CREATE OR REPLACE VIEW view_state_quarter_trends AS
SELECT state, year, quarter,
       SUM(amount) AS total_amount,
       SUM(count) AS total_count
FROM aggregated_transaction
GROUP BY state, year, quarter
ORDER BY state, year, quarter;

-- Top 10 states by total transaction amount
SELECT state, SUM(amount) AS total_amount
FROM aggregated_transaction
GROUP BY state
ORDER BY total_amount DESC
LIMIT 10;
