# database.py - Módulo de Banco de Dados do FiadoFácil
# Responsável por todas as operações com SQLite

import sqlite3
import os
import shutil
from datetime import datetime
from config import carregar_config, get_limite_padrao

ARQUIVO_DB = "fiado_facil.db"

def get_conexao():
    """Retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(ARQUIVO_DB)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def inicializar_banco():
    """Cria as tabelas do banco de dados se não existirem."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            limite_fiado REAL DEFAULT 500.00,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabela de Transações (Dívidas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            pago INTEGER DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    # Tabela de Pagamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            observacao TEXT,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

# ==================== OPERAÇÕES COM CLIENTES ====================

def adicionar_cliente(nome, telefone="", limite_fiado=None):
    """Adiciona um novo cliente ao banco de dados."""
    if limite_fiado is None:
        limite_fiado = get_limite_padrao()
    
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO clientes (nome, telefone, limite_fiado)
        VALUES (?, ?, ?)
    ''', (nome, telefone, limite_fiado))
    
    cliente_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return cliente_id

def atualizar_cliente(cliente_id, nome, telefone, limite_fiado):
    """Atualiza os dados de um cliente existente."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE clientes 
        SET nome = ?, telefone = ?, limite_fiado = ?
        WHERE id = ?
    ''', (nome, telefone, limite_fiado, cliente_id))
    
    conn.commit()
    conn.close()

def excluir_cliente(cliente_id):
    """Marca um cliente como inativo (exclusão lógica)."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE clientes SET ativo = 0 WHERE id = ?', (cliente_id,))
    
    conn.commit()
    conn.close()

def buscar_clientes(termo=""):
    """Busca clientes por nome ou telefone."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    if termo:
        cursor.execute('''
            SELECT * FROM clientes 
            WHERE ativo = 1 AND (nome LIKE ? OR telefone LIKE ?)
            ORDER BY nome
        ''', (f'%{termo}%', f'%{termo}%'))
    else:
        cursor.execute('SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome')
    
    clientes = cursor.fetchall()
    conn.close()
    
    return clientes

def buscar_cliente_por_id(cliente_id):
    """Busca um cliente específico pelo ID."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
    cliente = cursor.fetchone()
    
    conn.close()
    return cliente

# ==================== OPERAÇÕES COM TRANSAÇÕES ====================

def adicionar_transacao(cliente_id, descricao, valor):
    """Registra uma nova transação (venda fiada)."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transacoes (cliente_id, descricao, valor)
        VALUES (?, ?, ?)
    ''', (cliente_id, descricao, valor))
    
    transacao_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return transacao_id

def buscar_transacoes_cliente(cliente_id):
    """Busca todas as transações de um cliente."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM transacoes 
        WHERE cliente_id = ?
        ORDER BY data DESC
    ''', (cliente_id,))
    
    transacoes = cursor.fetchall()
    conn.close()
    
    return transacoes

# ==================== OPERAÇÕES COM PAGAMENTOS ====================

