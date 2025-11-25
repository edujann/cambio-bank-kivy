from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def verificar_transferencias_supabase():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)
    
    print("🔍 VERIFICANDO TRANSFERÊNCIAS NO SUPABASE:")
    
    try:
        response = supabase.table('transferencias').select('*').execute()
        print(f"📊 Total de transferências no Supabase: {len(response.data)}")
        
        if response.data:
            print("📋 Primeiras 5 transferências:")
            for i, transf in enumerate(response.data[:5]):
                print(f"   {i+1}. ID: {transf.get('id')} | Tipo: {transf.get('tipo')} | Valor: {transf.get('valor')}")
        else:
            print("❌ Nenhuma transferência encontrada no Supabase!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar transferências: {e}")

if __name__ == "__main__":
    verificar_transferencias_supabase()