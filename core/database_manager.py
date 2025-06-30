# core/database_manager.py (Versão com Sistema de Anexos PDF)
import sqlite3
import os
import shutil
import uuid
from PySide6.QtCore import QDate

class DatabaseManager:
    def __init__(self, db_file="pinknote.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._setup_tables()

    def _setup_tables(self):
        # Tabela de notas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT,
                category TEXT, modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de eventos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                event_date TEXT NOT NULL,
                title TEXT NOT NULL
            )
        ''')
        
        # Tabela de anexos PDF
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY,
                note_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
        print("Banco de dados e tabelas configurados com sucesso.")

    # --- MÉTODOS DE NOTAS (sem mudanças) ---
    # ... (todos os seus métodos de notas continuam aqui) ...
    def get_all_notes(self):
        self.cursor.execute("SELECT id, title, content FROM notes ORDER BY modified_at DESC")
        return self.cursor.fetchall()
    def get_note_by_id(self, note_id):
        self.cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        return self.cursor.fetchone()
    def add_note(self, title, content):
        try:
            self.cursor.execute("INSERT INTO notes (title, content, category) VALUES (?, ?, ?)",(title, content, "Geral"))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e: print(f"Erro ao adicionar nota: {e}"); return None
    def update_note(self, note_id, title, content):
        try:
            self.cursor.execute("UPDATE notes SET title = ?, content = ?, modified_at = CURRENT_TIMESTAMP WHERE id = ?",(title, content, note_id))
            self.conn.commit()
        except sqlite3.Error as e: print(f"Erro ao atualizar nota: {e}")
    def delete_note(self, note_id):
        try:
            self.cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            self.conn.commit()
        except sqlite3.Error as e: print(f"Erro ao deletar nota: {e}")

    # --- MÉTODOS PARA EVENTOS ---
    def add_event(self, event_date, title):
        # ... (sem mudanças) ...
        try:
            self.cursor.execute("INSERT INTO events (event_date, title) VALUES (?, ?)", (event_date, title))
            self.conn.commit()
            print(f"Evento '{title}' adicionado para {event_date}.")
        except sqlite3.Error as e: print(f"Erro ao adicionar evento: {e}")

    def get_events_for_date(self, event_date):
        """MODIFICADO: Busca ID e título dos eventos de uma data."""
        self.cursor.execute("SELECT id, title FROM events WHERE event_date = ?", (event_date,))
        return self.cursor.fetchall()

    # NOVO MÉTODO para deletar um evento pelo seu ID
    def delete_event(self, event_id):
        """Deleta um evento específico pelo seu ID."""
        try:
            self.cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            self.conn.commit()
            print(f"Evento com ID {event_id} deletado com sucesso.")
        except sqlite3.Error as e:
            print(f"Erro ao deletar evento: {e}")

    def get_all_event_dates(self):
        # ... (sem mudanças) ...
        self.cursor.execute("SELECT DISTINCT event_date FROM events")
        return [row[0] for row in self.cursor.fetchall()]

    # --- MÉTODOS PARA ANEXOS PDF ---
    def add_attachment(self, note_id, filename, original_filename, file_path, file_size):
        """Adiciona um novo anexo PDF à nota especificada.
        
        Args:
            note_id (int): ID da nota à qual o anexo será vinculado
            filename (str): Nome do arquivo gerado pelo sistema
            original_filename (str): Nome original do arquivo
            file_path (str): Caminho completo do arquivo no sistema
            file_size (int): Tamanho do arquivo em bytes
            
        Returns:
            int: ID do anexo criado ou None em caso de erro
        """
        try:
            self.cursor.execute(
                "INSERT INTO attachments (note_id, filename, original_filename, file_path, file_size) "
                "VALUES (?, ?, ?, ?, ?)",
                (note_id, filename, original_filename, file_path, file_size)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar anexo: {e}")
            return None
    
    def get_attachments_for_note(self, note_id):
        """Retorna todos os anexos associados a uma nota específica.
        
        Args:
            note_id (int): ID da nota
            
        Returns:
            list: Lista de tuplas contendo informações dos anexos
        """
        self.cursor.execute(
            "SELECT id, filename, original_filename, file_path, file_size, created_at "
            "FROM attachments WHERE note_id = ? ORDER BY created_at DESC",
            (note_id,)
        )
        return self.cursor.fetchall()
    
    def delete_attachment(self, attachment_id):
        """Remove um anexo do banco de dados e exclui o arquivo físico.
        
        Args:
            attachment_id (int): ID do anexo a ser removido
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            # Primeiro, obtém o caminho do arquivo para excluí-lo do sistema de arquivos
            self.cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
            result = self.cursor.fetchone()
            
            if result and os.path.exists(result[0]):
                try:
                    os.remove(result[0])
                except OSError as e:
                    print(f"Erro ao excluir arquivo físico: {e}")
            
            # Em seguida, remove o registro do banco de dados
            self.cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir anexo: {e}")
            return False
    
    def get_attachment_path(self, attachment_id):
        """Retorna o caminho completo de um anexo específico.
        
        Args:
            attachment_id (int): ID do anexo
            
        Returns:
            str: Caminho completo do arquivo ou None se não encontrado
        """
        self.cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def close(self):
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada.")