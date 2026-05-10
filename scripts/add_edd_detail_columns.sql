-- ============================================================
--  EDD CASE DETAIL — additional columns
-- ============================================================

ALTER TABLE edd_cases
    ADD COLUMN IF NOT EXISTS checklist      JSONB         DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS aprovado_por   TEXT,
    ADD COLUMN IF NOT EXISTS aprovado_em    TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS aprovacao_nota TEXT;

-- ── VERIFY ────────────────────────────────────────────────────
SELECT id, status, checklist, aprovado_por, aprovado_em
FROM edd_cases
LIMIT 5;
