# ui/note_editor.py (Versão para Adicionar e Editar)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QHBoxLayout
)

class NoteEditorWindow(QDialog):
    def __init__(self, db_manager, note_id=None):
        super().__init__()

        self.db = db_manager
        self.note_id = note_id # Armazena o ID da nota (será None se for uma nota nova)

        # --- Layout e Widgets (continua igual) ---
        layout = QVBoxLayout(self)
        self.titulo_input = QLineEdit()
        self.conteudo_input = QTextEdit()
        botoes_layout = QHBoxLayout()
        self.botao_cancelar = QPushButton("Cancelar")
        self.botao_salvar = QPushButton("Salvar")

        botoes_layout.addWidget(self.botao_cancelar)
        botoes_layout.addWidget(self.botao_salvar)
        layout.addWidget(self.titulo_input)
        layout.addWidget(self.conteudo_input)
        layout.addLayout(botoes_layout)

        # --- Lógica de Edição vs. Criação ---
        if self.note_id is None:
            # MODO DE CRIAÇÃO (novo)
            self.setWindowTitle("Nova Anotação")
            self.titulo_input.setPlaceholderText("Título da anotação...")
            self.conteudo_input.setPlaceholderText("Digite suas anotações aqui...")
        else:
            # MODO DE EDIÇÃO
            self.setWindowTitle("Editar Anotação")
            self._carregar_dados_da_nota()

        # --- Conectar Sinais ---
        self.botao_salvar.clicked.connect(self.salvar_nota)
        self.botao_cancelar.clicked.connect(self.reject)

    def _carregar_dados_da_nota(self):
        """Busca os dados da nota no banco e preenche os campos."""
        nota = self.db.get_note_by_id(self.note_id)
        if nota:
            # nota é uma tupla: (id, titulo, conteudo, ...)
            self.titulo_input.setText(nota[1])
            self.conteudo_input.setText(nota[2])

    def salvar_nota(self):
        """Salva a nota, seja atualizando uma existente ou criando uma nova."""
        titulo = self.titulo_input.text()
        conteudo = self.conteudo_input.toPlainText()

        if titulo:
            if self.note_id is None:
                # Se não tem ID, é uma nota nova
                self.db.add_note(titulo, conteudo)
            else:
                # Se tem ID, é uma atualização
                self.db.update_note(self.note_id, titulo, conteudo)

            self.accept() # Fecha a janela com sucesso
        else:
            print("O título não pode estar vazio!")