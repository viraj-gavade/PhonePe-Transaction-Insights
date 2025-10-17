-- Top states
SELECT state, SUM(amount) AS total_amount
FROM aggregated_transaction
GROUP BY state
ORDER BY total_amount DESC
LIMIT 10;

-- Top districts
SELECT state, district, SUM(amount) AS total_amount
FROM map_transaction
GROUP BY state, district
ORDER BY total_amount DESC
LIMIT 10;

-- Top pincodes
SELECT entity_name AS pincode, SUM(amount) AS total_amount
FROM top_transaction
WHERE entity_type ILIKE '%pincode%' OR entity_type ILIKE '%pincodes%'
GROUP BY entity_name
ORDER BY total_amount DESC
LIMIT 10;
