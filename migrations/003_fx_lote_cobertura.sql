-- Migration 003: Lote de Cobertura (multi-fechamento allocation)
-- Run in Supabase SQL Editor

-- Agrupa coberturas do mesmo lote bancário (1 compra → N alocações)
ALTER TABLE fx_coberturas ADD COLUMN IF NOT EXISTS lote_cobertura_id UUID;
CREATE INDEX IF NOT EXISTS idx_fx_cob_lote ON fx_coberturas(lote_cobertura_id);
