-- Migration 004: Despacho ↔ Fechamentos (N:M allocation)
-- Run in Supabase SQL Editor

-- Tabela de alocação: um despacho pode consumir N fechamentos (FIFO)
CREATE TABLE IF NOT EXISTS despacho_fechamentos (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT now(),
    despacho_id     UUID NOT NULL REFERENCES despachos(id),
    fechamento_id   UUID NOT NULL REFERENCES fx_fechamentos(id),
    valor_usd       NUMERIC(18,4) NOT NULL,
    valor_brl       NUMERIC(18,4) NOT NULL,
    UNIQUE(despacho_id, fechamento_id)
);

CREATE INDEX IF NOT EXISTS idx_desp_fech_despacho   ON despacho_fechamentos(despacho_id);
CREATE INDEX IF NOT EXISTS idx_desp_fech_fechamento ON despacho_fechamentos(fechamento_id);

-- Migrar despachos existentes que já tinham fechamento_id
INSERT INTO despacho_fechamentos (despacho_id, fechamento_id, valor_usd, valor_brl)
SELECT
    d.id,
    d.fechamento_id,
    ROUND(d.valor_total / NULLIF(f.taxa_usd_brl, 0), 4),
    d.valor_total
FROM despachos d
JOIN fx_fechamentos f ON f.id = d.fechamento_id
WHERE d.fechamento_id IS NOT NULL
ON CONFLICT (despacho_id, fechamento_id) DO NOTHING;
