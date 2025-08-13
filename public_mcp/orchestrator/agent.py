"""
Agente MCP Orquestrador
Coordena múltiplos agentes MCP para fornecer respostas completas
"""
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.mcp_agent.base_agent import BaseMCPAgent, AgentConfig, MCPMessage

# Importar os outros agentes
from src.agents.weather.agent import WeatherAgent
from src.agents.finance.agent import FinanceAgent

class OrchestratorAgent(BaseMCPAgent):
    """Agente orquestrador que coordena outros agentes MCP"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.sub_agents: Dict[str, BaseMCPAgent] = {}
        self.agent_configs = {
            "weather": AgentConfig(
                agent_id="weather_sub_001",
                agent_name="Weather Sub-Agent",
                version="1.0.0",
                description="Sub-agente de clima"
            ),
            "finance": AgentConfig(
                agent_id="finance_sub_001", 
                agent_name="Finance Sub-Agent",
                version="1.0.0",
                description="Sub-agente financeiro"
            )
        }
    
    async def _custom_initialize(self):
        """Inicialização do orquestrador e sub-agentes"""
        self.logger.info("🎭 Orquestrador inicializando...")
        
        # Inicializar agente de clima
        self.logger.info("   🌤️ Inicializando Weather Agent...")
        self.sub_agents["weather"] = WeatherAgent(self.agent_configs["weather"])
        await self.sub_agents["weather"].initialize()
        
        # Inicializar agente financeiro
        self.logger.info("   💰 Inicializando Finance Agent...")
        self.sub_agents["finance"] = FinanceAgent(self.agent_configs["finance"])
        await self.sub_agents["finance"].initialize()
        
        self.logger.info("✅ Todos os sub-agentes inicializados!")
        await asyncio.sleep(0.1)
    
    async def _process_custom_message(self, message: MCPMessage) -> Any:
        """Processamento de mensagens do orquestrador"""
        message_type = message.message_type.lower()
        
        if message_type == "relatorio_completo":
            cidade = message.payload.get("cidade", "São Paulo")
            return await self._generate_complete_report(cidade)
            
        elif message_type == "clima_e_economia":
            cidade = message.payload.get("cidade", "São Paulo")
            return await self._get_weather_and_finance(cidade)
            
        elif message_type == "multiplas_cidades_completo":
            cidades = message.payload.get("cidades", ["São Paulo", "Rio de Janeiro"])
            return await self._get_multiple_cities_complete(cidades)
            
        elif message_type == "analise_viagem":
            origem = message.payload.get("origem", "São Paulo")
            destino = message.payload.get("destino", "Rio de Janeiro")
            return await self._travel_analysis(origem, destino)
            
        elif message_type == "dashboard":
            return await self._generate_dashboard()
            
        elif message_type == "status_agentes":
            return await self._check_agents_status()
            
        elif message_type == "ping":
            return {"response": "pong", "agent": "orchestrator", "sub_agents": list(self.sub_agents.keys())}
            
        else:
            raise ValueError(f"Tipo de mensagem não suportado: {message_type}")
    
    async def _generate_complete_report(self, cidade: str) -> Dict[str, Any]:
        """Gera relatório completo combinando clima e finanças"""
        self.logger.info(f"🎭 Gerando relatório completo para {cidade}")
        
        # Passo 1: Obter dados climáticos
        self.logger.info("   ⏳ Consultando dados climáticos...")
        weather_msg = self.sub_agents["weather"].create_message("clima_atual", {"cidade": cidade})
        weather_response = await self.sub_agents["weather"].process_message(weather_msg)
        
        if not weather_response.success:
            return {"erro": f"Falha ao obter dados climáticos: {weather_response.error}"}
        
        # Passo 2: Obter previsão do tempo
        forecast_msg = self.sub_agents["weather"].create_message("previsao", {"cidade": cidade, "dias": 3})
        forecast_response = await self.sub_agents["weather"].process_message(forecast_msg)
        
        # Passo 3: Obter dados financeiros
        self.logger.info("   ⏳ Consultando dados financeiros...")
        finance_msg = self.sub_agents["finance"].create_message("resumo_mercado", {})
        finance_response = await self.sub_agents["finance"].process_message(finance_msg)
        
        if not finance_response.success:
            return {"erro": f"Falha ao obter dados financeiros: {finance_response.error}"}
        
        # Passo 4: Combinar e analisar dados
        self.logger.info("   🧠 Analisando e combinando dados...")
        
        # Análise combinada
        weather_data = weather_response.data
        finance_data = finance_response.data
        forecast_data = forecast_response.data if forecast_response.success else None
        
        # Gerar insights
        insights = self._generate_insights(weather_data, finance_data, forecast_data)
        
        # Passo 5: Montar relatório final
        relatorio = {
            "relatorio_id": f"REL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "cidade": cidade,
            "timestamp": datetime.now().isoformat(),
            "clima": {
                "atual": weather_data,
                "previsao": forecast_data.get("previsoes", []) if forecast_data else []
            },
            "financeiro": finance_data,
            "insights": insights,
            "resumo_executivo": self._generate_executive_summary(weather_data, finance_data, insights),
            "agentes_consultados": ["weather", "finance"],
            "tempo_processamento": "processado_em_tempo_real"
        }
        
        self.logger.info("✅ Relatório completo gerado!")
        return relatorio
    
    async def _get_weather_and_finance(self, cidade: str) -> Dict[str, Any]:
        """Obtém dados climáticos e financeiros de forma paralela"""
        self.logger.info(f"🎭 Consultando clima e finanças para {cidade} (paralelo)")
        
        # Executar consultas em paralelo
        tasks = []
        
        # Task 1: Clima atual
        weather_msg = self.sub_agents["weather"].create_message("clima_atual", {"cidade": cidade})
        weather_task = self.sub_agents["weather"].process_message(weather_msg)
        tasks.append(("weather", weather_task))
        
        # Task 2: Cotação USD/BRL
        usd_msg = self.sub_agents["finance"].create_message("cotacao_moeda", {"base": "USD", "target": "BRL"})
        usd_task = self.sub_agents["finance"].process_message(usd_msg)
        tasks.append(("usd_brl", usd_task))
        
        # Task 3: Bitcoin
        btc_msg = self.sub_agents["finance"].create_message("cotacao_crypto", {"crypto": "bitcoin", "currency": "brl"})
        btc_task = self.sub_agents["finance"].process_message(btc_msg)
        tasks.append(("bitcoin", btc_task))
        
        # Aguardar todas as tasks
        results = {}
        for name, task in tasks:
            try:
                response = await task
                results[name] = response.data if response.success else {"erro": response.error}
            except Exception as e:
                results[name] = {"erro": str(e)}
        
        return {
            "cidade": cidade,
            "clima": results.get("weather", {}),
            "cotacoes": {
                "usd_brl": results.get("usd_brl", {}),
                "bitcoin": results.get("bitcoin", {})
            },
            "correlacao": self._analyze_weather_finance_correlation(results.get("weather", {}), results),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_multiple_cities_complete(self, cidades: List[str]) -> Dict[str, Any]:
        """Obtém dados completos para múltiplas cidades"""
        self.logger.info(f"🎭 Processando {len(cidades)} cidades: {', '.join(cidades)}")
        
        resultados = {}
        
        for cidade in cidades:
            self.logger.info(f"   🏙️ Processando {cidade}...")
            
            # Obter dados da cidade
            resultado_cidade = await self._get_weather_and_finance(cidade)
            resultados[cidade] = resultado_cidade
            
            # Pequena pausa entre cidades
            await asyncio.sleep(0.2)
        
        # Análise comparativa
        comparacao = self._compare_cities(resultados)
        
        return {
            "cidades": resultados,
            "total_processadas": len(cidades),
            "comparacao": comparacao,
            "timestamp": datetime.now().isoformat(),
            "processamento": "sequencial"
        }
    
    async def _travel_analysis(self, origem: str, destino: str) -> Dict[str, Any]:
        """Análise completa para viagem entre duas cidades"""
        self.logger.info(f"✈️ Análise de viagem: {origem} → {destino}")
        
        # Obter dados das duas cidades
        dados_origem = await self._get_weather_and_finance(origem)
        dados_destino = await self._get_weather_and_finance(destino)
        
        # Obter previsões para ambas
        prev_origem_msg = self.sub_agents["weather"].create_message("previsao", {"cidade": origem, "dias": 5})
        prev_origem = await self.sub_agents["weather"].process_message(prev_origem_msg)
        
        prev_destino_msg = self.sub_agents["weather"].create_message("previsao", {"cidade": destino, "dias": 5})
        prev_destino = await self.sub_agents["weather"].process_message(prev_destino_msg)
        
        # Análise de viagem
        analise = {
            "origem": {
                "cidade": origem,
                "dados_atuais": dados_origem,
                "previsao": prev_origem.data if prev_origem.success else {}
            },
            "destino": {
                "cidade": destino, 
                "dados_atuais": dados_destino,
                "previsao": prev_destino.data if prev_destino.success else {}
            },
            "recomendacoes": self._generate_travel_recommendations(dados_origem, dados_destino),
            "melhor_dia_viagem": self._suggest_best_travel_day(prev_origem.data, prev_destino.data),
            "timestamp": datetime.now().isoformat()
        }
        
        return analise
    
    async def _generate_dashboard(self) -> Dict[str, Any]:
        """Gera dashboard com informações de múltiplas fontes"""
        self.logger.info("📊 Gerando dashboard completo...")
        
        # Obter dados de várias fontes em paralelo
        tasks = []
        
        # Clima de cidades principais
        cidades_principais = ["São Paulo", "Rio de Janeiro", "Brasília"]
        for cidade in cidades_principais:
            weather_msg = self.sub_agents["weather"].create_message("clima_atual", {"cidade": cidade})
            tasks.append(("weather_" + cidade.replace(" ", "_").lower(), 
                         self.sub_agents["weather"].process_message(weather_msg)))
        
        # Dados financeiros
        finance_msg = self.sub_agents["finance"].create_message("resumo_mercado", {})
        tasks.append(("market_summary", self.sub_agents["finance"].process_message(finance_msg)))
        
        # Top cryptos
        crypto_msg = self.sub_agents["finance"].create_message("top_cryptos", {"limit": 5, "currency": "brl"})
        tasks.append(("top_cryptos", self.sub_agents["finance"].process_message(crypto_msg)))
        
        # Processar todas as tasks
        dashboard_data = {}
        for name, task in tasks:
            try:
                response = await task
                dashboard_data[name] = response.data if response.success else {"erro": response.error}
            except Exception as e:
                dashboard_data[name] = {"erro": str(e)}
        
        # Montar dashboard
        dashboard = {
            "titulo": "Dashboard MCP Completo",
            "timestamp": datetime.now().isoformat(),
            "clima_cidades": {
                "sao_paulo": dashboard_data.get("weather_são_paulo", {}),
                "rio_janeiro": dashboard_data.get("weather_rio_de_janeiro", {}),
                "brasilia": dashboard_data.get("weather_brasília", {})
            },
            "mercado_financeiro": dashboard_data.get("market_summary", {}),
            "top_cryptos": dashboard_data.get("top_cryptos", {}),
            "alertas": self._generate_alerts(dashboard_data),
            "agentes_status": await self._check_agents_status()
        }
        
        return dashboard
    
    async def _check_agents_status(self) -> Dict[str, Any]:
        """Verifica status de todos os sub-agentes"""
        status = {}
        
        for agent_name, agent in self.sub_agents.items():
            try:
                ping_msg = agent.create_message("ping", {})
                response = await agent.process_message(ping_msg)
                
                status[agent_name] = {
                    "online": response.success,
                    "status": agent.status.value,
                    "response": response.data if response.success else response.error,
                    "config": {
                        "id": agent.config.agent_id,
                        "name": agent.config.agent_name,
                        "version": agent.config.version
                    }
                }
            except Exception as e:
                status[agent_name] = {
                    "online": False,
                    "erro": str(e)
                }
        
        return status
    
    def _generate_insights(self, weather_data: Dict, finance_data: Dict, forecast_data: Optional[Dict]) -> List[str]:
        """Gera insights baseados nos dados combinados"""
        insights = []
        
        # Insights climáticos
        if weather_data.get("temperatura"):
            temp = weather_data["temperatura"]
            if temp > 30:
                insights.append(f"🌡️ Temperatura elevada ({temp}°C) - ideal para atividades aquáticas")
            elif temp < 15:
                insights.append(f"🧥 Temperatura baixa ({temp}°C) - recomenda-se roupas quentes")
        
        if weather_data.get("descricao"):
            if "chuv" in weather_data["descricao"].lower():
                insights.append("☔ Condições chuvosas - leve guarda-chuva")
        
        # Insights financeiros
        if finance_data.get("moedas", {}).get("USD/BRL"):
            usd_rate = finance_data["moedas"]["USD/BRL"]
            if usd_rate > 5.5:
                insights.append(f"💰 Dólar alto (R$ {usd_rate:.2f}) - momento desfavorável para importações")
            elif usd_rate < 5.0:
                insights.append(f"💰 Dólar baixo (R$ {usd_rate:.2f}) - bom momento para compras internacionais")
        
        # Insights de forecast
        if forecast_data and forecast_data.get("previsoes"):
            chuva_dias = sum(1 for p in forecast_data["previsoes"] if p.get("probabilidade_chuva", 0) > 70)
            if chuva_dias >= 2:
                insights.append(f"🌧️ {chuva_dias} dias com alta probabilidade de chuva nos próximos dias")
        
        return insights
    
    def _generate_executive_summary(self, weather_data: Dict, finance_data: Dict, insights: List[str]) -> str:
        """Gera resumo executivo"""
        cidade = weather_data.get("cidade", "Cidade")
        temp = weather_data.get("temperatura", "N/A")
        condicao = weather_data.get("descricao", "N/A")
        
        usd_brl = finance_data.get("moedas", {}).get("USD/BRL", "N/A")
        
        summary = f"Relatório para {cidade}: Temperatura atual de {temp}°C com {condicao}. "
        summary += f"Cotação USD/BRL em {usd_brl}. "
        
        if insights:
            summary += f"Principais insights: {' | '.join(insights[:2])}"
        
        return summary
    
    def _analyze_weather_finance_correlation(self, weather_data: Dict, all_data: Dict) -> Dict[str, Any]:
        """Analisa correlação entre clima e dados financeiros"""
        correlacao = {"tipo": "analise_basica"}
        
        temp = weather_data.get("temperatura")
        if temp and temp > 35:
            correlacao["energia"] = "Temperatura alta pode aumentar demanda por energia elétrica"
        
        if "chuv" in weather_data.get("descricao", "").lower():
            correlacao["agro"] = "Chuva pode impactar positivamente commodities agrícolas"
        
        return correlacao
    
    def _compare_cities(self, resultados: Dict) -> Dict[str, Any]:
        """Compara dados entre cidades"""
        if len(resultados) < 2:
            return {"erro": "Necessário pelo menos 2 cidades para comparação"}
        
        temperaturas = {}
        for cidade, dados in resultados.items():
            temp = dados.get("clima", {}).get("temperatura")
            if temp:
                temperaturas[cidade] = temp
        
        if temperaturas:
            cidade_mais_quente = max(temperaturas, key=temperaturas.get)
            cidade_mais_fria = min(temperaturas, key=temperaturas.get)
            
            return {
                "temperatura": {
                    "mais_quente": {
                        "cidade": cidade_mais_quente,
                        "temperatura": temperaturas[cidade_mais_quente]
                    },
                    "mais_fria": {
                        "cidade": cidade_mais_fria,
                        "temperatura": temperaturas[cidade_mais_fria]
                    }
                }
            }
        
        return {"info": "Dados insuficientes para comparação"}
    
    def _generate_travel_recommendations(self, origem: Dict, destino: Dict) -> List[str]:
        """Gera recomendações de viagem"""
        recomendacoes = []
        
        # Comparar temperaturas
        temp_origem = origem.get("clima", {}).get("temperatura", 0)
        temp_destino = destino.get("clima", {}).get("temperatura", 0)
        
        if abs(temp_origem - temp_destino) > 10:
            recomendacoes.append(f"Grande diferença de temperatura ({temp_origem}°C → {temp_destino}°C) - prepare roupas adequadas")
        
        # Verificar chuva no destino
        desc_destino = destino.get("clima", {}).get("descricao", "")
        if "chuv" in desc_destino.lower():
            recomendacoes.append("Destino com previsão de chuva - leve guarda-chuva")
        
        return recomendacoes
    
    def _suggest_best_travel_day(self, prev_origem: Optional[Dict], prev_destino: Optional[Dict]) -> Dict[str, Any]:
        """Sugere melhor dia para viajar"""
        if not prev_origem or not prev_destino:
            return {"erro": "Dados de previsão insuficientes"}
        
        # Análise simplificada - menor probabilidade de chuva em ambas as cidades
        previsoes_origem = prev_origem.get("previsoes", [])
        previsoes_destino = prev_destino.get("previsoes", [])
        
        if not previsoes_origem or not previsoes_destino:
            return {"info": "Previsões não disponíveis"}
        
        melhor_dia = None
        menor_chuva = 100
        
        for i, (orig, dest) in enumerate(zip(previsoes_origem, previsoes_destino)):
            chuva_total = orig.get("probabilidade_chuva", 50) + dest.get("probabilidade_chuva", 50)
            if chuva_total < menor_chuva:
                menor_chuva = chuva_total
                melhor_dia = {
                    "dia": i + 1,
                    "data": orig.get("data", "N/A"),
                    "probabilidade_chuva_origem": orig.get("probabilidade_chuva", 0),
                    "probabilidade_chuva_destino": dest.get("probabilidade_chuva", 0)
                }
        
        return melhor_dia or {"info": "Não foi possível determinar melhor dia"}
    
    def _generate_alerts(self, dashboard_data: Dict) -> List[str]:
        """Gera alertas baseados nos dados do dashboard"""
        alertas = []
        
        # Verificar temperaturas extremas
        for key, value in dashboard_data.items():
            if key.startswith("weather_") and isinstance(value, dict):
                temp = value.get("temperatura")
                if temp and temp > 40:
                    cidade = key.replace("weather_", "").replace("_", " ").title()
                    alertas.append(f"🔥 ALERTA: Temperatura extrema em {cidade} ({temp}°C)")
        
        # Verificar volatilidade crypto
        cryptos = dashboard_data.get("top_cryptos", {}).get("top_cryptos", [])
        for crypto in cryptos:
            if abs(crypto.get("variacao_24h", 0)) > 10:
                alertas.append(f"📈 ALERTA: {crypto['nome']} com alta volatilidade ({crypto['variacao_24h']:+.1f}%)")
        
        return alertas
    
    async def shutdown(self):
        """Finalização do orquestrador e sub-agentes"""
        self.logger.info("🎭 Finalizando orquestrador...")
        
        for agent_name, agent in self.sub_agents.items():
            try:
                await agent.shutdown()
                self.logger.info(f"   ✅ {agent_name} finalizado")
            except Exception as e:
                self.logger.error(f"   ❌ Erro ao finalizar {agent_name}: {e}")
        
        self.logger.info("🎭 Orquestrador finalizado")

# Exemplo de uso completo
async def main():
    """Demonstração completa do orquestrador"""
    config = AgentConfig(
        agent_id="orchestrator_001",
        agent_name="Orchestrator Agent",
        version="1.0.0",
        description="Agente orquestrador MCP",
        log_level="INFO"
    )
    
    orquestrador = OrchestratorAgent(config)
    await orquestrador.initialize()
    
    print("🎭 Orchestrator Agent executando...")
    print("=" * 60)
    
    # Teste 1: Relatório completo
    print("\n📋 Teste 1: Relatório Completo (São Paulo)")
    msg_relatorio = orquestrador.create_message("relatorio_completo", {"cidade": "São Paulo"})
    resposta = await orquestrador.process_message(msg_relatorio)
    
    if resposta.success:
        dados = resposta.data
        print(f"   🏙️ Cidade: {dados['cidade']}")
        print(f"   🌡️ Temperatura: {dados['clima']['atual']['temperatura']}°C")
        print(f"   💰 USD/BRL: {dados['financeiro']['moedas']['USD/BRL']}")
        print(f"   📝 Resumo: {dados['resumo_executivo']}")
        print(f"   💡 Insights: {len(dados['insights'])} gerados")
    
    # Teste 2: Análise de viagem
    print("\n✈️ Teste 2: Análise de Viagem (SP → RJ)")
    msg_viagem = orquestrador.create_message("analise_viagem", {
        "origem": "São Paulo",
        "destino": "Rio de Janeiro"
    })
    resposta = await orquestrador.process_message(msg_viagem)
    
    if resposta.success:
        dados = resposta.data
        print(f"   🏁 Origem: {dados['origem']['cidade']} - {dados['origem']['dados_atuais']['clima']['temperatura']}°C")
        print(f"   🏁 Destino: {dados['destino']['cidade']} - {dados['destino']['dados_atuais']['clima']['temperatura']}°C")
        if dados['recomendacoes']:
            print(f"   💡 Recomendações: {dados['recomendacoes'][0]}")
    
    # Teste 3: Dashboard
    print("\n📊 Teste 3: Dashboard Completo")
    msg_dashboard = orquestrador.create_message("dashboard", {})
    resposta = await orquestrador.process_message(msg_dashboard)
    
    if resposta.success:
        dados = resposta.data
        print(f"   📊 {dados['titulo']}")
        print(f"   🏙️ Cidades monitoradas: {len(dados['clima_cidades'])}")
        print(f"   💰 Cotações: USD/BRL = {dados['mercado_financeiro']['moedas']['USD/BRL']}")
        print(f"   🚨 Alertas: {len(dados['alertas'])}")
        
        # Mostrar um alerta se houver
        if dados['alertas']:
            print(f"   ⚠️ Primeiro alerta: {dados['alertas'][0]}")
    
    # Teste 4: Status dos agentes
    print("\n🔍 Teste 4: Status dos Sub-Agentes")
    msg_status = orquestrador.create_message("status_agentes", {})
    resposta = await orquestrador.process_message(msg_status)
    
    if resposta.success:
        for agent_name, status in resposta.data.items():
            status_icon = "✅" if status['online'] else "❌"
            print(f"   {status_icon} {agent_name}: {status.get('status', 'unknown')}")
    
    await orquestrador.shutdown()
    print("\n✅ Demonstração do Orchestrator Agent concluída!")

if __name__ == "__main__":
    asyncio.run(main())