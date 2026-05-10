-- ============================================================
--  ADD PERIODIC REVIEW COLUMNS TO paises_risco
--  FCA MLR 2017: regulated firms must review risk classifications
--  at appropriate intervals based on the jurisdiction's risk level.
-- ============================================================

ALTER TABLE paises_risco
    ADD COLUMN IF NOT EXISTS ultima_revisao  DATE,
    ADD COLUMN IF NOT EXISTS proxima_revisao DATE;

-- Optional index — helps queries filtering overdue reviews
CREATE INDEX IF NOT EXISTS idx_paises_risco_proxima_revisao
    ON paises_risco (proxima_revisao)
    WHERE proxima_revisao IS NOT NULL;

-- ── VERIFY ────────────────────────────────────────────────────
SELECT
    COUNT(*)                                          AS total,
    COUNT(*) FILTER (WHERE ultima_revisao  IS NOT NULL) AS com_ultima_revisao,
    COUNT(*) FILTER (WHERE proxima_revisao IS NOT NULL) AS com_proxima_revisao,
    COUNT(*) FILTER (WHERE proxima_revisao < CURRENT_DATE) AS vencidas
FROM paises_risco;
