# GWorkspace Toolbox - Terminal User Interface (TUI)

🖥️ **Uma interface de terminal moderna e elegante para o GWorkspace Toolbox**

A TUI oferece uma alternativa ao frontend web, perfeita para:
- Ambientes de servidor sem GUI
- Sessões SSH remotas
- Power users que preferem terminal
- Automação e scripting

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.9+
- Backend rodando em `http://localhost:8000`
- Dependências instaladas (instaladas automaticamente com `pip install -r backend/requirements.txt`)

### Executar a TUI

```bash
# Método 1: Usar o script launcher (recomendado)
./start-tui.sh

# Método 2: Executar diretamente
cd backend && source venv/bin/activate && cd .. && python3 tui.py

# Método 3: Com URL customizada do backend
python3 tui.py --backend-url http://custom-backend:8000
```

## 📋 Funcionalidades

### 1. 🔐 Autenticação
- Upload de arquivo credentials.json
- Autenticação com Service Account
- Modo de teste (skip authentication)

### 2. 📧 Alias Extractor
- Extrair aliases de usuários do Google Workspace
- Visualizar aliases em tabela formatada
- Exportar para CSV

### 3. 🏷️ Attribute Injector
- Selecionar Organizational Unit (OU)
- Configurar atributos em formato JSON
- Injetar atributos em lote para usuários

### 4. 📊 Batch Jobs Monitor
- Visualizar jobs em andamento
- Monitorar progresso em tempo real
- Atualização manual com tecla `R`

## ⌨️ Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| `↑` `↓` `←` `→` | Navegar |
| `Tab` | Próximo elemento |
| `Enter` | Selecionar/Confirmar |
| `ESC` | Voltar |
| `Q` | Sair (na tela principal) |
| `R` | Atualizar (em listas) |
| `Ctrl+C` | Fechar aplicação |

## 🎨 Features da Interface

### Design Moderno com Textual
- ✨ Interface responsiva e bonita
- 🎨 Cores e temas consistentes
- 📊 Tabelas interativas com DataTable
- ⚡ Navegação rápida com teclado
- 🔄 Feedback visual em tempo real

### Componentes
- **Telas** (Screens): Diferentes seções da aplicação
- **Botões** (Buttons): Ações interativas
- **Tabelas** (DataTables): Visualização de dados
- **Inputs**: Campos de entrada de texto
- **TextArea**: Edição de JSON multi-linha
- **Labels**: Feedback de status

## 🏗️ Arquitetura

```
┌─────────────────────────────┐
│     TUI (Textual)           │
│     • WelcomeScreen         │
│     • AuthScreen            │
│     • MainMenuScreen        │
│     • Tool Screens          │
└──────────┬──────────────────┘
           │ HTTP API
           │ (httpx)
┌──────────▼──────────────────┐
│   Backend (FastAPI)         │
│   http://localhost:8000     │
└─────────────────────────────┘
```

### Fluxo de Navegação

```
WelcomeScreen (Verificação de conectividade)
    │
    ├─ Backend OK → AuthenticationScreen
    │                   │
    │                   └─ Upload JSON ou Service Account
    │                       │
    │                       └─ MainMenuScreen
    │                           ├─ AliasExtractorScreen
    │                           ├─ AttributeInjectorScreen
    │                           ├─ BatchMonitorScreen
    │                           └─ Settings (em breve)
    │
    └─ Backend Offline → Aviso + Opção de continuar
```

## 🔧 Configuração

### Variáveis de Ambiente

A TUI usa as mesmas variáveis do backend:

```bash
# Backend URL (padrão: http://localhost:8000)
BACKEND_URL=http://localhost:8000

# Timeout para requisições API (padrão: 30s)
API_TIMEOUT=30.0
```

### Personalização

Você pode personalizar a TUI editando o arquivo `tui.py`:

```python
# Mudar URL do backend
BACKEND_URL = "http://your-backend:8000"

# Ajustar timeout
API_TIMEOUT = 60.0

# Personalizar cores (via CSS do Textual)
CSS = """
    Screen {
        background: $surface-darken-1;
    }
"""
```

## 🐛 Troubleshooting

### Backend não conecta

```bash
# 1. Verificar se o backend está rodando
curl http://localhost:8000/

# 2. Iniciar o backend se necessário
./start-dev.sh

# 3. Verificar porta do backend
lsof -ti:8000
```

### Erro de dependências

```bash
# Reinstalar dependências
cd backend
source venv/bin/activate
pip install textual rich httpx

# Ou reinstalar tudo
pip install -r requirements.txt
```

### Terminal muito pequeno

A TUI requer pelo menos:
- **Largura mínima**: 70 colunas
- **Altura mínima**: 24 linhas

Ajuste o tamanho da janela do terminal se necessário.

### Caracteres estranhos

Se você vê caracteres estranhos em vez de bordas bonitas:
- Certifique-se de usar um terminal moderno (iTerm2, Windows Terminal, etc.)
- Verifique se o terminal suporta UTF-8

## 🆚 TUI vs Web Frontend

| Feature | TUI | Web |
|---------|-----|-----|
| Interface | Terminal | Browser |
| Instalação | Incluso no backend | Requer npm/node |
| Performance | Muito rápida | Rápida |
| Uso de recursos | Mínimo | Moderado |
| SSH remoto | ✅ Perfeito | ❌ Requer port forwarding |
| Scripting | ✅ Fácil | ❌ Difícil |
| Visual | Texto colorido | Gráfico completo |
| Acessibilidade | Screen readers nativos | Depende do browser |

## 🚧 Roadmap

Features planejadas para futuras versões:

- [ ] Tela de Settings com configurações avançadas
- [ ] Suporte a múltiplos backends
- [ ] Histórico de comandos
- [ ] Export de logs em tempo real
- [ ] Modo de scripting (non-interactive)
- [ ] Temas customizáveis
- [ ] Suporte a plugins
- [ ] Dashboard com métricas

## 📚 Documentação Técnica

### Bibliotecas Usadas

- **[Textual](https://textual.textualize.io/)**: Framework TUI moderno
- **[Rich](https://rich.readthedocs.io/)**: Terminal formatting
- **[httpx](https://www.python-httpx.org/)**: Cliente HTTP assíncrono

### Estrutura de Código

```
tui.py
├── APIClient              # Cliente HTTP para backend
├── WelcomeScreen          # Tela inicial
├── AuthenticationScreen   # Autenticação
├── MainMenuScreen         # Menu principal
├── AliasExtractorScreen   # Extração de aliases
├── AttributeInjectorScreen # Injeção de atributos
├── BatchMonitorScreen     # Monitor de jobs
└── GWorkspaceToolboxTUI   # Aplicação principal
```

### Extendendo a TUI

Para adicionar uma nova tela:

```python
class MyNewScreen(Screen):
    """My custom screen"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("My New Feature")
        yield Button("Click me!", id="my-btn")
        yield Footer()

    @on(Button.Pressed, "#my-btn")
    async def on_button_click(self):
        # Handle button click
        self.notify("Button clicked!")
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja o [CONTRIBUTING.md](../CONTRIBUTING.md) para guidelines.

## 📄 Licença

Este projeto está sob a mesma licença do GWorkspace Toolbox.

## 🙋 Suporte

- Issues: [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Documentação: [Docs](../docs/)
- Discussões: [GitHub Discussions](https://github.com/rafaelctz/GWorkspace-toolbox/discussions)

---

**Feito com ❤️ usando [Textual](https://textual.textualize.io/)**
