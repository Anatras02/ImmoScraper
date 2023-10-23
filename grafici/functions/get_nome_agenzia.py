from config.definitions import AGENZIE


def get_nome_agenzia(id_agenzia):
    for agenzia in AGENZIE:
        if agenzia["id"] == id_agenzia:
            return agenzia["nome"]

    return None