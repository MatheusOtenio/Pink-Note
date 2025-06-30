# core/folder_manager.py
import sqlite3
import os

class FolderManager:
    """
    Classe responsável pelo gerenciamento de pastas hierárquicas no PinkNote.
    
    Esta classe fornece métodos para criar, renomear, excluir e navegar por pastas,
    bem como para mover notas entre pastas.
    """
    
    def __init__(self, db_connection, cursor):
        """
        Inicializa o gerenciador de pastas.
        
        Args:
            db_connection: Conexão com o banco de dados SQLite
            cursor: Cursor para executar comandos SQL
        """
        self.conn = db_connection
        self.cursor = cursor
    
    def get_all_folders(self):
        """
        Retorna todas as pastas ordenadas hierarquicamente.
        
        Returns:
            list: Lista de tuplas (id, name, parent_id, path)
        """
        self.cursor.execute(
            "SELECT id, name, parent_id, path FROM folders ORDER BY path"
        )
        return self.cursor.fetchall()
    
    def get_folder_by_id(self, folder_id):
        """
        Retorna uma pasta específica pelo seu ID.
        
        Args:
            folder_id (int): ID da pasta
            
        Returns:
            tuple: (id, name, parent_id, path) ou None se não encontrada
        """
        self.cursor.execute(
            "SELECT id, name, parent_id, path FROM folders WHERE id = ?",
            (folder_id,)
        )
        return self.cursor.fetchone()
    
    def get_subfolders(self, parent_id=None):
        """
        Retorna todas as subpastas de uma pasta específica.
        
        Args:
            parent_id (int, optional): ID da pasta pai. Se None, retorna pastas de nível raiz.
            
        Returns:
            list: Lista de tuplas (id, name, parent_id, path)
        """
        if parent_id is None:
            self.cursor.execute(
                "SELECT id, name, parent_id, path FROM folders WHERE parent_id IS NULL ORDER BY name"
            )
        else:
            self.cursor.execute(
                "SELECT id, name, parent_id, path FROM folders WHERE parent_id = ? ORDER BY name",
                (parent_id,)
            )
        return self.cursor.fetchall()
    
    def create_folder(self, name, parent_id=None):
        """
        Cria uma nova pasta.
        
        Args:
            name (str): Nome da pasta
            parent_id (int, optional): ID da pasta pai. Se None, cria no nível raiz.
            
        Returns:
            int: ID da pasta criada ou None em caso de erro
        """
        try:
            # Verifica se já existe uma pasta com o mesmo nome no mesmo nível
            if parent_id is None:
                self.cursor.execute(
                    "SELECT id FROM folders WHERE name = ? AND parent_id IS NULL",
                    (name,)
                )
            else:
                self.cursor.execute(
                    "SELECT id FROM folders WHERE name = ? AND parent_id = ?",
                    (name, parent_id)
                )
                
            if self.cursor.fetchone():
                print(f"Já existe uma pasta chamada '{name}' neste nível.")
                return None
            
            # Determina o caminho completo da pasta
            path = "/" + name
            if parent_id is not None:
                parent = self.get_folder_by_id(parent_id)
                if parent:
                    path = parent[3] + "/" + name
            
            # Insere a nova pasta
            self.cursor.execute(
                "INSERT INTO folders (name, parent_id, path) VALUES (?, ?, ?)",
                (name, parent_id, path)
            )
            self.conn.commit()
            return self.cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"Erro ao criar pasta: {e}")
            return None
    
    def rename_folder(self, folder_id, new_name):
        """
        Renomeia uma pasta e atualiza os caminhos de todas as subpastas.
        
        Args:
            folder_id (int): ID da pasta a ser renomeada
            new_name (str): Novo nome para a pasta
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        try:
            # Obtém informações da pasta atual
            folder = self.get_folder_by_id(folder_id)
            if not folder:
                return False
                
            old_name = folder[1]
            old_path = folder[3]
            parent_id = folder[2]
            
            # Verifica se já existe uma pasta com o mesmo nome no mesmo nível
            if parent_id is None:
                self.cursor.execute(
                    "SELECT id FROM folders WHERE name = ? AND parent_id IS NULL AND id != ?",
                    (new_name, folder_id)
                )
            else:
                self.cursor.execute(
                    "SELECT id FROM folders WHERE name = ? AND parent_id = ? AND id != ?",
                    (new_name, parent_id, folder_id)
                )
                
            if self.cursor.fetchone():
                print(f"Já existe uma pasta chamada '{new_name}' neste nível.")
                return False
            
            # Calcula o novo caminho
            if parent_id is None:
                new_path = "/" + new_name
            else:
                parent = self.get_folder_by_id(parent_id)
                new_path = parent[3] + "/" + new_name
            
            # Inicia uma transação
            self.conn.execute("BEGIN TRANSACTION")
            
            # Atualiza o nome e caminho da pasta
            self.cursor.execute(
                "UPDATE folders SET name = ?, path = ? WHERE id = ?",
                (new_name, new_path, folder_id)
            )
            
            # Atualiza os caminhos de todas as subpastas
            self.cursor.execute(
                "SELECT id, path FROM folders WHERE path LIKE ?",
                (old_path + "/%",)
            )
            subfolders = self.cursor.fetchall()
            
            for subfolder_id, subfolder_path in subfolders:
                new_subfolder_path = new_path + subfolder_path[len(old_path):]
                self.cursor.execute(
                    "UPDATE folders SET path = ? WHERE id = ?",
                    (new_subfolder_path, subfolder_id)
                )
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            print(f"Erro ao renomear pasta: {e}")
            return False
    
    def delete_folder(self, folder_id):
        """
        Exclui uma pasta e todas as suas subpastas.
        As notas contidas na pasta e subpastas são movidas para a pasta 'Geral'.
        
        Args:
            folder_id (int): ID da pasta a ser excluída
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        try:
            # Verifica se a pasta existe
            folder = self.get_folder_by_id(folder_id)
            if not folder:
                return False
                
            # Não permite excluir a pasta 'Geral'
            if folder[1] == "Geral" and folder[2] is None:
                print("A pasta 'Geral' não pode ser excluída.")
                return False
            
            # Obtém o ID da pasta 'Geral'
            self.cursor.execute(
                "SELECT id FROM folders WHERE name = 'Geral' AND parent_id IS NULL"
            )
            general_folder = self.cursor.fetchone()
            if not general_folder:
                print("Pasta 'Geral' não encontrada.")
                return False
                
            general_folder_id = general_folder[0]
            
            # Inicia uma transação
            self.conn.execute("BEGIN TRANSACTION")
            
            # Move todas as notas da pasta e subpastas para a pasta 'Geral'
            self.cursor.execute(
                "UPDATE notes SET folder_id = ? WHERE folder_id = ?",
                (general_folder_id, folder_id)
            )
            
            # Obtém todas as subpastas
            self.cursor.execute(
                "SELECT id FROM folders WHERE path LIKE ?",
                (folder[3] + "/%",)
            )
            subfolders = self.cursor.fetchall()
            
            # Move as notas das subpastas para a pasta 'Geral'
            for subfolder in subfolders:
                self.cursor.execute(
                    "UPDATE notes SET folder_id = ? WHERE folder_id = ?",
                    (general_folder_id, subfolder[0])
                )
            
            # Exclui a pasta (as subpastas serão excluídas automaticamente devido à restrição ON DELETE CASCADE)
            self.cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            print(f"Erro ao excluir pasta: {e}")
            return False
    
    def move_folder(self, folder_id, new_parent_id=None):
        """
        Move uma pasta para outro local na hierarquia.
        
        Args:
            folder_id (int): ID da pasta a ser movida
            new_parent_id (int, optional): ID da nova pasta pai. Se None, move para o nível raiz.
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        try:
            # Verifica se a pasta existe
            folder = self.get_folder_by_id(folder_id)
            if not folder:
                return False
                
            # Não permite mover a pasta 'Geral'
            if folder[1] == "Geral" and folder[2] is None:
                print("A pasta 'Geral' não pode ser movida.")
                return False
                
            # Verifica se a nova pasta pai existe (se não for None)
            if new_parent_id is not None:
                new_parent = self.get_folder_by_id(new_parent_id)
                if not new_parent:
                    return False
                    
                # Verifica se a pasta de destino não é a própria pasta ou uma subpasta
                if new_parent_id == folder_id or new_parent[3].startswith(folder[3] + "/"):
                    print("Não é possível mover uma pasta para dentro dela mesma ou para uma de suas subpastas.")
                    return False
            
            # Verifica se já existe uma pasta com o mesmo nome no destino
            if new_parent_id is None:
                self.cursor.execute(
                    "SELECT id FROM folders WHERE name = ? AND parent_id IS NULL AND id != ?",
                    (folder[1], folder_id)
                )
            else:
                self.cursor.execute(
                    "SELECT id FROM folders WHERE name = ? AND parent_id = ? AND id != ?",
                    (folder[1], new_parent_id, folder_id)
                )
                
            if self.cursor.fetchone():
                print(f"Já existe uma pasta chamada '{folder[1]}' no destino.")
                return False
            
            # Calcula o novo caminho
            old_path = folder[3]
            if new_parent_id is None:
                new_path = "/" + folder[1]
            else:
                new_parent = self.get_folder_by_id(new_parent_id)
                new_path = new_parent[3] + "/" + folder[1]
            
            # Inicia uma transação
            self.conn.execute("BEGIN TRANSACTION")
            
            # Atualiza a pasta
            self.cursor.execute(
                "UPDATE folders SET parent_id = ?, path = ? WHERE id = ?",
                (new_parent_id, new_path, folder_id)
            )
            
            # Atualiza os caminhos de todas as subpastas
            self.cursor.execute(
                "SELECT id, path FROM folders WHERE path LIKE ?",
                (old_path + "/%",)
            )
            subfolders = self.cursor.fetchall()
            
            for subfolder_id, subfolder_path in subfolders:
                new_subfolder_path = new_path + subfolder_path[len(old_path):]
                self.cursor.execute(
                    "UPDATE folders SET path = ? WHERE id = ?",
                    (new_subfolder_path, subfolder_id)
                )
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            print(f"Erro ao mover pasta: {e}")
            return False
    
    def move_note(self, note_id, folder_id):
        """
        Move uma nota para outra pasta.
        
        Args:
            note_id (int): ID da nota a ser movida
            folder_id (int): ID da pasta de destino
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        try:
            # Verifica se a nota existe
            self.cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
            if not self.cursor.fetchone():
                return False
                
            # Verifica se a pasta existe
            if folder_id is not None:  # Permitimos folder_id None para compatibilidade
                self.cursor.execute("SELECT id FROM folders WHERE id = ?", (folder_id,))
                if not self.cursor.fetchone():
                    return False
            
            # Atualiza a pasta da nota
            self.cursor.execute(
                "UPDATE notes SET folder_id = ? WHERE id = ?",
                (folder_id, note_id)
            )
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao mover nota: {e}")
            return False
    
    def get_notes_in_folder(self, folder_id):
        """
        Retorna todas as notas em uma pasta específica.
        
        Args:
            folder_id (int): ID da pasta
            
        Returns:
            list: Lista de tuplas (id, title, content) das notas na pasta
        """
        self.cursor.execute(
            "SELECT id, title, content FROM notes WHERE folder_id = ? ORDER BY modified_at DESC",
            (folder_id,)
        )
        return self.cursor.fetchall()
    
    def get_folder_note_count(self, folder_id):
        """
        Retorna o número de notas em uma pasta específica.
        
        Args:
            folder_id (int): ID da pasta
            
        Returns:
            int: Número de notas na pasta
        """
        self.cursor.execute(
            "SELECT COUNT(*) FROM notes WHERE folder_id = ?",
            (folder_id,)
        )
        return self.cursor.fetchone()[0]
    
    def search_notes_across_folders(self, search_term):
        """
        Pesquisa notas em todas as pastas que contenham o termo de pesquisa no título ou conteúdo.
        
        Args:
            search_term (str): Termo a ser pesquisado
            
        Returns:
            list: Lista de tuplas (id, title, content, folder_id, folder_name) das notas encontradas
        """
        search_pattern = f"%{search_term}%"
        self.cursor.execute(
            """SELECT n.id, n.title, n.content, n.folder_id, f.name 
               FROM notes n 
               LEFT JOIN folders f ON n.folder_id = f.id 
               WHERE n.title LIKE ? OR n.content LIKE ? 
               ORDER BY n.modified_at DESC""",
            (search_pattern, search_pattern)
        )
        return self.cursor.fetchall()