"""
Testes para operações de ESTORNO - CRÍTICO (Pode causar perda financeira)
"""
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_api import (
    processar_estorno_por_inversao,
    calcular_estorno,
    executar_operacao_saldo
)


class TestProcessarEstorno:
    """Testes para processar_estorno_por_inversao - FUNÇÃO MAIS CRÍTICA"""
    
    def test_estorno_transferencia_internacional_completo(self):
        """Testa estorno de transferência internacional DEVE dar CRÉDITO ao cliente"""
        
        transacao_original = {
            'id': '12345',
            'tipo': 'transferencia_internacional',
            'conta_remetente': 'conta_cliente_123',
            'conta_destinatario': 'empresa_456',
            'valor': 1000.00,
            'moeda': 'USD',
            'status': 'rejected'
        }
        
        transacao_estorno = {
            'id': '99999',
            'transacao_original_id': '12345',
            'descricao': 'Estorno',
            'tipo': 'estorno'
        }
        
        conta_num = 'conta_cliente_123'
        moeda = 'USD'
        data_str = '2024-01-15 10:00:00'
        data_obj = datetime.now()
        
        resultado, tipo_original = processar_estorno_por_inversao(
            transacao_estorno, conta_num, moeda, data_str, data_obj
        )
        
        # 🔥 CRÍTICO: Cliente deve receber CRÉDITO
        assert resultado is not None
        assert resultado['credito'] == 1000.00
        assert resultado['debito'] == 0.00
        assert "ESTORNO" in resultado['descricao']
    
    def test_estorno_transferencia_internacional_quando_cliente_destino(self):
        """Testa estorno quando cliente é o DESTINO (recebeu dinheiro indevido)"""
        
        transacao_original = {
            'id': '12346',
            'tipo': 'transferencia_internacional',
            'conta_remetente': 'empresa_456',
            'conta_destinatario': 'conta_cliente_123',
            'valor': 500.00,
            'moeda': 'EUR',
            'status': 'completed'
        }
        
        transacao_estorno = {
            'id': '99998',
            'transacao_original_id': '12346',
            'tipo': 'estorno'
        }
        
        conta_num = 'conta_cliente_123'
        moeda = 'EUR'
        
        resultado, tipo_original = processar_estorno_por_inversao(
            transacao_estorno, conta_num, moeda, '2024-01-15 10:00:00', datetime.now()
        )
        
        # 🔥 CRÍTICO: Cliente destino deve pagar DÉBITO (devolver o dinheiro)
        assert resultado is not None
        assert resultado['credito'] == 0.00
        assert resultado['debito'] == 500.00
    
    def test_estorno_cambio_onde_cliente_original_perdeu_dinheiro(self):
        """Testa estorno de câmbio - cliente perdeu dinheiro, deve recuperar"""
        
        transacao_original = {
            'id': '850030',
            'tipo': 'cambio',
            'conta_origem': 'conta_cliente_123',
            'conta_destino': 'conta_cliente_456',
            'valor': 10000.00,
            'moeda_origem': 'USD',
            'moeda_destino': 'BRL',
            'valor_origem': 10000.00,
            'valor_destino': 52000.00
        }
        
        transacao_estorno = {
            'id': '99997',
            'transacao_original_id': '850030',
            'tipo': 'estorno'
        }
        
        conta_num = 'conta_cliente_123'
        moeda = 'USD'
        
        resultado, tipo_original = processar_estorno_por_inversao(
            transacao_estorno, conta_num, moeda, '2024-01-15 10:00:00', datetime.now()
        )
        
        # Cliente que PERDEU dinheiro deve RECUPERAR (CRÉDITO)
        assert resultado is not None
        assert resultado['credito'] == 10000.00
    
    def test_estorno_cambio_onde_cliente_original_ganhou_dinheiro(self):
        """Testa estorno de câmbio - cliente ganhou dinheiro, deve devolver"""
        
        transacao_original = {
            'id': '850031',
            'tipo': 'cambio',
            'conta_origem': 'conta_empresa_789',
            'conta_destino': 'conta_cliente_123',
            'valor': 5000.00,
            'moeda_origem': 'EUR',
            'moeda_destino': 'USD',
            'valor_origem': 5000.00,
            'valor_destino': 5450.00
        }
        
        transacao_estorno = {
            'id': '99996',
            'transacao_original_id': '850031',
            'tipo': 'estorno'
        }
        
        conta_num = 'conta_cliente_123'
        moeda = 'USD'
        
        resultado, tipo_original = processar_estorno_por_inversao(
            transacao_estorno, conta_num, moeda, '2024-01-15 10:00:00', datetime.now()
        )
        
        # Cliente que GANHOU dinheiro deve DEVOLVER (DÉBITO)
        assert resultado is not None
        assert resultado['debito'] == 5450.00
    
    def test_estorno_ajuste_admin_credito(self):
        """Testa estorno de ajuste administrativo do tipo CRÉDITO"""
        
        transacao_original = {
            'id': '12347',
            'tipo': 'ajuste_admin',
            'tipo_ajuste': 'CREDITO',
            'conta_remetente': 'conta_cliente_123',
            'valor': 100.00,
            'descricao_ajuste': 'Bônus'
        }
        
        transacao_estorno = {
            'id': '99995',
            'transacao_original_id': '12347',
            'tipo': 'estorno'
        }
        
        conta_num = 'conta_cliente_123'
        moeda = 'USD'
        
        resultado, tipo_original = processar_estorno_por_inversao(
            transacao_estorno, conta_num, moeda, '2024-01-15 10:00:00', datetime.now()
        )
        
        # Original: CRÉDITO (cliente ganhou) → Estorno: DÉBITO (devolve)
        assert resultado is not None
        assert resultado['debito'] == 100.00
        assert "ESTORNO" in resultado['descricao']


