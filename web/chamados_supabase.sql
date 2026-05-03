-- ============================================================
-- SISTEMA DE CHAMADOS B2B - Cambio Bank
-- Execute este SQL no Supabase SQL Editor
-- ============================================================

-- TABELA PRINCIPAL DE CHAMADOS
CREATE TABLE IF NOT EXISTS chamados (
    id TEXT PRIMARY KEY,                          -- ex: CHM-2026-0001
    cliente_username TEXT NOT NULL,
    cliente_nome TEXT,
    titulo TEXT NOT NULL,
    categoria TEXT NOT NULL DEFAULT 'outro',      -- transferencia | cambio | documentacao | financeiro | tecnico | outro
    prioridade TEXT NOT NULL DEFAULT 'normal',    -- baixa | normal | alta | urgente
    status TEXT NOT NULL DEFAULT 'aberto',        -- aberto | em_atendimento | aguardando_cliente | resolvido | fechado
    atribuido_a TEXT,                             -- username do admin responsável
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    sla_deadline TIMESTAMPTZ,
    total_mensagens INT DEFAULT 0
);

-- TABELA DE MENSAGENS (histórico imutável)
CREATE TABLE IF NOT EXISTS chamados_mensagens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chamado_id TEXT NOT NULL REFERENCES chamados(id) ON DELETE CASCADE,
    autor_tipo TEXT NOT NULL,                     -- 'cliente' ou 'admin'
    autor_nome TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    is_nota_interna BOOLEAN DEFAULT FALSE,        -- TRUE = visível só para admin
    lida_admin BOOLEAN DEFAULT FALSE,
    lida_cliente BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ÍNDICES PARA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_chamados_cliente ON chamados(cliente_username);
CREATE INDEX IF NOT EXISTS idx_chamados_status ON chamados(status);
CREATE INDEX IF NOT EXISTS idx_chamados_updated ON chamados(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_mensagens_chamado ON chamados_mensagens(chamado_id);
CREATE INDEX IF NOT EXISTS idx_mensagens_created ON chamados_mensagens(created_at ASC);

-- SLA em horas por prioridade: urgente=2h, alta=8h, normal=24h, baixa=72h
