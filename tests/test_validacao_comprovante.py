"""
Teste específico para validação do comprovante de endereço (3 meses)
"""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Adiciona o caminho da pasta web
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web'))

from web_api import verificar_documentos_validos


class TestValidacaoComprovante:
    """Testa especificamente a validação de 3 meses do comprovante"""
    
    def test_comprovante_com_2_meses_deve_passar(self):
        """Comprovante com 2 meses deve ser ACEITO"""
        cliente_id = "teste_123"
        
        # Simula cliente com comprovante de 60 dias atrás
        with patch('web_api.supabase') as mock_sb:
            mock_table = Mock()
            mock_sb.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.execute.return_value = Mock(data=[{
                'doc_address_ok': True,
                'doc_address_atualizado_em': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
                'doc_address_validade': (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d'),
                'doc_photo_id_ok': True,
                'doc_photo_id_validade': (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d')
            }])
            
            status, mensagem, docs = verificar_documentos_validos(cliente_id)
            
            # Deve passar
            assert status == True, f"Comprovante de 2 meses deveria ser aceito, mas falhou: {mensagem}"
    
    def test_comprovante_com_4_meses_deve_falhar(self):
        """Comprovante com 4 meses deve ser REJEITADO"""
        cliente_id = "teste_456"
        
        # Simula cliente com comprovante de 120 dias atrás
        with patch('web_api.supabase') as mock_sb:
            mock_table = Mock()
            mock_sb.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.execute.return_value = Mock(data=[{
                'doc_address_ok': True,
                'doc_address_atualizado_em': (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d'),
                'doc_address_validade': (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d'),
                'doc_photo_id_ok': True,
                'doc_photo_id_validade': (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d')
            }])
            
            status, mensagem, docs = verificar_documentos_validos(cliente_id)
            
            # Deve falhar (status False)
            assert status == False, f"Comprovante de 4 meses deveria ser REJEITADO, mas foi aceito. Docs: {docs}"
    
    def test_comprovante_sem_data_de_atualizacao(self):
        """Se não tiver data de atualização, usa apenas a validade"""
        cliente_id = "teste_789"
        
        with patch('web_api.supabase') as mock_sb:
            mock_table = Mock()
            mock_sb.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.execute.return_value = Mock(data=[{
                'doc_address_ok': True,
                'doc_address_atualizado_em': None,  # Sem data de atualização
                'doc_address_validade': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'doc_photo_id_ok': True,
                'doc_photo_id_validade': (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d')
            }])
            
            status, mensagem, docs = verificar_documentos_validos(cliente_id)
            
            print(f"📝 Teste sem data de atualização: status={status}, docs={docs}")
            # A função deve executar sem erro


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])