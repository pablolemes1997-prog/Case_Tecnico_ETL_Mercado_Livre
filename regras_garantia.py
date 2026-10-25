"""Regras de negócio da garantia."""
import unicodedata


def normalizar_texto(texto):
    """Deixa o texto em minúsculas e sem acentos, para facilitar comparações."""
    texto_decomposto = unicodedata.normalize("NFKD", texto or "")
    letras_sem_acento = [letra for letra in texto_decomposto if not unicodedata.combining(letra)]
    return "".join(letras_sem_acento).lower().strip()


def extrair_texto_garantia(publicacao):
    """Texto da garantia: usa o campo 'warranty' ou, se estiver vazio, os termos de venda."""
    if publicacao.get("warranty"):
        return publicacao["warranty"]
    termos_de_venda = {
        termo.get("id"): termo.get("value_name") for termo in publicacao.get("sale_terms") or []
    }
    partes = [termos_de_venda.get("WARRANTY_TYPE"), termos_de_venda.get("WARRANTY_TIME")]
    return " - ".join(parte for parte in partes if parte) or None


def possui_garantia(texto_garantia):
    """Retorna True somente se houver texto e ele não indicar 'sem garantia'."""
    texto = normalizar_texto(texto_garantia)
    return bool(texto) and not texto.startswith("sin garantia")
