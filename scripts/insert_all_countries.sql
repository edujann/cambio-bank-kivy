-- ============================================================
--  INSERT ALL COUNTRIES — paises_risco
--  Critérios: FATF 2024 + OFAC + Banco Central do Brasil
--  ON CONFLICT (codigo) DO NOTHING → só insere os que faltam
-- ============================================================

INSERT INTO paises_risco (codigo, nome, nome_nacionalidade, risco, bloqueado, continente) VALUES

-- ══════════════════════════════════════════════════════════════
--  EUROPA — 44 países
-- ══════════════════════════════════════════════════════════════

-- Low: núcleo EU Ocidental + OCDE fora da EU
('AT', 'Austria',               'Austrian',         'low',       false, 'Europe'),
('BE', 'Belgium',               'Belgian',          'low',       false, 'Europe'),
('HR', 'Croatia',               'Croatian',         'low',       false, 'Europe'),
('CZ', 'Czech Republic',        'Czech',            'low',       false, 'Europe'),
('DK', 'Denmark',               'Danish',           'low',       false, 'Europe'),
('EE', 'Estonia',               'Estonian',         'low',       false, 'Europe'),
('FI', 'Finland',               'Finnish',          'low',       false, 'Europe'),
('FR', 'France',                'French',           'low',       false, 'Europe'),
('DE', 'Germany',               'German',           'low',       false, 'Europe'),
('IS', 'Iceland',               'Icelandic',        'low',       false, 'Europe'),
('IE', 'Ireland',               'Irish',            'low',       false, 'Europe'),
('IT', 'Italy',                 'Italian',          'low',       false, 'Europe'),
('LV', 'Latvia',                'Latvian',          'low',       false, 'Europe'),
('LI', 'Liechtenstein',         'Liechtensteiner',  'low',       false, 'Europe'),
('LT', 'Lithuania',             'Lithuanian',       'low',       false, 'Europe'),
('LU', 'Luxembourg',            'Luxembourger',     'low',       false, 'Europe'),
('NL', 'Netherlands',           'Dutch',            'low',       false, 'Europe'),
('NO', 'Norway',                'Norwegian',        'low',       false, 'Europe'),
('PL', 'Poland',                'Polish',           'low',       false, 'Europe'),
('PT', 'Portugal',              'Portuguese',       'low',       false, 'Europe'),
('SK', 'Slovakia',              'Slovak',           'low',       false, 'Europe'),
('SI', 'Slovenia',              'Slovenian',        'low',       false, 'Europe'),
('ES', 'Spain',                 'Spanish',          'low',       false, 'Europe'),
('SE', 'Sweden',                'Swedish',          'low',       false, 'Europe'),
('CH', 'Switzerland',           'Swiss',            'low',       false, 'Europe'),
('GB', 'United Kingdom',        'British',          'low',       false, 'Europe'),

-- Standard: EU leste/sul + países europeus estáveis
('AD', 'Andorra',               'Andorran',         'standard',  false, 'Europe'),
('BG', 'Bulgaria',              'Bulgarian',        'standard',  false, 'Europe'),
('CY', 'Cyprus',                'Cypriot',          'standard',  false, 'Europe'),
('GR', 'Greece',                'Greek',            'standard',  false, 'Europe'),
('HU', 'Hungary',               'Hungarian',        'standard',  false, 'Europe'),
('MT', 'Malta',                 'Maltese',          'standard',  false, 'Europe'),
('MC', 'Monaco',                'Monégasque',       'standard',  false, 'Europe'),
('RO', 'Romania',               'Romanian',         'standard',  false, 'Europe'),
('SM', 'San Marino',            'Sammarinese',      'standard',  false, 'Europe'),
('VA', 'Vatican City',          'Vatican',          'standard',  false, 'Europe'),

