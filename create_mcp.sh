#!/bin/bash

# =============================================================================
# Script Unificado para Geração da Estrutura MCP Agent Archetype
#
# Uso:
#   ./gerar_projeto.sh minimal <NOME_DO_PROJETO>
#   ./gerar_projeto.sh full <NOME_DO_PROJETO>
# =============================================================================

# --- Variáveis Globais e Cores ---
PYTHON_VERSION="3.11"
COMPANY_NAME="Cielo"
COMPANY_EMAIL="dev@cielo.com.br"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# =============================================================================
# FUNÇÃO PARA GERAR ESTRUTURA MÍNIMA
# =============================================================================
generate_minimal_structure() {
    echo -e "${BLUE}📁 Criando estrutura de pastas MÍNIMA...${NC}"
    mkdir -p "$PROJECT_NAME"
    mkdir -p "$PROJECT_NAME/src/mcp_agent"
    mkdir -p "$PROJECT_NAME/src/agents"
    mkdir -p "$PROJECT_NAME/src/examples"
    mkdir -p "$PROJECT_NAME/tests"
    mkdir -p "$PROJECT_NAME/config"
    mkdir -p "$PROJECT_NAME/scripts"

    echo -e "${BLUE}📝 Criando arquivos essenciais...${NC}"
    touch "$PROJECT_NAME/src/__init__.py"
    touch "$PROJECT_NAME/src/mcp_agent/__init__.py"
    touch "$PROJECT_NAME/src/agents/__init__.py"
    touch "$PROJECT_NAME/src/examples/__init__.py"
    touch "$PROJECT_NAME/tests/__init__.py"

    # Core MCP Agent (base_agent.py)
    cat > "$PROJECT_NAME/src/mcp_agent/base_agent.py" << 'EOF'
"""
Arquétipo Base MCP (Model Context Protocol) Agent
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class AgentStatus(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class AgentConfig:
    agent_id: str
    agent_name: str
    version: str
    description: str
    log_level: str = "INFO"

@dataclass
class MCPMessage:
    id: str
    timestamp: datetime
    agent_id: str
    message_type: str
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentResponse:
    success: bool
    data: Any = None
    error: Optional[str] = None

class BaseMCPAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = AgentStatus.INITIALIZING
        self._setup_logging()
        self.logger.info(f"Agente {self.config.agent_name} inicializando...")

    def _setup_logging(self):
        self.logger = logging.getLogger(f"mcp.{self.config.agent_id}")
        self.logger.setLevel(getattr(logging, self.config.log_level))
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f'%(asctime)s - {self.config.agent_name} - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    async def initialize(self):
        self.status = AgentStatus.READY
        self.logger.info("Agente inicializado com sucesso!")
        await self._custom_initialize()

    @abstractmethod
    async def _custom_initialize(self):
        pass

    @abstractmethod
    async def _process_custom_message(self, message: MCPMessage) -> Any:
        pass

    async def process_message(self, message: MCPMessage) -> AgentResponse:
        if self.status != AgentStatus.READY:
            return AgentResponse(success=False, error=f"Agente não pronto. Status: {self.status.value}")
        
        self.status = AgentStatus.PROCESSING
        self.logger.debug(f"Processando: {message.message_type}")
        try:
            result = await self._process_custom_message(message)
            self.status = AgentStatus.READY
            return AgentResponse(success=True, data=result)
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {str(e)}")
            self.status = AgentStatus.ERROR
            return AgentResponse(success=False, error=str(e))

    def create_message(self, message_type: str, payload: Dict[str, Any]) -> MCPMessage:
        return MCPMessage(
            id=f"{self.config.agent_id}_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            agent_id=self.config.agent_id,
            message_type=message_type,
            payload=payload
        )
EOF

    # Exemplo funcional - simple_agent.py
    cat > "$PROJECT_NAME/src/examples/simple_agent.py" << 'EOF'
"""
Exemplo simples de um agente MCP
"""
import asyncio
from src.mcp_agent.base_agent import BaseMCPAgent, AgentConfig, MCPMessage

class SimpleAgent(BaseMCPAgent):
    """Agente simples de exemplo"""
    
    async def _custom_initialize(self):
        """Inicialização personalizada"""
        self.logger.info("Agente simples inicializado!")
        # Simular algum setup
        await asyncio.sleep(0.1)
    
    async def _process_custom_message(self, message: MCPMessage):
        """Processamento de mensagens"""
        message_type = message.message_type.lower()
        
        if message_type == "ping":
            return {"response": "pong", "timestamp": message.timestamp.isoformat()}
        
        elif message_type == "echo":
            return {"echo": message.payload.get("text", "Nenhum texto fornecido")}
        
        elif message_type == "soma":
            a = message.payload.get("a", 0)
            b = message.payload.get("b", 0)
            return {"resultado": a + b, "operacao": "soma"}
        
        elif message_type == "status":
            return {
                "agent_id": self.config.agent_id,
                "agent_name": self.config.agent_name,
                "status": self.status.value,
                "version": self.config.version
            }
        
        else:
            raise ValueError(f"Tipo de mensagem não suportado: {message_type}")

async def main():
    """Função principal de demonstração"""
    # Configuração do agente
    config = AgentConfig(
        agent_id="simple_001",
        agent_name="Agente Simples",
        version="1.0.0",
        description="Agente de exemplo para demonstração",
        log_level="INFO"
    )
    
    # Criar e inicializar o agente
    agente = SimpleAgent(config)
    await agente.initialize()
    
    print("🚀 Agente Simple Agent executando...")
    print("=" * 50)
    
    # Teste 1: Ping
    print("\n📨 Teste 1: Ping")
    msg_ping = agente.create_message("ping", {})
    resposta = await agente.process_message(msg_ping)
    print(f"   Resposta: {resposta.data}")
    
    # Teste 2: Echo
    print("\n📨 Teste 2: Echo")
    msg_echo = agente.create_message("echo", {"text": "Olá, mundo!"})
    resposta = await agente.process_message(msg_echo)
    print(f"   Resposta: {resposta.data}")
    
    # Teste 3: Soma
    print("\n📨 Teste 3: Soma")
    msg_soma = agente.create_message("soma", {"a": 15, "b": 27})
    resposta = await agente.process_message(msg_soma)
    print(f"   Resposta: {resposta.data}")
    
    # Teste 4: Status
    print("\n📨 Teste 4: Status")
    msg_status = agente.create_message("status", {})
    resposta = await agente.process_message(msg_status)
    print(f"   Resposta: {resposta.data}")
    
    # Teste 5: Comando inválido
    print("\n📨 Teste 5: Comando inválido")
    msg_invalido = agente.create_message("comando_inexistente", {})
    resposta = await agente.process_message(msg_invalido)
    print(f"   Sucesso: {resposta.success}")
    print(f"   Erro: {resposta.error}")
    
    print("\n✅ Demonstração concluída!")

if __name__ == "__main__":
    asyncio.run(main())
EOF

    # Script para criar novos agentes
    cat > "$PROJECT_NAME/scripts/create_agent.py" << 'EOF'
#!/usr/bin/env python3
"""
Script para criar novos agentes MCP
"""
import os
import argparse
from pathlib import Path

def create_agent(agent_name: str):
    """Cria um novo agente com estrutura básica"""
    
    # Sanitizar nome do agente
    agent_name_clean = agent_name.lower().replace('-', '_').replace(' ', '_')
    
    # Diretório do agente
    agent_dir = Path(f"src/agents/{agent_name_clean}")
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    # Arquivo __init__.py
    (agent_dir / "__init__.py").write_text('"""Módulo do agente"""\n')
    
    # Arquivo principal do agente
    agent_file = agent_dir / "agent.py"
    agent_content = f'''"""
Agente: {agent_name}
"""
import asyncio
from src.mcp_agent.base_agent import BaseMCPAgent, AgentConfig, MCPMessage

class {agent_name.title().replace('_', '').replace('-', '')}Agent(BaseMCPAgent):
    """Agente {agent_name}"""
    
    async def _custom_initialize(self):
        """Inicialização personalizada do agente"""
        self.logger.info("Agente {agent_name} inicializado!")
        # Adicione sua lógica de inicialização aqui
        await asyncio.sleep(0.1)
    
    async def _process_custom_message(self, message: MCPMessage):
        """Processamento de mensagens personalizadas"""
        message_type = message.message_type.lower()
        
        if message_type == "ping":
            return {{"response": "pong", "agent": "{agent_name}"}}
        
        elif message_type == "processar":
            # Implemente sua lógica de processamento aqui
            dados = message.payload.get("dados", [])
            resultado = f"Processados {{len(dados)}} itens pelo agente {agent_name}"
            return {{"resultado": resultado}}
        
        else:
            raise ValueError(f"Tipo de mensagem não suportado: {{message_type}}")

# Exemplo de uso
async def main():
    """Função principal para teste do agente"""
    config = AgentConfig(
        agent_id="{agent_name_clean}_001",
        agent_name="{agent_name.title()}",
        version="1.0.0",
        description="Agente {agent_name}",
        log_level="INFO"
    )
    
    agente = {agent_name.title().replace('_', '').replace('-', '')}Agent(config)
    await agente.initialize()
    
    # Teste básico
    msg = agente.create_message("ping", {{}})
    resposta = await agente.process_message(msg)
    print(f"Resposta: {{resposta.data}}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    agent_file.write_text(agent_content)
    
    # Arquivo de teste
    test_dir = Path("tests")
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / f"test_{agent_name_clean}.py"
    test_content = f'''"""
Testes para o agente {agent_name}
"""
import pytest
from src.agents.{agent_name_clean}.agent import {agent_name.title().replace('_', '').replace('-', '')}Agent
from src.mcp_agent.base_agent import AgentConfig

@pytest.fixture
def agent_config():
    return AgentConfig(
        agent_id="test_{agent_name_clean}",
        agent_name="Test {agent_name.title()}",
        version="1.0.0",
        description="Agente de teste"
    )

@pytest.mark.asyncio
async def test_agent_initialize(agent_config):
    agente = {agent_name.title().replace('_', '').replace('-', '')}Agent(agent_config)
    await agente.initialize()
    assert agente.status.value == "ready"

@pytest.mark.asyncio
async def test_ping_message(agent_config):
    agente = {agent_name.title().replace('_', '').replace('-', '')}Agent(agent_config)
    await agente.initialize()
    
    msg = agente.create_message("ping", {{}})
    resposta = await agente.process_message(msg)
    
    assert resposta.success is True
    assert resposta.data["response"] == "pong"
    assert resposta.data["agent"] == "{agent_name}"
'''
    
    test_file.write_text(test_content)
    
    print(f"✅ Agente '{agent_name}' criado com sucesso!")
    print(f"   📁 Diretório: {agent_dir}")
    print(f"   📄 Arquivo principal: {agent_file}")
    print(f"   🧪 Arquivo de teste: {test_file}")
    print(f"\n📋 Para executar:")
    print(f"   python -m src.agents.{agent_name_clean}.agent")
    print(f"   make run-agent NAME={agent_name_clean}")

def main():
    parser = argparse.ArgumentParser(description="Criar novo agente MCP")
    parser.add_argument("--name", required=True, help="Nome do agente")
    
    args = parser.parse_args()
    create_agent(args.name)

if __name__ == "__main__":
    main()
EOF

    # Makefile corrigido
    cat > "$PROJECT_NAME/Makefile" << 'EOF'
.PHONY: help install-dev test run create-agent run-agent

help:
	@echo "Comandos disponíveis:"
	@echo "  env          - Criar ambiente virtual"
	@echo "  install-dev  - Instalar dependências de desenvolvimento"
	@echo "  test         - Executar testes"
	@echo "  run          - Executar exemplo simples"
	@echo "  create-agent - Criar novo agente (uso: make create-agent NAME=meu_agente)"
	@echo "  run-agent    - Executar agente específico (uso: make run-agent NAME=meu_agente)"

env:
	@echo "Criando ambiente virtual..."
	python3 -m venv .venv
	@echo "Ative o ambiente virtual com: source .venv/bin/activate"

install-dev:
	pip install -e .[dev]

test:
	pytest tests/ -v

run:
	python3 -m src.examples.simple_agent

create-agent:
	@if [ -z "$(NAME)" ]; then echo "❌ Erro: defina NAME. Ex: make create-agent NAME=meu_agente"; exit 1; fi
	python3 scripts/create_agent.py --name $(NAME)

run-agent:
	@if [ -z "$(NAME)" ]; then echo "❌ Erro: defina NAME. Ex: make run-agent NAME=meu_agente"; exit 1; fi
	@if [ ! -f "src/agents/$(NAME)/agent.py" ]; then echo "❌ Erro: Agente '$(NAME)' não encontrado em src/agents/$(NAME)/"; exit 1; fi
	python3 -m src.agents.$(NAME).agent
EOF

    # requirements.txt
    cat > "$PROJECT_NAME/requirements.txt" << 'EOF'
# Dependências básicas do projeto
dataclasses-json>=0.5.7
typing-extensions>=4.0.0
EOF

    # requirements-dev.txt
    cat > "$PROJECT_NAME/requirements-dev.txt" << 'EOF'
# Dependências de desenvolvimento
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
coverage>=7.0.0
pytest-cov>=4.0.0
EOF

    # .gitignore
    cat > "$PROJECT_NAME/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
EOF

    # pyproject.toml (versão mínima)
    cat > "$PROJECT_NAME/pyproject.toml" << EOF
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "Arquétipo MCP Agent (Mínimo)"
authors = [{name = "$COMPANY_NAME", email = "$COMPANY_EMAIL"}]
readme = "README.md"
requires-python = ">=$PYTHON_VERSION"
dependencies = [
    "dataclasses-json>=0.5.7",
    "typing-extensions>=4.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0", 
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "coverage>=7.0.0",
    "pytest-cov>=4.0.0"
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
EOF

    # README.md corrigido
    cat > "$PROJECT_NAME/README.md" << EOF
# $PROJECT_NAME (Estrutura Mínima)

Este é um projeto gerado com a estrutura mínima do MCP Agent Archetype.

## 🚀 Início Rápido

### 1. Configurar ambiente
\`\`\`bash
# Criar ambiente virtual
make env
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
\`\`\`

### 2. Executar exemplo
\`\`\`bash
# Executar agente de exemplo
make run
\`\`\`

### 3. Criar novo agente
\`\`\`bash
# Criar agente
make create-agent NAME=meu_agente

# Executar agente criado
make run-agent NAME=meu_agente
\`\`\`

### 4. Executar testes
\`\`\`bash
make test
\`\`\`

## 📋 Comandos Disponíveis

- \`make help\` - Mostra ajuda
- \`make env\` - Cria ambiente virtual
- \`make run\` - Executa exemplo simples
- \`make create-agent NAME=nome\` - Cria novo agente
- \`make run-agent NAME=nome\` - Executa agente específico
- \`make test\` - Executa testes

## 🏗️ Estrutura do Projeto

\`\`\`
src/
├── mcp_agent/           # Core framework
│   └── base_agent.py    # Classe base
├── agents/              # Seus agentes aqui
├── examples/            # Exemplos
│   └── simple_agent.py  # Agente de exemplo
tests/                   # Testes
scripts/                 # Scripts utilitários
config/                  # Configurações
\`\`\`
EOF

    # Tornar script executável
    chmod +x "$PROJECT_NAME/scripts/create_agent.py"
}

# =============================================================================
# FUNÇÃO PARA GERAR ESTRUTURA COMPLETA
# =============================================================================
generate_full_structure() {
    echo -e "${BLUE}📁 Criando estrutura de pastas COMPLETA...${NC}"
    mkdir -p "$PROJECT_NAME/src/mcp_agent/core"
    mkdir -p "$PROJECT_NAME/src/mcp_agent/protocols"
    mkdir -p "$PROJECT_NAME/src/mcp_agent/utils"
    mkdir -p "$PROJECT_NAME/src/mcp_agent/middleware"
    mkdir -p "$PROJECT_NAME/src/agents/data_processor"
    mkdir -p "$PROJECT_NAME/src/agents/notification_service"
    mkdir -p "$PROJECT_NAME/tests/unit"
    mkdir -p "$PROJECT_NAME/tests/integration"
    mkdir -p "$PROJECT_NAME/config"
    mkdir -p "$PROJECT_NAME/scripts"
    mkdir -p "$PROJECT_NAME/docs/api"
    mkdir -p "$PROJECT_NAME/deployment/kubernetes"
    mkdir -p "$PROJECT_NAME/deployment/helm/templates"
    mkdir -p "$PROJECT_NAME/monitoring"
    mkdir -p "$PROJECT_NAME/.github/workflows"

    echo -e "${BLUE}📝 Criando arquivos de placeholder da estrutura completa...${NC}"
    touch "$PROJECT_NAME/src/__init__.py"
    touch "$PROJECT_NAME/src/mcp_agent/__init__.py"
    touch "$PROJECT_NAME/src/mcp_agent/core/__init__.py"
    touch "$PROJECT_NAME/src/agents/__init__.py"
    touch "$PROJECT_NAME/src/agents/data_processor/__init__.py"
    touch "$PROJECT_NAME/tests/__init__.py"
    touch "$PROJECT_NAME/tests/unit/__init__.py"

    echo '"""Implementação base do Agente"""' > "$PROJECT_NAME/src/mcp_agent/core/base_agent.py"
    echo '"""Configurações Pydantic"""' > "$PROJECT_NAME/src/mcp_agent/core/config.py"
    echo '"""Exceções customizadas"""' > "$PROJECT_NAME/src/mcp_agent/core/exceptions.py"

    # pyproject.toml (versão completa com Poetry)
    cat > "$PROJECT_NAME/pyproject.toml" << EOF
[tool.poetry]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "Arquétipo MCP para agentes da companhia (Completo)"
authors = ["$COMPANY_NAME <$COMPANY_EMAIL>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^$PYTHON_VERSION"
pydantic = "^2.0"
pyyaml = "^6.0"
loguru = "^0.7"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
pytest-asyncio = "^0.21"
black = "^23.0"
isort = "^5.0"
pre-commit = "^3.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOF

    # Arquivos de placeholder para Docker, CI/CD, etc.
    echo "# Dockerfile para o serviço de agentes" > "$PROJECT_NAME/Dockerfile"
    echo "name: CI Pipeline\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo 'Build step'" > "$PROJECT_NAME/.github/workflows/ci.yml"
    echo "# README da estrutura completa" > "$PROJECT_NAME/README.md"
}

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================
main() {
    # --- Validação dos Argumentos ---
    if [[ "$1" != "minimal" && "$1" != "full" ]] || [ -z "$2" ]; then
      echo -e "${RED}❌ Erro: Argumentos inválidos.${NC}"
      echo "Uso: $0 <minimal|full> <NOME_DO_PROJETO>"
      exit 1
    fi

    SETUP_TYPE=$1
    PROJECT_NAME=$2

    if [ -d "$PROJECT_NAME" ]; then
        echo -e "${YELLOW}⚠️  O diretório '$PROJECT_NAME' já existe. Encerrando para evitar sobrescrever.${NC}"
        exit 1
    fi

    echo -e "${CYAN}🚀 Iniciando a criação do projeto MCP Agent: ${PROJECT_NAME}${NC}"
    echo -e "${CYAN}   Tipo de estrutura: ${SETUP_TYPE}${NC}"
    echo ""

    case $SETUP_TYPE in
        minimal)
            generate_minimal_structure
            ;;
        full)
            generate_full_structure
            ;;
    esac

    # --- Mensagem Final ---
    echo ""
    echo -e "${GREEN}✅ Projeto '${PROJECT_NAME}' criado com sucesso!${NC}"
    echo ""
    echo -e "${CYAN}📋 Próximos passos:${NC}"
    echo "  1. cd ${PROJECT_NAME}"
    if [ "$SETUP_TYPE" == "full" ]; then
        echo "  2. Rode 'poetry install' para instalar as dependências."
    else
        echo "  2. Rode 'make env && source .venv/bin/activate' para criar o ambiente virtual."
        echo "  3. Rode 'pip install -r requirements.txt' para instalar as dependências."
        echo "  4. Rode 'make run' para testar o exemplo."
    fi
    echo "  5. Comece a desenvolver seus agentes!"
    echo ""
}

# --- Ponto de Entrada do Script ---
main "$@"