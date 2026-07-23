-- Demo 04 — synthetic sales schema + read-only role for the assistant
-- All data fabricated.

CREATE TABLE campaigns (
  campaign_id   serial PRIMARY KEY,
  campaign_name text NOT NULL,
  channel       text NOT NULL          -- 'paid_search' | 'paid_social' | 'email' | 'organic'
);

CREATE TABLE daily_performance (
  perf_date    date    NOT NULL,
  campaign_id  int     NOT NULL REFERENCES campaigns(campaign_id),
  revenue      numeric(12,2) NOT NULL DEFAULT 0,
  spend        numeric(12,2) NOT NULL DEFAULT 0,
  leads        int     NOT NULL DEFAULT 0,
  PRIMARY KEY (perf_date, campaign_id)   -- re-runs can't double-load
);

INSERT INTO campaigns (campaign_name, channel) VALUES
  ('Spring Promo',    'paid_search'),
  ('Spring Promo',    'paid_social'),
  ('Brand Always-On', 'paid_search'),
  ('Newsletter Q3',   'email');

-- 8 weeks of plausible synthetic dailies for each campaign
INSERT INTO daily_performance (perf_date, campaign_id, revenue, spend, leads)
SELECT d::date,
       c.campaign_id,
       round((300 + random()*400 + extract(dow from d)*40)::numeric, 2),
       round((80  + random()*90)::numeric, 2),
       (5 + floor(random()*12))::int
FROM generate_series(current_date - interval '56 days', current_date - interval '1 day', '1 day') AS d
CROSS JOIN campaigns c;

-- The assistant connects as this role: SELECT-only, defense in depth
CREATE ROLE ai_readonly LOGIN PASSWORD 'change-me';
GRANT CONNECT ON DATABASE postgres TO ai_readonly;
GRANT USAGE ON SCHEMA public TO ai_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ai_readonly;
