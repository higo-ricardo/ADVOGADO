"""
router.py — Roteamento determinístico.
Identifica domínio e código da peça a partir de palavras-chave.
Substitui a etapa de triagem do advogado.md sem gastar tokens.
"""

# ---------------------------------------------------------------------------
# Mapa de keywords → domínio
# ---------------------------------------------------------------------------
DOMINIOS: dict[str, tuple[str, str]] = {
    # (id, nome_exibicao)
    "posse":               ("A", "Imobiliário"),
    "esbulho":             ("A", "Imobiliário"),
    "turbação":            ("A", "Imobiliário"),
    "reintegração":        ("A", "Imobiliário"),
    "usucapião":           ("A", "Imobiliário"),
    "imissão":             ("A", "Imobiliário"),
    "reivindicatória":     ("A", "Imobiliário"),
    "vizinhança":          ("A", "Imobiliário"),
    "demarcação":          ("A", "Imobiliário"),
    "passagem forçada":    ("A", "Imobiliário"),
    "cdc":                 ("B", "Consumerista / JEC"),
    "consumidor":          ("B", "Consumerista / JEC"),
    "negativação":         ("B", "Consumerista / JEC"),
    "spc":                 ("B", "Consumerista / JEC"),
    "serasa":              ("B", "Consumerista / JEC"),
    "plano de saúde":      ("B", "Consumerista / JEC"),
    "telefonia":           ("B", "Consumerista / JEC"),
    "overbooking":         ("B", "Consumerista / JEC"),
    "corte de energia":    ("B", "Consumerista / JEC"),
    "produto defeituoso":  ("B", "Consumerista / JEC"),
    "troca de produto":    ("B", "Consumerista / JEC"),
    "acidente de trânsito":("C", "Cível"),
    "colisão":             ("C", "Cível"),
    "aluguel atrasado":    ("C", "Cível"),
    "despejo":             ("C", "Cível"),
    "locação":             ("C", "Cível"),
    "réplica":             ("C", "Cível"),
    "honorários":          ("D", "Documentos e Apoio"),
    "procuração":          ("D", "Documentos e Apoio"),
    "hipossuficiência":    ("D", "Documentos e Apoio"),
    "substabelecimento":   ("D", "Documentos e Apoio"),
    "habilitação":         ("D", "Documentos e Apoio"),
    "acordo":              ("D", "Documentos e Apoio"),
    "alvará":              ("D", "Documentos e Apoio"),
    "cumprimento de sentença": ("D", "Documentos e Apoio"),
    "penhora":             ("D", "Documentos e Apoio"),
    "alimentos":           ("F", "Família e Sucessões"),
    "paternidade":         ("F", "Família e Sucessões"),
    "inventário":          ("F", "Família e Sucessões"),
    "partilha":            ("F", "Família e Sucessões"),
    "guarda":              ("F", "Família e Sucessões"),
    "divórcio":            ("F", "Família e Sucessões"),
    "união estável":       ("F", "Família e Sucessões"),
    "curatela":            ("F", "Família e Sucessões"),
    "interdição":          ("F", "Família e Sucessões"),
    "habeas corpus":       ("G", "Remédios Constitucionais"),
    "habeas data":         ("G", "Remédios Constitucionais"),
    "mandado de segurança":("G", "Remédios Constitucionais"),
    "ação popular":        ("G", "Remédios Constitucionais"),
    "apelação":            ("R", "Recursos Cíveis"),
    "agravo de instrumento":("R", "Recursos Cíveis"),
    "recurso especial":    ("R", "Recursos Cíveis"),
    "recurso extraordinário":("R", "Recursos Cíveis"),
    "embargos de declaração":("R", "Recursos Cíveis"),
    "agravo interno":      ("R", "Recursos Cíveis"),
}

