### [ARQUIVO: acao_anulatoria_documento.md]

# Minuta: Ação Anulatória de Escritura Pública / Documento

## Código: ANU | CC/2002 (arts. 138–184) + CPC/2015 (arts. 319 ss.) | Vara Cível — Procedimento Comum

---

## Distinção Fundamental

| Situação | Ação correta |
|----------|-------------|
| Escritura pública com vício de consentimento (dolo, coação, erro, lesão, estado de perigo) | **ANU** (anulabilidade — art. 171, CC) — prazo decadencial 4 anos (art. 178, CC) |
| Escritura pública com vício de nulidade absoluta (simulação, objeto ilícito, incapacidade absoluta, fraude à lei) | **ANU** com fundamento em nulidade (art. 166, CC) — imprescritível (art. 169, CC) |
| Título válido, mas possuidor terceiro sem causa | **REI** — Reivindicatória |
| Escritura lavrada por quem não era dono (fraude na cadeia dominial) | **ANU** cumulada com **REI** ou registro indevido |
| Cancelamento de registro de imóvel por outro fundamento | Ação de Cancelamento de Registro (Lei 6.015/73, art. 250) |

> ⚠️ **Prazo decadencial crítico:**
> - Anulabilidade (vício de consentimento): **4 anos** contados da celebração do ato ou da cessação da coação (art. 178, CC).
> - Nulidade absoluta: **imprescritível** — pode ser arguida a qualquer tempo (art. 169, CC).
> - Verificar prazo ANTES de redigir. Usar python_tool se necessário.

> ⚠️ **Terceiro de boa-fé:** se o bem foi transferido a terceiro de boa-fé a título oneroso após o ato viciado, a tutela real pode ser inviável (art. 172, CC e Súm. 375, STJ). Alertar o cliente — tutela pode ser apenas ressarcitória.

---

## Checklist pré-redação

- [ ] Qual o documento viciado? (escritura pública de compra e venda, doação, procuração, contrato particular)
- [ ] Qual o vício? (dolo, coação, simulação, lesão, estado de perigo, incapacidade, fraude)
- [ ] Vício = anulabilidade (art. 171) ou nulidade absoluta (art. 166)?
- [ ] Data da celebração do ato — prazo decadencial ainda vigente?
- [ ] Imóvel ainda está no nome do réu ou foi repassado a terceiro?
- [ ] Há cadeia de transmissões após o ato viciado?
- [ ] Há terceiro adquirente de boa-fé a título oneroso?
- [ ] O autor pretende recuperar o imóvel (tutela real) ou apenas ressarcimento?
- [ ] Há registro no CRI a cancelar? (cumular pedido de cancelamento)
- [ ] Há danos materiais e morais?
- [ ] Gratuidade de justiça?
- [ ] Parte autora é idosa? → tramitação prioritária

---

## Estrutura Obrigatória da Peça

### 1. CABEÇA
```
EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA [__] VARA CÍVEL
DA COMARCA DE [COMARCA] — ESTADO DO [ESTADO]
```

### 2. QUALIFICAÇÃO E TIPO DE AÇÃO
```
[NOME COMPLETO DO AUTOR], [QUALIFICAÇÃO COMPLETA DO AUTOR], por seu advogado constituído,
vem, respeitosamente, à presença de Vossa Excelência, com fundamento nos arts. [166/171]
do Código Civil c/c arts. 319 e seguintes do Código de Processo Civil, propor a presente

AÇÃO ANULATÓRIA DE [ESCRITURA PÚBLICA / CONTRATO / DOCUMENTO]
C/C CANCELAMENTO DE REGISTRO E INDENIZAÇÃO POR DANOS MATERIAIS E MORAIS

em face de [NOME RÉU], [QUALIFICAÇÃO RÉU], pelos motivos a seguir expostos.
```

---

### 3. DOS FATOS

```
§1º — [CONTEXTO E RELAÇÃO ENTRE AS PARTES]
O(A) Autor(a) F o(a) Réu(ré) [dFscrFvFr a rFlação antFrior: familiar, negocial, de confiança etc.].
Em [DATA], foi lavrada perante o [CARTÓRIO], a [ESCRITURA PÚBLICA DE X / CONTRATO DE Y],
pelo qual [descrever o conteúdo do ato: transferência do imóvel situado em X, pelo valor de R$ Y etc.].
O documento foi registrado sob a matrícula nº [NÚMERO], no [CARTÓRIO DE REGISTRO DE IMÓVEIS DA COMARCA DE X].

§2º — [DO VÍCIO]
Ocorre que o ato jurídico ora impugnado padece de vício de [DOLO / COAÇÃO / SIMULAÇÃO /
LESÃO / ESTADO DE PERIGO / INCAPACIDADE], nos termos do art. [X] do Código Civil,
conforme se demonstra:

[Descrição detalhada do vício:
- Se DOLO: como o réu induziu o autor em erro; quais as manobras fraudulentas; provas
- Se COAÇÃO: qual a ameaça; como foi exercida; como afetou a vontade do autor
- Se SIMULAÇÃO: qual a aparência vs. realidade do negócio; o negócio foi fictício ou dissimulou outro?
- Se LESÃO: premência da necessidade ou inexperiência do autor; desproporção das prestações
- Se INCAPACIDADE: causa da incapacidade à época do ato; laudos médicos; interdição posterior?]

§3º — [DOS DANOS]
Em razão do ato viciado, o(a) Autor(a) sofreu os seguintes prejuízos:
(i)  Danos materiais: perda do imóvel avaliado em R$ [VALOR]; gastos com [X]: R$ [VALOR];
(ii) Danos morais: [descrição do sofrimento, abalo emocional, impacto na vida do autor].
```

