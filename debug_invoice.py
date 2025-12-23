import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.append(r'C:\Users\Usuário\Desktop\cambio_bank_kivy')

# Tenta importar o sistema
try:
    # Primeiro, simula um ambiente Kivy mínimo
    os.environ['KIVY_NO_CONSOLELOG'] = '1'
    
    # Importa apenas o necessário
    from app.sistema import SistemaCambioPremium
    
    print("🔍 CRIANDO SISTEMA PARA DEBUG...")
    
    # Cria uma instância do sistema
    sistema = SistemaCambioPremium()
    
    # Verifica se conectou ao Supabase
    if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
        print("✅ Conectado ao Supabase!")
        
        # Testa a transferência 943510
        print("\n📊 VERIFICANDO TRANSFERÊNCIA 943510:")
        
        # Método 1: Buscar direto no Supabase
        try:
            from supabase import create_client
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if supabase_url and supabase_key:
                supabase = create_client(supabase_url, supabase_key)
                
                # Buscar transferência
                response = supabase.table('transferencias')\
                    .select('invoice_info, id, status')\
                    .eq('id', '943510')\
                    .execute()
                
                if response.data:
                    print("✅ Transferência encontrada no Supabase!")
                    dados = response.data[0]
                    
                    print(f"\n📋 DADOS DA TRANSFERÊNCIA:")
                    print(f"   ID: {dados['id']}")
                    print(f"   Status: {dados['status']}")
                    
                    if dados.get('invoice_info'):
                        invoice = dados['invoice_info']
                        print(f"\n📄 INFORMAÇÕES DA INVOICE:")
                        print(f"   Status: {invoice.get('status')}")
                        print(f"   Caminho: {invoice.get('caminho_arquivo')}")
                        print(f"   Data Upload: {invoice.get('data_upload')}")
                        
                        # Verificar se arquivo existe no Storage
                        caminho = invoice.get('caminho_arquivo')
                        if caminho:
                            print(f"\n🔍 VERIFICANDO STORAGE: {caminho}")
                            try:
                                response = supabase.storage.from_("invoices")\
                                    .download(caminho)
                                print("✅ ARQUIVO EXISTE NO STORAGE!")
                            except Exception as e:
                                print(f"❌ ARQUIVO NÃO ENCONTRADO: {e}")
                    else:
                        print("⚠️ Sem informações de invoice")
                else:
                    print("❌ Transferência não encontrada")
                    
        except Exception as e:
            print(f"❌ Erro ao buscar no Supabase: {e}")
            
    else:
        print("❌ Não conectado ao Supabase")
        
except Exception as e:
    print(f"❌ ERRO GERAL: {e}")
    import traceback
    traceback.print_exc()

input("\nPressione Enter para sair...")