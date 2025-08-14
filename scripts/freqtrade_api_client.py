#!/usr/bin/env python3
"""
Freqtrade API Client - Cliente para conectar com APIs das estratégias
Permite controle real das estratégias via REST API
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class FreqtradeAPIClient:
    """Cliente para comunicação com APIs do Freqtrade"""
    
    def __init__(self):
        # Configuração das estratégias e suas APIs
        self.strategies = {
            "stratA": {
                "name": "Strategy A",
                "container": "ft-stratA",
                "api_url": "http://127.0.0.1:8081",
                "username": "stratA",
                "password": "stratA123"
            },
            "stratB": {
                "name": "Strategy B", 
                "container": "ft-stratB",
                "api_url": "http://127.0.0.1:8082",
                "username": "stratB",
                "password": "stratB123"
            },
            "waveHyperNW": {
                "name": "WaveHyperNW Strategy",
                "container": "ft-waveHyperNW",
                "api_url": "http://127.0.0.1:8083",
                "username": "waveHyperNW",
                "password": "waveHyperNW123"
            },
            "mlStrategy": {
                "name": "ML Strategy",
                "container": "ft-mlStrategy",
                "api_url": "http://127.0.0.1:8084",
                "username": "mlStrategy",
                "password": "mlStrategy123"
            },
            "mlStrategySimple": {
                "name": "ML Strategy Simple",
                "container": "ft-mlStrategySimple",
                "api_url": "http://127.0.0.1:8085",
                "username": "mlStrategySimple",
                "password": "mlStrategySimple123"
            },
            "multiTimeframe": {
                "name": "Multi Timeframe Strategy",
                "container": "ft-multiTimeframe",
                "api_url": "http://127.0.0.1:8086",
                "username": "multiTimeframe",
                "password": "multiTimeframe123"
            },
            "waveHyperNWEnhanced": {
                "name": "WaveHyperNW Enhanced",
                "container": "ft-waveHyperNWEnhanced",
                "api_url": "http://127.0.0.1:8087",
                "username": "waveHyperNWEnhanced",
                "password": "waveHyperNWEnhanced123"
            }
        }
        
        # Cache de tokens de autenticação
        self._auth_tokens = {}
    
    def _get_auth_token(self, strategy_id: str) -> Optional[str]:
        """Obter token de autenticação para uma estratégia"""
        if strategy_id not in self.strategies:
            return None
        
        # Verificar se já temos token em cache
        if strategy_id in self._auth_tokens:
            return self._auth_tokens[strategy_id]
        
        strategy = self.strategies[strategy_id]
        
        try:
            # Fazer login na API
            auth_data = {
                "username": strategy["username"],
                "password": strategy["password"]
            }
            
            response = requests.post(
                f"{strategy['api_url']}/api/v1/token/login",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                self._auth_tokens[strategy_id] = token
                logger.info(f"✅ Token obtido para {strategy_id}")
                return token
            else:
                logger.error(f"❌ Erro ao obter token para {strategy_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro de conexão com {strategy_id}: {e}")
            return None
    
    def _make_api_request(self, strategy_id: str, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Fazer requisição para API de uma estratégia"""
        token = self._get_auth_token(strategy_id)
        if not token:
            return None
        
        strategy = self.strategies[strategy_id]
        url = f"{strategy['api_url']}/api/v1{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Erro na API {strategy_id}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro de requisição para {strategy_id}: {e}")
            return None
    
    def get_strategy_status(self, strategy_id: str) -> Dict:
        """Obter status de uma estratégia"""
        result = self._make_api_request(strategy_id, "/status")
        
        if result:
            return {
                "success": True,
                "strategy_id": strategy_id,
                "name": self.strategies[strategy_id]["name"],
                "state": result.get("state", "unknown"),
                "trade_count": result.get("trade_count", 0),
                "best_pair": result.get("best_pair", "N/A"),
                "profit_closed_coin": result.get("profit_closed_coin", 0),
                "profit_closed_percent": result.get("profit_closed_percent", 0),
                "profit_all_coin": result.get("profit_all_coin", 0),
                "profit_all_percent": result.get("profit_all_percent", 0)
            }
        else:
            return {
                "success": False,
                "strategy_id": strategy_id,
                "name": self.strategies[strategy_id]["name"],
                "error": "API não disponível"
            }
    
    def get_open_trades(self, strategy_id: str) -> List[Dict]:
        """Obter trades abertos de uma estratégia"""
        result = self._make_api_request(strategy_id, "/trades")
        
        if result and isinstance(result, list):
            return result
        else:
            return []
    
    def force_buy(self, strategy_id: str, pair: str, price: Optional[float] = None) -> Dict:
        """Executar compra forçada"""
        data = {"pair": pair}
        if price:
            data["price"] = price
        
        result = self._make_api_request(strategy_id, "/forcebuy", "POST", data)
        
        if result:
            return {
                "success": True,
                "strategy_id": strategy_id,
                "pair": pair,
                "trade_id": result.get("trade_id"),
                "message": f"Compra forçada executada para {pair}"
            }
        else:
            return {
                "success": False,
                "strategy_id": strategy_id,
                "pair": pair,
                "error": "Falha ao executar compra forçada"
            }
    
    def force_sell(self, strategy_id: str, trade_id: str, amount: Optional[float] = None) -> Dict:
        """Executar venda forçada"""
        data = {"tradeid": trade_id}
        if amount:
            data["amount"] = amount
        
        result = self._make_api_request(strategy_id, "/forcesell", "POST", data)
        
        if result:
            return {
                "success": True,
                "strategy_id": strategy_id,
                "trade_id": trade_id,
                "message": f"Venda forçada executada para trade {trade_id}"
            }
        else:
            return {
                "success": False,
                "strategy_id": strategy_id,
                "trade_id": trade_id,
                "error": "Falha ao executar venda forçada"
            }
    
    def force_sell_all(self, strategy_id: str) -> Dict:
        """Vender todas as posições de uma estratégia"""
        trades = self.get_open_trades(strategy_id)
        
        if not trades:
            return {
                "success": False,
                "strategy_id": strategy_id,
                "error": "Nenhuma posição aberta encontrada"
            }
        
        results = []
        for trade in trades:
            trade_id = str(trade.get("trade_id", ""))
            if trade_id:
                result = self.force_sell(strategy_id, trade_id)
                results.append(result)
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "success": success_count > 0,
            "strategy_id": strategy_id,
            "total_trades": len(trades),
            "successful_sells": success_count,
            "message": f"Vendidas {success_count}/{len(trades)} posições"
        }
    
    def get_profit_stats(self, strategy_id: str) -> Dict:
        """Obter estatísticas de lucro"""
        result = self._make_api_request(strategy_id, "/profit")
        
        if result:
            return {
                "success": True,
                "strategy_id": strategy_id,
                "profit_closed_coin": result.get("profit_closed_coin", 0),
                "profit_closed_percent": result.get("profit_closed_percent", 0),
                "profit_all_coin": result.get("profit_all_coin", 0),
                "profit_all_percent": result.get("profit_all_percent", 0),
                "trade_count": result.get("trade_count", 0),
                "first_trade_date": result.get("first_trade_date"),
                "latest_trade_date": result.get("latest_trade_date"),
                "avg_duration": result.get("avg_duration"),
                "best_pair": result.get("best_pair"),
                "best_rate": result.get("best_rate")
            }
        else:
            return {
                "success": False,
                "strategy_id": strategy_id,
                "error": "Não foi possível obter estatísticas"
            }
    
    def get_balance(self, strategy_id: str) -> Dict:
        """Obter saldo da estratégia"""
        result = self._make_api_request(strategy_id, "/balance")
        
        if result:
            return {
                "success": True,
                "strategy_id": strategy_id,
                "currencies": result.get("currencies", []),
                "total": result.get("total", 0),
                "symbol": result.get("symbol", "USDT"),
                "value": result.get("value", 0)
            }
        else:
            return {
                "success": False,
                "strategy_id": strategy_id,
                "error": "Não foi possível obter saldo"
            }
    
    def get_performance(self, strategy_id: str) -> List[Dict]:
        """Obter performance por par"""
        result = self._make_api_request(strategy_id, "/performance")
        
        if result and isinstance(result, list):
            return result
        else:
            return []
    
    def reload_config(self, strategy_id: str) -> Dict:
        """Recarregar configuração da estratégia"""
        result = self._make_api_request(strategy_id, "/reload_config", "POST")
        
        if result:
            return {
                "success": True,
                "strategy_id": strategy_id,
                "message": "Configuração recarregada com sucesso"
            }
        else:
            return {
                "success": False,
                "strategy_id": strategy_id,
                "error": "Falha ao recarregar configuração"
            }
    
    def get_all_strategies_status(self) -> Dict:
        """Obter status de todas as estratégias"""
        results = {}
        
        for strategy_id in self.strategies.keys():
            results[strategy_id] = self.get_strategy_status(strategy_id)
        
        return results
    
    def test_connections(self) -> Dict:
        """Testar conexão com todas as APIs"""
        results = {}
        
        for strategy_id in self.strategies.keys():
            try:
                token = self._get_auth_token(strategy_id)
                results[strategy_id] = {
                    "connected": token is not None,
                    "name": self.strategies[strategy_id]["name"],
                    "api_url": self.strategies[strategy_id]["api_url"]
                }
            except Exception as e:
                results[strategy_id] = {
                    "connected": False,
                    "name": self.strategies[strategy_id]["name"],
                    "api_url": self.strategies[strategy_id]["api_url"],
                    "error": str(e)
                }
        
        return results

# Instância global do cliente
api_client = FreqtradeAPIClient()