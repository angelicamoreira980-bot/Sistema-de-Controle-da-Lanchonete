import customtkinter as ctk
import sqlite3
import os
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ---Conexão com o banco de dados---
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

# ---Sistema Principal---
def abrir_sistema_principal():
    global caixa_resultados, entry_nome, entry_preco, entry_quantidade, entry_baixa, janela

    # Destrói a janela de login antes de abrir a principal
    janela_login.destroy()

    janela = ctk.CTk()
    janela.title("Lanchonete Ennius Muniz")
    janela.geometry("500x750")

    titulo = ctk.CTkLabel(janela, text="Cadastro de Produtos", font=("Arial", 20, "bold"))
    titulo.pack(pady=15)

    entry_nome = ctk.CTkEntry(janela, placeholder_text="Nome do Produto", width=350)
    entry_nome.pack(pady=8)

    entry_preco = ctk.CTkEntry(janela, placeholder_text="Preço (Ex: 12.50)", width=350) 
    entry_preco.pack(pady=8)

    entry_quantidade = ctk.CTkEntry(janela, placeholder_text="Quantidade em Estoque", width=350)
    entry_quantidade.pack(pady=8)

    btn_salvar = ctk.CTkButton(janela, text="Salvar Produto", command=cadastrar_produto, fg_color="darkblue", hover_color="navy")
    btn_salvar.pack(pady=10)

    btn_consultar = ctk.CTkButton(janela, text="Consultar Produtos", command=consultar_produtos, fg_color="orange", hover_color="darkorange")
    btn_consultar.pack(pady=8)

    # ---Campo e Botão para Dar Baixa no Estoque---
    entry_baixa = ctk.CTkEntry(janela, placeholder_text="Nome do Produto para Venda/Baixa", width=350)
    entry_baixa.pack(pady=8)

    btn_baixa = ctk.CTkButton(janela, text="Vender", command=dar_baixa_estoque, fg_color="green", hover_color="darkgreen")
    btn_baixa.pack(pady=8)
   
    # Criamos a caixa de resultados com texto branco por padrão
    caixa_resultados = ctk.CTkTextbox(janela, width=400, height=150, text_color="white")
    caixa_resultados.pack(pady=15)
    
    # Configura uma "tag" (etiqueta) chamada "perigo" com a cor vermelha
    caixa_resultados.tag_config("perigo", foreground="red")
    caixa_resultados.configure(state="disabled")

    btn_encerrar = ctk.CTkButton(janela, text="Encerrar Sistema", command=encerrar_sistema, fg_color="red", hover_color="darkred")
    btn_encerrar.pack(pady=10)
    
    janela.mainloop()

# ---Funções de Lógica do Sistema---
def consultar_produtos():
    conexao, cursor = conectar()
    cursor.execute("SELECT * FROM produtos")
    itens = cursor.fetchall()
    conexao.close()
    
    caixa_resultados.configure(state="normal")
    caixa_resultados.delete("1.0", "end")
    
    for linha in itens:
        nome_prod, preco_prod, qtd_prod = linha[0], linha[1], linha[2]
        texto = f"Produto: {nome_prod} | Preço: R${preco_prod:.2f} | Estoque: {qtd_prod}\n"
        
        # Se a quantidade for menor que 5, insere aplicando a tag vermelha "perigo"
        if qtd_prod <= 5:
            caixa_resultados.insert("end", texto, "perigo")
        else:
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

        if preco < 0 or quantidade < 0:
            messagebox.showwarning("Aviso", "Os valores não podem ser negativos!")
            return

        conexao, cursor = conectar()

        cursor.execute("SELECT * FROM produtos WHERE nome = ?", (nome,))
        if cursor.fetchone():
            messagebox.showwarning("Aviso", "Este produto já está cadastrado!")
            entry_nome.delete(0, 'end')
            conexao.close()
            return

        cursor.execute("INSERT INTO produtos VALUES (?, ?, ?)", (nome, preco, quantidade))
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", f"Produto '{nome}' cadastrado!")

        entry_nome.delete(0, 'end')
        entry_preco.delete(0, 'end')
        entry_quantidade.delete(0, 'end')
        
    except ValueError:
        messagebox.showerror("ERRO DE DIGITAÇÃO", "Digite valores numéricos válidos!")

# --- FUNÇÃO ATUALIZADA IGUAL À IMAGEM ---
def dar_baixa_estoque():
    nome_produto = entry_baixa.get().strip()
    if not nome_produto:
        messagebox.showwarning("Aviso", "Digite o nome do produto para dar baixa!")
        return

    conexao, cursor = conectar()
    cursor.execute("SELECT quantidade FROM produtos WHERE nome = ?", (nome_produto,))
    resultado = cursor.fetchone()

    if resultado:
        qtd_atual = resultado[0]

        # Regra de Negócio: Não permite estoque negativo
        if qtd_atual > 0:
            nova_qtd = qtd_atual - 1
            cursor.execute("UPDATE produtos SET quantidade = ? WHERE nome = ?", (nova_qtd, nome_produto))
            conexao.commit()
            
            # Limpa o campo de texto da venda e atualiza a lista na tela na hora
            entry_baixa.delete(0, 'end')
            consultar_produtos()
        else:
            messagebox.showwarning("Esgotado", f"O produto '{nome_produto}' não possui saldo em estoque.")
    else:
        messagebox.showerror("Erro", "Produto não encontrado!")
         
    conexao.close()

def encerrar_sistema():
    messagebox.showinfo("Encerrando", "O sistema será encerrado.")
    janela.destroy()

# ---Autenticação e Login---
def validar_login():
    if entry_user.get() == "admin" and entry_senha.get() == "123":
        abrir_sistema_principal()
    else:
        messagebox.showerror("Erro de autenticação", "Credenciais inválidas.")

# --- Tela de login---
janela_login = ctk.CTk()
janela_login.title("Acesso")
janela_login.geometry("300x350")

label_login = ctk.CTkLabel(janela_login, text="Acesso ao Sistema", font=("Arial", 16, "bold"))
label_login.pack(pady=20)

entry_user = ctk.CTkEntry(janela_login, placeholder_text="Usuário")
entry_user.pack(pady=10)

entry_senha = ctk.CTkEntry(janela_login, placeholder_text="Senha", show="*")
entry_senha.pack(pady=10)

btn_login = ctk.CTkButton(janela_login, text="Autenticar", command=validar_login)
btn_login.pack(pady=30)

janela_login.mainloop()
