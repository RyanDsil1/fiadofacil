#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FiadoFácil - Sistema de Gestão de Crédito Informal
===================================================

Trabalho de Conclusão de Curso (TCC)
Desenvolvimento de Sistemas, 2024/2

Autores:
    - Ryan Rodrigues
    - Diogo
    - Fernanda

Orientador: Rodrigo Bruno Kehdy

Descrição:
    Sistema desktop desenvolvido em Python com Interface Gráfica Tkinter
    e banco de dados SQLite para gestão de crédito informal (fiado)
    em pequenos comércios.

Requisitos:
    - Python 3.8 ou superior
    - Bibliotecas padrão: tkinter, sqlite3, json, csv

Uso:
    python main.py
"""

import tkinter as tk
from datetime import datetime
import os

# Importar módulos do sistema
import database as db
from gui import FiadoFacilApp
from config import carregar_config

def fazer_backup_automatico():
    """Realiza backup automático se configurado."""
    config = carregar_config()
    if config.get('backup_automatico', True):
        backup_file = db.fazer_backup()
        if backup_file:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Backup automático: {backup_file}")

def main():
    """Função principal do sistema."""
    print("=" * 50)
    print("  FiadoFácil - Sistema de Gestão de Crédito")
    print("=" * 50)
    print()
    
    # Inicializar banco de dados
    print("[INFO] Inicializando banco de dados...")
    db.inicializar_banco()
    
    # Fazer backup automático ao iniciar
    print("[INFO] Verificando backup automático...")
    fazer_backup_automatico()
    
    # Criar janela principal
    print("[INFO] Iniciando interface gráfica...")
    root = tk.Tk()
    
    # Configurar ícone (se existir)
    try:
        if os.path.exists("icon.ico"):
            root.iconbitmap("icon.ico")
    except:
        pass
    
    # Iniciar aplicação
    app = FiadoFacilApp(root)
    
    print("[INFO] Sistema iniciado com sucesso!")
    print()
    print("Pressione Ctrl+C no terminal para encerrar.")
    print()
    
    # Loop principal
    root.mainloop()
    
    # Fazer backup ao fechar
    print("\n[INFO] Encerrando sistema...")
    fazer_backup_automatico()
    print("[INFO] Sistema encerrado com sucesso!")

if __name__ == "__main__":
    main()
