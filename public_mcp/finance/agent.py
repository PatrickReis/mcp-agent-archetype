"""
Agente MCP para consulta de cotações financeiras
Utiliza APIs públicas para dados financeiros
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from src.mcp_agent.base_agent import BaseMCPAgent, AgentConfig, MCPMessage

class FinanceAgent(BaseMCPAgent):
    """Agente para consulta de dados financeiros"""
    
    def __init__(self, config: AgentConfig, api_key: Optional[str] = None):
        super().__init__(config)
        self.api_key = api_key
        # APIs públicas gratuitas
        self.exchange_rate_api = "https://api.exchangerate-api.com/v4/latest"
        self.crypto_api = "https://api.coingecko.com/api/v3"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _custom_initialize(self):
        """Inicialização do agente financeiro"""
        self.logger.info("💰 Agente Financeiro inicializando...")
        self.session = aiohttp.ClientSession()
        
        # Cache simples para evitar muitas chamadas
        self.cache = {}
        self.cache_timeout = 300  # 5 minutos
        
        await asyncio.sleep(0.1)
    
    async def _process_custom_message(self, message: MCPMessage) -> Any:
        """Processamento de mensagens do agente financeiro"""
        message_type = message.message_type.lower()
        
        if message_type == "cotacao_moeda":
            base = message.payload.get("base", "USD")
            target = message.payload.get("target", "BRL")
            return await self._get_exchange_rate(base, target)
            
        elif message_type == "cotacao_crypto":
            crypto = message.payload.get("crypto", "bitcoin")
            currency = message.payload.get("currency", "brl")
            return await self._get_crypto_price(crypto, currency)
            
        elif message_type == "multiplas_moedas":
            base = message.payload.get("base", "USD")
            targets = message.payload.get("targets", ["BRL", "EUR", "GBP"])
            return await self._get_multiple_exchange_rates(base, targets)
            
        elif message_type == "top_cryptos":
            limit = message.payload.get("limit", 10)
            currency = message.payload.get("currency", "brl")
            return await self._get_top_cryptos(limit, currency)
            
        elif message_type == "resumo_mercado":
            return await self._get_market_summary()
            
        elif message_type == "ping":
            return {"response": "pong", "agent": "finance", "status": "online"}
            
        else:
            raise ValueError(f"Tipo de mensagem não suportado: {message_type}")
    
    async def _get_exchange_rate(self, base: str, target: str) -> Dict[str, Any]:
        """Obtém cotação entre duas moedas"""
        cache_key = f"exchange_{base}_{target}"
        
        # Verificar cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            if self.session:
                url = f"{self.exchange_rate_api}/{base}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if target.upper() in data["rates"]:
                            result = {
                                "par": f"{base}/{target}",
                                "taxa": data["rates"][target.upper()],
                                "base": base.upper(),
                                "target": target.upper(),
                                "timestamp": data["time_last_updated"],
                                "fonte": "ExchangeRate-API"
                            }
                            
                            # Cache do resultado
                            self._cache_data(cache_key, result)
                            return result
                        else:
                            return self._get_simulated_exchange_rate(base, target)
                    else:
                        return self._get_simulated_exchange_rate(base, target)
        except Exception as e:
            self.logger.error(f"Erro ao obter cotação {base}/{target}: {e}")
            return self._get_simulated_exchange_rate(base, target)
    
    async def _get_crypto_price(self, crypto: str, currency: str = "brl") -> Dict[str, Any]:
        """Obtém preço de criptomoeda"""
        cache_key = f"crypto_{crypto}_{currency}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            if self.session:
                url = f"{self.crypto_api}/simple/price"
                params = {
                    "ids": crypto.lower(),
                    "vs_currencies": currency.lower(),
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true"
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if crypto.lower() in data:
                            crypto_data = data[crypto.lower()]
                            result = {
                                "crypto": crypto.upper(),
                                "moeda": currency.upper(),
                                "preco": crypto_data[currency.lower()],
                                "variacao_24h": crypto_data.get(f"{currency.lower()}_24h_change", 0),
                                "volume_24h": crypto_data.get(f"{currency.lower()}_24h_vol", 0),
                                "timestamp": int(datetime.now().timestamp()),
                                "fonte": "CoinGecko"
                            }
                            
                            self._cache_data(cache_key, result)
                            return result
                        else:
                            return self._get_simulated_crypto_price(crypto, currency)
                    else:
                        return self._get_simulated_crypto_price(crypto, currency)
        except Exception as e:
            self.logger.error(f"Erro ao obter preço de {crypto}: {e}")
            return self._get_simulated_crypto_price(crypto, currency)
    
    async def _get_multiple_exchange_rates(self, base: str, targets: List[str]) -> Dict[str, Any]:
        """Obtém múltiplas cotações"""
        resultados = {}
        
        for target in targets:
            try:
                cotacao = await self._get_exchange_rate(base, target)
                resultados[target] = cotacao
                await asyncio.sleep(0.1)  # Evitar rate limiting
            except Exception as e:
                self.logger.error(f"Erro ao obter {base}/{target}: {e}")
                resultados[target] = {"erro": str(e)}
        
        return {
            "base": base.upper(),
            "cotacoes": resultados,
            "total_consultadas": len(targets),
            "timestamp": int(datetime.now().timestamp())
        }
    
    async def _get_top_cryptos(self, limit: int, currency: str) -> Dict[str, Any]:
        """Obtém top criptomoedas por market cap"""
        cache_key = f"top_cryptos_{limit}_{currency}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            if self.session:
                url = f"{self.crypto_api}/coins/markets"
                params = {
                    "vs_currency": currency.lower(),
                    "order": "market_cap_desc",
                    "per_page": limit,
                    "page": 1,
                    "sparkline": "false"
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        cryptos = []
                        for crypto in data:
                            cryptos.append({
                                "rank": crypto["market_cap_rank"],
                                "nome": crypto["name"],
                                "simbolo": crypto["symbol"].upper(),
                                "preco": crypto["current_price"],
                                "market_cap": crypto["market_cap"],
                                "variacao_24h": crypto["price_change_percentage_24h"],
                                "volume_24h": crypto["total_volume"]
                            })
                        
                        result = {
                            "top_cryptos": cryptos,
                            "moeda": currency.upper(),
                            "limite": limit,
                            "timestamp": int(datetime.now().timestamp()),
                            "fonte": "CoinGecko"
                        }
                        
                        self._cache_data(cache_key, result)
                        return result
                    else:
                        return self._get_simulated_top_cryptos(limit, currency)
        except Exception as e:
            self.logger.error(f"Erro ao obter top cryptos: {e}")
            return self._get_simulated_top_cryptos(limit, currency)
    
    async def _get_market_summary(self) -> Dict[str, Any]:
        """Obtém resumo do mercado"""
        try:
            # Obter algumas cotações principais
            usd_brl = await self._get_exchange_rate("USD", "BRL")
            eur_brl = await self._get_exchange_rate("EUR", "BRL")
            btc_brl = await self._get_crypto_price("bitcoin", "brl")
            eth_brl = await self._get_crypto_price("ethereum", "brl")
            
            return {
                "moedas": {
                    "USD/BRL": usd_brl["taxa"],
                    "EUR/BRL": eur_brl["taxa"]
                },
                "cryptos": {
                    "Bitcoin": {
                        "preco": btc_brl["preco"],
                        "variacao_24h": btc_brl["variacao_24h"]
                    },
                    "Ethereum": {
                        "preco": eth_brl["preco"],
                        "variacao_24h": eth_brl["variacao_24h"]
                    }
                },
                "timestamp": int(datetime.now().timestamp()),
                "resumo_gerado_em": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo do mercado: {e}")
            return self._get_simulated_market_summary()
    
    def _get_simulated_exchange_rate(self, base: str, target: str) -> Dict[str, Any]:
        """Cotação simulada"""
        import random
        
        # Taxas base simuladas
        rates = {
            "USD_BRL": 5.20,
            "EUR_BRL": 5.80,
            "GBP_BRL": 6.50,
            "USD_EUR": 0.90,
            "USD_GBP": 0.80
        }
        
        key = f"{base}_{target}"
        reverse_key = f"{target}_{base}"
        
        if key in rates:
            base_rate = rates[key]
        elif reverse_key in rates:
            base_rate = 1 / rates[reverse_key]
        else:
            base_rate = random.uniform(0.5, 10.0)
        
        # Adicionar variação
        variation = random.uniform(-0.05, 0.05)
        final_rate = base_rate * (1 + variation)
        
        return {
            "par": f"{base}/{target}",
            "taxa": round(final_rate, 4),
            "base": base.upper(),
            "target": target.upper(),
            "timestamp": int(datetime.now().timestamp()),
            "fonte": "Dados Simulados"
        }
    
    def _get_simulated_crypto_price(self, crypto: str, currency: str) -> Dict[str, Any]:
        """Preço de crypto simulado"""
        import random
        
        # Preços base simulados (em BRL)
        base_prices = {
            "bitcoin": 200000,
            "ethereum": 12000,
            "cardano": 2.5,
            "solana": 150,
            "dogecoin": 0.40
        }
        
        base_price = base_prices.get(crypto.lower(), random.uniform(1, 1000))
        variation = random.uniform(-10, 10)
        
        return {
            "crypto": crypto.upper(),
            "moeda": currency.upper(),
            "preco": round(base_price * (1 + variation/100), 2),
            "variacao_24h": round(variation, 2),
            "volume_24h": random.randint(1000000, 50000000),
            "timestamp": int(datetime.now().timestamp()),
            "fonte": "Dados Simulados"
        }
    
    def _get_simulated_top_cryptos(self, limit: int, currency: str) -> Dict[str, Any]:
        """Top cryptos simulado"""
        import random
        
        cryptos_populares = [
            "Bitcoin", "Ethereum", "Cardano", "Solana", "Dogecoin",
            "Polkadot", "Chainlink", "Litecoin", "XRP", "Polygon"
        ]
        
        cryptos = []
        for i, crypto in enumerate(cryptos_populares[:limit]):
            price = random.uniform(0.1, 300000)
            cryptos.append({
                "rank": i + 1,
                "nome": crypto,
                "simbolo": crypto[:3].upper(),
                "preco": round(price, 2),
                "market_cap": random.randint(1000000000, 1000000000000),
                "variacao_24h": round(random.uniform(-15, 15), 2),
                "volume_24h": random.randint(100000000, 10000000000)
            })
        
        return {
            "top_cryptos": cryptos,
            "moeda": currency.upper(),
            "limite": limit,
            "timestamp": int(datetime.now().timestamp()),
            "fonte": "Dados Simulados"
        }
    
    def _get_simulated_market_summary(self) -> Dict[str, Any]:
        """Resumo simulado"""
        import random
        
        return {
            "moedas": {
                "USD/BRL": round(random.uniform(5.0, 5.5), 4),
                "EUR/BRL": round(random.uniform(5.5, 6.0), 4)
            },
            "cryptos": {
                "Bitcoin": {
                    "preco": round(random.uniform(180000, 220000), 2),
                    "variacao_24h": round(random.uniform(-5, 5), 2)
                },
                "Ethereum": {
                    "preco": round(random.uniform(10000, 14000), 2),
                    "variacao_24h": round(random.uniform(-8, 8), 2)
                }
            },
            "timestamp": int(datetime.now().timestamp()),
            "resumo_gerado_em": datetime.now().isoformat(),
            "fonte": "Dados Simulados"
        }
    
    def _cache_data(self, key: str, data: Dict[str, Any]):
        """Cache simples"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now().timestamp()
        }
    
    def _is_cache_valid(self, key: str) -> bool:
        """Verifica se cache ainda é válido"""
        if key not in self.cache:
            return False
        
        age = datetime.now().timestamp() - self.cache[key]["timestamp"]
        return age < self.cache_timeout
    
    async def shutdown(self):
        """Finalização do agente"""
        if self.session:
            await self.session.close()
        self.logger.info("💰 Agente Financeiro finalizado")