# ---------------------------------------------------------------------------
# Mapa domínio → códigos disponíveis
# ---------------------------------------------------------------------------
CODIGOS_POR_DOMINIO: dict[str, list[tuple[str, str]]] = {
    "A": [
        ("RPO", "Reintegração de posse (esbulho)"),
        ("MPO", "Manutenção de posse (turbação)"),
        ("IPR", "Interdito proibitório (ameaça)"),
        ("IPO", "Imissão na posse"),
        ("REI", "Reivindicatória"),
        ("CUS", "Contestação em usucapião"),
        ("ANU", "Anulatória de negócio"),
        ("PAF", "Passagem forçada"),
        ("VIZ", "Direito de vizinhança"),
        ("DMT", "Demarcação de terras"),
    ],
    "B": [
        ("PI",  "Petição inicial genérica (CDC)"),
        ("NEG", "Negativação indevida"),
        ("PSC", "Plano de saúde — cancelamento"),
        ("PSN", "Plano de saúde — negativa de cobertura"),
        ("TEL", "Telefonia"),
        ("TRO", "Transporte — atraso/pane"),
        ("TRB", "Transporte — overbooking"),
        ("DIS", "Distrato — recusa de cancelamento"),
        ("CEL", "Corte de energia elétrica"),
        ("RPR", "Demora de reparo (art. 18 CDC)"),
        ("OBF", "Substituição de produto defeituoso"),
        ("RI",  "Recurso inominado (JEC)"),
        ("CR",  "Contrarrazões (JEC)"),
        ("ED",  "Embargos de declaração (JEC)"),
        ("AI",  "Agravo interno (JEC)"),
    ],
    "C": [
        ("ATR", "Acidente de trânsito"),
        ("ALU", "Locação / despejo"),
        ("REP", "Réplica à contestação"),
    ],
    "D": [
        ("CHO", "Contrato de honorários advocatícios"),
        ("PRO", "Procuração ad judicia et extra"),
        ("DHI", "Declaração de hipossuficiência"),
        ("SUB", "Substabelecimento"),
        ("HAB", "Habilitação de advogado"),
        ("ACO", "Petição de acordo"),
        ("ALV", "Expedição de alvará judicial"),
        ("CPS", "Cumprimento de sentença / penhora online"),
    ],
    "F": [
        ("NEP", "Negatória de paternidade"),
        ("INP", "Investigação de paternidade"),
        ("ALI", "Alimentos"),
        ("EXA", "Execução de alimentos"),
        ("INV", "Inventário"),
        ("OFA", "Oferta de alimentos"),
        ("UNE", "União estável"),
        ("INT", "Interdição"),
        ("GUA", "Guarda"),
        ("VIS", "Visitas / convivência familiar"),
        ("CUR", "Curatela"),
        ("DIV", "Divórcio"),
    ],
    "G": [
        ("AP",  "Ação popular"),
        ("HC",  "Habeas corpus"),
        ("HD",  "Habeas data"),
        ("MS",  "Mandado de segurança"),
    ],
    "R": [
        ("APE", "Apelação"),
        ("AGI", "Agravo de instrumento"),
        ("EDC", "Embargos de declaração"),
        ("AGR", "Agravo interno"),
        ("RES", "Recurso especial (STJ)"),
        ("REX", "Recurso extraordinário (STF)"),
    ],
}

