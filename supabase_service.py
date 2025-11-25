# supabase_service.py
import os
from supabase import create_client, Client
from datetime import datetime
import uuid

class SupabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
    
    async def salvar_transferencia(self, transferencia_data):
        """Salva uma transferência no Supabase"""
        try:
            # Garantir que tem ID único
            if 'id' not in transferencia_data:
                transferencia_data['id'] = str(uuid.uuid4())
            
            # Garantir timestamp
            if 'created_at' not in transferencia_data:
                transferencia_data['created_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('transferencias').insert(transferencia_data).execute()
            
            if response.data:
                print(f"✅ Transferência salva no Supabase! ID: {transferencia_data['id']}")
                return True
            else:
                print(f"❌ Erro ao salvar transferência: {response.error}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar transferência no Supabase: {e}")
            return False
    
    async def salvar_transacao(self, transacao_data):
        """Salva uma transação genérica (para câmbio, ajustes, etc)"""
        try:
            if 'id' not in transacao_data:
                transacao_data['id'] = str(uuid.uuid4())
            
            if 'created_at' not in transacao_data:
                transacao_data['created_at'] = datetime.now().isoformat()
            
            # Usar a mesma tabela transferencias para todas as transações
            response = self.supabase.table('transferencias').insert(transacao_data).execute()
            
            if response.data:
                print(f"✅ Transação salva no Supabase! ID: {transacao_data['id']}")
                return True
            else:
                print(f"❌ Erro ao salvar transação: {response.error}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar transação no Supabase: {e}")
            return False