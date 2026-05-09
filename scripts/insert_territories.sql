-- ============================================================
--  TERRITÓRIOS E DEPENDÊNCIAS — paises_risco
--  Relevantes para empresa regulada pela FCA/HMRC (Londres)
--  Estes não são países soberanos mas são jurisdições reais
--  usadas por clientes de câmbio internacional.
-- ============================================================

INSERT INTO paises_risco (codigo, nome, nome_nacionalidade, risco, bloqueado, continente) VALUES

-- ── UK CROWN DEPENDENCIES ─────────────────────────────────────
-- Jurisdições autônomas da Coroa Britânica com regulação
-- financeira própria equivalente ao padrão FCA.
-- JMLSG guidance trata como baixo risco por default.
('JE', 'Jersey',          'Jersey resident',   'standard', false, 'Europe'),
('GG', 'Guernsey',        'Guernsey resident', 'standard', false, 'Europe'),
('IM', 'Isle of Man',     'Manx',              'standard', false, 'Europe'),

-- ── UK BRITISH OVERSEAS TERRITORIES ──────────────────────────
('GI', 'Gibraltar',       'Gibraltarian',      'standard', false, 'Europe'),
('BM', 'Bermuda',         'Bermudian',         'standard', false, 'North America'),

-- ── OFFSHORE CARIBENHO — BRITÂNICO ───────────────────────────
-- Cayman: removido da FATF grey list out/2023 mas mantém
-- reputação offshore; BVI: corporate secrecy histórico.
('KY', 'Cayman Islands',           'Caymanian',             'medium', false, 'Caribbean'),
('VG', 'British Virgin Islands',   'Virgin Islander',       'medium', false, 'Caribbean'),
('TC', 'Turks and Caicos Islands', 'Turks and Caicos Isl.', 'medium', false, 'Caribbean'),
('AI', 'Anguilla',                 'Anguillian',            'medium', false, 'Caribbean'),
('MS', 'Montserrat',               'Montserratian',         'medium', false, 'Caribbean'),

-- ── OFFSHORE CARIBENHO — HOLANDÊS ────────────────────────────
-- Jurisdições offshore do Reino dos Países Baixos.
('CW', 'Curaçao',      'Curaçaoan',    'medium', false, 'Caribbean'),
('AW', 'Aruba',        'Aruban',       'medium', false, 'Caribbean'),
('SX', 'Sint Maarten', 'Sint Maarten', 'medium', false, 'Caribbean'),

-- ── TERRITÓRIOS AMERICANOS ────────────────────────────────────
-- Regulados pelos EUA (FinCEN / FDIC), framework AML robusto.
('PR', 'Puerto Rico',        'Puerto Rican',       'standard', false, 'Caribbean'),
('VI', 'U.S. Virgin Islands','U.S. Virgin Islander','standard', false, 'Caribbean'),

-- ── CENTROS FINANCEIROS ASIÁTICOS ────────────────────────────
-- Hong Kong: HKMA, framework AML robusto; pressões políticas
-- pós-2020 mas regulação financeira ainda sólida.
-- Macau: jurisdição de jogo, maior risco de lavagem.
('HK', 'Hong Kong', 'Hong Konger', 'standard', false, 'Asia'),
('MO', 'Macau',     'Macanese',    'medium',   false, 'Asia')

ON CONFLICT (codigo) DO NOTHING;

-- ── VERIFICAÇÃO ───────────────────────────────────────────────
SELECT codigo, nome, risco, bloqueado, continente
FROM paises_risco
WHERE codigo IN (
    'JE','GG','IM','GI','BM',
    'KY','VG','TC','AI','MS',
    'CW','AW','SX','PR','VI',
    'HK','MO'
)
ORDER BY continente, nome;

-- ── TOTAL ATUALIZADO ──────────────────────────────────────────
SELECT COUNT(*) AS total_paises FROM paises_risco;

-- ============================================================
--  REFERÊNCIAS REGULATÓRIAS FCA
-- ============================================================
--
--  Crown Dependencies (JE, GG, IM):
--    → Não são parte do UK mas partilham soberano e têm
--      frameworks AML equivalentes. JMLSG: Standard por default.
--    → Jersey FSC · Guernsey FSC · Isle of Man FSA
--
--  Cayman Islands (KY):
--    → Removido da FATF grey list out/2023. Manter Medium
--      por histórico e volume de estruturas offshore.
--
--  BVI (VG):
--    → Não na grey list. Medium por uso extensivo em
--      estruturas opacas (Panama Papers, Pandora Papers).
--
--  Hong Kong (HK):
--    → HKMA regulação sólida. Standard. Monitorar evolução
--      política (National Security Law pós-2020).
--
--  Macau (MO):
--    → Jurisdição de jogo com risco AML elevado. Medium.
-- ============================================================