class TestCalcularEstorno:
    """Testes para calcular_estorno - determina operações de reversão"""
    
    def test_calcular_estorno_ajuste_saldo_empresa_debito(self):
        """Testa reversão de ajuste DÉBITO da empresa"""
        
        transacao = {
            'tipo': 'ajuste_saldo_empresa',
            'conta_remetente': 'conta_empresa_001',
            'valor': 5000.00,
            'tipo_ajuste': 'DÉBITO'
        }
        
        operacoes = calcular_estorno(transacao)
        
        assert len(operacoes) == 1
        assert operacoes[0]['conta'] == 'conta_empresa_001'
        assert operacoes[0]['valor'] == 5000.00
        assert operacoes[0]['operacao'] == 'CREDITO'  # Reversão: crédito
        assert operacoes[0]['is_empresa'] == True
    
    def test_calcular_estorno_ajuste_saldo_empresa_credito(self):
        """Testa reversão de ajuste CRÉDITO da empresa"""
        
        transacao = {
            'tipo': 'ajuste_saldo_empresa',
            'conta_remetente': 'conta_empresa_001',
            'valor': 3000.00,
            'tipo_ajuste': 'CRÉDITO'
        }
        
        operacoes = calcular_estorno(transacao)
        
        assert len(operacoes) == 1
        assert operacoes[0]['operacao'] == 'DEBITO'  # Reversão: débito
    
    def test_calcular_estorno_cambio_com_duas_contas(self):
        """Testa câmbio entre duas contas - deve gerar duas operações"""
        
        transacao = {
            'tipo': 'cambio',
            'conta_remetente': 'conta_origem_123',
            'conta_destinatario': 'conta_destino_456',
            'valor': 10000.00,
            'valor_destino': 52000.00
        }
        
        operacoes = calcular_estorno(transacao)
        
        # Deve ter 2 operações (origem e destino)
        assert len(operacoes) == 2
        
        # Encontrar operação de origem
        op_origem = next((o for o in operacoes if o['conta'] == 'conta_origem_123'), None)
        op_destino = next((o for o in operacoes if o['conta'] == 'conta_destino_456'), None)
        
        assert op_origem is not None
        assert op_destino is not None
        
        # Operação de origem: CRÉDITO (recupera)
        assert op_origem['operacao'] == 'CREDITO'
        assert op_origem['valor'] == 10000.00
        
        # Operação de destino: DÉBITO (devolve)
        assert op_destino['operacao'] == 'DEBITO'
        assert op_destino['valor'] == 52000.00


