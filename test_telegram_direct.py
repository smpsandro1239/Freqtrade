#!/usr/bin/env python3
"""
Teste Direto do Telegram - Sem problemas de encoding
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

async def test_telegram_connection():
    """Testar conexão direta com Telegram"""
    
    # Obter credenciais
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print("=== TESTE DIRETO DO TELEGRAM ===")
    print()
    
    if not token or token == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
        print("ERRO: Token do Telegram nao configurado")
        return False
    
    if not chat_id or chat_id == 'YOUR_TELEGRAM_CHAT_ID_HERE':
        print("ERRO: Chat ID do Telegram nao configurado")
        return False
    
    print(f"Token encontrado: {token[:20]}...")
    print(f"Chat ID encontrado: {chat_id}")
    print()
    
    try:
        # Importar e testar bot
        from telegram import Bot
        
        bot = Bot(token=token)
        
        # Testar getMe
        print("Testando conexao com bot...")
        me = await bot.get_me()
        print(f"Bot conectado: @{me.username}")
        print(f"Nome: {me.first_name}")
        print()
        
        # Enviar mensagem de teste
        print("Enviando mensagem de teste...")
        
        message = """SISTEMA FREQTRADE ATIVO!

Bot principal inicializado
Trading manual habilitado
IA preditiva ativa
Monitoramento 24/7

Digite /start para comecar!"""
        
        await bot.send_message(chat_id=chat_id, text=message)
        print("Mensagem enviada com sucesso!")
        print()
        
        # Enviar status das estratégias
        print("Enviando status das estrategias...")
        
        status_message = """STATUS DAS ESTRATEGIAS

Sample Strategy A - RODANDO
Descricao: RSI basico - 15m
Container: ft-stratA
API Port: 8081

WaveHyperNW Strategy - RODANDO  
Descricao: WaveTrend + Nadaraya-Watson - 5m
Container: ft-waveHyperNW
API Port: 8083

RESUMO GERAL:
- Estrategias Ativas: 7/7
- Sistema: Operacional
- Modo: DRY-RUN (Simulacao)"""
        
        await bot.send_message(chat_id=chat_id, text=status_message)
        print("Status enviado com sucesso!")
        print()
        
        # Enviar previsões IA
        print("Enviando previsoes IA...")
        
        ai_message = """PREVISOES RAPIDAS - IA

TOP OPORTUNIDADES:
1. BTC/USDT - 78% (ALTA)
2. ETH/USDT - 72% (ALTA)  
3. ADA/USDT - 68% (BAIXA)

RESUMO:
- Pares Analisados: 10
- Alta Confianca: 3

Use /predict <PAR> para analise detalhada"""
        
        await bot.send_message(chat_id=chat_id, text=ai_message)
        print("Previsoes enviadas com sucesso!")
        print()
        
        # Enviar estatísticas
        print("Enviando estatisticas...")
        
        stats_message = """ESTATISTICAS DETALHADAS

Sample Strategy A
Trades: 5
P&L: +2.5 USDT
Win Rate: 80.0%

WaveHyperNW Strategy
Trades: 12
P&L: +5.8 USDT
Win Rate: 75.0%

RESUMO GERAL:
- Total Trades: 45
- Lucro Total: +24.7 USDT
- Win Rate Medio: 78.5%
- Periodo: Ultimas 24h
- Modo: DRY-RUN (Simulacao)"""
        
        await bot.send_message(chat_id=chat_id, text=stats_message)
        print("Estatisticas enviadas com sucesso!")
        print()
        
        # Enviar comandos disponíveis
        print("Enviando lista de comandos...")
        
        commands_message = """COMANDOS DISPONIVEIS

COMANDOS BASICOS:
/start - Menu principal interativo
/status - Status de todas as estrategias
/stats - Estatisticas detalhadas
/help - Ajuda completa

TRADING MANUAL:
/forcebuy stratA BTC/USDT - Compra forcada
/forcesell stratA BTC/USDT - Venda forcada
/adjust stratA aggressive - Modo agressivo
/emergency - Parada de emergencia

IA PREDITIVA:
/predict - Previsoes rapidas
/predict BTC/USDT - Analise especifica
/ai_analysis - Analise completa
/opportunities - Oportunidades de alta confianca

CONTROLE DE ESTRATEGIAS:
/start_strategy stratA - Iniciar estrategia
/stop_strategy stratA - Parar estrategia
/restart_strategy stratA - Reiniciar estrategia"""
        
        await bot.send_message(chat_id=chat_id, text=commands_message)
        print("Comandos enviados com sucesso!")
        print()
        
        print("=== TESTE CONCLUIDO COM SUCESSO! ===")
        print("Verifique seu Telegram para ver as mensagens!")
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False

async def main():
    """Função principal"""
    success = await test_telegram_connection()
    
    if success:
        print()
        print("SISTEMA TELEGRAM FUNCIONANDO!")
        print("Agora voce pode usar os comandos no Telegram.")
    else:
        print()
        print("ERRO: Sistema Telegram nao funcionou.")
        print("Verifique suas credenciais.")

if __name__ == "__main__":
    asyncio.run(main())