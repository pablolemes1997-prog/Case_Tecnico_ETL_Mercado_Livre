"""Leitura e gravação dos arquivos intermediários entre as etapas."""
import json

from excecoes import ErroEtapaAnterior


def salvar_json(dados, caminho_arquivo):
    """Grava os dados em JSON, criando a pasta se necessário."""
    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, indent=2, default=str)
    caminho_arquivo.write_text(texto, encoding="utf-8")
    return caminho_arquivo


def ler_json(caminho_arquivo):
    """Lê um JSON gerado por uma etapa anterior."""
    if not caminho_arquivo.exists():
        raise ErroEtapaAnterior(
            f"Arquivo {caminho_arquivo.name} não encontrado. Execute a etapa anterior primeiro."
        )
    return json.loads(caminho_arquivo.read_text(encoding="utf-8"))
