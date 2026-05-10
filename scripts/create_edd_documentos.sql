-- ============================================================
--  EDD DOCUMENTS — evidence attached to each checklist item
-- ============================================================

CREATE TABLE IF NOT EXISTS edd_documentos (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    edd_case_id     UUID        NOT NULL REFERENCES edd_cases(id) ON DELETE CASCADE,
    checklist_item  TEXT        NOT NULL,   -- e.g. 'source_funds', 'source_wealth'
    nome_arquivo    TEXT        NOT NULL,
    storage_path    TEXT        NOT NULL,   -- path inside 'edd-docs' bucket
    content_type    TEXT,
    tamanho_bytes   BIGINT,
    nota            TEXT,
    uploaded_por    TEXT        NOT NULL,
    uploaded_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_edd_docs_case ON edd_documentos(edd_case_id);
CREATE INDEX IF NOT EXISTS idx_edd_docs_item ON edd_documentos(edd_case_id, checklist_item);

-- ── VERIFY ────────────────────────────────────────────────────
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'edd_documentos'
ORDER BY ordinal_position;
