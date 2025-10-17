-- Top states by user registration
SELECT state,
       SUM(registered_users) AS total_registered_users
FROM aggregated_user
GROUP BY state
ORDER BY total_registered_users DESC
LIMIT 10;

-- Quarterly registration trends
SELECT state, year, quarter,
       SUM(registered_users) AS total_registered_users
FROM aggregated_user
GROUP BY state, year, quarter
ORDER BY state, year, quarter;
