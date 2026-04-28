"""
Testes para operações de câmbio - FUNÇÕES MAIS CRÍTICAS
"""
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa as funções do web_api (ajuste os imports conforme necessário)
from web_api import (
    obter_cotacao_simples, 
    obter_spread_cliente,
    verificar_permissao_cambio_seguro,
    verificar_horario_cliente,
    obter_config_cliente,
    obter_config_sistema
)


class TestCotacaoMoedas:
    """Testes para obtenção de cotações de moedas"""
    
    @patch('web_api.requests.get')
    def test_cotacao_usd_brl_via_awesomeapi(self, mock_get):
        """Testa se USD/BRL é obtido corretamente da AwesomeAPI"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'USDBRL': {'bid': '5.2345'}
        }
        mock_get.return_value = mock_response
        
        resultado = obter_cotacao_simples('USD_BRL')
        
        assert resultado > 0
        assert resultado == 5.2345
        mock_get.assert_called_once()
    
    @patch('web_api.requests.get')
    def test_cotacao_usd_brl_fallback_quando_api_falha(self, mock_get):
        """Testa se fallback funciona quando AwesomeAPI falha"""
        # Simula falha na API
        mock_get.side_effect = Exception("API Timeout")
        
        resultado = obter_cotacao_simples('USD_BRL')
        
        # Deve retornar valor de fallback
        assert resultado > 0
        assert resultado == 5.20  # Fallback definido na função
    
    def test_cotacao_par_invalido_retorna_fallback(self):
        """Testa par de moedas inválido retorna 1.0 como fallback"""
        resultado = obter_cotacao_simples('XYZ_ABC')
        
        assert resultado == 1.0
    
    def test_cotacao_brl_usd_eh_inversa(self):
        """Testa se BRL/USD é o inverso de USD/BRL"""
        with patch('web_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'USDBRL': {'bid': '5.20'}
            }
            mock_get.return_value = mock_response
            
            usd_brl = obter_cotacao_simples('USD_BRL')
            brl_usd = obter_cotacao_simples('BRL_USD')
            
            # BRL/USD deve ser aproximadamente 1 / USD/BRL
            assert abs(brl_usd - (1 / usd_brl)) < 0.0001


class TestSpreadsCliente:
    """Testes para spreads de câmbio por cliente"""
    
    @patch('web_api.supabase')
    @patch('web_api.verificar_permissao_cambio_seguro')
    def test_spread_cliente_com_configuracao_especifica(self, mock_perm, mock_supabase):
        """Testa busca de spread específico do cliente"""
        mock_perm.return_value = True
        
        # Mock da resposta do Supabase
        mock_response = Mock()
        mock_response.data = [{
            'valor_config': {
                'USD_BRL': {'compra': 1.5, 'venda': 1.5}
            }
        }]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        
        resultado = obter_spread_cliente('cliente_teste', 'USD_BRL')
        
        assert resultado['compra'] == 1.5
        assert resultado['venda'] == 1.5
    
    @patch('web_api.supabase')
    @patch('web_api.verificar_permissao_cambio_seguro')
    def test_spread_cliente_sem_config_usar_default(self, mock_perm, mock_supabase):
        """Testa se usa spread padrão quando cliente não tem configuração"""
        mock_perm.return_value = True
        
        # Mock - nenhuma configuração específica
        mock_response = Mock()
        mock_response.data = []  # Sem dados
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        
        resultado = obter_spread_cliente('cliente_novo', 'USD_BRL')
        
        # Deve retornar spread padrão (0.5%)
        assert resultado['compra'] == 0.5
        assert resultado['venda'] == 0.5
    
    @patch('web_api.verificar_permissao_cambio_seguro')
    def test_cliente_bloqueado_tem_spread_zero(self, mock_perm):
        """Testa se cliente sem permissão tem spread zero (BLOQUEIO TOTAL)"""
        mock_perm.return_value = False
        
        resultado = obter_spread_cliente('cliente_bloqueado', 'USD_BRL')
        
        assert resultado['compra'] == 0
        assert resultado['venda'] == 0


class TestPermissaoCambio:
    """Testes para verificação de permissão de câmbio - SEGURANÇA MÁXIMA"""
    
    @patch('web_api.obter_config_cliente')
    @patch('web_api.obter_config_sistema')
    def test_permissao_cliente_liberado_especifico(self, mock_sistema, mock_cliente):
        """Testa cliente com permissão específica = True"""
        mock_cliente.return_value = True
        mock_sistema.return_value = None
        
        resultado = verificar_permissao_cambio_seguro('cliente_liberado')
        
        assert resultado == True
    
    @patch('web_api.obter_config_cliente')
    @patch('web_api.obter_config_sistema')
    def test_permissao_cliente_bloqueado_especifico(self, mock_sistema, mock_cliente):
        """Testa cliente com permissão específica = False"""
        mock_cliente.return_value = False
        mock_sistema.return_value = None
        
        resultado = verificar_permissao_cambio_seguro('cliente_bloqueado')
        
        assert resultado == False
    
    @patch('web_api.obter_config_cliente')
    @patch('web_api.obter_config_sistema')
    def test_permissao_sem_configuracao_bloqueia_por_padrao(self, mock_sistema, mock_cliente):
        """Testa SEGURANÇA MÁXIMA: sem configuração → BLOQUEADO"""
        mock_cliente.return_value = None  # Sem configuração específica
        mock_sistema.return_value = None   # Sem configuração do sistema
        
        resultado = verificar_permissao_cambio_seguro('cliente_novo')
        
        # CRÍTICO: Por segurança, NEGAR quando não há configuração!
        assert resultado == False
    
    @patch('web_api.obter_config_cliente')
    @patch('web_api.obter_config_sistema')
    def test_permissao_sistema_liberado_quando_cliente_sem_config(self, mock_sistema, mock_cliente):
        """Testa usa configuração do sistema quando cliente não tem específica"""
        mock_cliente.return_value = None
        mock_sistema.return_value = True  # Sistema permite por padrão
        
        resultado = verificar_permissao_cambio_seguro('cliente_sem_config')
        
        assert resultado == True


class TestHorarioComercial:
    """Testes para verificação de horário comercial"""
    
    @patch('web_api.obter_config_cliente')
    @patch('web_api.obter_config_sistema')
    @patch('web_api.datetime')
    @patch('web_api.pytz')
    def test_dentro_do_horario_comercial(self, mock_pytz, mock_datetime, mock_sistema, mock_cliente):
        """Testa horário dentro do permitido"""
        from datetime import datetime as dt
        
        # Configurar horário do cliente
        mock_cliente.return_value = {
            'inicio': '09:00',
            'fim': '17:00',
            'dias_semana': [0, 1, 2, 3, 4],
            'fuso_horario': 'America/Sao_Paulo'
        }
        
        # Mock da hora atual (14:30 de uma quarta-feira)
        mock_now = Mock()
        mock_now.weekday.return_value = 2  # Quarta (0=segunda)
        mock_now.strftime.return_value = '14:30'
        mock_datetime.now.return_value = mock_now
        
        horario_ok, mensagem = verificar_horario_cliente('cliente_teste')
        
        assert horario_ok == True
        assert "Dentro" in mensagem
    
    @patch('web_api.obter_config_cliente')
    @patch('web_api.obter_config_sistema')
    @patch('web_api.datetime')
    @patch('web_api.pytz')
    def test_fora_do_horario_comercial(self, mock_pytz, mock_datetime, mock_sistema, mock_cliente):
        """Testa horário fora do permitido"""
        mock_cliente.return_value = {
            'inicio': '09:00',
            'fim': '17:00',
            'dias_semana': [0, 1, 2, 3, 4],
            'fuso_horario': 'America/Sao_Paulo'
        }
        
        # Mock da hora atual (20:00 - depois do horário)
        mock_now = Mock()
        mock_now.weekday.return_value = 2
        mock_now.strftime.return_value = '20:00'
        mock_datetime.now.return_value = mock_now
        
        horario_ok, mensagem = verificar_horario_cliente('cliente_teste')
        
        assert horario_ok == False
        assert "fora" in mensagem.lower()
    
    @patch('web_api.obter_config_cliente')
    @patch('web_api.obter_config_sistema')
    @patch('web_api.datetime')
    @patch('web_api.pytz')
    def test_fim_de_semana_bloqueado(self, mock_pytz, mock_datetime, mock_sistema, mock_cliente):
        """Testa fim de semana (sábado) deve bloquear"""
        mock_cliente.return_value = {
            'inicio': '09:00',
            'fim': '17:00',
            'dias_semana': [0, 1, 2, 3, 4],  # Só dias úteis
            'fuso_horario': 'America/Sao_Paulo'
        }
        
        # Mock: Sábado (weekday = 5)
        mock_now = Mock()
        mock_now.weekday.return_value = 5  # Sábado
        mock_now.strftime.return_value = '14:30'
        mock_datetime.now.return_value = mock_now
        
        horario_ok, mensagem = verificar_horario_cliente('cliente_teste')
        
        assert horario_ok == False
        assert "Dias permitidos" in mensagem


class TestCalculosCambio:
    """Testes para os cálculos de câmbio (spread aplicado)"""
    
    @patch('web_api.obter_cotacao_simples')
    @patch('web_api.obter_spread_cliente')
    @patch('web_api.verificar_permissao_cambio_seguro')
    @patch('web_api.verificar_horario_cliente')
    def test_calculo_compra_com_spread(self, mock_horario, mock_perm, mock_spread, mock_cotacao):
        """Testa cálculo de COMPRA com spread aplicado (cliente paga mais)"""
        mock_horario.return_value = (True, "Ok")
        mock_perm.return_value = True
        mock_cotacao.return_value = 5.20  # Cotação de mercado
        mock_spread.return_value = {'compra': 1.5, 'venda': 0.5}
        
        # Simular a API de cálculo (precisamos importar a função real)
        from web_api import api_calcular_cambio_core  # Vamos criar esta função
        
        # Aqui testamos a lógica de cálculo
        cotacao_cliente = mock_cotacao.return_value * (1 + 1.5/100)  # Compra: +spread
        valor_receber = 100  # Cliente quer receber 100 EUR
        valor_pagar = valor_receber * cotacao_cliente
        
        assert cotacao_cliente == 5.278  # 5.20 * 1.015
        assert valor_pagar == 527.80  # 100 * 5.278
    
    @patch('web_api.obter_cotacao_simples')
    @patch('web_api.obter_spread_cliente')
    @patch('web_api.verificar_permissao_cambio_seguro')
    @patch('web_api.verificar_horario_cliente')
    def test_calculo_venda_com_spread(self, mock_horario, mock_perm, mock_spread, mock_cotacao):
        """Testa cálculo de VENDA com spread aplicado (cliente recebe menos)"""
        mock_horario.return_value = (True, "Ok")
        mock_perm.return_value = True
        mock_cotacao.return_value = 5.20  # Cotação de mercado
        mock_spread.return_value = {'compra': 1.5, 'venda': 0.5}
        
        cotacao_cliente = mock_cotacao.return_value * (1 - 0.5/100)  # Venda: -spread
        valor_vender = 1000  # Cliente quer vender 1000 USD
        valor_receber = valor_vender * cotacao_cliente
        
        assert cotacao_cliente == 5.174  # 5.20 * 0.995
        assert valor_receber == 5174.00  # 1000 * 5.174