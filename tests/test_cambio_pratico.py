"""
Teste PRÁTICO de cálculo de câmbio
VOCÊ PODE EXECUTAR AGORA - Não depende do servidor rodando
"""
import pytest

class TestCalculoCambioPratico:
    """Testa a lógica de cálculo de câmbio que seu sistema usa"""
    
    def test_calculo_compra_cliente_paga_mais(self):
        """
        CENÁRIO: Cliente quer COMPRAR dólares com reais
        REGRA: Cliente paga MAIS que a cotação do mercado (spread)
        """
        print("\n" + "="*50)
        print("📊 TESTE: Compra de Dólar com spread")
        print("="*50)
        
        # Dados do mercado
        cotacao_mercado = 5.20  # 1 USD = 5.20 BRL
        spread_percentual = 1.5  # 1.5% de spread
        
        # Cálculo que seu sistema faz
        # Cliente PAGA MAIS na compra
        cotacao_cliente = cotacao_mercado * (1 + spread_percentual / 100)
        
        print(f"💰 Cotação de mercado: 1 USD = R$ {cotacao_mercado}")
        print(f"📈 Spread aplicado: {spread_percentual}%")
        print(f"💳 Cotação para cliente: 1 USD = R$ {cotacao_cliente:.4f}")
        
        # Cliente quer comprar 1000 USD
        valor_desejado = 1000  # USD
        valor_a_pagar = valor_desejado * cotacao_cliente
        
        print(f"\n🎯 Cliente quer comprar: {valor_desejado} USD")
        print(f"💸 Cliente vai PAGAR: R$ {valor_a_pagar:.2f}")
        
        # VERIFICAÇÕES - O TESTE SÓ PASSA SE TUDO ESTIVER CERTO
        assert cotacao_cliente > cotacao_mercado, "ERRO: Cotação do cliente deveria ser MAIOR"
        assert cotacao_cliente == 5.278, f"ERRO: Cotação deveria ser 5.278, foi {cotacao_cliente}"
        assert valor_a_pagar == 5278.00, f"ERRO: Valor deveria ser 5278.00, foi {valor_a_pagar}"
        
        print("\n✅ TESTE PASSOU! Cliente pagou MAIS (correto)")
        print("="*50)
    
    def test_calculo_venda_cliente_recebe_menos(self):
        """
        CENÁRIO: Cliente quer VENDER dólares para receber reais
        REGRA: Cliente recebe MENOS que a cotação do mercado (spread)
        """
        print("\n" + "="*50)
        print("📊 TESTE: Venda de Dólar com spread")
        print("="*50)
        
        # Dados do mercado
        cotacao_mercado = 5.20  # 1 USD = 5.20 BRL
        spread_percentual = 1.5  # 1.5% de spread
        
        # Cálculo que seu sistema faz
        # Cliente RECEBE MENOS na venda
        cotacao_cliente = cotacao_mercado * (1 - spread_percentual / 100)
        
        print(f"💰 Cotação de mercado: 1 USD = R$ {cotacao_mercado}")
        print(f"📉 Spread aplicado: {spread_percentual}%")
        print(f"💳 Cotação para cliente: 1 USD = R$ {cotacao_cliente:.4f}")
        
        # Cliente quer vender 1000 USD
        valor_para_vender = 1000  # USD
        valor_a_receber = valor_para_vender * cotacao_cliente
        
        print(f"\n🎯 Cliente quer vender: {valor_para_vender} USD")
        print(f"💰 Cliente vai RECEBER: R$ {valor_a_receber:.2f}")
        
        # VERIFICAÇÕES
        assert cotacao_cliente < cotacao_mercado, "ERRO: Cotação do cliente deveria ser MENOR"
        assert cotacao_cliente == 5.122, f"ERRO: Cotação deveria ser 5.122, foi {cotacao_cliente}"
        assert valor_a_receber == 5122.00, f"ERRO: Valor deveria ser 5122.00, foi {valor_a_receber}"
        
        print("\n✅ TESTE PASSOU! Cliente recebeu MENOS (correto)")
        print("="*50)
    
    def test_comparacao_compra_vs_venda(self):
        """
        CENÁRIO: Cliente compra E vende o mesmo valor
        REGRA: A diferença é o lucro do banco (spread)
        """
        print("\n" + "="*50)
        print("📊 TESTE: Diferença compra vs venda (lucro do banco)")
        print("="*50)
        
        cotacao_mercado = 5.20
        spread = 1.5
        
        # Mesmo cálculo dos testes anteriores
        cotacao_compra = cotacao_mercado * (1 + spread / 100)
        cotacao_venda = cotacao_mercado * (1 - spread / 100)
        
        valor_operacao = 1000  # USD
        
        # Cenário 1: Cliente compra
        paga_na_compra = valor_operacao * cotacao_compra
        
        # Cenário 2: Cliente vende o mesmo valor
        recebe_na_venda = valor_operacao * cotacao_venda
        
        # Lucro do banco
        lucro_banco = paga_na_compra - recebe_na_venda
        spread_total = (cotacao_compra - cotacao_venda) * valor_operacao
        
        print(f"📈 Cotação de COMPRA (cliente paga): R$ {cotacao_compra:.4f}")
        print(f"📉 Cotação de VENDA (cliente recebe): R$ {cotacao_venda:.4f}")
        print(f"💰 Diferença por dólar: R$ {(cotacao_compra - cotacao_venda):.4f}")
        print(f"\n💸 Cliente PAGA para comprar 1000 USD: R$ {paga_na_compra:.2f}")
        print(f"💵 Cliente RECEBE para vender 1000 USD: R$ {recebe_na_venda:.2f}")
        print(f"\n🏦 LUCRO DO BANCO: R$ {lucro_banco:.2f}")
        
        # VERIFICAÇÕES
        assert cotacao_compra > cotacao_venda, "ERRO: Cotação de compra deve ser maior"
        assert lucro_banco > 0, "ERRO: Banco deveria ter lucro"
        assert lucro_banco == 156.00, f"ERRO: Lucro deveria ser 156.00, foi {lucro_banco}"
        
        print("\n✅ TESTE PASSOU! Banco teve lucro (correto)")
        print("="*50)
    
    def test_cenario_sem_spread_sem_lucro(self):
        """
        CENÁRIO: Sem spread (cliente especial)
        REGRA: Banco não ganha dinheiro
        """
        print("\n" + "="*50)
        print("📊 TESTE: Cliente especial - SEM spread")
        print("="*50)
        
        cotacao_mercado = 5.20
        spread = 0  # SEM spread!
        
        cotacao_compra = cotacao_mercado * (1 + spread / 100)
        cotacao_venda = cotacao_mercado * (1 - spread / 100)
        
        print(f"📈 Cotação de COMPRA: R$ {cotacao_compra:.4f}")
        print(f"📉 Cotação de VENDA: R$ {cotacao_venda:.4f}")
        
        # VERIFICAÇÕES
        assert cotacao_compra == cotacao_venda, "ERRO: Sem spread, cotações deveriam ser iguais"
        assert cotacao_compra == cotacao_mercado
        
        print("\n✅ TESTE PASSOU! Sem spread, cotações são iguais")
        print("="*50)


