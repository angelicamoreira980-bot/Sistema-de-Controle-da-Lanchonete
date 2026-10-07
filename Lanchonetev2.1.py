import customtkinter as ctk
import sqlite3
import os
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def conectar():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_banco = os.path.join(diretorio_atual, "sistema.db")
    
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            nome TEXT,
            preco REAL,
            quantidade INTEGER
        )
    """)
    conexao.commit()
    return conexao, cursor

def consultar_produtos():
    conexao, cursor = conectar()
    cursor.execute("SELECT * FROM produtos")
    itens = cursor.fetchall()
    conexao.close()
    
    caixa_resultados.configure(state="normal")
    caixa_resultados.delete("1.0", "end")
    
    for linha in itens:
        texto = f"Produto: {linha[0]} | Preço: R${linha[1]:.2f} | Estoque: {linha[2]}\n"
        caixa_resultados.insert("end", texto)
        
    caixa_resultados.configure(state="disabled")

def cadastrar_produto():
    nome = entry_nome.get().strip()
    preco_str = entry_preco.get().strip()
    quantidade_str = entry_quantidade.get().strip()
    
    if not nome:
        messagebox.showwarning("Aviso", "O nome do produto não pode ficar vazio!")
        return

    try:
        preco = float(preco_str)
        quantidade = int(quantidade_str)
        
        # 1. Barreira Matemática: Bloqueia a execução se os valores forem menores que zero
        if preco < 0 or quantidade < 0:
            messagebox.showwarning("Aviso", "Valores não podem ser negativos!")
            return # 'return' expulsa o usuário da função antes de salvar
        
        conexao, cursor = conectar()
        
        # 2. Checagem de Duplicidade: Procura no banco se o nome já existe
        cursor.execute("SELECT * FROM produtos WHERE nome = ?", (nome,))

        # Se o fetchone() encontrar algo, significa que já tem cadastro
        if cursor.fetchone():
            messagebox.showwarning("Aviso", "Este produto já está cadastrado!")
            entry_nome.delete(0, 'end') # Limpa o campo para a nova tentativa
            conexao.close()
            return

        cursor.execute("INSERT INTO produtos VALUES (?, ?, ?)", (nome, preco, quantidade))
        conexao.commit()
        conexao.close()
        
        messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
        
    except ValueError:
        messagebox.showerror("Erro", "Digite valores numéricos válidos!")

def atualizar_produto():
    nome = entry_nome.get().strip()
    preco_str = entry_preco.get().strip()
    quantidade_str = entry_quantidade.get().strip()

    if not nome:
        messagebox.showwarning("Aviso", "O nome do produto não pode ficar vazio!")
        return

    try:
        novo_preco = float(preco_str)
        nova_qtd = int(quantidade_str)

        if novo_preco < 0 or nova_qtd < 0:
            messagebox.showwarning("Aviso", "Valores não podem ser negativos!")
            return

        conexao, cursor = conectar()
        
        # O comando SQL que altera dados sem precisar recadastrar
        # SET = O que vai mudar / WHERE = Quem vai sofrer a mudança
        cursor.execute("""
            UPDATE produtos
            SET preco = ?, quantidade = ?
            WHERE nome = ?
        """, (novo_preco, nova_qtd, nome))

        # Grava as alterações no arquivo
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")

    except ValueError:
        messagebox.showerror("Erro", "Digite valores numéricos válidos!")

def deletar_produto():
    nome_produto = entry_nome.get().strip()

    if not nome_produto:
        messagebox.showwarning("Aviso", "Digite o nome do produto que deseja remover!")
        return

    conexao, cursor = conectar()

    # O comando SQL que apaga um registro específico
    # A interrogação (?) é substituída com segurança pela variável 'nome_produto'
    cursor.execute("DELETE FROM produtos WHERE nome = ?", (nome_produto,))

    # Confirma e grava a exclusão no arquivo sistema.db
    conexao.commit()
    conexao.close()

    messagebox.showinfo("Sucesso", "Produto removido com sucesso!")

def encerrar_sistema():
    messagebox.showinfo("Encerrando", "O sistema será encerrado.")
    janela.destroy()

janela = ctk.CTk()
janela.title("Lanchonete Ennius Muniz")
janela.geometry("500x750")

titulo = ctk.CTkLabel(janela, text="Cadastro de Produtos", font=("Arial", 20, "bold"))
titulo.pack(pady=20)

entry_nome = ctk.CTkEntry(janela, placeholder_text="Nome do Produto", width=350)
entry_nome.pack(pady=10)

entry_preco = ctk.CTkEntry(janela, placeholder_text="Preço (Ex: 12.50)", width=350)
entry_preco.pack(pady=10)

entry_quantidade = ctk.CTkEntry(janela, placeholder_text="Quantidade em Estoque", width=350)
entry_quantidade.pack(pady=10)

btn_salvar = ctk.CTkButton(janela, text="Salvar Produto", command=cadastrar_produto, fg_color="darkblue", hover_color="navy")
btn_salvar.pack(pady=10)

btn_atualizar = ctk.CTkButton(janela, text="Atualizar Produto", command=atualizar_produto, fg_color="orange", hover_color="darkorange")
btn_atualizar.pack(pady=10)

btn_deletar = ctk.CTkButton(janela, text="Remover Produto", command=deletar_produto, fg_color="purple", hover_color="darkpurple")
btn_deletar.pack(pady=10)

btn_consultar = ctk.CTkButton(janela, text="Consultar Produtos", command=consultar_produtos, fg_color="green", hover_color="darkgreen")
btn_consultar.pack(pady=10)

btn_encerrar = ctk.CTkButton(janela, text="Encerrar Sistema", command=encerrar_sistema, fg_color="red", hover_color="darkred")
btn_encerrar.pack(pady=10)

caixa_resultados = ctk.CTkTextbox(janela, width=400, height=150)
caixa_resultados.pack(pady=20)
caixa_resultados.configure(state="disabled")

janela.mainloop()