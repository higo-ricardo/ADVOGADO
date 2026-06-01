# GUIA DE ROTEAMENTO E COLETA (FONTE UNICA)

Este arquivo e a fonte unica para triagem, codigo de peca, rito e coleta de dados obrigatorios.

---

## 1. TRIAGEM DE DOMINIOS

| Dominio | Triggers |
|---------|---------|
| A - Imobiliario | posse, esbulho, turbacao, reintegracao, interdito, imissao, reivindicatoria, usucapiao, vizinhanca, anulatoria, passagem forcada, demarcacao de terras, limites entre imoveis |
| B - Consumerista/JEC | CDC, consumidor, negativacao, plano de saude, telefonia, overbooking, distrato, corte de energia, vicio de produto, atraso de reparo, substituicao de produto, troca de produto |
| C - Civel | acidente de transito, aluguel atrasado, despejo, locacao, replica |
| D - Documentos e processuais de apoio | contrato de honorarios, procuracao, hipossuficiencia, substabelecimento, habilitacao, acordo, alvara, cumprimento de sentenca, penhora |
| F - Familia e Sucessoes | alimentos, paternidade, investigacao de paternidade, negatoria de paternidade, inventario, partilha, heranca, pensao alimenticia, execucao de alimentos, prisao civil por alimentos, oferta de alimentos, uniao estavel, interdicao, guarda, visitas, convivencia familiar, curatela, divorcio, dissolucao do casamento |
| G - Remedios Constitucionais | acao popular, habeas corpus, habeas data, patrimonio publico, dados pessoais, prisao ilegal, constrangimento ilegal, mandado de seguranca, ato coator, direito liquido e certo, autoridade publica |
| R - Recursos Civeis | apelacao, agravo de instrumento, recurso especial, recurso extraordinario, embargos de declaracao, agravo interno, prequestionamento, repercussao geral |

---

## 2. TRIAGEM DETALHADA POR TIPO DE PECA

### 2-A — Imobiliario (`minutas-imobiliarias.md`)

| Situacao | Codigo | Rito e notas |
|---------|--------|-------------|
| Perda de posse (esbulho) | RPO | < 1 ano e 1 dia: forca nova. >= 1 ano e 1 dia: forca velha |
| Posse perturbada (turbacao) | MPO | Mesma logica de forca nova/velha |
| Ameaca concreta a posse | IPR | Mesma logica de forca nova/velha |
| Proprietario sem posse previa | IPO | Ordinario |
| Reivindicacao de posse | REI | Ordinario |
| Contestacao em usucapiao | CUS | Ordinario |
| Direito de vizinhanca | VIZ | JEC (<=40 SM) ou ordinario |
| Anulatoria de negocio | ANU | Ordinario (decadencia 4 anos) |
| Passagem forcada | PAF | Ordinario |
| Demarcacao de terras | DMT | Ordinario — citar todos os confrontantes (art. 574, CPC) |

### 2-B — Consumerista/JEC (`minutas-consumeristas.md`)

| Codigo | Peca | Triggers |
|--------|------|---------|
| PI | Peticao inicial generica | produto nao entregue, servico nao prestado |
| NEG | Negativacao indevida | SPC, Serasa, fraude |
| PSC | Plano de saude (cancelamento) | cancelamento indevido |
| PSN | Plano de saude (negativa) | cobertura negada |
| TEL | Telefonia | bloqueio, internet, cobranca indevida |
| TRO | Transporte (pane) | atraso por pane |
| TRB | Transporte (overbooking) | pretericao de embarque |
| DIS | Distrato | recusa de cancelamento, multa abusiva |
| CEL | Corte de energia | interrupcao indevida |
| RPR | Demora de reparo | art. 18 CDC, prazo expirado |
| OBF | Obrigacao de fazer — substituicao de produto | vicio nao sanado, produto defeituoso, troca de produto, produto essencial |
| RI | Recurso inominado | prazo recursal JEC |
| CR | Contrarrazoes | resposta a recurso no JEC |
| ED | Embargos de declaracao (JEC) | omissao, contradicao, erro material — rito JEC |
| AI | Agravo interno (JEC) | decisao monocratica da Turma Recursal |

### 2-C — Civel (`minutas-civeis.md`)

