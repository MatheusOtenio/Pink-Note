# PinkNote - Aplicativo de Notas e Calendário

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellowgreen)

## 📋 Descrição

PinkNote é um aplicativo de desktop desenvolvido em Python com o objetivo de centralizar a vida acadêmica de um estudante. Ele oferece uma interface intuitiva para a gestão de anotações e um calendário para o acompanhamento de datas e eventos importantes. O projeto foi construído com uma arquitetura em camadas (Clean Architecture) e um design de interface moderno, focado na usabilidade.

## 🏗️ Arquitetura

O projeto segue os princípios de Clean Architecture, com separação clara entre as camadas:

- **Domain**: Contém as entidades de negócio e interfaces de repositório
- **Application**: Implementa os casos de uso da aplicação
- **Infrastructure**: Fornece implementações concretas para persistência e serviços externos
- **Presentation**: Gerencia a interface do usuário e interações
- **Shared**: Contém recursos compartilhados entre as camadas

### Estrutura de Diretórios

```
pinknote/
├── domain/                 # Camada de domínio (regras de negócio)
│   ├── entities/           # Entidades de domínio
│   ├── repositories/       # Interfaces de repositórios
│   └── value_objects/      # Objetos de valor
├── application/            # Camada de aplicação (casos de uso)
│   ├── interfaces/         # Interfaces de serviços
│   └── use_cases/          # Implementação dos casos de uso
├── infrastructure/         # Camada de infraestrutura
│   ├── database/           # Implementação de repositórios com SQLite
│   └── storage/            # Gerenciamento de armazenamento de arquivos
├── presentation/           # Camada de apresentação
│   ├── components/         # Componentes de UI reutilizáveis
│   ├── controllers/        # Controladores para a camada de apresentação
│   └── main_window.py      # Janela principal da aplicação
└── shared/                 # Recursos compartilhados
    ├── config/             # Configurações da aplicação
    ├── constants/          # Constantes da aplicação
    ├── di/                 # Injeção de dependência
    └── utils/              # Utilitários
```

### Padrões de Projeto Utilizados

- **Repository**: Para abstração da camada de persistência
- **Dependency Injection**: Para gerenciar dependências entre componentes
- **Service**: Para encapsular lógica de negócio
- **Observer**: Para comunicação entre componentes da UI

## ✨ Funcionalidades

### Gestão Completa de Notas

* 📝 **Criar**: Adicione novas anotações com título e conteúdo
* 👀 **Ler**: Visualize o conteúdo de qualquer nota selecionada
* ✏️ **Editar**: Edite notas existentes diretamente na tela principal
* 🗑️ **Deletar**: Remova anotações com uma caixa de diálogo de confirmação
* 📎 **Anexos**: Adicione, visualize e gerencie arquivos anexados às suas notas
* 📁 **Sistema de Pastas**: Organize suas notas em uma estrutura hierárquica de pastas e subpastas
* 🔍 **Pesquisa**: Encontre notas rapidamente através de pesquisa por conteúdo

### Calendário de Eventos

* 📅 **Visualização**: Navegue por um calendário completo
* ✨ **Marcação de Datas**: Dias com eventos são automaticamente destacados
* ➕ **Adicionar Eventos**: Adicione eventos a qualquer data
* 🗑️ **Deletar Eventos**: Selecione e delete eventos específicos

### Interface e UX

* 🎨 **Tema Customizado**: Interface com tema escuro e detalhes em rosa
* 🖥️ **Edição Integrada**: O modo de edição de notas acontece na mesma janela
* 👆 **Controles Contextuais**: Botões aparecem de forma inteligente quando necessários
* 🌳 **Navegação em Árvore**: Visualize e navegue pela estrutura de pastas em uma árvore interativa
* 🧭 **Breadcrumb Navigation**: Acompanhe e navegue facilmente pelo caminho da pasta atual
* 🖱️ **Drag-and-Drop**: Mova notas e pastas facilmente arrastando e soltando

## 🛠️ Tecnologias Utilizadas

* **Linguagem**: Python 3.6+
* **Framework GUI**: PyQt5
* **Banco de Dados**: SQLite3 (para armazenamento local e persistente)
* **Controle de Versão**: Git & GitHub

## 🚀 Como Executar o Projeto

### Pré-requisitos

* Python 3.6 ou superior
* Git

### Instalação e Execução

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/pinknote.git
   cd pinknote
   ```

2. **Crie e ative um ambiente virtual**:
   ```bash
   # No Windows
   python -m venv venv
   venv\Scripts\activate
   
   # No Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**:
   ```bash
   python main.py
   ```

## 🧪 Testes

Para executar os testes automatizados:

```bash
python -m unittest discover tests
```

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Contribuição

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Adicione suas mudanças (`git add .`)
4. Comite suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Faça o Push da Branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

## 📞 Contato

Seu Nome - [seu-email@exemplo.com](mailto:seu-email@exemplo.com)

Link do Projeto: [https://github.com/seu-usuario/pinknote](https://github.com/seu-usuario/pinknote)