-- Medium: países em transição, algumas preocupações AML
('AL', 'Albania',               'Albanian',         'medium',    false, 'Europe'),
('BA', 'Bosnia and Herzegovina','Bosnian',          'medium',    false, 'Europe'),
('GE', 'Georgia',               'Georgian',         'medium',    false, 'Europe'),
('XK', 'Kosovo',                'Kosovar',          'medium',    false, 'Europe'),
('MD', 'Moldova',               'Moldovan',         'medium',    false, 'Europe'),
('ME', 'Montenegro',            'Montenegrin',      'medium',    false, 'Europe'),
('MK', 'North Macedonia',       'Macedonian',       'medium',    false, 'Europe'),
('RS', 'Serbia',                'Serbian',          'medium',    false, 'Europe'),
('TR', 'Turkey',                'Turkish',          'medium',    false, 'Europe'),
('UA', 'Ukraine',               'Ukrainian',        'medium',    false, 'Europe'),

-- Sanctioned (OFAC/EU): bloqueado
('BY', 'Belarus',               'Belarusian',       'sanctioned',true,  'Europe'),
('RU', 'Russia',                'Russian',          'sanctioned',true,  'Europe'),

-- ══════════════════════════════════════════════════════════════
--  AMÉRICAS — 35 países
-- ══════════════════════════════════════════════════════════════

-- Low: economias desenvolvidas
('CA', 'Canada',                'Canadian',         'low',       false, 'Americas'),
('CL', 'Chile',                 'Chilean',          'low',       false, 'Americas'),
('US', 'United States',         'American',         'low',       false, 'Americas'),

-- Standard: principais parceiros comerciais do Brasil
('AR', 'Argentina',             'Argentine',        'standard',  false, 'Americas'),
('BR', 'Brazil',                'Brazilian',        'standard',  false, 'Americas'),
('CR', 'Costa Rica',            'Costa Rican',      'standard',  false, 'Americas'),
('MX', 'Mexico',                'Mexican',          'standard',  false, 'Americas'),
('PA', 'Panama',                'Panamanian',       'standard',  false, 'Americas'),
('PY', 'Paraguay',              'Paraguayan',       'standard',  false, 'Americas'),
('PE', 'Peru',                  'Peruvian',         'standard',  false, 'Americas'),
('UY', 'Uruguay',               'Uruguayan',        'standard',  false, 'Americas'),

-- Medium: desenvolvimento intermediário, riscos moderados
('AG', 'Antigua and Barbuda',   'Antiguan',         'medium',    false, 'Americas'),
('BS', 'Bahamas',               'Bahamian',         'medium',    false, 'Americas'),
('BB', 'Barbados',              'Barbadian',        'medium',    false, 'Americas'),
('BZ', 'Belize',                'Belizean',         'medium',    false, 'Americas'),
('BO', 'Bolivia',               'Bolivian',         'medium',    false, 'Americas'),
('CO', 'Colombia',              'Colombian',        'medium',    false, 'Americas'),
('DM', 'Dominica',              'Dominican',        'medium',    false, 'Americas'),
('DO', 'Dominican Republic',    'Dominican',        'medium',    false, 'Americas'),
('EC', 'Ecuador',               'Ecuadorian',       'medium',    false, 'Americas'),
('SV', 'El Salvador',           'Salvadoran',       'medium',    false, 'Americas'),
('GD', 'Grenada',               'Grenadian',        'medium',    false, 'Americas'),
('GT', 'Guatemala',             'Guatemalan',       'medium',    false, 'Americas'),
('GY', 'Guyana',                'Guyanese',         'medium',    false, 'Americas'),
('HN', 'Honduras',              'Honduran',         'medium',    false, 'Americas'),
('KN', 'Saint Kitts and Nevis', 'Kittitian',        'medium',    false, 'Americas'),
('LC', 'Saint Lucia',           'Saint Lucian',     'medium',    false, 'Americas'),
('VC', 'Saint Vincent',         'Vincentian',       'medium',    false, 'Americas'),
('SR', 'Suriname',              'Surinamese',       'medium',    false, 'Americas'),

-- High: FATF Grey List / governança fraca / instabilidade
('HT', 'Haiti',                 'Haitian',          'high',      false, 'Americas'),
('JM', 'Jamaica',               'Jamaican',         'high',      false, 'Americas'),
('NI', 'Nicaragua',             'Nicaraguan',       'high',      false, 'Americas'),
('TT', 'Trinidad and Tobago',   'Trinidadian',      'high',      false, 'Americas'),
('VE', 'Venezuela',             'Venezuelan',       'high',      false, 'Americas'),

