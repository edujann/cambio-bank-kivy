"""
Testes para extrato bancário
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_api import transacao_esta_no_periodo, parse_data_unificada


class TestParseData:
    """Testes para parse_data_unificada - converte vários formatos de data"""
    
    def test_parse_data_iso_com_t(self):
        """Testa formato ISO com T (ex: 2024-01-15T10:30:00)"""
        resultado = parse_data_unificada('2024-01-15T10:30:00')
        assert resultado is not None
        assert resultado.year == 2024
        assert resultado.month == 1
        assert resultado.day == 15
        assert resultado.hour == 10
        assert resultado.minute == 30
    
    def test_parse_data_formato_banco(self):
        """Testa formato padrão do banco (YYYY-MM-DD HH:MM:SS)"""
        resultado = parse_data_unificada('2024-01-15 14:45:30')
        assert resultado is not None
        assert resultado.year == 2024
        assert resultado.month == 1
        assert resultado.day == 15
        assert resultado.hour == 14
        assert resultado.minute == 45
    
    def test_parse_data_apenas_data(self):
        """Testa apenas data (YYYY-MM-DD)"""
        resultado = parse_data_unificada('2024-01-15')
        assert resultado is not None
        assert resultado.year == 2024
        assert resultado.month == 1
        assert resultado.day == 15
        # Hora deve ser meia-noite
        assert resultado.hour == 0
    
    def test_parse_data_formato_brasileiro(self):
        """Testa formato brasileiro (DD/MM/YYYY)"""
        resultado = parse_data_unificada('15/01/2024')
        assert resultado is not None
        assert resultado.year == 2024
        assert resultado.month == 1
        assert resultado.day == 15
    
    def test_parse_data_invalida_retorna_none(self):
        """Testa data inválida retorna None"""
        resultado = parse_data_unificada('data-invalida')
        assert resultado is None
        
        resultado = parse_data_unificada('')
        assert resultado is None


class TestTransacaoNoPeriodo:
    """Testes para transacao_esta_no_periodo"""
    
    def test_transacao_dentro_do_periodo(self):
        """Testa transação com data dentro do período"""
        data_inicio = datetime(2024, 1, 1)
        data_fim = datetime(2024, 1, 31)
        
        transacao = {
            'data': '2024-01-15 10:00:00'
        }
        
        resultado = transacao_esta_no_periodo(transacao, data_inicio, data_fim)
        assert resultado == True
    
    def test_transacao_antes_do_periodo(self):
        """Testa transação antes do período"""
        data_inicio = datetime(2024, 1, 1)
        data_fim = datetime(2024, 1, 31)
        
        transacao = {
            'data': '2023-12-31 23:59:00'
        }
        
        resultado = transacao_esta_no_periodo(transacao, data_inicio, data_fim)
        assert resultado == False
    
    def test_transacao_depois_do_periodo(self):
        """Testa transação depois do período"""
        data_inicio = datetime(2024, 1, 1)
        data_fim = datetime(2024, 1, 31)
        
        transacao = {
            'data': '2024-02-01 00:00:01'
        }
        
        resultado = transacao_esta_no_periodo(transacao, data_inicio, data_fim)
        assert resultado == False
    
    def test_transacao_sem_data_retorna_false(self):
        """Testa transação sem campo data"""
        data_inicio = datetime(2024, 1, 1)
        data_fim = datetime(2024, 1, 31)
        
        transacao = {}
        
        resultado = transacao_esta_no_periodo(transacao, data_inicio, data_fim)
        assert resultado == False
    
    def test_transacao_usando_data_solicitacao(self):
        """Testa uso de data_solicitacao quando data principal não existe"""
        data_inicio = datetime(2024, 1, 1)
        data_fim = datetime(2024, 1, 31)
        
        transacao = {
            'data_solicitacao': '2024-01-20 09:00:00'
        }
        
        resultado = transacao_esta_no_periodo(transacao, data_inicio, data_fim)
        assert resultado == True
    
    def test_transacao_rejeitada_com_data_recusa(self):
        """Testa transação rejeitada usando data_recusa"""
        data_inicio = datetime(2024, 1, 1)
        data_fim = datetime(2024, 1, 31)
        
        transacao = {
            'status': 'rejected',
            'data_recusa': '2024-01-25 15:30:00'
        }
        
        resultado = transacao_esta_no_periodo(transacao, data_inicio, data_fim)
        assert resultado == True