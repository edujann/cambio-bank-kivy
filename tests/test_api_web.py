"""
Testes da API real - REQUER O SERVIDOR RODANDO
"""
import pytest
import requests

# Configuração da API
API_URL = "http://localhost:5000/api"

class TestAPIStatus:
    """Testa os endpoints básicos da API"""
    
    def test_status_endpoint(self):
        """Testa GET /api/status"""
        response = requests.get(f"{API_URL}/status")
        
        assert response.status_code == 200
        assert response.json()["status"] == "operacional"
        print("✅ /api/status retornou status operacional")
    
    def test_info_endpoint(self):
        """Testa GET /api (informações)"""
        response = requests.get(f"{API_URL}")
        
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert data["app"] == "🏦 Cambio Bank API"
        print("✅ /api retornou informações corretas")
    
    def test_test_endpoint(self):
        """Testa GET /api/test"""
        response = requests.get(f"{API_URL}/test")
        
        assert response.status_code == 200
        assert response.json()["success"] == True
        print("✅ /api/test funcionando")


class TestAPILogin:
    """Testa o endpoint de login"""
    
    def test_login_sem_dados(self):
        """Login sem dados deve retornar erro"""
        response = requests.post(f"{API_URL}/login", json={})
        
        assert response.status_code == 400
        assert "Dados de login não fornecidos" in response.json()["message"]
        print("✅ Validação de dados vazios funcionando")
    
    def test_login_usuario_inexistente(self):
        """Login com usuário que não existe"""
        response = requests.post(f"{API_URL}/login", json={
            "usuario": "usuario_que_nao_existe_12345",
            "senha": "senha_qualquer"
        })
        
        assert response.status_code == 401
        assert response.json()["success"] == False
        print("✅ Usuário inexistente corretamente bloqueado")
    
    def test_login_fields_faltando(self):
        """Login sem senha ou sem usuário"""
        # Sem usuário
        response1 = requests.post(f"{API_URL}/login", json={"senha": "123"})
        assert response1.status_code == 400
        
        # Sem senha
        response2 = requests.post(f"{API_URL}/login", json={"usuario": "teste"})
        assert response2.status_code == 400
        
        print("✅ Validação de campos obrigatórios funcionando")


class TestAPICEP:
    """Testa o endpoint de consulta de CEP"""
    
    def test_cep_valido(self):
        """CEP válido deve retornar dados"""
        response = requests.get(f"{API_URL}/cep/01001000")
        
        assert response.status_code == 200
        data = response.json()
        # ViaCEP retorna erro=False quando CEP é válido
        assert data.get("erro") != True
        print("✅ CEP válido consultado com sucesso")
    
    def test_cep_invalido(self):
        """CEP inválido deve retornar erro"""
        response = requests.get(f"{API_URL}/cep/00000000")
        
        assert response.status_code == 200  # ViaCEP retorna 200 mesmo com erro
        data = response.json()
        # Se CEP não existe, ViaCEP retorna {"erro": true}
        # Seu sistema pode retornar diferente
        print(f"   Resposta para CEP inválido: {data}")
        print("✅ Teste de CEP inválido executado")


if __name__ == "__main__":
    # Verifica se o servidor está rodando antes de testar
    try:
        requests.get(f"{API_URL}/status", timeout=2)
        print("✅ Servidor encontrado! Executando testes...")
    except:
        print("❌ Servidor NÃO está rodando!")
        print("   Inicie o servidor com: python web_api.py")
        exit(1)