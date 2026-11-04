import sqlite3
import os

#pasta_atual = os.path.dirname(os.path.abspath(__file__))
#arquivo_banco = os.path.join(pasta_atual, "colecao_vinis.db")
import sys

# Descobre se está rodando como executável (.exe) ou script normal (.py)
if getattr(sys, 'frozen', False):
    pasta_atual = os.path.dirname(sys.executable)
else:
    pasta_atual = os.path.dirname(os.path.abspath(__file__))

arquivo_banco = os.path.join(pasta_atual, "colecao_vinis.db")

#aqui retorna ao original
def obter_conexao():
    return sqlite3.connect(arquivo_banco)

def buscar_vinis(busca="", bpm_min="", bpm_max=""):
    conn = obter_conexao()
    cursor = conn.cursor()
    query = "SELECT id, musica, artista, versao, vinil, bpm, caixa, posicao, estado FROM vinis WHERE 1=1"
    parametros = []

    if busca:
        query += " AND (musica LIKE ? OR artista LIKE ? OR vinil LIKE ?)"
        parametros.extend([f"%{busca}%", f"%{busca}%", f"%{busca}%"])
    if bpm_min.isdigit():
        query += " AND bpm >= ?"
        parametros.append(int(bpm_min))
    if bpm_max.isdigit():
        query += " AND bpm <= ?"
        parametros.append(int(bpm_max))

    # Ordena por caixa e por posição. Itens na mesma posição física aparecerão juntos.
    query += " ORDER BY caixa ASC, posicao ASC"
    cursor.execute(query, parametros)
    dados = cursor.fetchall()
    conn.close()
    return dados

def calcular_estatisticas():
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # Total geral de faixas
    cursor.execute("SELECT COUNT(*) FROM vinis")
    total = cursor.fetchone()[0]
    
    # Artista mais repetido
    cursor.execute("SELECT artista, COUNT(artista) as qtd FROM vinis GROUP BY artista ORDER BY qtd DESC LIMIT 1")
    res_artista = cursor.fetchone()
    artista_text = f"{res_artista[0]}\n({res_artista[1]} faixas)" if res_artista else "-"
    
    # Caixa mais cheia
    cursor.execute("SELECT caixa, COUNT(caixa) as qtd FROM vinis GROUP BY caixa ORDER BY qtd DESC LIMIT 1")
    res_caixa = cursor.fetchone()
    caixa_text = f"Caixa {res_caixa[0]}\n({res_caixa[1]} faixas)" if res_caixa else "-"
    
    # Quantidade de discos furados
    cursor.execute("SELECT COUNT(*) FROM vinis WHERE estado = 'Furado'")
    furados = cursor.fetchone()[0]
    
    # 📊 Estatística por caixa (CONTA DISCOS FÍSICOS, NÃO FAIXAS)
    # Mudamos COUNT(DISTINCT posicao) para contar as posições físicas reais existentes
    cursor.execute("SELECT caixa, COUNT(DISTINCT posicao) FROM vinis GROUP BY caixa ORDER BY caixa ASC")
    res_por_caixa = cursor.fetchall()
    texto_por_caixa = " / ".join([f"Cx {cx}: {qtd}" for cx, qtd in res_por_caixa]) if res_por_caixa else "Nenhuma"
    
    conn.close()
    return total, artista_text, caixa_text, furados, texto_por_caixa

def alternar_estado(id_registro, estado_atual):
    novo_estado = "Furado" if estado_atual == "Bom" else "Bom"
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("UPDATE vinis SET estado = ? WHERE id = ?", (novo_estado, id_registro))
    conn.commit()
    conn.close()

def checar_duplicado(musica, artista, versao):
    conn = obter_conexao()
    cursor = conn.cursor()
    if versao:
        cursor.execute("SELECT caixa, posicao FROM vinis WHERE musica = ? AND artista = ? AND versao = ?", (musica, artista, versao))
    else:
        cursor.execute("SELECT caixa, posicao FROM vinis WHERE musica = ? AND artista = ? AND (versao IS NULL OR versao = '')", (musica, artista))
    duplicado = cursor.fetchone()
    conn.close()
    return duplicado

def salvar_vinil_com_deslocamento(alvo_caixa, alvo_posicao, lista_faixas):
    """
    MODIFICADO: Abre exatamente 1 espaço físico na caixa (+1) para os discos 
    que estão depois da posição alvo, independentemente de quantas faixas o disco novo tem.
    """
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # Garante que os valores sejam numéricos para evitar falhas do SQLite
    alvo_caixa = int(alvo_caixa)
    alvo_posicao = int(alvo_posicao)
    
    # Empurra os discos antigos em 1 posição para a frente para abrir o espaço físico do novo disco
    cursor.execute(
        "UPDATE vinis SET posicao = posicao + 1 WHERE caixa = ? AND posicao >= ?", 
        (alvo_caixa, alvo_posicao)
    )
    
    # Insere todas as faixas informadas (todas herdarão a mesma posição alvo)
    cursor.executemany("""
        INSERT INTO vinis (musica, artista, versao, vinil, bpm, caixa, posicao, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, lista_faixas)
    
    conn.commit()
    conn.close()

def deletar_vinil(id_registro):
    """
    MODIFICADO: Descobre a caixa e a posição física do disco antes de deletar.
    Após deletar a faixa, verifica se ainda restam outras faixas daquele mesmo disco físico.
    Se não restar nenhuma faixa naquela posição, puxa todos os discos seguintes de volta (-1).
    """
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # Garante que o ID seja um número inteiro puro
    id_registro = int(id_registro)
    
    # 1. Busca a localização do item antes de apagá-lo
    cursor.execute("SELECT caixa, posicao FROM vinis WHERE id = ?", (id_registro,))
    resultado = cursor.fetchone()
    
    if resultado:
        caixa_atual, posicao_atual = resultado
        
        # 2. Deleta a faixa selecionada
        cursor.execute("DELETE FROM vinis WHERE id = ?", (id_registro,))
        
        # 3. Verifica se ainda existem outras faixas ocupando ESSA MESMA POSIÇÃO FÍSICA
        # (Para evitar puxar os discos se você deletou apenas 1 faixa de um disco que tem 4)
        cursor.execute("SELECT COUNT(*) FROM vinis WHERE caixa = ? AND posicao = ?", (caixa_atual, posicao_atual))
        restantes_no_disco = cursor.fetchone()[0]
        
        # Se não sobrou nenhuma música nessa posição, significa que o espaço físico ficou vazio.
        # Então puxamos todos os discos que vinham depois dele 1 posição para trás (-1)
        if restantes_no_disco == 0:
            cursor.execute(
                "UPDATE vinis SET posicao = posicao - 1 WHERE caixa = ? AND posicao > ?", 
                (caixa_atual, posicao_atual)
            )
        
    conn.commit()
    conn.close()

def atualizar_vinil(id_registro, musica, artista, versao, vinil, bpm, caixa, posicao):
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # Garante que o ID e localizações sejam inteiros corretos
    id_registro = int(id_registro)
    
    cursor.execute("""
        UPDATE vinis 
        SET musica=?, artista=?, versao=?, vinil=?, bpm=?, caixa=?, posicao=?
        WHERE id=?
    """, (musica, artista, versao, vinil, int(bpm) if bpm and str(bpm).isdigit() else None, int(caixa), int(posicao), id_registro))
    conn.commit()
    conn.close()
