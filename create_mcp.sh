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
    "asyncio",
    "dataclasses",
    "typing-extensions"
]
[project.optional-dependencies]
dev = [ "pytest", "pytest-asyncio", "black", "flake8", "mypy" ]
EOF

    # Makefile (interno do projeto)
    cat > "$PROJECT_NAME/Makefile" << 'EOF'
.PHONY: help install-dev test run create-agent

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
	@if [ -z "$(NAME)" ]; then echo "Erro: defina NAME. Ex: make create-agent NAME=meu_agente"; exit 1; fi
	python3 scripts/create_agent.py --name $(NAME)
EOF

    # README.md
    cat > "$PROJECT_NAME/README.md" << EOF
# $PROJECT_NAME (Estrutura Mínima)
Este é um projeto gerado com a estrutura mínima do MCP Agent Archetype.
EOF

    # Outros arquivos de configuração... (requirements, gitignore, etc.)
    # (Omitidos para brevidade, mas o script os criaria como na resposta anterior)
    touch "$PROJECT_NAME/requirements.txt"
    touch "$PROJECT_NAME/requirements-dev.txt"
    touch "$PROJECT_NAME/.gitignore"
    touch "$PROJECT_NAME/scripts/create_agent.py"
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
        echo "  2. Crie um ambiente virtual e instale as dependências (pip install -r requirements.txt)."
    fi
    echo "  3. Comece a desenvolver seus agentes!"
    echo ""
}

# --- Ponto de Entrada do Script ---
main "$@"