| Codigo | Peca | Triggers |
|--------|------|---------|
| ATR | Acidente de transito | colisao, BO, conserto, lucros cessantes |
| ALU | Locacao/despejo | aluguel atrasado, despejo |
| REP | Replica a contestacao | resposta do autor as teses defensivas do reu |

### 2-D — Documentos e processuais de apoio

| Codigo | Documento | Arquivo | Uso padrao |
|--------|----------|---------|-----------|
| CHO | Contrato de honorarios advocaticios | `documentos.md` | formalizar relacao cliente-advogado |
| PRO | Procuracao ad judicia et extra | `documentos.md` | representacao processual |
| DHI | Declaracao de hipossuficiencia | `documentos.md` | gratuidade de justica |
| SUB | Substabelecimento | `minutas-intermediariais.md` | transferir/compartilhar poderes |
| HAB | Habilitacao de advogado | `minutas-intermediariais.md` | regularizar representacao no processo |
| ACO | Peticao de acordo | `minutas-intermediariais.md` | homologacao de transacao |
| ALV | Expedicao de alvara judicial | `minutas-intermediariais.md` | levantamento de valores apos penhora |
| CPS | Cumprimento de sentenca | `minutas-intermediariais.md` | penhora online / SISBAJUD |

### 2-F — Familia e Sucessoes (`minutas-familia.md`)

| Codigo | Peca | Fundamento |
|--------|------|-----------|
| NEP | Acao Negatoria de Paternidade | Arts. 1.601-1.605, CC |
| INP | Acao de Investigacao de Paternidade | Lei 8.560/92 + Art. 1.606, CC |
| ALI | Acao de Alimentos | Lei 5.478/68 + Arts. 1.694-1.710, CC |
| EXA | Execucao de Alimentos | Arts. 528-533, CPC (3 vias: prisao civil / folha / patrimonial) |
| INV | Acao de Inventario e Partilha | Arts. 610-673, CPC + Arts. 1.784-2.027, CC |
| OFA | Oferta de Alimentos | Arts. 1.694-1.710, CC + Lei 5.478/68 |
| UNE | Reconhecimento e Dissolucao de Uniao Estavel | Arts. 1.723-1.727, CC + Art. 226, p.3, CF |
| INT | Acao de Interdicao | Arts. 747-758, CPC + Arts. 1.767-1.783-A, CC + Lei 13.146/15 |
| GUA | Acao de Guarda | Arts. 1.583-1.590, CC + Arts. 693-699, CPC + ECA |
| VIS | Regulacao de Visitas / Regime de Convivencia | Arts. 1.589-1.590, CC + Art. 227, CF + ECA |
| CUR | Curatela (Prestacao de Contas / Revisao / Nascituro) | Arts. 1.767-1.783-A, CC + Arts. 747-763, CPC |
| DIV | Acao de Divorcio | Arts. 1.571-1.582, CC + Arts. 693-699, CPC + Art. 226, p.6, CF (EC 66/2010) |

### 2-G — Remedios Constitucionais + Mandado de Seguranca (`remedios-constitucionais.md`)

| Codigo | Peca | Fundamento |
|--------|------|-----------|
| AP | Acao Popular | Lei 4.717/65 + Art. 5º, LXXIII, CF |
| HD | Habeas Data | Lei 9.507/97 + Art. 5º, LXXII, CF |
| HC | Habeas Corpus | Art. 5º, LXVIII, CF + Arts. 647-667, CPP |
| MS | Mandado de Seguranca | Lei 12.016/09 + Art. 5º, LXIX, CF |

### 2-R — Recursos Civeis (`recursos-civeis.md`)

> Escopo: recursos do rito comum (CPC/2015) e dos tribunais superiores.
> Recursos do JEC (RI, CR, ED, AI) permanecem em `minutas-consumeristas.md`.

| Codigo | Peca | Fundamento |
|--------|------|-----------|
| APE | Apelacao Civel | Arts. 1.009-1.014, CPC/2015 |
| AGI | Agravo de Instrumento | Arts. 1.015-1.020, CPC/2015 (rol taxativo) |
| EDC | Embargos de Declaracao (rito comum) | Arts. 1.022-1.026, CPC/2015 |
| AGR | Agravo Interno (tribunais superiores / TJ / TRF) | Art. 1.021, CPC/2015 |
| RES | Recurso Especial | Art. 105, III, CF + Arts. 1.029-1.035, CPC/2015 |
| REX | Recurso Extraordinario | Art. 102, III, CF + Arts. 1.029-1.035, CPC/2015 |

