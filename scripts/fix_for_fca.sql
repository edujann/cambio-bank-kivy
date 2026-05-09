-- ============================================================
--  CORREÇÕES FCA/HMRC — paises_risco
--  Empresa regulada pela FCA + HMRC (Londres, UK)
--  Referências: UK OFSI, MLR 2017 (Reg.33), FATF 2024,
--               JMLSG Guidance, UK High-Risk Third Countries List
-- ============================================================

-- ── PROMOVER PARA HIGH ────────────────────────────────────────
-- Países adicionados à FATF Grey List (Increased Monitoring)
-- A MLR 2017 Reg.33(3) obriga EDD para esses países.

UPDATE paises_risco SET risco = 'high', bloqueado = false
WHERE codigo IN (
    'JO',  -- Jordan     — FATF grey list desde jun/2023
    'TN',  -- Tunisia    — FATF grey list desde jun/2023
    'MA',  -- Morocco    — FATF grey list desde fev/2023
    'NA',  -- Namibia    — FATF grey list desde jun/2024
    'TZ',  -- Tanzania   — FATF grey list desde jun/2024
    'KE'   -- Kenya      — FATF grey list desde jun/2024
);

-- ── RECLASSIFICAR PARA MEDIUM ─────────────────────────────────
-- Países removidos da grey list recentemente ou jurisdições
-- offshore que a FCA trata com escrutínio elevado.

UPDATE paises_risco SET risco = 'medium', bloqueado = false
WHERE codigo IN (
    'PA',  -- Panama      — offshore center histórico (Panama Papers);
           --               removido da grey list jun/2023 mas FCA mantém
           --               monitoramento reforçado por reputação da jurisdição
    'AE',  -- UAE         — removido da grey list fev/2024; histórico recente
           --               como jurisdição de alto risco exige EDD continuado
    'ZA'   -- South Africa — removido da grey list jun/2024; transição recente
           --               não justifica retorno imediato a Standard
);

-- ── VERIFICAÇÃO FINAL ─────────────────────────────────────────
SELECT
    risco,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE bloqueado) AS bloqueados
FROM paises_risco
GROUP BY risco
ORDER BY CASE risco
    WHEN 'low' THEN 1 WHEN 'standard' THEN 2
    WHEN 'medium' THEN 3 WHEN 'high' THEN 4
    WHEN 'sanctioned' THEN 5 ELSE 6 END;

-- Confirmar os países alterados
SELECT codigo, nome, risco, bloqueado, continente
FROM paises_risco
WHERE codigo IN ('JO','TN','MA','NA','TZ','KE','PA','AE','ZA')
ORDER BY risco, nome;

-- ============================================================
--  NOTAS FCA/HMRC
-- ============================================================
--
--  SANÇÕES UK → consultar sempre: gov.uk/government/publications/
--              financial-sanctions-consolidated-list-of-targets
--              (OFSI, HM Treasury) — não usar só o OFAC americano.
--
--  FATF GREY LIST 2024 (HIGH obrigatório por MLR 2017 Reg.33):
--  BF CM CF CD HT IQ JM JO KE LA LB LY MA ML MR MZ NA NE NG
--  PG PH PS SL SN SO SS TJ TM TN TZ UG VU YE ZW
--
--  FATF BLACKLIST 2024 (SANCTIONED):
--  KP IR MM
--
--  UK OFSI SANCTIONED (além do blacklist FATF):
--  RU BY CU SY AF (Taliban) SD (parcial)
--
--  JURISDIÇÕES OFFSHORE UK A MONITORAR (sem código ISO soberano):
--  Cayman Islands (KY) · BVI (VG) · Isle of Man (IM)
--  Jersey (JE) · Guernsey (GG) — considerar adicionar ao sistema
--  com risco 'medium' ou 'high' conforme política interna.
-- ============================================================
