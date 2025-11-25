# migrar_transferencia_233695.py
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv

def migrar_transferencia_233695():
    """Migra a transferência específica 233695 para o Supabase"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Credenciais do Supabase não encontradas")
        return False
    
    try:
        # Conectar ao Supabase
        supabase = create_client(supabase_url, supabase_key)
        
        # Carregar transferências do arquivo local
        with open('data/transferencias.json', 'r', encoding='utf-8') as f:
            transferencias = json.load(f)
        
        transferencia_id = "233695"
        
        if transferencia_id not in transferencias:
            print(f"❌ Transferência {transferencia_id} não encontrada no arquivo local")
            return False
        
        transferencia = transferencias[transferencia_id]
        print(f"🔍 Encontrada transferência: {transferencia_id}")
        
        # Preparar dados para Supabase
        dados_supabase = {
            'id': transferencia_id,
            'tipo': 'transferencia_internacional',
            'status': transferencia.get('status', 'solicitada'),
            'data': transferencia.get('data_solicitacao', datetime.now().isoformat()),
            'moeda': transferencia.get('moeda', 'USD'),
            'valor': float(transferencia.get('valor', 0)),
            'conta_remetente': transferencia.get('conta_remetente', ''),
            'descricao': transferencia.get('descricao', ''),
            'executado_por': transferencia.get('executado_por', ''),
            'beneficiario': transferencia.get('beneficiario', ''),
            'endereco_beneficiario': transferencia.get('endereco_beneficiario', ''),
            'cidade': transferencia.get('cidade', ''),
            'pais': transferencia.get('pais', ''),
            'nome_banco': transferencia.get('nome_banco', ''),
            'endereco_banco': transferencia.get('endereco_banco', ''),
            'codigo_swift': transferencia.get('codigo_swift', ''),
            'iban_account': transferencia.get('iban_account', ''),
            'aba_routing': transferencia.get('aba_routing', ''),
            'finalidade': transferencia.get('finalidade', ''),
            'created_at': datetime.now().isoformat()
        }
        
        print("📦 Dados preparados para Supabase:")
        for key, value in dados_supabase.items():
            print(f"   {key}: {value}")
        
        # Inserir no Supabase
        print(f"🌍 Migrando transferência {transferencia_id} para o Supabase...")
        response = supabase.table('transferencias').insert(dados_supabase).execute()
        
        if response.data:
            print(f"✅ Transferência {transferencia_id} migrada com sucesso para o Supabase!")
            print(f"📊 Dados inseridos: {response.data}")
            return True
        else:
            print(f"❌ Erro ao migrar transferência: {response.error}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 MIGRANDO TRANSFERÊNCIA 233695 PARA SUPABASE")
    print("=" * 50)
    
    sucesso = migrar_transferencia_233695()
    
    if sucesso:
        print("\n🎯 Migração concluída com sucesso!")
        print("💡 Agora faça uma nova transferência de teste para verificar se ambas funcionam.")
    else:
        print("\n❌ Falha na migração.")