# 🤖 MCP Agent Archetype

> **Arquétipo para desenvolvimento de agentes MCP (Model Context Protocol) na Cielo**

Um framework robusto e extensível para criar agentes MCP com estruturas mínimas ou completas, dependendo das suas necessidades de projeto.

## 📋 Índice

- [🚀 Início Rápido](#-início-rápido)
- [📊 Tipos de Setup](#-tipos-de-setup)
- [🏗️ Estruturas Geradas](#️-estruturas-geradas)
- [🤖 Criando Seu Primeiro Agente](#-criando-seu-primeiro-agente)
- [📚 Guia Completo](#-guia-completo)
- [🧪 Testes](#-testes)
- [🔧 Comandos Úteis](#-comandos-úteis)
- [📖 Referência da API](#-referência-da-api)

## 🚀 Início Rápido

### Pré-requisitos

- **Python 3.11+**
- **Git**
- **pip** ou **Poetry** (dependendo do setup escolhido)

### Instalação

```bash
# 1. Clone o repositório do archetype
git clone <repo-url>
cd mcp-agent-archetype

# 2. Torne o script executável
chmod +x gerar_projeto.sh

# 3. Crie seu projeto
./gerar_projeto.sh minimal meu-agente-mcp
```

## 📊 Tipos de Setup

### 🎯 **Setup Minimal**
Ideal para **prototipagem rápida** e **projetos simples**

```bash
./gerar_projeto.sh minimal meu-projeto-simples
```

**Características:**
- ✅ Core MCP framework completo
- ✅ Exemplo funcional incluído  
- ✅ Estrutura de testes básica
- ✅ Scripts de utilitários
- ✅ Configuração com pip/setuptools
- ✅ Pronto para uso imediato

### 🏢 **Setup Full**
Ideal para **projetos enterprise** e **produção**

```bash
./gerar_projeto.sh full meu-projeto-enterprise
```

**Características:**
- ✅ Tudo do setup minimal +
- ✅ Arquitetura modular avançada
- ✅ Middleware e protocolos
- ✅ Poetry para gerenciamento de dependências
- ✅ Docker e Kubernetes ready
- ✅ CI/CD com GitHub Actions
- ✅ Monitoramento e observabilidade
- ✅ Documentação API automática

## 🏗️ Estruturas Geradas

### Setup Minimal
```
meu-projeto/
├── 📁 src/
│   ├── 📁 mcp_agent/
│   │   ├── __init__.py
│   │   └── base_agent.py          # 🏗️ Core MCP framework
│   ├── 📁 agents/                 # 🤖 Seus agentes aqui
│   ├── 📁 examples/
│   │   └── simple_agent.py        # 💡 Exemplo funcional
│   └── __init__.py
├── 📁 tests/                      # 🧪 Testes
├── 📁 config/                     # ⚙️ Configurações
├── 📁 scripts/
│   └── create_agent.py            # 📜 Gerador de agentes
├── requirements.txt               # 📦 Dependências
├── requirements-dev.txt           # 🛠️ Deps desenvolvimento
├── pyproject.toml                 # 🔧 Configuração projeto
├── Makefile                       # 🎯 Comandos úteis
├── .gitignore                     # 📝 Git ignore
└── README.md                      # 📖 Documentação
```

### Setup Full
```
meu-projeto/
├── 📁 src/
│   ├── 📁 mcp_agent/
│   │   ├── 📁 core/               # 🏗️ Core framework
│   │   ├── 📁 protocols/          # 🔌 Protocolos MCP
│   │   ├── 📁 utils/              # 🛠️ Utilitários
│   │   └── 📁 middleware/         # 🔄 Middleware
│   ├── 📁 agents/
│   │   ├── 📁 data_processor/     # 📊 Processamento dados
│   │   └── 📁 notification_service/ # 📨 Notificações
│   └── 📁 examples/
├── 📁 tests/
│   ├── 📁 unit/                   # 🧪 Testes unitários
│   └── 📁 integration/            # 🔗 Testes integração
├── 📁 deployment/
│   ├── 📁 kubernetes/             # ☸️ K8s configs
│   └── 📁 helm/                   # 📊 Helm charts
├── 📁 monitoring/                 # 📈 Observabilidade
├── 📁 .github/workflows/          # 🔄 CI/CD
├── pyproject.toml                 # 🎭 Poetry config
├── Dockerfile                     # 🐳 Container
└── README.md
```

## 🤖 Criando Seu Primeiro Agente

### Passo 1: Gerar o Projeto

```bash
# Setup mínimo (recomendado para começar)
./gerar_projeto.sh minimal meu-primeiro-agente
cd meu-primeiro-agente
```

### Passo 2: Configurar Ambiente

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Passo 3: Testar a Base

```bash
# Executar exemplo incluído
python -m src.examples.simple_agent

# Executar testes
pytest tests/ -v
```

### Passo 4: Criar Seu Agente

```bash
# Usar o gerador automático
make create-agent NAME=processador_dados

# Ou manualmente
mkdir -p src/agents/meu_agente
```

### Passo 5: Implementar o Agente

```python
# src/agents/meu_agente/agent.py
from src.mcp_agent.base_agent import BaseMCPAgent, AgentConfig, MCPMessage
import asyncio

class MeuAgente(BaseMCPAgent):
    """Meu primeiro agente MCP"""
    
    async def _custom_initialize(self):
        """Inicialização personalizada"""
        self.logger.info("Inicializando meu agente...")
        # Sua lógica de setup aqui
        await asyncio.sleep(0.1)
    
    async def _process_custom_message(self, message: MCPMessage):
        """Processamento de mensagens"""
        message_type = message.message_type.lower()
        
        if message_type == "processar":
            # Sua lógica de processamento
            dados = message.payload.get("dados", [])
            resultado = self._processar_dados(dados)
            
            return {
                "status": "processado",
                "resultado": resultado,
                "timestamp": message.timestamp.isoformat()
            }
        
        elif message_type == "ping":
            return {"response": "pong", "agent": "meu_agente"}
        
        else:
            raise ValueError(f"Tipo de mensagem não suportado: {message_type}")
    
    def _processar_dados(self, dados):
        """Lógica específica do seu domínio"""
        # Implementar sua lógica aqui
        return f"Processados {len(dados)} itens"

# Exemplo de uso
async def main():
    config = AgentConfig(
        agent_id="meu_agente_001",
        agent_name="Meu Agente",
        version="1.0.0",
        description="Meu primeiro agente MCP"
    )
    
    agente = MeuAgente(config)
    
    if await agente.initialize():
        # Testar o agente
        mensagem = agente.create_message("processar", {
            "dados": [1, 2, 3, 4, 5]
        })
        
        resposta = await agente.process_message(mensagem)
        print(f"Resposta: {resposta.data}")
    
if __name__ == "__main__":
    asyncio.run(main())
```

### Passo 6: Testar Seu Agente

```python
# tests/test_meu_agente.py
import pytest
from src.agents.meu_agente.agent import MeuAgente
from src.mcp_agent.base_agent import AgentConfig

@pytest.fixture
def agente_config():
    return AgentConfig(
        agent_id="test_agente",
        agent_name="Test Agente",
        version="1.0.0",
        description="Agente para testes"
    )

@pytest.mark.asyncio
async def test_agente_inicializa(agente_config):
    agente = MeuAgente(agente_config)
    resultado = await agente.initialize()
    assert resultado is not None

@pytest.mark.asyncio
async def test_processa_mensagem(agente_config):
    agente = MeuAgente(agente_config)
    await agente.initialize()
    
    mensagem = agente.create_message("processar", {"dados": [1, 2, 3]})
    resposta = await agente.process_message(mensagem)
    
    assert resposta.success is True
    assert "processados" in resposta.data["resultado"].lower()
```

## 📚 Guia Completo

### Conceitos Fundamentais

#### 🏗️ **BaseMCPAgent**
Classe base que todos os agentes devem herdar:

- **Gerenciamento de estado** (INITIALIZING, READY, PROCESSING, ERROR, SHUTDOWN)
- **Sistema de logging** configurável
- **Processamento de mensagens** assíncrono
- **Tratamento de erros** robusto

#### 📨 **MCPMessage**
Estrutura padrão para comunicação:

```python
@dataclass
class MCPMessage:
    id: str                        # Identificador único
    timestamp: datetime            # Timestamp da mensagem
    agent_id: str                 # ID do agente remetente
    message_type: str             # Tipo da mensagem
    payload: Dict[str, Any]       # Dados da mensagem
    metadata: Optional[Dict[str, Any]] = None  # Metadados opcionais
```

#### ✅ **AgentResponse**
Resposta padronizada:

```python
@dataclass
class AgentResponse:
    success: bool                 # Se a operação foi bem-sucedida
    data: Any = None             # Dados de resposta
    error: Optional[str] = None  # Mensagem de erro (se houver)
```

### Padrões de Implementação

#### 🔄 **Ciclo de Vida do Agente**

1. **Criação** → Instancia com `AgentConfig`
2. **Inicialização** → Chama `initialize()`
3. **Processamento** → Recebe e processa `MCPMessage`
4. **Finalização** → Chama `shutdown()` (se necessário)

#### 🎯 **Tipos de Mensagem Recomendados**

| Tipo | Descrição | Exemplo de Payload |
|------|-----------|-------------------|
| `ping` | Teste de conectividade | `{}` |
| `status` | Status do agente | `{}` |
| `process` | Processamento principal | `{"data": [...]}` |
| `configure` | Configuração dinâmica | `{"settings": {...}}` |
| `shutdown` | Finalização graceful | `{}` |

### Configuração Avançada

#### 📊 **Logging Personalizado**

```python
config = AgentConfig(
    agent_id="meu_agente",
    agent_name="Meu Agente",
    version="1.0.0",
    description="Agente com logging avançado",
    log_level="DEBUG"  # DEBUG, INFO, WARNING, ERROR
)
```

#### ⚙️ **Configuração por Arquivo**

```yaml
# config/agent_config.yaml
agent:
  id: "processador_001"
  name: "Processador de Dados"
  version: "2.1.0"
  log_level: "INFO"

settings:
  batch_size: 100
  timeout: 30
  max_retries: 3
```

```python
# Carregar configuração
import yaml

with open("config/agent_config.yaml") as f:
    config_dict = yaml.safe_load(f)

config = AgentConfig(**config_dict["agent"])
```

## 🧪 Testes

### Estrutura de Testes

```bash
tests/
├── conftest.py                 # Fixtures compartilhadas
├── test_base_agent.py         # Testes da classe base
├── unit/
│   └── test_meu_agente.py     # Testes unitários
└── integration/
    └── test_agent_integration.py  # Testes de integração
```

### Fixtures Úteis

```python
# tests/conftest.py
import pytest
from src.mcp_agent.base_agent import AgentConfig

@pytest.fixture
def agent_config():
    return AgentConfig(
        agent_id="test_agent",
        agent_name="Test Agent",
        version="1.0.0",
        description="Agent for testing"
    )

@pytest.fixture
async def initialized_agent(agent_config):
    from src.agents.meu_agente.agent import MeuAgente
    agent = MeuAgente(agent_config)
    await agent.initialize()
    yield agent
    # Cleanup se necessário
```

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/unit/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html

# Testes de performance
pytest tests/ --benchmark-only
```

## 🔧 Comandos Úteis

### Makefile (Setup Minimal)

```bash
# Instalar dependências de desenvolvimento
make install-dev

# Executar testes
make test

# Executar exemplo
make run

# Criar novo agente
make create-agent NAME=processador_vendas

# Ajuda
make help
```

### Poetry (Setup Full)

```bash
# Instalar dependências
poetry install

# Adicionar nova dependência
poetry add requests

# Executar dentro do ambiente
poetry run python -m src.examples.simple_agent

# Shell do ambiente
poetry shell
```

### Scripts Personalizados

```bash
# Gerar documentação da API
python scripts/generate_docs.py

# Executar linting
python scripts/lint.py

# Deploy para staging
python scripts/deploy.py --env staging
```

## 📖 Referência da API

### Classes Principais

#### `BaseMCPAgent`

```python
class BaseMCPAgent(ABC):
    def __init__(self, config: AgentConfig)
    async def initialize() -> None
    async def process_message(self, message: MCPMessage) -> AgentResponse
    def create_message(self, message_type: str, payload: Dict[str, Any]) -> MCPMessage
    
    # Métodos abstratos para implementar
    @abstractmethod
    async def _custom_initialize(self) -> None
    @abstractmethod
    async def _process_custom_message(self, message: MCPMessage) -> Any
```

#### `AgentConfig`

```python
@dataclass
class AgentConfig:
    agent_id: str           # Identificador único do agente
    agent_name: str         # Nome amigável
    version: str            # Versão do agente
    description: str        # Descrição do agente
    log_level: str = "INFO" # Nível de logging
```

#### `MCPMessage`

```python
@dataclass
class MCPMessage:
    id: str                                    # ID único da mensagem
    timestamp: datetime                        # Timestamp
    agent_id: str                             # ID do agente remetente
    message_type: str                         # Tipo da mensagem
    payload: Dict[str, Any]                   # Dados
    metadata: Optional[Dict[str, Any]] = None # Metadados
```

#### `AgentResponse`

```python
@dataclass
class AgentResponse:
    success: bool                   # Sucesso da operação
    data: Any = None               # Dados de resposta
    error: Optional[str] = None    # Mensagem de erro
```

### Enums

#### `AgentStatus`

```python
class AgentStatus(Enum):
    INITIALIZING = "initializing"  # Inicializando
    READY = "ready"               # Pronto para processar
    PROCESSING = "processing"     # Processando mensagem
    ERROR = "error"              # Estado de erro
    SHUTDOWN = "shutdown"        # Finalizado
```

---

## 🚀 Próximos Passos

1. **Escolha o setup** adequado ao seu projeto
2. **Gere a estrutura** com o script
3. **Implemente seu primeiro agente** seguindo os exemplos
4. **Escreva testes** para garantir qualidade
5. **Configure CI/CD** (setup full) para automação
6. **Monitore em produção** com as ferramentas incluídas

## 🤝 Contribuição

Encontrou um bug ou tem uma sugestão? Abra uma issue ou envie um PR!

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

---

**Desenvolvido com ❤️ pela equipe Cielo**