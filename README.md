# 📋 FiadoFácil - Sistema de Gestão de Crédito Informal

Sistema desktop desenvolvido em Python para gestão de crédito informal (fiado) em pequenos comércios.

## 📦 Requisitos

- **Python 3.8** ou superior
- Bibliotecas padrão (já incluídas no Python):
  - `tkinter` - Interface gráfica
  - `sqlite3` - Banco de dados
  - `json` - Configurações
  - `csv` - Exportação de relatórios

---

## 🚀 Como Executar

### Windows

1. Certifique-se de ter o Python instalado
2. Abra o terminal (CMD ou PowerShell)
3. Navegue até a pasta do projeto
4. Execute:

```bash
python main.py
```

### Linux / macOS

```bash
python3 main.py
```

---

## 📁 Estrutura do Projeto

```
FiadoFacil/
│
├── main.py          # Arquivo principal - execute este
├── gui.py           # Interface gráfica (Tkinter)
├── database.py      # Operações com banco de dados (SQLite)
├── config.py        # Gerenciamento de configurações
├── config.json      # Arquivo de configurações
├── README.md        # Este arquivo
│
├── fiado_facil.db   # Banco de dados (criado automaticamente)
└── backups/         # Pasta de backups (criada automaticamente)
```

---

## ⚙️ Configurações

O arquivo `config.json` permite personalizar o sistema:

```json
{
    "empresa": {
        "nome": "Minha Loja de Conveniência",
        "telefone": "(00) 00000-0000"
    },
    "limite_fiado_padrao": 500.00,
    "backup_dir": "backups",
    "backup_automatico": true,
    "interface": {
        "tema": "claro",
        "font_size": 10,
        "largura_janela": 1200,
        "altura_janela": 700
    }
}
```

---

## 🎯 Funcionalidades

### 👥 Gestão de Clientes
- ✅ Cadastro de clientes (nome, telefone, limite de fiado)
- ✅ Edição de dados do cliente
- ✅ Exclusão (lógica) de clientes
- ✅ Busca rápida por nome ou telefone

### 🛒 Registro de Transações (Vendas Fiadas)
- ✅ Registrar compra fiada com descrição e valor
- ✅ Alerta quando ultrapassa o limite de fiado
- ✅ Data e hora automáticas

### 💵 Registro de Pagamentos
- ✅ Registrar pagamentos parciais ou totais
- ✅ Campo para observações
- ✅ Opção de pagar valor total com um clique

### 📊 Consultas e Relatórios
- ✅ Visualização do saldo devedor em tempo real
- ✅ Histórico completo de transações por cliente
- ✅ Estatísticas gerais (total em aberto, clientes com dívida)
- ✅ Exportação de relatório completo para CSV

### 💾 Backup e Segurança
- ✅ Backup automático ao iniciar/fechar o sistema
- ✅ Banco de dados local (SQLite)
- ✅ Dados persistentes

---

## 📸 Screenshots

### Tela Principal
- Lista de clientes à esquerda
- Detalhes do cliente selecionado à direita
- Estatísticas no cabeçalho

### Funcionalidades
- Botão "Nova Compra Fiada" (laranja)
- Botão "Registrar Pagamento" (verde)
- Histórico de transações com cores diferenciadas

---

## 🔧 Banco de Dados

O sistema utiliza **SQLite** com as seguintes tabelas:

### Tabela `clientes`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | Chave primária |
| nome | TEXT | Nome do cliente |
| telefone | TEXT | Telefone (opcional) |
| limite_fiado | REAL | Limite de crédito |
| data_cadastro | TEXT | Data de cadastro |
| ativo | INTEGER | Status (1=ativo, 0=excluído) |

### Tabela `transacoes`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | Chave primária |
| cliente_id | INTEGER | FK para clientes |
| descricao | TEXT | Descrição da compra |
| valor | REAL | Valor da compra |
| data | TEXT | Data/hora da transação |
| pago | INTEGER | Status (0=aberto, 1=pago) |

### Tabela `pagamentos`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | Chave primária |
| cliente_id | INTEGER | FK para clientes |
| valor | REAL | Valor do pagamento |
| observacao | TEXT | Observação (opcional) |
| data | TEXT | Data/hora do pagamento |

---

## 📝 Licença

Este projeto foi desenvolvido como Trabalho de Conclusão de Curso (TCC) para fins educacionais.

---

## 🆘 Suporte

Em caso de dúvidas ou problemas, verifique:

1. Se o Python está instalado corretamente (`python --version`)
2. Se você está na pasta correta do projeto
3. Se todos os arquivos estão presentes


