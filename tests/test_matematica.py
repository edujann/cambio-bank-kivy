"""
Teste super simples - Não depende do seu sistema
"""
import pytest

class TestMatematicaBasica:
    
    def test_soma(self):
        resultado = 2 + 2
        assert resultado == 4
        print("✅ 2 + 2 = 4")
    
    def test_multiplicacao(self):
        resultado = 5 * 3
        assert resultado == 15
        print("✅ 5 * 3 = 15")
    
    def test_divisao(self):
        resultado = 10 / 2
        assert resultado == 5
        print("✅ 10 / 2 = 5")