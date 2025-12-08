"""
API Web para o Cambio Bank
Versão inicial - apenas endpoints básicos
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from flask import render_template, send_from_directory
from flask import Flask, jsonify, request, render_template, send_from_directory, redirect
import os
import hashlib

# Carrega variáveis de ambiente
load_dotenv()

# ============================================
# CONEXÃO COM SUPABASE
# ============================================

try:
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"DEBUG: Tentando conectar ao Supabase...")
    print(f"DEBUG: URL: {supabase_url}")
    print(f"DEBUG: Key (início): {supabase_key[:30] if supabase_key else 'None'}...")
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Conectado ao Supabase!")
        print(f"DEBUG: Conexão bem-sucedida!")
    else:
        print("⚠️  Variáveis do Supabase não encontradas")
        print(f"DEBUG: URL existe: {bool(supabase_url)}")
        print(f"DEBUG: Key existe: {bool(supabase_key)}")
        supabase = None
except Exception as e:
    print(f"❌ Erro ao conectar ao Supabase: {e}")
    import traceback
    traceback.print_exc()  # ← MOSTRA O ERRO COMPLETO
    supabase = None

# Cria app Flask
app = Flask(__name__)
CORS(app)  # Permite conexão do frontend

# ============================================
# ENDPOINTS BÁSICOS (VAMOS COMEÇAR COM ESTES)
# ============================================

@app.route('/')
def home():
    """Redireciona para a página de login"""
    return pagina_login()  # ⬅️ Alterado!

@app.route('/api')
def api_info():
    """Informações da API"""
    return jsonify({
        "status": "online",
        "app": "🏦 Cambio Bank API",
        "version": "2.0.0",
        "endpoints": {
            "/api/status": "Status do sistema",
            "/api/test": "Endpoint de teste", 
            "/api/echo": "Ecoa dados recebidos",
            "/api/test-supabase": "Testar conexão Supabase",
            "/api/login": "Login de usuário",
            "/login": "Página de login web",
            "/dashboard": "Dashboard (em construção)"
        }
    })

@app.route('/api/status')
def status():
    """Endpoint de status do sistema"""
    return jsonify({
        "status": "operacional",
        "database": "supabase",
        "responsivo": True,
        "timestamp": "2024-01-15T10:30:00Z"
    })

@app.route('/api/test', methods=['GET'])
def test():
    """Endpoint de teste simples"""
    return jsonify({
        "message": "API funcionando corretamente!",
        "success": True,
        "data": {
            "usuario": "sistema",
            "acao": "teste_conexao"
        }
    })

@app.route('/api/echo', methods=['POST'])
def echo():
    """Ecoa os dados recebidos (para teste)"""
    dados = request.json or {}
    return jsonify({
        "received": dados,
        "message": "Dados recebidos com sucesso!"
    })

@app.route('/api/test-supabase', methods=['GET'])
def test_supabase():
    """Testa conexão com o Supabase"""
    if supabase is None:
        return jsonify({
            "success": False,
            "message": "Supabase não configurado",
            "error": "Verifique as variáveis no .env"
        }), 500
    
    try:
        # Testa uma query simples (ajuste conforme suas tabelas)
        response = supabase.table('usuarios').select('count', count='exact').execute()
        
        return jsonify({
            "success": True,
            "message": "✅ Conexão com Supabase estabelecida!",
            "data": {
                "tabela": "usuarios",
                "contagem": response.count if hasattr(response, 'count') else "N/A"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "❌ Erro ao acessar Supabase",
            "error": str(e)
        }), 500

# ============================================
# CONFIGURAÇÃO DO SERVIDOR
# ============================================

@app.route('/api/login', methods=['POST'])
def login():
    """Autentica um usuário"""
    if supabase is None:
        return jsonify({
            "success": False,
            "message": "Sistema indisponível"
        }), 500
    
    try:
        dados = request.json
        
        if not dados:
            return jsonify({
                "success": False,
                "message": "Dados de login não fornecidos"
            }), 400
        
        usuario = dados.get('usuario')
        senha = dados.get('senha')
        
        if not usuario or not senha:
            return jsonify({
                "success": False,
                "message": "Usuário e senha são obrigatórios"
            }), 400
        
        # 🔐 Calcula o hash SHA-256 da senha fornecida
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        # 🔍 Busca o usuário no Supabase
        response = supabase.table('usuarios')\
            .select('*')\
            .eq('username', usuario)\
            .eq('senha_hash', senha_hash)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({
                "success": False,
                "message": "Usuário ou senha inválidos"
            }), 401
        
        usuario_data = response.data[0]
        
        # 🚫 Remove a senha da resposta por segurança
        if 'senha_hash' in usuario_data:
            del usuario_data['senha_hash']
        
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "usuario": usuario_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Erro ao processar login",
            "error": str(e)
        }), 500

# ============================================
# ENDPOINTS PARA FRONTEND
# ============================================

@app.route('/login')
def pagina_login():
    """Página de login"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Página do dashboard - requer login"""
    # Pega usuário da query string (simplificado)
    usuario = request.args.get('usuario')
    
    if not usuario:
        # Se não tem usuário, redireciona para login
        return redirect('/login')
    
    try:
        # Busca dados REAIS do Supabase
        if supabase:
            response = supabase.table('usuarios')\
                .select('username, email, nome, saldo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if response.data:
                dados = response.data
            else:
                dados = {
                    'usuario': usuario,
                    'email': f'{usuario}@exemplo.com',
                    'saldo': 48750.00
                }
        else:
            dados = {
                'usuario': usuario,
                'email': f'{usuario}@exemplo.com', 
                'saldo': 48750.00
            }
            
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        dados = {
            'usuario': usuario,
            'email': f'{usuario}@exemplo.com',
            'saldo': 48750.00
        }
    
    return render_template('dashboard.html', **dados)

@app.route('/static/<path:path>')
def servir_estaticos(path):
    """Serve arquivos estáticos (CSS, JS, imagens)"""
    return send_from_directory('static', path)

@app.route('/api/dashboard/<username>')
def dashboard_data(username):
    """Retorna dados para o dashboard do usuário"""
    if supabase is None:
        return jsonify({"success": False, "message": "Sistema indisponível"}), 500
    
    try:
        # 1. Busca dados do usuário
        usuario_res = supabase.table('usuarios')\
            .select('id, username, nome, email, tipo, status, cambio_liberado, contas')\
            .eq('username', username)\
            .single()\
            .execute()
        
        if not usuario_res.data:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 404
        
        usuario = usuario_res.data
        
        # 2. Busca saldo das contas
        saldo_total = 0
        contas_detalhes = []
        
        if usuario.get('contas'):
            for conta_id in usuario['contas']:
                try:
                    conta_res = supabase.table('contas')\
                        .select('id, saldo, moeda, cliente_username, cliente_nome, ativa')\
                        .eq('id', conta_id)\
                        .single()\
                        .execute()
                    
                    if conta_res.data:
                        conta = conta_res.data
                        contas_detalhes.append(conta)
                        saldo_total += float(conta.get('saldo', 0))
                except:
                    continue  # Se não encontrar a conta, continua
        
        # 3. Busca últimas transferências
        transferencias_res = supabase.table('transferencias')\
            .select('id, tipo, status, data, moeda, valor, conta_remetente, conta_destinatario, descricao, cliente, usuario')\
            .or_(f'cliente.eq.{username},usuario.eq.{username},conta_remetente.eq.{username},conta_destinatario.eq.{username}')\
            .order('data', desc=True)\
            .limit(10)\
            .execute()
        
        # 4. Conta beneficiários
        beneficiarios_res = supabase.table('beneficiarios')\
            .select('id, nome, banco, swift, iban, ativo')\
            .eq('cliente_username', username)\
            .execute()
        
        return jsonify({
            "success": True,
            "usuario": usuario,
            "dashboard": {
                "saldo_total": saldo_total,
                "contas": contas_detalhes,
                "quantidade_contas": len(contas_detalhes),
                "ultimas_transferencias": transferencias_res.data,
                "quantidade_beneficiarios": len(beneficiarios_res.data) if beneficiarios_res.data else 0,
                "beneficiarios": beneficiarios_res.data if beneficiarios_res.data else []
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Erro ao buscar dados do dashboard",
            "error": str(e)
        }), 500

@app.route('/logout')
def logout():
    return redirect('/login')

@app.route('/api/transacoes')
def get_transacoes():
    """Retorna transações de exemplo"""
    transacoes = [
        {
            "tipo": "sucesso",
            "descricao": "Transferência enviada",
            "detalhes": "Para: João Silva • TED",
            "valor": -2500.00,
            "data": "Hoje, 14:30"
        },
        {
            "tipo": "recebida", 
            "descricao": "Depósito recebido",
            "detalhes": "De: Empresa XYZ • DOC",
            "valor": 5000.00,
            "data": "Ontem, 09:15"
        }
    ]
    return jsonify(transacoes)

@app.route('/teste')
def teste():
    return render_template('teste.html')

@app.after_request
def add_header(response):
    """Adiciona headers para evitar cache e corrigir MIME types"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Corrige MIME type para CSS se necessário
    if response.mimetype == 'text/css' or response.mimetype == 'text/plain':
        response.headers['Content-Type'] = 'text/css; charset=utf-8'
    
    return response

@app.route('/api/transferencias/criar', methods=['POST'])
def criar_transferencia_cliente():
    """Cliente cria transferência internacional (igual ao app Python)"""
    try:
        dados = request.json
        
        print(f"📨 Dados recebidos: {dados}")
        
        # Validação básica (igual ao seu código Python)
        campos_obrigatorios = ['usuario', 'conta_origem', 'valor', 'moeda', 'beneficiario']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({
                    "success": False,
                    "message": f"Campo '{campo}' é obrigatório"
                }), 400
        
        # Criar ID único (igual ao seu sistema Python)
        import random
        from datetime import datetime
        transferencia_id = f"TRF{int(datetime.now().timestamp())}{random.randint(1000, 9999)}"
        
        # Preparar dados para Supabase (MESMOS CAMPOS do seu Python)
        dados_supabase = {
            'id': transferencia_id,
            'tipo': 'transferencia_internacional',
            'status': 'solicitada',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': dados['moeda'],
            'valor': float(dados['valor']),
            'conta_remetente': dados['conta_origem'],
            'descricao': dados.get('descricao', ''),
            'usuario': dados['usuario'],
            'cliente': dados['usuario'],  # 🔥 IGUAL AO SEU PYTHON
            'beneficiario': dados['beneficiario'],
            'endereco_beneficiario': dados.get('endereco', ''),
            'cidade': dados.get('cidade', ''),
            'pais': dados.get('pais', ''),
            'nome_banco': dados.get('banco', ''),
            'endereco_banco': dados.get('endereco_banco', ''),
            'cidade_banco': dados.get('cidade_banco', ''),
            'pais_banco': dados.get('pais_banco', ''),
            'codigo_swift': dados.get('swift', ''),
            'iban_account': dados.get('iban', ''),
            'aba_routing': dados.get('aba', ''),
            'finalidade': dados.get('finalidade', ''),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"💾 Salvando no Supabase: {transferencia_id}")
        
        # Salvar no Supabase (MESMA TABELA que seu Python usa)
        response = supabase.table('transferencias').insert(dados_supabase).execute()
        
        if response.data:
            return jsonify({
                "success": True,
                "message": "Transferência solicitada com sucesso!",
                "transferencia_id": transferencia_id,
                "dados": dados_supabase
            })
        else:
            return jsonify({
                "success": False,
                "message": "Erro ao salvar no banco de dados"
            }), 500
            
    except Exception as e:
        print(f"❌ Erro na API criar_transferencia: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500
    
@app.route('/api/user')
def get_user_info():
    """Retorna informações do usuário logado (mock por enquanto)"""
    # TODO: Implementar autenticação real
    return jsonify({
        "success": True,
        "user": {
            "username": "cliente_exemplo",
            "nome": "João da Silva",
            "tipo": "cliente"
        }
    })

@app.route('/api/user/contas')
def get_user_contas():
    """Retorna contas do usuário (mock por enquanto)"""
    # TODO: Buscar do Supabase baseado no usuário
    return jsonify({
        "success": True,
        "contas": [
            {
                "numero": "001234-5",
                "moeda": "USD",
                "saldo": 48750.00,
                "tipo": "corrente"
            },
            {
                "numero": "001235-6", 
                "moeda": "EUR",
                "saldo": 32500.00,
                "tipo": "corrente"
            },
            {
                "numero": "001236-7",
                "moeda": "GBP", 
                "saldo": 28000.00,
                "tipo": "corrente"
            }
        ]
    })

@app.route('/api/beneficiarios')
def get_beneficiarios():
    """Retorna beneficiários salvos (mock por enquanto)"""
    # TODO: Buscar do Supabase baseado no usuário
    return jsonify({
        "success": True,
        "beneficiarios": [
            {
                "id": "1",
                "nome": "Microsoft Corporation",
                "banco": "JPMorgan Chase Bank",
                "pais": "Estados Unidos"
            },
            {
                "id": "2",
                "nome": "Amazon Web Services",
                "banco": "Bank of America", 
                "pais": "Estados Unidos"
            }
        ]
    })

@app.route('/transferencia')
def tela_transferencia():
    """Renderiza a tela de transferência internacional"""
    return render_template('transferencia.html')

# ============================================================================
# APIs PARA TRANSFERÊNCIA (MOCK - DEPOIS SUBSTITUI POR SUPABASE)
# ============================================================================

@app.route('/api/user')
def get_user_info_web():
    """Retorna informações do usuário logado"""
    return jsonify({
        "success": True,
        "user": {
            "username": "cliente_exemplo",
            "nome": "João da Silva",
            "email": "joao@email.com",
            "tipo": "cliente"
        }
    })

@app.route('/api/user/contas')
def get_user_contas_web():
    """Retorna contas do usuário"""
    return jsonify({
        "success": True,
        "contas": [
            {
                "numero": "001234-5",
                "moeda": "USD",
                "saldo": 48750.00,
                "tipo": "corrente",
                "descricao": "Conta Corrente USD"
            },
            {
                "numero": "001235-6",
                "moeda": "EUR",
                "saldo": 32500.00,
                "tipo": "corrente",
                "descricao": "Conta Corrente EUR"
            },
            {
                "numero": "001236-7",
                "moeda": "GBP",
                "saldo": 28000.00,
                "tipo": "corrente",
                "descricao": "Conta Corrente GBP"
            }
        ]
    })

@app.route('/api/beneficiarios')
def get_beneficiarios_web():
    """Retorna beneficiários salvos do usuário"""
    return jsonify({
        "success": True,
        "beneficiarios": [
            {
                "id": "1",
                "nome": "Microsoft Corporation",
                "endereco": "One Microsoft Way, Redmond",
                "cidade": "Redmond",
                "pais": "Estados Unidos",
                "banco": "JPMorgan Chase Bank",
                "swift": "CHASUS33XXX",
                "iban": "US12345678901234567890"
            },
            {
                "id": "2",
                "nome": "Amazon Web Services",
                "endereco": "410 Terry Ave N, Seattle",
                "cidade": "Seattle",
                "pais": "Estados Unidos",
                "banco": "Bank of America",
                "swift": "BOFAUS3NXXX",
                "iban": "US09876543210987654321"
            }
        ]
    })

@app.route('/api/beneficiarios/<benef_id>')
def get_beneficiario_web(benef_id):
    """Retorna um beneficiário específico"""
    beneficiarios = {
        "1": {
            "id": "1",
            "nome": "Microsoft Corporation",
            "endereco": "One Microsoft Way, Redmond",
            "cidade": "Redmond",
            "pais": "Estados Unidos",
            "banco": "JPMorgan Chase Bank",
            "endereco_banco": "383 Madison Avenue, New York",
            "cidade_banco": "New York",
            "pais_banco": "Estados Unidos",
            "swift": "CHASUS33XXX",
            "iban": "US12345678901234567890",
            "aba": "021000021"
        },
        "2": {
            "id": "2",
            "nome": "Amazon Web Services",
            "endereco": "410 Terry Ave N, Seattle",
            "cidade": "Seattle",
            "pais": "Estados Unidos",
            "banco": "Bank of America",
            "endereco_banco": "100 North Tryon Street, Charlotte",
            "cidade_banco": "Charlotte",
            "pais_banco": "Estados Unidos",
            "swift": "BOFAUS3NXXX",
            "iban": "US09876543210987654321",
            "aba": "026009593"
        }
    }
    
    if benef_id in beneficiarios:
        return jsonify({
            "success": True,
            "beneficiario": beneficiarios[benef_id]
        })
    
    return jsonify({
        "success": False,
        "message": "Beneficiário não encontrado"
    }), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 50)
    print("🚀 INICIANDO API FLASK DO CAMBIO BANK")
    print("=" * 50)
    print(f"📡 URL: http://localhost:{port}")
    print(f"🏠 Home: http://localhost:{port}/")
    print(f"📊 Status: http://localhost:{port}/api/status")
    print(f"🔗 Supabase: http://localhost:{port}/api/test-supabase")
    print("=" * 50)
    
    app.run(debug=debug, port=port)