-- Sanctioned (OFAC)
('CU', 'Cuba',                  'Cuban',            'sanctioned',true,  'Americas'),

-- ══════════════════════════════════════════════════════════════
--  ÁSIA — 48 países/territórios
-- ══════════════════════════════════════════════════════════════

-- Low: economias asiáticas desenvolvidas
('JP', 'Japan',                 'Japanese',         'low',       false, 'Asia'),
('KR', 'South Korea',           'South Korean',     'low',       false, 'Asia'),
('SG', 'Singapore',             'Singaporean',      'low',       false, 'Asia'),
('TW', 'Taiwan',                'Taiwanese',        'low',       false, 'Asia'),

-- Standard: parceiros comerciais estáveis
('AE', 'United Arab Emirates',  'Emirati',          'standard',  false, 'Asia'),
('AM', 'Armenia',               'Armenian',         'standard',  false, 'Asia'),
('AZ', 'Azerbaijan',            'Azerbaijani',      'standard',  false, 'Asia'),
('BH', 'Bahrain',               'Bahraini',         'standard',  false, 'Asia'),
('BT', 'Bhutan',                'Bhutanese',        'standard',  false, 'Asia'),
('BN', 'Brunei',                'Bruneian',         'standard',  false, 'Asia'),
('CN', 'China',                 'Chinese',          'standard',  false, 'Asia'),
('IN', 'India',                 'Indian',           'standard',  false, 'Asia'),
('ID', 'Indonesia',             'Indonesian',       'standard',  false, 'Asia'),
('IL', 'Israel',                'Israeli',          'standard',  false, 'Asia'),
('JO', 'Jordan',                'Jordanian',        'standard',  false, 'Asia'),
('KW', 'Kuwait',                'Kuwaiti',          'standard',  false, 'Asia'),
('MY', 'Malaysia',              'Malaysian',        'standard',  false, 'Asia'),
('MV', 'Maldives',              'Maldivian',        'standard',  false, 'Asia'),
('MN', 'Mongolia',              'Mongolian',        'standard',  false, 'Asia'),
('OM', 'Oman',                  'Omani',            'standard',  false, 'Asia'),
('QA', 'Qatar',                 'Qatari',           'standard',  false, 'Asia'),
('SA', 'Saudi Arabia',          'Saudi',            'standard',  false, 'Asia'),
('TH', 'Thailand',              'Thai',             'standard',  false, 'Asia'),

-- Medium: riscos moderados, alguns controles AML a reforçar
('BD', 'Bangladesh',            'Bangladeshi',      'medium',    false, 'Asia'),
('KH', 'Cambodia',              'Cambodian',        'medium',    false, 'Asia'),
('KZ', 'Kazakhstan',            'Kazakhstani',      'medium',    false, 'Asia'),
('KG', 'Kyrgyzstan',            'Kyrgyz',           'medium',    false, 'Asia'),
('NP', 'Nepal',                 'Nepali',           'medium',    false, 'Asia'),
('LK', 'Sri Lanka',             'Sri Lankan',       'medium',    false, 'Asia'),
('TL', 'Timor-Leste',           'Timorese',         'medium',    false, 'Asia'),
('UZ', 'Uzbekistan',            'Uzbek',            'medium',    false, 'Asia'),
('VN', 'Vietnam',               'Vietnamese',       'medium',    false, 'Asia'),

-- High: FATF Grey List / conflito / risco elevado
('IQ', 'Iraq',                  'Iraqi',            'high',      false, 'Asia'),
('LA', 'Laos',                  'Laotian',          'high',      false, 'Asia'),
('LB', 'Lebanon',               'Lebanese',         'high',      false, 'Asia'),
('PK', 'Pakistan',              'Pakistani',        'high',      false, 'Asia'),
('PS', 'Palestine',             'Palestinian',      'high',      false, 'Asia'),
('PH', 'Philippines',           'Filipino',         'high',      false, 'Asia'),
('TJ', 'Tajikistan',            'Tajik',            'high',      false, 'Asia'),
('TM', 'Turkmenistan',          'Turkmen',          'high',      false, 'Asia'),
('YE', 'Yemen',                 'Yemeni',           'high',      false, 'Asia'),

