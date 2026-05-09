-- ============================================================
--  VERIFICAÇÃO DA TABELA paises_risco
-- ============================================================

-- ── 1. TOTAIS POR NÍVEL DE RISCO ─────────────────────────────
SELECT
    risco,
    COUNT(*)                                      AS total,
    COUNT(*) FILTER (WHERE bloqueado = true)      AS bloqueados,
    COUNT(*) FILTER (WHERE bloqueado = false)     AS ativos
FROM paises_risco
GROUP BY risco
ORDER BY
    CASE risco
        WHEN 'low'        THEN 1
        WHEN 'standard'   THEN 2
        WHEN 'medium'     THEN 3
        WHEN 'high'       THEN 4
        WHEN 'sanctioned' THEN 5
        ELSE 6
    END;

-- ── 2. TOTAIS POR CONTINENTE ──────────────────────────────────
SELECT
    COALESCE(continente, '(sem continente)')  AS continente,
    COUNT(*)                                  AS total,
    COUNT(*) FILTER (WHERE risco = 'low')        AS low,
    COUNT(*) FILTER (WHERE risco = 'standard')   AS standard,
    COUNT(*) FILTER (WHERE risco = 'medium')     AS medium,
    COUNT(*) FILTER (WHERE risco = 'high')       AS high,
    COUNT(*) FILTER (WHERE risco = 'sanctioned') AS sanctioned
FROM paises_risco
GROUP BY continente
ORDER BY continente;

-- ── 3. TOTAL GERAL ────────────────────────────────────────────
SELECT COUNT(*) AS total_paises FROM paises_risco;

-- ── 4. INCONSISTÊNCIAS — sanctioned mas NÃO bloqueado ────────
SELECT codigo, nome, risco, bloqueado
FROM paises_risco
WHERE risco = 'sanctioned' AND bloqueado = false
ORDER BY nome;

-- ── 5. INCONSISTÊNCIAS — bloqueado mas risco ≠ sanctioned ─────
SELECT codigo, nome, risco, bloqueado
FROM paises_risco
WHERE bloqueado = true AND risco != 'sanctioned'
ORDER BY nome;

-- ── 6. CAMPOS VAZIOS (nome ou continente nulo/vazio) ──────────
SELECT codigo, nome, nome_nacionalidade, continente, risco
FROM paises_risco
WHERE nome IS NULL OR nome = ''
   OR continente IS NULL OR continente = ''
   OR nome_nacionalidade IS NULL OR nome_nacionalidade = ''
ORDER BY codigo;

-- ── 7. LISTA COMPLETA — países sanctioned/blocked ────────────
SELECT codigo, nome, risco, bloqueado, continente
FROM paises_risco
WHERE risco = 'sanctioned' OR bloqueado = true
ORDER BY continente, nome;

-- ── 8. LISTA COMPLETA — países HIGH RISK ─────────────────────
SELECT codigo, nome, continente, bloqueado
FROM paises_risco
WHERE risco = 'high'
ORDER BY continente, nome;

-- ── 9. VERIFICAR DUPLICATAS (não deve retornar nada) ──────────
SELECT codigo, COUNT(*) AS duplicatas
FROM paises_risco
GROUP BY codigo
HAVING COUNT(*) > 1;
