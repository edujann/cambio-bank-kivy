-- ============================================================
--  CORREÇÕES — paises_risco
--  Baseado na verificação: corrige países que já existiam
--  no banco com classificações incorretas
-- ============================================================

-- ── 1. SANCTIONED — promover países que estavam como 'high' ──
UPDATE paises_risco SET risco = 'sanctioned', bloqueado = true
WHERE codigo IN ('BY', 'IR', 'MM', 'SY');

-- ── 2. SUDAN — bloquear (high já está correto, só falta o block)
UPDATE paises_risco SET bloqueado = true
WHERE codigo = 'SD';

-- ── 3. RECLASSIFICAR — países standard que estavam como high ─
UPDATE paises_risco SET risco = 'standard'
WHERE codigo IN (
    'TH',  -- Thailand   (estável, parceiro comercial)
    'JO',  -- Jordan     (estável, coopera com FATF)
    'SA'   -- Saudi Arabia (estável, parceiro)
);

-- ── 4. CORRIGIR CONTINENTES — novos países inseridos com
--      continente errado ('Americas' → granular correto) ──────
UPDATE paises_risco SET continente = 'North America'
WHERE codigo IN ('CA', 'US', 'MX');

UPDATE paises_risco SET continente = 'Caribbean'
WHERE codigo IN ('AG','BB','BS','CU','DM','DO','GD','JM','KN','LC','TT','VC');

UPDATE paises_risco SET continente = 'Central America'
WHERE codigo IN ('BZ','CR','GT','HN','NI','PA','SV');

UPDATE paises_risco SET continente = 'South America'
WHERE codigo IN ('AR','BO','BR','CL','CO','EC','GY','PE','PY','SR','UY','VE');

UPDATE paises_risco SET continente = 'Middle East'
WHERE codigo IN ('AE','BH','IL','IQ','IR','JO','KW','LB','OM','PS','QA','SA','SY','YE');

-- Ásia pura (sem Oriente Médio)
UPDATE paises_risco SET continente = 'Asia'
WHERE codigo IN (
    'AF','AM','AZ','BD','BN','BT','GE','ID','IN','JP','KG','KH','KP',
    'KR','KZ','LA','LK','MM','MN','MY','NP','PH','PK','SG','TJ','TL',
    'TM','TR','TW','UZ','VN'
);

-- ── 5. VERIFICAÇÃO FINAL ──────────────────────────────────────
-- Rode após o UPDATE para confirmar:

SELECT risco, COUNT(*) AS total,
       COUNT(*) FILTER (WHERE bloqueado) AS bloqueados
FROM paises_risco
GROUP BY risco
ORDER BY CASE risco
    WHEN 'low' THEN 1 WHEN 'standard' THEN 2
    WHEN 'medium' THEN 3 WHEN 'high' THEN 4
    WHEN 'sanctioned' THEN 5 ELSE 6 END;

SELECT codigo, nome, risco, bloqueado, continente
FROM paises_risco
WHERE risco = 'sanctioned' OR bloqueado = true
ORDER BY continente, nome;
