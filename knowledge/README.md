# Knowledge Base — Estrutura atual

## Organização

Os arquivos de minuta estão divididos por domínio jurídico em subpastas:

```text
knowledge/
├── imobiliarias/
├── civeis/
├── intermediarias/
├── familia/
├── remedios-constitucionais.md
├── recursos-civeis.md
├── minuta-base.md
├── roteamento.md
├── advogado.md
├── estagiario.md
├── estilo_juridico.md
├── contrato_decisao.md
├── fontes.md
├── verbetesSTF.md
├── verbetesSTJ.md
└── sumulas-vinculantes.md
```

## Domínios

| Domínio | Pasta/Arquivo | Códigos |
|---------|---------------|---------|
| A — Imobiliário | `imobiliarias/` | RPO, MPO, IPR, IPO, REI, CUS, ANU, PAF, VIZ, DMT |
| B — Consumerista | `minutas-consumeristas.md` | PI, NEG, PSC, PSN, TEL, TRO, TRB, DIS, CEL, RPR, OBF, RI, CR, ED, AI |
| C — Cível | `civeis/` | ATR, ALU, REP |
| D — Intermediárias | `intermediarias/` | PRO, HAB, ACO, ALV, CPS, SUB, DHI |
| E — Família | `familia/` | NEP, INP, ALI, EXA, INV, OFA, UNE, INT, GUA, VIS, CUR, DIV |
| G — Remédios Constitucionais | `remedios-constitucionais.md` | AP, HC, HD, MS |
| R — Recursos Cíveis | `recursos-civeis.md` | APE, AGI, EDC, AGR, RES, REX |

## Mapeamento código → arquivo

Cada código está mapeado em `knowledge.py`, função `carregar_minuta_do_codigo()`.

O RAG usa `rglob("*.md")` para indexar todos os arquivos automaticamente.
