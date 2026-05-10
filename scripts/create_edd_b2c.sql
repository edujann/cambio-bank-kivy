-- ============================================================
--  EDD B2C — Enhanced Due Diligence for retail customers
-- ============================================================

CREATE TABLE IF NOT EXISTS edd_cases_b2c (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    ordem_id        UUID        NOT NULL REFERENCES ordens_captacao(id) ON DELETE CASCADE,
    cliente_id      UUID        NOT NULL REFERENCES clientes_varejo(id) ON DELETE CASCADE,

    -- Triggers that caused this EDD (array of strings)
    trigger_reasons JSONB       NOT NULL DEFAULT '[]',

    -- Workflow
    status          TEXT        NOT NULL DEFAULT 'aberto',
    -- aberto | em_analise | aprovado | rejeitado

    prioridade      TEXT        NOT NULL DEFAULT 'medium',
    -- low | medium | high | critical

    -- Checklist (per-item: status, nota, doc_id, verificado_por, verificado_em)
    checklist       JSONB       NOT NULL DEFAULT '{}',

    -- PEP flag snapshot at time of EDD creation
    requer_mlro     BOOLEAN     NOT NULL DEFAULT FALSE,

    -- Notes
    notas           TEXT,

    -- Creation
    criado_por      TEXT        NOT NULL DEFAULT 'sistema',
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em   TIMESTAMPTZ,

    -- Resolution
    aprovado_por    TEXT,
    aprovado_em     TIMESTAMPTZ,
    aprovacao_nota  TEXT,

    -- Periodic monitoring
    proxima_revisao DATE,
    tipo_revisao    TEXT        -- 'mensal' | 'trimestral'
);

CREATE INDEX IF NOT EXISTS idx_edd_b2c_ordem    ON edd_cases_b2c(ordem_id);
CREATE INDEX IF NOT EXISTS idx_edd_b2c_cliente  ON edd_cases_b2c(cliente_id);
CREATE INDEX IF NOT EXISTS idx_edd_b2c_status   ON edd_cases_b2c(status);

-- ============================================================
--  EDD B2C DOCUMENTS — evidence per checklist item
-- ============================================================

CREATE TABLE IF NOT EXISTS edd_b2c_documentos (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    edd_case_id     UUID        NOT NULL REFERENCES edd_cases_b2c(id) ON DELETE CASCADE,
    checklist_item  TEXT        NOT NULL,
    nome_arquivo    TEXT        NOT NULL,
    storage_path    TEXT        NOT NULL,
    content_type    TEXT,
    tamanho_bytes   BIGINT,
    nota            TEXT,
    uploaded_por    TEXT        NOT NULL,
    uploaded_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_edd_b2c_docs_case ON edd_b2c_documentos(edd_case_id);
CREATE INDEX IF NOT EXISTS idx_edd_b2c_docs_item ON edd_b2c_documentos(edd_case_id, checklist_item);

-- ── VERIFY ────────────────────────────────────────────────────
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'edd_cases_b2c'
ORDER BY ordinal_position;