-- Sanctioned (FATF Blacklist + OFAC)
('AF', 'Afghanistan',           'Afghan',           'sanctioned',true,  'Asia'),
('IR', 'Iran',                  'Iranian',          'sanctioned',true,  'Asia'),
('KP', 'North Korea',           'North Korean',     'sanctioned',true,  'Asia'),
('MM', 'Myanmar',               'Burmese',          'sanctioned',true,  'Asia'),
('SY', 'Syria',                 'Syrian',           'sanctioned',true,  'Asia'),

-- ══════════════════════════════════════════════════════════════
--  ÁFRICA — 54 países
-- ══════════════════════════════════════════════════════════════

-- Standard: governança moderada, baixo risco para BR
('CV', 'Cape Verde',            'Cape Verdean',     'standard',  false, 'Africa'),
('MU', 'Mauritius',             'Mauritian',        'standard',  false, 'Africa'),
('NA', 'Namibia',               'Namibian',         'standard',  false, 'Africa'),
('ZA', 'South Africa',          'South African',    'standard',  false, 'Africa'),

-- Medium: risco intermediário
('DZ', 'Algeria',               'Algerian',         'medium',    false, 'Africa'),
('AO', 'Angola',                'Angolan',          'medium',    false, 'Africa'),
('BJ', 'Benin',                 'Beninese',         'medium',    false, 'Africa'),
('BW', 'Botswana',              'Botswanan',        'medium',    false, 'Africa'),
('CM', 'Cameroon',              'Cameroonian',      'medium',    false, 'Africa'),
('CI', 'Ivory Coast',           'Ivorian',          'medium',    false, 'Africa'),
('DJ', 'Djibouti',              'Djiboutian',       'medium',    false, 'Africa'),
('EG', 'Egypt',                 'Egyptian',         'medium',    false, 'Africa'),
('GA', 'Gabon',                 'Gabonese',         'medium',    false, 'Africa'),
('GM', 'Gambia',                'Gambian',          'medium',    false, 'Africa'),
('GH', 'Ghana',                 'Ghanaian',         'medium',    false, 'Africa'),
('KE', 'Kenya',                 'Kenyan',           'medium',    false, 'Africa'),
('LS', 'Lesotho',               'Basotho',          'medium',    false, 'Africa'),
('MG', 'Madagascar',            'Malagasy',         'medium',    false, 'Africa'),
('MW', 'Malawi',                'Malawian',         'medium',    false, 'Africa'),
('MA', 'Morocco',               'Moroccan',         'medium',    false, 'Africa'),
('RW', 'Rwanda',                'Rwandan',          'medium',    false, 'Africa'),
('ST', 'São Tomé and Príncipe', 'São Toméan',       'medium',    false, 'Africa'),
('SC', 'Seychelles',            'Seychellois',      'medium',    false, 'Africa'),
('SZ', 'Eswatini',              'Swazi',            'medium',    false, 'Africa'),
('TZ', 'Tanzania',              'Tanzanian',        'medium',    false, 'Africa'),
('TG', 'Togo',                  'Togolese',         'medium',    false, 'Africa'),
('TN', 'Tunisia',               'Tunisian',         'medium',    false, 'Africa'),
('ZM', 'Zambia',                'Zambian',          'medium',    false, 'Africa'),

