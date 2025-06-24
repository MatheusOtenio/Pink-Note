# main.py (Versão Completa com Deleção de Eventos - 23 de Junho de 2025)

import sys
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QTextCharFormat, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QPushButton, QVBoxLayout, QListWidget, QTextEdit,
    QListWidgetItem, QHBoxLayout, QMessageBox,
    QStackedWidget, QLineEdit, QCalendarWidget, QLabel, QInputDialog
)
from core.database_manager import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.db = DatabaseManager()
        self.id_nota_em_edicao = None

        if not self.db.get_all_notes() and not self.db.get_all_event_dates():
            self.db.add_note("Bem-vindo ao PinkNote!", "Clique duplo nesta nota para editá-la.")
            self.db.add_event(QDate.currentDate().addDays(1).toString("yyyy-MM-dd"), "Entregar projeto!")

        self.setWindowTitle("PinkNote Desktop")
        self.resize(800, 600)
        self.setMinimumSize(700, 500)

        # --- Estrutura Principal ---
        container_principal = QWidget()
        self.setCentralWidget(container_principal)
        layout_principal = QVBoxLayout(container_principal)

        self.abas = QTabWidget()
        
        # --- Aba "Notas" ---
        widget_da_aba_notas = QWidget()
        layout_aba_notas = QHBoxLayout(widget_da_aba_notas)
        self.lista_de_notas = QListWidget()
        layout_aba_notas.addWidget(self.lista_de_notas, 1)
        self.stacked_widget = QStackedWidget()
        layout_aba_notas.addWidget(self.stacked_widget, 2)
        self._criar_paginas_stacked_widget()
        self.abas.addTab(widget_da_aba_notas, "Notas")
        
        # --- Aba "Calendário" ---
        widget_da_aba_calendario = QWidget()
        layout_aba_calendario = QVBoxLayout(widget_da_aba_calendario)
        self.calendario = QCalendarWidget()
        self.calendario.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        layout_aba_calendario.addWidget(self.calendario)
        layout_aba_calendario.addWidget(QLabel("Eventos para a data selecionada:"))
        self.lista_de_eventos = QListWidget()
        self.lista_de_eventos.setMaximumHeight(150)
        layout_aba_calendario.addWidget(self.lista_de_eventos)
        
        botoes_calendario_layout = QHBoxLayout()
        botoes_calendario_layout.addStretch()
        self.botao_delete_evento = QPushButton("Deletar Evento")
        self.botao_delete_evento.setVisible(False)
        botoes_calendario_layout.addWidget(self.botao_delete_evento)
        self.botao_add_evento = QPushButton("Adicionar Evento")
        botoes_calendario_layout.addWidget(self.botao_add_evento)
        layout_aba_calendario.addLayout(botoes_calendario_layout)
        
        self.abas.addTab(widget_da_aba_calendario, "Calendário")

        layout_principal.addWidget(self.abas)
        
        # --- Botões de Ação Globais (para Notas) ---
        layout_botoes_acao = QHBoxLayout()
        layout_botoes_acao.addStretch()
        self.botao_delete = QPushButton("Deletar Nota")
        self.botao_delete.setVisible(False)
        layout_botoes_acao.addWidget(self.botao_delete)
        self.botao_add = QPushButton("+")
        self.botao_add.setObjectName("addButton")
        layout_botoes_acao.addWidget(self.botao_add)
        layout_principal.addLayout(layout_botoes_acao)

        # --- Conexões de Sinais ---
        self.lista_de_notas.currentItemChanged.connect(self.display_note_content)
        self.lista_de_notas.itemDoubleClicked.connect(self.entrar_modo_edicao)
        self.botao_add.clicked.connect(self.entrar_modo_criacao)
        self.botao_delete.clicked.connect(self.deletar_nota_selecionada)
        self.botao_salvar.clicked.connect(self.salvar_nota)
        self.botao_cancelar.clicked.connect(self.sair_modo_edicao)
        
        self.calendario.selectionChanged.connect(self.atualizar_lista_de_eventos)
        self.lista_de_eventos.currentItemChanged.connect(self.atualizar_estado_botao_delete_evento)
        self.botao_add_evento.clicked.connect(self.adicionar_novo_evento)
        self.botao_delete_evento.clicked.connect(self.deletar_evento_selecionado)
        
        # --- Carregamento Inicial ---
        self.carregar_notas()
        self.stacked_widget.setCurrentIndex(0)
        self.destacar_datas_com_eventos()
        self.atualizar_lista_de_eventos()

    def _criar_paginas_stacked_widget(self):
        pagina_visualizacao = QWidget()
        layout_visualizacao = QVBoxLayout(pagina_visualizacao)
        self.conteudo_viewer = QTextEdit()
        self.conteudo_viewer.setReadOnly(True)
        layout_visualizacao.addWidget(self.conteudo_viewer)
        
        pagina_edicao = QWidget()
        layout_edicao = QVBoxLayout(pagina_edicao)
        self.editor_titulo = QLineEdit()
        self.editor_titulo.setPlaceholderText("Título...")
        self.editor_conteudo = QTextEdit()
        layout_edicao.addWidget(self.editor_titulo)
        layout_edicao.addWidget(self.editor_conteudo)
        
        botoes_edicao_layout = QHBoxLayout()
        self.botao_salvar = QPushButton("Salvar")
        self.botao_cancelar = QPushButton("Cancelar")
        botoes_edicao_layout.addStretch()
        botoes_edicao_layout.addWidget(self.botao_cancelar)
        botoes_edicao_layout.addWidget(self.botao_salvar)
        layout_edicao.addLayout(botoes_edicao_layout)
        
        self.stacked_widget.addWidget(pagina_visualizacao)
        self.stacked_widget.addWidget(pagina_edicao)

    # --- MÉTODOS DE NOTAS ---
    def carregar_notas(self):
        self.lista_de_notas.clear()
        self.conteudo_viewer.clear()
        self.botao_delete.setVisible(False)
        notas = self.db.get_all_notes()
        for nota in notas:
            id_nota, titulo, conteudo = nota
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, id_nota)
            self.lista_de_notas.addItem(item)
    
    def display_note_content(self, current_item, previous_item=None):
        if self.stacked_widget.currentIndex() == 1:
            return
            
        item_para_exibir = current_item if current_item else self.lista_de_notas.currentItem()
        if item_para_exibir:
            self.botao_delete.setVisible(True)
            id_nota = item_para_exibir.data(Qt.ItemDataRole.UserRole)
            nota = self.db.get_note_by_id(id_nota)
            if nota:
                titulo, conteudo = nota[1], nota[2]
                conteudo_html = conteudo.replace('\n', '<br>') if conteudo else ""
                self.conteudo_viewer.setHtml(f"<h2>{titulo}</h2>{conteudo_html}")
        else:
            self.botao_delete.setVisible(False)
            self.conteudo_viewer.clear()

    def entrar_modo_criacao(self):
        self.id_nota_em_edicao = None
        self.stacked_widget.setCurrentIndex(1)
        self.editor_titulo.clear()
        self.editor_conteudo.clear()
        self.editor_titulo.setFocus()

    def entrar_modo_edicao(self, item):
        id_nota = item.data(Qt.ItemDataRole.UserRole)
        nota = self.db.get_note_by_id(id_nota)
        if nota:
            self.id_nota_em_edicao = id_nota
            self.stacked_widget.setCurrentIndex(1)
            self.editor_titulo.setText(nota[1])
            self.editor_conteudo.setText(nota[2])

    def sair_modo_edicao(self):
        self.stacked_widget.setCurrentIndex(0)
        self.display_note_content(self.lista_de_notas.currentItem())

    def salvar_nota(self):
        titulo = self.editor_titulo.text()
        conteudo = self.editor_conteudo.toPlainText()
        if not titulo:
            return

        if self.id_nota_em_edicao is None:
            self.db.add_note(titulo, conteudo)
        else:
            self.db.update_note(self.id_nota_em_edicao, titulo, conteudo)
        
        self.carregar_notas()
        self.sair_modo_edicao()
    
    def deletar_nota_selecionada(self):
        item_selecionado = self.lista_de_notas.currentItem()
        if item_selecionado is None:
            return
        
        titulo_nota = item_selecionado.text()
        caixa_confirmacao = QMessageBox()
        caixa_confirmacao.setText(f'Tem certeza que deseja deletar a nota "{titulo_nota}"?')
        caixa_confirmacao.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        caixa_confirmacao.setIcon(QMessageBox.Icon.Warning)
        caixa_confirmacao.setDefaultButton(QMessageBox.StandardButton.No)
        
        if caixa_confirmacao.exec() == QMessageBox.StandardButton.Yes:
            id_da_nota = item_selecionado.data(Qt.ItemDataRole.UserRole)
            self.db.delete_note(id_da_nota)
            self.carregar_notas()

    # --- MÉTODOS DO CALENDÁRIO ---
    def destacar_datas_com_eventos(self):
        datas_com_eventos = self.db.get_all_event_dates()
        formato_vazio = QTextCharFormat()
        
        # Limpa formatação antiga para o mês atual
        ano, mes = self.calendario.yearShown(), self.calendario.monthShown()
        for dia in range(1, 32):
            self.calendario.setDateTextFormat(QDate(ano, mes, dia), formato_vazio)
            
        formato_destaque = QTextCharFormat()
        formato_destaque.setFontWeight(QFont.Weight.Bold)
        formato_destaque.setForeground(QColor("pink"))
        
        for data_str in datas_com_eventos:
            data = QDate.fromString(data_str, "yyyy-MM-dd")
            self.calendario.setDateTextFormat(data, formato_destaque)

    def atualizar_lista_de_eventos(self):
        self.lista_de_eventos.clear()
        self.botao_delete_evento.setVisible(False)
        data_selecionada = self.calendario.selectedDate().toString("yyyy-MM-dd")
        eventos = self.db.get_events_for_date(data_selecionada)
        for evento_id, evento_titulo in eventos:
            item = QListWidgetItem(evento_titulo)
            item.setData(Qt.ItemDataRole.UserRole, evento_id)
            self.lista_de_eventos.addItem(item)
    
    def atualizar_estado_botao_delete_evento(self, current_item, previous_item=None):
        self.botao_delete_evento.setVisible(current_item is not None)

    def adicionar_novo_evento(self):
        data_selecionada = self.calendario.selectedDate()
        texto_evento, ok = QInputDialog.getText(self, "Novo Evento", f"Adicionar evento para {data_selecionada.toString('dd/MM/yyyy')}:")
        
        if ok and texto_evento:
            data_str = data_selecionada.toString("yyyy-MM-dd")
            self.db.add_event(data_str, texto_evento)
            self.atualizar_lista_de_eventos()
            self.destacar_datas_com_eventos()

    def deletar_evento_selecionado(self):
        item_selecionado = self.lista_de_eventos.currentItem()
        if item_selecionado is None:
            return
        
        titulo_evento = item_selecionado.text()
        caixa_confirmacao = QMessageBox()
        caixa_confirmacao.setText(f'Tem certeza que deseja deletar o evento "{titulo_evento}"?')
        caixa_confirmacao.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        caixa_confirmacao.setIcon(QMessageBox.Icon.Warning)
        caixa_confirmacao.setDefaultButton(QMessageBox.StandardButton.No)
        
        if caixa_confirmacao.exec() == QMessageBox.StandardButton.Yes:
            id_do_evento = item_selecionado.data(Qt.ItemDataRole.UserRole)
            self.db.delete_event(id_do_evento)
            self.atualizar_lista_de_eventos()
            self.destacar_datas_com_eventos()

    # --- MÉTODO DE FECHAMENTO ---
    def closeEvent(self, event):
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        with open("assets/style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Arquivo de estilo 'assets/style.qss' não encontrado.")
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec())