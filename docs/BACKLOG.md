# Backlog

## ✅ Concluído (v2.0.0)
- [x] Implementar Clean Architecture com separação em camadas
- [x] Criar API REST com FastAPI desacoplada do Streamlit
- [x] Implementar Rate Limiting para chamadas à API LLM
- [x] Implementar validação de inputs do usuário (XSS, tamanho, caracteres)
- [x] Extrair CSS e temas para módulo dedicado (`ui/themes.py`)
- [x] Criar testes de integração para a API REST
- [x] Documentar arquitetura e endpoints da API

## Alta prioridade
- [ ] Expandir RAG para domínios Consumeristas, Recursos e Remédios Constitucionais
- [ ] Ajustar `knowledge.py` para mapear todos os códigos às subpastas corretas
- [ ] Corrigir eventuais links quebrados nas referências entre minutas
- [ ] Implementar autenticação JWT na API REST
- [ ] Adicionar suporte a múltiplas sessões simultâneas

## Média prioridade
- [ ] Corrigir bug de encoding no Windows ao digitar acentos
- [ ] Adicionar loading state durante indexação do RAG
- [ ] Padronizar numeração dos pedidos após inserções manuais
- [ ] Implementar cache de respostas LLM para reduzir custos
- [ ] Criar dashboard administrativo para monitoramento da API

## Baixa prioridade
- [ ] Adicionar testes unitários para `rag.py` e `text_utils.py`
- [ ] Melhorar mensagens de erro para arquivos `.md` ausentes
- [ ] Documentar como usar o `.env` após divisão das minutas
- [ ] Implementar exportação de documentos em PDF
- [ ] Adicionar suporte a webhooks para notificações
