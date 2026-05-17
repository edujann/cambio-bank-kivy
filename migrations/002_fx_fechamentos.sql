-- Migration 002: FX Fechamentos & Coberturas
-- Run in Supabase SQL Editor

-- Tabela de fechamentos (acordos comerciais com parceiros)
CREATE TABLE IF NOT EXISTS fx_fechamentos (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    executado_por   TEXT NOT NULL,
    parceiro_username TEXT NOT NULL,
    taxa_usd_brl    NUMERIC(12,6) NOT NULL,
    valor_usd_estimado NUMERIC(18,4) NOT NULL,
    taxa_gbp_brl_real  NUMERIC(12,6),
    status          TEXT NOT NULL DEFAULT 'aberto',
    observacoes     TEXT,
    CONSTRAINT fx_fechamentos_status_chk CHECK (status IN ('aberto', 'coberto', 'fechado'))
);

-- Tabela de coberturas (compras de USD do banco para cobrir fechamentos)
CREATE TABLE IF NOT EXISTS fx_coberturas (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT now(),
    fechamento_id   UUID REFERENCES fx_fechamentos(id),
    tipo            TEXT NOT NULL DEFAULT 'compra_banco',
    valor_usd       NUMERIC(18,4) NOT NULL,
    valor_gbp       NUMERIC(18,4) NOT NULL,
    taxa_gbp_usd    NUMERIC(12,6) NOT NULL,
    conta_debitada  TEXT,
    conta_creditada TEXT,
    executado_por   TEXT NOT NULL,
    observacoes     TEXT,
    pool_compra_id  UUID
);

-- Colunas FX em despachos (vinculo, valor GBP e P&L por despacho)
ALTER TABLE despachos ADD COLUMN IF NOT EXISTS fechamento_id  UUID REFERENCES fx_fechamentos(id);
ALTER TABLE despachos ADD COLUMN IF NOT EXISTS valor_gbp      NUMERIC(18,4);
ALTER TABLE despachos ADD COLUMN IF NOT EXISTS taxa_gbp_brl   NUMERIC(12,6);
ALTER TABLE despachos ADD COLUMN IF NOT EXISTS lucro_gbp      NUMERIC(18,4);
ALTER TABLE despachos ADD COLUMN IF NOT EXISTS lucro_brl      NUMERIC(18,4);

-- Índices úteis
CREATE INDEX IF NOT EXISTS idx_fx_cob_fechamento ON fx_coberturas(fechamento_id);
CREATE INDEX IF NOT EXISTS idx_despachos_fechamento ON despachos(fechamento_id);
