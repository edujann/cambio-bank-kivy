-- ============================================================
--  Add purpose_of_remittance to ordens_captacao
-- ============================================================

ALTER TABLE ordens_captacao
    ADD COLUMN IF NOT EXISTS purpose_of_remittance TEXT;

-- ── VERIFY ────────────────────────────────────────────────────
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'ordens_captacao'
  AND column_name = 'purpose_of_remittance';
