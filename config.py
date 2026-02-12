# config.py - Módulo de Configurações do FiadoFácil
# Responsável por carregar e gerenciar as configurações do sistema

import json
import os

ARQUIVO_CONFIG = "config.json"

# Configurações padrão caso o arquivo não exista
CONFIG_PADRAO = {
    "empresa": {
        "nome": "Minha Loja de Conveniência",
        "telefone": "(00) 00000-0000"
    },
    "limite_fiado_padrao": 500.00,
    "backup_dir": "backups",
    "backup_automatico": True,
    "interface": {
        "tema": "claro",
        "font_size": 10,
        "largura_janela": 1200,
        "altura_janela": 700
    }
}

def carregar_config():
    """Carrega as configurações do arquivo JSON ou retorna as configurações padrão."""
    try:
        if os.path.exists(ARQUIVO_CONFIG):
            with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Mescla com config padrão para garantir que todas as chaves existam
                return {**CONFIG_PADRAO, **config}
        else:
            # Cria o arquivo de configuração padrão
            salvar_config(CONFIG_PADRAO)
            return CONFIG_PADRAO
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return CONFIG_PADRAO

def salvar_config(config):
    """Salva as configurações no arquivo JSON."""
    try:
        with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

def get_limite_padrao():
    """Retorna o limite de fiado padrão."""
    config = carregar_config()
    return config.get("limite_fiado_padrao", 500.00)

def get_config_interface():
    """Retorna as configurações de interface."""
    config = carregar_config()
    return config.get("interface", CONFIG_PADRAO["interface"])

def get_nome_empresa():
    """Retorna o nome da empresa."""
    config = carregar_config()
    return config.get("empresa", {}).get("nome", "FiadoFácil")