---

## 3. DADOS OBRIGATORIOS POR CODIGO

| Codigo | Dados adicionais obrigatorios |
|--------|------------------------------|
| RPO/MPO/IPR | data do fato, historico da posse, atos do reu, prova documental |
| IPO/REI | titulo registrado, matricula, cadeia dominial |
| CUS | numero do processo, area, cadeia possessoria/dominial |
| ANU | documento viciado, data, tipo de vicio, terceiro de boa-fe |
| PAF | imovel serviente, proposta de indenizacao |
| DMT | matriculas dos imoveis confrontantes, todos os confrontantes para citacao, existencia de marcos, laudo ou planta tecnica disponivel, cumulacao com divisao |
| NEG | credor, valor, data de descoberta, impactos |
| CEL | UC, data/hora do corte, adimplencia |
| RPR | produto, data de assistencia, prazo de 30 dias |
| OBF | produto (marca/modelo/NF), data da compra, valor, data do vicio, datas e ordens de servico das visitas tecnicas, produto essencial (sim/nao), danos materiais colaterais, opcao pela substituicao declarada |
| ALU | debitos, fiadores, ocupacao atual do imovel |
| ATR | data/hora/local, BO, danos, orcamentos |
| CHO | qualificacao do cliente, objeto preciso do servico, modalidade (fixo/exito/misto), valor ou percentual, forma de pagamento, destino dos honorarios sucumbenciais |
| PRO | qualificacao do outorgante, CPF, poderes especiais, dados dos outorgados |
| SUB | dados do substabelecente/substabelecido, reserva de poderes, processo |
| HAB | numero do processo, dados do novo patrono, pedido de intimacao exclusiva |
| DHI | qualificacao do declarante, fundamento da hipossuficiencia, assinatura |
| ACO | partes, objeto, valor, forma de pagamento, clausulas de quitacao |
| REP | numero do processo, resumo das teses da contestacao, preliminares arguidas, documentos juntados pelo reu |
| ALV | numero do processo, ID da penhora/deposito, valor penhorado, dados bancarios completos, procuracao com poderes de receber e dar quitacao |
| CPS | numero do processo, data da sentenca, valor da condenacao, datas-base para correcao, CNPJ/CPF do executado, dados bancarios do exequente |
| NEP | data do registro, tipo (presuncao/voluntario/erro), resultado DNA se disponivel, existencia de vinculo socioafetivo, obrigacao alimentar em curso |
| INP | data do nascimento, relacionamento das partes, DNA disponivel, dados do investigado |
| ALI | vinculo de parentesco/conjugal, renda do alimentante, necessidades do alimentando, outros filhos do alimentante |
| EXA | via escolhida (prisao civil/folha/patrimonial), titulo executivo, debito calculado por parcela, empregador do executado |
| INV | certidao de obito, herdeiros e qualificacoes completas, bens com matriculas/placas/saldos, dividas do espolio |
| OFA | vinculo entre as partes, rendimentos liquidos do ofertante, outros dependentes, valor ofertado em % e R$, forma de pagamento |
| UNE | periodo da UP (inicio e fim), regime de bens, bens adquiridos na constancia, filhos comuns, dependencia economica |
| INT | causa do art. 1.767 CC (qual inciso), laudo medico recente, curador indicado, bens do interditando, endereco para citacao |
| GUA | modalidade (compartilhada/unilateral), domicilio do menor, situacao do outro genitor, alimentos a cumular |
| VIS | guarda atual (de fato ou judicial), cidades dos genitores, proposta de regime completo (regular+ferias+feriados), historico de conflitos |
| CUR | modalidade (prestacao/revisao/nascituro), processo de interdicao original, periodo da prestacao, laudo medico para revisao |
| DIV | modalidade (consensual/litigioso), certidao de casamento, regime de bens, filhos menores (nomes e idades), bens a partilhar, alimentos entre conjuges, retomada de nome |
| APE | numero do processo e vara de origem, data da sentenca, capitulos impugnados, pedido de efeito suspensivo, necessidade de causa madura |
| AGI | numero do processo e vara de origem, data da decisao interlocutoria, inciso do art. 1.015 aplicavel, pedido de tutela recursal |
| EDC | numero do processo, data da decisao embargada, tipo de vicio (omissao/contradicao/obscuridade/erro material), ponto especifico impugnado, pedido de efeito infringente |
| AGR | numero do processo, tribunal e camara/turma, data da decisao monocratica, hipotese do art. 932 invocada pelo relator, paradigma distinguido se houver |
| RES | numero do processo e tribunal de origem, data do acordao, alinea aplicavel (a ou c), questao federal e norma violada, prequestionamento verificado, paradigma para divergencia se alinea c |
| REX | numero do processo e tribunal de origem, data do acordao, alinea aplicavel, questao constitucional, prequestionamento verificado, tema de repercussao geral reconhecida se houver |
| AP | titulo de eleitor do autor, ato lesivo identificado, valor do dano, todos os reus (entidade + agente + beneficiario) |
| HD | pedido administrativo previo e recusa documentada, tipo de dado (conhecimento/retificacao/anotacao), entidade detentora |
| HC | paciente e autoridade coatora, especie (liberatorio/preventivo/trancamento), hipotese do art. 648 CPP, prazo da prisao |
| MS | autoridade coatora (nome+cargo+orgao), ato impugnado, norma violada, data do ato (prazo de 120 dias) |

