import tkinter as tk
from tkinter import messagebox, ttk
import funcoes_banco as fb
import janela_editar as je  # Importa o arquivo modular de edição

class AppVinisPro:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("👑 Catálogo de Vinis - Modular ADS Edition")
        self.raiz.geometry("1200x650")

        # Cria a lista na memória para guardar as músicas da sua playlist:
        self.playlist_atual = []


        # ==================== PAINEL SUPERIOR: FILTROS ====================
        frame_top = tk.LabelFrame(raiz, text=" 🔍 Filtros de Busca & Mixagem (BPM) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_top.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_top, text="Texto:").grid(row=0, column=0, padx=5, sticky="e")
        self.entry_busca = tk.Entry(frame_top, width=30)
        self.entry_busca.grid(row=0, column=1, padx=5)
        self.entry_busca.bind("<KeyRelease>", lambda e: self.carregar_dados())
        
        tk.Label(frame_top, text="BPM Mín:").grid(row=0, column=2, padx=5, sticky="e")
        self.entry_bpm_min = tk.Entry(frame_top, width=6)
        self.entry_bpm_min.grid(row=0, column=3, padx=5)
        self.entry_bpm_min.bind("<KeyRelease>", lambda e: self.carregar_dados())
        
        tk.Label(frame_top, text="BPM Máx:").grid(row=0, column=4, padx=5, sticky="e")
        self.entry_bpm_max = tk.Entry(frame_top, width=6)
        self.entry_bpm_max.grid(row=0, column=5, padx=5)
        self.entry_bpm_max.bind("<KeyRelease>", lambda e: self.carregar_dados())

        tk.Button(frame_top, text="Limpar Filtros", command=self.limpar_filtros, bg="#e2e8f0").grid(row=0, column=6, padx=15)

        # ==================== PAINEL LATERAL ESQUERDO: ESTATÍSTICAS ====================
        self.frame_esquerda = tk.LabelFrame(raiz, text=" 📊 Estatísticas ", font=("Arial", 10, "bold"), padx=10, pady=10)
        self.frame_esquerda.pack(side="left", fill="y", padx=10, pady=5)
        
        self.lbl_total = tk.Label(self.frame_esquerda, text="Total de Faixas: 0", font=("Arial", 11))
        self.lbl_total.pack(anchor="w", pady=5)
        self.lbl_artista = tk.Label(self.frame_esquerda, text="Rei da Coleção: -", font=("Arial", 11), fg="#3182ce")
        self.lbl_artista.pack(anchor="w", pady=5)
        self.lbl_caixa = tk.Label(self.frame_esquerda, text="Caixa Mais Cheia: -", font=("Arial", 11))
        self.lbl_caixa.pack(anchor="w", pady=5)
        self.lbl_furados = tk.Label(self.frame_esquerda, text="Discos Furados: 0", font=("Arial", 11), fg="#e53e3e")
        self.lbl_furados.pack(anchor="w", pady=5)

        # Rótulo: Quantidade detalhada por caixa
        tk.Label(self.frame_esquerda, text="Discos por Caixa:", font=("Arial", 10, "bold"), fg="#2b6cb0").pack(anchor="w", pady=(10, 2))
        self.lbl_por_caixa = tk.Label(self.frame_esquerda, text="-", font=("Arial", 10), justify="left", wraplength=220)
        self.lbl_por_caixa.pack(anchor="w", pady=2)

        tk.Frame(self.frame_esquerda, height=2, bd=1, relief="sunken", bg="gray").pack(fill="x", pady=15)
        tk.Button(self.frame_esquerda, text="⚠️ Alternar Estado (Bom/Furado)", bg="#ed8936", fg="white", font=("Arial", 9, "bold"), command=self.alternar_estado_disco).pack(fill="x", pady=5)

        # ==================== PAINEL CENTRAL: TABELA COM BARRA DE ROLAGEM ====================
        frame_centro = tk.Frame(raiz)
        frame_centro.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        frame_tabela = tk.Frame(frame_centro)
        frame_tabela.pack(fill="both", expand=True, pady=5)

        colunas = ("ID", "Música", "Artista", "Versão", "Vinil", "BPM", "Caixa", "Posição", "Estado")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        
        # Barra de Rolagem (Scrollbar) conectada à tabela
        scrollbar_vertical = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_vertical.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_vertical.pack(side="right", fill="y")

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=95, anchor="center")
        self.tree.column("Música", width=170, anchor="w")
        self.tree.column("Artista", width=140, anchor="w")

        frame_botoes = tk.Frame(frame_centro)
        frame_botoes.pack(fill="x", pady=5)

        tk.Button(frame_botoes, text="➕ Inserir Novo Vinil", bg="#bdecb6", font=("Arial", 10, "bold"), command=self.abrir_janela_inserir).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="✏️ Editar Selecionado", bg="#90cdf4", command=self.chamar_edicao).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="❌ Excluir Selecionado", bg="#feb2b2", command=self.excluir_vinil).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="+ Playlist", bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), command=self.adicionar_a_playlist).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Salvar Playlist (.txt)", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=self.salvar_playlist_txt).pack(side="left", padx=5)

        self.carregar_dados()
    
    # dados novos
    def adicionar_a_playlist(self):
        # 1. Verifica se o usuário selecionou alguma linha na Treeview
        selecionado = self.tree.selection()
        if not selecionado:
            from tkinter import messagebox
            messagebox.showwarning("Aviso", "Por favor, selecione uma música na tabela primeiro!")
            return
        
        # 2. Pega os dados da linha selecionada
        item = self.tree.item(selecionado)
        valores = item['values']
        
        # Mapeia as colunas certas do seu banco de dados
        musica = valores[1]
        artista = valores[2]
        vinil = valores[4]
        caixa = valores[6]
        posicao = valores[7]
        
        # 3. Guarda as informações formatadas na lista
        dados_musica = f"Música: {musica} | Artista: {artista} | Vinil: {vinil} | Caixa: {caixa} - Posição: {posicao}"
        self.playlist_atual.append(dados_musica)
        
        # 4. Avisa o usuário que deu certo
        from tkinter import messagebox
        messagebox.showinfo("Playlist", f"'{musica}' adicionada!\nTotal na playlist: {len(self.playlist_atual)}")

    def salvar_playlist_txt(self):
        from tkinter import messagebox
        if not self.playlist_atual:
            messagebox.showwarning("Aviso", "A playlist está vazia! Adicione músicas primeiro.")
            return
        
        # Abre a janela para escolher onde salvar o arquivo
        from tkinter import filedialog
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt")],
            title="Salvar Playlist"
        )
        
        if arquivo:
            try:
                with open(arquivo, "w", encoding="utf-8") as f:
                    f.write("=== MINHA PLAYLIST DE VINIS ===\n\n")
                    for i, musica in enumerate(self.playlist_atual, start=1):
                        f.write(f"{i}. {musica}\n")
                
                messagebox.showinfo("Sucesso", "Playlist salva com sucesso em formato TXT!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")

    # dados antigos 
    def limpar_filtros(self):
        self.entry_busca.delete(0, tk.END)
        self.entry_bpm_min.delete(0, tk.END)
        self.entry_bpm_max.delete(0, tk.END)
        self.carregar_dados()

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        dados = fb.buscar_vinis(self.entry_busca.get(), self.entry_bpm_min.get(), self.entry_bpm_max.get())
        for linha in dados:
            self.tree.insert("", "end", values=linha)
        
        self.atualizar_estatisticas()
    def atualizar_estatisticas(self):
        total, artista, caixa, furados, texto_caixas = fb.calcular_estatisticas()
        self.lbl_total.config(text=f"Total de Faixas: {total}")
        self.lbl_artista.config(text=f"Rei da Coleção:\n{artista}")
        self.lbl_caixa.config(text=f"Caixa Mais Cheia:\n{caixa}")
        self.lbl_furados.config(text=f"Discos Furados: {furados}")
        self.lbl_por_caixa.config(text=texto_caixas)

    def alternar_estado_disco(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item na tabela!")
            return
        valores = self.tree.item(selecionado)['values']
        fb.alternar_estado(int(valores[0]), valores[8])
        self.carregar_dados()

    def chamar_edicao(self):
        je.abrir(self.raiz, self.tree, self.carregar_dados)

    def abrir_janela_inserir(self):
        janela_ins = tk.Toplevel(self.raiz)
        janela_ins.title("Inserir Novo Vinil")
        janela_ins.geometry("320x250")

        campos = ["Título do Vinil", "Caixa (Número)", "Posição Desejada", "Qtd de Faixas"]
        entradas = {}

        for i, campo in enumerate(campos):
            tk.Label(janela_ins, text=campo).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(janela_ins)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entradas[campo] = entry

        def avancar():
            try:
                titulo = entradas["Título do Vinil"].get().strip()
                caixa = int(entradas["Caixa (Número)"].get().strip())
                posicao = int(entradas["Posição Desejada"].get().strip())
                qtd = int(entradas["Qtd de Faixas"].get().strip())
            except ValueError:
                messagebox.showerror("Erro", "Campos numéricos inválidos.")
                return

            if not titulo:
                messagebox.showerror("Erro", "O título do vinil é obrigatório.")
                return

            janela_ins.destroy()
            self.coletar_faixas(titulo, caixa, posicao, qtd)

        tk.Button(janela_ins, text="Avançar para Músicas ➡️", bg="#bdecb6", command=avancar).grid(row=len(campos), columnspan=2, pady=15)

    def coletar_faixas(self, titulo, caixa, posicao_inicial, total_faixas):
        janela_faixas = tk.Toplevel(self.raiz)
        janela_faixas.title(f"Cadastro - {titulo}")
        janela_faixas.geometry("350x280")

        lbl_status = tk.Label(janela_faixas, text=f"Música 1 de {total_faixas}", font=("Arial", 10, "bold"))
        lbl_status.pack(pady=5)

        frame_campos = tk.Frame(janela_faixas)
        frame_campos.pack(pady=5)

        campos_musica = ["MUSICA", "ARTISTA", "VERSAO", "BPM"]
        entradas_musica = {}

        for i, cm in enumerate(campos_musica):
            tk.Label(frame_campos, text=cm).grid(row=i, column=0, padx=10, pady=3, sticky="w")
            entry = tk.Entry(frame_campos, width=25)
            entry.grid(row=i, column=1, padx=10, pady=3)
            entradas_musica[cm] = entry

        faixas_coletadas = []

        def salvar_faixa_atual():
            musica = entradas_musica["MUSICA"].get().strip()
            artista = entradas_musica["ARTISTA"].get().strip()
            versao = entradas_musica["VERSAO"].get().strip()
            bpm = entradas_musica["BPM"].get().strip()

            if not musica or not artista:
                messagebox.showerror("Erro", "Música e Artista são obrigatórios!")
                return

            duplicado = fb.checar_duplicado(musica, artista, versao)
            if duplicado:
                resposta = messagebox.askyesno("Alerta de Duplicata", f"'{musica}' já existe na Caixa {duplicado[0]}, Pos {duplicado[1]}.\nInserir mesmo assim?")
                if not resposta: 
                    return

            faixas_coletadas.append((musica, artista, versao, titulo, int(bpm) if bpm.isdigit() else None, caixa, posicao_inicial, "Bom"))

            for entry in entradas_musica.values():
                entry.delete(0, tk.END)

            atual = len(faixas_coletadas) + 1
            if atual <= total_faixas:
                lbl_status.config(text=f"Música {atual} de {total_faixas}")
                entradas_musica["MUSICA"].focus()
            else:
                janela_faixas.destroy()
                fb.salvar_vinil_com_deslocamento(caixa, posicao_inicial, faixas_coletadas)
                self.carregar_dados()

        tk.Button(janela_faixas, text="Próxima Faixa ➡️", bg="#e2e8f0", command=salvar_faixa_atual).pack(pady=15)

    def excluir_vinil(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para excluir.")
            return
        valores = self.tree.item(selecionado)['values']
        id_registro = int(valores[0])
        if messagebox.askyesno("Confirmar", "Excluir a música da coleção?"):
            fb.deletar_vinil(id_registro)
            self.carregar_dados()

if __name__ == "__main__":
    raiz = tk.Tk()
    app = AppVinisPro(raiz)
    raiz.mainloop()
