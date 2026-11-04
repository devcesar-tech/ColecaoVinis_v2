import tkinter as tk
from tkinter import messagebox
import funcoes_banco as fb

def abrir(raiz, tree, callback_atualizar):
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um vinil para editar.")
        return
    
    valores = tree.item(selecionado)['values']
    
    # 🎯 CORREÇÃO 1: Garante que o ID do registro seja tratado como número inteiro
    id_registro = int(valores[0])

    janela = tk.Toplevel(raiz)
    janela.title("Editar Registro")
    janela.geometry("300x380")
    
    campos = ["Música", "Artista", "Versão", "Vinil", "BPM", "Caixa", "Posição"]
    entradas = {}
    
    for i, col in enumerate(campos):
        tk.Label(janela, text=col).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(janela)
        valor_atual = valores[i+1] if valores[i+1] is not None else ""
        entry.insert(0, valor_atual)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entradas[col] = entry

    def salvar():
        # Captura os dados de Caixa e Posição informados pelo usuário
        val_caixa = entradas["Caixa"].get().strip()
        val_posicao = entradas["Posição"].get().strip()

        # 🎯 CORREÇÃO 2: Valida se Caixa e Posição são números válidos para não quebrar o banco
        if not val_caixa.isdigit() or not val_posicao.isdigit():
            messagebox.showerror("Erro", "Os campos 'Caixa' e 'Posição' devem ser apenas números!")
            return

        fb.atualizar_vinil(
            id_registro,
            entradas["Música"].get().strip(),
            entradas["Artista"].get().strip(),
            entradas["Versão"].get().strip(),
            entradas["Vinil"].get().strip(),
            entradas["BPM"].get().strip(),
            int(val_caixa),
            int(val_posicao)
        )
        janela.destroy()
        callback_atualizar()
        messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")

    tk.Button(janela, text="Salvar Alterações", command=salvar, bg="#90cdf4").grid(row=len(campos), columnspan=2, pady=15)
