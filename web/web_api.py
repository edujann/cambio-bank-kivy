"""
API Web para o Cambio Bank
Versão CORRIGIDA - Sem duplicações
"""
from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import hashlib
import json
import random
from datetime import datetime
import secrets
import traceback

# Carrega variáveis de ambiente
load_dotenv()

# ============================================
# CONEXÃO COM SUPABASE
# ============================================

try:
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"✅ Conectando ao Supabase...")
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Conectado ao Supabase!")
    else:
        print("⚠️ Variáveis do Supabase não encontradas")
        supabase = None
except Exception as e:
    print(f"❌ Erro ao conectar ao Supabase: {e}")
    supabase = None

# Cria app Flask
app = Flask(__name__)
CORS(app)

# Configurar sessões
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# ============================================
# ENDPOINTS BÁSICOS
# ============================================

@app.route('/')
def home():
    """Redireciona para login"""
    return redirect('/login')

@app.route('/api/status')
def status():
    """Status do sistema"""
    return jsonify({"status": "operacional", "database": "supabase"})

@app.route('/api/test-supabase', methods=['GET'])
def test_supabase():
    """Testa conexão com Supabase"""
    if supabase is None:
        return jsonify({"success": False, "message": "Supabase não configurado"}), 500
    
    try:
        response = supabase.table('usuarios').select('count', count='exact').execute()
        return jsonify({
            "success": True,
            "message": "✅ Conexão com Supabase OK!",
            "data": {"contagem": response.count if hasattr(response, 'count') else "N/A"}
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Erro: {str(e)}"}), 500

# ============================================
# AUTENTICAÇÃO
# ============================================

@app.route('/login')
def pagina_login():
    """Página de login"""
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Autentica usuário"""
    if supabase is None:
        return jsonify({"success": False, "message": "Sistema indisponível"}), 500
    
    try:
        dados = request.json
        if not dados:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        usuario = dados.get('usuario')
        senha = dados.get('senha')
        
        if not usuario or not senha:
            return jsonify({"success": False, "message": "Usuário/senha obrigatórios"}), 400
        
        # Hash da senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        # Buscar usuário
        response = supabase.table('usuarios')\
            .select('*')\
            .eq('username', usuario)\
            .eq('senha_hash', senha_hash)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Credenciais inválidas"}), 401
        
        usuario_data = response.data[0]
        
        # Salvar na sessão
        session['username'] = usuario_data['username']
        session['nome'] = usuario_data.get('nome', usuario_data['username'])
        session['email'] = usuario_data.get('email', f"{usuario_data['username']}@exemplo.com")
        session['user_id'] = usuario_data['id']
        
        # Remover hash da resposta
        if 'senha_hash' in usuario_data:
            del usuario_data['senha_hash']
        
        return jsonify({
            "success": True,
            "message": "Login realizado",
            "usuario": usuario_data
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

@app.route('/logout')
def logout():
    """Faz logout"""
    session.clear()
    return redirect('/login')

# ============================================
# PÁGINAS PRINCIPAIS
# ============================================

@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário"""
    usuario = session.get('username')
    if not usuario:
        return redirect('/login')
    
    # Buscar dados do usuário
    email = f'{usuario}@exemplo.com'
    nome = usuario.upper()
    
    if supabase:
        try:
            response = supabase.table('usuarios')\
                .select('email, nome')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if response.data:
                if response.data.get('email'):
                    email = response.data['email']
                if response.data.get('nome'):
                    nome = response.data['nome']
        except:
            pass
    
    return render_template('dashboard.html', 
                          usuario=usuario,
                          nome=nome,
                          email=email)

@app.route('/transferencia')
def tela_transferencia():
    """Tela de transferência internacional"""
    usuario = session.get('username')
    if not usuario:
        return redirect('/login')
    
    # Buscar dados do usuário
    email = f'{usuario}@exemplo.com'
    nome = usuario.upper()
    
    if supabase:
        try:
            response = supabase.table('usuarios')\
                .select('email, nome')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if response.data:
                if response.data.get('email'):
                    email = response.data['email']
                if response.data.get('nome'):
                    nome = response.data['nome']
        except:
            pass
    
    return render_template('transferencia.html', 
                          usuario=usuario,
                          nome=nome,
                          email=email)

# ============================================
# ENDPOINTS DE DADOS (APIs)
# ============================================

@app.route('/api/user')
def get_user_info():
    """Retorna dados do usuário logado"""
    usuario = session.get('username')
    if not usuario:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    try:
        response = supabase.table('usuarios')\
            .select('username, nome, email, tipo, telefone, verificado, cambio_liberado')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if response.data:
            return jsonify({"success": True, "user": response.data})
        else:
            return jsonify({
                "success": True,
                "user": {
                    "username": usuario,
                    "nome": usuario.upper(),
                    "email": f"{usuario}@exemplo.com",
                    "tipo": "cliente",
                    "verificado": True,
                    "cambio_liberado": True
                }
            })
    except Exception as e:
        print(f"❌ Erro ao buscar usuário: {e}")
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

@app.route('/api/user/contas')
def get_user_contas():
    """Retorna contas do usuário"""
    usuario = session.get('username')
    if not usuario:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    try:
        response = supabase.table('contas')\
            .select('id, moeda, saldo, cliente_username, cliente_nome, ativa')\
            .eq('cliente_username', usuario)\
            .eq('ativa', True)\
            .execute()
        
        if response.data:
            return jsonify({"success": True, "contas": response.data})
        else:
            return jsonify({"success": True, "contas": []})
    except Exception as e:
        print(f"❌ Erro ao buscar contas: {e}")
        return jsonify({"success": False, "message": f"Erro: {str(e)}", "contas": []}), 500

@app.route('/api/beneficiarios', methods=['GET', 'POST'])
def handle_beneficiarios():
    """GET: Lista beneficiários | POST: Cria beneficiário"""
    usuario = session.get('username')
    if not usuario:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    try:
        # POST - Criar beneficiário
        if request.method == 'POST':
            dados = request.get_json()
            if not dados:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            
            # Validar campos
            if not dados.get('nome'):
                return jsonify({"success": False, "message": "Nome obrigatório"}), 400
            if not dados.get('banco'):
                return jsonify({"success": False, "message": "Banco obrigatório"}), 400
            
            novo_beneficiario = {
                'nome': dados['nome'],
                'endereco': dados.get('endereco', ''),
                'cidade': dados.get('cidade', ''),
                'pais': dados.get('pais', ''),
                'banco': dados['banco'],
                'endereco_banco': dados.get('endereco_banco', ''),
                'cidade_banco': dados.get('cidade_banco', ''),
                'pais_banco': dados.get('pais_banco', ''),
                'swift': dados.get('swift', ''),
                'iban': dados.get('iban', ''),
                'aba': dados.get('aba', ''),
                'cliente_username': usuario,
                'ativo': True,
                'criado_em': datetime.now().isoformat()
            }
            
            print(f"💾 Salvando beneficiário: {novo_beneficiario['nome']}")
            
            response = supabase.table('beneficiarios').insert(novo_beneficiario).execute()
            
            if response.data:
                return jsonify({
                    "success": True,
                    "message": "Beneficiário salvo",
                    "id": response.data[0]['id']
                })
            else:
                return jsonify({"success": False, "message": "Erro ao salvar"}), 500
        
        # GET - Listar beneficiários
        else:
            response = supabase.table('beneficiarios')\
                .select('id, nome, endereco, cidade, pais, banco, swift, iban, aba, cidade_banco, pais_banco, endereco_banco')\
                .eq('cliente_username', usuario)\
                .eq('ativo', True)\
                .execute()
            
            if response.data:
                return jsonify({"success": True, "beneficiarios": response.data})
            else:
                return jsonify({"success": True, "beneficiarios": []})
                
    except Exception as e:
        print(f"❌ Erro em beneficiários: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

@app.route('/api/beneficiarios/<int:benef_id>')
def get_beneficiario_detalhe(benef_id):
    """Retorna detalhes de um beneficiário"""
    usuario = session.get('username')
    if not usuario:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    try:
        response = supabase.table('beneficiarios')\
            .select('id, nome, endereco, cidade, pais, banco, endereco_banco, cidade_banco, pais_banco, swift, iban, aba')\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .eq('ativo', True)\
            .single()\
            .execute()
        
        if response.data:
            return jsonify({"success": True, "beneficiario": response.data})
        else:
            return jsonify({"success": False, "message": "Não encontrado"}), 404
    except Exception as e:
        print(f"❌ Erro ao buscar beneficiário: {e}")
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

# ============================================
# TRANSFERÊNCIA INTERNACIONAL (ENDPOINT PRINCIPAL)
# ============================================

@app.route('/api/transferencias/criar', methods=['POST'])
def criar_transferencia():
    """Cria uma transferência internacional"""
    print("\n" + "="*60)
    print("🚀 INICIANDO CRIAÇÃO DE TRANSFERÊNCIA")
    print("="*60)
    
    try:
        # 1. Verificar autenticação
        usuario = session.get('username')
        if not usuario:
            print("❌ Usuário não autenticado")
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        print(f"✅ Usuário: {usuario}")
        
        # 2. Obter dados
        dados = {}
        
        if request.is_json:
            dados = request.json
            print("📦 Dados via JSON")
        elif request.form:
            dados_str = request.form.get('dados', '{}')
            try:
                dados = json.loads(dados_str)
                print("📦 Dados via FormData")
            except json.JSONDecodeError as e:
                print(f"❌ JSON inválido: {e}")
                return jsonify({"success": False, "message": "Dados inválidos"}), 400
        else:
            print("❌ Formato não suportado")
            return jsonify({"success": False, "message": "Formato não suportado"}), 400

        # 🔍🔍🔍 ADICIONE ESTAS 4 LINHAS 🔍🔍🔍
        print(f"✅ Dados recebidos como JSON")
        print("\n📋 TODOS OS CAMPOS RECEBIDOS:")
        for chave, valor in dados.items():
            print(f"   {chave}: {repr(valor)}")
        print("="*60)
        
        # 3. Validar campos obrigatórios
        campos_obrigatorios = ['conta_origem', 'valor', 'moeda', 'beneficiario']
        for campo in campos_obrigatorios:
            if campo not in dados or not str(dados[campo]).strip():
                print(f"❌ Campo faltando: {campo}")
                return jsonify({"success": False, "message": f"Campo '{campo}' obrigatório"}), 400
        
        # 4. Buscar e validar conta
        conta_id = dados['conta_origem']
        response_conta = supabase.table('contas')\
            .select('id, saldo, cliente_username, moeda')\
            .eq('id', conta_id)\
            .eq('cliente_username', usuario)\
            .eq('ativa', True)\
            .execute()
        
        if not response_conta.data:
            print(f"❌ Conta não encontrada: {conta_id}")
            return jsonify({"success": False, "message": "Conta não encontrada"}), 400
        
        conta = response_conta.data[0]
        saldo_atual = float(conta['saldo']) if conta['saldo'] else 0.0
        
        # Converter valor para float CORRETAMENTE
        try:
            # Tenta converter independente do tipo
            valor_str = str(dados['valor']).replace(',', '.')
            valor = float(valor_str)
        except (ValueError, TypeError):
            print(f"❌ Erro ao converter valor: {dados['valor']}")
            valor = 0.0
        
        print(f"💰 Saldo atual: {saldo_atual}, Valor convertido: {valor} (tipo: {type(valor)})")
        
        print(f"💰 Conta: {conta_id}, Saldo: {saldo_atual}, Valor: {valor}")
        
        # 5. Verificar saldo
        if valor > saldo_atual:
            print(f"❌ Saldo insuficiente")
            return jsonify({"success": False, "message": f"Saldo insuficiente. Disponível: {saldo_atual:.2f}"}), 400
        
        # 6. Verificar moeda
        if conta.get('moeda') != dados['moeda']:
            print(f"❌ Moeda diferente: conta={conta.get('moeda')}, transf={dados['moeda']}")
            return jsonify({"success": False, "message": "Moeda da conta não corresponde"}), 400
        
        # 7. Criar ID da transferência
        transferencia_id = str(random.randint(100000, 999999))
        agora = datetime.now()
        
        # 8. Preparar dados para Supabase
        dados_supabase = {
            'id': transferencia_id,
            'tipo': 'transferencia_internacional',
            'status': 'solicitada',
            'data': agora.strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': dados['moeda'],
            'valor': valor,
            'conta_remetente': conta_id,
            'descricao': dados.get('descricao', ''),
            'usuario': usuario,
            'cliente': usuario,
            'beneficiario': dados['beneficiario'],
            'endereco_beneficiario': dados.get('endereco_beneficiario', ''),
            'cidade': dados.get('cidade', ''),
            'pais': dados.get('pais', ''),
            'nome_banco': dados.get('nome_banco', ''),
            'endereco_banco': dados.get('endereco_banco', ''),
            'cidade_banco': dados.get('cidade_banco', ''),
            'pais_banco': dados.get('pais_banco', ''),
            'codigo_swift': dados.get('codigo_swift', ''),
            'iban_account': dados.get('iban_account', ''),
            'aba_routing': dados.get('aba_routing', ''),
            'finalidade': dados.get('finalidade', ''),
            'created_at': agora.isoformat(),
            'data_solicitacao': agora.isoformat(),
            'solicitado_por': usuario
        }

        # 🔍 PRIMEIRO: VERIFIQUE SE CHEGA AQUI
        print(f"\n" + "="*60)
        print(f"🔍 ETAPA 1: CHEGOU ATÉ AQUI?")
        print(f"   Tem dados_supabase? {bool(dados_supabase)}")
        print(f"   Número de campos: {len(dados_supabase)}")
        print(f"="*60)

        # 🔍 SEGUNDO: DEBUG COMPLETO
        print(f"\n" + "="*60)
        print(f"🔍 DEBUG COMPLETO - dados_supabase:")
        print(f"="*60)
        for chave, valor in dados_supabase.items():
            print(f"   {chave}: {repr(valor)}")
        
        print(f"="*60 + "\n")

        # 9. Salvar no Supabase
        print(f"💾 Salvando transferência {transferencia_id}...")
        response = supabase.table('transferencias').insert(dados_supabase).execute()
        
        if not response.data:
            print(f"❌ Erro ao salvar no Supabase")
            return jsonify({"success": False, "message": "Erro ao salvar transferência"}), 500
        
        print(f"✅ Transferência salva: {transferencia_id}")
        
        # 10. Atualizar saldo da conta
        novo_saldo = saldo_atual - valor
        supabase.table('contas')\
            .update({'saldo': novo_saldo})\
            .eq('id', conta_id)\
            .execute()
        
        print(f"💸 Saldo atualizado: {novo_saldo}")
        
        # 11. Upload de arquivo (opcional)
        if 'invoice' in request.files:
            arquivo = request.files['invoice']
            if arquivo and arquivo.filename:
                try:
                    nome_seguro = f"invoice_{agora.strftime('%Y%m%d_%H%M%S')}_{arquivo.filename}"
                    caminho = f"transferencias/{transferencia_id}/{nome_seguro}"
                    arquivo_bytes = arquivo.read()
                    
                    # Upload para storage
                    supabase.storage.from_("invoices").upload(
                        caminho,
                        arquivo_bytes,
                        file_options={"content-type": arquivo.content_type}
                    )
                    
                    # Atualizar transferência com info do invoice
                    supabase.table('transferencias').update({
                        'invoice_info': {
                            'caminho_arquivo': caminho,
                            'nome_arquivo': arquivo.filename,
                            'tipo': arquivo.content_type,
                            'tamanho': len(arquivo_bytes),
                            'status': 'pending',
                            'data_upload': agora.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }).eq('id', transferencia_id).execute()
                    
                    print(f"📎 Invoice salvo: {arquivo.filename}")
                except Exception as upload_error:
                    print(f"⚠️ Erro no upload: {upload_error}")
        
        print("="*60)
        print("🎉 TRANSFERÊNCIA CRIADA COM SUCESSO!")
        print("="*60)
        
        return jsonify({
            "success": True,
            "message": "Transferência solicitada!",
            "transferencia_id": transferencia_id
        })
        
    except Exception as e:
        print(f"❌❌❌ ERRO CRÍTICO: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

# ============================================
# SERVIÇOS AUXILIARES
# ============================================

@app.route('/static/<path:path>')
def servir_estaticos(path):
    """Serve arquivos estáticos"""
    return send_from_directory('static', path)

@app.after_request
def add_header(response):
    """Headers para evitar cache"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ============================================
# INICIALIZAÇÃO
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("="*50)
    print("🚀 API FLASK - CAMBIO BANK")
    print(f"📡 Porta: {port}")
    print(f"🐛 Debug: {debug}")
    print("="*50)
    
    app.run(debug=debug, port=port)