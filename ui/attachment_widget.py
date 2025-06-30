# ui/attachment_widget.py
import os
import uuid
import shutil
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QFileDialog, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QIcon, QPixmap

class AttachmentWidget(QWidget):
    """Widget para gerenciar anexos PDF em notas.
    
    Este widget permite adicionar, visualizar e remover anexos PDF associados a uma nota.
    Ele emite sinais quando anexos são adicionados ou removidos para notificar componentes pai.
    
    Signals:
        attachment_added: Emitido quando um novo anexo é adicionado
        attachment_removed: Emitido quando um anexo é removido
    """
    
    attachment_added = Signal()
    attachment_removed = Signal()
    
    def __init__(self, db_manager, note_id=None, read_only=False):
        """Inicializa o widget de anexos.
        
        Args:
            db_manager: Instância do DatabaseManager para operações de banco de dados
            note_id (int, optional): ID da nota associada aos anexos. Defaults to None.
            read_only (bool, optional): Se True, o widget estará em modo somente leitura. Defaults to False.
        """
        super().__init__()
        
        self.db = db_manager
        self.note_id = note_id
        self.read_only = read_only
        self.attachments_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "attachments")
        
        # Garante que o diretório de anexos exista
        if not os.path.exists(self.attachments_dir):
            os.makedirs(self.attachments_dir)
        
        self._setup_ui()
        
        if self.note_id is not None:
            self._load_attachments()
    
    def _setup_ui(self):
        """Configura a interface do usuário do widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título da seção
        title_label = QLabel("Anexos PDF")
        title_label.setObjectName("attachmentTitle")
        main_layout.addWidget(title_label)
        
        # Lista de anexos
        self.attachments_list = QListWidget()
        self.attachments_list.setMinimumHeight(100)
        self.attachments_list.setMaximumHeight(150)
        self.attachments_list.itemSelectionChanged.connect(self._update_button_states)
        main_layout.addWidget(self.attachments_list)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Adicionar PDF")
        self.add_button.clicked.connect(self._add_attachment)
        self.add_button.setVisible(not self.read_only)
        buttons_layout.addWidget(self.add_button)
        
        buttons_layout.addStretch()
        
        self.open_button = QPushButton("Abrir")
        self.open_button.clicked.connect(self._open_attachment)
        self.open_button.setEnabled(False)
        buttons_layout.addWidget(self.open_button)
        
        self.remove_button = QPushButton("Remover")
        self.remove_button.clicked.connect(self._remove_attachment)
        self.remove_button.setEnabled(False)
        self.remove_button.setVisible(not self.read_only)
        buttons_layout.addWidget(self.remove_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _update_button_states(self):
        """Atualiza o estado dos botões com base na seleção atual."""
        has_selection = len(self.attachments_list.selectedItems()) > 0
        self.open_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection and not self.read_only)
    
    def _load_attachments(self):
        """Carrega os anexos da nota atual."""
        self.attachments_list.clear()
        
        if self.note_id is None:
            return
        
        attachments = self.db.get_attachments_for_note(self.note_id)
        
        for attachment in attachments:
            attachment_id, filename, original_filename, file_path, file_size, created_at = attachment
            
            # Formata o tamanho do arquivo
            size_str = self._format_file_size(file_size) if file_size else "Desconhecido"
            
            # Cria o item da lista
            item = QListWidgetItem(f"{original_filename} ({size_str})")
            item.setData(Qt.ItemDataRole.UserRole, attachment_id)
            self.attachments_list.addItem(item)
    
    def _format_file_size(self, size_bytes):
        """Formata o tamanho do arquivo em uma string legível.
        
        Args:
            size_bytes (int): Tamanho em bytes
            
        Returns:
            str: Tamanho formatado (ex: "2.5 MB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _add_attachment(self):
        """Abre um diálogo para selecionar e adicionar um arquivo PDF."""
        if self.note_id is None:
            QMessageBox.warning(self, "Erro", "Salve a nota antes de adicionar anexos.")
            return
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Arquivos PDF (*.pdf)")
        file_dialog.setWindowTitle("Selecionar Arquivo PDF")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if not selected_files:
                return
                
            source_path = selected_files[0]
            
            # Verifica se é um arquivo PDF
            if not source_path.lower().endswith('.pdf'):
                QMessageBox.warning(self, "Tipo de Arquivo Inválido", 
                                  "Apenas arquivos PDF são permitidos.")
                return
            
            try:
                # Obtém informações do arquivo
                file_size = os.path.getsize(source_path)
                original_filename = os.path.basename(source_path)
                
                # Gera um nome de arquivo único para evitar conflitos
                unique_filename = f"{uuid.uuid4().hex}.pdf"
                destination_path = os.path.join(self.attachments_dir, unique_filename)
                
                # Copia o arquivo para o diretório de anexos
                shutil.copy2(source_path, destination_path)
                
                # Adiciona o anexo ao banco de dados
                attachment_id = self.db.add_attachment(
                    self.note_id, 
                    unique_filename, 
                    original_filename, 
                    destination_path, 
                    file_size
                )
                
                if attachment_id:
                    # Atualiza a lista de anexos
                    self._load_attachments()
                    self.attachment_added.emit()
                else:
                    # Se falhou ao adicionar ao banco, remove o arquivo copiado
                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                    QMessageBox.warning(self, "Erro", "Falha ao adicionar o anexo.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao adicionar anexo: {str(e)}")
    
    def _open_attachment(self):
        """Abre o anexo selecionado com o aplicativo padrão do sistema."""
        selected_items = self.attachments_list.selectedItems()
        if not selected_items:
            return
            
        attachment_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        file_path = self.db.get_attachment_path(attachment_id)
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Arquivo Não Encontrado", 
                              "O arquivo não foi encontrado no sistema.")
            return
        
        # Abre o arquivo com o aplicativo padrão do sistema
        import subprocess
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS e Linux
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Abrir Arquivo", 
                               f"Não foi possível abrir o arquivo: {str(e)}")
    
    def _remove_attachment(self):
        """Remove o anexo selecionado após confirmação do usuário."""
        if self.read_only:
            return
            
        selected_items = self.attachments_list.selectedItems()
        if not selected_items:
            return
            
        attachment_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Pede confirmação antes de remover
        reply = QMessageBox.question(
            self, 
            "Confirmar Remoção", 
            "Tem certeza que deseja remover este anexo? Esta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_attachment(attachment_id):
                self._load_attachments()
                self.attachment_removed.emit()
            else:
                QMessageBox.warning(self, "Erro", "Falha ao remover o anexo.")
    
    def set_note_id(self, note_id):
        """Define o ID da nota associada e recarrega os anexos.
        
        Args:
            note_id (int): ID da nota
        """
        self.note_id = note_id
        self._load_attachments()
    
    def set_read_only(self, read_only):
        """Define o modo somente leitura do widget.
        
        Args:
            read_only (bool): Se True, o widget estará em modo somente leitura
        """
        self.read_only = read_only
        self.add_button.setVisible(not read_only)
        self.remove_button.setVisible(not read_only)
        self._update_button_states()