class TestExecutarOperacaoSaldo:
    """Testes para executar_operacao_saldo - ALTERA SALDO REAL"""
    
    @patch('web_api.supabase')
    def test_executar_credito_em_conta_cliente_aumenta_saldo(self, mock_supabase):
        """Testa CRÉDITO em conta de cliente DEVE aumentar saldo"""
        
        # Mock da consulta de saldo atual
        mock_response = Mock()
        mock_response.data = [{'saldo': 1000.00}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock da atualização
        mock_update = Mock()
        mock_update.data = [{'saldo': 1500.00}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update
        
        sucesso, novo_saldo = executar_operacao_saldo(
            conta='conta_cliente_123',
            valor=500.00,
            operacao='CREDITO',
            is_empresa=False
        )
        
        assert sucesso == True
        assert novo_saldo == 1500.00
    
    @patch('web_api.supabase')
    def test_executar_debito_em_conta_cliente_diminui_saldo(self, mock_supabase):
        """Testa DÉBITO em conta de cliente DEVE diminuir saldo"""
        
        mock_response = Mock()
        mock_response.data = [{'saldo': 1000.00}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        mock_update = Mock()
        mock_update.data = [{'saldo': 800.00}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update
        
        sucesso, novo_saldo = executar_operacao_saldo(
            conta='conta_cliente_123',
            valor=200.00,
            operacao='DEBITO',
            is_empresa=False
        )
        
        assert sucesso == True
        assert novo_saldo == 800.00
    
    @patch('web_api.supabase')
    def test_operacao_em_conta_empresa_logica_invertida(self, mock_supabase):
        """Testa conta EMPRESA: CREDITO = DIMINUI, DEBITO = AUMENTA"""
        
        mock_response = Mock()
        mock_response.data = [{'saldo': 10000.00}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        mock_update = Mock()
        mock_update.data = [{'saldo': 9500.00}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update
        
        # CRÉDITO na conta empresa = DIMINUI saldo
        sucesso, novo_saldo = executar_operacao_saldo(
            conta='conta_empresa_001',
            valor=500.00,
            operacao='CREDITO',
            is_empresa=True
        )
        
        assert sucesso == True
        assert novo_saldo == 9500.00  # 10000 - 500
    
    @patch('web_api.supabase')
    def test_debito_em_conta_empresa_aumenta_saldo(self, mock_supabase):
        """Testa DÉBITO em conta empresa = AUMENTA saldo (lógica invertida)"""
        
        mock_response = Mock()
        mock_response.data = [{'saldo': 10000.00}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        mock_update = Mock()
        mock_update.data = [{'saldo': 10500.00}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update
        
        sucesso, novo_saldo = executar_operacao_saldo(
            conta='conta_empresa_001',
            valor=500.00,
            operacao='DEBITO',
            is_empresa=True
        )
        
        assert sucesso == True
        assert novo_saldo == 10500.00  # 10000 + 500
    
    @patch('web_api.supabase')
    def test_conta_nao_encontrada_retorna_erro(self, mock_supabase):
        """Testa conta inexistente deve retornar erro"""
        
        mock_response = Mock()
        mock_response.data = []  # Conta não encontrada
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        sucesso, mensagem = executar_operacao_saldo(
            conta='conta_que_nao_existe',
            valor=100.00,
            operacao='CREDITO',
            is_empresa=False
        )
        
        assert sucesso == False
        assert "não encontrada" in mensagem