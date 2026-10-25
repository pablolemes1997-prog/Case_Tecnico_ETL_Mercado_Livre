# Arquitetura

**Autor: Pablo Felix**

## Camadas

| Pasta | Responsabilidade |
|---|---|
| `[001] - Configuracoes` | Lê o `.env` e centraliza URL, endpoints, paginação, produto pesquisado, banco e opções do ETL |
| `[002] - Autenticacao API` | Todo o OAuth: code, access token, refresh token e gravação no `.env` |
| `[003] - Extracao` | Cliente HTTP (retry, renovação de token em 401, paginação), publicações, itens em lote e moedas |
| `[004] - Transformacao` | Regras de negócio (USD, garantia, envio) e validação de qualidade |
| `[005] - Carga` | Gravação transacional e em lote |
| `[006] - Banco de Dados` | `ddl.sql`, conexão com chaves estrangeiras ativas e criação das tabelas |
| `[007] - Consultas SQL` | Queries do desafio e gerador de resultados |
| `[008] - Utilitarios` | Exceções, logs e arquivos intermediários |
| `[009] - Documentacao` | Respostas do case e documentação técnica |

`executar.py` orquestra as etapas e define o `JOB_RUN`. Cada módulo depende apenas das camadas inferiores (configurações e utilitários), o que mantém as responsabilidades separadas.

## Tratamento de erros

- Hierarquia `ErroPipeline` → `ErroConfiguracao`, `ErroAutenticacao`, `ErroApi`, `ErroBancoDados`, `ErroEtapaAnterior`.
- Falhas pontuais (um produto, uma taxa, detalhes de itens) geram aviso e o ETL continua; falhas estruturais interrompem com código de saída `1`.
- Transações com commit/rollback; a carga de três tabelas é atômica.

## Desempenho

Sessão HTTP reutilizada, novas tentativas com *backoff* (429/5xx), detalhes de itens em lotes de 20, uma consulta de câmbio por moeda e carga com `executemany`. Em caso de 401/403 em `/items`, a extração para de insistir.

## Segurança

Credenciais somente em variáveis de ambiente (`.env` fora do Git); tokens nunca vão para os logs; respostas de erro da API são truncadas.
