-- Top states view
CREATE OR REPLACE VIEW view_top_states AS
SELECT state, SUM(amount) AS total_amount, SUM(count) AS total_count
FROM aggregated_transaction
GROUP BY state
ORDER BY total_amount DESC;

-- District totals view
CREATE OR REPLACE VIEW view_district_totals AS
SELECT state, district, SUM(amount) AS total_amount, SUM(count) AS total_count
FROM map_transaction
GROUP BY state, district
ORDER BY total_amount DESC;

-- Top pincodes view
CREATE OR REPLACE VIEW view_top_pincodes AS
SELECT entity_name AS pincode, SUM(amount) AS total_amount
FROM top_transaction
WHERE entity_type ILIKE '%pincode%' OR entity_type ILIKE '%pincodes%'
GROUP BY entity_name
ORDER BY total_amount DESC;

-- Indexes for speed
CREATE INDEX IF NOT EXISTS idx_agg_state_year_quarter ON aggregated_transaction(state, year, quarter);
CREATE INDEX IF NOT EXISTS idx_map_state_district ON map_transaction(state, district);
CREATE INDEX IF NOT EXISTS idx_top_entity_type ON top_transaction(entity_type);
CREATE INDEX IF NOT EXISTS idx_agg_trx_type ON aggregated_transaction(transaction_type);