---

### 4. DO DIREITO

#### 4.1 Do Vício do Negócio Jurídico

```
[Se ANULABILIDADE — art. 171:]
O negócio jurídico é anulável, nos termos do art. 171, II, do Código Civil,
por vício resultante de [dolo (art. 145)/coação (art. 151)/lesão (art. 157)/estado de perigo (art. 156)].

Verificada a presença de todos os requisitos legais do vício alegado — [descrever sucintamente] —,
impõe-se a decretação da anulação do ato, com efeito ex tunc, restituindo as partes ao
estado anterior (art. 182, CC).

[Se NULIDADE ABSOLUTA — art. 166:]
O negócio jurídico é nulo de pleno direito, nos termos do art. 166, [I a VII], do Código Civil,
por [simulação (art. 167) / objeto ilícito / fraude à lei / incapacidade absoluta].
A nulidade absoluta é imprescritível (art. 169, CC) e pode ser decretada de ofício pelo juízo
(art. 168, CC), independentemente de provocação das partes.
```

#### 4.2 Do Cancelamento do Registro

```
Decretada a anulação/nulidade do ato, impõe-se o cancelamento do registro do imóvel
perante o Cartório de Registro de Imóveis, nos termos do art. 250, I, da Lei 6.015/73
(Lei de Registros Públicos), restituindo-se a matrícula ao nome do(a) Autor(a).
```

#### 4.3 Da Indenização por Danos Materiais e Morais

```
O ato viciado praticado pelo(a) Réu(ré) constitui ato ilícito (art. 186, CC),
impondo-lhe o dever de reparar integralmente os danos causados (art. 927, CC), incluindo:
- Danos materiais: R$ [VALOR] (restituição / perdas e danos — art. 182 c/c 944 CC);
- Danos morais: arbitramento equitativo pelo juízo (Súm. 37, STJ).
```

#### 4.4 Do Prazo Decadencial (se anulabilidade)

```
O prazo decadencial de 4 (quatro) anos previsto no art. 178 do Código Civil começa a fluir
da data da celebração do ato, ocorrida em [DATA]. O ajuizamento da presente ação em [DATA]
se dá dentro do prazo legal, sendo a demanda tempestiva.
```

---

### 5. DOS PEDIDOS (ESPECÍFICOS)

```
E. A declaração de [ANULAÇÃO / NULIDADE] da [Escritura Pública / Contrato] por vício de [VÍCIO], com efeito retroativo (ex tunc);

F. O cancelamento do registro do imóvel na matrícula nº [NÚMERO], com expedição de mandado ao RI (art. 250, I, Lei 6.015/73);

G. A condenação do(a) réu(ré) ao pagamento de indenização por danos materiais (R$ [VALOR]) e danos morais (R$ [VALOR]);

H. A concessão da gratuidade de justiça (art. 98, CPC).

I. A dispensa da audiência de conciliação, nos termos do art. 319, VII, CPC, por inviável a autocomposição em razão da complexidade do conflito fundiário.

Atribui-se à causa o valor de R$ [VALOR] ([por extenso]).

[COMARCA]/[ESTADO], [DATA].

Pede deferimento.

[NOME DO ADVOGADO]
OAB/[UF] nº [NÚMERO]
```

---

## Base Normativa (ANU)

| Artigo | Diploma | Aplicação |
|--------|---------|-----------|
| Art. 104 | CC/2002 | Requisitos de validade do negócio jurídico |
| Art. 138–148 | CC/2002 | Vícios de consentimento (erro, dolo, coação) |
| Art. 156–157 | CC/2002 | Estado de perigo e lesão |
| Art. 166–167 | CC/2002 | Nulidade absoluta e simulação |
| Art. 169 | CC/2002 | Imprescritibilidade da nulidade |
| Art. 171 | CC/2002 | Causas de anulabilidade |
| Art. 172 | CC/2002 | Possibilidade de confirmação do ato anulável |
| Art. 178 | CC/2002 | Prazo decadencial de 4 anos (anulabilidade) |
| Art. 182 | CC/2002 | Efeito ex tunc — restituição ao estado anterior |
| Art. 186 + 927 | CC/2002 | Responsabilidade civil / dever de indenizar |
| Art. 944 | CC/2002 | Extensão da indenização |
| Art. 250, I | Lei 6.015/73 | Cancelamento do registro imobiliário |
| Súm. 37 | STJ | Cumulação de danos material e moral |
| Súm. 375 | STJ | Presunção de boa-fé do terceiro adquirente |

---

## Checklist de Validação Final (ANU)

- [ ] Vício identificado e enquadrado (anulabilidade ou nulidade)?
- [ ] Prazo decadencial verificado (e cálculo realizado com python_tool se necessário)?
- [ ] Terceiro de boa-fé analisado (alerta ao cliente se aplicável)?
- [ ] Pedido de cancelamento de registro incluído?
- [ ] Pedido de indenização por danos materiais e morais incluído?
- [ ] Valor da causa (imóvel + danos) indicado em algarismos e por extenso?
- [ ] Fundamento: art. 166 (nulidade) ou art. 171 (anulabilidade) — não misturar?

---
---