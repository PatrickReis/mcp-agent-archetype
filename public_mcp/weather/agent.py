"""
Agente MCP para consulta de dados climáticos
Utiliza API pública do OpenWeatherMap
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from src.mcp_agent.base_agent import BaseMCPAgent, AgentConfig, MCPMessage

class WeatherAgent(BaseMCPAgent):
    """Agente para consulta de dados climáticos"""
    
    def __init__(self, config: AgentConfig, api_key: Optional[str] = None):
        super().__init__(config)
        # Para demonstração, usaremos dados simulados se não houver API key
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _custom_initialize(self):
        """Inicialização do agente de clima"""
        self.logger.info("🌤️ Agente de Clima inicializando...")
        self.session = aiohttp.ClientSession()
        
        if not self.api_key:
            self.logger.warning("⚠️ Nenhuma API key fornecida, usando dados simulados")
        else:
            self.logger.info("✅ API key configurada, usando dados reais")
            
        await asyncio.sleep(0.1)
    
    async def _process_custom_message(self, message: MCPMessage) -> Any:
        """Processamento de mensagens do agente de clima"""
        message_type = message.message_type.lower()
        
        if message_type == "clima_atual":
            cidade = message.payload.get("cidade", "São Paulo")
            return await self._get_current_weather(cidade)
            
        elif message_type == "previsao":
            cidade = message.payload.get("cidade", "São Paulo")
            dias = message.payload.get("dias", 5)
            return await self._get_forecast(cidade, dias)
            
        elif message_type == "clima_multiplas_cidades":
            cidades = message.payload.get("cidades", ["São Paulo", "Rio de Janeiro"])
            return await self._get_multiple_cities_weather(cidades)
            
        elif message_type == "ping":
            return {"response": "pong", "agent": "weather", "status": "online"}
            
        else:
            raise ValueError(f"Tipo de mensagem não suportado: {message_type}")
    
    async def _get_current_weather(self, cidade: str) -> Dict[str, Any]:
        """Obtém clima atual de uma cidade"""
        if self.api_key and self.session:
            try:
                url = f"{self.base_url}/weather"
                params = {
                    "q": cidade,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "pt_br"
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_current_weather(data)
                    else:
                        self.logger.error(f"Erro na API: {response.status}")
                        return self._get_simulated_weather(cidade)
                        
            except Exception as e:
                self.logger.error(f"Erro ao consultar API: {e}")
                return self._get_simulated_weather(cidade)
        else:
            return self._get_simulated_weather(cidade)
    
    async def _get_forecast(self, cidade: str, dias: int) -> Dict[str, Any]:
        """Obtém previsão do tempo"""
        if self.api_key and self.session:
            try:
                url = f"{self.base_url}/forecast"
                params = {
                    "q": cidade,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "pt_br",
                    "cnt": dias * 8  # 8 previsões por dia (3h intervalo)
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_forecast(data, dias)
                    else:
                        return self._get_simulated_forecast(cidade, dias)
                        
            except Exception as e:
                self.logger.error(f"Erro ao consultar previsão: {e}")
                return self._get_simulated_forecast(cidade, dias)
        else:
            return self._get_simulated_forecast(cidade, dias)
    
    async def _get_multiple_cities_weather(self, cidades: list) -> Dict[str, Any]:
        """Obtém clima de múltiplas cidades"""
        resultados = {}
        
        for cidade in cidades:
            try:
                clima = await self._get_current_weather(cidade)
                resultados[cidade] = clima
                # Pequena pausa para não sobrecarregar a API
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Erro ao obter clima de {cidade}: {e}")
                resultados[cidade] = {"erro": str(e)}
        
        return {
            "cidades": resultados,
            "total_consultadas": len(cidades),
            "timestamp": message.timestamp.isoformat() if hasattr(message, 'timestamp') else None
        }
    
    def _format_current_weather(self, data: Dict) -> Dict[str, Any]:
        """Formata dados da API real"""
        return {
            "cidade": data["name"],
            "pais": data["sys"]["country"],
            "temperatura": round(data["main"]["temp"], 1),
            "sensacao_termica": round(data["main"]["feels_like"], 1),
            "humidade": data["main"]["humidity"],
            "pressao": data["main"]["pressure"],
            "descricao": data["weather"][0]["description"],
            "vento_velocidade": data["wind"]["speed"],
            "vento_direcao": data["wind"].get("deg", 0),
            "visibilidade": data.get("visibility", 0) / 1000,  # em km
            "fonte": "OpenWeatherMap",
            "timestamp": data["dt"]
        }
    
    def _get_simulated_weather(self, cidade: str) -> Dict[str, Any]:
        """Dados simulados para demonstração"""
        import random
        from datetime import datetime
        
        # Simular dados baseados na cidade
        base_temp = 20 if "São Paulo" in cidade else 25
        temp_variation = random.uniform(-5, 10)
        
        condicoes = ["ensolarado", "parcialmente nublado", "nublado", "chuvoso", "tempestade"]
        condicao = random.choice(condicoes)
        
        return {
            "cidade": cidade,
            "pais": "BR",
            "temperatura": round(base_temp + temp_variation, 1),
            "sensacao_termica": round(base_temp + temp_variation + random.uniform(-2, 3), 1),
            "humidade": random.randint(40, 90),
            "pressao": random.randint(1010, 1025),
            "descricao": condicao,
            "vento_velocidade": round(random.uniform(0, 15), 1),
            "vento_direcao": random.randint(0, 360),
            "visibilidade": round(random.uniform(5, 20), 1),
            "fonte": "Dados Simulados",
            "timestamp": int(datetime.now().timestamp())
        }
    
    def _format_forecast(self, data: Dict, dias: int) -> Dict[str, Any]:
        """Formata previsão da API real"""
        previsoes = []
        
        for item in data["list"][:dias*8:8]:  # Pegar uma previsão por dia
            previsoes.append({
                "data": item["dt_txt"],
                "temperatura_min": round(item["main"]["temp_min"], 1),
                "temperatura_max": round(item["main"]["temp_max"], 1),
                "descricao": item["weather"][0]["description"],
                "humidade": item["main"]["humidity"],
                "probabilidade_chuva": item.get("pop", 0) * 100
            })
        
        return {
            "cidade": data["city"]["name"],
            "pais": data["city"]["country"],
            "previsoes": previsoes,
            "fonte": "OpenWeatherMap"
        }
    
    def _get_simulated_forecast(self, cidade: str, dias: int) -> Dict[str, Any]:
        """Previsão simulada"""
        import random
        from datetime import datetime, timedelta
        
        previsoes = []
        base_temp = 20 if "São Paulo" in cidade else 25
        
        for i in range(dias):
            data_previsao = datetime.now() + timedelta(days=i)
            temp_var = random.uniform(-3, 8)
            
            previsoes.append({
                "data": data_previsao.strftime("%Y-%m-%d"),
                "temperatura_min": round(base_temp + temp_var - 3, 1),
                "temperatura_max": round(base_temp + temp_var + 5, 1),
                "descricao": random.choice(["ensolarado", "nublado", "chuvoso"]),
                "humidade": random.randint(40, 90),
                "probabilidade_chuva": random.randint(0, 80)
            })
        
        return {
            "cidade": cidade,
            "pais": "BR",
            "previsoes": previsoes,
            "fonte": "Dados Simulados"
        }
    
    async def shutdown(self):
        """Finalização do agente"""
        if self.session:
            await self.session.close()
        self.logger.info("🌤️ Agente de Clima finalizado")

# Exemplo de uso
async def main():
    """Demonstração do agente de clima"""
    config = AgentConfig(
        agent_id="weather_001",
        agent_name="Weather Agent",
        version="1.0.0",
        description="Agente para consulta de dados climáticos",
        log_level="INFO"
    )
    
    # Inicializar sem API key (dados simulados)
    agente = WeatherAgent(config)
    await agente.initialize()
    
    print("🌤️ Weather Agent executando...")
    print("=" * 50)
    
    # Teste 1: Clima atual
    print("\n📍 Teste 1: Clima atual em São Paulo")
    msg_clima = agente.create_message("clima_atual", {"cidade": "São Paulo"})
    resposta = await agente.process_message(msg_clima)
    print(f"   🌡️ Temperatura: {resposta.data['temperatura']}°C")
    print(f"   📊 Condição: {resposta.data['descricao']}")
    print(f"   💧 Umidade: {resposta.data['humidade']}%")
    
    # Teste 2: Previsão
    print("\n📅 Teste 2: Previsão para 3 dias")
    msg_previsao = agente.create_message("previsao", {"cidade": "Rio de Janeiro", "dias": 3})
    resposta = await agente.process_message(msg_previsao)
    print(f"   📍 Cidade: {resposta.data['cidade']}")
    for i, prev in enumerate(resposta.data['previsoes']):
        print(f"   Dia {i+1}: {prev['temperatura_min']}°C - {prev['temperatura_max']}°C ({prev['descricao']})")
    
    # Teste 3: Múltiplas cidades
    print("\n🌍 Teste 3: Clima em múltiplas cidades")
    cidades = ["São Paulo", "Rio de Janeiro", "Brasília"]
    msg_multiplas = agente.create_message("clima_multiplas_cidades", {"cidades": cidades})
    resposta = await agente.process_message(msg_multiplas)
    for cidade, dados in resposta.data['cidades'].items():
        if 'temperatura' in dados:
            print(f"   {cidade}: {dados['temperatura']}°C - {dados['descricao']}")
    
    await agente.shutdown()
    print("\n✅ Demonstração do Weather Agent concluída!")

if __name__ == "__main__":
    asyncio.run(main())