import sqlite3

def criar_banco():
    conn = sqlite3.connect("babelup.db")
    c = conn.cursor()

    # Tabela de Usuários (com plano e vencimento)
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT,
            telefone TEXT,
            email TEXT,
            senha TEXT,
            idiomas_contratados TEXT,
            plano TEXT,
            nivel TEXT,
            data_pagamento TEXT,  -- Aqui fica a data de vencimento atual
            status_curso TEXT
        )
    ''')

    # Tabela de Pagamentos (Histórico com vencimento de cada compra)
    c.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            idiomas TEXT,
            plano TEXT,
            valor REAL,
            metodo TEXT,
            vencimento TEXT,      -- Data calculada (Ex: +30, +180 ou +365 dias)
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados 'babelup.db' criado/atualizado com sucesso!")

if __name__ == "__main__":
    criar_banco()