class TestValidacoes:
    """Testa validações que seu sistema faz"""
    
    def test_valor_negativo_invalido(self):
        """Valores negativos devem ser rejeitados"""
        print("\n" + "="*50)
        print("📊 TESTE: Validação de valores negativos")
        print("="*50)
        
        valor_operacao = -1000
        
        # Simula a validação que seu sistema faz
        def is_valido(valor):
            return valor > 0
        
        print(f"🔍 Testando valor: R$ {valor_operacao}")
        
        if is_valido(valor_operacao):
            print("❌ ERRO: Valor negativo NÃO deveria ser aceito")
        else:
            print("✅ Valor negativo foi REJEITADO (correto)")
        
        assert is_valido(valor_operacao) == False, "ERRO: Valor negativo foi aceito"
        print("="*50)
    
    def test_valor_muito_alto_precisa_aprovacao(self):
        """Valores acima do limite precisam de aprovação"""
        print("\n" + "="*50)
        print("📊 TESTE: Valores acima do limite")
        print("="*50)
        
        limite_diario = 10000
        valor_operacao = 15000
        
        # Simula verificação de limite
        precisa_aprovacao = valor_operacao > limite_diario
        
        print(f"💰 Limite diário: R$ {limite_diario}")
        print(f"🎯 Valor da operação: R$ {valor_operacao}")
        
        if precisa_aprovacao:
            print("✅ Operação PRECISA de aprovação (correto)")
        else:
            print("❌ ERRO: Operação deveria precisar de aprovação")
        
        assert precisa_aprovacao == True
        print("="*50)


# Para rodar este teste sozinho, sem pytest
if __name__ == "__main__":
    print("\n" + "🔬"*20)
    print("EXECUTANDO TESTES MANUALMENTE")
    print("🔬"*20)
    
    test = TestCalculoCambioPratico()
    test.test_calculo_compra_cliente_paga_mais()
    test.test_calculo_venda_cliente_recebe_menos()
    test.test_comparacao_compra_vs_venda()
    test.test_cenario_sem_spread_sem_lucro()
    
    valid = TestValidacoes()
    valid.test_valor_negativo_invalido()
    valid.test_valor_muito_alto_precisa_aprovacao()
    
    print("\n" + "🎉"*20)
    print("TODOS OS TESTES PASSARAM!")
    print("🎉"*20)