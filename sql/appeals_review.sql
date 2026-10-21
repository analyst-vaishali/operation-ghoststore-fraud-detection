-- Operation GhostStore - Trust & Safety SQL Analysis
-- Database: trust_safety_risk

-- 1. Find banned sellers creating ghost stores (using LAG)
USE trust_safety_risk;
SELECT seller_id, violation_date, 
  LAG(violation_date) OVER (PARTITION BY seller_id ORDER BY violation_date) as prev_violation,
  DATEDIFF(violation_date, LAG(violation_date) OVER (PARTITION BY seller_id ORDER BY violation_date)) as days_between
FROM violations
ORDER BY seller_id, violation_date;

-- 2. Count total ghost names per real seller
SELECT s.seller_name, COUNT(*) as ghost_count
FROM sellers s
JOIN violations v ON s.seller_id = v.seller_id
WHERE v.is_ghost = 1
GROUP BY s.seller_name
ORDER BY ghost_count DESC;

-- 3. Pending appeals that need review (Your screenshot - MOST important for AHS)
SELECT
  a.appeal_id,
  v.seller_id,
  s.seller_name,
  a.appeal_date,
  a.appeal_status,
  DATEDIFF(CURDATE(), a.appeal_date) as days_pending
FROM appeals a
JOIN violations v ON a.violation_id = v.violation_id
JOIN sellers s ON v.seller_id = s.seller_id
WHERE a.appeal_status = 'Pending';
