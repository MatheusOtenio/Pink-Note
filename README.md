#  caderno-digital
> Um caderno digital para anotações e gerenciamento de eventos, desenvolvido como um projeto de Engenharia de Software.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellowgreen)


### 📸 Visão Geral do Projeto

[Insira um screenshot da aplicação aqui]

O PinkNote é uma aplicação de desktop desenvolvida em Python com o objetivo de centralizar a vida acadêmica de um estudante. Ele oferece uma interface intuitiva para a gestão de anotações e um calendário para o acompanhamento de datas e eventos importantes. O projeto foi construído com uma arquitetura em camadas e um design de interface moderno, focado na usabilidade.

---

### ✨ Funcionalidades Implementadas

* **Gestão Completa de Notas:**
    * 📝 **Criar:** Adicione novas anotações com título e conteúdo.
    * 👀 **Ler:** Visualize o conteúdo de qualquer nota selecionada.
    * ✏️ **Editar:** Edite notas existentes diretamente na tela principal, sem a necessidade de pop-ups.
    * 🗑️ **Deletar:** Remova anotações com uma caixa de diálogo de confirmação para evitar acidentes.

* **Calendário de Eventos:**
    * 📅 **Visualização:** Navegue por um calendário completo.
    * ✨ **Marcação de Datas:** Dias com eventos são automaticamente destacados em rosa e negrito.
    * ➕ **Adicionar Eventos:** Adicione eventos a qualquer data através de uma simples caixa de diálogo.
    * 🗑️ **Deletar Eventos:** Selecione e delete eventos específicos de uma data.

* **Interface e UX:**
    * 🎨 **Tema Customizado:** Interface com tema escuro e detalhes em rosa, inspirada no protótipo inicial.
    * 🖥️ **Edição Integrada:** O modo de edição de notas acontece na mesma janela, proporcionando um fluxo de trabalho mais rápido e moderno.
    * 👆 **Controles Contextuais:** Botões como "Deletar Nota" e "Deletar Evento" aparecem de forma inteligente apenas quando um item é selecionado.

---

### 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Framework GUI:** PySide6 (Qt for Python)
* **Banco de Dados:** SQLite3 (para armazenamento local e persistente)
* **Controle de Versão:** Git & GitHub

---

### 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e executar o projeto em um ambiente Linux (Debian/Ubuntu).

**Pré-requisitos:**
* Python 3
* Git

**Instalação e Execução:**

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd caderno-digital
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install pyside6
    ```

5.  **Execute a aplicação:**
    ```bash
    python3 main.py
    ```

---

### 📂 Estrutura de Pastas

O projeto está organizado da seguinte forma para manter a separação de responsabilidades:

```
caderno-digital/
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git
├── README.md           # Documentação do projeto
├── main.py             # Ponto de entrada e lógica principal da interface
├── core/
│   └── database_manager.py # Camada de acesso a dados (gerencia o SQLite)
└── assets/
    └── style.qss       # Folha de estilos da aplicação
```

---
