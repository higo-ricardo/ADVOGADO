# Advogado-Civel-IA

Sistema modular de redacao juridica para Direito Civil, Imobiliario, Consumerista, Familia, Remedios Constitucionais, Execucao e Recursos Civeis, com separacao de papeis por contrato entre agentes (`advogado`, `estagiario`) e base normativa centralizada.

---

## Arquitetura de Agentes

```text
Usuario
  └─> advogado.md          ← orquestrador principal (estrategia + decisao)
        ├─> roteamento.md  ← triagem de dominio, codigo, rito, dados
        ├─> contrato_decisao.md  ← handoff portatil (interface oficial)
        │     └─> estagiario.md  ← executor contratual (redacao)
        │           ├─> estilo_juridico.md
        │           ├─> minuta-base.md  ← fragmentos de formatacao
        │           └─> minutas (por dominio)
        └─> fontes.md / verbetes / sumulas  ← fundamentacao
```

---

## Agentes e Responsabilidades

### `advogado` — Orquestrador Estrategico
**Arquivo:** `advogado.md`
**Papel:** Decide estrategia, escopo, rito e criterios de aceite. Coordena handoff ao `estagiario` via contrato. Revisa entregas e emite deltas.

**Responsabilidades exclusivas:**
- Triagem de dominio via `roteamento.md`
- Escolha do modo de operacao (`autonomo` ou `integrado`)
- Geracao do `contrato_decisao.md` (modo integrado)
- Revisao pos-escrita e deltas incrementais
- Comandos de controle (ver tabela abaixo)

**Nao faz:** Inventar dados; misturar ritos; escrever a peca (modo integrado).

### `estagiario` — Executor Contratual
**Arquivo:** `estagiario.md`
**Papel:** Redige a peca com base no contrato. Nao redefine estrategia. Executa deltas com intervencao minima.

**Responsabilidades exclusivas:**
- Redacao da peca conforme contrato + `estilo_juridico.md`
- Consulta a `minuta-base.md` para fragmentos de cabecalho e qualificacao (referencia de formatacao, nao heranca de template)
- Emissao de `Decisao Necessaria` quando faltar campo minimo
- Modo autonomo para documentos D sem ambiguidade estrategica
- Escalar ao `advogado` em caso de ambiguidade estrategica

**Nao faz:** Tomar decisao estrategica sem diretriz; reescrever trechos validados sem ordem expressa.

---

## Interface de Acoplamento: Contrato

**Arquivo:** `contrato_decisao.md`

Toda comunicacao entre agentes passa pelo contrato — sem acoplamento direto entre arquivos. Contem: escopo, regras de validacao, criterios de aceite, modo de operacao, dependencias e registro de deltas por rodada.

---

## Relacao entre Agentes e Minutas

| Agente | Arquivo | Funcao |
|--------|---------|--------|
| `advogado` | `roteamento.md` | Leitura obrigatoria na triagem |
| `advogado` | `contrato_decisao.md` | Gera (modo integrado) |
| `advogado` | `fontes.md` + verbetes + sumulas | Checagem antes do handoff |
| `estagiario` | `estilo_juridico.md` | Aplicacao em toda redacao |
| `estagiario` | `minuta-base.md` | Fragmentos de cabecalho e qualificacao (referencia, nao heranca) |
| `estagiario` | `minutas-imobiliarias.md` | Dom. A — Imobiliario |
| `estagiario` | `minutas-consumeristas.md` | Dom. B — Consumerista / JEC |
| `estagiario` | `minutas-civeis.md` | Dom. C — Civel + Replica |
| `estagiario` | `documentos.md` | Dom. D — CHO, PRO, DHI (autonomo) |
| `estagiario` | `minutas-intermediariais.md` | Dom. D — SUB, HAB, ACO, ALV, CPS (autonomo) |
| `estagiario` | `minutas-familia.md` | Dom. E — Familia e Sucessoes |
| `estagiario` | `remedios-constitucionais.md` | Dom. G — Remedios + MS |
| `estagiario` | `recursos-civeis.md` | Dom. R — Recursos Civeis |

---

## Arvore de Arquivos

```text
.
├── README.md
├── claude.json                        ← config dos agentes
│
├── — AGENTES —
├── advogado.md
├── estagiario.md
├── contrato_decisao.md
│
├── — ROTEAMENTO E ESTILO —
├── roteamento.md
├── estilo_juridico.md
├── minuta-base.md                     ← fragmentos de formatacao (cabecalho, qualificacao, fechamento)
│
├── — MINUTAS POR DOMINIO —
├── minutas-imobiliarias.md            ← Dom. A (10 pecas): RPO MPO IPR IPO REI CUS ANU PAF VIZ DMT
├── minutas-consumeristas.md           ← Dom. B (15 pecas): PI NEG PSC PSN TEL TRO TRB DIS CEL RPR OBF + RI CR ED AI
├── minutas-civeis.md                  ← Dom. C (3 pecas): ATR ALU REP
├── documentos.md                      ← Dom. D (3 docs): CHO PRO DHI
├── minutas-intermediariais.md         ← Dom. D (5 docs): SUB HAB ACO ALV CPS
├── minutas-familia.md                 ← Dom. E (12 pecas): NEP INP ALI EXA INV OFA UNE INT GUA VIS CUR DIV
├── remedios-constitucionais.md        ← Dom. G (4 pecas): AP HD HC MS
├── recursos-civeis.md                 ← Dom. R (6 pecas): APE AGI EDC AGR RES REX
│
├── — TEMPLATES DOCX —
├── replica_contestacao.docx           ← template REP
├── expedicao_alvara.docx              ← template ALV
├── cumprimento_sentenca.docx          ← template CPS
│
├── — FUNDAMENTACAO —
├── fontes.md
├── sumulas-vinculantes.md
├── verbetesSTF.md
├── verbetesSTJ.md
│
└── task.md                            ← backlog tecnico
```

---

## Inventario Completo de Pecas

| Dom. | Arquivo | Codigos | Total |
|------|---------|---------|-------|
| A | `minutas-imobiliarias.md` | RPO · MPO · IPR · IPO · REI · CUS · ANU · PAF · VIZ · DMT | 10 |
| B | `minutas-consumeristas.md` | PI · NEG · PSC · PSN · TEL · TRO · TRB · DIS · CEL · RPR · OBF · RI · CR · ED · AI | 15 |
| C | `minutas-civeis.md` | ATR · ALU · REP | 3 |
| D | `documentos.md` | CHO · PRO · DHI | 3 |
| D | `minutas-intermediariais.md` | SUB · HAB · ACO · ALV · CPS | 5 |
| E | `minutas-familia.md` | NEP · INP · ALI · EXA · INV · OFA · UNE · INT · GUA · VIS · CUR · DIV | 12 |
| G | `remedios-constitucionais.md` | AP · HD · HC · MS | 4 |
| R | `recursos-civeis.md` | APE · AGI · EDC · AGR · RES · REX | 6 |
| **TOTAL** | | | **58** |

> **Recursos JEC:** RI, CR, ED e AI permanecem em `minutas-consumeristas.md` por serem
> especificos do rito dos Juizados. Dom. R cobre exclusivamente o rito comum (CPC/2015)
> e os tribunais superiores (STJ/STF).

> **minuta-base.md:** biblioteca de fragmentos reutilizaveis (cabecalho JEC, cabecalho
> vara civel, qualificacao unica, fechamento padrao). Consultado pelo estagiario como
> referencia de formatacao — nao e template herdado pelas minutas individuais.

---

## Comandos de Controle (`advogado`)

| Comando | Acao |
|---------|------|
| `REINICIAR` | Retorna a triagem inicial |
| `REVISAR` | Revisao tecnica da peca atual |
| `GERAR CONTRATO HONORARIOS` | Fluxo CHO (autonomo) |
| `GERAR PROCURACAO` | Fluxo PRO (autonomo) |
| `GERAR DECLARACAO` | Fluxo DHI (autonomo) |
| `GERAR ACORDO` | Fluxo ACO (autonomo) |
| `GERAR SUBSTABELECIMENTO` | Fluxo SUB (autonomo) |
| `GERAR ALVARA` | Fluxo ALV — n° processo + dados bancarios |
| `GERAR CUMPRIMENTO` | Fluxo CPS — condenacao + memoria de calculo |
| `GERAR REPLICA` | Fluxo REP — teses da contestacao mapeadas |

---

## Fluxo de Operacao

```
1. Usuario descreve o caso
2. advogado le roteamento.md → identifica dominio e codigo
3. advogado coleta dados faltantes em blocos curtos
4. advogado define modo:
   ├─ AUTONOMO: estagiario redige diretamente (Dom. D sem ambiguidade estrategica)
   └─ INTEGRADO: advogado gera contrato_decisao.md → estagiario redige
5. estagiario entrega peca + checklist + pendencias
6. advogado revisa → delta incremental se necessario
```

---

## Backlog Tecnico

Ver `task.md`.