# ---------------------------------------------------------------------------
# Campos obrigatórios por código de peça
# ---------------------------------------------------------------------------
CAMPOS_OBRIGATORIOS: dict[str, list[dict]] = {
    # --- DOMÍNIO A ---
    "RPO": [
        {"id": "autor", "label": "Nome completo do autor", "tipo": "text"},
        {"id": "reu",   "label": "Nome completo do réu",   "tipo": "text"},
        {"id": "imovel","label": "Descrição do imóvel",    "tipo": "textarea"},
        {"id": "data_esbulho","label": "Data do esbulho",  "tipo": "text"},
        {"id": "forca", "label": "Força nova (<1 ano) ou velha?", "tipo": "select",
         "opcoes": ["Nova (menos de 1 ano e 1 dia)", "Velha (1 ano e 1 dia ou mais)"]},
    ],
    "MPO": [
        {"id": "autor", "label": "Nome completo do autor", "tipo": "text"},
        {"id": "reu",   "label": "Nome completo do réu",   "tipo": "text"},
        {"id": "imovel","label": "Descrição do imóvel",    "tipo": "textarea"},
        {"id": "atos_turbacao","label": "Descreva os atos de turbação", "tipo": "textarea"},
    ],
    # --- DOMÍNIO B ---
    "NEG": [
        {"id": "autor",  "label": "Nome completo do autor",     "tipo": "text"},
        {"id": "cpf",    "label": "CPF do autor",                "tipo": "text"},
        {"id": "reu",    "label": "Nome do réu (credor/empresa)","tipo": "text"},
        {"id": "valor",  "label": "Valor negativado (R$)",       "tipo": "text"},
        {"id": "data",   "label": "Data da negativação",         "tipo": "text"},
        {"id": "fatos",  "label": "Descreva brevemente os fatos","tipo": "textarea"},
    ],
    "PSC": [
        {"id": "autor",  "label": "Nome completo do autor",     "tipo": "text"},
        {"id": "plano",  "label": "Nome da operadora",           "tipo": "text"},
        {"id": "fatos",  "label": "Descreva o cancelamento indevido", "tipo": "textarea"},
    ],
    "PSN": [
        {"id": "autor",      "label": "Nome completo do autor",         "tipo": "text"},
        {"id": "plano",      "label": "Nome da operadora",               "tipo": "text"},
        {"id": "procedimento","label": "Procedimento/cobertura negada",  "tipo": "textarea"},
        {"id": "justificativa","label": "Justificativa dada pela operadora","tipo": "textarea"},
    ],
    "TEL": [
        {"id": "autor",  "label": "Nome completo do autor",     "tipo": "text"},
        {"id": "empresa","label": "Nome da operadora",           "tipo": "text"},
        {"id": "fatos",  "label": "Descreva o problema (bloqueio, cobrança, etc.)","tipo": "textarea"},
    ],
    # --- DOMÍNIO C ---
    "ATR": [
        {"id": "autor",   "label": "Nome completo do autor",    "tipo": "text"},
        {"id": "reu",     "label": "Nome completo do réu",      "tipo": "text"},
        {"id": "data",    "label": "Data do acidente",          "tipo": "text"},
        {"id": "local",   "label": "Local do acidente",         "tipo": "text"},
        {"id": "danos",   "label": "Descreva os danos (veículo, físicos, etc.)", "tipo": "textarea"},
        {"id": "bo",      "label": "Número do BO (se houver)",  "tipo": "text"},
    ],
    "ALU": [
        {"id": "locador", "label": "Nome do locador",           "tipo": "text"},
        {"id": "locatario","label": "Nome do locatário",        "tipo": "text"},
        {"id": "imovel",  "label": "Endereço do imóvel",        "tipo": "textarea"},
        {"id": "valor_aluguel","label": "Valor mensal do aluguel (R$)","tipo": "text"},
        {"id": "meses_devidos","label": "Quantidade de meses em débito","tipo": "text"},
    ],
    "REP": [
        {"id": "autor",        "label": "Nome do autor",            "tipo": "text"},
        {"id": "reu",          "label": "Nome do réu",              "tipo": "text"},
        {"id": "processo",     "label": "Número do processo",       "tipo": "text"},
        {"id": "preliminares", "label": "Preliminares levantadas pelo réu (se houver)", "tipo": "textarea"},
        {"id": "teses_merito", "label": "Teses de mérito da contestação (resumidas)", "tipo": "textarea"},
    ],
    # --- DOMÍNIO D ---
    "CHO": [
        {"id": "advogado",  "label": "Nome completo do advogado",   "tipo": "text"},
        {"id": "oab",       "label": "OAB (número e estado)",        "tipo": "text"},
        {"id": "cliente",   "label": "Nome completo do cliente",     "tipo": "text"},
        {"id": "cpf_cliente","label": "CPF do cliente",             "tipo": "text"},
        {"id": "objeto",    "label": "Objeto dos honorários (descreva a causa)", "tipo": "textarea"},
        {"id": "valor",     "label": "Valor dos honorários (R$) ou percentual","tipo": "text"},
    ],
    "PRO": [
        {"id": "outorgante", "label": "Nome completo do outorgante","tipo": "text"},
        {"id": "cpf",        "label": "CPF do outorgante",          "tipo": "text"},
        {"id": "advogado",   "label": "Nome completo do advogado",  "tipo": "text"},
        {"id": "oab",        "label": "OAB (número e estado)",      "tipo": "text"},
        {"id": "objeto",     "label": "Finalidade da procuração",   "tipo": "textarea"},
    ],
    "DHI": [
        {"id": "requerente","label": "Nome completo do requerente", "tipo": "text"},
        {"id": "cpf",       "label": "CPF do requerente",           "tipo": "text"},
        {"id": "renda",     "label": "Renda mensal aproximada (R$)","tipo": "text"},
    ],
    "ALV": [
        {"id": "requerente","label": "Nome do requerente",          "tipo": "text"},
        {"id": "processo",  "label": "Número do processo",          "tipo": "text"},
        {"id": "valor",     "label": "Valor a ser levantado (R$)",  "tipo": "text"},
        {"id": "banco",     "label": "Banco, agência e conta corrente","tipo": "text"},
        {"id": "cpf",       "label": "CPF do titular da conta",     "tipo": "text"},
    ],
    "CPS": [
        {"id": "exequente", "label": "Nome do exequente",           "tipo": "text"},
        {"id": "executado",  "label": "Nome do executado",          "tipo": "text"},
        {"id": "processo",   "label": "Número do processo",         "tipo": "text"},
        {"id": "valor_condenacao","label": "Valor da condenação (R$)","tipo": "text"},
        {"id": "memoria_calculo","label": "Memória de cálculo atualizada (cole aqui)", "tipo": "textarea"},
    ],
    # --- DOMÍNIO F ---
    "ALI": [
        {"id": "alimentando","label": "Nome do alimentando",        "tipo": "text"},
        {"id": "alimentante","label": "Nome do alimentante",        "tipo": "text"},
        {"id": "necessidade","label": "Descreva a necessidade (despesas mensais)", "tipo": "textarea"},
        {"id": "possibilidade","label": "Descreva a possibilidade do alimentante","tipo": "textarea"},
        {"id": "valor_pedido","label": "Valor dos alimentos pleiteados (R$ ou SM)","tipo": "text"},
    ],
    "DIV": [
        {"id": "conjuge1", "label": "Nome do cônjuge 1",            "tipo": "text"},
        {"id": "conjuge2", "label": "Nome do cônjuge 2",            "tipo": "text"},
        {"id": "casamento","label": "Data do casamento",            "tipo": "text"},
        {"id": "regime",   "label": "Regime de bens",               "tipo": "select",
         "opcoes": ["Comunhão parcial de bens","Comunhão universal de bens","Separação de bens","Participação final nos aquestos"]},
        {"id": "filhos",   "label": "Há filhos menores? Informe nome(s) e idade(s)", "tipo": "textarea"},
        {"id": "bens",     "label": "Bens a partilhar (se houver)", "tipo": "textarea"},
    ],
    # --- DOMÍNIO G ---
    "HC": [
        {"id": "paciente",    "label": "Nome do paciente",          "tipo": "text"},
        {"id": "autoridade",  "label": "Autoridade coatora",        "tipo": "text"},
        {"id": "especie",     "label": "Espécie do HC", "tipo": "select",
         "opcoes": ["Liberatório (soltar preso)","Preventivo (evitar prisão)","Trancamento de ação penal"]},
        {"id": "fatos",       "label": "Descreva o constrangimento ilegal", "tipo": "textarea"},
    ],
    "MS": [
        {"id": "impetrante",  "label": "Nome do impetrante",        "tipo": "text"},
        {"id": "autoridade",  "label": "Autoridade coatora",        "tipo": "text"},
        {"id": "ato_coator",  "label": "Descreva o ato coator",     "tipo": "textarea"},
        {"id": "direito",     "label": "Direito líquido e certo violado", "tipo": "textarea"},
    ],
    # --- DOMÍNIO R ---
    "APE": [
        {"id": "apelante",  "label": "Nome do apelante",            "tipo": "text"},
        {"id": "apelado",   "label": "Nome do apelado",             "tipo": "text"},
        {"id": "processo",  "label": "Número do processo",          "tipo": "text"},
        {"id": "sentenca",  "label": "Resumo da sentença recorrida","tipo": "textarea"},
        {"id": "teses",     "label": "Teses do recurso",            "tipo": "textarea"},
    ],
}

