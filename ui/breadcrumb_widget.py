# ui/breadcrumb_widget.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QIcon

class BreadcrumbWidget(QWidget):
    """
    Widget para exibir navegação em breadcrumb para pastas.
    
    Este widget mostra o caminho completo da pasta atual e permite
    navegar para pastas superiores clicando nos elementos do caminho.
    
    Signals:
        folder_selected: Emitido quando um elemento do caminho é clicado (folder_id)
    """
    
    folder_selected = Signal(int)  # folder_id
    
    def __init__(self, db_manager):
        """
        Inicializa o widget de breadcrumb.
        
        Args:
            db_manager: Instância do DatabaseManager para operações de banco de dados
        """
        super().__init__()
        
        self.db = db_manager
        self.current_folder_id = None
        self.breadcrumb_buttons = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """
        Configura a interface do usuário do widget.
        """
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        
        # Ícone inicial (casa)
        self.home_button = QPushButton("Início")
        self.home_button.setObjectName("homeButton")
        self.home_button.setFlat(True)
        self.home_button.clicked.connect(self._on_home_clicked)
        self.layout.addWidget(self.home_button)
        
        # Espaço para os elementos do caminho
        self.layout.addStretch()
    
    def set_folder(self, folder_id):
        """
        Define a pasta atual e atualiza o breadcrumb.
        
        Args:
            folder_id (int): ID da pasta
        """
        self.current_folder_id = folder_id
        self._update_breadcrumb()
    
    def _update_breadcrumb(self):
        """
        Atualiza os elementos do breadcrumb com base na pasta atual.
        """
        # Limpa os botões existentes
        for button in self.breadcrumb_buttons:
            self.layout.removeWidget(button)
            button.deleteLater()
        self.breadcrumb_buttons = []
        
        if self.current_folder_id is None:
            return
        
        # Obtém o caminho completo da pasta atual
        folder_path = []
        current_id = self.current_folder_id
        
        while current_id is not None:
            folder = self.db.get_folder_by_id(current_id)
            if folder:
                folder_path.insert(0, (current_id, folder[1]))  # (id, name)
                current_id = folder[2]  # parent_id
            else:
                break
        
        # Adiciona separadores e botões para cada elemento do caminho
        for i, (folder_id, folder_name) in enumerate(folder_path):
            if i > 0:
                separator = QLabel(">")
                separator.setObjectName("breadcrumbSeparator")
                self.layout.insertWidget(self.layout.count() - 1, separator)
                self.breadcrumb_buttons.append(separator)
            
            button = QPushButton(folder_name)
            button.setObjectName("breadcrumbButton")
            button.setFlat(True)
            button.setProperty("folder_id", folder_id)
            button.clicked.connect(lambda checked, fid=folder_id: self._on_breadcrumb_clicked(fid))
            
            # O último elemento (pasta atual) tem estilo diferente
            if i == len(folder_path) - 1:
                button.setObjectName("currentBreadcrumbButton")
            
            self.layout.insertWidget(self.layout.count() - 1, button)
            self.breadcrumb_buttons.append(button)
    
    def _on_home_clicked(self):
        """
        Manipula o clique no botão inicial (casa).
        """
        # Busca a pasta 'Geral'
        self.db.cursor.execute(
            "SELECT id FROM folders WHERE name = 'Geral' AND parent_id IS NULL"
        )
        result = self.db.cursor.fetchone()
        if result:
            general_folder_id = result[0]
            self.folder_selected.emit(general_folder_id)
    
    def _on_breadcrumb_clicked(self, folder_id):
        """
        Manipula o clique em um elemento do caminho.
        
        Args:
            folder_id (int): ID da pasta clicada
        """
        self.folder_selected.emit(folder_id)