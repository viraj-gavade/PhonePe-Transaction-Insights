-- Device dominance and engagement
CREATE OR REPLACE VIEW view_device_engagement AS
SELECT brand_name,
       SUM(registered_users) AS total_registered_users,
       SUM(app_opens) AS total_app_opens
FROM aggregated_user
GROUP BY brand_name
ORDER BY total_registered_users DESC;

-- Device usage ratio (app opens / registered users)
SELECT brand_name,
       SUM(registered_users) AS total_registered_users,
       SUM(app_opens) AS total_app_opens,
       ROUND(SUM(app_opens)::numeric / NULLIF(SUM(registered_users),0), 2) AS engagement_ratio
FROM aggregated_user
GROUP BY brand_name
ORDER BY engagement_ratio DESC;
