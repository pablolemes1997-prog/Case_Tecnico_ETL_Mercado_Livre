"""Executa as consultas de consultas.sql e grava o resultado em Markdown.

Saída: [009] - Documentacao/Resultados da Ultima Execucao.md
"""
from datetime import datetime

from conexao_banco import conectar_banco
from configuracoes import ARQUIVO_CONSULTAS_SQL, ARQUIVO_RESULTADOS


def _ler_consultas():
    """Separa o arquivo em blocos '-- QUESTÃO' e devolve [(título, sql)]."""
    blocos = ARQUIVO_CONSULTAS_SQL.read_text(encoding="utf-8").split("-- QUESTÃO")[1:]
    consultas = []
    for bloco in blocos:
        linhas = bloco.splitlines()
        titulo = "QUESTÃO" + linhas[0]
        comando_sql = "\n".join(
            linha for linha in linhas[1:] if not linha.strip().startswith("--")
        ).strip()
        consultas.append((titulo, comando_sql))
    return consultas


def _montar_tabela_markdown(nomes_colunas, linhas):
    """Transforma o resultado de uma consulta em tabela Markdown."""
    if not linhas:
        return "_Sem registros (ex.: quantidade vendida nula quando /items retorna HTTP 403)._"
    cabecalho = "| " + " | ".join(nomes_colunas) + " |\n|" + "---|" * len(nomes_colunas)
    corpo = "\n".join("| " + " | ".join(str(valor) for valor in linha) + " |" for linha in linhas)
    return f"{cabecalho}\n{corpo}"


def gerar_resultados():
    """Roda todas as consultas na última execução e grava o arquivo de resultados."""
    secoes = [f"# Resultados da última execução\n\nGerado em {datetime.now():%d/%m/%Y %H:%M:%S}.\n"]
    with conectar_banco() as conexao:
        job_run, total_publicacoes = conexao.execute(
            "SELECT MAX(JOB_RUN), COUNT(*) FROM etl_publications "
            "WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)"
        ).fetchone()
        secoes.append(f"JOB_RUN: `{job_run}` — {total_publicacoes} publicações.\n")
        for titulo, comando_sql in _ler_consultas():
            cursor = conexao.execute(comando_sql)
            nomes_colunas = [coluna[0] for coluna in cursor.description]
            tabela = _montar_tabela_markdown(nomes_colunas, cursor.fetchall())
            secoes.append(f"## {titulo}\n\n```sql\n{comando_sql}\n```\n\n{tabela}\n")
    ARQUIVO_RESULTADOS.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_RESULTADOS.write_text("\n".join(secoes), encoding="utf-8")
    return ARQUIVO_RESULTADOS
