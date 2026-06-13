-- RevOps KPI model + dashboard queries (demo)
-- Standard SQL; runs on PostgreSQL. Source tables are synthetic.
-- One fact table at (day, channel) grain so every KPI reconciles.

-- ---------------------------------------------------------------------------
-- 0. Source tables (in production: loaded by the attribution pipeline / CRM sync)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ad_spend  (day date, channel text, spend numeric);
CREATE TABLE IF NOT EXISTS signups   (day date, channel text, new_customers int);
CREATE TABLE IF NOT EXISTS revenue   (day date, channel text, revenue numeric);

-- ---------------------------------------------------------------------------
-- 1. The one fact table everything reads from
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW fct_daily_channel AS
SELECT
    COALESCE(s.day, su.day, r.day)             AS day,
    COALESCE(s.channel, su.channel, r.channel) AS channel,
    COALESCE(s.spend, 0)                       AS spend,
    COALESCE(su.new_customers, 0)              AS new_customers,
    COALESCE(r.revenue, 0)                     AS revenue
FROM ad_spend s
FULL OUTER JOIN signups su ON s.day = su.day AND s.channel = su.channel
FULL OUTER JOIN revenue r  ON COALESCE(s.day, su.day) = r.day
                          AND COALESCE(s.channel, su.channel) = r.channel;

-- ---------------------------------------------------------------------------
-- 2. Channel leaderboard tile: CAC, ROAS, payback (last 30 days)
-- ---------------------------------------------------------------------------
SELECT
    channel,
    SUM(spend)                                              AS spend,
    SUM(new_customers)                                      AS customers,
    ROUND(SUM(spend) / NULLIF(SUM(new_customers), 0), 2)    AS cac,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2)          AS roas,
    -- payback months = CAC / monthly revenue per customer
    ROUND(
        (SUM(spend) / NULLIF(SUM(new_customers), 0))
        / NULLIF(SUM(revenue) / NULLIF(SUM(new_customers), 0), 0), 1
    )                                                       AS payback_months
FROM fct_daily_channel
WHERE day >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY channel
ORDER BY roas DESC NULLS LAST;

-- ---------------------------------------------------------------------------
-- 3. Daily ROAS trend (line chart)
-- ---------------------------------------------------------------------------
SELECT
    day,
    channel,
    ROUND(revenue / NULLIF(spend, 0), 2) AS roas
FROM fct_daily_channel
WHERE day >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY day, channel;

-- ---------------------------------------------------------------------------
-- 4. Blended top-line tiles (CAC, ROAS, LTV:CAC)
-- ---------------------------------------------------------------------------
WITH agg AS (
    SELECT SUM(spend) AS spend, SUM(new_customers) AS customers, SUM(revenue) AS revenue
    FROM fct_daily_channel
    WHERE day >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
    ROUND(spend / NULLIF(customers, 0), 2)                       AS blended_cac,
    ROUND(revenue / NULLIF(spend, 0), 2)                         AS blended_roas,
    -- simple blended LTV proxy: revenue per acquired customer
    ROUND(revenue / NULLIF(customers, 0), 2)                     AS ltv_proxy,
    ROUND((revenue / NULLIF(customers, 0))
          / NULLIF(spend / NULLIF(customers, 0), 0), 2)          AS ltv_to_cac
FROM agg;

-- ---------------------------------------------------------------------------
-- 5. Alert query: channels whose CAC rose >20% week-over-week
-- ---------------------------------------------------------------------------
WITH wk AS (
    SELECT channel,
           date_trunc('week', day) AS wk,
           SUM(spend) / NULLIF(SUM(new_customers), 0) AS cac
    FROM fct_daily_channel
    GROUP BY channel, date_trunc('week', day)
)
SELECT cur.channel, prev.cac AS cac_prev_week, cur.cac AS cac_this_week,
       ROUND((cur.cac - prev.cac) / NULLIF(prev.cac, 0) * 100, 1) AS pct_change
FROM wk cur
JOIN wk prev ON cur.channel = prev.channel
            AND cur.wk = prev.wk + INTERVAL '1 week'
WHERE cur.cac > prev.cac * 1.20
ORDER BY pct_change DESC;
