"""
Testes de segurança - Login, permissões, rate limiting
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLogin:
    """Testes para autenticação e segurança"""
    
    @patch('web_api.supabase')
    def test_login_senha_incorreta_recebe_401(self, mock_supabase, client):
        """Testa senha incorreta retorna erro 401"""
        
        # Mock do Supabase retornando nenhum usuário
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.post('/api/login', json={
            'usuario': 'cliente_teste',
            'senha': 'senha_errada'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] == False
        assert 'Usuário ou senha inválidos' in data['message']
    
    @patch('web_api.supabase')
    def test_login_com_sucesso_cria_sessao(self, mock_supabase, client):
        """Testa login bem-sucedido cria sessão corretamente"""
        
        # Mock do Supabase com usuário encontrado
        mock_response = Mock()
        mock_response.data = [{
            'id': 1,
            'username': 'joao_silva',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'tipo': 'cliente',
            'status': 'ativo'
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.post('/api/login', json={
            'usuario': 'joao_silva',
            'senha': 'senha_correta'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['usuario']['username'] == 'joao_silva'
    
    def test_login_sem_dados_retorna_400(self, client):
        """Testa requisição sem dados retorna 400"""
        
        response = client.post('/api/login', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
    
    @patch('web_api.supabase')
    def test_login_usuario_bloqueado(self, mock_supabase, client):
        """Testa usuário bloqueado não pode fazer login"""
        
        mock_response = Mock()
        mock_response.data = [{
            'id': 1,
            'username': 'usuario_bloqueado',
            'status': 'bloqueado'
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.post('/api/login', json={
            'usuario': 'usuario_bloqueado',
            'senha': 'qualquer_senha'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'bloqueado' in data['message']
    
    def test_logout_limpa_sessao(self, cliente_teste_autenticado):
        """Testa logout limpa completamente a sessão"""
        
        response = cliente_teste_autenticado.get('/logout')
        
        assert response.status_code == 302  # Redirect
        
        # Verificar se sessão foi limpa
        with cliente_teste_autenticado.session_transaction() as sess:
            assert 'username' not in sess
            assert 'tipo' not in sess
    
    @patch('web_api.supabase')
    def test_login_rate_limit_excedido(self, mock_supabase, client):
        """Testa rate limiting - muitas tentativas bloqueiam temporariamente"""
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(data=[])
        
        # Fazer 11 tentativas (limite é 10)
        for _ in range(11):
            response = client.post('/api/login', json={
                'usuario': 'teste',
                'senha': 'senha'
            })
        
        # A 11ª tentativa deve retornar 429
        assert response.status_code == 429
        data = response.get_json()
        assert 'Muitas tentativas' in data['message']


class TestPermissoes:
    """Testes de autorização de endpoints"""
    
    def test_dashboard_sem_login_redireciona(self, client):
        """Testa acesso ao dashboard sem login redireciona para login"""
        
        response = client.get('/dashboard')
        
        # Deve redirecionar para login (302)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_com_login_acessa(self, cliente_teste_autenticado):
        """Testa dashboard com usuário logado retorna página"""
        
        with patch('web_api.supabase') as mock_supabase:
            # Mock das consultas ao Supabase
            mock_response = Mock()
            mock_response.data = [{'email': 'teste@email.com', 'nome': 'Teste'}]
            mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
            
            # Mock de beneficiários
            mock_benef = Mock()
            mock_benef.data = []
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_benef
            
            response = cliente_teste_autenticado.get('/dashboard')
            
            assert response.status_code == 200
            # Deve renderizar o template
            assert b'<!DOCTYPE html>' in response.data or b'dashboard' in response.data.lower()
    
    def test_api_user_sem_login_retorna_401(self, client):
        """Testa endpoint /api/user sem autenticação retorna 401"""
        
        response = client.get('/api/user')
        
        assert response.status_code == 401
    
    def test_api_user_com_login_retorna_dados(self, cliente_teste_autenticado):
        """Testa endpoint /api/user com autenticação retorna dados do usuário"""
        
        with patch('web_api.supabase') as mock_supabase:
            mock_response = Mock()
            mock_response.data = [{
                'username': 'cliente_teste',
                'nome': 'Cliente Teste',
                'email': 'cliente@teste.com',
                'tipo': 'cliente'
            }]
            mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
            
            response = cliente_teste_autenticado.get('/api/user')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True
            assert data['user']['username'] == 'cliente_teste'