def adicionar_pagamento(cliente_id, valor, observacao=""):
    """Registra um novo pagamento."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO pagamentos (cliente_id, valor, observacao)
        VALUES (?, ?, ?)
    ''', (cliente_id, valor, observacao))
    
    pagamento_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return pagamento_id

def buscar_pagamentos_cliente(cliente_id):
    """Busca todos os pagamentos de um cliente."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM pagamentos 
        WHERE cliente_id = ?
        ORDER BY data DESC
    ''', (cliente_id,))
    
    pagamentos = cursor.fetchall()
    conn.close()
    
    return pagamentos

# ==================== CÁLCULOS E RELATÓRIOS ====================

def calcular_saldo_cliente(cliente_id):
    """Calcula o saldo devedor de um cliente (Transações - Pagamentos)."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    # Soma das transações (dívidas)
    cursor.execute('''
        SELECT COALESCE(SUM(valor), 0) as total_dividas
        FROM transacoes 
        WHERE cliente_id = ? AND pago = 0
    ''', (cliente_id,))
    total_dividas = cursor.fetchone()['total_dividas']
    
    # Soma dos pagamentos
    cursor.execute('''
        SELECT COALESCE(SUM(valor), 0) as total_pagamentos
        FROM pagamentos 
        WHERE cliente_id = ?
    ''', (cliente_id,))
    total_pagamentos = cursor.fetchone()['total_pagamentos']
    
    conn.close()
    
    saldo = total_dividas - total_pagamentos
    return max(0, saldo)  # Não pode ser negativo

def buscar_historico_cliente(cliente_id):
    """Busca o histórico completo de transações e pagamentos de um cliente."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    # União de transações e pagamentos ordenados por data
    cursor.execute('''
        SELECT 'COMPRA' as tipo, descricao, valor, data 
        FROM transacoes WHERE cliente_id = ?
        UNION ALL
        SELECT 'PAGAMENTO' as tipo, observacao as descricao, valor, data 
        FROM pagamentos WHERE cliente_id = ?
        ORDER BY data DESC
    ''', (cliente_id, cliente_id))
    
    historico = cursor.fetchall()
    conn.close()
    
    return historico

def obter_estatisticas():
    """Retorna estatísticas gerais do sistema."""
    conn = get_conexao()
    cursor = conn.cursor()
    
    # Total de clientes ativos
    cursor.execute('SELECT COUNT(*) as total FROM clientes WHERE ativo = 1')
    total_clientes = cursor.fetchone()['total']
    
    # Total em aberto (todas as dívidas)
    cursor.execute('''
        SELECT COALESCE(SUM(t.valor), 0) - COALESCE(
            (SELECT SUM(p.valor) FROM pagamentos p), 0
        ) as total_aberto
        FROM transacoes t WHERE t.pago = 0
    ''')
    
    # Recalcula corretamente
    cursor.execute('SELECT COALESCE(SUM(valor), 0) as total FROM transacoes WHERE pago = 0')
    total_dividas = cursor.fetchone()['total']
    
    cursor.execute('SELECT COALESCE(SUM(valor), 0) as total FROM pagamentos')
    total_pagamentos = cursor.fetchone()['total']
    
    total_aberto = max(0, total_dividas - total_pagamentos)
    
    # Clientes com dívida
    cursor.execute('''
        SELECT COUNT(DISTINCT c.id) as total
        FROM clientes c
        WHERE c.ativo = 1 AND (
            SELECT COALESCE(SUM(t.valor), 0) - COALESCE(SUM(p.valor), 0)
            FROM transacoes t
            LEFT JOIN pagamentos p ON p.cliente_id = c.id
            WHERE t.cliente_id = c.id AND t.pago = 0
        ) > 0
    ''')
    
    conn.close()
    
    return {
        'total_clientes': total_clientes,
        'total_aberto': total_aberto,
        'total_dividas': total_dividas,
        'total_pagamentos': total_pagamentos
    }

def obter_clientes_com_divida():
    """Retorna lista de clientes que possuem dívidas em aberto."""
    clientes = buscar_clientes()
    clientes_com_divida = []
    
    for cliente in clientes:
        saldo = calcular_saldo_cliente(cliente['id'])
        if saldo > 0:
            clientes_com_divida.append({
                'id': cliente['id'],
                'nome': cliente['nome'],
                'telefone': cliente['telefone'],
                'saldo': saldo
            })
    
    return clientes_com_divida

# ==================== BACKUP ====================

def fazer_backup():
    """Realiza backup do banco de dados."""
    config = carregar_config()
    backup_dir = config.get('backup_dir', 'backups')
    
    # Cria o diretório de backup se não existir
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Nome do arquivo de backup com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'fiado_facil_backup_{timestamp}.db')
    
    # Copia o arquivo do banco de dados
    if os.path.exists(ARQUIVO_DB):
        shutil.copy2(ARQUIVO_DB, backup_file)
        print(f"Backup realizado: {backup_file}")
        return backup_file
    
    return None

# ==================== EXPORTAÇÃO CSV ====================

def exportar_relatorio_csv(caminho_arquivo):
    """Exporta um relatório completo para CSV."""
    import csv
    
    clientes = buscar_clientes()
    
    with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Cabeçalho - Resumo de Clientes
        writer.writerow(['=== RELATÓRIO FIADOFÁCIL ==='])
        writer.writerow(['Data de Geração:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
        writer.writerow([])
        writer.writerow(['=== RESUMO DE CLIENTES ==='])
        writer.writerow(['Nome', 'Telefone', 'Limite', 'Saldo Devedor'])
        
        for cliente in clientes:
            saldo = calcular_saldo_cliente(cliente['id'])
            writer.writerow([
                cliente['nome'],
                cliente['telefone'] or '',
                f"R$ {cliente['limite_fiado']:.2f}",
                f"R$ {saldo:.2f}"
            ])
        
        writer.writerow([])
        writer.writerow(['=== HISTÓRICO DE TRANSAÇÕES ==='])
        writer.writerow(['Cliente', 'Tipo', 'Descrição', 'Valor', 'Data'])
        
        for cliente in clientes:
            historico = buscar_historico_cliente(cliente['id'])
            for item in historico:
                writer.writerow([
                    cliente['nome'],
                    item['tipo'],
                    item['descricao'] or '',
                    f"R$ {item['valor']:.2f}",
                    item['data']
                ])
    
    return caminho_arquivo