-- High: FATF Grey List + conflito + governança fraca
('BF', 'Burkina Faso',          'Burkinabe',        'high',      false, 'Africa'),
('BI', 'Burundi',               'Burundian',        'high',      false, 'Africa'),
('CF', 'Central African Rep.',  'Central African',  'high',      false, 'Africa'),
('TD', 'Chad',                  'Chadian',          'high',      false, 'Africa'),
('KM', 'Comoros',               'Comorian',         'high',      false, 'Africa'),
('CG', 'Congo',                 'Congolese',        'high',      false, 'Africa'),
('CD', 'DR Congo',              'Congolese',        'high',      false, 'Africa'),
('GQ', 'Equatorial Guinea',     'Equatorial Guinean','high',     false, 'Africa'),
('ER', 'Eritrea',               'Eritrean',         'high',      false, 'Africa'),
('ET', 'Ethiopia',              'Ethiopian',        'high',      false, 'Africa'),
('GN', 'Guinea',                'Guinean',          'high',      false, 'Africa'),
('GW', 'Guinea-Bissau',         'Bissau-Guinean',   'high',      false, 'Africa'),
('LR', 'Liberia',               'Liberian',         'high',      false, 'Africa'),
('LY', 'Libya',                 'Libyan',           'high',      false, 'Africa'),
('ML', 'Mali',                  'Malian',           'high',      false, 'Africa'),
('MR', 'Mauritania',            'Mauritanian',      'high',      false, 'Africa'),
('MZ', 'Mozambique',            'Mozambican',       'high',      false, 'Africa'),
('NE', 'Niger',                 'Nigerien',         'high',      false, 'Africa'),
('NG', 'Nigeria',               'Nigerian',         'high',      false, 'Africa'),
('SN', 'Senegal',               'Senegalese',       'high',      false, 'Africa'),
('SL', 'Sierra Leone',          'Sierra Leonean',   'high',      false, 'Africa'),
('SO', 'Somalia',               'Somali',           'high',      false, 'Africa'),
('SS', 'South Sudan',           'South Sudanese',   'high',      false, 'Africa'),
('SD', 'Sudan',                 'Sudanese',         'high',      true,  'Africa'),
('UG', 'Uganda',                'Ugandan',          'high',      false, 'Africa'),
('ZW', 'Zimbabwe',              'Zimbabwean',       'high',      false, 'Africa'),

-- ══════════════════════════════════════════════════════════════
--  OCEANIA — 14 países
-- ══════════════════════════════════════════════════════════════

-- Low
('AU', 'Australia',             'Australian',       'low',       false, 'Oceania'),
('NZ', 'New Zealand',           'New Zealander',    'low',       false, 'Oceania'),

-- Medium
('FJ', 'Fiji',                  'Fijian',           'medium',    false, 'Oceania'),
('KI', 'Kiribati',              'I-Kiribati',       'medium',    false, 'Oceania'),
('MH', 'Marshall Islands',      'Marshallese',      'medium',    false, 'Oceania'),
('FM', 'Micronesia',            'Micronesian',      'medium',    false, 'Oceania'),
('NR', 'Nauru',                 'Nauruan',          'medium',    false, 'Oceania'),
('PW', 'Palau',                 'Palauan',          'medium',    false, 'Oceania'),
('WS', 'Samoa',                 'Samoan',           'medium',    false, 'Oceania'),
('SB', 'Solomon Islands',       'Solomon Islander', 'medium',    false, 'Oceania'),
('TO', 'Tonga',                 'Tongan',           'medium',    false, 'Oceania'),
('TV', 'Tuvalu',                'Tuvaluan',         'medium',    false, 'Oceania'),

-- High: FATF monitoring
('PG', 'Papua New Guinea',      'Papua New Guinean','high',      false, 'Oceania'),
('VU', 'Vanuatu',               'Ni-Vanuatu',       'high',      false, 'Oceania')

ON CONFLICT (codigo) DO NOTHING;

-- ══════════════════════════════════════════════════════════════
--  RESUMO DA CLASSIFICAÇÃO
-- ══════════════════════════════════════════════════════════════
--
--  LOW (verde)        ~30 países — G7 + EU Ocidental + OCDE avançada
--  STANDARD (âmbar)   ~35 países — parceiros estáveis sem alertas FATF
--  MEDIUM (amarelo)   ~60 países — risco moderado, EDD padrão
--  HIGH (vermelho)    ~55 países — FATF Grey List + conflito + governança fraca
--  SANCTIONED (roxo)  ~7 países  — FATF Blacklist + OFAC: AF,BY,CU,IR,KP,MM,RU,SY
--
--  Fontes: FATF Public Statement 2024, OFAC Sanctions List,
--          COAF/Bacen regulação PLD-FT Brasil
-- ══════════════════════════════════════════════════════════════