# Exemplo de uso
async def main():
    """Demonstração do agente financeiro"""
    config = AgentConfig(
        agent_id="finance_001",
        agent_name="Finance Agent",
        version="1.0.0",
        description="Agente para consulta de dados financeiros",
        log_level="INFO"
    )
    
    agente = FinanceAgent(config)
    await agente.initialize()
    
    print("💰 Finance Agent executando...")
    print("=" * 50)
    
    # Teste 1: Cotação USD/BRL
    print("\n💵 Teste 1: Cotação USD/BRL")
    msg_cotacao = agente.create_message("cotacao_moeda", {"base": "USD", "target": "BRL"})
    resposta = await agente.process_message(msg_cotacao)
    print(f"   💱 USD/BRL: {resposta.data['taxa']}")
    
    # Teste 2: Preço Bitcoin
    print("\n₿ Teste 2: Preço do Bitcoin")
    msg_btc = agente.create_message("cotacao_crypto", {"crypto": "bitcoin", "currency": "brl"})
    resposta = await agente.process_message(msg_btc)
    print(f"   ₿ Bitcoin: R$ {resposta.data['preco']:,.2f}")
    print(f"   📈 Variação 24h: {resposta.data['variacao_24h']:.2f}%")
    
    # Teste 3: Múltiplas moedas
    print("\n🌍 Teste 3: Múltiplas cotações")
    moedas = ["BRL", "EUR", "GBP", "JPY"]
    msg_multiplas = agente.create_message("multiplas_moedas", {"base": "USD", "targets": moedas})
    resposta = await agente.process_message(msg_multiplas)
    for moeda, dados in resposta.data['cotacoes'].items():
        if 'taxa' in dados:
            print(f"   USD/{moeda}: {dados['taxa']}")
    
    # Teste 4: Top cryptos
    print("\n🏆 Teste 4: Top 5 Criptomoedas")
    msg_top = agente.create_message("top_cryptos", {"limit": 5, "currency": "brl"})
    resposta = await agente.process_message(msg_top)
    for crypto in resposta.data['top_cryptos']:
        print(f"   #{crypto['rank']} {crypto['nome']} ({crypto['simbolo']}): R$ {crypto['preco']:,.2f}")
    
    # Teste 5: Resumo do mercado
    print("\n📊 Teste 5: Resumo do Mercado")
    msg_resumo = agente.create_message("resumo_mercado", {})
    resposta = await agente.process_message(msg_resumo)
    print("   Moedas:")
    for par, taxa in resposta.data['moedas'].items():
        print(f"     {par}: {taxa}")
    print("   Cryptos:")
    for crypto, dados in resposta.data['cryptos'].items():
        print(f"     {crypto}: R$ {dados['preco']:,.2f} ({dados['variacao_24h']:+.2f}%)")
    
    await agente.shutdown()
    print("\n✅ Demonstração do Finance Agent concluída!")

if __name__ == "__main__":
    asyncio.run(main())