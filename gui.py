"""
GUI.PY - Interface Gráfica do FiadoFácil
=========================================

Sistema de Gestão de Crédito Informal
Desenvolvido com Tkinter e SQLite
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import database as db
from config import carregar_config, salvar_config, get_limite_padrao


class JanelaPagamento:
    """Janela para registrar pagamentos de clientes."""
    
    def __init__(self, parent, cliente_id, callback_atualizar=None):
        """
        Inicializa a janela de pagamento.
        
        Args:
            parent: Janela pai
            cliente_id: ID do cliente
            callback_atualizar: Função para atualizar a tela principal após o pagamento
        """
        self.parent = parent
        self.cliente_id = cliente_id
        self.callback_atualizar = callback_atualizar
        
        # Buscar dados do cliente
        self.cliente = db.buscar_cliente_por_id(cliente_id)
        self.saldo_atual = db.calcular_saldo_cliente(cliente_id)
        
        # Criar janela
        self.janela = tk.Toplevel(parent)
        self.janela.title("Registrar Pagamento")
        self.janela.geometry("500x400")
        self.janela.resizable(False, False)
        self.janela.grab_set()  # Tornar modal
        
        self.criar_widgets()
        self.centralizar_janela()
    
    def criar_widgets(self):
        """Cria os widgets da janela."""
        
        # Frame principal com fundo verde
        frame_principal = tk.Frame(self.janela, bg='#2ecc71', padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Título
        titulo = tk.Label(
            frame_principal,
            text=f"💵 Pagamento - {self.cliente['nome']}",
            font=('Arial', 16, 'bold'),
            bg='#2ecc71',
            fg='white'
        )
        titulo.pack(pady=(0, 20))
        
        # Frame branco com informações
        frame_info = tk.Frame(frame_principal, bg='white', padx=20, pady=15)
        frame_info.pack(fill='x', pady=(0, 20))
        
        # Saldo devedor atual
        label_saldo_titulo = tk.Label(
            frame_info,
            text="Saldo Devedor Atual",
            font=('Arial', 10),
            bg='white',
            fg='#7f8c8d'
        )
        label_saldo_titulo.pack()
        
        label_saldo_valor = tk.Label(
            frame_info,
            text=f"R$ {self.saldo_atual:.2f}",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#e74c3c'
        )
        label_saldo_valor.pack()
        
        # Frame do formulário
        frame_form = tk.Frame(frame_principal, bg='#2ecc71')
        frame_form.pack(fill='both', expand=True)
        
        # Campo: Valor do Pagamento
        label_valor = tk.Label(
            frame_form,
            text="Valor do Pagamento (R$) *",
            font=('Arial', 10),
            bg='#2ecc71',
            fg='white'
        )
        label_valor.pack(anchor='w', pady=(0, 5))
        
        self.entry_valor = tk.Entry(
            frame_form,
            font=('Arial', 12),
            bg='white'
        )
        self.entry_valor.pack(fill='x', pady=(0, 10))
        self.entry_valor.focus()
        
        # Link para preencher valor total
        link_preencher = tk.Label(
            frame_form,
            text="Preencher valor total da dívida",
            font=('Arial', 9, 'underline'),
            bg='#2ecc71',
            fg='#ecf0f1',
            cursor='hand2'
        )
        link_preencher.pack(anchor='w', pady=(0, 15))
        link_preencher.bind('<Button-1>', self.preencher_valor_total)
        
        # Campo: Observação
        label_obs = tk.Label(
            frame_form,
            text="Observação",
            font=('Arial', 10),
            bg='#2ecc71',
            fg='white'
        )
        label_obs.pack(anchor='w', pady=(0, 5))
        
        self.entry_obs = tk.Entry(
            frame_form,
            font=('Arial', 12),
            bg='white'
        )
        self.entry_obs.pack(fill='x', pady=(0, 20))
        
        # Frame dos botões
        frame_botoes = tk.Frame(frame_form, bg='#2ecc71')
        frame_botoes.pack(fill='x')
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            frame_botoes,
            text="Cancelar",
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.cancelar
        )
        btn_cancelar.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botão Registrar Pagamento
        btn_registrar = tk.Button(
            frame_botoes,
            text="Registrar Pagamento",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.registrar_pagamento
        )
        btn_registrar.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Bind Enter para registrar
        self.janela.bind('<Return>', lambda e: self.registrar_pagamento())
        self.janela.bind('<Escape>', lambda e: self.cancelar())
    
    def preencher_valor_total(self, event=None):
        """Preenche automaticamente o valor total da dívida."""
        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, f"{self.saldo_atual:.2f}")
    
    def validar_dados(self):
        """Valida os dados inseridos."""
        
        # Validar valor
        valor_str = self.entry_valor.get().strip().replace(',', '.')
        
        if not valor_str:
            messagebox.showerror(
                "Erro de Validação",
                "Por favor, informe o valor do pagamento.",
                parent=self.janela
            )
            self.entry_valor.focus()
            return None
        
        try:
            valor = float(valor_str)
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError:
            messagebox.showerror(
                "Erro de Validação",
                "Valor inválido. Digite apenas números.",
                parent=self.janela
            )
            self.entry_valor.focus()
            return None
        
        # Verificar se o valor não excede a dívida
        if valor > self.saldo_atual:
            resposta = messagebox.askyesno(
                "Atenção",
                f"O valor informado (R$ {valor:.2f}) é maior que a dívida atual (R$ {self.saldo_atual:.2f}).\n\n"
                f"Deseja continuar? O excedente ficará como crédito.",
                parent=self.janela
            )
            if not resposta:
                return None
        
        observacao = self.entry_obs.get().strip()
        
        return {
            'valor': valor,
            'observacao': observacao
        }
    
    def registrar_pagamento(self):
        """Registra o pagamento no banco de dados."""
        
        # Validar dados
        dados = self.validar_dados()
        if not dados:
            return
        
        try:
            # Registrar pagamento no banco
            pagamento_id = db.adicionar_pagamento(
                self.cliente_id,
                dados['valor'],
                dados['observacao']
            )
            
            # Calcular novo saldo
            novo_saldo = db.calcular_saldo_cliente(self.cliente_id)
            
            # Mensagem de sucesso
            if novo_saldo <= 0:
                mensagem = (
                    f"✅ Pagamento de R$ {dados['valor']:.2f} registrado com sucesso!\n\n"
                    f"🎉 A dívida foi quitada completamente!"
                )
            else:
                mensagem = (
                    f"✅ Pagamento de R$ {dados['valor']:.2f} registrado com sucesso!\n\n"
                    f"Saldo devedor restante: R$ {novo_saldo:.2f}"
                )
            
            messagebox.showinfo(
                "Sucesso",
                mensagem,
                parent=self.janela
            )
            
            # Chamar callback para atualizar tela principal
            if self.callback_atualizar:
                self.callback_atualizar()
            
            # Fechar janela
            self.janela.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao registrar pagamento:\n{str(e)}",
                parent=self.janela
            )
    
    def cancelar(self):
        """Cancela e fecha a janela."""
        self.janela.destroy()
    
    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.janela.update_idletasks()
        
        largura = self.janela.winfo_width()
        altura = self.janela.winfo_height()
        
        x = (self.janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela.winfo_screenheight() // 2) - (altura // 2)
        
        self.janela.geometry(f'{largura}x{altura}+{x}+{y}')


# JANELA DE NOVA TRANSAÇÃO (COMPRA FIADA)
class JanelaNovaTransacao:
    """Janela para registrar uma nova compra fiada."""
    
    def __init__(self, parent, cliente_id, callback_atualizar=None):
        self.parent = parent
        self.cliente_id = cliente_id
        self.callback_atualizar = callback_atualizar
        
        # Buscar dados do cliente
        self.cliente = db.buscar_cliente_por_id(cliente_id)
        
        # Criar janela
        self.janela = tk.Toplevel(parent)
        self.janela.title("Nova Compra Fiada")
        self.janela.geometry("500x350")
        self.janela.resizable(False, False)
        self.janela.grab_set()
        
        self.criar_widgets()
        self.centralizar_janela()
    
    def criar_widgets(self):
        """Cria os widgets da janela."""
        
        # Frame principal com fundo laranja
        frame_principal = tk.Frame(self.janela, bg='#e67e22', padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Título
        titulo = tk.Label(
            frame_principal,
            text=f"🛒 Nova Compra - {self.cliente['nome']}",
            font=('Arial', 16, 'bold'),
            bg='#e67e22',
            fg='white'
        )
        titulo.pack(pady=(0, 20))
        
        # Frame do formulário
        frame_form = tk.Frame(frame_principal, bg='#e67e22')
        frame_form.pack(fill='both', expand=True)
        
        # Campo: Descrição do Item
        label_desc = tk.Label(
            frame_form,
            text="Descrição do Item *",
            font=('Arial', 10),
            bg='#e67e22',
            fg='white'
        )
        label_desc.pack(anchor='w', pady=(0, 5))
        
        self.entry_descricao = tk.Entry(
            frame_form,
            font=('Arial', 12),
            bg='white'
        )
        self.entry_descricao.pack(fill='x', pady=(0, 15))
        self.entry_descricao.focus()
        
        # Campo: Valor
        label_valor = tk.Label(
            frame_form,
            text="Valor (R$) *",
            font=('Arial', 10),
            bg='#e67e22',
            fg='white'
        )
        label_valor.pack(anchor='w', pady=(0, 5))
        
        self.entry_valor = tk.Entry(
            frame_form,
            font=('Arial', 12),
            bg='white'
        )
        self.entry_valor.pack(fill='x', pady=(0, 20))
        
        # Frame dos botões
        frame_botoes = tk.Frame(frame_form, bg='#e67e22')
        frame_botoes.pack(fill='x')
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            frame_botoes,
            text="Cancelar",
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.cancelar
        )
        btn_cancelar.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botão Registrar Compra
        btn_registrar = tk.Button(
            frame_botoes,
            text="Registrar Compra",
            font=('Arial', 11, 'bold'),
            bg='#d35400',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.registrar_compra
        )
        btn_registrar.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Bind Enter
        self.janela.bind('<Return>', lambda e: self.registrar_compra())
        self.janela.bind('<Escape>', lambda e: self.cancelar())
    
    def validar_dados(self):
        """Valida os dados inseridos."""
        
        descricao = self.entry_descricao.get().strip()
        if not descricao:
            messagebox.showerror(
                "Erro de Validação",
                "Por favor, informe a descrição do item.",
                parent=self.janela
            )
            self.entry_descricao.focus()
            return None
        
        valor_str = self.entry_valor.get().strip().replace(',', '.')
        if not valor_str:
            messagebox.showerror(
                "Erro de Validação",
                "Por favor, informe o valor.",
                parent=self.janela
            )
            self.entry_valor.focus()
            return None
        
        try:
            valor = float(valor_str)
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError:
            messagebox.showerror(
                "Erro de Validação",
                "Valor inválido. Digite apenas números.",
                parent=self.janela
            )
            self.entry_valor.focus()
            return None
        
        return {
            'descricao': descricao,
            'valor': valor
        }
    
    def registrar_compra(self):
        """Registra a compra no banco de dados."""
        
        dados = self.validar_dados()
        if not dados:
            return
        
        try:
            # Registrar transação
            db.adicionar_transacao(
                self.cliente_id,
                dados['descricao'],
                dados['valor']
            )
            
            messagebox.showinfo(
                "Sucesso",
                f"✅ Compra de R$ {dados['valor']:.2f} registrada com sucesso!",
                parent=self.janela
            )
            
            # Atualizar tela principal
            if self.callback_atualizar:
                self.callback_atualizar()
            
            # Fechar janela
            self.janela.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao registrar compra:\n{str(e)}",
                parent=self.janela
            )
    
    def cancelar(self):
        """Cancela e fecha a janela."""
        self.janela.destroy()
    
    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.janela.update_idletasks()
        largura = self.janela.winfo_width()
        altura = self.janela.winfo_height()
        x = (self.janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela.winfo_screenheight() // 2) - (altura // 2)
        self.janela.geometry(f'{largura}x{altura}+{x}+{y}')


# JANELA DE CLIENTE (ADICIONAR/EDITAR)
class JanelaCliente:
    """Janela para adicionar ou editar cliente."""
    
    def __init__(self, parent, cliente_id=None, callback_atualizar=None):
        self.parent = parent
        self.cliente_id = cliente_id
        self.callback_atualizar = callback_atualizar
        
        # Modo edição ou novo
        self.modo_edicao = cliente_id is not None
        
        # Criar janela
        self.janela = tk.Toplevel(parent)
        self.janela.title("Editar Cliente" if self.modo_edicao else "Novo Cliente")
        self.janela.geometry("450x400")
        self.janela.resizable(False, False)
        self.janela.grab_set()
        
        self.criar_widgets()
        
        if self.modo_edicao:
            self.carregar_dados()
        
        self.centralizar_janela()
    
    def criar_widgets(self):
        """Cria os widgets da janela."""
        
        # Frame principal
        frame_principal = tk.Frame(self.janela, bg='#3498db', padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Título
        titulo_texto = "✏️ Editar Cliente" if self.modo_edicao else "➕ Novo Cliente"
        titulo = tk.Label(
            frame_principal,
            text=titulo_texto,
            font=('Arial', 16, 'bold'),
            bg='#3498db',
            fg='white'
        )
        titulo.pack(pady=(0, 20))
        
        # Frame formulário
        frame_form = tk.Frame(frame_principal, bg='#3498db')
        frame_form.pack(fill='both', expand=True)
        
        # Nome
        tk.Label(
            frame_form,
            text="Nome *",
            font=('Arial', 10),
            bg='#3498db',
            fg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        self.entry_nome = tk.Entry(frame_form, font=('Arial', 12))
        self.entry_nome.pack(fill='x', pady=(0, 15))
        self.entry_nome.focus()
        
        # Telefone
        tk.Label(
            frame_form,
            text="Telefone",
            font=('Arial', 10),
            bg='#3498db',
            fg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        self.entry_telefone = tk.Entry(frame_form, font=('Arial', 12))
        self.entry_telefone.pack(fill='x', pady=(0, 15))
        
        # Limite de Fiado
        tk.Label(
            frame_form,
            text="Limite de Fiado (R$)",
            font=('Arial', 10),
            bg='#3498db',
            fg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        self.entry_limite = tk.Entry(frame_form, font=('Arial', 12))
        self.entry_limite.pack(fill='x', pady=(0, 20))
        self.entry_limite.insert(0, f"{get_limite_padrao():.2f}")
        
        # Frame botões
        frame_botoes = tk.Frame(frame_form, bg='#3498db')
        frame_botoes.pack(fill='x')
        
        # Botão Cancelar
        tk.Button(
            frame_botoes,
            text="Cancelar",
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.cancelar
        ).pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botão Salvar
        texto_botao = "Salvar Alterações" if self.modo_edicao else "Adicionar Cliente"
        tk.Button(
            frame_botoes,
            text=texto_botao,
            font=('Arial', 11, 'bold'),
            bg='#2980b9',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.salvar
        ).pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        self.janela.bind('<Return>', lambda e: self.salvar())
        self.janela.bind('<Escape>', lambda e: self.cancelar())
    
    def carregar_dados(self):
        """Carrega dados do cliente para edição."""
        cliente = db.buscar_cliente_por_id(self.cliente_id)
        if cliente:
            self.entry_nome.insert(0, cliente['nome'])
            self.entry_telefone.insert(0, cliente['telefone'] or '')
            self.entry_limite.delete(0, tk.END)
            self.entry_limite.insert(0, f"{cliente['limite_fiado']:.2f}")
    
    def validar_dados(self):
        """Valida os dados inseridos."""
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório!", parent=self.janela)
            return None
        
        telefone = self.entry_telefone.get().strip()
        
        limite_str = self.entry_limite.get().strip().replace(',', '.')
        try:
            limite = float(limite_str)
            if limite < 0:
                raise ValueError()
        except:
            messagebox.showerror("Erro", "Limite inválido!", parent=self.janela)
            return None
        
        return {'nome': nome, 'telefone': telefone, 'limite': limite}
    
    def salvar(self):
        """Salva o cliente."""
        dados = self.validar_dados()
        if not dados:
            return
        
        try:
            if self.modo_edicao:
                db.atualizar_cliente(
                    self.cliente_id,
                    dados['nome'],
                    dados['telefone'],
                    dados['limite']
                )
                messagebox.showinfo("Sucesso", "Cliente atualizado!", parent=self.janela)
            else:
                db.adicionar_cliente(
                    dados['nome'],
                    dados['telefone'],
                    dados['limite']
                )
                messagebox.showinfo("Sucesso", "Cliente adicionado!", parent=self.janela)
            
            if self.callback_atualizar:
                self.callback_atualizar()
            
            self.janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self.janela)
    
    def cancelar(self):
        self.janela.destroy()
    
    def centralizar_janela(self):
        self.janela.update_idletasks()
        largura = self.janela.winfo_width()
        altura = self.janela.winfo_height()
        x = (self.janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela.winfo_screenheight() // 2) - (altura // 2)
        self.janela.geometry(f'{largura}x{altura}+{x}+{y}')



# APLICAÇÃO PRINCIPAL

class FiadoFacilApp:
    """Classe principal da aplicação."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FiadoFácil - Sistema de Gestão de Crédito")
        self.root.geometry("1200x700")
        
        # Cliente selecionado
        self.cliente_selecionado = None
        
        # Criar interface
        self.criar_widgets()
        self.atualizar_lista_clientes()
        
    def criar_widgets(self):
        """Cria a interface principal."""
        
        # Barra superior
        frame_topo = tk.Frame(self.root, bg='#2c3e50', height=60)
        frame_topo.pack(fill='x')
        frame_topo.pack_propagate(False)
        
        tk.Label(
            frame_topo,
            text="💰 FiadoFácil",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(side='left', padx=20, pady=10)
        
        # Frame principal dividido
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(fill='both', expand=True)
        
        # ====== PAINEL ESQUERDO (Lista de Clientes) ======
        frame_esquerdo = tk.Frame(frame_principal, bg='#ecf0f1', width=350)
        frame_esquerdo.pack(side='left', fill='both')
        frame_esquerdo.pack_propagate(False)
        
        # Título
        tk.Label(
            frame_esquerdo,
            text="Clientes",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=(10, 5))
        
        # Busca
        frame_busca = tk.Frame(frame_esquerdo, bg='#ecf0f1')
        frame_busca.pack(fill='x', padx=10, pady=(0, 10))
        
        self.entry_busca = tk.Entry(
            frame_busca,
            font=('Arial', 11),
            bg='white'
        )
        self.entry_busca.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entry_busca.insert(0, "Buscar cliente...")
        self.entry_busca.bind('<FocusIn>', lambda e: self.limpar_placeholder())
        self.entry_busca.bind('<FocusOut>', lambda e: self.restaurar_placeholder())
        self.entry_busca.bind('<KeyRelease>', lambda e: self.atualizar_lista_clientes())
        
        tk.Button(
            frame_busca,
            text="+ Novo",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.abrir_janela_novo_cliente
        ).pack(side='right')
        
        # Lista de clientes
        frame_lista = tk.Frame(frame_esquerdo, bg='white')
        frame_lista.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Treeview
        colunas = ('Nome', 'Saldo')
        self.tree_clientes = ttk.Treeview(
            frame_lista,
            columns=colunas,
            show='headings',
            selectmode='browse'
        )
        
        self.tree_clientes.heading('Nome', text='Nome')
        self.tree_clientes.heading('Saldo', text='Saldo')
        
        self.tree_clientes.column('Nome', width=200)
        self.tree_clientes.column('Saldo', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            frame_lista,
            orient='vertical',
            command=self.tree_clientes.yview
        )
        self.tree_clientes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_clientes.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Evento de seleção
        self.tree_clientes.bind('<<TreeviewSelect>>', self.ao_selecionar_cliente)
        
        # ====== PAINEL DIREITO (Detalhes do Cliente) ======
        self.frame_direito = tk.Frame(frame_principal, bg='white')
        self.frame_direito.pack(side='right', fill='both', expand=True)
        
        # Mensagem inicial
        self.label_sem_selecao = tk.Label(
            self.frame_direito,
            text="📋 Selecione um cliente para ver os detalhes",
            font=('Arial', 14),
            bg='white',
            fg='#7f8c8d'
        )
        self.label_sem_selecao.pack(expand=True)
        
    def limpar_placeholder(self):
        """Remove o placeholder do campo de busca."""
        if self.entry_busca.get() == "Buscar cliente...":
            self.entry_busca.delete(0, tk.END)
    
    def restaurar_placeholder(self):
        """Restaura o placeholder se estiver vazio."""
        if not self.entry_busca.get():
            self.entry_busca.insert(0, "Buscar cliente...")
    
    def atualizar_lista_clientes(self):
        """Atualiza a lista de clientes."""
        # Limpar lista
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        # Buscar termo
        termo = self.entry_busca.get()
        if termo == "Buscar cliente...":
            termo = ""
        
        # Buscar clientes
        clientes = db.buscar_clientes(termo)
        
        for cliente in clientes:
            saldo = db.calcular_saldo_cliente(cliente['id'])
            self.tree_clientes.insert(
                '',
                'end',
                values=(cliente['nome'], f"R$ {saldo:.2f}"),
                tags=(cliente['id'],)
            )
    
    def ao_selecionar_cliente(self, event):
        """Evento ao selecionar um cliente na lista."""
        selecao = self.tree_clientes.selection()
        if not selecao:
            return
        
        # Obter ID do cliente
        item = self.tree_clientes.item(selecao[0])
        cliente_id = item['tags'][0]
        
        # Buscar dados completos
        self.cliente_selecionado = db.buscar_cliente_por_id(cliente_id)
        
        # Atualizar painel direito
        self.mostrar_detalhes_cliente()
    
    def mostrar_detalhes_cliente(self):
        """Mostra os detalhes do cliente selecionado."""
        if not self.cliente_selecionado:
            return
        
        # Limpar frame direito
        for widget in self.frame_direito.winfo_children():
            widget.destroy()
        
        cliente = self.cliente_selecionado
        saldo = db.calcular_saldo_cliente(cliente['id'])
        
        # Header com nome e saldo
        frame_header = tk.Frame(self.frame_direito, bg='#ecf0f1', height=120)
        frame_header.pack(fill='x')
        frame_header.pack_propagate(False)
        
        # Nome
        tk.Label(
            frame_header,
            text=cliente['nome'],
            font=('Arial', 20, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=(15, 5))
        
        # Telefone
        if cliente['telefone']:
            tk.Label(
                frame_header,
                text=f"📞 {cliente['telefone']}",
                font=('Arial', 11),
                bg='#ecf0f1',
                fg='#7f8c8d'
            ).pack()
        
        # Limite
        tk.Label(
            frame_header,
            text=f"Limite: R$ {cliente['limite_fiado']:.2f}",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(5, 0))
        
        # Saldo
        frame_saldo = tk.Frame(self.frame_direito, bg='white', height=100)
        frame_saldo.pack(fill='x')
        frame_saldo.pack_propagate(False)
        
        tk.Label(
            frame_saldo,
            text="Saldo",
            font=('Arial', 12),
            bg='white',
            fg='#7f8c8d'
        ).pack(pady=(20, 0))
        
        cor_saldo = '#e74c3c' if saldo > 0 else '#27ae60'
        tk.Label(
            frame_saldo,
            text=f"R$ {saldo:.2f}",
            font=('Arial', 28, 'bold'),
            bg='white',
            fg=cor_saldo
        ).pack()
        
        # Botões de ação
        frame_acoes = tk.Frame(self.frame_direito, bg='white')
        frame_acoes.pack(fill='x', padx=20, pady=10)
        
        tk.Button(
            frame_acoes,
            text="🛒 Nova Compra Fiada",
            font=('Arial', 11, 'bold'),
            bg='#e67e22',
            fg='white',
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.abrir_janela_nova_compra
        ).pack(fill='x', pady=(0, 10))
        
        tk.Button(
            frame_acoes,
            text="💵 Registrar Pagamento",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.abrir_janela_pagamento
        ).pack(fill='x', pady=(0, 10))
        
        tk.Button(
            frame_acoes,
            text="✏️ Editar",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.editar_cliente
        ).pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        tk.Button(
            frame_acoes,
            text="🗑️ Excluir",
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.excluir_cliente
        ).pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Histórico
        tk.Label(
            self.frame_direito,
            text="📜 Histórico de Transações",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=(20, 10))
        
        frame_historico = tk.Frame(self.frame_direito, bg='white')
        frame_historico.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Treeview histórico
        colunas_hist = ('Tipo', 'Descrição', 'Valor', 'Data')
        self.tree_historico = ttk.Treeview(
            frame_historico,
            columns=colunas_hist,
            show='headings',
            height=10
        )
        
        self.tree_historico.heading('Tipo', text='Tipo')
        self.tree_historico.heading('Descrição', text='Descrição')
        self.tree_historico.heading('Valor', text='Valor')
        self.tree_historico.heading('Data', text='Data')
        
        self.tree_historico.column('Tipo', width=80)
        self.tree_historico.column('Descrição', width=200)
        self.tree_historico.column('Valor', width=100)
        self.tree_historico.column('Data', width=150)
        
        scrollbar_hist = ttk.Scrollbar(
            frame_historico,
            orient='vertical',
            command=self.tree_historico.yview
        )
        self.tree_historico.configure(yscrollcommand=scrollbar_hist.set)
        
        self.tree_historico.pack(side='left', fill='both', expand=True)
        scrollbar_hist.pack(side='right', fill='y')
        
        # Carregar histórico
        self.atualizar_historico()
    
    def atualizar_historico(self):
        """Atualiza o histórico de transações do cliente."""
        if not self.cliente_selecionado:
            return
        
        # Limpar
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        # Buscar histórico
        historico = db.buscar_historico_cliente(self.cliente_selecionado['id'])
        
        for item in historico:
            tipo = item['tipo']
            descricao = item['descricao'] or '-'
            valor = item['valor']
            data = item['data']
            
            # Formatar
            sinal = '+' if tipo == 'COMPRA' else '-'
            cor = 'red' if tipo == 'COMPRA' else 'green'
            
            self.tree_historico.insert(
                '',
                'end',
                values=(tipo, descricao, f"{sinal}R$ {valor:.2f}", data),
                tags=(cor,)
            )
        
        # Configurar cores
        self.tree_historico.tag_configure('red', foreground='#e74c3c')
        self.tree_historico.tag_configure('green', foreground='#27ae60')
    
    def abrir_janela_novo_cliente(self):
        """Abre janela para adicionar novo cliente."""
        JanelaCliente(self.root, callback_atualizar=self.atualizar_lista_clientes)
    
    def editar_cliente(self):
        """Abre janela para editar cliente."""
        if not self.cliente_selecionado:
            return
        
        JanelaCliente(
            self.root,
            cliente_id=self.cliente_selecionado['id'],
            callback_atualizar=self.atualizar_apos_edicao
        )
    
    def excluir_cliente(self):
        """Exclui o cliente selecionado."""
        if not self.cliente_selecionado:
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir {self.cliente_selecionado['nome']}?\n\n"
            "Esta ação não pode ser desfeita!"
        )
        
        if resposta:
            db.excluir_cliente(self.cliente_selecionado['id'])
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
            self.cliente_selecionado = None
            self.atualizar_lista_clientes()
            
            # Limpar painel direito
            for widget in self.frame_direito.winfo_children():
                widget.destroy()
            
            self.label_sem_selecao = tk.Label(
                self.frame_direito,
                text="📋 Selecione um cliente para ver os detalhes",
                font=('Arial', 14),
                bg='white',
                fg='#7f8c8d'
            )
            self.label_sem_selecao.pack(expand=True)
    
    def abrir_janela_nova_compra(self):
        """Abre janela para registrar nova compra."""
        if not self.cliente_selecionado:
            messagebox.showwarning("Atenção", "Selecione um cliente primeiro.")
            return
        
        JanelaNovaTransacao(
            self.root,
            self.cliente_selecionado['id'],
            callback_atualizar=self.atualizar_detalhes_cliente
        )
    
    def abrir_janela_pagamento(self):
        """Abre janela para registrar pagamento."""
        if not self.cliente_selecionado:
            messagebox.showwarning("Atenção", "Selecione um cliente primeiro.")
            return
        
        # Verificar se tem dívida
        saldo = db.calcular_saldo_cliente(self.cliente_selecionado['id'])
        if saldo <= 0:
            messagebox.showinfo(
                "Informação",
                f"{self.cliente_selecionado['nome']} não possui dívidas em aberto."
            )
            return
        
        JanelaPagamento(
            self.root,
            self.cliente_selecionado['id'],
            callback_atualizar=self.atualizar_detalhes_cliente
        )
    
    def atualizar_detalhes_cliente(self):
        """Atualiza os detalhes do cliente após uma ação."""
        if self.cliente_selecionado:
            # Recarregar dados do cliente
            self.cliente_selecionado = db.buscar_cliente_por_id(
                self.cliente_selecionado['id']
            )
            self.mostrar_detalhes_cliente()
        
        # Atualizar lista também
        self.atualizar_lista_clientes()
    
    def atualizar_apos_edicao(self):
        """Atualiza tudo após editar cliente."""
        self.atualizar_lista_clientes()
        if self.cliente_selecionado:
            self.cliente_selecionado = db.buscar_cliente_por_id(
                self.cliente_selecionado['id']
            )
            self.mostrar_detalhes_cliente()
