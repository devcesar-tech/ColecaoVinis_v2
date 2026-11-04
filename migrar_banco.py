import csv
import os
import sqlite3
import re

# Descobre a pasta onde este script está salvo
pasta_atual = os.path.dirname(os.path.abspath(__file__))

# Configura os caminhos assumindo que o CSV está na mesma pasta do script
arquivo_csv = os.path.join(pasta_atual, "meus_discos.csv")
arquivo_banco = os.path.join(pasta_atual, "colecao_vinis.db")

def iniciar_migracao():
    # Validação de segurança: avisa se o arquivo não estiver na pasta correta
    if not os.path.exists(arquivo_csv):
        print("❌ Erro: O arquivo 'meus_discos.csv' não foi encontrado na pasta principal!")
        print(f"Por favor, certifique-se de que ele está em: {pasta_atual}")
        return

    print("🔄 Conectando ao Banco de Dados SQLite...")
    conn = sqlite3.connect(arquivo_banco)
    cursor = conn.cursor()

    # Cria a estrutura da tabela limpa com tipos de dados adequados (Inteiros para Caixa/Posição/BPM)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vinis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        musica TEXT NOT NULL,
        artista TEXT NOT NULL,
        versao TEXT,
        vinil TEXT,
        bpm INTEGER,
        caixa INTEGER NOT NULL,
        posicao INTEGER NOT NULL,
        estado TEXT DEFAULT 'Bom'
    )
    """)

    linhas_migradas = 0

    print("📖 Lendo os dados do seu arquivo Excel .csv antigo...")
    # Abre o arquivo usando codificação latin-1 para preservar acentos e caracteres especiais
    with open(arquivo_csv, mode='r', encoding='latin-1') as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=';')
        
        for linha in leitor:
            # Captura o texto da localização (pode estar na coluna CAIXAS ou POSICAO)
            texto_caixa = linha.get("CAIXAS", "") or linha.get("POSICAO", "")
            
            # Algoritmo de Inteligência Artificial / RegEx: Extrai os números isolados do texto
            # Transforma "Caixa 5 - Pos 32" em números separados: caixa=5, posicao=32
            match = re.search(r'Caixa\s*(\d+)\s*-\s*Pos\s*(\d+)', str(texto_caixa), re.IGNORECASE)
            
            if match:
                num_caixa = int(match.group(1))
                num_posicao = int(match.group(2))
            else:
                num_caixa = 1
                num_posicao = 1

            # Tratamento de dados para o BPM (se estiver vazio no Excel, salva como nulo no banco)
            try:
                val_bpm = int(linha["BPM"]) if linha["BPM"] and linha["BPM"].strip().isdigit() else None
            except (ValueError, KeyError):
                val_bpm = None

            # Insere a faixa de música formatada na nova tabela relacional
            cursor.execute("""
                INSERT INTO vinis (musica, artista, versao, vinil, bpm, caixa, posicao, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                linha.get("MUSICA", "Música Sem Nome").strip(),
                linha.get("ARTISTA", "Artista Desconhecido").strip(),
                linha.get("VERSAO", "").strip(),
                linha.get("VINIL", "").strip(),
                val_bpm,
                num_caixa,
                num_posicao,
                "Bom" # Todos os discos antigos começam com o estado padrão 'Bom'
            ))
            linhas_migradas += 1

    conn.commit()
    conn.close()
    print(f"🎉 MÁGICA CONCLUÍDA! {linhas_migradas} faixas foram importadas para o arquivo '{os.path.basename(arquivo_banco)}'!")

if __name__ == "__main__":
    iniciar_migracao()
