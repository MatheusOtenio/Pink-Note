# core/database_manager.py (Versão com Deleção de Eventos)
import sqlite3
from PySide6.QtCore import QDate

class DatabaseManager:
    def __init__(self, db_file="pinknote.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._setup_tables()

    def _setup_tables(self):
        # ... (código da criação de tabelas continua o mesmo) ...
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT,
                category TEXT, modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                event_date TEXT NOT NULL,
                title TEXT NOT NULL
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

    def close(self):
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada.")