# ui/folder_tree_widget.py
import os
from PySide6.QtCore import Qt, Signal, QSize, QMimeData, QPoint
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel, QMenu, QInputDialog, QMessageBox, QSizePolicy, QFrame, QHeaderView
)
from PySide6.QtGui import QIcon, QDrag, QCursor, QAction

class FolderTreeWidget(QWidget):
    """
    Widget para exibir e gerenciar a estrutura hierárquica de pastas.
    
    Este widget permite visualizar, criar, renomear, excluir e mover pastas,
    bem como mover notas entre pastas via drag-and-drop.
    
    Signals:
        folder_selected: Emitido quando uma pasta é selecionada (folder_id)
        folder_created: Emitido quando uma nova pasta é criada (folder_id)
        folder_renamed: Emitido quando uma pasta é renomeada (folder_id)
        folder_deleted: Emitido quando uma pasta é excluída (folder_id)
        folder_moved: Emitido quando uma pasta é movida (folder_id, new_parent_id)
        note_moved: Emitido quando uma nota é movida para outra pasta (note_id, folder_id)
    """
    
    folder_selected = Signal(int)  # folder_id
    folder_created = Signal(int)   # folder_id
    folder_renamed = Signal(int)   # folder_id
    folder_deleted = Signal(int)   # folder_id
    folder_moved = Signal(int, object)  # folder_id, new_parent_id
    note_moved = Signal(int, int)  # note_id, folder_id
    
    def __init__(self, db_manager):
        """
        Inicializa o widget de árvore de pastas.
        
        Args:
            db_manager: Instância do DatabaseManager para operações de banco de dados
        """
        super().__init__()
        
        self.db = db_manager
        self.current_folder_id = None
        self.dragged_note_id = None
        
        self._setup_ui()
        self._load_folders()
    
    def _setup_ui(self):
        """
        Configura a interface do usuário do widget.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título da seção
        title_layout = QHBoxLayout()
        title_label = QLabel("Pastas")
        title_label.setObjectName("folderTitle")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Botão de adicionar pasta
        self.add_button = QPushButton("+")
        self.add_button.setObjectName("addFolderButton")
        self.add_button.setToolTip("Adicionar nova pasta")
        self.add_button.setMaximumWidth(24)
        self.add_button.clicked.connect(self._add_folder)
        title_layout.addWidget(self.add_button)
        
        main_layout.addLayout(title_layout)
        
        # Árvore de pastas
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setIndentation(20)
        self.folder_tree.setAnimated(True)
        self.folder_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.folder_tree.setDragEnabled(True)
        self.folder_tree.setAcceptDrops(True)
        self.folder_tree.setDropIndicatorShown(True)
        self.folder_tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.folder_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.folder_tree.itemSelectionChanged.connect(self._on_folder_selected)
        self.folder_tree.customContextMenuRequested.connect(self._show_context_menu)
        self.folder_tree.itemChanged.connect(self._on_item_changed)
        
        main_layout.addWidget(self.folder_tree)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
    
    def _load_folders(self):
        """
        Carrega a estrutura de pastas do banco de dados e preenche a árvore.
        """
        # Bloqueia sinais para evitar chamadas durante a reconstrução da árvore
        self.folder_tree.blockSignals(True)
        self.folder_tree.clear()
        
        # Dicionário para mapear IDs de pastas para itens da árvore
        self.folder_items = {}
        
        try:
            # Obtém todas as pastas
            folders = self.db.get_all_folders()
            
            # Primeiro, adiciona as pastas de nível raiz
            root_folders = [f for f in folders if f[2] is None]  # parent_id is None
            for folder in root_folders:
                folder_id, name, _, _ = folder
                item = QTreeWidgetItem(self.folder_tree)
                
                # Adiciona o contador de notas
                note_count = self.db.get_folder_note_count(folder_id)
                display_name = f"{name} ({note_count})"
                
                item.setText(0, display_name)
                item.setData(0, Qt.ItemDataRole.UserRole, folder_id)
                self.folder_items[folder_id] = item
            
            # Em seguida, adiciona as subpastas
            non_root_folders = [f for f in folders if f[2] is not None]  # parent_id is not None
            
            # Ordena as pastas por profundidade do caminho para garantir que as pastas pai sejam adicionadas antes das filhas
            non_root_folders.sort(key=lambda f: f[3].count('/') if f[3] else 0)
            
            for folder in non_root_folders:
                folder_id, name, parent_id, _ = folder
                if parent_id in self.folder_items:
                    parent_item = self.folder_items[parent_id]
                    
                    # Verifica se o parent_item ainda é válido
                    if parent_item is None:
                        continue
                        
                    item = QTreeWidgetItem()
                    
                    # Adiciona o contador de notas
                    note_count = self.db.get_folder_note_count(folder_id)
                    display_name = f"{name} ({note_count})"
                    
                    item.setText(0, display_name)
                    item.setData(0, Qt.ItemDataRole.UserRole, folder_id)
                    
                    # Adiciona o item ao pai
                    parent_item.addChild(item)
                    self.folder_items[folder_id] = item
            
            # Expande todos os itens
            self.folder_tree.expandAll()
            
            # Seleciona a pasta 'Geral' por padrão
            general_folder_found = False
            for i in range(self.folder_tree.topLevelItemCount()):
                item = self.folder_tree.topLevelItem(i)
                if item and item.text(0).startswith("Geral"):
                    self.folder_tree.setCurrentItem(item)
                    general_folder_found = True
                    break
                    
            # Se não encontrou a pasta 'Geral', seleciona o primeiro item (se houver)
            if not general_folder_found and self.folder_tree.topLevelItemCount() > 0:
                self.folder_tree.setCurrentItem(self.folder_tree.topLevelItem(0))
        except Exception as e:
            print(f"Erro ao carregar pastas: {e}")
        finally:
            # Desbloqueia sinais após a reconstrução da árvore
            self.folder_tree.blockSignals(False)
    
    def _on_folder_selected(self):
        """
        Manipula a seleção de uma pasta na árvore.
        """
        selected_items = self.folder_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            folder_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.current_folder_id = folder_id
            self.folder_selected.emit(folder_id)
    
    def _show_context_menu(self, position):
        """
        Exibe o menu de contexto para operações de pasta.
        
        Args:
            position (QPoint): Posição do cursor onde o menu deve ser exibido
        """
        item = self.folder_tree.itemAt(position)
        if not item:
            return
            
        folder_id = item.data(0, Qt.ItemDataRole.UserRole)
        folder = self.db.get_folder_by_id(folder_id)
        if not folder:
            return
            
        # Cria o menu de contexto
        context_menu = QMenu(self)
        
        # Ações do menu
        add_action = QAction("Nova Pasta", self)
        rename_action = QAction("Renomear", self)
        delete_action = QAction("Excluir", self)
        
        # Adiciona as ações ao menu
        context_menu.addAction(add_action)
        context_menu.addAction(rename_action)
        context_menu.addAction(delete_action)
        
        # Desativa a exclusão para a pasta 'Geral'
        if folder[1] == "Geral" and folder[2] is None:
            delete_action.setEnabled(False)
        
        # Conecta as ações aos métodos correspondentes
        add_action.triggered.connect(lambda: self._add_subfolder(folder_id))
        rename_action.triggered.connect(lambda: self._rename_folder(folder_id))
        delete_action.triggered.connect(lambda: self._delete_folder(folder_id))
        
        # Exibe o menu na posição do cursor
        context_menu.exec(self.folder_tree.mapToGlobal(position))
    
    def _add_folder(self):
        """
        Adiciona uma nova pasta de nível raiz.
        """
        name, ok = QInputDialog.getText(self, "Nova Pasta", "Nome da pasta:")
        if ok and name:
            folder_id = self.db.create_folder(name)
            if folder_id:
                self._load_folders()
                self.folder_created.emit(folder_id)
    
    def _add_subfolder(self, parent_id):
        """
        Adiciona uma subpasta a uma pasta existente.
        
        Args:
            parent_id (int): ID da pasta pai
        """
        name, ok = QInputDialog.getText(self, "Nova Subpasta", "Nome da subpasta:")
        if ok and name:
            folder_id = self.db.create_folder(name, parent_id)
            if folder_id:
                self._load_folders()
                self.folder_created.emit(folder_id)
    
    def _rename_folder(self, folder_id):
        """
        Renomeia uma pasta existente.
        
        Args:
            folder_id (int): ID da pasta a ser renomeada
        """
        folder = self.db.get_folder_by_id(folder_id)
        if not folder:
            return
            
        # Extrai o nome atual sem o contador de notas
        current_name = folder[1]
        
        name, ok = QInputDialog.getText(self, "Renomear Pasta", "Novo nome:", text=current_name)
        if ok and name and name != current_name:
            if self.db.rename_folder(folder_id, name):
                self._load_folders()
                self.folder_renamed.emit(folder_id)
    
    def _delete_folder(self, folder_id):
        """
        Exclui uma pasta existente após confirmação.
        
        Args:
            folder_id (int): ID da pasta a ser excluída
        """
        folder = self.db.get_folder_by_id(folder_id)
        if not folder:
            return
            
        # Não permite excluir a pasta 'Geral'
        if folder[1] == "Geral" and folder[2] is None:
            QMessageBox.warning(self, "Operação não permitida", "A pasta 'Geral' não pode ser excluída.")
            return
            
        # Pede confirmação
        reply = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir a pasta '{folder[1]}'?\n\nTodas as notas serão movidas para a pasta 'Geral'.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_folder(folder_id):
                self._load_folders()
                self.folder_deleted.emit(folder_id)
    
    def _on_item_changed(self, item, column):
        """
        Manipula alterações nos itens da árvore, como arrastar e soltar pastas.
        
        Args:
            item (QTreeWidgetItem): Item que foi alterado
            column (int): Coluna que foi alterada
        """
        try:
            # Este método é chamado quando um item é movido via drag-and-drop
            folder_id = item.data(0, Qt.ItemDataRole.UserRole)
            if not folder_id:
                return
                
            # Verifica se é a pasta Geral (que não pode ser movida)
            folder = self.db.get_folder_by_id(folder_id)
            if folder and folder[1] == "Geral" and folder[2] is None:
                # Recarrega a árvore para reverter a operação
                self._load_folders()
                QMessageBox.warning(self, "Operação não permitida", "A pasta 'Geral' não pode ser movida.")
                return
            
            # Determina o novo pai
            parent_item = item.parent()
            if parent_item:
                new_parent_id = parent_item.data(0, Qt.ItemDataRole.UserRole)
            else:
                new_parent_id = None
            
            # Guarda o ID da pasta atual antes de recarregar
            previous_folder_id = self.current_folder_id
            
            # Move a pasta no banco de dados
            if self.db.move_folder(folder_id, new_parent_id):
                self._load_folders()
                
                # Restaura a seleção da pasta
                if previous_folder_id in self.folder_items:
                    self.folder_tree.setCurrentItem(self.folder_items[previous_folder_id])
                
                self.folder_moved.emit(folder_id, new_parent_id)
        except Exception as e:
            print(f"Erro ao mover pasta: {e}")
            self._load_folders()  # Recarrega para garantir consistência
    
    def handle_note_drop(self, note_id, folder_id):
        """
        Manipula o drop de uma nota em uma pasta.
        
        Args:
            note_id (int): ID da nota que foi arrastada
            folder_id (int): ID da pasta de destino
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            if self.db.move_note(note_id, folder_id):
                # Guarda o ID da pasta atual antes de recarregar
                previous_folder_id = self.current_folder_id
                
                # Atualiza os contadores de notas
                self._load_folders()
                
                # Restaura a seleção da pasta
                if previous_folder_id in self.folder_items:
                    self.folder_tree.setCurrentItem(self.folder_items[previous_folder_id])
                
                # Emite o sinal de que a nota foi movida
                self.note_moved.emit(note_id, folder_id)
                return True
            return False
        except Exception as e:
            print(f"Erro ao mover nota: {e}")
            return False
    
    def get_current_folder_id(self):
        """
        Retorna o ID da pasta atualmente selecionada.
        
        Returns:
            int: ID da pasta ou None se nenhuma pasta estiver selecionada
        """
        return self.current_folder_id
    
    def refresh(self):
        """
        Atualiza a árvore de pastas.
        """
        # Guarda o ID da pasta atual antes de recarregar
        previous_folder_id = self.current_folder_id
        
        # Recarrega as pastas
        self._load_folders()
        
        # Tenta restaurar a seleção anterior
        if previous_folder_id and previous_folder_id in self.folder_items:
            self.folder_tree.setCurrentItem(self.folder_items[previous_folder_id])
        # Se a pasta anterior não existir mais, seleciona a pasta Geral ou a primeira disponível
        elif self.folder_tree.topLevelItemCount() > 0:
            # Procura pela pasta Geral
            general_folder_found = False
            for i in range(self.folder_tree.topLevelItemCount()):
                item = self.folder_tree.topLevelItem(i)
                if item and item.text(0).startswith("Geral"):
                    self.folder_tree.setCurrentItem(item)
                    general_folder_found = True
                    break
            
            # Se não encontrou a pasta Geral, seleciona o primeiro item
            if not general_folder_found:
                self.folder_tree.setCurrentItem(self.folder_tree.topLevelItem(0))