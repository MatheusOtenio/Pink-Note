# core/folder_migration.py
import sqlite3
import os

def migrate_database(db_file="pinknote.db"):
    """
    Migra o banco de dados para adicionar suporte a pastas hierárquicas.
    
    Esta função realiza as seguintes operações:
    1. Cria a tabela 'folders' para armazenar a estrutura de pastas
    2. Adiciona a coluna 'folder_id' à tabela 'notes'
    3. Cria uma pasta 'Geral' padrão
    4. Migra todas as notas existentes para a pasta 'Geral'
    5. Adiciona índices para melhorar a performance das consultas
    
    Args:
        db_file (str): Caminho para o arquivo do banco de dados SQLite
    
    Returns:
        bool: True se a migração foi bem-sucedida, False caso contrário
    """
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Verifica se a migração já foi realizada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='folders'")
        if cursor.fetchone():
            print("A migração já foi realizada anteriormente.")
            conn.close()
            return True
        
        # Inicia uma transação para garantir atomicidade
        conn.execute("BEGIN TRANSACTION")
        
        # 1. Cria a tabela de pastas
        cursor.execute('''
            CREATE TABLE folders (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                parent_id INTEGER,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES folders (id) ON DELETE CASCADE
            )
        ''')
        
        # 2. Adiciona a coluna folder_id à tabela notes
        cursor.execute("ALTER TABLE notes ADD COLUMN folder_id INTEGER")
        
        # 3. Cria a pasta 'Geral' padrão
        cursor.execute("INSERT INTO folders (name, parent_id, path) VALUES (?, NULL, ?);", 
                      ("Geral", "/Geral"))
        general_folder_id = cursor.lastrowid
        
        # 4. Migra todas as notas existentes para a pasta 'Geral'
        cursor.execute("UPDATE notes SET folder_id = ?", (general_folder_id,))
        
        # 5. Adiciona índices para melhorar a performance
        cursor.execute("CREATE INDEX idx_notes_folder_id ON notes (folder_id)")
        cursor.execute("CREATE INDEX idx_folders_parent_id ON folders (parent_id)")
        cursor.execute("CREATE INDEX idx_folders_path ON folders (path)")
        
        # Confirma as alterações
        conn.commit()
        print("Migração concluída com sucesso!")
        
        # Fecha a conexão
        conn.close()
        return True
        
    except sqlite3.Error as e:
        # Em caso de erro, reverte as alterações
        if conn:
            conn.rollback()
            conn.close()
        print(f"Erro durante a migração: {e}")
        return False

if __name__ == "__main__":
    # Executa a migração quando o script é executado diretamente
    migrate_database()