---

## 4. REGRAS GERAIS DE EXECUCAO

- Confirmar rito e codigo antes da redacao final.
- Nao inventar dados; usar `[A PREENCHER]`.
- Valor da causa por algarismos e por extenso quando aplicavel.
- Em possessorias, observar fungibilidade e criterio temporal de forca nova/velha.
- Em documentos D (CHO, PRO, DHI, SUB, HAB, ACO, ALV, CPS), permitir modo autonomo do `estagiario` quando nao houver ambiguidade estrategica.
- Em CHO: definir modalidade (fixo/exito/misto) e destino dos honorarios sucumbenciais antes de redigir.
- Em REP: o `advogado` deve mapear as teses ANTES de delegar — nao delegar REP sem briefing completo.
- Em CPS: incluir memoria de calculo com IPCA + juros 1%/mes desde a data-base da sentenca.
- Em ALV: verificar se penhora e o alvara sao do mesmo processo ou se ha processo separado de honorarios.
- Em EXA: escolher a via ANTES de redigir — prisao civil (3 ultimas parcelas) / folha / patrimonial.
- Em OFA: demonstrar o trinomio necessidade+possibilidade+proporcionalidade com valores concretos antes de gerar o contrato.
- Em UNE: identificar TODOS os bens adquiridos na constancia e verificar se ha filhos menores (MP obrigatorio).
- Em INT: verificar se tomada de decisao apoiada (TDA) nao seria suficiente antes de propor interdicao.
- Em GUA: guarda compartilhada e a REGRA — guarda unilateral exige fundamento especifico e concreto.
- Em VIS: proposta de regime deve contemplar periodo regular + ferias + feriados + datas especiais + transporte.
- Em CUR: identificar a modalidade (prestacao/revisao/nascituro) antes de redigir — sao estruturas distintas.
- Em DMT: verificar se e demarcacao (limites incertos) ou reivindicatoria (limites conhecidos, invasao identificada) — erro de enquadramento causa extincao sem merito. Tutela de urgencia SEMPRE presente — descrever a hipotese (obra/marcos/invasao) em DO DIREITO antes de gerar os pedidos.
- Em OBF: confirmar a opcao do consumidor (substituicao) antes de redigir — para restituicao usar RPR. Tutela de urgencia SEMPRE presente. Identificar produto essencial para invocar art. 18, §3º, CDC.
- Em APE/AGI/EDC/AGR: verificar prequestionamento e prazo antes de qualquer outra etapa.
- Em RES: confirmar que a questao e de direito federal (nao factual) e que ha prequestionamento no acordao recorrido.
- Em REX: demonstrar repercussao geral em topico proprio — requisito constitucional obrigatorio.












