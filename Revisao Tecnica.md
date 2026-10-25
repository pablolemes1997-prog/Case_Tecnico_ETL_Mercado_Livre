# Revisão técnica

**Autor: Pablo Felix**

## Correções de lógica
| Problema | Correção |
|---|---|
| Garantia vazia/nula contava como "com garantia" | `has_warranty` só é 1 se houver texto diferente de "Sin garantía"; usa `sale_terms` como alternativa |
| Taxa ARS aplicada a qualquer moeda | Uma taxa por moeda, guardada em `etl_currency_rates` |
| Busca de produtos lia só a primeira página | Paginação genérica com `limit`/`offset` e total da API |
| Token renovado não era usado na mesma execução | Atualiza também o ambiente do processo; renovação automática em 401 |
| Faltava a troca do `code` por tokens | `garantir_tokens()` usa `ML_CODE` na 1ª execução e o remove do `.env` |
| Uma chamada por item e sem parada em 403 | Lotes de 20 itens e interrupção em 401/403 |
| Erros engolidos com `print` | Exceções próprias, logs e código de saída |
| Dados sujos/duplicados poderiam quebrar a carga | Validação antes da carga |
| Modelo sem relacionamentos | Três tabelas com chaves primárias, estrangeiras e índices |

## Riscos
- **HTTP 403 em `/items`** impede responder à pergunta 2 (depende da permissão da aplicação).
- **Code de uso único**: se expirar, gerar outro com `autenticar.py`.
- **Credenciais**: nunca versionar o `.env`; se o Client Secret foi compartilhado, gere um novo no DevCenter.
- **Mudanças nos campos da API** (`warranty`, `shipping`) podem exigir ajustes na transformação.
- **SQLite**: adequado para execução local; não atende concorrência.