# Fallback genérico para códigos sem campos mapeados
CAMPOS_GENERICOS = [
    {"id": "autor",  "label": "Nome completo do autor / requerente", "tipo": "text"},
    {"id": "reu",    "label": "Nome completo do réu / requerido",    "tipo": "text"},
    {"id": "fatos",  "label": "Descreva os fatos do caso",           "tipo": "textarea"},
    {"id": "pedido", "label": "O que deseja pedir ao juiz?",         "tipo": "textarea"},
]

# Modos autônomos — não precisam de handoff para o estagiário
CODIGOS_AUTONOMOS = {"CHO", "PRO", "DHI", "SUB", "HAB", "ACO"}


def detectar_dominio(texto: str) -> tuple[str, str] | None:
    """Retorna (id_dominio, nome) se encontrar keyword, senão None."""
    texto_lower = texto.lower()
    for kw, (dom_id, dom_nome) in DOMINIOS.items():
        if kw in texto_lower:
            return dom_id, dom_nome
    return None


def codigos_do_dominio(dom_id: str) -> list[tuple[str, str]]:
    return CODIGOS_POR_DOMINIO.get(dom_id, [])


def campos_do_codigo(codigo: str) -> list[dict]:
    return CAMPOS_OBRIGATORIOS.get(codigo, CAMPOS_GENERICOS)


def is_autonomo(codigo: str) -> bool:
    return codigo in CODIGOS_AUTONOMOS
