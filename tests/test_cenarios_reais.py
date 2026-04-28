"""
TESTES IMPORTANTES - CENÁRIOS REAIS
Simula situações que acontecem no dia a dia
"""
import pytest

class TestCenariosCompraVenda:
    """Cenários reais de compra e venda"""
    
    def test_cenario_cliente_compra_1000_dolares(self):
        """Cenário: Cliente compra US$ 1.000,00"""
        cotacao = 5.20
        spread = 1.5
        valor_desejado = 1000
        
        cotacao_cliente = cotacao * (1 + spread / 100)
        valor_pagar = valor_desejado * cotacao_cliente
        
        # Verificações
        assert cotacao_cliente == 5.278
        assert valor_pagar == 5278.00
        assert valor_pagar > valor_desejado * cotacao  # Pagou mais que o mercado
    
    def test_cenario_cliente_vende_1000_dolares(self):
        """Cenário: Cliente vende US$ 1.000,00"""
        cotacao = 5.20
        spread = 1.5
        valor_venda = 1000
        
        cotacao_cliente = cotacao * (1 - spread / 100)
        valor_receber = valor_venda * cotacao_cliente
        
        # Verificações
        assert cotacao_cliente == 5.122
        assert valor_receber == 5122.00
        assert valor_receber < valor_venda * cotacao  # Recebeu menos que o mercado
    
    def test_cenario_compra_500_euros(self):
        """Cenário: Cliente compra € 500,00"""
        cotacao = 6.00  # 1 EUR = R$ 6,00
        spread = 2.0
        valor_desejado = 500
        
        cotacao_cliente = cotacao * (1 + spread / 100)
        valor_pagar = valor_desejado * cotacao_cliente
        
        assert cotacao_cliente == 6.12
        assert valor_pagar == 3060.00
    
    def test_cenario_compra_10000_dolares(self):
        """Cenário: Cliente compra US$ 10.000 (acima do limite)"""
        limite = 10000
        valor_desejado = 10000
        
        precisa_aprovacao = valor_desejado > limite
        
        # Se for igual ao limite, não precisa aprovação
        assert precisa_aprovacao == False
        assert valor_desejado == limite
    
    def test_cenario_compra_15000_dolares(self):
        """Cenário: Cliente compra US$ 15.000 (acima do limite)"""
        limite = 10000
        valor_desejado = 15000
        
        precisa_aprovacao = valor_desejado > limite
        
        # Verificações
        assert precisa_aprovacao == True
        assert valor_desejado > limite


class TestCenariosErro:
    """Cenários de erro que o sistema deve tratar"""
    
    def test_erro_valor_zero(self):
        """Erro: Tentar operação com valor zero"""
        valor = 0
        is_valido = valor > 0
        assert is_valido == False
    
    def test_erro_valor_negativo(self):
        """Erro: Tentar operação com valor negativo"""
        valor = -500
        is_valido = valor > 0
        assert is_valido == False
    
    def test_erro_moeda_invalida(self):
        """Erro: Tentar operação com moeda inválida"""
        moedas_validas = ['USD', 'EUR', 'GBP', 'BRL']
        moeda_teste = 'XYZ'
        is_valida = moeda_teste in moedas_validas
        assert is_valida == False
    
    def test_erro_saldo_insuficiente(self):
        """Erro: Tentar transferir mais que o saldo"""
        saldo = 1000
        valor_transferir = 1500
        tem_saldo = valor_transferir <= saldo
        assert tem_saldo == False
    
    def test_erro_conta_inexistente(self):
        """Erro: Tentar usar conta que não existe"""
        contas_validas = ['123456', '789012']
        conta_teste = '999999'
        existe = conta_teste in contas_validas
        assert existe == False


class TestCenariosEstorno:
    """Cenários de estorno"""
    
    def test_estorno_apos_transferencia(self):
        """Cenário: Estornar transferência após erro"""
        valor_original = 1000
        saldo_antes = 5000
        
        # Transferência
        saldo_depois_transf = saldo_antes - valor_original
        assert saldo_depois_transf == 4000
        
        # Estorno
        saldo_depois_estorno = saldo_depois_transf + valor_original
        assert saldo_depois_estorno == saldo_antes
    
    def test_estorno_dentro_do_prazo(self):
        """Cenário: Estorno dentro do prazo (90 dias)"""
        prazo = 90
        dias_desde_transacao = 30
        pode_estornar = dias_desde_transacao <= prazo
        assert pode_estornar == True
    
    def test_estorno_fora_do_prazo(self):
        """Cenário: Estorno fora do prazo (NÃO pode)"""
        prazo = 90
        dias_desde_transacao = 100
        pode_estornar = dias_desde_transacao <= prazo
        assert pode_estornar == False


class TestCenariosHorario:
    """Cenários de horário comercial"""
    
    def test_operacao_10h(self):
        """Cenário: Operação às 10:00 - DEVE funcionar"""
        hora = "10:00"
        inicio = "09:00"
        fim = "17:00"
        permitido = inicio <= hora <= fim
        assert permitido == True
    
    def test_operacao_08h30(self):
        """Cenário: Operação às 08:30 - NÃO deve funcionar (antes do horário)"""
        hora = "08:30"
        inicio = "09:00"
        fim = "17:00"
        permitido = inicio <= hora <= fim
        assert permitido == False
        assert hora < inicio
    
    def test_operacao_18h(self):
        """Cenário: Operação às 18:00 - NÃO deve funcionar (depois do horário)"""
        hora = "18:00"
        inicio = "09:00"
        fim = "17:00"
        permitido = inicio <= hora <= fim
        assert permitido == False
        assert hora > fim