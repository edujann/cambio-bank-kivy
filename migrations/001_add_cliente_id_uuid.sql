-- ============================================================
-- MIGRAÇÃO 001 — Adicionar cliente_id (UUID) nas tabelas FK
-- Executar no Supabase SQL Editor
-- ============================================================
-- OBJETIVO: substituir cliente_username (string mutável) por
-- cliente_id (UUID imutável) como chave estrangeira.
-- As colunas _username são mantidas durante a transição.
-- ============================================================

-- 1. ADICIONAR COLUNAS UUID
-- ------------------------------------------------------------

ALTER TABLE contas
    ADD COLUMN IF NOT EXISTS cliente_id UUID;

ALTER TABLE beneficiarios
    ADD COLUMN IF NOT EXISTS cliente_id UUID;

ALTER TABLE chamados
    ADD COLUMN IF NOT EXISTS cliente_id UUID;

ALTER TABLE config_cotacoes
    ADD COLUMN IF NOT EXISTS cliente_id UUID;

ALTER TABLE clientes_b2b
    ADD COLUMN IF NOT EXISTS usuario_id UUID;


-- 2. BACKFILL — popular UUID a partir dos registros existentes
-- ------------------------------------------------------------

UPDATE contas c
SET    cliente_id = u.id
FROM   usuarios u
WHERE  c.cliente_username = u.username
  AND  c.cliente_id IS NULL;

UPDATE beneficiarios b
SET    cliente_id = u.id
FROM   usuarios u
WHERE  b.cliente_username = u.username
  AND  b.cliente_id IS NULL;

UPDATE chamados ch
SET    cliente_id = u.id
FROM   usuarios u
WHERE  ch.cliente_username = u.username
  AND  ch.cliente_id IS NULL;

UPDATE config_cotacoes cc
SET    cliente_id = u.id
FROM   usuarios u
WHERE  cc.cliente_username = u.username
  AND  cc.cliente_id IS NULL;

UPDATE clientes_b2b cb
SET    usuario_id = u.id
FROM   usuarios u
WHERE  cb.usuario_username = u.username
  AND  cb.usuario_id IS NULL;


-- 3. VERIFICAÇÃO — confirmar que o backfill foi completo
-- ------------------------------------------------------------

SELECT 'contas sem cliente_id'         AS tabela, COUNT(*) AS pendentes FROM contas         WHERE cliente_id IS NULL AND cliente_username IS NOT NULL
UNION ALL
SELECT 'beneficiarios sem cliente_id'  AS tabela, COUNT(*) AS pendentes FROM beneficiarios  WHERE cliente_id IS NULL AND cliente_username IS NOT NULL
UNION ALL
SELECT 'chamados sem cliente_id'       AS tabela, COUNT(*) AS pendentes FROM chamados        WHERE cliente_id IS NULL AND cliente_username IS NOT NULL
UNION ALL
SELECT 'config_cotacoes sem cliente_id'AS tabela, COUNT(*) AS pendentes FROM config_cotacoes WHERE cliente_id IS NULL AND cliente_username IS NOT NULL
UNION ALL
SELECT 'clientes_b2b sem usuario_id'   AS tabela, COUNT(*) AS pendentes FROM clientes_b2b   WHERE usuario_id IS NULL AND usuario_username IS NOT NULL;

-- Resultado esperado: todas as linhas com pendentes = 0
-- ============================================================
-- PRÓXIMO PASSO (depois de validar que tudo funciona):
-- Executar migrations/002_drop_username_fks.sql para remover
-- as colunas _username das tabelas (não fazer agora).
-- ============================================================
