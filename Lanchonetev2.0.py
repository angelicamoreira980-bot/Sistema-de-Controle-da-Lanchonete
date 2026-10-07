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
        
        conexao, cursor = conectar()
        cursor.execute("INSERT INTO produtos VALUES (?, ?, ?)", (nome, preco, quantidade))
        conexao.commit()
        conexao.close()
        
        messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
        
    except ValueError:
        messagebox.showerror("Erro", "Digite valores numéricos válidos!")

def encerrar_sistema():
    messagebox.showinfo("Encerrando", "O sistema será encerrado.")
    janela.destroy()

janela = ctk.CTk()
janela.title("Lanchonete Ennius Muniz")
janela.geometry("500x650")

titulo = ctk.CTkLabel(janela, text="Cadastro de Produtos", font=("Arial", 20, "bold"))
titulo.pack(pady=20)

entry_nome = ctk.CTkEntry(janela, placeholder_text="Nome do Produto", width=350)
entry_nome.pack(pady=10)

entry_preco = ctk.CTkEntry(janela, placeholder_text="Preço (Ex: 12.50)", width=350)
entry_preco.pack(pady=10)

entry_quantidade = ctk.CTkEntry(janela, placeholder_text="Quantidade em Estoque", width=350)
entry_quantidade.pack(pady=10)

btn_salvar = ctk.CTkButton(janela, text="Salvar Produto", command=cadastrar_produto, fg_color="darkblue", hover_color="darkblue")
btn_salvar.pack(pady=15)

btn_consultar = ctk.CTkButton(janela, text="Consultar Produtos", command=consultar_produtos, fg_color="green", hover_color="darkgreen")
btn_consultar.pack(pady=10)

btn_encerrar = ctk.CTkButton(janela, text="Encerrar Sistema", command=encerrar_sistema, fg_color="red", hover_color="darkred")
btn_encerrar.pack(pady=10)

caixa_resultados = ctk.CTkTextbox(janela, width=400, height=150)
caixa_resultados.pack(pady=20)
caixa_resultados.configure(state="disabled")

janela.mainloop()