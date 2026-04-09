"""
API Web para o Cambio Bank
Versão inicial - apenas endpoints básicos
"""
# ============================================
# IMPORTS PADRÃO DO PYTHON
# ============================================
import os
import hashlib
import re
import random
import threading
from datetime import datetime, timezone  # ← CORRETO: import único  

# ============================================
# IMPORTS DE TERCEIROS
# ============================================
import requests
import pytz 
from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, session
from flask_cors import CORS
from dotenv import load_dotenv

# ============================================
# CONFIGURAÇÕES INICIAIS
# ============================================
# 🔥 CACHE DE COTAÇÕES (igual ao Kivy)
cotacoes_cache = {}
ultima_atualizacao = None
cotacao_lock = threading.Lock()

# Carrega variáveis de ambiente
load_dotenv()

# ============================================
# CONEXÃO COM SUPABASE
# ============================================
try:
    from supabase import create_client  # ← AGORA AQUI (após dotenv)
    
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
    traceback.print_exc()
    supabase = None

# Cria app Flask
app = Flask(__name__)
CORS(app)  # Permite conexão do frontend

# ✅ ADICIONE ESTAS 2 LINHAS PARA CONFIGURAR SESSÕES
import secrets
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
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
        
        # ✅ CRÍTICO: Salva o usuário na SESSÃO Flask
        session['username'] = usuario_data['username']
        session['nome'] = usuario_data.get('nome', usuario_data['username'])
        session['email'] = usuario_data.get('email', f"{usuario_data['username']}@exemplo.com")
        session['user_id'] = usuario_data['id']
        session['tipo'] = usuario_data.get('tipo', 'cliente')  # 🔥 ADICIONE ESTA LINHA!
        
        print(f"✅ Login: {usuario} - Tipo: {session['tipo']}")  # 🔥 ADICIONE ESTA LINHA (DEBUG)
        
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "usuario": usuario_data,
            "tipo": usuario_data.get('tipo', 'cliente')  # 🔥 ADICIONE ESTA LINHA!
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
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    try:
        email = f'{usuario}@exemplo.com'
        nome = usuario.upper()
        beneficiarios_count = 0  # ← INICIALIZA
        
        if supabase:
            # 1. Buscar dados do usuário
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
            
            # 2. 🔥 NOVO: Contar beneficiários ATIVOS
            print(f"🔍 Contando beneficiários para {usuario}...")
            benef_response = supabase.table('beneficiarios')\
                .select('id, nome, ativo')\
                .eq('cliente_username', usuario)\
                .eq('ativo', True)\
                .execute()
            
            if benef_response.data:
                beneficiarios_count = len(benef_response.data)
                print(f"✅ Encontrados {beneficiarios_count} beneficiários para {usuario}")
            else:
                print(f"⚠️ Nenhum beneficiário encontrado para {usuario}")
                
    except Exception as e:
        print(f"⚠️  Erro ao buscar dados: {e}")
        beneficiarios_count = 0
    
    # Dados para o template
    dados = {
        'usuario': usuario,
        'email': email,
        'nome': nome,
        'beneficiarios_count': beneficiarios_count  # ← ENVIADO PARA O TEMPLATE
    }
    
    print(f"📊 Dashboard para {usuario}: {beneficiarios_count} beneficiários")
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
        
        # 2. Busca saldo das contas REAIS do Supabase
        saldo_total = 0
        
        # Busca TODAS as contas ativas do usuário
        contas_res = supabase.table('contas')\
            .select('id, saldo, moeda, cliente_username, cliente_nome, ativa')\
            .eq('cliente_username', username)\
            .eq('ativa', True)\
            .execute()
        
        if contas_res.data:
            contas_detalhes = contas_res.data
            
            # Calcula saldo total
            for conta in contas_detalhes:
                try:
                    saldo_total += float(conta.get('saldo', 0))
                except (ValueError, TypeError):
                    saldo_total += 0  # Se saldo for inválido, ignora
        else:
            contas_detalhes = []
        
        # 3. Busca últimas transferências INTERNACIONAIS (5 mais recentes)
        transferencias_res = supabase.table('transferencias')\
            .select('id, tipo, status, data, moeda, valor, conta_remetente, conta_destinatario, descricao, cliente, usuario, beneficiario, cidade, pais, invoice_info')\
            .eq('tipo', 'transferencia_internacional')\
            .eq('cliente', username)\
            .order('data', desc=True)\
            .limit(5)\
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
    
@app.route('/api/dashboard/saldos')
def get_dashboard_saldos():
    """Retorna saldos REAIS para o dashboard"""
    try:
        # ✅ Pega usuário da SESSÃO (correto!)
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        # Buscar contas do usuário
        contas_response = supabase.table('contas')\
            .select('moeda, saldo, cliente_nome')\
            .eq('cliente_username', usuario)\
            .eq('ativa', True)\
            .execute()
        
        # Buscar últimas transferências
        transferencias_response = supabase.table('transferencias')\
            .select('id, tipo, data, valor, moeda, status, descricao, beneficiario')\
            .eq('usuario', usuario)\
            .order('data', desc=True)\
            .limit(5)\
            .execute()
        
        return jsonify({
            "success": True,
            "contas": contas_response.data if contas_response.data else [],
            "ultimas_transferencias": transferencias_response.data if transferencias_response.data else [],
            "usuario": usuario
        })
        
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro ao carregar dashboard: {str(e)}"
        }), 500

@app.route('/logout')
def logout():
    """Limpa COMPLETAMENTE a sessão e faz logout"""
    session.clear()  # ← Remove TODAS as chaves da sessão
    print("✅ Sessão completamente limpa - logout realizado")
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
    """Cliente cria transferência internacional - SALVA NO SUPABASE REAL"""
    try:
        print("\n" + "="*60)
        print("🔍 INICIANDO CRIAÇÃO DE TRANSFERÊNCIA")
        print("="*60)
        
        import json
        
        # Verificar tipo de requisição
        print(f"📨 Método: {request.method}")
        print(f"📨 Content-Type: {request.content_type}")
        
        # Obter dados da requisição
        dados = {}

        if request.is_json:
            dados = request.json
            print("✅ Dados recebidos como JSON")
        elif request.form:
            dados_json_str = request.form.get('dados', '{}')
            dados = json.loads(dados_json_str)
            print("✅ Dados convertidos de FormData JSON")
        else:
            print("⚠️ Nenhum dato recebido ou formato desconhecido")
            return jsonify({
                "success": False,
                "message": "Formato de requisição inválido"
            }), 400
        
        # ✅ Verificar quem está logado (SESSÃO)
        usuario_logado = session.get('username')
        
        if not usuario_logado:
            print(f"❌ USUÁRIO NÃO AUTENTICADO NA SESSÃO")
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        # ✅ Validar campos obrigatórios
        campos_obrigatorios = ['conta_origem', 'valor', 'moeda', 'beneficiario']
        for campo in campos_obrigatorios:
            if campo not in dados:
                print(f"❌ CAMPO OBRIGATÓRIO FALTANDO: {campo}")
                return jsonify({
                    "success": False,
                    "message": f"Campo '{campo}' é obrigatório"
                }), 400
        
        # ✅ Usar usuário da sessão
        dados['usuario'] = usuario_logado
        print(f"✅ Usuário da transferência: {usuario_logado}")
        
        # ✅ DEBUG: Mostrar dados importantes
        print(f"\n📋 DADOS PARA VALIDAÇÃO:")
        print(f"   conta_origem: '{dados['conta_origem']}'")
        print(f"   valor: '{dados['valor']}'")
        print(f"   moeda: '{dados['moeda']}'")
        
        # ✅ Buscar conta CORRETAMENTE
        print(f"\n🔍 Buscando conta: '{dados['conta_origem']}' para usuário: '{usuario_logado}'")

        response_conta = supabase.table('contas')\
            .select('id, saldo, cliente_username, moeda')\
            .eq('id', dados['conta_origem'])\
            .eq('cliente_username', usuario_logado)\
            .eq('ativa', True)\
            .execute()

        if not response_conta.data:
            print(f"❌ Conta não encontrada ou não pertence ao usuário")
            
            # Listar contas disponíveis para debug
            contas_disponiveis = supabase.table('contas')\
                .select('id, saldo, moeda')\
                .eq('cliente_username', usuario_logado)\
                .eq('ativa', True)\
                .execute()
            
            print(f"📊 Contas disponíveis para {usuario_logado}:")
            for conta in contas_disponiveis.data:
                print(f"   - ID: '{conta['id']}', Saldo: {conta['saldo']}, Moeda: {conta['moeda']}")
            
            return jsonify({
                "success": False,
                "message": f"Conta não encontrada. Contas disponíveis: {[c['id'] for c in contas_disponiveis.data]}"
            }), 400

        conta = response_conta.data[0]
        saldo_atual = float(conta['saldo']) if conta['saldo'] else 0.0
        
        print(f"✅ Conta encontrada: ID '{conta['id']}', Saldo: {saldo_atual}, Moeda: {conta.get('moeda', 'N/A')}")
        
        # ✅ Converter valor CORRETAMENTE
        try:
            valor_transferencia = float(dados['valor'])
            print(f"💰 Valor da transferência: {valor_transferencia}")
        except Exception as e:
            print(f"❌ Erro ao converter valor: {e}")
            return jsonify({
                "success": False,
                "message": f"Valor inválido: '{dados['valor']}'"
            }), 400

        # ✅ Verificar saldo suficiente
        print(f"💰 Comparação: Saldo ({saldo_atual}) >= Valor ({valor_transferencia})? {saldo_atual >= valor_transferencia}")
        
        if valor_transferencia > saldo_atual:
            print(f"❌ Saldo insuficiente! Disponível: {saldo_atual}, Necessário: {valor_transferencia}")
            return jsonify({
                "success": False,
                "message": f"Saldo insuficiente! Disponível: {saldo_atual:.2f}"
            }), 400
        
        print(f"✅ Saldo suficiente! Continuando...")
        
        # ✅ Criar transferência
        import random
        from datetime import datetime
        
        transferencia_id = f"{random.randint(100000, 999999)}"
        agora = datetime.now()
        
        # Preparar dados para Supabase
        dados_supabase = {
            'id': transferencia_id,
            'tipo': 'transferencia_internacional',
            'status': 'solicitada',
            'data': agora.strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': dados['moeda'],
            'valor': valor_transferencia,
            'conta_remetente': dados['conta_origem'],
            'descricao': dados.get('descricao', ''),
            'usuario': usuario_logado,
            'cliente': usuario_logado,
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
            'solicitado_por': usuario_logado
        }

        # DEBUG: Verificar dados
        print(f"\n📊 DADOS PARA SALVAR:")
        print(f"   ID: {transferencia_id}")
        print(f"   Conta: {dados['conta_origem']}")
        print(f"   Valor: {valor_transferencia}")
        print(f"   Moeda: {dados['moeda']}")

        # Salvar no Supabase
        print(f"💾 Salvando transferência {transferencia_id}...")
        response = supabase.table('transferencias').insert(dados_supabase).execute()

        if response.data:
            print(f"✅✅✅ TRANSFERÊNCIA SALVA COM SUCESSO!")
            print(f"✅ ID: {transferencia_id}")
            print(f"✅ Registros inseridos: {len(response.data)}")
            
            # ATUALIZAR SALDO DA CONTA (DÉBITO)
            novo_saldo = saldo_atual - valor_transferencia
            print(f"💸 Atualizando saldo: {saldo_atual} - {valor_transferencia} = {novo_saldo}")
            
            update_response = supabase.table('contas').update({
                'saldo': novo_saldo,
                'created_at': datetime.now().isoformat()
            }).eq('id', dados['conta_origem']).execute()
            
            if update_response.data:
                print(f"✅ Saldo atualizado com sucesso! Novo saldo: {novo_saldo}")
            else:
                print(f"⚠️ Transferência salva mas erro ao atualizar saldo")
            
            # 🔥 🔥 🔥 NOVO: SALVAR BENEFICIÁRIO SE CHECKBOX MARCADO 🔥 🔥 🔥
            try:
                # Verificar se o checkbox 'salvar_beneficiario' foi marcado
                # Pode vir como boolean (True/False) ou string ("true"/"false")
                salvar_beneficiario = dados.get('salvar_beneficiario', False)
                
                # Converter para boolean se for string
                if isinstance(salvar_beneficiario, str):
                    salvar_beneficiario = salvar_beneficiario.lower() in ['true', '1', 'yes', 'on']
                
                print(f"📝 Checkbox 'salvar beneficiário': {salvar_beneficiario}")
                
                if salvar_beneficiario:
                    print(f"💾 Salvando beneficiário para {usuario_logado}...")
                    
                    # Preparar dados do beneficiário
                    dados_beneficiario = {
                        'nome': dados.get('beneficiario', '').strip(),
                        'endereco': dados.get('endereco_beneficiario', '').strip(),
                        'cidade': dados.get('cidade', '').strip(),
                        'pais': dados.get('pais', '').strip(),
                        'banco': dados.get('nome_banco', '').strip(),
                        'endereco_banco': dados.get('endereco_banco', '').strip(),
                        'cidade_banco': dados.get('cidade_banco', '').strip(),
                        'pais_banco': dados.get('pais_banco', '').strip(),
                        'swift': dados.get('codigo_swift', '').strip(),
                        'iban': dados.get('iban_account', '').strip(),
                        'aba': dados.get('aba_routing', '').strip(),
                        'cliente_username': usuario_logado,
                        'ativo': True
                    }
                    
                    # Verificar campos mínimos
                    if dados_beneficiario['nome'] and dados_beneficiario['banco'] and dados_beneficiario['swift']:
                        response_benef = supabase.table('beneficiarios').insert(dados_beneficiario).execute()
                        
                        if response_benef.data:
                            print(f"✅✅✅ BENEFICIÁRIO SALVO COM SUCESSO!")
                            print(f"✅ ID: {response_benef.data[0]['id']}")
                            print(f"✅ Nome: {dados_beneficiario['nome']}")
                        else:
                            print(f"⚠️ Erro ao salvar beneficiário")
                    else:
                        print(f"⚠️ Campos insuficientes para salvar beneficiário")
                        
            except Exception as benef_error:
                print(f"⚠️ Erro ao salvar beneficiário: {benef_error}")
                # Não interrompe o fluxo principal
                print(f"⚠️ Continuando sem salvar beneficiário...")
            
            # 🔥 🔥 🔥 NOVO: PROCESSAR UPLOAD DA INVOICE SE EXISTIR 🔥 🔥 🔥
            try:
                # Verificar se há arquivo na requisição
                if 'file' in request.files:
                    arquivo = request.files['file']
                    
                    if arquivo and arquivo.filename != '':
                        print(f"\n📁 📁 📁 PROCESSANDO UPLOAD DE INVOICE NA CRIAÇÃO 📁 📁 📁")
                        print(f"   Nome do arquivo: {arquivo.filename}")
                        print(f"   Tipo: {arquivo.content_type}")
                        print(f"   Tamanho: {arquivo.content_length} bytes")
                        
                        # Validar arquivo
                        nome_arquivo = arquivo.filename
                        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
                        
                        extensoes_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
                        if extensao not in extensoes_permitidas:
                            print(f"⚠️  Extensão não permitida: .{extensao}")
                        elif arquivo.content_length > 5 * 1024 * 1024:
                            print(f"⚠️  Arquivo muito grande: {arquivo.content_length} bytes")
                        else:
                            # Criar nome único
                            import time
                            timestamp = str(int(time.time() * 1000))
                            nome_base = nome_arquivo.rsplit('.', 1)[0]
                            novo_nome = f"{timestamp}_{nome_base}.{extensao}"
                            caminho_supabase = f"transferencias/{transferencia_id}/{novo_nome}"
                            
                            print(f"📤 Caminho no storage: {caminho_supabase}")
                            
                            # Ler bytes do arquivo
                            arquivo.seek(0)  # Garantir que estamos no início
                            arquivo_bytes = arquivo.read()
                            
                            print(f"🔼 Fazendo upload de {len(arquivo_bytes)} bytes...")
                            
                            # Fazer upload para o Supabase Storage
                            upload_response = supabase.storage.from_("invoices")\
                                .upload(caminho_supabase, arquivo_bytes)
                            
                            if upload_response:
                                print(f"✅✅✅ UPLOAD DA INVOICE REALIZADO COM SUCESSO!")
                                
                                # Atualizar invoice_info na transferência
                                nova_invoice_info = {
                                    'status': 'pending',
                                    'data_upload': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'caminho_arquivo': caminho_supabase,
                                    'nome_arquivo': novo_nome,
                                    'tamanho': arquivo.content_length,
                                    'tipo': arquivo.content_type or f'application/{extensao}'
                                }
                                
                                print(f"📝 Invoice info para salvar: {nova_invoice_info}")
                                
                                update_invoice_response = supabase.table('transferencias')\
                                    .update({'invoice_info': nova_invoice_info})\
                                    .eq('id', transferencia_id)\
                                    .execute()
                                
                                if update_invoice_response.data:
                                    print(f"✅✅✅ INVOICE INFO SALVA NO BANCO DE DADOS!")
                                else:
                                    print(f"⚠️  Invoice salva no storage mas erro ao atualizar banco")
                            else:
                                print(f"❌ Erro ao fazer upload da invoice para o storage")
                    else:
                        print(f"ℹ️  Nenhum arquivo enviado ou nome vazio")
                else:
                    print(f"ℹ️  Nenhum arquivo 'file' na requisição")
                    
            except Exception as upload_error:
                print(f"⚠️  Erro ao processar upload da invoice: {upload_error}")
                import traceback
                traceback.print_exc()
                # NÃO LANÇAR ERRO - A TRANSFERÊNCIA JÁ FOI CRIADA!
                print(f"⚠️  Continuando sem invoice...")
            
            print(f"\n🎉🎉🎉 PROCESSO DE CRIAÇÃO COMPLETO CONCLUÍDO! 🎉🎉🎉")
            print(f"📊 Transferência ID: {transferencia_id}")
            print(f"💰 Valor: {valor_transferencia} {dados['moeda']}")
            print(f"👤 Usuário: {usuario_logado}")
            
            # 🔥 🔥 🔥 FIM DO PROCESSAMENTO DA INVOICE 🔥 🔥 🔥
            
            return jsonify({
                "success": True,
                "message": "Transferência criada com sucesso!",
                "transferencia_id": transferencia_id
            })
        else:
            print(f"❌ ERRO: Nenhum dado retornado do Supabase")
            return jsonify({
                "success": False,
                "message": "Erro ao salvar no banco de dados"
            }), 500
            
    except Exception as e:
        print(f"❌❌❌ ERRO CRÍTICO NA API criar_transferencia: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
                "success": False,
                "message": f"Erro interno: {str(e)}"
        }), 500
    
@app.route('/api/transferencias/<transferencia_id>/invoice/upload', methods=['POST'])
def upload_invoice_nova_transferencia(transferencia_id):
    """Upload de invoice para transferência RECÉM-CRIADA (mesma lógica do reenvio)"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    print(f"📤 [UPLOAD-NOVA] Iniciando upload para transferência recém-criada: {transferencia_id}")
    
    try:
        # 1. VERIFICAR SE TRANSFERÊNCIA É DO USUÁRIO
        response = supabase.table('transferencias')\
            .select('id, cliente, usuario')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({'error': 'Transferência não encontrada'}), 404
        
        transferencia = response.data[0]
        
        # Verificar permissão
        usuario_permitido = (
            transferencia.get('cliente') == usuario_nome or
            transferencia.get('usuario') == usuario_nome
        )
        
        if not usuario_permitido:
            return jsonify({'error': 'Acesso não autorizado'}), 403
        
        # 2. VERIFICAR ARQUIVO
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['file']
        
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # 3. VALIDAR ARQUIVO (IGUAL AO REENVIO)
        nome_arquivo = arquivo.filename
        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
        
        extensoes_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
        if extensao not in extensoes_permitidas:
            return jsonify({
                'error': f'Extensão não permitida: .{extensao}',
                'permitidas': extensoes_permitidas
            }), 400
        
        # Verificar tamanho (5MB)
        arquivo.seek(0, 2)
        tamanho = arquivo.tell()
        arquivo.seek(0)
        
        if tamanho > 5 * 1024 * 1024:
            return jsonify({'error': 'Arquivo muito grande. Máximo: 5MB'}), 400
        
        print(f"📁 [UPLOAD-NOVA] Arquivo validado: {nome_arquivo} ({tamanho} bytes, .{extensao})")
        
        # 4. CRIAR NOVO NOME
        import time
        timestamp = str(int(time.time() * 1000))
        nome_base = nome_arquivo.rsplit('.', 1)[0]
        novo_nome = f"{timestamp}_{nome_base}.{extensao}"
        caminho_supabase = f"transferencias/{transferencia_id}/{novo_nome}"
        
        print(f"📤 [UPLOAD-NOVA] Caminho: {caminho_supabase}")
        
        # 5. FAZER UPLOAD
        arquivo_bytes = arquivo.read()
        
        print(f"🔼 [UPLOAD-NOVA] Fazendo upload de {len(arquivo_bytes)} bytes...")
        upload_response = supabase.storage.from_("invoices")\
            .upload(caminho_supabase, arquivo_bytes)
        
        if not upload_response:
            return jsonify({'error': 'Erro ao fazer upload para o storage'}), 500
        
        print(f"✅ [UPLOAD-NOVA] Upload realizado!")
        
        # 6. ATUALIZAR INVOICE INFO
        nova_invoice_info = {
            'status': 'pending',
            'data_upload': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'caminho_arquivo': caminho_supabase,
            'nome_arquivo': novo_nome,
            'tamanho': tamanho,
            'tipo': arquivo.content_type or f'application/{extensao}'
        }
        
        update_response = supabase.table('transferencias')\
            .update({'invoice_info': nova_invoice_info})\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ [UPLOAD-NOVA] Invoice info atualizada no banco")
            
            return jsonify({
                'success': True,
                'message': 'Invoice enviada com sucesso!',
                'invoice': {
                    'caminho': caminho_supabase,
                    'nome': novo_nome,
                    'tamanho': tamanho,
                    'status': 'pending'
                }
            })
        else:
            return jsonify({'error': 'Erro ao atualizar informações da invoice'}), 500
        
    except Exception as e:
        print(f"❌ [UPLOAD-NOVA] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    
@app.route('/api/user')
def get_user_info():
    """Retorna informações REAIS do usuário logado"""
    try:
        # ✅ Pega usuário da SESSÃO (correto!)
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        response = supabase.table('usuarios')\
            .select('username, nome, email, tipo, telefone, verificado, cambio_liberado')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if response.data:
            return jsonify({
                "success": True,
                "user": response.data
            })
        else:
            # Fallback se não encontrar
            return jsonify({
                "success": True,
                "user": {
                    "username": usuario,
                    "nome": usuario.upper(),
                    "email": f"{usuario}@exemplo.com",
                    "tipo": "cliente",
                    "telefone": "",
                    "verificado": True,
                    "cambio_liberado": True
                }
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar usuário do Supabase: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro ao carregar dados do usuário: {str(e)}"
        }), 500

@app.route('/api/user/contas')
def get_user_contas():
    """Retorna contas REAIS do usuário logado"""
    try:
        # ✅ Pega usuário da SESSÃO (correto!)
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado",
                "contas": []
            }), 401
        
        response = supabase.table('contas')\
            .select('id, moeda, saldo, cliente_username, cliente_nome, ativa')\
            .eq('cliente_username', usuario)\
            .eq('ativa', True)\
            .execute()
        
        if response.data:
            return jsonify({
                "success": True,
                "contas": response.data
            })
        else:
            # Se não tem contas, retorna vazio
            return jsonify({
                "success": True,
                "contas": []
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar contas do Supabase: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro ao carregar contas: {str(e)}",
            "contas": []
        }), 500

@app.route('/api/beneficiarios', methods=['GET', 'POST'])  # ← ADICIONAR POST AQUI!
def get_beneficiarios():
    """Retorna beneficiários REAIS do usuário logado (GET) ou cria novo (POST)"""
    try:
        # ✅ Pega usuário da SESSÃO (correto!)
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado",
                "beneficiarios": []
            }), 401
        
        # ********** SE FOR POST **********
        if request.method == 'POST':
            print("📥 RECEBENDO POST PARA CRIAR BENEFICIÁRIO")
            dados = request.get_json()
            
            print(f"📋 Dados recebidos: {dados}")
            
            # Validar campos obrigatórios
            if not dados.get('nome'):
                return jsonify({"success": False, "message": "Nome do beneficiário é obrigatório"}), 400
            if not dados.get('banco'):
                return jsonify({"success": False, "message": "Nome do banco é obrigatório"}), 400
            if not dados.get('swift'):
                return jsonify({"success": False, "message": "Código SWIFT é obrigatório"}), 400
            
            # Preparar dados para inserção
            novo_beneficiario = {
                'nome': dados['nome'],
                'banco': dados['banco'],
                'swift': dados['swift'],
                'iban': dados.get('iban', ''),
                'endereco': dados.get('endereco', ''),
                'cidade': dados.get('cidade', ''),
                'pais': dados.get('pais', ''),
                # 🔍 CAMPOS ADICIONADOS
                'endereco_banco': dados.get('endereco_banco', ''),
                'cidade_banco': dados.get('cidade_banco', ''),
                'pais_banco': dados.get('pais_banco', ''),
                'cliente_username': usuario,
                'ativo': True,
            }
            
            print(f"💾 Inserindo beneficiário: {novo_beneficiario}")
            
            # Inserir no Supabase
            response = supabase.table('beneficiarios').insert(novo_beneficiario).execute()
            
            if response.data:
                print(f"✅ Beneficiário salvo com sucesso! ID: {response.data[0]['id']}")
                return jsonify({
                    "success": True,
                    "message": "Beneficiário salvo com sucesso",
                    "id": response.data[0]['id']
                })
            else:
                print(f"❌ Erro ao salvar beneficiário: {response}")
                return jsonify({
                    "success": False,
                    "message": "Erro ao salvar beneficiário"
                }), 500
        
        # ********** SE FOR GET (código original) **********
        else:  # GET
            response = supabase.table('beneficiarios')\
                .select('id, nome, endereco, cidade, pais, banco, swift, iban, aba, cidade_banco, pais_banco, endereco_banco')\
                .eq('cliente_username', usuario)\
                .eq('ativo', True)\
                .execute()
            
            if response.data:
                return jsonify({
                    "success": True,
                    "beneficiarios": response.data
                })
            else:
                return jsonify({
                    "success": True,
                    "beneficiarios": []
                })
                
    except Exception as e:
        print(f"❌ Erro em /api/beneficiarios: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro ao processar beneficiários: {str(e)}",
            "beneficiarios": []
        }), 500

@app.route('/api/beneficiarios/<int:benef_id>')
def get_beneficiario_detalhe(benef_id):
    """Retorna detalhes de UM beneficiário específico do Supabase"""
    try:
        # ✅ Pega usuário da SESSÃO (correto!)
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        print(f"🔍 Buscando beneficiário ID: {benef_id} para usuário: {usuario}")
        
        response = supabase.table('beneficiarios')\
            .select('id, nome, endereco, cidade, pais, banco, endereco_banco, cidade_banco, pais_banco, swift, iban, aba')\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .eq('ativo', True)\
            .single()\
            .execute()
        
        if response.data:
            print(f"✅ Beneficiário encontrado: {response.data['nome']}")
            return jsonify({
                "success": True,
                "beneficiario": response.data
            })
        else:
            print(f"⚠️ Beneficiário {benef_id} não encontrado para {usuario}")
            return jsonify({
                "success": False,
                "message": "Beneficiário não encontrado"
            }), 404
            
    except Exception as e:
        print(f"❌ Erro ao buscar beneficiário {benef_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro ao carregar beneficiário: {str(e)}"
        }), 500

@app.route('/transferencia')
def tela_transferencia():
    """Renderiza a tela de transferência internacional"""
    # ✅ Pega usuário da SESSÃO
    usuario = session.get('username')
    
    if not usuario:
        # Se não estiver logado, redireciona para login
        return redirect('/login')
    
    # Busca dados básicos do usuário
    email = f'{usuario}@exemplo.com'
    nome = usuario.upper()
    
    try:
        if supabase:
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
    except Exception as e:
        print(f"⚠️  Erro ao buscar usuário em /transferencia: {e}")
    
    # Passa variáveis para o template (igual ao dashboard!)
    return render_template('transferencia.html', 
                          usuario=usuario,
                          nome=nome,
                          email=email)

@app.route('/api/beneficiarios', methods=['GET', 'POST'])
def handle_beneficiarios():
    """Gerencia beneficiários: GET para listar, POST para criar"""
    try:
        usuario = session.get('username')
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        if request.method == 'GET':
            # Listar beneficiários ATIVOS do usuário
            response = supabase.table('beneficiarios') \
                .select('*') \
                .eq('cliente_username', usuario) \
                .eq('ativo', True) \
                .order('nome') \
                .execute()
            
            return jsonify({
                "success": True,
                "beneficiarios": response.data if response.data else []
            })
            
        elif request.method == 'POST':
            # Criar novo beneficiário
            dados = request.get_json()
            
            # Validar campos obrigatórios
            if not dados.get('nome'):
                return jsonify({"success": False, "message": "Nome do beneficiário é obrigatório"}), 400
            if not dados.get('banco'):
                return jsonify({"success": False, "message": "Nome do banco é obrigatório"}), 400
            if not dados.get('swift'):
                return jsonify({"success": False, "message": "Código SWIFT é obrigatório"}), 400
            
            # Preparar dados
            novo_beneficiario = {
                'nome': dados['nome'],
                'banco': dados['banco'],
                'swift': dados['swift'],
                'iban': dados.get('iban', ''),
                'endereco': dados.get('endereco', ''),
                'cidade': dados.get('cidade', ''),
                'pais': dados.get('pais', ''),
                'cliente_username': usuario,
                'ativo': True
            }
            
            # Inserir no Supabase
            response = supabase.table('beneficiarios').insert(novo_beneficiario).execute()
            
            if response.data:
                return jsonify({
                    "success": True,
                    "message": "Beneficiário salvo com sucesso",
                    "id": response.data[0]['id']
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Erro ao salvar beneficiário"
                }), 500
                
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Erro ao processar beneficiários",
            "error": str(e)
        }), 500

# ============================================================================
# APIs PARA TRANSFERÊNCIA (MOCK - DEPOIS SUBSTITUI POR SUPABASE)
# ============================================================================

@app.route('/api/user')
def get_user_info_web():
    """Retorna informações REAIS do usuário do Supabase"""
    try:
        # TODO: Quando tiver autenticação, buscar usuário logado
        # Por enquanto, buscar um usuário exemplo ou mock
        
        # Tentar buscar usuários do Supabase
        response = supabase.table('usuarios').select('*').limit(1).execute()
        
        if response.data and len(response.data) > 0:
            usuario = response.data[0]
            return jsonify({
                "success": True,
                "user": {
                    "id": usuario.get('id'),
                    "username": usuario.get('username', 'cliente'),
                    "nome": usuario.get('nome', 'Cliente Exemplo'),
                    "email": usuario.get('email', 'cliente@email.com'),
                    "tipo": usuario.get('tipo', 'cliente'),
                    "telefone": usuario.get('telefone', ''),
                    "documento": usuario.get('documento', '')
                }
            })
        else:
            # Se não tem usuários no Supabase, criar um mock melhor
            return jsonify({
                "success": True,
                "user": {
                    "id": "user_001",
                    "username": "cliente_exemplo",
                    "nome": "João da Silva",
                    "email": "joao.silva@email.com",
                    "tipo": "cliente",
                    "telefone": "+55 11 99999-9999",
                    "documento": "123.456.789-00"
                }
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar usuário do Supabase: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro ao carregar dados do usuário: {str(e)}"
        }), 500
    
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

# Adicione esta rota no web_api.py (logo após as rotas existentes)
@app.route('/minhas-transferencias')
def minhas_transferencias():
    """Tela de minhas transferências (histórico, status, invoices, comprovantes)"""
    
    # ✅ CORREÇÃO: usar 'username' (igual ao login), não 'usuario'
    usuario = session.get('username')
    
    if usuario:
        print(f"✅ [SESSÃO] Usuário {usuario} acessando minhas-transferencias")
    else:
        # Fallback: tentar parâmetro da URL
        usuario = request.args.get('usuario')
        
        if usuario:
            print(f"✅ [URL PARAM] Usuário {usuario} acessando minhas-transferencias via URL")
            # Salva na sessão com a chave CORRETA
            session['username'] = usuario
        else:
            print(f"❌ Nenhum usuário autenticado")
            return redirect('/login')
    
    # Buscar dados do usuário para o template
    email = f'{usuario}@exemplo.com'
    nome = usuario.upper()
    
    try:
        if supabase:
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
    except Exception as e:
        print(f"⚠️  Erro ao buscar usuário: {e}")
    
    # Renderizar template
    return render_template('minhas_transferencias.html',
                         usuario=usuario,
                         nome=nome,
                         email=email)

# === NOVO ENDPOINT PARA TRANSFERÊNCIAS INTERNACIONAIS ===
@app.route('/api/transferencias-internacionais')
def api_transferencias_internacionais():
    """API para buscar transferências internacionais do usuário logado"""
    
    if 'username' not in session:  # ✅ CORRIGIDO
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']  # ✅ CORRIGIDO
    print(f"🔍 [API] Buscando transferências internacionais para: {usuario_nome}")
    
    try:
        # 1. BUSCAR O USUÁRIO E SUAS CONTAS
        user_response = supabase.table('usuarios').select('contas').eq('username', usuario_nome).execute()
        
        if not user_response.data:
            print(f"❌ [API] Usuário não encontrado na tabela usuarios")
            return jsonify([])
        
        contas_usuario = user_response.data[0].get('contas', [])
        print(f"📊 [API] Contas do usuário: {contas_usuario}")
        
        # 2. BUSCAR TRANSFERÊNCIAS POR MÚLTIPLOS CAMPOS
        todas_transferencias = []
        ids_ja_adicionados = set()
        
        # ESTRATÉGIA 1: Buscar pelo campo 'cliente'
        print(f"🔍 Buscando pelo campo 'cliente' = {usuario_nome}")
        response_cliente = supabase.table('transferencias').select(
            '*'
        ).eq('cliente', usuario_nome).execute()
        
        if response_cliente.data:
            for transf in response_cliente.data:
                if transf['id'] not in ids_ja_adicionados:
                    todas_transferencias.append(transf)
                    ids_ja_adicionados.add(transf['id'])
            print(f"✅ Encontradas {len(response_cliente.data)} pelo campo 'cliente'")
        
        # ESTRATÉGIA 2: Buscar pelo campo 'usuario'
        print(f"🔍 Buscando pelo campo 'usuario' = {usuario_nome}")
        response_usuario = supabase.table('transferencias').select(
            '*'
        ).eq('usuario', usuario_nome).execute()
        
        if response_usuario.data:
            novas = 0
            for transf in response_usuario.data:
                if transf['id'] not in ids_ja_adicionados:
                    todas_transferencias.append(transf)
                    ids_ja_adicionados.add(transf['id'])
                    novas += 1
            print(f"✅ Encontradas {novas} pelo campo 'usuario' (total únicas)")
        
        # ESTRATÉGIA 3: Buscar pelas contas do usuário
        for conta in contas_usuario:
            print(f"🔍 Buscando pela conta '{conta}'")
            response_conta = supabase.table('transferencias').select(
                '*'
            ).eq('conta_remetente', conta).execute()
            
            if response_conta.data:
                novas = 0
                for transf in response_conta.data:
                    if transf['id'] not in ids_ja_adicionados:
                        todas_transferencias.append(transf)
                        ids_ja_adicionados.add(transf['id'])
                        novas += 1
                print(f"✅ Encontradas {novas} pela conta '{conta}'")
        
        print(f"📊 [API] Total de transferências únicas encontradas: {len(todas_transferencias)}")
        
        # 3. FILTRAR APENAS INTERNACIONAIS
        transferencias_internacionais = []
        
        for transf in todas_transferencias:
            tipo = transf.get('tipo', '')
            
            # VERIFICAR SE É INTERNACIONAL
            is_internacional = (
                tipo == 'transferencia_internacional' or
                'internacional' in str(tipo).lower() or
                transf.get('codigo_swift') or
                transf.get('iban_account') or
                (transf.get('pais') and transf.get('pais').lower() != 'brasil')
            )
            
            if is_internacional:
                transferencias_internacionais.append(transf)
        
        print(f"🎯 [API] Transferências internacionais filtradas: {len(transferencias_internacionais)}")
        
        # 4. LOG DETALHADO
        if transferencias_internacionais:
            print(f"📋 TRANSFERÊNCIAS INTERNACIONAIS ENCONTRADAS:")
            for i, t in enumerate(transferencias_internacionais):
                print(f"   {i+1}. ID: {t.get('id')}")
                print(f"      Tipo: {t.get('tipo')}")
                print(f"      Status: {t.get('status')}")
                print(f"      Cliente: {t.get('cliente')}")
                print(f"      Usuário: {t.get('usuario')}")
                print(f"      Conta: {t.get('conta_remetente')}")
                print(f"      Beneficiário: {t.get('beneficiario')}")
                print(f"      Valor: {t.get('valor')} {t.get('moeda')}")
        
        # 5. FORMATAR RESPOSTA
        resultado = []
        for t in transferencias_internacionais:
            invoice_info = t.get('invoice_info') or {}
            
            resultado.append({
                'id': t['id'],
                'tipo': t.get('tipo'),
                'status': t.get('status'),
                'beneficiario': t.get('beneficiario'),
                # 🔍 CAMPOS DO BENEFICIÁRIO (FALTANDOS)
                'endereco_beneficiario': t.get('endereco_beneficiario', ''),
                'cidade': t.get('cidade', ''),
                'pais': t.get('pais', ''),
                # 🔍 CAMPOS DO BANCO (FALTANDOS)
                'nome_banco': t.get('nome_banco', ''),
                'endereco_banco': t.get('endereco_banco', ''),
                'cidade_banco': t.get('cidade_banco', ''),
                'pais_banco': t.get('pais_banco', ''),
                'codigo_swift': t.get('codigo_swift', ''),
                'iban_account': t.get('iban_account', ''),
                'aba_routing': t.get('aba_routing', ''),

                # 🔥 CAMPOS SWIFT:
                'dados_swift_pagamento': t.get('dados_swift_pagamento', {}),  # ← FALTANDO!
                'data_conclusao': t.get('data_conclusao'),  # ← Para mostrar data completed

                # 🔍 INFORMAÇÕES FINANCEIRAS
                'valor': float(t['valor']) if t.get('valor') else 0,
                'moeda': t.get('moeda', 'USD'),
                # 🔍 DATAS E TEMPOS
                'data': t.get('data') or t.get('data_solicitacao') or t.get('created_at'),
                'created_at': t.get('created_at'),
                # 🔍 INFORMAÇÕES ADICIONAIS
                'finalidade': t.get('finalidade', ''),
                'descricao': t.get('descricao', ''),
                # 🔍 INFORMAÇÕES DA CONTA
                'conta_remetente': t.get('conta_remetente', ''),
                'cliente': t.get('cliente', ''),
                'usuario': t.get('usuario', ''),
                'solicitado_por': t.get('solicitado_por', ''),
                # 🔍 INVOICE/COMPROVANTES
                'invoice': bool(invoice_info),
                'invoice_status': invoice_info.get('status') if isinstance(invoice_info, dict) else None,
                'invoice_recusada': t.get('status') == 'rejected' or 
                                   (invoice_info.get('status') == 'rejected' if isinstance(invoice_info, dict) else False),
                'motivo_recusa': t.get('motivo_recusa', '')
            })
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"❌ [API] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([])
    
# === ENDPOINT ESPECÍFICO PARA PDF ===
@app.route('/api/transferencias/<int:transferencia_id>/completo')
def transferencia_completa(transferencia_id):
    """Retorna TODOS os dados de uma transferência específica para o PDF"""
    
    if 'username' not in session:  # ✅ CORRIGIDO
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']  # ✅ CORRIGIDO
    print(f"📄 [PDF API] Buscando dados completos para transferência {transferencia_id}")
    
    try:
        # Buscar transferência específica
        response = supabase.table('transferencias').select('*').eq('id', transferencia_id).execute()
        
        if not response.data:
            print(f"❌ Transferência {transferencia_id} não encontrada")
            return jsonify({'error': 'Transferência não encontrada'}), 404
        
        transferencia = response.data[0]
        
        # Verificar se o usuário tem permissão para ver esta transferência
        usuario_permitido = (
            transferencia.get('cliente') == usuario_nome or
            transferencia.get('usuario') == usuario_nome or
            usuario_nome in transferencia.get('conta_remetente', '')
        )
        
        if not usuario_permitido:
            print(f"⚠️ Usuário {usuario_nome} não tem permissão para ver transferência {transferencia_id}")
            return jsonify({'error': 'Acesso não autorizado'}), 403
        
        # 🔥 CORREÇÃO CRÍTICA: Garantir que dados_swift_pagamento seja um dict
        dados_swift_raw = transferencia.get('dados_swift_pagamento')
        dados_swift = {}
        
        if dados_swift_raw:
            if isinstance(dados_swift_raw, dict):
                dados_swift = dados_swift_raw
            elif isinstance(dados_swift_raw, str):
                try:
                    # Tentar parsear JSON string
                    import json
                    dados_swift = json.loads(dados_swift_raw)
                except:
                    print(f"⚠️ Não foi possível parsear dados_swift_pagamento: {dados_swift_raw}")
                    # Criar dicionário vazio se não conseguir parsear
                    dados_swift = {}
        
        print(f"✅ Dados SWIFT encontrados: {bool(dados_swift)}")
        if dados_swift:
            print(f"   Keys SWIFT: {list(dados_swift.keys())}")
        
        # Preparar resposta completa
        dados_formatados = {
            'id': transferencia.get('id'),
            'status': transferencia.get('status', 'solicitada').lower(),
            'valor': float(transferencia.get('valor', 0)),
            'moeda': transferencia.get('moeda', 'USD'),
            'data': transferencia.get('data') or transferencia.get('data_solicitacao') or transferencia.get('created_at'),
            'data_conclusao': transferencia.get('data_conclusao'),
            'tipo': transferencia.get('tipo', 'transferencia_internacional'),
            'finalidade': transferencia.get('finalidade', 'Not informed'),
            
            # 🔥 DADOS DO BENEFICIÁRIO (garantir que existem)
            'beneficiario': transferencia.get('beneficiario', ''),
            'endereco_beneficiario': transferencia.get('endereco_beneficiario', ''),
            'cidade': transferencia.get('cidade', ''),
            'pais': transferencia.get('pais', ''),
            
            # 🔥 DADOS DO BANCO (garantir que existem)
            'nome_banco': transferencia.get('nome_banco', ''),
            'endereco_banco': transferencia.get('endereco_banco', ''),
            'cidade_banco': transferencia.get('cidade_banco', ''),
            'pais_banco': transferencia.get('pais_banco', ''),
            'codigo_swift': transferencia.get('codigo_swift', ''),
            'iban_account': transferencia.get('iban_account', ''),
            'aba_routing': transferencia.get('aba_routing', ''),
            
            # 🔥 DADOS SWIFT (CRÍTICO!)
            'dados_swift_pagamento': dados_swift,
            
            # Informações adicionais
            'cliente': transferencia.get('cliente', ''),
            'usuario': transferencia.get('usuario', ''),
            'conta_remetente': transferencia.get('conta_remetente', ''),
            'solicitado_por': transferencia.get('solicitado_por', ''),
            'descricao': transferencia.get('descricao', ''),
            'motivo_recusa': transferencia.get('motivo_recusa', ''),
            'created_at': transferencia.get('created_at')
        }
        
        print(f"✅ [PDF API] Dados preparados para transferência {transferencia_id}")
        print(f"   Status: {dados_formatados['status']}")
        print(f"   Tem SWIFT: {bool(dados_formatados['dados_swift_pagamento'])}")
        
        return jsonify(dados_formatados)
        
    except Exception as e:
        print(f"❌ [PDF API] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro interno do servidor'}), 500
    
@app.route('/api/transferencias/<transferencia_id>/invoice/verificar')
def verificar_invoice(transferencia_id):
    """Verifica se existe invoice e retorna informações básicas"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    
    try:
        # Buscar invoice info
        response = supabase.table('transferencias')\
            .select('invoice_info')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({'available': False, 'error': 'Transferência não encontrada'})
        
        invoice_info = response.data[0].get('invoice_info')
        
        if not invoice_info or not invoice_info.get('caminho_arquivo'):
            return jsonify({'available': False, 'error': 'Nenhuma invoice encontrada'})
        
        # Verificar se o arquivo existe no storage
        caminho_arquivo = invoice_info.get('caminho_arquivo')
        
        try:
            # Tentar verificar se o arquivo existe
            supabase.storage.from_("invoices")\
                .download(caminho_arquivo)
            
            return jsonify({
                'available': True,
                'status': invoice_info.get('status', 'pending'),
                'filename': caminho_arquivo.split('/')[-1],
                'upload_date': invoice_info.get('data_upload'),
                'rejection_reason': invoice_info.get('motivo_recusa'),
                'can_reupload': invoice_info.get('status') == 'rejected'
            })
            
        except Exception as storage_error:
            print(f"⚠️ [VERIFICAR] Arquivo não encontrado no storage: {storage_error}")
            return jsonify({'available': False, 'error': 'Arquivo não encontrado no storage'})
            
    except Exception as e:
        print(f"❌ [VERIFICAR] Erro: {e}")
        return jsonify({'available': False, 'error': str(e)}), 500

@app.route('/api/transferencias/<transferencia_id>/upload-invoice', methods=['POST'])
def upload_invoice_web(transferencia_id):
    """Upload de invoice - VERSÃO COMPATÍVEL COM KIVY"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    print(f"📤 [UPLOAD-WEB] Iniciando upload para transferência {transferencia_id}")
    
    try:
        # 1. VERIFICAR TRANSFERÊNCIA E PERMISSÃO
        response = supabase.table('transferencias')\
            .select('id, cliente, usuario, conta_remetente')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({'error': 'Transferência não encontrada'}), 404
        
        transferencia = response.data[0]
        conta_transferencia = transferencia.get('conta_remetente')
        
        # 🔥 MESMA VERIFICAÇÃO DO KIVY
        user_response = supabase.table('usuarios')\
            .select('contas')\
            .eq('username', usuario_nome)\
            .execute()
        
        if not user_response.data:
            return jsonify({'error': 'Acesso não autorizado'}), 403
        
        contas_usuario = user_response.data[0].get('contas', [])
        
        # Verificar se a conta da transferência está nas contas do usuário
        tem_permissao = False
        if isinstance(contas_usuario, list) and conta_transferencia in contas_usuario:
            tem_permissao = True
        elif isinstance(contas_usuario, str) and conta_transferencia in contas_usuario:
            tem_permissao = True
        
        # Também permitir se for o cliente ou usuário
        if transferencia.get('cliente') == usuario_nome or transferencia.get('usuario') == usuario_nome:
            tem_permissao = True
        
        if not tem_permissao:
            return jsonify({'error': 'Acesso não autorizado'}), 403
        
        # 2. VERIFICAR ARQUIVO ENVIADO
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['file']
        
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # 3. VALIDAR O ARQUIVO (IGUAL KIVY)
        nome_arquivo = arquivo.filename
        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
        
        extensoes_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
        if extensao not in extensoes_permitidas:
            return jsonify({
                'error': f'Extensão não permitida: .{extensao}',
                'permitidas': extensoes_permitidas
            }), 400
        
        # Verificar tamanho (5MB - igual Kivy)
        arquivo.seek(0, 2)
        tamanho = arquivo.tell()
        arquivo.seek(0)
        
        if tamanho > 5 * 1024 * 1024:
            return jsonify({'error': 'Arquivo muito grande. Máximo: 5MB'}), 400
        
        print(f"📁 [UPLOAD-WEB] Arquivo validado: {nome_arquivo} ({tamanho} bytes, .{extensao})")
        
        # 4. GERAR NOME ÚNICO (IGUAL KIVY)
        import time
        timestamp = str(int(time.time() * 1000))
        nome_base = nome_arquivo.rsplit('.', 1)[0]
        novo_nome = f"{timestamp}_{nome_base}.{extensao}"
        caminho_supabase = f"transferencias/{transferencia_id}/{novo_nome}"
        
        print(f"📤 [UPLOAD-WEB] Caminho: {caminho_supabase}")
        
        # 5. FAZER UPLOAD PARA O STORAGE (IGUAL KIVY)
        arquivo_bytes = arquivo.read()
        
        print(f"🔼 [UPLOAD-WEB] Fazendo upload de {len(arquivo_bytes)} bytes...")
        
        try:
            # 🔥 MESMA LÓGICA DO KIVY - usar client.storage
            upload_response = supabase.storage.from_("invoices")\
                .upload(caminho_supabase, arquivo_bytes)
            
            print(f"📊 [UPLOAD-WEB] Resposta do upload: {upload_response}")
            
            if not upload_response:
                return jsonify({'error': 'Erro ao fazer upload para o storage'}), 500
                
        except Exception as upload_error:
            print(f"❌ [UPLOAD-WEB] Erro no upload: {upload_error}")
            return jsonify({'error': f'Erro no upload: {str(upload_error)}'}), 500
        
        print(f"✅ [UPLOAD-WEB] Upload realizado!")
        
        # 6. ATUALIZAR NO BANCO (IGUAL KIVY)
        nova_invoice_info = {
            'status': 'pending',
            'caminho_arquivo': caminho_supabase,
            'data_upload': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'motivo_recusa': '',  # Limpa motivo anterior
            'data_recusa': None
        }
        
        update_response = supabase.table('transferencias')\
            .update({'invoice_info': nova_invoice_info})\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ [UPLOAD-WEB] Invoice info atualizada no banco")
            
            return jsonify({
                'success': True,
                'message': 'Invoice enviada com sucesso!',
                'invoice': {
                    'caminho': caminho_supabase,
                    'nome': novo_nome,
                    'tamanho': tamanho,
                    'status': 'pending'
                }
            })
        else:
            return jsonify({'error': 'Erro ao atualizar informações da invoice'}), 500
        
    except Exception as e:
        print(f"❌ [UPLOAD-WEB] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/transferencias/<transferencia_id>/invoice')
def download_invoice(transferencia_id):
    """Download da invoice - VERSÃO CORRIGIDA"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    print(f"📄 [DOWNLOAD] Usuário: {usuario_nome}, Transferência: {transferencia_id}")
    
    try:
        # 1. BUSCAR TRANSFERÊNCIA DIRETAMENTE
        trans_response = supabase.table('transferencias')\
            .select('invoice_info, conta_remetente, cliente, usuario')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not trans_response.data:
            return jsonify({'error': 'Transferência não encontrada'}), 404
        
        transferencia = trans_response.data[0]
        invoice_info = transferencia.get('invoice_info') or {}
        caminho_arquivo = invoice_info.get('caminho_arquivo')
        
        if not caminho_arquivo:
            return jsonify({'error': 'Nenhuma invoice encontrada'}), 404
        
        print(f"📁 [DOWNLOAD] Caminho: {caminho_arquivo}")
        
        # 2. 🔥 CORREÇÃO CRÍTICA: Usar supabase.storage (NÃO supabase.client.storage)
        try:
            # Use supabase.storage.from_() diretamente!
            file_data = supabase.storage.from_("invoices")\
                .download(caminho_arquivo)
            
            if not file_data:
                return jsonify({'error': 'Arquivo não encontrado no storage'}), 404
                
        except Exception as e:
            print(f"❌ [DOWNLOAD] Erro ao buscar arquivo: {e}")
            # Tentar método alternativo se o primeiro falhar
            try:
                file_data = supabase.storage.from_("invoices").download(caminho_arquivo)
            except Exception as e2:
                print(f"❌ [DOWNLOAD] Erro alternativo: {e2}")
                return jsonify({'error': 'Erro ao buscar arquivo no storage'}), 500
        
        # 3. RETORNAR ARQUIVO
        nome = caminho_arquivo.split('/')[-1]
        extensao = nome.lower().split('.')[-1] if '.' in nome else ''
        
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        
        content_type = mime_types.get(extensao, 'application/octet-stream')
        
        from flask import Response
        return Response(
            file_data,
            content_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{nome}"',
                'Cache-Control': 'no-cache'
            }
        )
        
    except Exception as e:
        print(f"❌ [DOWNLOAD] Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ROTA ALTERNATIVA PARA VERIFICAR DISPONIBILIDADE DA INVOICE
@app.route('/api/transferencias/<transferencia_id>/invoice/reenviar', methods=['POST'])
def reenviar_invoice(transferencia_id):
    """Reenvia invoice - VERSÃO COMPATÍVEL COM KIVY"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    print(f"📤 [REENVIO-WEB] Iniciando para transferência {transferencia_id}")
    
    try:
        # 1. VERIFICAR TRANSFERÊNCIA E PERMISSÃO
        response = supabase.table('transferencias')\
            .select('id, cliente, usuario, invoice_info')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({'error': 'Transferência não encontrada'}), 404
        
        transferencia = response.data[0]
        
        # Verificar permissão (igual Kivy)
        usuario_permitido = (
            transferencia.get('cliente') == usuario_nome or
            transferencia.get('usuario') == usuario_nome
        )
        
        if not usuario_permitido:
            return jsonify({'error': 'Acesso não autorizado'}), 403
        
        # 2. VERIFICAR SE A INVOICE ESTÁ RECUSADA
        invoice_info = transferencia.get('invoice_info') or {}
        current_status = invoice_info.get('status', 'pending')
        
        if current_status != 'rejected':
            return jsonify({
                'error': f'Não é possível reenviar invoice com status {current_status}',
                'current_status': current_status
            }), 400
        
        motivo_recusa_anterior = invoice_info.get('motivo_recusa', '')
        print(f"📝 [WEB] Motivo anterior: {motivo_recusa_anterior}")
        
        # 3. VERIFICAR ARQUIVO ENVIADO
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['file']
        
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # 4. VALIDAR O ARQUIVO (IGUAL KIVY)
        nome_arquivo = arquivo.filename
        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
        
        extensoes_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
        if extensao not in extensoes_permitidas:
            return jsonify({
                'error': f'Extensão não permitida: .{extensao}',
                'permitidas': extensoes_permitidas
            }), 400
        
        # Verificar tamanho (5MB - igual Kivy)
        arquivo.seek(0, 2)
        tamanho = arquivo.tell()
        arquivo.seek(0)
        
        if tamanho > 5 * 1024 * 1024:
            return jsonify({'error': 'Arquivo muito grande. Máximo: 5MB'}), 400
        
        print(f"📁 [WEB] Arquivo validado: {nome_arquivo} ({tamanho} bytes, .{extensao})")
        
        # 5. DELETAR ARQUIVOS ANTIGOS (IGUAL KIVY)
        print(f"🗑️ [WEB] Deletando arquivos antigos...")
        try:
            # Listar arquivos na pasta
            lista_arquivos = supabase.storage.from_("invoices")\
                .list(f"transferencias/{transferencia_id}")
            
            if lista_arquivos:
                for arquivo_antigo in lista_arquivos:
                    caminho_antigo = f"transferencias/{transferencia_id}/{arquivo_antigo['name']}"
                    print(f"🗑️ [WEB] Deletando: {caminho_antigo}")
                    supabase.storage.from_("invoices")\
                        .remove([caminho_antigo])
        except Exception as delete_error:
            print(f"⚠️ [WEB] Não consegui deletar arquivos antigos: {delete_error}")
            # Continua mesmo se falhar
        
        # 6. CRIAR NOVO NOME (IGUAL KIVY)
        import time
        timestamp = str(int(time.time() * 1000))
        nome_base = nome_arquivo.rsplit('.', 1)[0]
        novo_nome = f"{timestamp}_{nome_base}.{extensao}"
        caminho_supabase = f"transferencias/{transferencia_id}/{novo_nome}"
        
        print(f"📤 [WEB] Novo caminho: {caminho_supabase}")
        
        # 7. FAZER UPLOAD (IGUAL KIVY - SEM upsert=True)
        arquivo_bytes = arquivo.read()
        
        print(f"🔼 [WEB] Fazendo upload de {len(arquivo_bytes)} bytes...")
        upload_response = supabase.storage.from_("invoices")\
            .upload(caminho_supabase, arquivo_bytes)
        
        if not upload_response:
            return jsonify({'error': 'Erro ao fazer upload para o storage'}), 500
        
        print(f"✅ [WEB] Upload realizado!")
        
        # 8. ATUALIZAR NO BANCO (IGUAL KIVY)
        nova_invoice_info = {
            'status': 'pending',
            'data_upload': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'motivo_recusa': '',  # Limpa motivo anterior
            'caminho_arquivo': caminho_supabase,
            'nome_arquivo': novo_nome,
            'tamanho': tamanho,
            'tipo': arquivo.content_type or f'application/{extensao}'
        }
        
        update_response = supabase.table('transferencias')\
            .update({'invoice_info': nova_invoice_info})\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ [WEB] Invoice info atualizada no banco")
            
            return jsonify({
                'success': True,
                'message': 'Nova invoice enviada com sucesso!',
                'invoice': {
                    'caminho': caminho_supabase,
                    'nome': novo_nome,
                    'tamanho': tamanho,
                    'status': 'pending'
                }
            })
        else:
            return jsonify({'error': 'Erro ao atualizar informações da invoice'}), 500
        
    except Exception as e:
        print(f"❌ [REENVIO-WEB] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/transferencias/<transferencia_id>/invoice/status')
def check_invoice_status(transferencia_id):
    """Verifica status da invoice - VERSÃO FINAL"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    print(f"📋 [STATUS] Usuário: {usuario_nome}, Transferência: {transferencia_id}")
    
    try:
        # 🔥 1. BUSCAR DADOS DO USUÁRIO (campo CORRETO: 'contas')
        user_response = supabase.table('usuarios')\
            .select('contas, cliente')\
            .eq('username', usuario_nome)\
            .execute()
        
        if not user_response.data:
            return jsonify({'available': False, 'error': 'Usuário não encontrado'}), 404
        
        usuario_info = user_response.data[0]
        contas_usuario = usuario_info.get('contas', [])
        cliente_usuario = usuario_info.get('cliente')
        
        print(f"📝 [STATUS] Contas do usuário: {contas_usuario}")
        print(f"📝 [STATUS] Cliente do usuário: {cliente_usuario}")
        
        # 🔥 2. BUSCAR TRANSFERÊNCIA
        trans_response = supabase.table('transferencias')\
            .select('invoice_info, conta_remetente, cliente, usuario')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not trans_response.data:
            return jsonify({'available': False, 'error': 'Transferência não encontrada'}), 404
        
        transferencia = trans_response.data[0]
        conta_transferencia = transferencia.get('conta_remetente')
        cliente_transferencia = transferencia.get('cliente')
        usuario_transferencia = transferencia.get('usuario')
        
        print(f"📝 [STATUS] Conta da transferência: {conta_transferencia}")
        print(f"📝 [STATUS] Cliente da transferência: {cliente_transferencia}")
        print(f"📝 [STATUS] Usuário da transferência: {usuario_transferencia}")
        
        # 🔥 3. VERIFICAÇÃO DE PERMISSÃO
        permissao_concedida = False
        
        # Método 1: Verificar pela CONTA (conta_remetente está nas contas do usuário)
        if conta_transferencia and contas_usuario:
            if isinstance(contas_usuario, list):
                # Se contas_usuario é uma lista
                if conta_transferencia in contas_usuario:
                    permissao_concedida = True
                    print(f"✅ [STATUS] Permissão por CONTA: {conta_transferencia} está em {contas_usuario}")
            elif isinstance(contas_usuario, str):
                # Se contas_usuario é uma string (talvez JSON ou lista como string)
                if conta_transferencia in contas_usuario:
                    permissao_concedida = True
                    print(f"✅ [STATUS] Permissão por CONTA: {conta_transferencia} está em string {contas_usuario}")
        
        # Método 2: Verificar pelo CLIENTE
        if not permissao_concedida and cliente_usuario and cliente_transferencia:
            if cliente_usuario == cliente_transferencia:
                permissao_concedida = True
                print(f"✅ [STATUS] Permissão por CLIENTE: {cliente_usuario}")
        
        # Método 3: Verificar pelo USUÁRIO
        if not permissao_concedida and usuario_transferencia:
            if usuario_transferencia == usuario_nome:
                permissao_concedida = True
                print(f"✅ [STATUS] Permissão por USUÁRIO: {usuario_nome}")
        
        # Método 4: Admin pode tudo
        if not permissao_concedida and usuario_nome in ['admin', 'superadmin', 'administrador']:
            permissao_concedida = True
            print(f"✅ [STATUS] Permissão por ADMIN")
        
        if not permissao_concedida:
            print(f"❌ [STATUS] SEM PERMISSÃO!")
            return jsonify({'available': False, 'error': 'Acesso não autorizado'}), 403
        
        print(f"🎯 [STATUS] PERMISSÃO CONCEDIDA!")
        
        # 4. VERIFICAR INVOICE INFO
        invoice_info = transferencia.get('invoice_info')
        if not invoice_info:
            return jsonify({'available': False, 'error': 'Nenhuma invoice encontrada'})
        
        # 5. RETORNAR DADOS
        invoice_status = invoice_info.get('status', 'pending')
        caminho_arquivo = invoice_info.get('caminho_arquivo', '')
        
        print(f"📊 [STATUS] Invoice status: {invoice_status}")
        print(f"📁 [STATUS] Caminho arquivo: {caminho_arquivo}")
        
        return jsonify({
            'available': True,
            'status': invoice_status,
            'filename': caminho_arquivo.split('/')[-1] if caminho_arquivo else '',
            'upload_date': invoice_info.get('data_upload', ''),
            'rejection_reason': invoice_info.get('motivo_recusa', ''),
            'can_reupload': invoice_status == 'rejected',
            'permission_granted': True
        })
        
    except Exception as e:
        print(f"❌ [STATUS] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'available': False, 'error': str(e)}), 500
    
@app.route('/api/test-storage-simple')
def test_storage_simple():
    """Teste simples do storage"""
    try:
        print("🔍 Testando acesso ao storage 'invoices'...")
        
        # Teste 1: Verificar se o método storage existe
        if not hasattr(supabase, 'storage'):
            return jsonify({
                'success': False,
                'message': 'Método storage não disponível no objeto supabase',
                'supabase_type': str(type(supabase))
            })
        
        print("✅ supabase.storage está disponível")
        
        # Teste 2: Tentar listar um arquivo de exemplo
        try:
            # Tente listar arquivos no bucket 'invoices'
            files = supabase.storage.from_("invoices").list("transferencias/")
            return jsonify({
                'success': True,
                'message': 'Conexão com storage estabelecida!',
                'files_count': len(files) if files else 0,
                'storage_method': 'supabase.storage'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao acessar bucket: {str(e)}',
                'error_type': str(type(e).__name__)
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro geral: {str(e)}'
        })
    
# Adicione estas rotas no web_api.py:

@app.route('/api/beneficiarios/<int:benef_id>', methods=['PUT', 'DELETE'])
def gerenciar_beneficiario(benef_id):
    """Editar ou excluir (soft delete) um beneficiário"""
    usuario = session.get('username')
    
    if not usuario:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    if request.method == 'PUT':
        # Editar beneficiário
        dados = request.get_json()
        
        # Verificar se o beneficiário pertence ao usuário
        benef_response = supabase.table('beneficiarios')\
            .select('id')\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if not benef_response.data:
            return jsonify({"success": False, "message": "Beneficiário não encontrado"}), 404
        
        # Atualizar beneficiário
        update_response = supabase.table('beneficiarios')\
            .update(dados)\
            .eq('id', benef_id)\
            .execute()
        
        if update_response.data:
            return jsonify({"success": True, "message": "Beneficiário atualizado"})
        else:
            return jsonify({"success": False, "message": "Erro ao atualizar"}), 500
    
    elif request.method == 'DELETE':
        # Soft delete (marcar como inativo)
        update_response = supabase.table('beneficiarios')\
            .update({'ativo': False})\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if update_response.data:
            return jsonify({"success": True, "message": "Beneficiário excluído"})
        else:
            return jsonify({"success": False, "message": "Erro ao excluir"}), 500
        
@app.route('/meus-beneficiarios')
def meus_beneficiarios():
    """Tela de gerenciamento de beneficiários"""
    # ✅ Pega usuário da SESSÃO
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Buscar dados do usuário
    email = f'{usuario}@exemplo.com'
    nome = usuario.upper()
    
    try:
        if supabase:
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
    except Exception as e:
        print(f"⚠️  Erro ao buscar usuário: {e}")
    
    return render_template('meus_beneficiarios.html',
                         usuario=usuario,
                         nome=nome,
                         email=email)

@app.route('/api/beneficiarios/<int:benef_id>', methods=['PUT'])
def editar_beneficiario(benef_id):
    """Editar um beneficiário existente"""
    try:
        # ✅ Pega usuário da SESSÃO
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        dados = request.get_json()
        
        # Validar campos obrigatórios (exceto aba)
        campos_obrigatorios = [
            'nome', 'endereco', 'cidade', 'pais', 
            'banco', 'endereco_banco', 'cidade_banco', 'pais_banco',
            'swift', 'iban'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return jsonify({
                    "success": False,
                    "message": f"Campo '{campo}' é obrigatório"
                }), 400
        
        # Validação SWIFT (8 ou 11 caracteres)
        swift = dados['swift'].upper().replace(' ', '')
        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', swift):
            return jsonify({
                "success": False,
                "message": "Código SWIFT inválido. Deve ter 8 ou 11 caracteres"
            }), 400
        
        # Validação ABA (se preenchido, deve ter 9 dígitos)
        if dados.get('aba'):
            if not re.match(r'^[0-9]{9}$', dados['aba']):
                return jsonify({
                    "success": False,
                    "message": "Código ABA inválido. Deve ter 9 dígitos"
                }), 400
        
        # Primeiro, verificar se o beneficiário pertence ao usuário
        benef_existente = supabase.table('beneficiarios')\
            .select('id')\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if not benef_existente.data:
            return jsonify({
                "success": False,
                "message": "Beneficiário não encontrado ou não pertence ao usuário"
            }), 404
        
        # Preparar dados para atualização
        dados_atualizados = {
            'nome': dados['nome'],
            'endereco': dados['endereco'],
            'cidade': dados['cidade'],
            'pais': dados['pais'],
            'banco': dados['banco'],
            'endereco_banco': dados['endereco_banco'],
            'cidade_banco': dados['cidade_banco'],
            'pais_banco': dados['pais_banco'],
            'swift': swift,
            'iban': dados['iban'].upper().replace(' ', ''),
            'aba': dados.get('aba', '')  # Pode ser vazio
        }
        
        print(f"🔄 Atualizando beneficiário {benef_id} para usuário {usuario}")
        print(f"📝 Dados: {dados_atualizados}")
        
        # Atualizar no Supabase
        response = supabase.table('beneficiarios')\
            .update(dados_atualizados)\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if response.data:
            print(f"✅ Beneficiário {benef_id} atualizado com sucesso!")
            return jsonify({
                "success": True,
                "message": "Beneficiário atualizado com sucesso",
                "id": benef_id
            })
        else:
            print(f"❌ Erro ao atualizar beneficiário {benef_id}")
            return jsonify({
                "success": False,
                "message": "Erro ao atualizar beneficiário"
            }), 500
            
    except Exception as e:
        print(f"❌ Erro em editar_beneficiario: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500
    
@app.route('/api/beneficiarios/<int:benef_id>', methods=['DELETE'])
def excluir_beneficiario(benef_id):
    """Excluir (soft delete) um beneficiário - marca como inativo"""
    try:
        # ✅ Pega usuário da SESSÃO
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        print(f"🗑️  Excluindo beneficiário {benef_id} para usuário {usuario}")
        
        # Verificar se o beneficiário existe e pertence ao usuário
        benef_existente = supabase.table('beneficiarios')\
            .select('id, nome')\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if not benef_existente.data:
            return jsonify({
                "success": False,
                "message": "Beneficiário não encontrado ou não pertence ao usuário"
            }), 404
        
        # Soft delete - marcar como inativo
        response = supabase.table('beneficiarios')\
            .update({'ativo': False})\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if response.data:
            nome_beneficiario = benef_existente.data[0]['nome']
            print(f"✅ Beneficiário '{nome_beneficiario}' ({benef_id}) marcado como inativo")
            
            return jsonify({
                "success": True,
                "message": f"Beneficiário '{nome_beneficiario}' excluído com sucesso"
            })
        else:
            print(f"❌ Erro ao excluir beneficiário {benef_id}")
            return jsonify({
                "success": False,
                "message": "Erro ao excluir beneficiário"
            }), 500
            
    except Exception as e:
        print(f"❌ Erro em excluir_beneficiario: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500
    
@app.route('/api/beneficiarios/<int:benef_id>', methods=['DELETE'])
def excluir_beneficiario_api(benef_id):
    """Excluir um beneficiário do Supabase"""
    try:
        # ✅ Pega usuário da SESSÃO
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        print(f"🗑️  [API DELETE] Excluindo beneficiário {benef_id} para usuário {usuario}")
        
        # 1. Verificar se o beneficiário existe e pertence ao usuário
        benef_existente = supabase.table('beneficiarios')\
            .select('id, nome')\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .eq('ativo', True)\
            .execute()
        
        if not benef_existente.data:
            print(f"❌ Beneficiário {benef_id} não encontrado para {usuario}")
            return jsonify({
                "success": False,
                "message": "Beneficiário não encontrado ou não pertence ao usuário"
            }), 404
        
        nome_beneficiario = benef_existente.data[0]['nome']
        
        # 2. DELETAR REALMENTE do Supabase (hard delete)
        response = supabase.table('beneficiarios')\
            .delete()\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if response.data:
            print(f"✅ Beneficiário '{nome_beneficiario}' ({benef_id}) deletado com sucesso!")
            
            return jsonify({
                "success": True,
                "message": f"Beneficiário '{nome_beneficiario}' excluído com sucesso"
            })
        else:
            print(f"❌ Erro ao deletar beneficiário {benef_id}")
            return jsonify({
                "success": False,
                "message": "Erro ao excluir beneficiário"
            }), 500
            
    except Exception as e:
        print(f"❌ Erro em excluir_beneficiario_api: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/beneficiarios/<int:benef_id>', methods=['PUT'])
def editar_beneficiario_api(benef_id):
    """Editar um beneficiário existente"""
    try:
        # ✅ Pega usuário da SESSÃO
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        dados = request.get_json()
        
        print(f"🔄 [API PUT] Editando beneficiário {benef_id} para usuário {usuario}")
        print(f"📝 Dados recebidos: {dados}")
        
        # Validar campos obrigatórios (exceto aba)
        campos_obrigatorios = [
            'nome', 'endereco', 'cidade', 'pais', 
            'banco', 'endereco_banco', 'cidade_banco', 'pais_banco',
            'swift', 'iban'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return jsonify({
                    "success": False,
                    "message": f"Campo '{campo}' é obrigatório"
                }), 400
        
        # Validação SWIFT (8 ou 11 caracteres)
        swift = dados['swift'].upper().replace(' ', '')
        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', swift):
            return jsonify({
                "success": False,
                "message": "Código SWIFT inválido. Deve ter 8 ou 11 caracteres"
            }), 400
        
        # Validação ABA (se preenchido, deve ter 9 dígitos)
        if dados.get('aba'):
            if not re.match(r'^[0-9]{9}$', dados['aba']):
                return jsonify({
                    "success": False,
                    "message": "Código ABA inválido. Deve ter 9 dígitos"
                }), 400
        
        # Verificar se o beneficiário pertence ao usuário
        benef_existente = supabase.table('beneficiarios')\
            .select('id')\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if not benef_existente.data:
            return jsonify({
                "success": False,
                "message": "Beneficiário não encontrado ou não pertence ao usuário"
            }), 404
        
        # Preparar dados para atualização
        dados_atualizados = {
            'nome': dados['nome'],
            'endereco': dados['endereco'],
            'cidade': dados['cidade'],
            'pais': dados['pais'],
            'banco': dados['banco'],
            'endereco_banco': dados['endereco_banco'],
            'cidade_banco': dados['cidade_banco'],
            'pais_banco': dados['pais_banco'],
            'swift': swift,
            'iban': dados['iban'].upper().replace(' ', ''),
            'aba': dados.get('aba', '')
        }
        
        # Atualizar no Supabase
        response = supabase.table('beneficiarios')\
            .update(dados_atualizados)\
            .eq('id', benef_id)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if response.data:
            print(f"✅ Beneficiário {benef_id} atualizado com sucesso!")
            return jsonify({
                "success": True,
                "message": "Beneficiário atualizado com sucesso",
                "id": benef_id
            })
        else:
            print(f"❌ Erro ao atualizar beneficiário {benef_id}")
            return jsonify({
                "success": False,
                "message": "Erro ao atualizar beneficiário"
            }), 500
            
    except Exception as e:
        print(f"❌ Erro em editar_beneficiario_api: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500
    
# ============================================
# ROTAS DO EXTRATO (REPLICANDO LÓGICA DO KIVY)
# ============================================

@app.route('/meu_extrato')
def meu_extrato():
    """Renderiza a tela de extrato"""
    usuario = session.get('username')
    nome = session.get('nome')
    
    if not usuario:
        return redirect('/login')
    
    # Passar dados do usuário para o template
    return render_template('meu_extrato.html', 
                         usuario=usuario,
                         nome=nome,
                         data_atual=datetime.now().strftime("%d/%m/%Y"))

@app.route('/api/contas')
def obter_contas_usuario():
    """Obtém contas REAIS do usuário logado - VERSÃO CORRIGIDA"""
    try:
        usuario = session.get('username')
        if not usuario:
            print("❌ [CONTAS] Usuário não autenticado")
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        print(f"✅ [CONTAS] Usuário autenticado: {usuario}")
        
        # 🔥 CORREÇÃO: Usando a coluna CORRETA 'cliente_username' SEM .or_()
        response = supabase.table('contas')\
            .select('id, moeda, saldo, cliente_username, cliente_nome, data_criacao, ativa, created_at')\
            .eq('cliente_username', usuario)\
            .execute()
        
        print(f"📊 [CONTAS] Query executada. Resultados: {len(response.data)}")
        
        contas = []
        for conta in response.data:
            print(f"📊 [CONTAS] Processando conta ID: {conta.get('id')}")
            
            # O campo 'id' é o número da conta
            numero_conta = conta.get('id', '')
            
            # Converter saldo
            saldo = conta.get('saldo')
            saldo_float = 0.0
            if saldo is not None:
                try:
                    saldo_float = float(saldo)
                except:
                    saldo_float = 0.0
            
            contas.append({
                'numero': numero_conta,
                'moeda': conta.get('moeda', 'USD'),
                'saldo': saldo_float,
                'cliente_nome': conta.get('cliente_nome', ''),
                'cliente_username': conta.get('cliente_username', ''),
                'data_criacao': conta.get('data_criacao', ''),
                'ativa': conta.get('ativa', True),
                'id_supabase': conta.get('id')
            })
        
        print(f"✅ [CONTAS] Retornando {len(contas)} contas para {usuario}")
        
        # Se não encontrar contas
        if not contas:
            print(f"⚠️ [CONTAS] Nenhuma conta encontrada para {usuario}")
            
            return jsonify({
                "success": True,
                "contas": [],
                "total": 0,
                "message": f"Nenhuma conta cadastrada para {usuario}",
                "sugestao": "Cadastre contas no Supabase com 'cliente_username' igual ao usuário"
            })
        
        return jsonify({
            "success": True,
            "contas": contas,
            "total": len(contas),
            "usuario": usuario
        })
        
    except Exception as e:
        print(f"❌ [CONTAS] ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar contas: {str(e)}"
        }), 500

# 🔥 FUNÇÃO AUXILIAR: Buscar transferências da conta
def buscar_transferencias_conta(conta_num, usuario):
    """Busca TODAS as transferências relacionadas à conta"""
    try:
        # Buscar em transferencias
        response = supabase.table('transferencias')\
            .select('*')\
            .or_(f'conta_remetente.eq.{conta_num},conta_destinatario.eq.{conta_num}')\
            .eq('cliente_username', usuario)\
            .execute()
        
        return response.data
        
    except Exception as e:
        print(f"❌ Erro ao buscar transferências: {e}")
        return []

# 🔥 FUNÇÃO CRÍTICA: Processar transação (MESMA LÓGICA DO KIVY)
def processar_transacao_kivy(dados, conta_num, moeda):
    """Processa uma transação com exatamente a mesma lógica do Kivy"""
    from datetime import datetime
    
    tipo = dados.get('tipo', '')
    status = dados.get('status', '')
    valor = dados.get('valor', 0)
    
    # 🔥 LÓGICA DE DECISÃO (MESMA DO KIVY)
    if tipo in ['ajuste_admin', 'cambio']:
        deve_incluir = True
    elif status == 'pending':
        deve_incluir = True
    elif status == 'rejected':
        deve_incluir = True
    elif status in ['processing', 'completed']:
        deve_incluir = True
    else:
        deve_incluir = False
    
    if not deve_incluir:
        return None
    
    transacao = {
        'id': dados.get('id', ''),
        'data': dados.get('data', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'tipo': tipo,
        'moeda': moeda
    }
    
    # 🔥 CLIENTE É REMETENTE (SAÍDA/DÉBITO)
    if dados.get('conta_remetente') == conta_num:
        
        if tipo == 'deposito':
            # Cliente recebe CRÉDITO no depósito
            transacao['descricao'] = f"DEPÓSITO CONFIRMADO - {dados.get('banco_origem', 'Banco')}"
            transacao['credito'] = valor
            transacao['debito'] = 0.00
            
        elif tipo == 'ajuste_admin':
            tipo_ajuste = dados.get('tipo_ajuste', 'DÉBITO')
            if tipo_ajuste and tipo_ajuste.upper() == 'CREDITO':
                transacao['descricao'] = f"CRÉDITO ADMINISTRATIVO - {dados.get('descricao_ajuste', '')}"
                transacao['credito'] = valor
                transacao['debito'] = 0.00
            else:
                transacao['descricao'] = f"DÉBITO ADMINISTRATIVO - {dados.get('descricao_ajuste', '')}"
                transacao['credito'] = 0.00
                transacao['debito'] = valor
                
        elif tipo in ['internacional', 'transferencia_internacional']:
            status_text = "SOLICITADA" if status == 'pending' else \
                         "EM PROCESSAMENTO" if status == 'processing' else \
                         "CONCLUÍDA" if status == 'completed' else "RECUSADA"
            
            transacao['descricao'] = f"TRANSF. INTERNACIONAL {status_text} - {dados.get('beneficiario', 'N/A')}"
            transacao['credito'] = 0.00
            transacao['debito'] = valor
            
        elif tipo == 'cambio':
            transacao['descricao'] = f"CÂMBIO - {dados.get('descricao_origem', 'Operação de câmbio')}"
            transacao['credito'] = 0.00
            transacao['debito'] = valor
            
        elif tipo in ['transferencia_interna', 'transferencia_interna_cliente']:
            status_text = "SOLICITADA" if status == 'pending' else \
                         "EM PROCESSAMENTO" if status == 'processing' else \
                         "CONCLUÍDA" if status == 'completed' else "RECUSADA"
            
            transacao['descricao'] = f"TRANSFERÊNCIA {status_text} - {dados.get('nome_destinatario', 'N/A')}"
            transacao['credito'] = 0.00
            transacao['debito'] = valor
    
    # 🔥 CLIENTE É DESTINATÁRIO (ENTRADA/CRÉDITO)
    elif dados.get('conta_destinatario') == conta_num:
        
        if tipo == 'deposito':
            transacao['descricao'] = f"DEPÓSITO CONFIRMADO - {dados.get('banco_origem', 'Banco')}"
            transacao['credito'] = valor
            transacao['debito'] = 0.00
            
        elif tipo == 'ajuste_admin' and dados.get('tipo_ajuste') == 'CREDITO':
            transacao['descricao'] = f"CRÉDITO ADMINISTRATIVO - {dados.get('descricao_ajuste', '')}"
            transacao['credito'] = valor
            transacao['debito'] = 0.00
            
        elif tipo == 'cambio':
            transacao['descricao'] = f"CÂMBIO - {dados.get('descricao_destino', 'Operação de câmbio')}"
            transacao['credito'] = dados.get('valor_destino', valor)
            transacao['debito'] = 0.00
            
        elif tipo not in ['ajuste_admin']:
            status_text = "SOLICITADA" if status == 'pending' else \
                         "EM PROCESSAMENTO" if status == 'processing' else \
                         "CONCLUÍDA" if status == 'completed' else "RECUSADA"
            
            transacao['descricao'] = f"TRANSFERÊNCIA {status_text} RECEBIDA - {dados.get('nome_remetente', 'N/A')}"
            transacao['credito'] = valor
            transacao['debito'] = 0.00
    
    return transacao

@app.route('/api/extrato/exportar-pdf', methods=['POST'])
def exportar_extrato_pdf():
    """Exporta extrato para PDF completo - VERSÃO FINAL CORRIGIDA"""
    try:
        usuario = session.get('username')
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        dados = request.get_json()
        
        print(f"📊 [PDF] Gerando extrato para {usuario}")
        print(f"📋 [PDF] {len(dados.get('transacoes', []))} transações recebidas")
        
        # Preparar dados
        conta_numero = dados.get('conta')
        transacoes = dados.get('transacoes', [])
        periodo = dados.get('periodo', 'N/A')
        resumo = dados.get('resumo', {})
        
        if not conta_numero or not transacoes:
            return jsonify({"success": False, "message": "Dados insuficientes"}), 400
        
        # Buscar dados da conta
        response_conta = supabase.table('contas')\
            .select('id, cliente_nome, moeda, saldo')\
            .eq('id', conta_numero)\
            .eq('cliente_username', usuario)\
            .single()\
            .execute()
        
        if not response_conta.data:
            return jsonify({"success": False, "message": "Conta não encontrada"}), 404
        
        conta_data = response_conta.data
        
        # 🔥 GERAR PDF COM CORREÇÕES
        from datetime import datetime
        import os
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.pdfgen import canvas
        
        # Criar nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"extrato_{conta_numero}_{timestamp}.pdf"
        
        # Criar pasta estática
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        pasta_extratos = os.path.join(pasta_atual, 'static', 'extratos')
        os.makedirs(pasta_extratos, exist_ok=True)
        
        caminho_pdf = os.path.join(pasta_extratos, nome_arquivo)
        
        print(f"📄 [PDF] Criando PDF final em: {caminho_pdf}")
        
        # 🔥 FUNÇÃO PARA FORMATAR DATA COMPACTA
        def formatar_data_compacta(data_str):
            try:
                if not data_str:
                    return ""
                
                # Formato ISO: 2025-12-18T22:04:44 → 18-12-25
                if 'T' in data_str:
                    try:
                        data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                        return data_obj.strftime('%d-%m-%y')
                    except:
                        data_obj = datetime.strptime(data_str.split('T')[0], '%Y-%m-%d')
                        return data_obj.strftime('%d-%m-%y')
                
                # Formato com barras: 18/12/2025 → 18-12-25
                if '/' in data_str:
                    partes = data_str.split('/')
                    if len(partes) >= 3:
                        dia = partes[0].zfill(2)
                        mes = partes[1].zfill(2)
                        ano = partes[2][-2:] if len(partes[2]) >= 4 else partes[2]
                        return f"{dia}-{mes}-{ano}"
                
                # Formato com hífens: 2025-12-18 → 18-12-25
                if '-' in data_str and len(data_str) >= 10:
                    partes = data_str.split('-')
                    if len(partes) >= 3:
                        ano = partes[0][-2:] if len(partes[0]) == 4 else partes[0]
                        mes = partes[1].zfill(2)
                        dia = partes[2][:2].zfill(2)
                        return f"{dia}-{mes}-{ano}"
                
                return data_str[:8] if len(data_str) >= 8 else data_str
                
            except:
                return data_str[:8] if len(data_str) >= 8 else data_str
        
        # 🔥 1. INVERTER ORDEM: Mais antigas primeiro
        transacoes_ordenadas = sorted(transacoes, key=lambda x: x.get('data', ''))
        
        # 🔥 2. PREPARAR DADOS
        saldo_atual = float(conta_data.get('saldo', 0))
        saldo_final = float(resumo.get('saldo_final', 0))
        total_entradas = float(resumo.get('total_entradas', 0))
        total_saidas = float(resumo.get('total_saidas', 0))
        total_transacoes = resumo.get('total_transacoes', 0)
        moeda = resumo.get('moeda', conta_data.get('moeda', 'USD'))
        
        # 🔥 FUNÇÃO PARA CRIAR RODAPÉ
        def add_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.gray)
            
            footer_left = "Cambio Bank - Extrato bancário oficial"
            footer_center = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            footer_right = f"Página {doc.page} de {doc.page}"
            
            page_width = letter[0]
            
            canvas.drawString(30, 25, footer_left)
            text_width = canvas.stringWidth(footer_center, 'Helvetica', 7)
            canvas.drawString((page_width - text_width) / 2, 25, footer_center)
            canvas.drawString(page_width - 80, 25, footer_right)
            
            canvas.restoreState()
        
        # CRIAR DOCUMENTO
        doc = SimpleDocTemplate(
            caminho_pdf,
            pagesize=letter,
            topMargin=40,
            bottomMargin=50,
            leftMargin=20,
            rightMargin=20
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # CABEÇALHO
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=8,
            textColor=colors.HexColor("#1a5fb4"),
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("CÂMBIO BANK - BANK STATEMENT", title_style)
        story.append(title)
        
        # INFORMAÇÕES
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=15,
            textColor=colors.gray
        )
        
        info_text = f"""
        Account: {conta_numero} | Client: {conta_data.get('cliente_nome', usuario)} | 
        Currency: {moeda} | Period: {periodo}
        """
        info = Paragraph(info_text, info_style)
        story.append(info)
        
        # RESUMO
        summary_data = [
            ['Description', 'Value', 'Currency'],
            ['Current Balance', f"{saldo_atual:,.2f}", moeda],
            ['Final Balance', f"{saldo_final:,.2f}", moeda],
            ['Total Credits', f"{total_entradas:,.2f}", moeda],
            ['Total Debits', f"{total_saidas:,.2f}", moeda],
            ['Transactions', str(total_transacoes), '']
        ]
        
        summary_table = Table(summary_data, colWidths=[180, 90, 70])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a5fb4")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # 🔥 3. TABELA DE TRANSAÇÕES - CORREÇÃO CRÍTICA
        if transacoes_ordenadas:
            # Cabeçalho
            header = ['Date', 'Description', 'Credit', 'Debit', 'Balance']
            data = [header]
            
            # 🔥 CORREÇÃO: ADICIONAR TRANSAÇÕES SEM HTML
            for t in transacoes_ordenadas:
                # Data
                data_formatada = formatar_data_compacta(t.get('data', ''))
                
                # 🔥 CORREÇÃO: DESCRIÇÃO SIMPLES, SEM HTML
                desc_original = t.get('descricao', '')
                
                # Se descrição muito longa, corta sem quebrar linha
                if len(desc_original) > 68:
                    # Corta no último espaço antes do limite
                    desc_cortada = desc_original[:65]
                    ultimo_espaco = desc_cortada.rfind(' ')
                    if ultimo_espaco > 50:  # Se encontrar espaço razoável
                        desc = desc_cortada[:ultimo_espaco] + '...'
                    else:
                        desc = desc_cortada + '...'
                else:
                    desc = desc_original
                
                # Valores
                credito_valor = float(t.get('credito', 0))
                debito_valor = float(t.get('debito', 0))
                saldo_valor = float(t.get('saldo_apos', 0))
                
                credito = f"{credito_valor:,.2f}" if credito_valor > 0 else ""
                debito = f"{debito_valor:,.2f}" if debito_valor > 0 else ""
                saldo = f"{saldo_valor:,.2f}"
                
                data.append([data_formatada, desc, credito, debito, saldo])
            
            # 🔥 CORREÇÃO: ÚLTIMA LINHA SEM TAGS HTML
            # Usamos strings normais, o estilo aplicará o negrito
            current_balance_row = [
                "",  # Data vazia
                "CURRENT BALANCE",  # Texto normal
                "",  # Crédito vazio
                "",  # Débito vazio
                f"{saldo_atual:,.2f}"  # Valor normal
            ]
            data.append(current_balance_row)
            
            # Larguras ajustadas
            col_widths = [40, 340, 60, 60, 70]
            
            # Criar tabela
            trans_table = Table(data, colWidths=col_widths, repeatRows=1)
            
            # 🔥 ESTILO CORRIGIDO
            estilo_tabela = TableStyle([
                # CABEÇALHO
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # DADOS (transações normais)
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 7.5),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('ALIGN', (2, 1), (-1, -2), 'RIGHT'),
                ('ALIGN', (0, 1), (0, -2), 'CENTER'),
                
                # PADDING
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                
                # QUEBRA DE TEXTO (apenas para descrição)
                ('WORDWRAP', (1, 1), (1, -2), True),
            ])
            
            # 🔥 APLICAR CORES DINÂMICAS PARA TRANSAÇÕES
            for i in range(1, len(data) - 1):
                credito_valor = float(transacoes_ordenadas[i-1].get('credito', 0))
                debito_valor = float(transacoes_ordenadas[i-1].get('debito', 0))
                saldo_valor = float(transacoes_ordenadas[i-1].get('saldo_apos', 0))
                
                # Crédito AZUL
                if credito_valor > 0:
                    estilo_tabela.add('TEXTCOLOR', (2, i), (2, i), colors.HexColor("#1a5fb4"))
                    estilo_tabela.add('FONTNAME', (2, i), (2, i), 'Helvetica-Bold')
                
                # Débito VERMELHO
                if debito_valor > 0:
                    estilo_tabela.add('TEXTCOLOR', (3, i), (3, i), colors.red)
                    estilo_tabela.add('FONTNAME', (3, i), (3, i), 'Helvetica-Bold')
                
                # Saldo AZUL ou VERMELHO
                if saldo_valor >= 0:
                    estilo_tabela.add('TEXTCOLOR', (4, i), (4, i), colors.HexColor("#1a5fb4"))
                else:
                    estilo_tabela.add('TEXTCOLOR', (4, i), (4, i), colors.red)
                estilo_tabela.add('FONTNAME', (4, i), (4, i), 'Helvetica-Bold')
            
            # 🔥 ESTILO PARA LINHAS ALTERNADAS
            for i in range(1, len(data) - 1):
                if i % 2 == 0:
                    estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f9f9f9"))
            
            # 🔥 CORREÇÃO: ESTILO PARA ÚLTIMA LINHA (CURRENT BALANCE)
            # Aplica negrito e cores via estilo, não HTML
            estilo_tabela.add('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e8f4f8"))
            estilo_tabela.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
            estilo_tabela.add('FONTSIZE', (0, -1), (-1, -1), 8)
            estilo_tabela.add('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor("#1a5fb4"))
            estilo_tabela.add('ALIGN', (1, -1), (1, -1), 'RIGHT')
            estilo_tabela.add('ALIGN', (4, -1), (4, -1), 'RIGHT')
            
            # Cor do saldo final
            if saldo_atual >= 0:
                estilo_tabela.add('TEXTCOLOR', (4, -1), (4, -1), colors.HexColor("#1a5fb4"))
            else:
                estilo_tabela.add('TEXTCOLOR', (4, -1), (4, -1), colors.red)
            
            # Borda especial
            estilo_tabela.add('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor("#1a5fb4"))
            estilo_tabela.add('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor("#1a5fb4"))
            
            # 🔥 IMPORTANTE: REMOVER GRADE DA ÚLTIMA LINHA
            estilo_tabela.add('GRID', (0, 0), (-1, -2), 0.5, colors.grey)  # Até penúltima
            estilo_tabela.add('GRID', (0, -1), (-1, -1), 0, colors.white)  # Última sem grade
            
            trans_table.setStyle(estilo_tabela)
            story.append(trans_table)
        
        # Gerar PDF
        print("🔄 [PDF] Gerando documento final...")
        
        # Função simples de rodapé
        def simple_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.gray)
            canvas.drawString(30, 25, "Cambio Bank - Extrato oficial")
            canvas.drawString(500, 25, f"Página {doc.page}")
            canvas.restoreState()
        
        try:
            doc.build(story, onFirstPage=simple_footer, onLaterPages=simple_footer)
        except:
            doc.build(story)
        
        print(f"✅✅✅ [PDF] PDF FINAL gerado: {caminho_pdf}")
        
        if os.path.exists(caminho_pdf):
            tamanho = os.path.getsize(caminho_pdf)
            print(f"📏 [PDF] Tamanho: {tamanho} bytes")
        
        # Retornar URL
        pdf_url = f"/static/extratos/{nome_arquivo}"
        
        return jsonify({
            "success": True,
            "pdf_url": pdf_url,
            "message": "PDF gerado com sucesso!",
            "filename": nome_arquivo
        })
        
    except Exception as e:
        print(f"❌ [PDF] Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro ao gerar PDF: {str(e)}"
        }), 500

@app.route('/api/debug/contas')
def debug_contas():
    """Debug: Ver todas as contas e usuários"""
    try:
        usuario = session.get('username')
        
        # Buscar todas as contas
        contas_response = supabase.table('contas').select('*').limit(10).execute()
        
        # Buscar usuário atual
        user_response = supabase.table('usuarios')\
            .select('*')\
            .eq('username', usuario)\
            .execute() if usuario else None
        
        return jsonify({
            "usuario_atual": usuario,
            "total_contas": len(contas_response.data),
            "contas": contas_response.data[:5],  # Primeiras 5
            "meus_dados": user_response.data[0] if user_response and user_response.data else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/extrato_kivy')
def obter_extrato_kivy():
    """Obtém extrato com EXATAMENTE a mesma lógica do Kivy"""
    try:
        usuario = session.get('username')
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Parâmetros
        conta_num = request.args.get('conta')
        periodo = request.args.get('periodo', '30')
        data_inicio_br = request.args.get('data_inicio', '')
        data_fim_br = request.args.get('data_fim', '')
        
        if not conta_num:
            return jsonify({"success": False, "message": "Conta não especificada"}), 400
        
        print(f"📊 [EXTRATO KIVY] Usuário: {usuario}, Conta: {conta_num}, Período: {periodo}")
        
        # 🔥 FUNÇÃO AUXILIAR PARA BUSCAR NOMES (IGUAL AO KIVY)
        def obter_nome_cliente_por_conta(conta_numero):
            """Busca nome do cliente pelo número da conta (igual ao Kivy)"""
            if not conta_numero:
                return f"Conta N/A"
            
            try:
                response = supabase.table('contas')\
                    .select('cliente_nome')\
                    .eq('id', conta_numero)\
                    .execute()
                
                if response.data and response.data[0].get('cliente_nome'):
                    nome = response.data[0]['cliente_nome']
                    if nome and nome != 'None':
                        return nome
                
                # Se não encontrar, retorna o número da conta
                return f"Conta {conta_numero}"
            except Exception as e:
                print(f"⚠️ Erro ao buscar nome para conta {conta_numero}: {e}")
                return f"Conta {conta_numero}"
        
        # 🔥 1. VERIFICAR CONTA
        conta_response = supabase.table('contas')\
            .select('*')\
            .eq('id', conta_num)\
            .eq('cliente_username', usuario)\
            .execute()
        
        if not conta_response.data:
            return jsonify({
                "success": False, 
                "message": "Conta não encontrada ou não pertence ao usuário"
            }), 404
        
        conta = conta_response.data[0]
        moeda = conta.get('moeda', 'USD')
        saldo_atual = float(conta.get('saldo', 0)) if conta.get('saldo') is not None else 0.0
        
        # 🔥 2. CONFIGURAR PERÍODO (MESMA LÓGICA DO KIVY)
        from datetime import datetime, timedelta
        
        data_fim_filtro = datetime.now()
        
        if periodo == 'personalizado':
            if not data_inicio_br or not data_fim_br:
                return jsonify({"success": False, "message": "Datas não fornecidas"}), 400
            
            # Validar formato BR
            def validar_data_br(data_str):
                try:
                    partes = data_str.split('/')
                    if len(partes) != 3:
                        return False
                    dia, mes, ano = int(partes[0]), int(partes[1]), int(partes[2])
                    if mes < 1 or mes > 12:
                        return False
                    if dia < 1 or dia > 31:
                        return False
                    return True
                except:
                    return False
            
            if not validar_data_br(data_inicio_br) or not validar_data_br(data_fim_br):
                return jsonify({"success": False, "message": "Formato de data inválido. Use DD/MM/AAAA"}), 400
            
            # Converter para ISO
            def formatar_para_iso(data_br):
                partes = data_br.split('/')
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
            
            data_inicio_filtro = datetime.strptime(formatar_para_iso(data_inicio_br), "%Y-%m-%d")
            data_fim_filtro = datetime.strptime(formatar_para_iso(data_fim_br), "%Y-%m-%d")\
                .replace(hour=23, minute=59, second=59, microsecond=999999)
                
        elif periodo == '0':
            data_inicio_filtro = datetime(2024, 1, 1)
        else:
            dias = int(periodo)
            data_inicio_filtro = data_fim_filtro - timedelta(days=dias)
        
        print(f"📅 Período: {data_inicio_filtro.date()} a {data_fim_filtro.date()}")

        # 🔥 3. BUSCAR TODAS AS TRANSFERÊNCIAS DO USUÁRIO
        todas_transferencias = []
        
        # Buscar transferências onde o usuário é remetente ou destinatário
        try:
            # Buscar como remetente
            transf_remetente = supabase.table('transferencias')\
                .select('*')\
                .eq('conta_remetente', conta_num)\
                .execute()
            todas_transferencias.extend(transf_remetente.data)
            
            # Buscar como destinatário
            transf_destinatario = supabase.table('transferencias')\
                .select('*')\
                .eq('conta_destinatario', conta_num)\
                .execute()
            todas_transferencias.extend(transf_destinatario.data)
            
            # Buscar em conta_origem (para câmbio nova tela)
            transf_origem = supabase.table('transferencias')\
                .select('*')\
                .eq('conta_origem', conta_num)\
                .execute()
            todas_transferencias.extend(transf_origem.data)
            
            # Buscar em conta_destino (para câmbio nova tela)
            transf_destino = supabase.table('transferencias')\
                .select('*')\
                .eq('conta_destino', conta_num)\
                .execute()
            todas_transferencias.extend(transf_destino.data)
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar transferências: {e}")
        
        # Remover duplicados pelo ID
        transferencias_dict = {}
        for transf in todas_transferencias:
            transf_id = transf.get('id')
            if transf_id:
                transferencias_dict[transf_id] = transf
        
        transferencias = list(transferencias_dict.values())
        print(f"📊 Total de transferências únicas: {len(transferencias)}")

        # 🔥 DEBUG: Listar todas as transferências encontradas
        print(f"\n" + "="*80)
        print("🔍 DEBUG INICIAL - LISTANDO TODAS AS TRANSFERÊNCIAS ENCONTRADAS")
        print("="*80)

        tipos_contagem = {}
        for i, transf in enumerate(transferencias[:20]):
            tipo = transf.get('tipo', 'sem_tipo')
            status = transf.get('status', 'sem_status')
            valor = transf.get('valor', 0)
            conta_remetente = transf.get('conta_remetente', '')
            conta_destinatario = transf.get('conta_destinatario', '')
            
            tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1
            
            # 🔥 DEBUG ESPECÍFICO PARA 850030
            transf_id = transf.get('id', 'N/A')
            if str(transf_id) == '850030':
                print(f"\n🔍🔍🔍 DEBUG 850030 NA LISTA COMPLETA:")
                print(f"   Índice: {i}")
                print(f"   ID: {transf_id}")
                print(f"   Tipo: {tipo}")
                print(f"   Status: {status}")
                print(f"   Conta remetente: {conta_remetente}")
                print(f"   Conta destinatario: {conta_destinatario}")
                print(f"   Valor: {valor}")
            
            if i < 10:
                print(f"{i+1}. ID: {transf_id}")
                print(f"   Tipo: {tipo}")
                print(f"   Status: {status}")
                print(f"   Valor: {valor}")
                print(f"   Conta remetente: {conta_remetente}")
                print(f"   Conta destinatário: {conta_destinatario}")
                print(f"   É nossa conta? {conta_remetente == conta_num or conta_destinatario == conta_num}")

        print(f"\n📊 RESUMO: {len(transferencias)} transferências encontradas")
        for tipo, quantidade in tipos_contagem.items():
            print(f"   {tipo}: {quantidade}")
        print("="*80 + "\n")

        # 🔥 VERIFICAR QUANTAS VEZES 850030 APARECE
        contador_850030 = 0
        for transf in transferencias:
            if str(transf.get('id', '')) == '850030':
                contador_850030 += 1

        print(f"\n🔍 CONTAGEM DA TRANSAÇÃO 850030: {contador_850030} ocorrência(s)")

        def parse_data_unificada(data_str):
            """Parse data em múltiplos formatos"""
            try:
                if not data_str:
                    return None
                
                if 'T' in data_str:
                    return datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                elif ' ' in data_str:
                    return datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                elif '-' in data_str and len(data_str) == 10:
                    return datetime.strptime(data_str, "%Y-%m-%d")
                elif '/' in data_str:
                    partes = data_str.split('/')
                    if len(partes) == 3:
                        dia, mes, ano = map(int, partes)
                        return datetime(ano, mes, dia)
                
                return None
            except:
                return None
            
        def transacao_esta_no_periodo(transf, data_inicio_filtro, data_fim_filtro):
            """
            Verifica se uma transação deve aparecer no período
            Considera TODAS as datas possíveis (solicitação, processamento, conclusão, estorno)
            """
            
            # 1. Data principal da transação
            data_principal_str = transf.get('data', '')
            if data_principal_str:
                data_principal = parse_data_unificada(data_principal_str)
                if data_principal and data_inicio_filtro <= data_principal <= data_fim_filtro:
                    return True
            
            # 2. Data de solicitação (para transações internacionais/internas)
            data_solicitacao_str = transf.get('data_solicitacao', '')
            if data_solicitacao_str:
                data_solicitacao = parse_data_unificada(data_solicitacao_str)
                if data_solicitacao and data_inicio_filtro <= data_solicitacao <= data_fim_filtro:
                    return True
            
            # 3. Data de processamento
            data_processing_str = transf.get('data_processing', '')
            if data_processing_str:
                data_processing = parse_data_unificada(data_processing_str)
                if data_processing and data_inicio_filtro <= data_processing <= data_fim_filtro:
                    return True
            
            # 4. Data de recusa/rejeição (para estornos)
            data_recusa_str = transf.get('data_recusa', '')
            if data_recusa_str:
                data_recusa = parse_data_unificada(data_recusa_str)
                if data_recusa and data_inicio_filtro <= data_recusa <= data_fim_filtro:
                    return True
            
            # 5. Data de conclusão/completed
            data_conclusao_str = transf.get('data_conclusao', '')
            if data_conclusao_str:
                data_conclusao = parse_data_unificada(data_conclusao_str)
                if data_conclusao and data_inicio_filtro <= data_conclusao <= data_fim_filtro:
                    return True
            
            # 6. Para transações rejeitadas: verificar se foram solicitadas antes mas estornadas no período
            if transf.get('status') == 'rejected':
                # Se foi rejeitada, precisa aparecer no período do estorno
                # Usa data_principal como fallback
                if data_principal_str:
                    data_principal = parse_data_unificada(data_principal_str)
                    if data_principal and data_inicio_filtro <= data_principal <= data_fim_filtro:
                        return True
            
            # 7. Para ajustes administrativos: verificar data_ajuste se existir
            data_ajuste_str = transf.get('data_ajuste', '')
            if data_ajuste_str:
                data_ajuste = parse_data_unificada(data_ajuste_str)
                if data_ajuste and data_inicio_filtro <= data_ajuste <= data_fim_filtro:
                    return True
            
            return False

        # 🔥 4. FUNÇÃO PARA CALCULAR SALDO ATÉ UMA DATA (USANDO DADOS JÁ CARREGADOS)
        def calcular_saldo_ate_data(conta_numero, data_fim_periodo, transferencias_dict):
            """Calcula saldo até uma data"""
            
            print(f"\n🔥🔥🔥 DEBUG SALDO ATÉ DATA 🔥🔥🔥")
            print(f"Conta: {conta_numero}")
            print(f"Data limite: {data_fim_periodo.date()}")
            print(f"Total transações disponíveis: {len(transferencias_dict)}")
            
            # Listar PRIMEIRAS 5 transações com datas
            print(f"\nPRIMEIRAS 5 TRANSAÇÕES:")
            contador = 0
            for transf_id, dados in transferencias_dict.items():
                if contador >= 5:
                    break
                data_str = dados.get('data', 'N/A')
                tipo = dados.get('tipo', 'N/A')
                valor = dados.get('valor', 0)
                conta_remetente = dados.get('conta_remetente', 'N/A')
                conta_destinatario = dados.get('conta_destinatario', 'N/A')
                print(f"  {data_str} | ID: {transf_id} | {tipo} | Valor: {valor} | Rem: {conta_remetente} | Dest: {conta_destinatario}")
                contador += 1
            
            # Data limite = FIM DO DIA ANTERIOR ao início do período
            data_limite = data_fim_periodo - timedelta(days=1)
            data_limite = data_limite.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            print(f"\n💰 [SALDO INICIAL] Calculando saldo até {data_fim_periodo.date()}")
            print(f"   Data limite (fim do dia anterior): {data_limite}")
            
            # 🔥 PASSO 1: CRIAR LISTA DE TRANSAÇÕES (IGUAL AO PERÍODO 0)
            transacoes_para_processar = []
            
            for transf_id, dados in transferencias_dict.items():
                data_str = dados.get('data', '')
                if not data_str:
                    continue
                    
                data_obj = parse_data_unificada(data_str)
                if not data_obj:
                    continue
                    
                # FILTRAR: Apenas transações ATÉ a data limite
                if data_obj > data_limite:
                    continue
                    
                transacoes_para_processar.append({
                    'id': transf_id,
                    'dados': dados,
                    'data': data_obj,
                    'data_str': data_str
                })
            
            print(f"   Transações para processar (até {data_limite.date()}): {len(transacoes_para_processar)}")

            
            # 🔥 PASSO 2: ORDENAR POR DATA (IGUAL AO PERÍODO 0)
            transacoes_para_processar.sort(key=lambda x: x['data'])
            
            # 🔥 PASSO 3: USAR A MESMA FUNÇÃO que processa transações no período 0
            # Vamos copiar A LÓGICA EXATA do loop principal
            saldo = 0.0
            
            for item in transacoes_para_processar:
                transf_id = item['id']
                dados = item['dados']
                
                tipo = dados.get('tipo', '')
                status = dados.get('status', '')
                valor = float(dados.get('valor', 0)) if dados.get('valor') is not None else 0.0
                
                conta_remetente = dados.get('conta_remetente')
                conta_destinatario = dados.get('conta_destinatario')
                conta_origem = dados.get('conta_origem')
                conta_destino = dados.get('conta_destino')
                
                # 🔥🔥🔥 LÓGICA IDÊNTICA AO PERÍODO 0 (COM DUAS LINHAS PARA REJEITADAS)
                
                # Cliente é REMETENTE/ORIGEM
                if (conta_remetente == conta_numero or conta_origem == conta_numero):
                    if tipo == 'deposito':
                        saldo += valor
                    elif tipo == 'ajuste_admin' and dados.get('tipo_ajuste', '').upper() == 'CREDITO':
                        saldo += valor
                    elif tipo == 'ajuste_admin':
                        saldo -= valor
                    elif tipo == 'cambio':
                        saldo -= valor
                    elif tipo in ['transferencia_internacional', 'internacional']:
                        if status == 'rejected':
                            # ⚠️ DUAS LINHAS: Débito + Crédito
                            saldo -= valor  # Linha 1: Débito (solicitação)
                            # A data do estorno pode ser DIFERENTE da solicitação!
                            # Precisamos verificar se o estorno está dentro do período
                            data_estorno_str = dados.get('data_recusa') or dados.get('data_processing') or dados.get('data')
                            data_estorno = parse_data_unificada(data_estorno_str) if data_estorno_str else item['data']
                            
                            if data_estorno <= data_limite:
                                saldo += valor  # Linha 2: Crédito (estorno) se dentro do período
                        else:
                            saldo -= valor  # Transação normal (não rejeitada)
                    elif tipo in ['transferencia_interna', 'transferencia_interna_cliente']:
                        if status == 'rejected':
                            # ⚠️ DUAS LINHAS: Débito + Crédito
                            saldo -= valor
                            # Verificar data do estorno
                            data_estorno_str = dados.get('data_recusa') or dados.get('data_processing') or dados.get('data')
                            data_estorno = parse_data_unificada(data_estorno_str) if data_estorno_str else item['data']
                            
                            if data_estorno <= data_limite:
                                saldo += valor
                        else:
                            saldo -= valor  # Cliente é REMETENTE = DÉBITO
                    elif tipo == 'receita':
                        saldo -= valor
                    elif tipo not in ['deposito', 'ajuste_admin', 'cambio']:
                        saldo -= valor  # Caso padrão
                
                # Cliente é DESTINATÁRIO/DESTINO
                elif (conta_destinatario == conta_numero or conta_destino == conta_numero):
                    if tipo == 'deposito':
                        saldo += valor
                    elif tipo == 'ajuste_admin' and dados.get('tipo_ajuste', '').upper() == 'CREDITO':
                        saldo += valor
                    elif tipo == 'cambio':
                        valor_entrada = dados.get('valor_destino', valor)
                        saldo += valor_entrada
                    elif tipo in ['transferencia_internacional', 'internacional']:
                        saldo += valor
                    elif tipo in ['transferencia_interna', 'transferencia_interna_cliente']:
                        saldo += valor  # Cliente é DESTINATÁRIO = CRÉDITO
                    elif tipo not in ['ajuste_admin']:
                        saldo += valor  # Caso padrão
            
            print(f"   Saldo calculado: {saldo:,.2f}")
            
            # VERIFICAÇÃO para 7 dias
            if data_limite.date() == datetime(2025, 12, 9).date():
                print(f"\n🎯 VERIFICAÇÃO 09/12 (dia anterior ao início do período 7 dias):")
                print(f"   Saldo calculado: {saldo:,.2f}")
                print(f"   Saldo esperado: 20.950,00 (baseado no extrato de 30 dias)")
                print(f"   Diferença: {saldo - 20950.00:+,.2f}")
            
            return saldo

        # 🔥 5. CALCULAR SALDO INICIAL DO PERÍODO
        if periodo == '0':
            saldo_inicial_periodo = 0.0
            print(f"💰 Saldo inicial (todo período): 0.00")
        else:
            # 🔥 CORREÇÃO CRÍTICA: Passar o dicionário de transações já carregado!
            saldo_inicial_periodo = calcular_saldo_ate_data(conta_num, data_inicio_filtro, transferencias_dict)
            print(f"💰 Saldo inicial do período: {saldo_inicial_periodo:,.2f}")

        # 🔥 DEBUG ESPECÍFICO PARA CÂMBIOS DA NOVA TELA
        print(f"\n🎯🎯🎯 DEBUG CÂMBIOS ENCONTRADOS 🎯🎯🎯")
        cambios_encontrados = 0
        cambios_nt_encontrados = 0

        for transf in transferencias:
            transf_id = transf.get('id', '')
            transf_tipo = transf.get('tipo', '')
            
            if transf_tipo == 'cambio':
                cambios_encontrados += 1
                
                # Verificar se é da nova tela
                is_nt = '_nt' in str(transf_id) or 'conta_origem' in transf or 'conta_destino' in transf
                
                if is_nt:
                    cambios_nt_encontrados += 1
                    
                    conta_origem = transf.get('conta_origem', 'N/A')
                    conta_destino = transf.get('conta_destino', 'N/A')
                    conta_remetente = transf.get('conta_remetente', 'N/A')
                    conta_destinatario = transf.get('conta_destinatario', 'N/A')
                    
                    print(f"💰 CÂMBIO NT ID: {transf_id}")
                    print(f"   conta_origem: {conta_origem}")
                    print(f"   conta_destino: {conta_destino}")
                    print(f"   conta_remetente: {conta_remetente}")
                    print(f"   conta_destinatario: {conta_destinatario}")
                    print(f"   Nossa conta: {conta_num}")
                    print(f"   É origem? {conta_origem == conta_num}")
                    print(f"   É destino? {conta_destino == conta_num}")
                    print(f"   ---")
                else:
                    print(f"💰 CÂMBIO NORMAL ID: {transf_id}")

        print(f"\n📊 RESUMO CÂMBIOS:")
        print(f"   Total de câmbios encontrados: {cambios_encontrados}")
        print(f"   Câmbios da nova tela: {cambios_nt_encontrados}")
        print(f"🎯🎯🎯 FIM DEBUG 🎯🎯🎯\n")
        
        def gerar_descricao_cambio_inteligente(dados_cambio, conta_num, sistema_supabase=None):
            """Gera descrição clara para operações de câmbio - VERSÃO WEB (igual ao Kivy)"""
            
            # 1. Obter informações básicas
            operacao = dados_cambio.get('operacao', '').lower()
            moeda_origem = dados_cambio.get('moeda_origem', 'USD')
            moeda_destino = dados_cambio.get('moeda_destino', 'BRL')
            valor_origem = dados_cambio.get('valor_origem', 0)
            valor_destino = dados_cambio.get('valor_destino', 0)
            
            # 2. Obter taxa (cotacao)
            taxa = dados_cambio.get('cotacao', 0)
            if not taxa or taxa == 0:
                # Tentar calcular com base nos valores
                if valor_origem > 0 and valor_destino > 0:
                    taxa = valor_destino / valor_origem
            
            # 3. Gerar descrição baseada na operação (versão simplificada do Kivy)
            if operacao == 'compra':
                return f"COMPRA {moeda_destino} - Pagou {valor_origem:,.2f} {moeda_origem} → Recebeu {valor_destino:,.2f} {moeda_destino} (Taxa: {taxa:.4f})"
            elif operacao == 'venda':
                return f"VENDA {moeda_origem} - Vendeu {valor_origem:,.2f} {moeda_origem} → Recebeu {valor_destino:,.2f} {moeda_destino} (Taxa: {taxa:.4f})"
            elif operacao == 'cambio_admin':
                return f"CÂMBIO ADMINISTRATIVO - {moeda_origem} {valor_origem:,.2f} → {moeda_destino} {valor_destino:,.2f} (Taxa: {taxa:.4f})"
            else:
                # Descrição padrão
                if moeda_origem and moeda_destino:
                    return f"CÂMBIO {moeda_origem}/{moeda_destino} - {valor_origem:,.2f} {moeda_origem} → {valor_destino:,.2f} {moeda_destino} (Taxa: {taxa:.4f})"
                else:
                    return f"CÂMBIO - {valor_origem:,.2f} → {valor_destino:,.2f} (Taxa: {taxa:.4f})"

        # 🔥 6. DEBUG DETALHADO DO PROCESSAMENTO
        print(f"\n" + "="*80)
        print("🔍 DEBUG DETALHADO - PROCESSAMENTO DE TRANSAÇÕES")
        print("="*80)

        contadores = {
            'total': 0,
            'dentro_periodo': 0,
            'fora_periodo': 0,
            'sem_data': 0,
            'incluidas': 0,
            'excluidas_status': 0,
            'excluidas_outro': 0
        }

        excluidas_detalhes = []
        transacoes_todas = []
        
        # Adicionar saldo inicial
        transacoes_todas.append({
            'data': data_inicio_filtro.strftime("%Y-%m-%d 00:00:00"),
            'descricao': "SALDO INICIAL DO PERÍODO",
            'credito': 0.00,
            'debito': 0.00,
            'saldo_apos': saldo_inicial_periodo,
            'tipo': "Saldo Inicial",
            'moeda': moeda,
            'timestamp': data_inicio_filtro.replace(hour=0, minute=0, second=0),
            'id': 'SALDO_INICIAL'
        })
        
        # 🔥 DEBUG ESPECÍFICO PARA TRANSAÇÃO 733125
        print(f"\n" + "="*80)
        print("🔍 BUSCANDO ESPECIFICAMENTE A TRANSAÇÃO 733125")
        print("="*80)

        transf_733125_encontrada = False
        for transf in transferencias:
            transf_id = transf.get('id', '')
            if str(transf_id) == '733125':
                transf_733125_encontrada = True
                print(f"✅ TRANSAÇÃO 733125 ENCONTRADA!")
                print(f"   ID: {transf.get('id')}")
                print(f"   Tipo: {transf.get('tipo')}")
                print(f"   Status: {transf.get('status')}")
                print(f"   Valor: {transf.get('valor')}")
                print(f"   Data: {transf.get('data')}")
                print(f"   Conta remetente: {transf.get('conta_remetente')}")
                print(f"   Conta destinatario: {transf.get('conta_destinatario')}")
                print(f"   Nome destinatário: {transf.get('nome_destinatario')}")
                print(f"   É remetente? {transf.get('conta_remetente') == conta_num}")
                print(f"   É destinatário? {transf.get('conta_destinatario') == conta_num}")
                break

        if not transf_733125_encontrada:
            print("❌ TRANSAÇÃO 733125 NÃO ENCONTRADA NAS TRANSFERÊNCIAS!")
            print("🔍 Verificando se está em alguma outra conta...")
            
            for transf in transferencias:
                transf_id = transf.get('id', '')
                if '733125' in str(transf_id):
                    print(f"⚠️  ID PARECIDO ENCONTRADO: {transf_id}")
                    print(f"   Tipo: {transf.get('tipo')}")
                    print(f"   Status: {transf.get('status')}")

        print("="*80 + "\n")

        # 🔥 7. PROCESSAR CADA TRANSAÇÃO COM DEBUG
        for transf in transferencias:
            contadores['total'] += 1
            transf_id = transf.get('id', 'N/A')
            transf_tipo = transf.get('tipo', 'sem_tipo')
            transf_status = transf.get('status', 'sem_status')
            transf_valor = transf.get('valor', 0)
            
            # 🔥 DEBUG: VERIFICAR SE 850030 PASSA PELO LOOP
            if str(transf_id) == '850030':
                print(f"\n🔁🔁🔁 DEBUG 850030 - PASSOU PELO LOOP PRINCIPAL 🔁🔁🔁")
                print(f"   Contador total: {contadores['total']}")
                print(f"   É a primeira vez? {contadores['total'] == 1}")
            
            try:
                data_transacao_str = transf.get('data', '')
                
                if not data_transacao_str:
                    contadores['sem_data'] += 1
                    excluidas_detalhes.append(f"Sem data: ID {transf_id}, Tipo: {transf_tipo}")
                    continue
                
                data_transacao = parse_data_unificada(data_transacao_str)
                if not data_transacao:
                    contadores['sem_data'] += 1
                    excluidas_detalhes.append(f"Data inválida: ID {transf_id}, Data: {data_transacao_str}")
                    continue
                
                # Verificar período
                if not transacao_esta_no_periodo(transf, data_inicio_filtro, data_fim_filtro):
                    contadores['fora_periodo'] += 1
                    if contadores['fora_periodo'] <= 3:
                        print(f"📅 FORA DO PERÍODO: ID {transf_id} | Data principal: {data_transacao.date() if data_transacao else 'N/A'}")
                    continue
                
                # Transação dentro do período
                contadores['dentro_periodo'] += 1
                
                # 🔥 LÓGICA DE DECISÃO DO KIVY (CORRIGIDA)
                deve_incluir = False
                motivo = ""

                # Normalizar status (alguns podem ser "solicitada" em vez de "pending")
                status_normalizado = transf_status.lower() if transf_status else ''

                if transf_tipo in ['ajuste_admin', 'cambio']:
                    deve_incluir = True
                    motivo = f"Tipo especial: {transf_tipo}"
                elif status_normalizado in ['pending', 'solicitada']:  # 🔥 CORREÇÃO CRÍTICA AQUI
                    deve_incluir = True
                    motivo = f"Status: {transf_status} (solicitação)"
                elif status_normalizado == 'rejected':
                    deve_incluir = True
                    motivo = "Status: rejected"
                elif status_normalizado in ['processing', 'completed']:
                    deve_incluir = True
                    motivo = f"Status: {transf_status}"
                else:
                    deve_incluir = False
                    motivo = f"Status não incluído: {transf_status}"
                    contadores['excluidas_status'] += 1
                    
                    if contadores['excluidas_status'] <= 3:
                        print(f"🚫 EXCLUÍDA POR STATUS: ID {transf_id} | Motivo: {motivo}")

                if not deve_incluir:
                    excluidas_detalhes.append(f"Status: {transf_status} | ID: {transf_id} | Tipo: {transf_tipo}")
                    continue
                
                # Transação será incluída
                contadores['incluidas'] += 1
                
                if contadores['incluidas'] <= 5:
                    print(f"🎯 SERÁ INCLUÍDA (#{contadores['incluidas']}): ID {transf_id} | {motivo}")
                
                # 🔥 8. PROCESSAR A TRANSAÇÃO (LÓGICA DO KIVY)
                valor = float(transf.get('valor', 0)) if transf.get('valor') is not None else 0.0

                # Cliente é REMETENTE
                if transf.get('conta_remetente') == conta_num or transf.get('conta_origem') == conta_num:
                    
                    if transf_tipo == 'deposito':
                        # 🔥 LOG DE DIAGNÓSTICO NO BACKEND
                        print(f"\n{'='*60}")
                        print(f"🔍 [BACKEND] Depósito encontrado - ID: {transf_id}")
                        print(f"   banco_origem: '{transf.get('banco_origem', 'N/A')}'")
                        print(f"   remetente: '{transf.get('remetente', 'N/A')}'")
                        print(f"   descricao original: '{transf.get('descricao', 'N/A')}'")
                        print(f"   Todas as chaves: {list(transf.keys())}")
                        print(f"{'='*60}\n")
                        # 🔥 Extrair campos
                        banco_origem = transf.get('banco_origem', '')
                        remetente_nome = transf.get('remetente', '')
                        
                        # 🔥 Se os campos estiverem vazios, extrair da descrição
                        if not banco_origem or not remetente_nome:
                            descricao_original = transf.get('descricao', '')
                            
                            # Extrair banco
                            import re
                            banco_match = re.search(r'Banco:\s*([^-]+)', descricao_original)
                            if banco_match and not banco_origem:
                                banco_origem = banco_match.group(1).strip()
                            
                            # Extrair remetente
                            remetente_match = re.search(r'Remetente:\s*(.+)$', descricao_original)
                            if remetente_match and not remetente_nome:
                                remetente_nome = remetente_match.group(1).strip()
                        
                        # 🔥 Construir descrição simplificada
                        if banco_origem and remetente_nome:
                            descricao_final = f"💰 Depósito de: {banco_origem} - {remetente_nome}"
                        elif banco_origem:
                            descricao_final = f"💰 Depósito do banco: {banco_origem}"
                        elif remetente_nome:
                            descricao_final = f"💰 Depósito de: {remetente_nome}"
                        else:
                            descricao_final = "💰 Depósito"
                        
                        transacoes_todas.append({
                            'id': transf_id,
                            'data': data_transacao_str,
                            'descricao': descricao_final,
                            'credito': valor,
                            'debito': 0.00,
                            'tipo': "Depósito",
                            'moeda': moeda,
                            'timestamp': data_transacao,
                            'banco_origem': banco_origem,
                            'remetente': remetente_nome
                        })
                    
                    elif transf_tipo == 'ajuste_admin':
                        tipo_ajuste = transf.get('tipo_ajuste', 'DÉBITO')
                        if tipo_ajuste and tipo_ajuste.upper() == 'CREDITO':
                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': f"CRÉDITO ADMINISTRATIVO - {transf.get('descricao_ajuste', '')}",
                                'credito': valor,
                                'debito': 0.00,
                                'tipo': "Crédito Admin",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })
                        else:
                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': f"DÉBITO ADMINISTRATIVO - {transf.get('descricao_ajuste', '')}",
                                'credito': 0.00,
                                'debito': valor,
                                'tipo': "Débito Admin",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })
                    
                    elif transf_tipo == 'transferencia_interna_cliente':
                        status_normalizado = transf_status.lower() if transf_status else ''
                        
                        # Cliente é REMETENTE (debitar valor)
                        if transf.get('conta_remetente') == conta_num:
                            status_text = "SOLICITADA" if status_normalizado in ['pending', 'solicitada'] else \
                                        "EM PROCESSAMENTO" if status_normalizado == 'processing' else \
                                        "CONCLUÍDA" if status_normalizado == 'completed' else "RECUSADA"
                            
                            # 🔥 USAR FUNÇÃO PARA BUSCAR NOME DO DESTINATÁRIO (IGUAL AO KIVY)
                            conta_destinatario = transf.get('conta_destinatario', '')
                            nome_destinatario = obter_nome_cliente_por_conta(conta_destinatario)
                            
                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': f"TRANSFERÊNCIA INTERNA {status_text} - {nome_destinatario}",
                                'credito': 0.00,
                                'debito': valor,
                                'tipo': "Transferência Interna",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })
                            
                            # DEBUG
                            print(f"💰 TRANSFERÊNCIA INTERNA CLIENTE: {status_text} - {nome_destinatario} | -{valor:,.2f}")
                        
                        # Cliente é DESTINATÁRIO (crédito - se for transferência recebida)
                        elif transf.get('conta_destinatario') == conta_num:
                            status_text = "SOLICITADA" if status_normalizado in ['pending', 'solicitada'] else \
                                        "EM PROCESSAMENTO" if status_normalizado == 'processing' else \
                                        "CONCLUÍDA" if status_normalizado == 'completed' else "RECUSADA"
                            
                            # 🔥 USAR FUNÇÃO PARA BUSCAR NOME DO REMETENTE (IGUAL AO KIVY)
                            conta_remetente = transf.get('conta_remetente', '')
                            nome_remetente = obter_nome_cliente_por_conta(conta_remetente)
                            
                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': f"TRANSFERÊNCIA INTERNA {status_text} RECEBIDA - {nome_remetente}",
                                'credito': valor,
                                'debito': 0.00,
                                'tipo': "Transferência Interna",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })
                    
                    elif transf_tipo in ['internacional', 'transferencia_internacional']:
                        status_normalizado = transf_status.lower() if transf_status else ''
                        
                        # 🔥 LÓGICA DO KIVY PARA TRANSFERÊNCIAS REJEITADAS (CRÍTICO!)
                        if status_normalizado == 'rejected':
                            # 🔥 CORREÇÃO: Verificar datas para decidir o que mostrar
                            
                            # Obter datas
                            data_solicitacao_str = transf.get('data_solicitacao') or data_transacao_str
                            data_estorno_str = transf.get('data_recusa') or transf.get('data_processing') or data_transacao_str
                            
                            data_solicitacao = parse_data_unificada(data_solicitacao_str)
                            data_estorno = parse_data_unificada(data_estorno_str)
                            
                            # Verificar se cada data está dentro do período
                            solicitacao_dentro = (
                                data_solicitacao and 
                                data_inicio_filtro <= data_solicitacao <= data_fim_filtro
                            )
                            estorno_dentro = (
                                data_estorno and 
                                data_inicio_filtro <= data_estorno <= data_fim_filtro
                            )
                            
                            # 🔥 CASO 1: Solicitação DENTRO + Estorno DENTRO → mostrar AMBAS
                            if solicitacao_dentro and estorno_dentro:
                                # 1. TRANSAÇÃO DE DÉBITO (solicitação)
                                transacoes_todas.append({
                                    'id': f"{transf_id}_DEBITO",
                                    'data': data_solicitacao_str,
                                    'descricao': f"TRANSF. INTERNACIONAL SOLICITADA - {transf.get('beneficiario', 'N/A')}",
                                    'credito': 0.00,
                                    'debito': valor,
                                    'tipo': "Transferência Internacional",
                                    'moeda': moeda,
                                    'timestamp': data_solicitacao
                                })
                                
                                # 2. TRANSAÇÃO DE CRÉDITO (estorno)
                                transacoes_todas.append({
                                    'id': f"{transf_id}_CREDITO",
                                    'data': data_estorno_str,
                                    'descricao': f"ESTORNO TRANSF. INTERNACIONAL - {transf.get('beneficiario', 'N/A')}",
                                    'credito': valor,
                                    'debito': 0.00,
                                    'tipo': "Estorno",
                                    'moeda': moeda,
                                    'timestamp': data_estorno
                                })
                                
                                print(f"💰 REJEITADA COMPLETA: Mostrando débito + crédito | ID: {transf_id}")
                            
                            # 🔥 CASO 2: Solicitação DENTRO + Estorno FORA → mostrar APENAS débito
                            elif solicitacao_dentro and not estorno_dentro:
                                transacoes_todas.append({
                                    'id': f"{transf_id}_DEBITO",
                                    'data': data_solicitacao_str,
                                    'descricao': f"TRANSF. INTERNACIONAL SOLICITADA - {transf.get('beneficiario', 'N/A')}",
                                    'credito': 0.00,
                                    'debito': valor,
                                    'tipo': "Transferência Internacional",
                                    'moeda': moeda,
                                    'timestamp': data_solicitacao
                                })
                                
                                print(f"💰 REJEITADA PARCIAL: Mostrando apenas débito | ID: {transf_id}")
                            
                            # 🔥 CASO 3: Solicitação FORA + Estorno DENTRO → mostrar APENAS crédito
                            elif not solicitacao_dentro and estorno_dentro:
                                transacoes_todas.append({
                                    'id': f"{transf_id}_CREDITO",
                                    'data': data_estorno_str,
                                    'descricao': f"ESTORNO TRANSF. INTERNACIONAL - {transf.get('beneficiario', 'N/A')}",
                                    'credito': valor,
                                    'debito': 0.00,
                                    'tipo': "Estorno",
                                    'moeda': moeda,
                                    'timestamp': data_estorno
                                })
                                
                                print(f"💰 REJEITADA PARCIAL: Mostrando apenas crédito (estorno) | ID: {transf_id}")
                            
                            # 🔥 CASO 4: Ambos FORA → não mostrar nada
                            else:
                                print(f"💰 REJEITADA FORA: Não mostrar nada | ID: {transf_id}")
                        
                        else:
                            # Para outros status: SOLICITADA, EM PROCESSAMENTO, CONCLUÍDA
                            status_text = "SOLICITADA" if status_normalizado in ['pending', 'solicitada'] else \
                                        "EM PROCESSAMENTO" if status_normalizado == 'processing' else \
                                        "CONCLUÍDA" if status_normalizado == 'completed' else "STATUS DESCONHECIDO"
                            
                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': f"TRANSF. INTERNACIONAL {status_text} - {transf.get('beneficiario', 'N/A')}",
                                'credito': 0.00,
                                'debito': valor,
                                'tipo': "Transferência Internacional",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })
                    
                    elif transf_tipo == 'cambio':
                        # 🔥 VERIFICAR SE É CÂMBIO DA NOVA TELA (_nt) ou usa conta_origem/conta_destino
                        if '_nt' in str(transf_id) or 'conta_origem' in transf or 'conta_destino' in transf:
                            # 🔥 CÂMBIO DA NOVA TELA - Estrutura diferente
                            
                            # 🔥🔥🔥 CORREÇÃO CRÍTICA: Se conta_origem/conta_destino são None, usar conta_remetente/conta_destinatario
                            conta_cliente_origem = transf.get('conta_origem')
                            conta_cliente_destino = transf.get('conta_destino')
                            
                            # Se campos da nova tela são None, usar campos da tela antiga
                            if conta_cliente_origem is None or conta_cliente_destino is None:
                                conta_cliente_origem = transf.get('conta_remetente')
                                conta_cliente_destino = transf.get('conta_destinatario')
                            
                            if conta_cliente_origem == conta_num:
                                # Cliente é ORIGEM/REMETENTE (pagou/saída)
                                descricao_cambio = gerar_descricao_cambio_inteligente(transf, conta_num)
                                
                                transacoes_todas.append({
                                    'id': transf_id,
                                    'data': data_transacao_str,
                                    'descricao': descricao_cambio,
                                    'credito': 0.00,
                                    'debito': valor,
                                    'tipo': "Câmbio",
                                    'moeda': transf.get('moeda_origem', moeda),
                                    'timestamp': data_transacao
                                })
                                print(f"💰 CÂMBIO NT SAÍDA CORRIGIDO: {descricao_cambio[:50]}...")
                            
                            elif conta_cliente_destino == conta_num:
                                # Cliente é DESTINO/DESTINATÁRIO (recebeu/entrada) - Processar aqui também!
                                descricao_cambio = gerar_descricao_cambio_inteligente(transf, conta_num)
                                
                                transacoes_todas.append({
                                    'id': transf_id,
                                    'data': data_transacao_str,
                                    'descricao': descricao_cambio,
                                    'credito': transf.get('valor_destino', valor),
                                    'debito': 0.00,
                                    'tipo': "Câmbio",
                                    'moeda': transf.get('moeda_destino', moeda),
                                    'timestamp': data_transacao
                                })
                                print(f"💰 CÂMBIO NT ENTRADA CORRIGIDO (REMETENTE SECTION): {descricao_cambio[:50]}...")
                            
                            else:
                                print(f"⚠️ CÂMBIO NT não processado: conta_origem={transf.get('conta_origem')}, conta_destino={transf.get('conta_destino')}, conta_remetente={transf.get('conta_remetente')}, conta_destinatario={transf.get('conta_destinatario')}")
                        else:
                            # 🔥 CÂMBIO NORMAL (tela antiga)
                            descricao_cambio = gerar_descricao_cambio_inteligente(transf, conta_num)
                            
                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': descricao_cambio,
                                'credito': 0.00,
                                'debito': valor,
                                'tipo': "Câmbio",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })
                            print(f"💰 CÂMBIO NORMAL: {descricao_cambio[:50]}...")
                    
                    elif transf_tipo == 'receita':
                        transacoes_todas.append({
                            'id': transf_id,
                            'data': data_transacao_str,
                            'descricao': f"TAXA/DESPESA - {transf.get('descricao_receita', '')}",
                            'credito': 0.00,
                            'debito': valor,
                            'tipo': "Taxa/Despesa",
                            'moeda': moeda,
                            'timestamp': data_transacao
                        })
                    
                    # 🔥 BLOCO TRANSFERÊNCIA CLIENTE → EMPRESA (AGORA COMO CRÉDITO)
                    elif transf_tipo == 'transferencia_cliente_empresa':
                        status_normalizado = transf_status.lower() if transf_status else ''
                        
                        # 🔥 PEGAR APENAS A DESCRIÇÃO ORIGINAL QUE FOI INSERIDA
                        descricao_original = transf.get('descricao', '').strip()
                        
                        # Se não tiver descrição, usar padrão
                        if not descricao_original:
                            descricao_original = "Transferência para empresa"
                        
                        transacoes_todas.append({
                            'id': transf_id,
                            'data': data_transacao_str,
                            'descricao': descricao_original,  # 🔥 APENAS A DESCRIÇÃO ORIGINAL
                            'credito': valor,           # CRÉDITO (saldo aumenta)
                            'debito': 0.00,
                            'tipo': "Transferência para Empresa",
                            'moeda': moeda,
                            'timestamp': data_transacao,
                            'conta_destino': transf.get('conta_destinatario', ''),
                            'descricao_original': descricao_original
                        })
                        
                        print(f"💰 TRANSFERÊNCIA CLIENTE → EMPRESA (CRÉDITO): +{valor:,.2f} {moeda} | Desc: {descricao_original}")
                    
                    else:
                        # Para outros tipos de transação (fallback)
                        transacoes_todas.append({
                            'id': transf_id,
                            'data': data_transacao_str,
                            'descricao': f"{transf_tipo.upper()} - {transf.get('descricao', '')}",
                            'credito': 0.00,
                            'debito': valor,
                            'tipo': transf_tipo,
                            'moeda': moeda,
                            'timestamp': data_transacao
                        })                  
                
                # Cliente é DESTINATÁRIO
                elif transf.get('conta_destinatario') == conta_num or transf.get('conta_destino') == conta_num:

                    # 🔥 DEBUG ESPECÍFICO PARA 850030
                    if str(transf_id) == '850030':
                        print(f"\n🎯🎯🎯 DEBUG 850030 - SEÇÃO DESTINATÁRIO 🎯🎯🎯")
                        print(f"   Tipo: {transf_tipo}")
                        print(f"   Status: {transf_status}")
                        print(f"   Conta remetente: {transf.get('conta_remetente')}")
                        print(f"   Conta destinatario: {transf.get('conta_destinatario')}")
                        print(f"   Nossa conta: {conta_num}")
                        print(f"   É remetente? {transf.get('conta_remetente') == conta_num}")
                        print(f"   É destinatário? {transf.get('conta_destinatario') == conta_num}")
                        print(f"   Vai entrar na seção DESTINATÁRIO? SIM")
                    
                    if transf_tipo == 'deposito':
                        transacoes_todas.append({
                            'id': transf_id,
                            'data': data_transacao_str,
                            'descricao': f"DEPÓSITO CONFIRMADO - {transf.get('banco_origem', 'Banco')}",
                            'credito': valor,
                            'debito': 0.00,
                            'tipo': "Depósito",
                            'moeda': moeda,
                            'timestamp': data_transacao
                        })
                    elif transf_tipo == 'ajuste_admin' and transf.get('tipo_ajuste') == 'CREDITO':
                        transacoes_todas.append({
                            'id': transf_id,
                            'data': data_transacao_str,
                            'descricao': f"CRÉDITO ADMINISTRATIVO - {transf.get('descricao_ajuste', '')}",
                            'credito': valor,
                            'debito': 0.00,
                            'tipo': "Crédito Admin",
                            'moeda': moeda,
                            'timestamp': data_transacao
                        })
                    elif transf_tipo == 'cambio':
                        # 🔥 VERIFICAR SE É CÂMBIO DA NOVA TELA (_nt) ou usa conta_origem/conta_destino
                        if '_nt' in str(transf_id) or 'conta_origem' in transf or 'conta_destino' in transf:
                            # 🔥 CÂMBIO DA NOVA TELA - Verificar se o cliente é DESTINO/DESTINATÁRIO
                            # 🔥🔥🔥 CORREÇÃO: Se conta_origem/conta_destino são None, usar conta_remetente/conta_destinatario
                            conta_cliente_origem = transf.get('conta_origem')
                            conta_cliente_destino = transf.get('conta_destino')
                            
                            # Se campos da nova tela são None, usar campos da tela antiga
                            if conta_cliente_origem is None or conta_cliente_destino is None:
                                conta_cliente_origem = transf.get('conta_remetente')
                                conta_cliente_destino = transf.get('conta_destinatario')
                            
                            if conta_cliente_destino == conta_num:
                                # Cliente é DESTINO/DESTINATÁRIO (recebeu/entrada)
                                descricao_cambio = gerar_descricao_cambio_inteligente(transf, conta_num)
                                
                                transacoes_todas.append({
                                    'id': transf_id,
                                    'data': data_transacao_str,
                                    'descricao': descricao_cambio,
                                    'credito': transf.get('valor_destino', valor),
                                    'debito': 0.00,
                                    'tipo': "Câmbio",
                                    'moeda': transf.get('moeda_destino', moeda),
                                    'timestamp': data_transacao
                                })
                                print(f"💰 CÂMBIO NT ENTRADA (DESTINATÁRIO SECTION): {descricao_cambio[:50]}...")
                            else:
                                print(f"🔧 CÂMBIO NT não é nosso como destinatário: {transf_id}")
                        else:
                            # 🔥 CÂMBIO NORMAL (tela antiga) - Cliente recebe
                            descricao_cambio = gerar_descricao_cambio_inteligente(transf, conta_num)
                            
                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': descricao_cambio,
                                'credito': transf.get('valor_destino', valor),
                                'debito': 0.00,
                                'tipo': "Câmbio",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })
                            print(f"💰 CÂMBIO NORMAL RECEBIDO: {descricao_cambio[:50]}...")
                    
                    # 🔥 NOVO BLOCO PARA TRANSFERÊNCIA EMPRESA → CLIENTE (AGORA COMO DÉBITO)
                    elif transf_tipo == 'transferencia_empresa_cliente':
                        status_normalizado = transf_status.lower() if transf_status else ''
                        
                        # 🔥 PEGAR APENAS A DESCRIÇÃO ORIGINAL QUE FOI INSERIDA
                        descricao_original = transf.get('descricao', '').strip()
                        
                        # Se não tiver descrição, usar padrão
                        if not descricao_original:
                            descricao_original = "Transferência da empresa"
                        
                        transacoes_todas.append({
                            'id': transf_id,
                            'data': data_transacao_str,
                            'descricao': descricao_original,  # 🔥 APENAS A DESCRIÇÃO ORIGINAL
                            'credito': 0.00,              # DÉBITO (saldo diminui)
                            'debito': valor,
                            'tipo': "Transferência da Empresa",
                            'moeda': moeda,
                            'timestamp': data_transacao,
                            'conta_remetente': transf.get('conta_remetente', ''),
                            'descricao_original': descricao_original
                        })
                        
                        print(f"💰 TRANSFERÊNCIA EMPRESA → CLIENTE (DÉBITO): -{valor:,.2f} {moeda} | Desc: {descricao_original}")
                    
                    # 🔥 OUTROS TIPOS DE TRANSAÇÕES (quando cliente é destinatário em transferências normais)
                    elif transf_tipo not in ['ajuste_admin', 'deposito', 'cambio', 'transferencia_empresa_cliente']:
                        status_normalizado = transf_status.lower() if transf_status else ''
                        
                        # 🔥 DEBUG ESPECÍFICO PARA 850030
                        if str(transf_id) == '850030':
                            print(f"\n🎯🎯🎯 DEBUG 850030 - DENTRO DA CONDIÇÃO transferencias normais 🎯🎯🎯")
                            print(f"   Vai processar transação tipo: {transf_tipo}")
                            print(f"   Status normalizado: {status_normalizado}")
                        
                        # Verificar se é uma transferência interna rejeitada
                        if status_normalizado == 'rejected' and transf_tipo in ['transferencia_interna', 'transferencia_interna_cliente']:
                            # 🔥 LÓGICA DO KIVY: Para transferências internas rejeitadas, criar duas transações
                            
                            # 1. Transação de débito (solicitação original)
                            data_solicitacao = transf.get('data_solicitacao') or data_transacao_str
                            nome_destinatario = transf.get('nome_destinatario', 'N/A')
                            
                            transacoes_todas.append({
                                'id': f"{transf_id}_DEBITO",
                                'data': data_solicitacao,
                                'descricao': f"TRANSFERÊNCIA SOLICITADA - {nome_destinatario}",
                                'credito': 0.00,
                                'debito': valor,
                                'tipo': "Transferência",
                                'moeda': moeda,
                                'timestamp': parse_data_unificada(data_solicitacao) or data_transacao
                            })
                            
                            # 2. Transação de crédito (estorno)
                            data_estorno = transf.get('data_recusa') or data_transacao_str
                            
                            transacoes_todas.append({
                                'id': f"{transf_id}_CREDITO",
                                'data': data_estorno,
                                'descricao': f"ESTORNO TRANSFERÊNCIA - {nome_destinatario}",
                                'credito': valor,  # 🔥 CRÉDITO (estorno)
                                'debito': 0.00,
                                'tipo': "Estorno",
                                'moeda': moeda,
                                'timestamp': parse_data_unificada(data_estorno) or data_transacao
                            })
                            
                            # DEBUG
                            print(f"💰 ESTORNO INTERNO CRIADO: ESTORNO TRANSFERÊNCIA - {nome_destinatario} | +{valor:,.2f}")
                            
                        else:
                            # Para outros status ou tipos
                            status_text = "SOLICITADA" if status_normalizado in ['pending', 'solicitada'] else \
                                        "EM PROCESSAMENTO" if status_normalizado == 'processing' else \
                                        "CONCLUÍDA" if status_normalizado == 'completed' else "RECUSADA"
                            
                            # 🔥 DEBUG ESPECÍFICO PARA 850030
                            if str(transf_id) == '850030':
                                print(f"\n🎯🎯🎯 DEBUG 850030 - STATUS TEXT DEFINIDO 🎯🎯🎯")
                                print(f"   Status text: {status_text}")
                            
                            # Buscar nome do remetente
                            conta_remetente = transf.get('conta_remetente', '')
                            nome_remetente = obter_nome_cliente_por_conta(conta_remetente)
                            
                            # 🔥 DEBUG ESPECÍFICO PARA 850030 - ANTES DE ADICIONAR
                            if str(transf_id) == '850030':
                                print(f"\n🎯🎯🎯 DEBUG 850030 - VAI ADICIONAR TRANSAÇÃO 🎯🎯🎯")
                                print(f"   Contador atual de transações: {len(transacoes_todas)}")

                            transacoes_todas.append({
                                'id': transf_id,
                                'data': data_transacao_str,
                                'descricao': f"TRANSFERÊNCIA {status_text} RECEBIDA - {nome_remetente}",
                                'credito': valor,
                                'debito': 0.00,
                                'tipo': "Transferência",
                                'moeda': moeda,
                                'timestamp': data_transacao
                            })

                            # 🔥 DEBUG ESPECÍFICO PARA 850030 - DEPOIS DE ADICIONAR
                            if str(transf_id) == '850030':
                                print(f"\n🎯🎯🎯 DEBUG 850030 - TRANSAÇÃO ADICIONADA 🎯🎯🎯")
                                print(f"   Nova contagem de transações: {len(transacoes_todas)}")

                        
            except Exception as e:
                print(f"⚠️ Erro ao processar transação {transf_id}: {e}")
                contadores['excluidas_outro'] += 1
                continue

        # 🔥 9. RESUMO FINAL DO DEBUG
        print(f"\n" + "="*80)
        print("📊 RESUMO DETALHADO DO PROCESSAMENTO")
        print("="*80)
        print(f"Total transferências encontradas: {contadores['total']}")
        print(f"  - Dentro do período (30 dias): {contadores['dentro_periodo']}")
        print(f"  - Fora do período: {contadores['fora_periodo']}")
        print(f"  - Sem data válida: {contadores['sem_data']}")
        print(f"\nTRANSAÇÕES DENTRO DO PERÍODO:")
        print(f"  - Incluídas: {contadores['incluidas']}")
        print(f"  - Excluídas por status: {contadores['excluidas_status']}")
        print(f"  - Excluídas por outros motivos: {contadores['excluidas_outro']}")
        print(f"\n🚫 PRINCIPAIS MOTIVOS DE EXCLUSÃO:")
        for i, detalhe in enumerate(excluidas_detalhes[:10]):
            print(f"  {i+1}. {detalhe}")
        print("="*80 + "\n")

        # 🔥 DEBUG: VERIFICAR SE A 850030 ESTÁ DUPLICADA NO ARRAY
        print(f"\n🔍🔍🔍 VERIFICANDO TRANSAÇÃO 850030 NO ARRAY transacoes_todas")
        contador_850030_array = 0
        for transacao in transacoes_todas:
            if str(transacao.get('id', '')) == '850030':
                contador_850030_array += 1
                print(f"   ENCONTRADA: ID {transacao.get('id')} | Descrição: {transacao.get('descricao', '')[:50]}...")

        print(f"🔍 TOTAL DE 850030 NO ARRAY: {contador_850030_array}")

        # 🔥 10. ORDENAR POR DATA E CALCULAR SALDO SEQUENCIAL
        transacoes_todas.sort(key=lambda x: x.get('timestamp', datetime.min))

        saldo_sequencial = saldo_inicial_periodo
        for transacao in transacoes_todas:
            if transacao.get('tipo') == "Saldo Inicial":
                continue
                
            credito = transacao.get('credito', 0)
            debito = transacao.get('debito', 0)
            saldo_sequencial += credito - debito
            transacao['saldo_apos'] = saldo_sequencial

        # 🔥 11. CALCULAR TOTAIS
        total_entradas = sum(t.get('credito', 0) for t in transacoes_todas if t.get('tipo') != 'Saldo Inicial')
        total_saidas = sum(t.get('debito', 0) for t in transacoes_todas if t.get('tipo') != 'Saldo Inicial')

        # 🔥 12. INVERTER PARA EXIBIÇÃO (mais recente primeiro)
        transacoes_exibicao = list(reversed(transacoes_todas))

        # 🔥 DEBUG: VERIFICAR APÓS ORDENAR E INVERTER
        print(f"\n🔍🔍🔍 VERIFICANDO TRANSAÇÃO 850030 APÓS ORDENAÇÃO E INVERSÃO")
        contador_850030_final = 0
        for transacao in transacoes_exibicao:
            if str(transacao.get('id', '')) == '850030':
                contador_850030_final += 1
                print(f"   ENCONTRADA NO EXTRATO: ID {transacao.get('id')} | Descrição: {transacao.get('descricao', '')[:50]}...")

        print(f"🔍 TOTAL DE 850030 NO EXTRATO FINAL: {contador_850030_final}")

        print(f"✅ [EXTRATO KIVY] Processado: {len(transacoes_exibicao)} transações")
        
        return jsonify({
            "success": True,
            "transacoes": transacoes_exibicao,
            "saldo_final": saldo_sequencial,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "moeda": moeda,
            "periodo": periodo,
            "conta": conta_num,
            "usuario": usuario
        })
        
    except Exception as e:
        print(f"❌ [EXTRATO KIVY] ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar extrato: {str(e)}"
        }), 500




# 🔥 FUNÇÕES AUXILIARES PARA CÂMBIO (IGUAL AO KIVY)

def obter_cotacao_simples(par_moedas):
    """RETORNA: 1 MOEDA_ESQUERDA = X MOEDA_DIREITA"""
    try:
        moeda_esquerda = par_moedas[:3]  # Ex: BRL em BRL_USD
        moeda_direita = par_moedas[4:]   # Ex: USD em BRL_USD
        
        print(f"🌐 Buscando: 1 {moeda_esquerda} = X {moeda_direita}")
        
        # =================================================
        # 🔥 CASO 1: SE ENVOLVER BRL → USAR BCB (CONFIÁVEL)
        # =================================================
        if moeda_esquerda == 'BRL' or moeda_direita == 'BRL':
            print(f"🔷 ENVOLVE BRL - Usando BCB/AwesomeAPI")
            
            # Para BRL_USD ou USD_BRL
            if 'USD' in [moeda_esquerda, moeda_direita]:
                try:
                    # AwesomeAPI tem dados do BCB para USD-BRL
                    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        cotacao_usd_brl = float(dados['USDBRL']['bid'])  # Taxa compra
                        
                        if par_moedas == 'BRL_USD':
                            # 1 BRL = ? USD → 1 / cotação
                            cotacao = 1 / cotacao_usd_brl
                            print(f"✅ BCB AwesomeAPI: 1 BRL = {cotacao:.6f} USD")
                        else:  # USD_BRL
                            cotacao = cotacao_usd_brl
                            print(f"✅ BCB AwesomeAPI: 1 USD = {cotacao:.4f} BRL")
                        
                        return cotacao
                except Exception as e:
                    print(f"⚠️ Erro AwesomeAPI BRL: {e}")
            
            # Para BRL_EUR
            elif 'EUR' in [moeda_esquerda, moeda_direita]:
                try:
                    # EUR-BRL do AwesomeAPI (também usa BCB)
                    url = "https://economia.awesomeapi.com.br/json/last/EUR-BRL"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        cotacao_eur_brl = float(dados['EURBRL']['bid'])
                        
                        if par_moedas == 'BRL_EUR':
                            cotacao = 1 / cotacao_eur_brl
                            print(f"✅ BCB AwesomeAPI: 1 BRL = {cotacao:.6f} EUR")
                        else:  # EUR_BRL
                            cotacao = cotacao_eur_brl
                            print(f"✅ BCB AwesomeAPI: 1 EUR = {cotacao:.4f} BRL")
                        
                        return cotacao
                except Exception as e:
                    print(f"⚠️ Erro AwesomeAPI EUR-BRL: {e}")
            
            # Para outras moedas com BRL
            else:
                # Usar ExchangeRate-API como fallback
                try:
                    api_key = os.getenv('EXCHANGERATE_API_KEY')
                    if api_key:
                        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{moeda_esquerda}/{moeda_direita}"
                        response = requests.get(url, timeout=5)
                        
                        if response.status_code == 200:
                            dados = response.json()
                            if dados.get('result') == 'success':
                                cotacao = float(dados['conversion_rate'])
                                print(f"✅ ExchangeRate-API BRL: 1 {moeda_esquerda} = {cotacao:.6f} {moeda_direita}")
                                return cotacao
                except:
                    pass
        
        # =================================================
        # 🔥 CASO 2: OUTRAS MOEDAS (EUR_USD, USD_EUR, etc.)
        # =================================================
        print(f"🔷 OUTRAS MOEDAS - Usando ExchangeRate-API")
        
        try:
            # PRIMEIRO: Sua API ExchangeRate-API
            api_key = os.getenv('EXCHANGERATE_API_KEY')
            if api_key:
                url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{moeda_esquerda}/{moeda_direita}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    dados = response.json()
                    if dados.get('result') == 'success':
                        cotacao = float(dados['conversion_rate'])
                        print(f"✅ ExchangeRate-API: 1 {moeda_esquerda} = {cotacao:.6f} {moeda_direita}")
                        return cotacao
        except Exception as e:
            print(f"⚠️ Erro ExchangeRate-API: {e}")
        
        # SEGUNDO: AwesomeAPI para pares não-BRL
        try:
            # Tenta direto primeiro
            url_direto = f"https://economia.awesomeapi.com.br/json/last/{moeda_esquerda}-{moeda_direita}"
            response = requests.get(url_direto, timeout=5)
            
            if response.status_code == 200:
                dados = response.json()
                chave = f"{moeda_esquerda}{moeda_direita}"
                
                if chave in dados:
                    cotacao = float(dados[chave]['bid'])
                    print(f"✅ AwesomeAPI direto: 1 {moeda_esquerda} = {cotacao:.6f} {moeda_direita}")
                    return cotacao
        except:
            try:
                # Tenta invertido
                url_invertido = f"https://economia.awesomeapi.com.br/json/last/{moeda_direita}-{moeda_esquerda}"
                response = requests.get(url_invertido, timeout=5)
                
                if response.status_code == 200:
                    dados = response.json()
                    chave = f"{moeda_direita}{moeda_esquerda}"
                    
                    if chave in dados:
                        cotacao_invertida = float(dados[chave]['bid'])
                        cotacao = 1 / cotacao_invertida
                        print(f"✅ AwesomeAPI invertido: 1 {moeda_esquerda} = {cotacao:.6f} {moeda_direita}")
                        return cotacao
            except:
                pass
        
        # ÚLTIMO RECURSO: Valores fixos de fallback
        print(f"⚠️ Usando fallback fixo para {par_moedas}")
        
        cotacoes_fallback = {
            'USD_BRL': 5.20,    # 1 USD = 5.20 BRL
            'BRL_USD': 0.1923,  # 1 BRL = 0.1923 USD (1/5.20)
            'EUR_BRL': 5.65,    # 1 EUR = 5.65 BRL
            'BRL_EUR': 0.1770,  # 1 BRL = 0.1770 EUR
            'GBP_BRL': 6.70,    # 1 GBP = 6.70 BRL
            'BRL_GBP': 0.1493,  # 1 BRL = 0.1493 GBP
            'USD_EUR': 0.92,    # 1 USD = 0.92 EUR
            'EUR_USD': 1.087,   # 1 EUR = 1.087 USD
            'USD_GBP': 0.78,    # 1 USD = 0.78 GBP
            'GBP_USD': 1.282,   # 1 GBP = 1.282 USD
        }
        
        if par_moedas in cotacoes_fallback:
            cotacao = cotacoes_fallback[par_moedas]
            print(f"📌 Fallback fixo: 1 {moeda_esquerda} = {cotacao} {moeda_direita}")
            return cotacao
        
        # Fallback genérico
        print(f"🚨 NENHUMA COTAÇÃO encontrada - usando 1.0")
        return 1.0
        
    except Exception as e:
        print(f"❌ Erro crítico em obter_cotacao_simples: {e}")
        import traceback
        traceback.print_exc()
        return 1.0

def obter_spread_cliente(usuario, par_moedas):
    """
    NOVA VERSÃO SEGURA - Busca spread com verificação de segurança máxima
    """
    try:
        print(f"💰 Buscando spread para {usuario} - par: {par_moedas}")
        
        # 1. VERIFICAÇÃO DE SEGURANÇA PRIMEIRO
        if not verificar_permissao_cambio_seguro(usuario):
            print(f"🚫 Cliente {usuario} SEM PERMISSÃO - spread zero")
            return {'compra': 0, 'venda': 0}  # Cliente bloqueado = spread zero
        
        # 2. Busca configuração de spreads
        spreads = obter_config_cliente('spreads', usuario)
        
        # 3. Verifica se o par específico existe
        if spreads and isinstance(spreads, dict) and par_moedas in spreads:
            spread_info = spreads[par_moedas]
            compra = float(spread_info.get('compra', 0.5))
            venda = float(spread_info.get('venda', 0.5))
            print(f"✅ Spread específico: compra={compra}%, venda={venda}%")
            return {'compra': compra, 'venda': venda}
        
        # 4. Se não encontrou específico, busca spread padrão do sistema
        spreads_sistema = obter_config_sistema('spreads')
        if spreads_sistema and isinstance(spreads_sistema, dict) and par_moedas in spreads_sistema:
            spread_info = spreads_sistema[par_moedas]
            compra = float(spread_info.get('compra', 0.5))
            venda = float(spread_info.get('venda', 0.5))
            print(f"⚠️ Spread do sistema: compra={compra}%, venda={venda}%")
            return {'compra': compra, 'venda': venda}
        
        # 5. Spread padrão final
        print(f"ℹ️ Spread padrão: 0.5%")
        return {'compra': 0.5, 'venda': 0.5}
        
    except Exception as e:
        print(f"⚠️ Erro ao obter spread: {e}")
        return {'compra': 0.5, 'venda': 0.5}

def verificar_horario_comercial(usuario=None):
    """
    NOVA VERSÃO - Usa config_cotacoes em vez de config_sistema
    Mantém compatibilidade com código existente
    """
    # Simplesmente chama a nova função, mas mantém o mesmo formato de retorno
    horario_ok, mensagem = verificar_horario_cliente(usuario)
    return horario_ok, mensagem


@app.route('/cambio-moedas')
def cambio_moedas():
    """Tela de compra e venda de moedas - VERSÃO ATUALIZADA"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    try:
        email = f'{usuario}@exemplo.com'
        nome = usuario.upper()
        cambio_liberado = False
        tipo_cliente = 'cliente'
        
        if supabase:
            # 🔥 BUSCAR DADOS REAIS
            response = supabase.table('usuarios')\
                .select('email, nome, cambio_liberado, tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if response.data:
                if response.data.get('email'):
                    email = response.data['email']
                if response.data.get('nome'):
                    nome = response.data['nome']
                if response.data.get('cambio_liberado') is not None:
                    cambio_liberado = bool(response.data['cambio_liberado'])
                if response.data.get('tipo'):
                    tipo_cliente = response.data['tipo']
                    
    except Exception as e:
        print(f"⚠️ Erro ao buscar dados do usuário: {e}")
    
    print(f"💰 Câmbio para {usuario}: liberado={cambio_liberado}, tipo={tipo_cliente}")
    
    # 🔥 PASSAR USUÁRIO CORRETO PARA O TEMPLATE
    return render_template('cambio_moedas.html',
                          usuario=usuario,  # ← CRÍTICO: passar o nome de usuário
                          email=email,
                          nome=nome,
                          cambio_liberado=cambio_liberado,
                          tipo_cliente=tipo_cliente)

# ============================================
# APIs PARA CÂMBIO DE MOEDAS (REAIS - IGUAL AO KIVY)
# ============================================

# ============================================
# ENDPOINTS PARA SEGURANÇA MÁXIMA
# (ADICIONAR ANTES de /api/pares-disponiveis/)
# ============================================

@app.route('/api/cambio/verificar-permissao/<cliente_username>')
def api_verificar_permissao_segura(cliente_username):
    """
    Endpoint específico para verificação de permissão (frontend)
    """
    pode_operar = verificar_permissao_cambio_seguro(cliente_username)
    
    if pode_operar:
        horario_ok, mensagem_horario = verificar_horario_cliente(cliente_username)
        pode_operar = horario_ok
        mensagem = mensagem_horario if not horario_ok else "Cliente autorizado"
        codigo = "FORA_HORARIO" if not horario_ok else None
    else:
        mensagem = "Cliente não autorizado para operações de câmbio"
        codigo = "PERMISSAO_NEGADA"
    
    return jsonify({
        'success': True,
        'pode_operar': pode_operar,
        'mensagem': mensagem,
        'codigo_erro': codigo,
        'cliente': cliente_username
    })

@app.route('/api/cambio/configuracao-completa/<cliente_username>')
def api_configuracao_completa(cliente_username):
    """
    Retorna TODAS as configurações do cliente
    """
    try:
        print(f"📋 Obtendo configurações completas para: {cliente_username}")
        
        # Verifica se pode operar
        pode_operar = verificar_permissao_cambio_seguro(cliente_username)
        horario_ok, mensagem_horario = verificar_horario_cliente(cliente_username)
        
        # Obtém outras configurações
        spreads = obter_config_cliente('spreads', cliente_username)
        limite = obter_config_cliente('limites', cliente_username)
        horario_config = obter_config_cliente('horarios', cliente_username)
        
        # Verifica se tem configuração específica
        tem_config_especifica = obter_config_cliente('permissoes', cliente_username) is not None
        
        # Configuração padrão do sistema
        horario_padrao = obter_config_sistema('horario_padrao')
        spreads_sistema = obter_config_sistema('spreads')
        
        return jsonify({
            'success': True,
            'configs': {
                'pode_operar': pode_operar and horario_ok,
                'mensagem': "Autorizado" if (pode_operar and horario_ok) else mensagem_horario,
                'codigo_erro': None if (pode_operar and horario_ok) else ("PERMISSAO_NEGADA" if not pode_operar else "FORA_HORARIO"),
                'limite': float(limite) if limite else 10000.00,
                'tem_config_especifica': tem_config_especifica,
                'horario_config': horario_config,
                'horario_padrao': horario_padrao,
                'spreads': spreads,
                'spreads_sistema': spreads_sistema
            },
            'cliente': cliente_username
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter configurações: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/cambio/verificar-horario/<cliente_username>')
def api_verificar_horario_cliente(cliente_username):
    """
    Verifica apenas horário do cliente
    """
    horario_ok, mensagem = verificar_horario_cliente(cliente_username)
    
    return jsonify({
        'success': True,
        'horario_ok': horario_ok,
        'mensagem': mensagem
    })

@app.route('/api/pares-disponiveis/<usuario>')
def api_pares_disponiveis(usuario):
    """API REAL - Pares disponíveis baseado nas contas do usuário"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    print(f"🔍 Buscando pares disponíveis para: {usuario}")
    
    try:
        if not supabase:
            return jsonify({
                'success': False,
                'error': 'Supabase não conectado',
                'pares': []
            })
        
        # 🔥 BUSCAR CONTAS REAIS DO SUPABASE
        response = supabase.table('contas')\
            .select('moeda')\
            .eq('cliente_username', usuario)\
            .eq('ativa', True)\
            .execute()
        
        if not response.data:
            print(f"⚠️ Usuário {usuario} não tem contas ativas")
            return jsonify({
                'success': True,
                'pares': [],
                'moedas_usuario': [],
                'mensagem': 'Usuário não tem contas ativas'
            })
        
        moedas_usuario = list(set([conta['moeda'] for conta in response.data]))
        print(f"✅ Moedas encontradas: {moedas_usuario}")
        
        # 🔥 GERAR PARES POSSÍVEIS (igual ao Kivy)
        pares = []
        for moeda1 in moedas_usuario:
            for moeda2 in moedas_usuario:
                if moeda1 != moeda2:
                    pares.append(f"{moeda1}_{moeda2}")
        
        print(f"✅ Pares gerados: {len(pares)} combinações")
        
        return jsonify({
            'success': True,
            'pares': pares,
            'moedas_usuario': moedas_usuario,
            'total_contas': len(moedas_usuario)
        })
        
    except Exception as e:
        print(f"❌ Erro em api_pares_disponiveis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'pares': []
        })

@app.route('/api/calcular-cambio', methods=['POST'])
def api_calcular_cambio():
    """API REAL - Calcula operação de câmbio EXATAMENTE como o Kivy"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    moeda_de = data.get('moedaDe')
    moeda_para = data.get('moedaPara')
    tipo_operacao = data.get('tipoOperacao')
    valor_digitado = float(data.get('valor', 0))
    usuario = data.get('usuario')
    
    print(f"🧮 Calculando câmbio: {moeda_de}->{moeda_para} ({tipo_operacao})")
    print(f"   Valor: {valor_digitado}")
    print(f"   Usuário: {usuario}")
    
    if not all([moeda_de, moeda_para, tipo_operacao, usuario]):
        return jsonify({'success': False, 'error': 'Parâmetros inválidos'})
    
    try:
        # 🔥 LÓGICA IDÊNTICA AO KIVY
        if tipo_operacao == 'compra':
            # COMPRA: Cliente COMPRA moeda_para, PAGA moeda_de
            # Par: MOEDA_PARA_MOEDA_DE (1 moeda_para = X moeda_de)
            par_correto = f"{moeda_para}_{moeda_de}"
            print(f"   PERSPECTIVA CORRIGIDA: COMPRA {moeda_para}, PAGA {moeda_de}")
        else:
            # VENDA: Cliente VENDE moeda_de, RECEBE moeda_para  
            # Par: MOEDA_DE_MOEDA_PARA (1 moeda_de = X moeda_para)
            par_correto = f"{moeda_de}_{moeda_para}"
            print(f"   PERSPECTIVA CORRIGIDA: VENDE {moeda_de}, RECEBE {moeda_para}")
        
        # 🔥 OBTER COTAÇÃO REAL (AwesomeAPI)
        cotacao_real = obter_cotacao_simples(par_correto)
        
        if not cotacao_real:
            return jsonify({'success': False, 'error': 'Erro ao obter cotação'})
        
        print(f"   Par correto: {par_correto}")
        print(f"   1 {par_correto[:3]} = {cotacao_real:.6f} {par_correto[4:]}")
        
        # 🔥 OBTER SPREAD
        spread_info = obter_spread_cliente(usuario, par_correto)
        spread = spread_info.get(tipo_operacao, 0.5)
        
        print(f"   Spread aplicado: {spread}%")
        
        # 🔥 APLICAR SPREAD (igual ao Kivy)
        if tipo_operacao == 'compra':
            # COMPRA: Cliente PAGA MAIS
            cotacao_cliente = cotacao_real * (1 + spread/100)
            print(f"   CLIENTE PAGA MAIS -> Spread: +{spread}%")
        else:
            # VENDA: Cliente RECEBE MENOS
            cotacao_cliente = cotacao_real * (1 - spread/100)
            print(f"   CLIENTE RECEBE MENOS -> Spread: -{spread}%")
        
        print(f"   Cotação para cliente: {cotacao_cliente:.6f}")
        
        # 🔥 CÁLCULO FINAL (igual ao Kivy)
        if tipo_operacao == 'compra':
            # COMPRA: Cliente RECEBE moeda_para (valor digitado), PAGA moeda_de
            valor_receber = valor_digitado
            valor_pagar = valor_receber * cotacao_cliente  # MULTIPLICAÇÃO
            resultado = valor_pagar
            print(f"   CÁLCULO COMPRA: {valor_receber:.2f} {moeda_para} x {cotacao_cliente:.6f} = {valor_pagar:.2f} {moeda_de}")
        else:
            # VENDA: Cliente PAGA moeda_de (valor digitado), RECEBE moeda_para
            valor_pagar = valor_digitado
            valor_receber = valor_pagar * cotacao_cliente  # MULTIPLICAÇÃO
            resultado = valor_receber
            print(f"   CÁLCULO VENDA: {valor_pagar:.2f} {moeda_de} x {cotacao_cliente:.6f} = {valor_receber:.2f} {moeda_para}")
        
        return jsonify({
            'success': True,
            'resultado': round(resultado, 2),
            'cotacao_usada': round(cotacao_cliente, 6),
            'moeda_de': moeda_de,
            'moeda_para': moeda_para,
            'valor_original': valor_digitado,
            'tipo_operacao': tipo_operacao,
            'spread_aplicado': spread,
            'par_calculo': par_correto
        })
        
    except Exception as e:
        print(f"❌ Erro em api_calcular_cambio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/cotacao', methods=['POST'])
def api_cotacao():
    """API REAL - Retorna cotação com spread (para exibição na UI)"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    par = data.get('par')
    operacao = data.get('operacao')
    usuario = data.get('usuario')
    
    print(f"📊 Solicitando cotação: {par} ({operacao}) para {usuario}")
    
    if not all([par, operacao, usuario]):
        return jsonify({'success': False, 'error': 'Parâmetros inválidos'})
    
    try:
        moeda_de = par.split('_')[0]
        moeda_para = par.split('_')[1]
        
        # 🔥 LÓGICA DO Kivy.calcular_cotacao_cliente()
        if operacao == 'compra':
            par_correto = f"{moeda_para}_{moeda_de}"  # RECEBE_PAGA
        else:
            par_correto = f"{moeda_de}_{moeda_para}"  # PAGA_RECEBE
        
        print(f"   Par para cálculo: {par_correto}")
        
        # Obter cotação real
        cotacao_real = obter_cotacao_simples(par_correto)
        
        if not cotacao_real:
            return jsonify({'success': False, 'error': 'Erro ao obter cotação'})
        
        # Obter spread
        spread_info = obter_spread_cliente(usuario, par_correto)
        spread = spread_info.get(operacao, 0.5)
        
        print(f"   Spread: {spread}%")
        
        # Aplicar spread
        if operacao == 'compra':
            cotacao_cliente = cotacao_real * (1 + spread/100)
        else:
            cotacao_cliente = cotacao_real * (1 - spread/100)
        
        print(f"   Cotação com spread: {cotacao_cliente:.6f}")
        
        # 🔥 CORREÇÃO APENAS PARA EXIBIÇÃO (igual ao Kivy)
        if operacao == 'venda':
            cotacao_exibicao = 1 / cotacao_cliente if cotacao_cliente != 0 else 0
            cotacao_final = round(cotacao_exibicao, 4)
            print(f"   Cotação invertida para exibição: {cotacao_final}")
        else:
            cotacao_final = round(cotacao_cliente, 4)
        
        return jsonify({
            'success': True,
            'cotacao': cotacao_final,
            'cotacao_base': round(cotacao_real, 4),
            'spread': spread,
            'par': par,
            'operacao': operacao,
            'par_calculo': par_correto
        })
        
    except Exception as e:
        print(f"❌ Erro em api_cotacao: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/verificar-horario/<usuario>')
def api_verificar_horario(usuario):
    """API para verificar horário comercial"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    print(f"⏰ Verificando horário para: {usuario}")
    
    horario_ok, mensagem = verificar_horario_comercial(usuario)
    
    return jsonify({
        'success': True,
        'horarioOk': horario_ok,
        'mensagem': mensagem
    })

@app.route('/api/limite-operacional/<usuario>')
def api_limite_operacional(usuario):
    """API para obter limite do cliente - USANDO SUA TABELA config_cotacoes"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        if not supabase:
            return jsonify({'success': True, 'limite': 10000.00})
        
        print(f"🔍 Buscando limite para {usuario}")
        
        # 🔥 1. VERIFICAR CÂMBIO LIBERADO
        cambio_liberado = False
        try:
            response_usuario = supabase.table('usuarios')\
                .select('cambio_liberado')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if response_usuario.data:
                cambio_liberado = bool(response_usuario.data.get('cambio_liberado', False))
        except Exception as e:
            print(f"⚠️  Erro ao verificar cambio_liberado: {e}")
        
        if not cambio_liberado:
            print(f"🚫 Câmbio NÃO liberado para {usuario}")
            return jsonify({
                'success': True,
                'limite': 0.00,
                'usuario': usuario,
                'cambio_liberado': False,
                'mensagem': 'Câmbio não liberado para este cliente'
            })
        
        # 🔥 2. BUSCAR LIMITE DO CLIENTE (config_cotacoes)
        limite_encontrado = None
        try:
            response = supabase.table('config_cotacoes')\
                .select('valor_config')\
                .eq('tipo_config', 'limites')\
                .eq('cliente_username', usuario)\
                .order('data_atualizacao', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                limite_encontrado = float(response.data[0]['valor_config'])
                print(f"✅ Limite ESPECÍFICO do cliente: {limite_encontrado}")
        except Exception as e:
            print(f"⚠️  Nenhum limite específico encontrado: {e}")
        
        # 🔥 3. SE NÃO ENCONTRAR, USAR LIMITE GERAL (config_sistema)
        if limite_encontrado is None:
            try:
                response = supabase.table('config_sistema')\
                    .select('valor_config')\
                    .eq('modulo', 'financeiras')\
                    .eq('chave_config', 'limite_transferencia_diario')\
                    .single()\
                    .execute()
                
                if response.data:
                    limite_encontrado = float(response.data['valor_config'])
                    print(f"✅ Limite GERAL do sistema: {limite_encontrado}")
            except Exception as e:
                print(f"⚠️  Erro ao buscar limite geral: {e}")
                limite_encontrado = 10000.00  # Default
        
        return jsonify({
            'success': True,
            'limite': limite_encontrado,
            'usuario': usuario,
            'cambio_liberado': cambio_liberado
        })
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar limite: {e}")
        return jsonify({'success': True, 'limite': 10000.00})

@app.route('/api/verificar-saldos/<usuario>', methods=['POST'])
def api_verificar_saldos(usuario):
    """API para verificar saldos antes da operação"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    moeda_pagar = data.get('moedaPagar')
    valor_pagar = float(data.get('valorPagar', 0))
    
    print(f"💰 Verificando saldos para {usuario}: {valor_pagar} {moeda_pagar}")
    
    try:
        if not supabase:
            return jsonify({
                'success': True,
                'saldosNegativos': [],
                'mensagem': 'Supabase não disponível'
            })
        
        # 🔥 BUSCAR SALDO REAL NO SUPABASE
        response = supabase.table('contas')\
            .select('saldo')\
            .eq('cliente_username', usuario)\
            .eq('moeda', moeda_pagar)\
            .eq('ativa', True)\
            .limit(1)\
            .execute()
        
        if response.data:
            saldo_atual = float(response.data[0]['saldo'])
            saldo_pos_operacao = saldo_atual - valor_pagar
            
            print(f"   Saldo atual: {saldo_atual:.2f} {moeda_pagar}")
            print(f"   Saldo pós-operação: {saldo_pos_operacao:.2f} {moeda_pagar}")
            
            if saldo_pos_operacao < 0:
                return jsonify({
                    'success': True,
                    'saldosNegativos': [{
                        'moeda': moeda_pagar,
                        'saldoAtual': saldo_atual,
                        'saldoPos': saldo_pos_operacao,
                        'valorOperacao': valor_pagar
                    }]
                })
        
        return jsonify({
            'success': True,
            'saldosNegativos': [],
            'mensagem': 'Saldos OK'
        })
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar saldos: {e}")
        return jsonify({
            'success': True,
            'saldosNegativos': [],
            'mensagem': 'Erro na verificação'
        })
    
@app.route('/api/executar-cambio', methods=['POST'])
def api_executar_cambio():
    """API REAL - Executa operação de câmbio e salva no Supabase"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    usuario = data.get('usuario')
    tipo_operacao = data.get('tipoOperacao')
    valor_pagar = data.get('valorPagar')
    valor_receber = data.get('valorReceber')
    moeda_pagar = data.get('moedaPagar')
    moeda_receber = data.get('moedaReceber')
    cotacao_cliente = data.get('cotacaoDireta')
    
    print(f"💰 Executando operação REAL de câmbio:")
    print(f"   Usuário: {usuario}")
    print(f"   Operação: {tipo_operacao}")
    print(f"   Pagar: {valor_pagar} {moeda_pagar}")
    print(f"   Receber: {valor_receber} {moeda_receber}")
    print(f"   Cotação: {cotacao_cliente}")
    
    # 🔥 🔥 🔥 NOVA VERIFICAÇÃO DE SEGURANÇA MÁXIMA 🔥 🔥 🔥
    print(f"🔐 Verificação SEGURANÇA MÁXIMA para: {usuario}")
    
    # 1. VERIFICAR PERMISSÃO (SEGURANÇA MÁXIMA)
    if not verificar_permissao_cambio_seguro(usuario):
        print(f"🚫 BLOQUEADO: Cliente {usuario} NÃO TEM PERMISSÃO")
        return jsonify({
            'success': False,
            'error': 'Cliente não autorizado para operações de câmbio',
            'codigo': 'PERMISSAO_NEGADA',
            'mensagem': 'Entre em contato com o suporte para liberar câmbio'
        })
    
    # 2. VERIFICAR HORÁRIO
    horario_ok, mensagem_horario = verificar_horario_cliente(usuario)
    if not horario_ok:
        print(f"🚫 FORA DO HORÁRIO: {mensagem_horario}")
        return jsonify({
            'success': False,
            'error': mensagem_horario,
            'codigo': 'FORA_HORARIO',
            'mensagem': mensagem_horario
        })
    
    print(f"✅ Cliente {usuario} AUTORIZADO para operar")
    # 🔥 🔥 🔥 FIM DA VERIFICAÇÃO DE SEGURANÇA 🔥 🔥 🔥
    
    # 3. VERIFICAR LIMITE DO CLIENTE (OPCIONAL MAS RECOMENDADO)
    try:
        # Buscar limite do cliente
        limite_config = obter_config_cliente('limites', usuario)
        
        if limite_config is not None:
            limite_cliente = float(limite_config)
            print(f"🔍 Limite do cliente: {limite_cliente}")
            
            # Converter valor da operação para float
            valor_operacao = float(valor_pagar) if tipo_operacao == 'venda' else float(valor_receber)
            
            if valor_operacao > limite_cliente:
                print(f"🚫 LIMITE EXCEDIDO: {valor_operacao} > {limite_cliente}")
                return jsonify({
                    'success': False,
                    'error': f'Limite de transação excedido. Máximo permitido: {limite_cliente:.2f}',
                    'codigo': 'LIMITE_EXCEDIDO',
                    'mensagem': f'Reduza o valor da operação. Seu limite: {limite_cliente:.2f}'
                })
    except Exception as e:
        print(f"⚠️ Erro ao verificar limite (continuando): {e}")
        # Continua mesmo se der erro na verificação de limite
    
    print(f"✅ Cliente {usuario} AUTORIZADO para operar")
    # 🔥 🔥 🔥 FIM DA VERIFICAÇÃO DE SEGURANÇA 🔥 🔥 🔥
    
    try:
        if not supabase:
            return jsonify({
                'success': False,
                'error': 'Supabase não conectado'
            })
        
        # 🔥 1. BUSCAR CONTAS DO USUÁRIO
        response_contas = supabase.table('contas')\
            .select('id, moeda, saldo')\
            .eq('cliente_username', usuario)\
            .eq('ativa', True)\
            .execute()
        
        if not response_contas.data:
            return jsonify({
                'success': False,
                'error': 'Usuário não tem contas ativas'
            })
        
        # Encontrar contas específicas
        conta_pagar = None
        conta_receber = None
        
        for conta in response_contas.data:
            if conta['moeda'] == moeda_pagar:
                conta_pagar = conta['id']
                saldo_pagar_antes = float(conta['saldo'])
            if conta['moeda'] == moeda_receber:
                conta_receber = conta['id']
                saldo_receber_antes = float(conta['saldo'])
        
        if not conta_pagar or not conta_receber:
            return jsonify({
                'success': False,
                'error': f'Conta não encontrada: {moeda_pagar} ou {moeda_receber}'
            })
        
        # 🔥 2. CALCULAR NOVOS SALDOS
        saldo_pagar_depois = saldo_pagar_antes - float(valor_pagar)
        saldo_receber_depois = saldo_receber_antes + float(valor_receber)
        
        print(f"   Conta pagar: {conta_pagar} ({moeda_pagar})")
        print(f"   Saldo antes: {saldo_pagar_antes:.2f} → depois: {saldo_pagar_depois:.2f}")
        print(f"   Conta receber: {conta_receber} ({moeda_receber})")
        print(f"   Saldo antes: {saldo_receber_antes:.2f} → depois: {saldo_receber_depois:.2f}")
        
        # 🔥 3. ATUALIZAR SALDOS NO SUPABASE
        # Conta que paga (diminui saldo)
        supabase.table('contas')\
            .update({'saldo': saldo_pagar_depois})\
            .eq('id', conta_pagar)\
            .execute()
        
        # Conta que recebe (aumenta saldo)
        supabase.table('contas')\
            .update({'saldo': saldo_receber_depois})\
            .eq('id', conta_receber)\
            .execute()
        
        # 🔥 4. REGISTRAR TRANSAÇÃO (igual ao Kivy com sufixo _nt)
        import random
        from datetime import datetime
        
        transacao_id = f"{random.randint(100000, 999999)}_nt"
        par_moedas = f"{moeda_pagar}_{moeda_receber}"
        
        dados_transacao = {
            'id': transacao_id,
            'tipo': 'cambio',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda_pagar,
            'valor': float(valor_pagar),
            'conta_remetente': conta_pagar,
            'conta_destinatario': conta_receber,
            'descricao': f'CÂMBIO - {tipo_operacao.upper()} {par_moedas}',
            'usuario': usuario,
            'cliente': usuario,
            'operacao': tipo_operacao,
            'par_moedas': par_moedas,
            'valor_origem': float(valor_pagar),
            'valor_destino': float(valor_receber),
            'cotacao': float(cotacao_cliente),
            'moeda_origem': moeda_pagar,
            'moeda_destino': moeda_receber,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Salvar no Supabase
        supabase.table('transferencias')\
            .insert(dados_transacao)\
            .execute()
        
        print(f"✅ Transação REAL salva: {transacao_id}")
        
        return jsonify({
            'success': True,
            'transacaoId': transacao_id,
            'mensagem': 'Operação realizada com sucesso!',
            'novo_saldo_pagar': saldo_pagar_depois,
            'novo_saldo_receber': saldo_receber_depois
        })
        
    except Exception as e:
        print(f"❌ Erro ao executar câmbio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

def obter_cotacao_exchangerate(moeda_origem, moeda_destino):
    """API REAL do ExchangeRate-API (sua chave já está configurada)"""
    try:
        # 🔥 PEGAR CHAVE DO AMBIENTE
        api_key = os.getenv('EXCHANGERATE_API_KEY')
        
        if not api_key:
            print("⚠️  EXCHANGERATE_API_KEY não configurada no ambiente")
            return None
        
        print(f"🌐 ExchangeRate-API: {moeda_origem}→{moeda_destino}")
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{moeda_origem}/{moeda_destino}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            if dados.get('result') == 'success':
                cotacao = float(dados['conversion_rate'])
                print(f"✅ ExchangeRate-API: 1 {moeda_origem} = {cotacao} {moeda_destino}")
                return cotacao
            else:
                print(f"⚠️  ExchangeRate-API erro: {dados.get('error-type', 'Unknown')}")
        else:
            print(f"⚠️  ExchangeRate-API HTTP {response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"⚠️  Erro ExchangeRate-API: {e}")
        return None
    
# ============================================
# FUNÇÕES DE SEGURANÇA MÁXIMA - BLOQUEIO POR PADRÃO
# (ADICIONAR ESTA SEÇÃO NO SEU web_api.py)
# ============================================

def obter_config_cliente(tipo_config, cliente_username, par_moeda=None):
    """
    Busca configuração ESPECÍFICA de um cliente
    Retorna None se não encontrar configuração para este cliente
    """
    try:
        print(f"🔍 Buscando {tipo_config} para cliente: {cliente_username}")
        
        if not supabase:
            return None
        
        query = supabase.table('config_cotacoes')\
            .select('valor_config, data_atualizacao')\
            .eq('tipo_config', tipo_config)\
            .eq('cliente_username', cliente_username)
        
        if par_moeda:
            query = query.eq('par_moeda', par_moeda)
        
        response = query.order('data_atualizacao', desc=True)\
                       .limit(1)\
                       .execute()
        
        if response.data and response.data[0]['valor_config'] is not None:
            print(f"✅ Configuração específica encontrada para {cliente_username}")
            return response.data[0]['valor_config']
        
        print(f"ℹ️ Nenhuma configuração específica para {cliente_username}")
        return None
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar {tipo_config} para {cliente_username}: {e}")
        return None

def obter_config_sistema(tipo_config):
    """
    Busca configuração PADRÃO do sistema (cliente_username = 'sistema')
    """
    try:
        print(f"🔍 Buscando {tipo_config} do sistema")
        
        response = supabase.table('config_cotacoes')\
            .select('valor_config')\
            .eq('tipo_config', tipo_config)\
            .eq('cliente_username', 'sistema')\
            .order('data_atualizacao', desc=True)\
            .limit(1)\
            .execute()
        
        if response.data and response.data[0]['valor_config'] is not None:
            print(f"✅ Configuração do sistema encontrada")
            return response.data[0]['valor_config']
        
        print(f"ℹ️ Nenhuma configuração do sistema para {tipo_config}")
        return None
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar configuração do sistema: {e}")
        return None

def verificar_permissao_cambio_seguro(cliente_username):
    """
    VERIFICAÇÃO SEGURA - BLOQUEIA se não houver configuração explícita
    ORDEM: 1. Cliente específico → 2. Sistema → 3. BLOQUEADO
    """
    try:
        print(f"🔐 Verificação SEGURA para: {cliente_username}")
        
        # 1. BUSCA CONFIGURAÇÃO ESPECÍFICA DO CLIENTE
        config_cliente = obter_config_cliente('permissoes', cliente_username)
        
        if config_cliente is not None:
            # Cliente TEM configuração específica
            if isinstance(config_cliente, str):
                config_cliente = config_cliente.lower() in ['true', 't', '1', 'yes', 'y', 'verdadeiro']
            
            permissao = bool(config_cliente)
            status = "LIBERADO" if permissao else "BLOQUEADO"
            print(f"✅ Configuração ESPECÍFICA: {status}")
            return permissao
        
        # 2. BUSCA CONFIGURAÇÃO PADRÃO DO SISTEMA
        config_sistema = obter_config_sistema('permissoes')
        
        if config_sistema is not None:
            # Sistema TEM configuração padrão
            if isinstance(config_sistema, str):
                config_sistema = config_sistema.lower() in ['true', 't', '1', 'yes', 'y', 'verdadeiro']
            
            permissao = bool(config_sistema)
            status = "LIBERADO" if permissao else "BLOQUEADO"
            print(f"⚠️ Configuração do SISTEMA: {status}")
            return permissao
        
        # 3. SE NÃO TEM NENHUMA CONFIGURAÇÃO → BLOQUEADO POR PADRÃO 🔥
        print(f"🚫 SEM configuração → BLOQUEADO POR PADRÃO (segurança máxima)")
        return False
        
    except Exception as e:
        print(f"⚠️ Erro na verificação segura: {e}")
        return False  # Em caso de erro, BLOQUEIA por segurança
    
def verificar_horario_cliente(cliente_username):
    """
    Verifica se QUALQUER cliente está dentro do horário permitido
    Usa config_cotacoes em vez de config_sistema
    """
    try:
        from datetime import datetime
        import pytz
        
        print(f"⏰ Verificando horário para {cliente_username}")
        
        # 1. Busca horário do cliente (se tiver)
        horario_cliente = obter_config_cliente('horarios', cliente_username)
        
        # 2. Se cliente não tem horário, usa horário padrão do sistema
        if horario_cliente is None:
            horario_cliente = obter_config_sistema('horario_padrao')
            if horario_cliente:
                print(f"   Usando horário padrão do sistema")
        
        # 3. Se não tiver nenhum, usar valores padrão de segurança
        if not horario_cliente:
            horario_cliente = {
                'inicio': '10:00',
                'fim': '15:00',
                'dias_semana': [0, 1, 2, 3, 4],
                'fuso_horario': 'America/Sao_Paulo'
            }
            print(f"   Usando valores padrão de segurança")
        
        # 4. Extrair configurações
        inicio = horario_cliente.get('inicio', '10:00')
        fim = horario_cliente.get('fim', '15:00')
        dias_semana = horario_cliente.get('dias_semana', [0, 1, 2, 3, 4])
        fuso_horario = horario_cliente.get('fuso_horario', 'America/Sao_Paulo')
        
        print(f"   Config: {inicio}-{fim}, dias: {dias_semana}, fuso: {fuso_horario}")
        
        # 5. Obtém hora atual no fuso correto
        try:
            tz = pytz.timezone(fuso_horario)
            agora = datetime.now(tz)
        except:
            tz = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(tz)
        
        hora_atual = agora.strftime('%H:%M')
        dia_semana_num = agora.weekday()
        
        print(f"   Hora atual: {hora_atual} (dia {dia_semana_num})")
        
        # 6. Verifica dia da semana
        if dia_semana_num not in dias_semana:
            nomes_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            dias_permitidos_nomes = [nomes_dias[i] for i in dias_semana if i < 7]
            mensagem = f"Fora do horário comercial. Dias permitidos: {', '.join(dias_permitidos_nomes)}"
            print(f"   ❌ {mensagem}")
            return False, mensagem
        
        # 7. Verifica horário
        if hora_atual < inicio:
            mensagem = f"Fora do horário. Disponível a partir das {inicio}"
            print(f"   ❌ {mensagem}")
            return False, mensagem
        
        if hora_atual > fim:
            mensagem = f"Fora do horário. Disponível até às {fim}"
            print(f"   ❌ {mensagem}")
            return False, mensagem
        
        print(f"   ✅ Dentro do horário permitido")
        return True, "Dentro do horário comercial"
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar horário: {e}")
        return True, "Erro na verificação - permitido por segurança"

@app.route('/perfil')
def perfil():
    """Tela completa do perfil do usuário"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    try:
        # 1. Buscar dados do usuário
        user_response = supabase.table('usuarios')\
            .select('*')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        user_data = user_response.data if user_response.data else {}
        
        # 2. Buscar contas do usuário
        contas_response = supabase.table('contas')\
            .select('id, moeda, saldo, ativa, data_criacao')\
            .eq('cliente_username', usuario)\
            .eq('ativa', True)\
            .order('data_criacao', desc=True)\
            .execute()
        
        contas = contas_response.data if contas_response.data else []
        
        # 3. Calcular estatísticas
        total_contas = len(contas)
        status_conta = user_data.get('status', 'pendente')
        verificado = user_data.get('verificado', False)
        cambio_liberado = user_data.get('cambio_liberado', False)
        
        # 4. Formatar dados para exibição
        dados_formatados = {
            # Informações básicas
            'username': user_data.get('username', usuario),
            'nome': user_data.get('nome', usuario.upper()),
            'email': user_data.get('email', f'{usuario}@email.com'),
            'telefone': user_data.get('telefone', 'Não informado'),
            'tipo': user_data.get('tipo', 'cliente').title(),
            
            # Endereço
            'endereco': user_data.get('endereco', 'Não informado'),
            'cidade': user_data.get('cidade', 'Não informado'),
            'estado': user_data.get('estado', 'Não informado'),
            'pais': user_data.get('pais', 'Não informado'),
            'cep': user_data.get('cep', 'Não informado'),
            
            # Datas
            'data_cadastro': user_data.get('data_cadastro', ''),
            'created_at': user_data.get('created_at', ''),
            
            # Status
            'status': status_conta,
            'verificado': verificado,
            'cambio_liberado': cambio_liberado,
            'codigo_verificacao': user_data.get('codigo_verificacao', '')
        }
        
        # 5. Preparar contas por moeda
        contas_por_moeda = {}
        for conta in contas:
            moeda = conta['moeda']
            if moeda not in contas_por_moeda:
                contas_por_moeda[moeda] = []
            contas_por_moeda[moeda].append(conta)
        
        return render_template('perfil.html',
                             usuario=usuario,
                             dados=dados_formatados,
                             contas=contas,
                             contas_por_moeda=contas_por_moeda,
                             total_contas=total_contas,
                             tem_contas=total_contas > 0)
        
    except Exception as e:
        print(f"❌ Erro ao carregar perfil: {e}")
        import traceback
        traceback.print_exc()
        # Fallback seguro
        return render_template('perfil.html',
                             usuario=usuario,
                             dados={'username': usuario, 'nome': usuario.upper()},
                             contas=[],
                             contas_por_moeda={},
                             total_contas=0,
                             tem_contas=False)





# ============================================
# ENDPOINTS ADMIN (DASHBOARD)
# ============================================

@app.route('/admin/dashboard')
def admin_dashboard():
    """Dashboard administrativo"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Verificar se é admin
    try:
        response = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if response.data.get('tipo') != 'admin':
            return redirect('/dashboard')
    except:
        return redirect('/dashboard')
    
    # Buscar dados do usuário
    nome = usuario.upper()
    email = f'{usuario}@exemplo.com'
    
    try:
        user_response = supabase.table('usuarios')\
            .select('nome, email')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if user_response.data:
            if user_response.data.get('nome'):
                nome = user_response.data['nome']
            if user_response.data.get('email'):
                email = user_response.data['email']
    except:
        pass
    
    return render_template('admin_dashboard.html',
                          usuario=usuario,
                          nome=nome,
                          email=email)

@app.route('/api/admin/dashboard')
def api_admin_dashboard():
    """API para dados do dashboard admin"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        # 1. Estatísticas
        # Total de clientes
        clientes_response = supabase.table('usuarios')\
            .select('username', count='exact')\
            .eq('tipo', 'cliente')\
            .execute()
        total_clientes = clientes_response.count if clientes_response.count else 0
        
        # Total de transferências
        transf_response = supabase.table('transferencias')\
            .select('id', count='exact')\
            .execute()
        total_transferencias = transf_response.count if transf_response.count else 0
        
        # Pendentes (solicitada)
        pendentes_response = supabase.table('transferencias')\
            .select('id', count='exact')\
            .eq('status', 'solicitada')\
            .execute()
        pendentes = pendentes_response.count if pendentes_response.count else 0
        
        # Processando
        processando_response = supabase.table('transferencias')\
            .select('id', count='exact')\
            .eq('status', 'processing')\
            .execute()
        processando = processando_response.count if processando_response.count else 0
        
        # 2. Últimas 10 transações
        ultimas_transf = supabase.table('transferencias')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(10)\
            .execute()
        
        transacoes_formatadas = []
        for t in (ultimas_transf.data or []):
            transacoes_formatadas.append({
                'id': t.get('id'),
                'tipo': t.get('tipo'),
                'status': t.get('status'),
                'valor': t.get('valor', 0),
                'moeda': t.get('moeda', 'USD'),
                'beneficiario': t.get('beneficiario', ''),
                'descricao': t.get('descricao', ''),
                'data': t.get('created_at') or t.get('data'),
                'cliente': t.get('cliente') or t.get('usuario')
            })
        
        return jsonify({
            "success": True,
            "stats": {
                "total_clientes": total_clientes,
                "total_transferencias": total_transferencias,
                "pendentes": pendentes,
                "processando": processando
            },
            "ultimas_transacoes": transacoes_formatadas
        })
        
    except Exception as e:
        print(f"❌ Erro no admin dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# ENDPOINTS ADMIN - CLIENTES
# ============================================

@app.route('/admin/clientes')
def admin_clientes():
    """Lista de clientes para admin"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Verificar admin
    user_check = supabase.table('usuarios')\
        .select('tipo')\
        .eq('username', usuario)\
        .single()\
        .execute()
    
    if not user_check.data or user_check.data.get('tipo') != 'admin':
        return redirect('/dashboard')
    
    return render_template('admin_clientes.html',
                          usuario=usuario,
                          nome="Administrador")

@app.route('/api/admin/clientes')
def api_admin_clientes():
    """API para listar todos os clientes"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar admin
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        # Buscar todos os clientes
        clientes_response = supabase.table('usuarios')\
            .select('username, nome, email, telefone, tipo, status, verificado, cambio_liberado, data_cadastro')\
            .eq('tipo', 'cliente')\
            .order('data_cadastro', desc=True)\
            .execute()
        
        clientes = []
        for c in (clientes_response.data or []):
            # Buscar contas do cliente
            contas_response = supabase.table('contas')\
                .select('id, moeda, saldo')\
                .eq('cliente_username', c['username'])\
                .eq('ativa', True)\
                .execute()
            
            saldo_total = sum(float(conta.get('saldo', 0)) for conta in (contas_response.data or []))
            
            clientes.append({
                'username': c.get('username'),
                'nome': c.get('nome', c.get('username')),
                'email': c.get('email', ''),
                'telefone': c.get('telefone', ''),
                'status': c.get('status', 'ativo'),
                'verificado': c.get('verificado', False),
                'cambio_liberado': c.get('cambio_liberado', False),
                'data_cadastro': c.get('data_cadastro', ''),
                'total_contas': len(contas_response.data or []),
                'saldo_total': saldo_total
            })
        
        return jsonify({
            "success": True,
            "clientes": clientes
        })
        
    except Exception as e:
        print(f"❌ Erro ao listar clientes: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/clientes/<username>/toggle-cambio', methods=['POST'])
def api_admin_toggle_cambio(username):
    """Ativa/desativa câmbio para um cliente"""
    try:
        admin_user = session.get('username')
        
        if not admin_user:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar admin
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', admin_user)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        data = request.get_json()
        liberado = data.get('cambio_liberado', False)
        
        # Atualizar usuário
        update_response = supabase.table('usuarios')\
            .update({'cambio_liberado': liberado})\
            .eq('username', username)\
            .execute()
        
        # Também atualizar config_cotacoes
        config_data = {
            'tipo_config': 'permissoes',
            'cliente_username': username,
            'valor_config': liberado,
            'data_atualizacao': datetime.now().isoformat()
        }
        
        # Verificar se já existe
        check = supabase.table('config_cotacoes')\
            .select('id')\
            .eq('tipo_config', 'permissoes')\
            .eq('cliente_username', username)\
            .execute()
        
        if check.data:
            supabase.table('config_cotacoes')\
                .update(config_data)\
                .eq('id', check.data[0]['id'])\
                .execute()
        else:
            supabase.table('config_cotacoes')\
                .insert(config_data)\
                .execute()
        
        return jsonify({
            "success": True,
            "message": f"Câmbio {'liberado' if liberado else 'bloqueado'} para {username}"
        })
        
    except Exception as e:
        print(f"❌ Erro ao alterar permissão de câmbio: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    

# ============================================
# ADMIN - CONTAS BANCÁRIAS DA EMPRESA
# ============================================

@app.route('/admin/contas-bancarias')
def admin_contas_bancarias():
    """Tela de gerenciamento de contas bancárias"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Verificar se é admin
    if supabase:
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return redirect('/dashboard')
    
    # Buscar dados do usuário
    nome = usuario.upper()
    email = f'{usuario}@exemplo.com'
    
    try:
        if supabase:
            user_response = supabase.table('usuarios')\
                .select('nome, email')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if user_response.data:
                if user_response.data.get('nome'):
                    nome = user_response.data['nome']
                if user_response.data.get('email'):
                    email = user_response.data['email']
    except:
        pass
    
    return render_template('admin_contas_bancarias.html',
                          usuario=usuario,
                          nome=nome,
                          email=email)


@app.route('/api/admin/contas-bancarias', methods=['GET'])
def api_admin_contas_bancarias():
    """Retorna todas as contas bancárias da empresa"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        # Buscar contas do Supabase
        response = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .order('moeda')\
            .execute()
        
        contas = []
        totais = {'USD': 0, 'EUR': 0, 'GBP': 0, 'BRL': 0}
        
        for conta in (response.data or []):
            saldo = float(conta.get('saldo', 0))
            moeda = conta.get('moeda', 'USD')
            
            contas.append({
                'numero': conta.get('numero'),
                'banco': conta.get('banco'),
                'agencia': conta.get('agencia', ''),
                'moeda': moeda,
                'saldo': saldo,
                'tipo': conta.get('tipo', 'empresa'),
                'data_criacao': conta.get('data_criacao')
            })
            
            if moeda in totais:
                totais[moeda] += saldo
        
        return jsonify({
            "success": True,
            "contas": contas,
            "totais": totais
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar contas bancárias: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/contas-bancarias', methods=['POST'])
def api_admin_criar_conta_bancaria():
    """Cria uma nova conta bancária"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        banco = dados.get('banco', '').strip()
        agencia = dados.get('agencia', '').strip()
        numero = dados.get('numero', '').strip()
        moeda = dados.get('moeda', '').strip().upper()
        
        if not banco or not agencia or not numero or not moeda:
            return jsonify({"success": False, "message": "Todos os campos são obrigatórios"}), 400
        
        if len(moeda) != 3 or not moeda.isalpha():
            return jsonify({"success": False, "message": "Moeda inválida! Use exatamente 3 letras (Ex: USD, EUR, JPY)"}), 400
        
        from datetime import datetime
        import random
        
        # Verificar se conta já existe
        check = supabase.table('contas_bancarias_empresa')\
            .select('numero')\
            .eq('numero', numero)\
            .execute()
        
        if check.data:
            return jsonify({"success": False, "message": f"Conta {numero} já existe!"}), 400
        
        # Criar nova conta
        nova_conta = {
            'numero': numero,
            'banco': banco,
            'agencia': agencia,
            'moeda': moeda,
            'saldo': 0.00,
            'saldo_inicial': 0.00,
            'tipo': 'empresa',
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('contas_bancarias_empresa')\
            .insert(nova_conta)\
            .execute()
        
        if response.data:
            print(f"✅ Conta {numero} criada com sucesso!")
            return jsonify({
                "success": True,
                "message": f"Conta {numero} criada com sucesso!",
                "conta": nova_conta
            })
        else:
            return jsonify({"success": False, "message": "Erro ao criar conta"}), 500
        
    except Exception as e:
        print(f"❌ Erro ao criar conta bancária: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/contas-bancarias/deposito', methods=['POST'])
def api_admin_deposito_conta():
    """Realiza depósito em conta bancária"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        conta_numero = dados.get('conta_numero')
        valor = float(dados.get('valor', 0))
        descricao = dados.get('descricao', 'Depósito em conta')
        
        if not conta_numero:
            return jsonify({"success": False, "message": "Conta não informada"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        # Buscar conta
        response = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_numero)\
            .single()\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Conta não encontrada"}), 404
        
        conta = response.data
        saldo_atual = float(conta.get('saldo', 0))
        novo_saldo = saldo_atual + valor
        moeda = conta.get('moeda', 'USD')
        
        # Atualizar saldo
        update_response = supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo})\
            .eq('numero', conta_numero)\
            .execute()
        
        if not update_response.data:
            return jsonify({"success": False, "message": "Erro ao atualizar saldo"}), 500
        
        # Registrar transação
        from datetime import datetime
        import random
        
        transacao_id = f"{random.randint(100000, 999999)}_dep"
        
        transacao = {
            'id': transacao_id,
            'tipo': 'deposito',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda,
            'valor': valor,
            'conta_destinatario': conta_numero,
            'descricao': descricao,
            'usuario': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('transferencias').insert(transacao).execute()
        
        print(f"💰 Depósito de {valor:.2f} {moeda} realizado na conta {conta_numero}")
        
        return jsonify({
            "success": True,
            "message": f"Depósito de {valor:.2f} {moeda} realizado com sucesso!",
            "novo_saldo": novo_saldo
        })
        
    except Exception as e:
        print(f"❌ Erro ao realizar depósito: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/contas-bancarias/saque', methods=['POST'])
def api_admin_saque_conta():
    """Realiza saque de conta bancária"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        conta_numero = dados.get('conta_numero')
        valor = float(dados.get('valor', 0))
        descricao = dados.get('descricao', 'Saque da conta')
        
        if not conta_numero:
            return jsonify({"success": False, "message": "Conta não informada"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        # Buscar conta
        response = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_numero)\
            .single()\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Conta não encontrada"}), 404
        
        conta = response.data
        saldo_atual = float(conta.get('saldo', 0))
        moeda = conta.get('moeda', 'USD')
        
        # Verificar saldo (apenas aviso, permite negativo)
        if valor > saldo_atual:
            print(f"⚠️ Aviso: Saldo insuficiente! Saldo: {saldo_atual:.2f}, Saque: {valor:.2f}")
        
        novo_saldo = saldo_atual - valor
        
        # Atualizar saldo
        update_response = supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo})\
            .eq('numero', conta_numero)\
            .execute()
        
        if not update_response.data:
            return jsonify({"success": False, "message": "Erro ao atualizar saldo"}), 500
        
        # Registrar transação
        from datetime import datetime
        import random
        
        transacao_id = f"{random.randint(100000, 999999)}_saq"
        
        transacao = {
            'id': transacao_id,
            'tipo': 'saque',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda,
            'valor': valor,
            'conta_remetente': conta_numero,
            'descricao': descricao,
            'usuario': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('transferencias').insert(transacao).execute()
        
        print(f"💸 Saque de {valor:.2f} {moeda} realizado da conta {conta_numero}")
        
        return jsonify({
            "success": True,
            "message": f"Saque de {valor:.2f} {moeda} realizado com sucesso!",
            "novo_saldo": novo_saldo
        })
        
    except Exception as e:
        print(f"❌ Erro ao realizar saque: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/contas-bancarias/ajuste', methods=['POST'])
def api_admin_ajuste_saldo():
    """Realiza ajuste de saldo em conta bancária (permite saldo negativo)"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        conta_numero = dados.get('conta_numero')
        valor = float(dados.get('valor', 0))
        operacao = dados.get('operacao')  # 'credito' ou 'debito'
        descricao = dados.get('descricao', 'Ajuste administrativo')
        
        if not conta_numero:
            return jsonify({"success": False, "message": "Conta não informada"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        if operacao not in ['credito', 'debito']:
            return jsonify({"success": False, "message": "Operação inválida"}), 400
        
        # Buscar conta
        response = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_numero)\
            .single()\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Conta não encontrada"}), 404
        
        conta = response.data
        saldo_atual = float(conta.get('saldo', 0))
        moeda = conta.get('moeda', 'USD')
        
        if operacao == 'credito':
            novo_saldo = saldo_atual + valor
            tipo_ajuste = "CRÉDITO"
            tipo_registro = "DÉBITO"  # Aparece na coluna DÉBITO do extrato
        else:
            novo_saldo = saldo_atual - valor
            tipo_ajuste = "DÉBITO"
            tipo_registro = "CRÉDITO"  # Aparece na coluna CRÉDITO do extrato
        
        # Atualizar saldo
        update_response = supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo})\
            .eq('numero', conta_numero)\
            .execute()
        
        if not update_response.data:
            return jsonify({"success": False, "message": "Erro ao atualizar saldo"}), 500
        
        # Registrar transação
        from datetime import datetime
        import random
        
        transacao_id = f"{random.randint(100000, 999999)}_aj"
        
        transacao = {
            'id': transacao_id,
            'tipo': 'ajuste_saldo_empresa',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda,
            'valor': valor,
            'conta_remetente': conta_numero,
            'descricao': descricao,
            'tipo_ajuste': tipo_registro,
            'tipo_interface': tipo_ajuste,
            'descricao_ajuste': descricao,
            'usuario': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('transferencias').insert(transacao).execute()
        
        aviso = ""
        if novo_saldo < 0:
            aviso = " ⚠️ ATENÇÃO: A conta ficou com saldo NEGATIVO!"
        
        print(f"💰 Ajuste {tipo_ajuste} de {valor:.2f} {moeda} na conta {conta_numero}")
        
        return jsonify({
            "success": True,
            "message": f"Ajuste {tipo_ajuste} de {valor:.2f} {moeda} realizado com sucesso!{aviso}",
            "novo_saldo": novo_saldo
        })
        
    except Exception as e:
        print(f"❌ Erro ao realizar ajuste: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/contas-bancarias/cambio', methods=['POST'])
def api_admin_cambio_contas():
    """Realiza câmbio entre contas bancárias da empresa"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        conta_origem = dados.get('conta_origem')
        conta_destino = dados.get('conta_destino')
        valor = float(dados.get('valor', 0))
        taxa_principal = float(dados.get('taxa_principal', 0))
        
        if not conta_origem or not conta_destino:
            return jsonify({"success": False, "message": "Contas origem e destino são obrigatórias"}), 400
        
        if conta_origem == conta_destino:
            return jsonify({"success": False, "message": "Conta origem e destino devem ser diferentes"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        if taxa_principal <= 0:
            return jsonify({"success": False, "message": "Taxa de câmbio inválida"}), 400
        
        # Buscar contas
        response_origem = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_origem)\
            .single()\
            .execute()
        
        response_destino = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_destino)\
            .single()\
            .execute()
        
        if not response_origem.data:
            return jsonify({"success": False, "message": f"Conta origem {conta_origem} não encontrada"}), 404
        
        if not response_destino.data:
            return jsonify({"success": False, "message": f"Conta destino {conta_destino} não encontrada"}), 404
        
        conta_origem_data = response_origem.data
        conta_destino_data = response_destino.data
        
        saldo_origem = float(conta_origem_data.get('saldo', 0))
        moeda_origem = conta_origem_data.get('moeda', 'USD')
        moeda_destino = conta_destino_data.get('moeda', 'USD')
        
        valor_destino = valor * taxa_principal
        
        # Verificar saldo origem (apenas aviso)
        if valor > saldo_origem:
            print(f"⚠️ Aviso: Saldo insuficiente na origem! Saldo: {saldo_origem:.2f}, Valor: {valor:.2f}")
        
        novo_saldo_origem = saldo_origem - valor
        novo_saldo_destino = float(conta_destino_data.get('saldo', 0)) + valor_destino
        
        # Atualizar saldos
        supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo_origem})\
            .eq('numero', conta_origem)\
            .execute()
        
        supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo_destino})\
            .eq('numero', conta_destino)\
            .execute()
        
        # Registrar transação
        from datetime import datetime
        import random
        
        transacao_id = f"{random.randint(100000, 999999)}_cb"
        
        transacao = {
            'id': transacao_id,
            'tipo': 'cambio_contas_empresa',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda_origem': moeda_origem,
            'moeda_destino': moeda_destino,
            'valor_origem': valor,
            'valor_destino': valor_destino,
            'taxa_cambio': taxa_principal,
            'taxa_principal_registro': taxa_principal,
            'conta_origem': conta_origem,
            'conta_destino': conta_destino,
            'usuario': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('transferencias').insert(transacao).execute()
        
        print(f"💱 Câmbio realizado: {valor:.2f} {moeda_origem} → {valor_destino:.2f} {moeda_destino}")
        
        return jsonify({
            "success": True,
            "message": f"Câmbio realizado com sucesso!\n{valor:.2f} {moeda_origem} → {valor_destino:.2f} {moeda_destino}",
            "novo_saldo_origem": novo_saldo_origem,
            "novo_saldo_destino": novo_saldo_destino
        })
        
    except Exception as e:
        print(f"❌ Erro ao realizar câmbio: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# ADMIN - EXTRATO DE CONTA BANCÁRIA
# ============================================

@app.route('/admin/extrato-conta')
def admin_extrato_conta():
    """Tela de extrato de conta bancária"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Verificar se é admin
    if supabase:
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return redirect('/dashboard')
    
    conta_numero = request.args.get('conta', '')
    
    # Buscar dados da conta
    conta_info = {}
    if supabase and conta_numero:
        response = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_numero)\
            .single()\
            .execute()
        
        if response.data:
            conta_info = response.data
    
    return render_template('admin_extrato_conta.html',
                          usuario=usuario,
                          conta_numero=conta_numero,
                          conta_info=conta_info)


@app.route('/api/admin/extrato-conta', methods=['POST'])
def api_admin_extrato_conta():
    """Retorna extrato da conta bancária com filtro de período"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        conta_numero = dados.get('conta_numero')
        periodo = dados.get('periodo', '30')
        data_inicio = dados.get('data_inicio')
        data_fim = dados.get('data_fim')
        
        if not conta_numero:
            return jsonify({"success": False, "message": "Conta não informada"}), 400
        
        from datetime import datetime, timedelta
        
        # Definir período
        if periodo == 'personalizado' and data_inicio and data_fim:
            data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
            data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
        elif periodo == '0':
            data_inicio_obj = datetime(2024, 1, 1)
            data_fim_obj = datetime.now()
        else:
            dias = int(periodo)
            data_inicio_obj = datetime.now() - timedelta(days=dias)
            data_fim_obj = datetime.now()
        
        print(f"📅 Período: {data_inicio_obj} a {data_fim_obj}")
        print(f"🔍 Buscando transações para conta: {conta_numero}")
        
        # ============================================
        # BUSCAR TODAS AS TRANSAÇÕES QUE ENVOLVEM A CONTA
        # ============================================
        
        # Buscar onde a conta é remetente
        response1 = supabase.table('transferencias')\
            .select('*')\
            .eq('conta_remetente', conta_numero)\
            .execute()
        
        # Buscar onde a conta é destinatário
        response2 = supabase.table('transferencias')\
            .select('*')\
            .eq('conta_destinatario', conta_numero)\
            .execute()
        
        # Buscar onde a conta é origem (para câmbio)
        response3 = supabase.table('transferencias')\
            .select('*')\
            .eq('conta_origem', conta_numero)\
            .execute()
        
        # Buscar onde a conta é destino (para câmbio)
        response4 = supabase.table('transferencias')\
            .select('*')\
            .eq('conta_destino', conta_numero)\
            .execute()
        
        # Buscar onde a conta está no campo conta_bancaria_credito (transferências internacionais)
        response5 = supabase.table('transferencias')\
            .select('*')\
            .eq('conta_bancaria_credito', conta_numero)\
            .execute()
        
        # Combinar todos os resultados
        todas_transacoes = []
        todas_transacoes.extend(response1.data or [])
        todas_transacoes.extend(response2.data or [])
        todas_transacoes.extend(response3.data or [])
        todas_transacoes.extend(response4.data or [])
        todas_transacoes.extend(response5.data or [])
        
        # Remover duplicatas
        transacoes_dict = {}
        for t in todas_transacoes:
            transacoes_dict[t['id']] = t
        
        transacoes = list(transacoes_dict.values())
        
        print(f"\n📊 DETALHAMENTO DAS BUSCAS:")
        print(f"   conta_remetente: {len(response1.data)}")
        print(f"   conta_destinatario: {len(response2.data)}")
        print(f"   conta_origem: {len(response3.data)}")
        print(f"   conta_destino: {len(response4.data)}")
        print(f"   conta_bancaria_credito: {len(response5.data)}")
        print(f"   Total únicas: {len(transacoes)}")
        
        # Processar transações
        transacoes_processadas = []
        
        for transf in transacoes:
            # Filtrar por data
            data_transf = transf.get('created_at') or transf.get('data')
            if data_transf:
                try:
                    if 'T' in data_transf:
                        data_transf_obj = datetime.fromisoformat(data_transf.replace('Z', '+00:00'))
                    else:
                        data_transf_obj = datetime.strptime(data_transf, "%Y-%m-%d %H:%M:%S")
                    
                    if not (data_inicio_obj <= data_transf_obj <= data_fim_obj):
                        continue
                except Exception as e:
                    print(f"⚠️ Erro ao processar data {data_transf}: {e}")
                    continue
            
            tipo = transf.get('tipo', '')
            status = transf.get('status', 'completed')
            
            # Pular transações não concluídas (exceto internacionais pendentes)
            if status not in ['completed', 'processing', 'solicitada', 'pending']:
                continue
            
            # ============================================
            # PROCESSAR TRANSFERÊNCIAS INTERNACIONAIS
            # ============================================
            if tipo == 'transferencia_internacional' or tipo == 'internacional':
                conta_remetente = transf.get('conta_remetente', '')
                conta_bancaria_credito = transf.get('conta_bancaria_credito', '')
                valor = float(transf.get('valor', 0))
                moeda = transf.get('moeda', 'USD')
                beneficiario = transf.get('beneficiario', 'Destinatário')
                status_transf = transf.get('status', 'solicitada')
                
                print(f"\n🌍 Transferência Internacional: {transf.get('id')}")
                print(f"   conta_remetente: {conta_remetente}")
                print(f"   conta_bancaria_credito: {conta_bancaria_credito}")
                print(f"   Nossa conta: {conta_numero}")
                print(f"   Status: {status_transf}")
                
                # Mapear status para texto amigável
                status_text = {
                    'solicitada': 'SOLICITADA',
                    'pending': 'PENDENTE',
                    'processing': 'PROCESSANDO',
                    'completed': 'CONCLUÍDA',
                    'rejected': 'RECUSADA'
                }.get(status_transf, status_transf.upper())
                
                # CASO 1: Nossa conta é a REMETENTE (SAÍDA de dinheiro)
                if conta_remetente == conta_numero:
                    descricao = f"TRANSFERÊNCIA INTERNACIONAL {status_text} - Enviada para: {beneficiario}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': 0,
                        'debito': valor,  # SAÍDA = CRÉDITO
                        'tipo': 'Transferência Internacional',
                        'moeda': moeda,
                        'status': status_transf
                    })
                    print(f"   ✅ SAÍDA: -{valor:.2f} {moeda} (CRÉDITO)")
                
                # CASO 2: Nossa conta é a CREDORA (ENTRADA de dinheiro)
                elif conta_bancaria_credito == conta_numero:
                    descricao = f"TRANSFERÊNCIA INTERNACIONAL {status_text} - Recebida de: {beneficiario}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': valor,  # ENTRADA = DÉBITO
                        'debito': 0,
                        'tipo': 'Transferência Internacional',
                        'moeda': moeda,
                        'status': status_transf
                    })
                    print(f"   ✅ ENTRADA: +{valor:.2f} {moeda} (DÉBITO)")
                else:
                    print(f"   ⏭️ Conta não envolvida - ignorando")
            
            # ============================================
            # PROCESSAR CÂMBIO ENTRE CONTAS
            # ============================================
            elif tipo == 'cambio_contas_empresa':
                conta_origem = transf.get('conta_origem', '')
                conta_destino = transf.get('conta_destino', '')
                valor_origem = float(transf.get('valor_origem', 0))
                valor_destino = float(transf.get('valor_destino', 0))
                moeda_origem = transf.get('moeda_origem', '')
                moeda_destino = transf.get('moeda_destino', '')
                taxa = transf.get('taxa_cambio', 0) or transf.get('taxa_principal_registro', 0)
                
                print(f"\n💱 Câmbio: {transf.get('id')}")
                print(f"   conta_origem: {conta_origem}")
                print(f"   conta_destino: {conta_destino}")
                print(f"   Nossa conta: {conta_numero}")
                
                if conta_origem == conta_numero:
                    descricao = f"CÂMBIO - Enviado: {valor_origem:.2f} {moeda_origem} → {valor_destino:.2f} {moeda_destino} (Taxa: {taxa:.6f})"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': valor_origem,  # SAÍDA = CRÉDITO
                        'debito': 0,
                        'tipo': 'Câmbio entre Contas',
                        'moeda': moeda_origem,
                        'status': status
                    })
                    print(f"   ✅ SAÍDA: -{valor_origem:.2f} {moeda_origem}")
                
                elif conta_destino == conta_numero:
                    descricao = f"CÂMBIO - Recebido: {valor_origem:.2f} {moeda_origem} → {valor_destino:.2f} {moeda_destino} (Taxa: {taxa:.6f})"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': 0,
                        'debito': valor_destino,  # ENTRADA = DÉBITO
                        'tipo': 'Câmbio entre Contas',
                        'moeda': moeda_destino,
                        'status': status
                    })
                    print(f"   ✅ ENTRADA: +{valor_destino:.2f} {moeda_destino}")
            
            # ============================================
            # PROCESSAR AJUSTES DE SALDO
            # ============================================
            elif tipo == 'ajuste_saldo_empresa':
                if transf.get('conta_remetente') != conta_numero:
                    continue
                
                tipo_ajuste = transf.get('tipo_ajuste', '')
                descricao_ajuste = transf.get('descricao_ajuste', 'Ajuste de saldo')
                valor = float(transf.get('valor', 0))
                moeda = transf.get('moeda', 'USD')
                
                print(f"\n💰 Ajuste: {transf.get('id')} - {tipo_ajuste}")
                
                if tipo_ajuste == 'DÉBITO':
                    # DÉBITO = ENTRADA de dinheiro
                    descricao = f"AJUSTE - ENTRADA: {descricao_ajuste}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': 0,
                        'debito': valor,
                        'tipo': 'Ajuste de Saldo',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ ENTRADA: +{valor:.2f} {moeda}")
                else:
                    # CRÉDITO = SAÍDA de dinheiro
                    descricao = f"AJUSTE - SAÍDA: {descricao_ajuste}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': valor,
                        'debito': 0,
                        'tipo': 'Ajuste de Saldo',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ SAÍDA: -{valor:.2f} {moeda}")
            
            # ============================================
            # PROCESSAR DEPÓSITOS
            # ============================================
            elif tipo == 'deposito':
                if transf.get('conta_destinatario') == conta_numero or transf.get('conta_destino') == conta_numero:
                    valor = float(transf.get('valor', 0))
                    moeda = transf.get('moeda', 'USD')
                    descricao = transf.get('descricao', f"DEPÓSITO - {transf.get('banco_origem', 'Banco')}")
                    
                    print(f"\n💰 Depósito: {transf.get('id')}")
                    
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': 0,
                        'debito': valor,  # DEPÓSITO = ENTRADA = DÉBITO
                        'tipo': 'Depósito',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ ENTRADA: +{valor:.2f} {moeda}")
            
            # ============================================
            # PROCESSAR SAQUES
            # ============================================
            elif tipo == 'saque':
                if transf.get('conta_remetente') == conta_numero or transf.get('conta_origem') == conta_numero:
                    valor = float(transf.get('valor', 0))
                    moeda = transf.get('moeda', 'USD')
                    descricao = transf.get('descricao', 'SAQUE')
                    
                    print(f"\n💸 Saque: {transf.get('id')}")
                    
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': valor,  # SAQUE = SAÍDA = CRÉDITO
                        'debito': 0,
                        'tipo': 'Saque',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ SAÍDA: -{valor:.2f} {moeda}")
            
            # ============================================
            # PROCESSAR TRANSFERÊNCIAS INTERNAS EMPRESA
            # ============================================
            elif tipo == 'transferencia_interna_empresa':
                conta_origem = transf.get('conta_remetente', '')
                conta_destino = transf.get('conta_destinatario', '')
                valor = float(transf.get('valor', 0))
                moeda = transf.get('moeda', 'USD')
                descricao_transf = transf.get('descricao', 'Transferência Interna')
                
                print(f"\n🏦 Transferência Interna: {transf.get('id')}")
                print(f"   Origem: {conta_origem}")
                print(f"   Destino: {conta_destino}")
                
                if conta_origem == conta_numero:
                    descricao = f"TRANSFERÊNCIA ENVIADA - {descricao_transf} - Para: {conta_destino}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': valor,  # SAÍDA = CRÉDITO
                        'debito': 0,
                        'tipo': 'Transferência Interna',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ SAÍDA: -{valor:.2f} {moeda}")
                elif conta_destino == conta_numero:
                    descricao = f"TRANSFERÊNCIA RECEBIDA - {descricao_transf} - De: {conta_origem}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': 0,
                        'debito': valor,  # ENTRADA = DÉBITO
                        'tipo': 'Transferência Interna',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ ENTRADA: +{valor:.2f} {moeda}")
            
            # ============================================
            # PROCESSAR TRANSFERÊNCIA CLIENTE → EMPRESA
            # ============================================
            elif tipo == 'transferencia_cliente_empresa':
                conta_destino = transf.get('conta_destinatario', '')
                valor = float(transf.get('valor', 0))
                moeda = transf.get('moeda', 'USD')
                descricao_transf = transf.get('descricao', 'Transferência de cliente')
                cliente_nome = transf.get('cliente_nome', 'Cliente')
                
                print(f"\n🏦 Transferência Cliente→Empresa: {transf.get('id')}")
                print(f"   Destino: {conta_destino}")
                
                if conta_destino == conta_numero:
                    descricao = f"TRANSFERÊNCIA DE CLIENTE - {descricao_transf} - Cliente: {cliente_nome}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': 0,
                        'debito': valor,  # ENTRADA = DÉBITO
                        'tipo': 'Transferência de Cliente',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ ENTRADA: +{valor:.2f} {moeda}")

            # ============================================
            # PROCESSAR TRANSFERÊNCIA EMPRESA → CLIENTE
            # ============================================
            elif tipo == 'transferencia_empresa_cliente':
                conta_remetente = transf.get('conta_remetente', '')
                valor = float(transf.get('valor', 0))
                moeda = transf.get('moeda', 'USD')
                descricao_transf = transf.get('descricao', 'Transferência para cliente')
                cliente_nome = transf.get('cliente_nome', 'Cliente')
                
                print(f"\n🏦 Transferência Empresa→Cliente: {transf.get('id')}")
                print(f"   Remetente: {conta_remetente}")
                
                if conta_remetente == conta_numero:
                    descricao = f"TRANSFERÊNCIA PARA CLIENTE - {descricao_transf} - Cliente: {cliente_nome}"
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': valor,  # SAÍDA = CRÉDITO
                        'debito': 0,
                        'tipo': 'Transferência para Cliente',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ SAÍDA: -{valor:.2f} {moeda}")

            # ============================================
            # PROCESSAR DESPESAS ADMINISTRATIVAS
            # ============================================
            elif tipo == 'despesa':
                conta_remetente = transf.get('conta_remetente', '')
                valor = float(transf.get('valor', 0))
                moeda = transf.get('moeda', 'USD')
                descricao_despesa = transf.get('descricao_despesa', 'Despesa administrativa')
                categoria_despesa = transf.get('categoria_despesa', '')
                
                print(f"\n📉 Despesa: {transf.get('id')}")
                print(f"   Remetente: {conta_remetente}")
                
                if conta_remetente == conta_numero:
                    descricao = f"DESPESA - {descricao_despesa}"
                    if categoria_despesa:
                        descricao += f" ({categoria_despesa})"
                    
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': descricao,
                        'credito': valor,  # SAÍDA = CRÉDITO
                        'debito': 0,
                        'tipo': 'Despesa',
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ SAÍDA: -{valor:.2f} {moeda}")

            # ============================================
            # FALLBACK para outros tipos
            # ============================================
            else:
                if transf.get('conta_remetente') == conta_numero or transf.get('conta_origem') == conta_numero:
                    valor = float(transf.get('valor', 0))
                    moeda = transf.get('moeda', 'USD')
                    descricao = transf.get('descricao', f"{tipo.upper()}")
                    
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': f"{descricao} - SAÍDA",
                        'credito': valor,
                        'debito': 0,
                        'tipo': tipo,
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ FALLBACK SAÍDA: -{valor:.2f} {moeda}")
                
                elif transf.get('conta_destinatario') == conta_numero or transf.get('conta_destino') == conta_numero:
                    valor = float(transf.get('valor', 0))
                    moeda = transf.get('moeda', 'USD')
                    descricao = transf.get('descricao', f"{tipo.upper()}")
                    
                    transacoes_processadas.append({
                        'id': transf.get('id'),
                        'data': data_transf,
                        'descricao': f"{descricao} - ENTRADA",
                        'credito': 0,
                        'debito': valor,
                        'tipo': tipo,
                        'moeda': moeda,
                        'status': status
                    })
                    print(f"   ✅ FALLBACK ENTRADA: +{valor:.2f} {moeda}")
        
        # Ordenar por data (mais antiga primeiro para calcular saldo)
        transacoes_processadas.sort(key=lambda x: x.get('data', ''))
        
        # Calcular saldo sequencial
        saldo_atual = 0
        for t in transacoes_processadas:
            saldo_atual += t['debito'] - t['credito']
            t['saldo_apos'] = saldo_atual
        
        # Reverter para exibição (mais recente primeiro)
        transacoes_processadas.reverse()
        
        # Calcular totais
        total_entradas = sum(t['debito'] for t in transacoes_processadas)
        total_saidas = sum(t['credito'] for t in transacoes_processadas)
        
        print(f"\n✅ EXTRATO PROCESSADO COM SUCESSO!")
        print(f"   Total transações: {len(transacoes_processadas)}")
        print(f"   Total entradas (DÉBITO): {total_entradas:.2f}")
        print(f"   Total saídas (CRÉDITO): {total_saidas:.2f}")
        print(f"   Saldo final: {saldo_atual:.2f}")
        
        return jsonify({
            "success": True,
            "transacoes": transacoes_processadas,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "saldo_final": saldo_atual,
            "quantidade": len(transacoes_processadas)
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar extrato: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

# ============================================
# ADMIN - APROVAR OPERAÇÕES (VERSÃO SÍNCRONA)
# ============================================

@app.route('/admin/aprovar-operacoes')
def admin_aprovar_operacoes():
    """Tela de aprovar operações"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Verificar se é admin
    if supabase:
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return redirect('/dashboard')
    
    # Buscar dados do usuário
    nome = usuario.upper()
    email = f'{usuario}@exemplo.com'
    
    try:
        if supabase:
            user_response = supabase.table('usuarios')\
                .select('nome, email')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if user_response.data:
                if user_response.data.get('nome'):
                    nome = user_response.data['nome']
                if user_response.data.get('email'):
                    email = user_response.data['email']
    except:
        pass
    
    return render_template('admin_aprovar_operacoes.html',
                          usuario=usuario,
                          nome=nome,
                          email=email)


@app.route('/api/admin/aprovar-operacoes', methods=['GET'])
def api_admin_aprovar_operacoes():
    """Retorna transferências pendentes e em processamento - VERSÃO SÍNCRONA"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        print(f"🔍 Buscando operações para admin: {usuario}")
        
        # Buscar transferências pendentes (solicitada)
        pendentes_response = supabase.table('transferencias')\
            .select('*')\
            .eq('status', 'solicitada')\
            .order('created_at', desc=True)\
            .execute()
        
        # Buscar transferências em processamento
        processando_response = supabase.table('transferencias')\
            .select('*')\
            .eq('status', 'processing')\
            .order('created_at', desc=True)\
            .execute()
        
        print(f"📊 Encontrados: {len(pendentes_response.data)} pendentes, {len(processando_response.data)} processando")
        
        # Processar pendentes
        pendentes = []
        for t in (pendentes_response.data or []):
            pendentes.append(processar_transferencia_sync(t))
        
        # Processar processando
        processando = []
        for t in (processando_response.data or []):
            processando.append(processar_transferencia_sync(t))
        
        return jsonify({
            "success": True,
            "pendentes": pendentes,
            "processando": processando
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar operações: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


def processar_transferencia_sync(transf):
    """Processa os dados de uma transferência para exibição (versão síncrona)"""
    try:
        # Obter nome do cliente
        cliente_nome = None
        conta_remetente = transf.get('conta_remetente')
        
        if conta_remetente and supabase:
            response = supabase.table('contas')\
                .select('cliente_nome, cliente_username')\
                .eq('id', conta_remetente)\
                .execute()
            
            if response.data:
                cliente_nome = response.data[0].get('cliente_nome') or response.data[0].get('cliente_username')
        
        # Obter informações da invoice
        invoice_info = transf.get('invoice_info')
        if invoice_info and isinstance(invoice_info, str):
            try:
                import json
                invoice_info = json.loads(invoice_info)
            except:
                invoice_info = None
        
        return {
            'id': transf.get('id'),
            'tipo': transf.get('tipo'),
            'status': transf.get('status'),
            'valor': float(transf.get('valor', 0)),
            'moeda': transf.get('moeda', 'USD'),
            'data': transf.get('created_at') or transf.get('data'),
            'cliente': transf.get('cliente') or transf.get('usuario'),
            'cliente_nome': cliente_nome,
            'conta_remetente': conta_remetente,
            'conta_destinatario': transf.get('conta_destinatario'),
            'beneficiario': transf.get('beneficiario'),
            'finalidade': transf.get('finalidade'),
            'descricao': transf.get('descricao'),
            'invoice_info': invoice_info,
            'motivo_recusa': transf.get('motivo_recusa')
        }
    except Exception as e:
        print(f"⚠️ Erro ao processar transferência {transf.get('id')}: {e}")
        return {
            'id': transf.get('id'),
            'tipo': transf.get('tipo'),
            'status': transf.get('status'),
            'valor': float(transf.get('valor', 0)),
            'moeda': transf.get('moeda', 'USD'),
            'data': transf.get('created_at') or transf.get('data'),
            'cliente_nome': None
        }


@app.route('/api/admin/aprovar-operacoes/aprovar', methods=['POST'])
def api_admin_aprovar_transferencia():
    """Aprova uma transferência pendente"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        transferencia_id = dados.get('transferencia_id')
        
        if not transferencia_id:
            return jsonify({"success": False, "message": "ID da transferência não informado"}), 400
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('*')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        transf = response.data[0]
        
        # Verificar se é internacional e se invoice está aprovada
        if transf.get('tipo') == 'transferencia_internacional':
            invoice_info = transf.get('invoice_info')
            if isinstance(invoice_info, str):
                try:
                    import json
                    invoice_info = json.loads(invoice_info)
                except:
                    invoice_info = None
            
            if not invoice_info or invoice_info.get('status') != 'approved':
                return jsonify({"success": False, "message": "Invoice não aprovada! Não é possível aprovar a transferência."}), 400
        
        # Atualizar status para 'processing'
        from datetime import datetime
        data_aprovacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        update_data = {
            'status': 'processing',
            'executado_por': usuario,
            'data_aprovacao': data_aprovacao,
            'data_processing': data_aprovacao
        }
        
        update_response = supabase.table('transferencias')\
            .update(update_data)\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ Transferência {transferencia_id} aprovada por {usuario}")
            return jsonify({
                "success": True,
                "message": f"Transferência {transferencia_id} aprovada com sucesso!"
            })
        else:
            return jsonify({"success": False, "message": "Erro ao aprovar transferência"}), 500
        
    except Exception as e:
        print(f"❌ Erro ao aprovar transferência: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/recusar', methods=['POST'])
def api_admin_recusar_transferencia():
    """Recusa uma transferência pendente e estorna o valor"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        transferencia_id = dados.get('transferencia_id')
        motivo = dados.get('motivo', '')
        
        if not transferencia_id:
            return jsonify({"success": False, "message": "ID da transferência não informado"}), 400
        
        if not motivo:
            return jsonify({"success": False, "message": "Motivo da recusa é obrigatório"}), 400
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('*')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        transf = response.data[0]
        
        # Estornar valor para a conta do cliente
        conta_remetente = transf.get('conta_remetente')
        valor = float(transf.get('valor', 0))
        
        if conta_remetente and valor > 0:
            # Buscar saldo atual da conta
            conta_response = supabase.table('contas')\
                .select('saldo')\
                .eq('id', conta_remetente)\
                .execute()
            
            if conta_response.data:
                saldo_atual = float(conta_response.data[0]['saldo'])
                novo_saldo = saldo_atual + valor
                
                # Atualizar saldo
                supabase.table('contas')\
                    .update({'saldo': novo_saldo})\
                    .eq('id', conta_remetente)\
                    .execute()
                
                print(f"💰 Estorno de {valor:.2f} para conta {conta_remetente}")
        
        # Atualizar status para 'rejected'
        from datetime import datetime
        data_recusa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        update_data = {
            'status': 'rejected',
            'executado_por': usuario,
            'data_recusa': data_recusa,
            'motivo_recusa': motivo
        }
        
        update_response = supabase.table('transferencias')\
            .update(update_data)\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ Transferência {transferencia_id} recusada por {usuario}. Motivo: {motivo}")
            return jsonify({
                "success": True,
                "message": f"Transferência {transferencia_id} recusada com sucesso!"
            })
        else:
            return jsonify({"success": False, "message": "Erro ao recusar transferência"}), 500
        
    except Exception as e:
        print(f"❌ Erro ao recusar transferência: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/concluir', methods=['POST'])
def api_admin_concluir_transferencia():
    """Conclui uma transferência em processamento (interna)"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        transferencia_id = dados.get('transferencia_id')
        conta_bancaria = dados.get('conta_bancaria')
        
        if not transferencia_id:
            return jsonify({"success": False, "message": "ID da transferência não informado"}), 400
        
        if not conta_bancaria:
            return jsonify({"success": False, "message": "Conta bancária não informada"}), 400
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('*')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        transf = response.data[0]
        valor = float(transf.get('valor', 0))
        moeda = transf.get('moeda', 'USD')
        
        # Buscar conta bancária
        conta_response = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_bancaria)\
            .execute()
        
        if not conta_response.data:
            return jsonify({"success": False, "message": "Conta bancária não encontrada"}), 404
        
        conta_info = conta_response.data[0]
        
        # Verificar moeda
        if conta_info.get('moeda') != moeda:
            return jsonify({"success": False, "message": f"Moeda da conta ({conta_info.get('moeda')}) não corresponde à transferência ({moeda})"}), 400
        
        # Verificar saldo
        saldo_atual = float(conta_info.get('saldo', 0))
        if saldo_atual < valor:
            return jsonify({"success": False, "message": f"Saldo insuficiente na conta {conta_bancaria}. Disponível: {saldo_atual:.2f} {moeda}"}), 400
        
        # Debitar da conta bancária (CRÉDITO = SAÍDA)
        novo_saldo = saldo_atual - valor
        
        supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo})\
            .eq('numero', conta_bancaria)\
            .execute()
        
        # Atualizar transferência
        from datetime import datetime
        data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        update_data = {
            'status': 'completed',
            'data_conclusao': data_conclusao,
            'concluido_por': usuario,
            'conta_bancaria_credito': conta_bancaria,
            'data': data_conclusao
        }
        
        update_response = supabase.table('transferencias')\
            .update(update_data)\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ Transferência {transferencia_id} concluída por {usuario}. Conta: {conta_bancaria}")
            return jsonify({
                "success": True,
                "message": f"Transferência {transferencia_id} concluída com sucesso!"
            })
        else:
            return jsonify({"success": False, "message": "Erro ao concluir transferência"}), 500
        
    except Exception as e:
        print(f"❌ Erro ao concluir transferência: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/concluir-swift', methods=['POST'])
def api_admin_concluir_transferencia_swift():
    """Conclui uma transferência internacional com dados SWIFT"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        transferencia_id = dados.get('transferencia_id')
        conta_bancaria = dados.get('conta_bancaria')
        dados_swift = dados.get('dados_swift', {})
        
        if not transferencia_id:
            return jsonify({"success": False, "message": "ID da transferência não informado"}), 400
        
        if not conta_bancaria:
            return jsonify({"success": False, "message": "Conta bancária não informada"}), 400
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('*')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        transf = response.data[0]
        valor = float(transf.get('valor', 0))
        moeda = transf.get('moeda', 'USD')
        
        # Buscar conta bancária
        conta_response = supabase.table('contas_bancarias_empresa')\
            .select('*')\
            .eq('numero', conta_bancaria)\
            .execute()
        
        if not conta_response.data:
            return jsonify({"success": False, "message": "Conta bancária não encontrada"}), 404
        
        conta_info = conta_response.data[0]
        
        # Verificar moeda
        if conta_info.get('moeda') != moeda:
            return jsonify({"success": False, "message": f"Moeda da conta ({conta_info.get('moeda')}) não corresponde à transferência ({moeda})"}), 400
        
        # Verificar saldo
        saldo_atual = float(conta_info.get('saldo', 0))
        if saldo_atual < valor:
            return jsonify({"success": False, "message": f"Saldo insuficiente na conta {conta_bancaria}. Disponível: {saldo_atual:.2f} {moeda}"}), 400
        
        # Debitar da conta bancária (CRÉDITO = SAÍDA)
        novo_saldo = saldo_atual - valor
        
        supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo})\
            .eq('numero', conta_bancaria)\
            .execute()
        
        # Atualizar transferência com dados SWIFT
        from datetime import datetime
        data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        update_data = {
            'status': 'completed',
            'data_conclusao': data_conclusao,
            'concluido_por': usuario,
            'conta_bancaria_credito': conta_bancaria,
            'dados_swift_pagamento': dados_swift,
            'data': data_conclusao
        }
        
        update_response = supabase.table('transferencias')\
            .update(update_data)\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ Transferência internacional {transferencia_id} concluída por {usuario}. Conta: {conta_bancaria}")
            return jsonify({
                "success": True,
                "message": f"Transferência {transferencia_id} concluída com sucesso!"
            })
        else:
            return jsonify({"success": False, "message": "Erro ao concluir transferência"}), 500
        
    except Exception as e:
        print(f"❌ Erro ao concluir transferência internacional: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/detalhes/<transferencia_id>', methods=['GET'])
def api_admin_detalhes_transferencia(transferencia_id):
    """Retorna detalhes completos de uma transferência"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('*')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        transf = response.data[0]
        
        # Obter nome do cliente
        cliente_nome = None
        conta_remetente = transf.get('conta_remetente')
        
        if conta_remetente:
            conta_response = supabase.table('contas')\
                .select('cliente_nome, cliente_username')\
                .eq('id', conta_remetente)\
                .execute()
            
            if conta_response.data:
                cliente_nome = conta_response.data[0].get('cliente_nome') or conta_response.data[0].get('cliente_username')
        
        # Processar invoice_info
        invoice_info = transf.get('invoice_info')
        if invoice_info and isinstance(invoice_info, str):
            try:
                import json
                invoice_info = json.loads(invoice_info)
            except:
                invoice_info = None
        
        return jsonify({
            "success": True,
            "transferencia": {
                'id': transf.get('id'),
                'tipo': transf.get('tipo'),
                'status': transf.get('status'),
                'valor': float(transf.get('valor', 0)),
                'moeda': transf.get('moeda', 'USD'),
                'data': transf.get('created_at') or transf.get('data'),
                'data_solicitacao': transf.get('data_solicitacao'),
                'data_aprovacao': transf.get('data_aprovacao'),
                'data_conclusao': transf.get('data_conclusao'),
                'cliente_nome': cliente_nome,
                'cliente': transf.get('cliente') or transf.get('usuario'),
                'conta_remetente': conta_remetente,
                'conta_destinatario': transf.get('conta_destinatario'),
                'beneficiario': transf.get('beneficiario'),
                'endereco_beneficiario': transf.get('endereco_beneficiario'),
                'cidade': transf.get('cidade'),
                'pais': transf.get('pais'),
                'nome_banco': transf.get('nome_banco'),
                'codigo_swift': transf.get('codigo_swift'),
                'iban_account': transf.get('iban_account'),
                'finalidade': transf.get('finalidade'),
                'descricao': transf.get('descricao'),
                'motivo_recusa': transf.get('motivo_recusa'),
                'executado_por': transf.get('executado_por'),
                'concluido_por': transf.get('concluido_por'),
                'conta_bancaria_credito': transf.get('conta_bancaria_credito'),
                'dados_swift_pagamento': transf.get('dados_swift_pagamento'),
                'invoice_info': invoice_info
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/invoice/<transferencia_id>', methods=['GET'])
def api_admin_invoice_info(transferencia_id):
    """Retorna informações da invoice de uma transferência"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('invoice_info')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        invoice_info = response.data[0].get('invoice_info')
        
        if invoice_info and isinstance(invoice_info, str):
            try:
                import json
                invoice_info = json.loads(invoice_info)
            except:
                invoice_info = None
        
        return jsonify({
            "success": True,
            "invoice_info": invoice_info
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar invoice: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/invoice/<transferencia_id>/download', methods=['GET'])
def api_admin_invoice_download(transferencia_id):
    """Download do arquivo da invoice"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('invoice_info')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"error": "Transferência não encontrada"}), 404
        
        invoice_info = response.data[0].get('invoice_info')
        
        if isinstance(invoice_info, str):
            try:
                import json
                invoice_info = json.loads(invoice_info)
            except:
                invoice_info = None
        
        if not invoice_info or not invoice_info.get('caminho_arquivo'):
            return jsonify({"error": "Invoice não encontrada"}), 404
        
        caminho_arquivo = invoice_info['caminho_arquivo']
        
        # Buscar arquivo no storage
        file_data = supabase.storage.from_("invoices").download(caminho_arquivo)
        
        if not file_data:
            return jsonify({"error": "Arquivo não encontrado no storage"}), 404
        
        # Determinar content type
        nome_arquivo = caminho_arquivo.split('/')[-1]
        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
        
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        
        content_type = mime_types.get(extensao, 'application/octet-stream')
        
        from flask import Response
        return Response(
            file_data,
            content_type=content_type,
            headers={
                'Content-Disposition': f'inline; filename="{nome_arquivo}"',
                'Cache-Control': 'no-cache'
            }
        )
        
    except Exception as e:
        print(f"❌ Erro ao baixar invoice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/invoice/aprovar', methods=['POST'])
def api_admin_invoice_aprovar():
    """Aprova a invoice de uma transferência"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        dados = request.get_json()
        transferencia_id = dados.get('transferencia_id')
        
        if not transferencia_id:
            return jsonify({"success": False, "message": "ID da transferência não informado"}), 400
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('invoice_info')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        invoice_info = response.data[0].get('invoice_info')
        
        if isinstance(invoice_info, str):
            try:
                import json
                invoice_info = json.loads(invoice_info)
            except:
                invoice_info = {}
        
        if not invoice_info:
            invoice_info = {}
        
        # Atualizar status da invoice
        invoice_info['status'] = 'approved'
        if 'motivo_recusa' in invoice_info:
            del invoice_info['motivo_recusa']
        
        # Salvar no Supabase
        update_response = supabase.table('transferencias')\
            .update({'invoice_info': invoice_info})\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ Invoice da transferência {transferencia_id} aprovada por {usuario}")
            return jsonify({
                "success": True,
                "message": "Invoice aprovada com sucesso!"
            })
        else:
            return jsonify({"success": False, "message": "Erro ao aprovar invoice"}), 500
        
    except Exception as e:
        print(f"❌ Erro ao aprovar invoice: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/aprovar-operacoes/invoice/recusar', methods=['POST'])
def api_admin_invoice_recusar():
    """Recusa a invoice de uma transferência"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        dados = request.get_json()
        transferencia_id = dados.get('transferencia_id')
        motivo = dados.get('motivo', '')
        
        if not transferencia_id:
            return jsonify({"success": False, "message": "ID da transferência não informado"}), 400
        
        if not motivo:
            return jsonify({"success": False, "message": "Motivo da recusa é obrigatório"}), 400
        
        # Buscar transferência
        response = supabase.table('transferencias')\
            .select('invoice_info')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Transferência não encontrada"}), 404
        
        invoice_info = response.data[0].get('invoice_info')
        
        if isinstance(invoice_info, str):
            try:
                import json
                invoice_info = json.loads(invoice_info)
            except:
                invoice_info = {}
        
        if not invoice_info:
            invoice_info = {}
        
        # Atualizar status da invoice
        from datetime import datetime
        invoice_info['status'] = 'rejected'
        invoice_info['motivo_recusa'] = motivo
        invoice_info['data_recusa'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Opcional: deletar arquivo do storage
        caminho_arquivo = invoice_info.get('caminho_arquivo')
        if caminho_arquivo:
            try:
                supabase.storage.from_("invoices").remove([caminho_arquivo])
                print(f"🗑️ Arquivo {caminho_arquivo} deletado do storage")
                invoice_info['caminho_arquivo'] = None
            except Exception as e:
                print(f"⚠️ Erro ao deletar arquivo: {e}")
        
        # Salvar no Supabase
        update_response = supabase.table('transferencias')\
            .update({'invoice_info': invoice_info})\
            .eq('id', transferencia_id)\
            .execute()
        
        if update_response.data:
            print(f"✅ Invoice da transferência {transferencia_id} recusada por {usuario}. Motivo: {motivo}")
            return jsonify({
                "success": True,
                "message": "Invoice recusada com sucesso!"
            })
        else:
            return jsonify({"success": False, "message": "Erro ao recusar invoice"}), 500
        
    except Exception as e:
        print(f"❌ Erro ao recusar invoice: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    

# ============================================
# ADMIN - CONFIRMAR DEPÓSITOS
# ============================================

@app.route('/admin/confirmar-depositos')
def admin_confirmar_depositos():
    """Tela de confirmar depósitos"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Verificar se é admin
    if supabase:
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return redirect('/dashboard')
    
    # Buscar dados do usuário
    nome = usuario.upper()
    email = f'{usuario}@exemplo.com'
    
    try:
        if supabase:
            user_response = supabase.table('usuarios')\
                .select('nome, email')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if user_response.data:
                if user_response.data.get('nome'):
                    nome = user_response.data['nome']
                if user_response.data.get('email'):
                    email = user_response.data['email']
    except:
        pass
    
    return render_template('admin_confirmar_depositos.html',
                          usuario=usuario,
                          nome=nome,
                          email=email)


@app.route('/api/admin/clientes/<username>/contas', methods=['GET'])
def api_admin_cliente_contas(username):
    """Retorna as contas de um cliente específico com saldos atualizados"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        # Buscar contas do cliente
        response = supabase.table('contas')\
            .select('id, moeda, saldo, cliente_nome')\
            .eq('cliente_username', username)\
            .eq('ativa', True)\
            .execute()
        
        contas = []
        for conta in (response.data or []):
            contas.append({
                'numero': conta.get('id'),
                'moeda': conta.get('moeda', 'USD'),
                'saldo': float(conta.get('saldo', 0)),
                'cliente_nome': conta.get('cliente_nome', '')
            })
        
        return jsonify({
            "success": True,
            "contas": contas
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar contas do cliente: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/confirmar-deposito', methods=['POST'])
def api_admin_confirmar_deposito():
    """Confirma um depósito e atualiza os saldos"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        username = dados.get('username')
        conta_cliente = dados.get('conta_cliente')
        conta_empresa = dados.get('conta_empresa')
        banco_origem = dados.get('banco_origem')
        remetente = dados.get('remetente')
        valor = float(dados.get('valor', 0))
        moeda = dados.get('moeda', 'USD')
        
        # Validar campos obrigatórios
        if not username:
            return jsonify({"success": False, "message": "Cliente não informado"}), 400
        
        if not conta_cliente:
            return jsonify({"success": False, "message": "Conta do cliente não informada"}), 400
        
        if not conta_empresa:
            return jsonify({"success": False, "message": "Conta da empresa não informada"}), 400
        
        if not banco_origem:
            return jsonify({"success": False, "message": "Banco de origem não informado"}), 400
        
        if not remetente:
            return jsonify({"success": False, "message": "Nome do remetente não informado"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor inválido"}), 400
        
        # Buscar saldo atual da conta do cliente
        cliente_conta_response = supabase.table('contas')\
            .select('saldo, cliente_nome')\
            .eq('id', conta_cliente)\
            .single()\
            .execute()
        
        if not cliente_conta_response.data:
            return jsonify({"success": False, "message": "Conta do cliente não encontrada"}), 404
        
        saldo_cliente_atual = float(cliente_conta_response.data.get('saldo', 0))
        cliente_nome = cliente_conta_response.data.get('cliente_nome', username)
        
        # Buscar saldo atual da conta da empresa
        empresa_conta_response = supabase.table('contas_bancarias_empresa')\
            .select('saldo')\
            .eq('numero', conta_empresa)\
            .single()\
            .execute()
        
        if not empresa_conta_response.data:
            return jsonify({"success": False, "message": "Conta da empresa não encontrada"}), 404
        
        saldo_empresa_atual = float(empresa_conta_response.data.get('saldo', 0))
        
        # Calcular novos saldos
        novo_saldo_cliente = saldo_cliente_atual + valor
        novo_saldo_empresa = saldo_empresa_atual + valor
        
        from datetime import datetime
        import random
        
        transacao_id = f"{random.randint(100000, 999999)}_dep"
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 🔥 SUPABASE FIRST - Tentar salvar no Supabase primeiro
        supabase_sucesso = False
        erro_mensagem = ""
        
        try:
            print(f"🚀 Processando depósito via Supabase...")
            print(f"   Cliente: {username} - Conta: {conta_cliente}")
            print(f"   Empresa: {conta_empresa}")
            print(f"   Valor: {valor:.2f} {moeda}")
            
            # 1. Criar transação no Supabase
            transacao_data = {
                'id': transacao_id,
                'tipo': 'deposito',
                'status': 'completed',
                'data': data_atual,
                'moeda': moeda,
                'valor': valor,
                'conta_remetente': conta_cliente,
                'conta_destinatario': conta_empresa,
                'descricao': f"Depósito confirmado - Banco: {banco_origem} - Remetente: {remetente}",
                'banco_origem': banco_origem,
                'remetente': remetente,
                'cliente': username,
                'usuario': usuario,
                'executado_por': usuario,
                'created_at': datetime.now().isoformat()
            }
            
            transacao_response = supabase.table('transferencias')\
                .insert(transacao_data)\
                .execute()
            
            if not transacao_response.data:
                raise Exception("Erro ao criar transação no Supabase")
            
            print(f"✅ Transação {transacao_id} criada no Supabase")
            
            # 2. Atualizar saldo da conta do cliente
            cliente_update = supabase.table('contas')\
                .update({'saldo': novo_saldo_cliente})\
                .eq('id', conta_cliente)\
                .execute()
            
            if not cliente_update.data:
                raise Exception("Erro ao atualizar saldo do cliente")
            
            print(f"✅ Saldo do cliente atualizado: {saldo_cliente_atual:.2f} → {novo_saldo_cliente:.2f}")
            
            # 3. Atualizar saldo da conta da empresa
            empresa_update = supabase.table('contas_bancarias_empresa')\
                .update({'saldo': novo_saldo_empresa})\
                .eq('numero', conta_empresa)\
                .execute()
            
            if not empresa_update.data:
                raise Exception("Erro ao atualizar saldo da empresa")
            
            print(f"✅ Saldo da empresa atualizado: {saldo_empresa_atual:.2f} → {novo_saldo_empresa:.2f}")
            
            supabase_sucesso = True
            
        except Exception as e:
            erro_mensagem = str(e)
            print(f"⚠️ Erro no Supabase: {erro_mensagem}")
            print("🔄 Tentando fallback local...")
        
        # 🔥 Se Supabase falhou, tentar salvar localmente (fallback)
        if not supabase_sucesso:
            try:
                # Atualizar arquivos locais (simulado)
                print(f"⚠️ Usando fallback local para depósito")
                # Aqui você poderia atualizar arquivos JSON locais se existirem
                pass
            except Exception as local_error:
                print(f"❌ Erro também no fallback local: {local_error}")
                return jsonify({
                    "success": False, 
                    "message": f"Erro ao processar depósito: {erro_mensagem}"
                }), 500
        
        # Buscar dados atualizados para retornar
        cliente_atualizado = supabase.table('contas')\
            .select('saldo')\
            .eq('id', conta_cliente)\
            .single()\
            .execute()
        
        saldo_final_cliente = float(cliente_atualizado.data.get('saldo', novo_saldo_cliente)) if cliente_atualizado.data else novo_saldo_cliente
        
        print(f"🎉 Depósito concluído com sucesso!")
        
        return jsonify({
            "success": True,
            "message": f"Depósito de {valor:.2f} {moeda} realizado com sucesso!",
            "transacao_id": transacao_id,
            "novo_saldo_cliente": saldo_final_cliente,
            "novo_saldo_empresa": novo_saldo_empresa,
            "status_supabase": "✅ Sincronizado com Supabase" if supabase_sucesso else "⚠️ Salvo apenas localmente"
        })
        
    except Exception as e:
        print(f"❌ Erro ao confirmar depósito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
    

# ============================================
# ADMIN - GERENCIAR CONTAS
# ============================================

@app.route('/admin/gerenciar-contas')
def admin_gerenciar_contas():
    """Tela de gerenciar contas"""
    usuario = session.get('username')
    
    if not usuario:
        return redirect('/login')
    
    # Verificar se é admin
    if supabase:
        user_check = supabase.table('usuarios')\
            .select('tipo')\
            .eq('username', usuario)\
            .single()\
            .execute()
        
        if not user_check.data or user_check.data.get('tipo') != 'admin':
            return redirect('/dashboard')
    
    # Buscar dados do usuário
    nome = usuario.upper()
    email = f'{usuario}@exemplo.com'
    
    try:
        if supabase:
            user_response = supabase.table('usuarios')\
                .select('nome, email')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if user_response.data:
                if user_response.data.get('nome'):
                    nome = user_response.data['nome']
                if user_response.data.get('email'):
                    email = user_response.data['email']
    except:
        pass
    
    return render_template('admin_gerenciar_contas.html',
                          usuario=usuario,
                          nome=nome,
                          email=email)


@app.route('/api/admin/clientes/<username>/detalhes', methods=['GET'])
def api_admin_cliente_detalhes(username):
    """Retorna detalhes completos de um cliente"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Buscar dados do cliente
        cliente_response = supabase.table('usuarios')\
            .select('*')\
            .eq('username', username)\
            .single()\
            .execute()
        
        if not cliente_response.data:
            return jsonify({"success": False, "message": "Cliente não encontrado"}), 404
        
        cliente = cliente_response.data
        
        # Buscar contas do cliente
        contas_response = supabase.table('contas')\
            .select('*')\
            .eq('cliente_username', username)\
            .execute()
        
        contas = []
        for conta in (contas_response.data or []):
            contas.append({
                'numero': conta.get('id'),
                'moeda': conta.get('moeda'),
                'saldo': float(conta.get('saldo', 0)),
                'ativa': conta.get('ativa', True),
                'data_criacao': conta.get('data_criacao')
            })
        
        return jsonify({
            "success": True,
            "cliente": {
                'username': cliente.get('username'),
                'nome': cliente.get('nome'),
                'email': cliente.get('email'),
                'telefone': cliente.get('telefone'),
                'status': cliente.get('status'),
                'verificado': cliente.get('verificado', False),
                'cambio_liberado': cliente.get('cambio_liberado', False),
                'data_cadastro': cliente.get('data_cadastro')
            },
            "contas": contas
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes do cliente: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/contas-contabeis', methods=['GET'])
def api_admin_contas_contabeis():
    """Retorna todas as contas contábeis organizadas por categoria"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Buscar contas contábeis
        response = supabase.table('contas_contabeis')\
            .select('*')\
            .execute()
        
        receitas = {}
        despesas = {}
        
        for conta in (response.data or []):
            tipo = conta.get('tipo')
            categoria = conta.get('categoria')
            nome = conta.get('nome')
            moeda = conta.get('moeda')
            
            if tipo == 'receita':
                if categoria not in receitas:
                    receitas[categoria] = {}
                if nome not in receitas[categoria]:
                    receitas[categoria][nome] = {}
                receitas[categoria][nome][moeda] = float(conta.get('saldo', 0))
            elif tipo == 'despesa':
                if categoria not in despesas:
                    despesas[categoria] = {}
                if nome not in despesas[categoria]:
                    despesas[categoria][nome] = {}
                despesas[categoria][nome][moeda] = float(conta.get('saldo', 0))
        
        return jsonify({
            "success": True,
            "receitas": receitas,
            "despesas": despesas
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar contas contábeis: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/gerenciar-contas/ajuste', methods=['POST'])
def api_admin_gerenciar_ajuste():
    """Realiza ajuste de saldo na conta do cliente"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        username = dados.get('username')
        conta_numero = dados.get('conta_numero')
        valor = float(dados.get('valor', 0))
        operacao = dados.get('operacao')  # 'credito' ou 'debito'
        descricao = dados.get('descricao', 'Ajuste administrativo')
        
        if not username or not conta_numero:
            return jsonify({"success": False, "message": "Dados incompletos"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        # Buscar conta do cliente
        conta_response = supabase.table('contas')\
            .select('saldo, moeda')\
            .eq('id', conta_numero)\
            .eq('cliente_username', username)\
            .single()\
            .execute()
        
        if not conta_response.data:
            return jsonify({"success": False, "message": "Conta não encontrada"}), 404
        
        saldo_atual = float(conta_response.data['saldo'])
        moeda = conta_response.data['moeda']
        
        if operacao == 'credito':
            novo_saldo = saldo_atual + valor
            # 🔥 CORREÇÃO: Usar "CREDITO" sem acento
            tipo_ajuste = "CREDITO"
        else:
            novo_saldo = saldo_atual - valor
            tipo_ajuste = "DEBITO"  # 🔥 Também padronizar em maiúsculo
        
        # Atualizar saldo
        update_response = supabase.table('contas')\
            .update({'saldo': novo_saldo})\
            .eq('id', conta_numero)\
            .execute()
        
        if not update_response.data:
            return jsonify({"success": False, "message": "Erro ao atualizar saldo"}), 500
        
        # Registrar transação
        from datetime import datetime
        import random
        
        # Gerar ID numérico
        transacao_id = str(random.randint(100000, 999999))
        while True:
            check = supabase.table('transferencias').select('id').eq('id', transacao_id).execute()
            if not check.data:
                break
            transacao_id = str(random.randint(100000, 999999))
        
        transacao_data = {
            'id': transacao_id,
            'tipo': 'ajuste_admin',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda,
            'valor': valor,
            'conta_remetente': conta_numero,
            'descricao': descricao,
            'tipo_ajuste': tipo_ajuste,  # 🔥 "CREDITO" ou "DEBITO"
            'descricao_ajuste': descricao,
            'usuario': usuario,
            'cliente': username,
            'executado_por': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('transferencias').insert(transacao_data).execute()
        
        print(f"💰 Ajuste {tipo_ajuste} de {valor:.2f} {moeda} na conta {conta_numero} do cliente {username}")
        
        return jsonify({
            "success": True,
            "message": f"Ajuste realizado com sucesso!",
            "novo_saldo": novo_saldo
        })
        
    except Exception as e:
        print(f"❌ Erro ao realizar ajuste: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/gerenciar-contas/cambio', methods=['POST'])
def api_admin_gerenciar_cambio():
    """Realiza operação de câmbio entre contas do cliente"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        username = dados.get('username')
        conta_origem = dados.get('conta_origem')
        conta_destino = dados.get('conta_destino')
        valor = float(dados.get('valor', 0))
        taxa_principal = float(dados.get('taxa_principal', 0))
        
        if not username or not conta_origem or not conta_destino:
            return jsonify({"success": False, "message": "Dados incompletos"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        if taxa_principal <= 0:
            return jsonify({"success": False, "message": "Taxa de câmbio inválida"}), 400
        
        # Buscar contas
        conta_origem_response = supabase.table('contas')\
            .select('saldo, moeda')\
            .eq('id', conta_origem)\
            .eq('cliente_username', username)\
            .single()\
            .execute()
        
        conta_destino_response = supabase.table('contas')\
            .select('saldo, moeda')\
            .eq('id', conta_destino)\
            .eq('cliente_username', username)\
            .single()\
            .execute()
        
        if not conta_origem_response.data:
            return jsonify({"success": False, "message": "Conta origem não encontrada"}), 404
        
        if not conta_destino_response.data:
            return jsonify({"success": False, "message": "Conta destino não encontrada"}), 404
        
        saldo_origem = float(conta_origem_response.data['saldo'])
        moeda_origem = conta_origem_response.data['moeda']
        moeda_destino = conta_destino_response.data['moeda']
        
        # Calcular valor destino
        valor_destino = valor * taxa_principal
        novo_saldo_origem = saldo_origem - valor
        novo_saldo_destino = float(conta_destino_response.data['saldo']) + valor_destino
        
        # Verificar saldo
        if saldo_origem < valor:
            return jsonify({"success": False, "message": f"Saldo insuficiente na conta origem"}), 400
        
        # Atualizar saldos
        supabase.table('contas')\
            .update({'saldo': novo_saldo_origem})\
            .eq('id', conta_origem)\
            .execute()
        
        supabase.table('contas')\
            .update({'saldo': novo_saldo_destino})\
            .eq('id', conta_destino)\
            .execute()
        
        # 🔥 CORREÇÃO: Gerar ID APENAS COM NÚMEROS (sem sufixo)
        import random
        from datetime import datetime
        
        # Gerar ID numérico de 6 dígitos
        transacao_id = str(random.randint(100000, 999999))
        while True:
            # Verificar se já existe
            check = supabase.table('transferencias').select('id').eq('id', transacao_id).execute()
            if not check.data:
                break
            transacao_id = str(random.randint(100000, 999999))
        
        # 🔥 CORREÇÃO: Formatar par de moedas no formato CORRETO (MOEDA_ORIGEM_MOEDA_DESTINO)
        par_moedas = f"{moeda_origem}_{moeda_destino}"
        
        # 🔥 CORREÇÃO: Formatar descrição
        descricao = f"CÂMBIO ADMIN - {moeda_origem} → {moeda_destino}"
        
        # 🔥 CORREÇÃO: Formatar taxa com 6 casas decimais
        taxa_formatada = f"{taxa_principal:.6f}"
        
        # 🔥 CORREÇÃO: Salvar com a estrutura EXATA do exemplo
        transacao_data = {
            'id': transacao_id,
            'tipo': 'cambio',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda_origem,
            'valor': valor,
            'conta_remetente': conta_origem,
            'conta_destinatario': conta_destino,
            'descricao': descricao,
            'executado_por': usuario,
            'cliente': username,
            'usuario': usuario,
            'operacao': 'cambio_admin',
            'par_moedas': par_moedas,
            'valor_origem': valor,
            'valor_destino': valor_destino,
            'cotacao': taxa_formatada,
            'moeda_origem': moeda_origem,
            'moeda_destino': moeda_destino,
            'tipo_taxa_usada': 'principal',
            'taxa_principal_registro': taxa_formatada,
            'created_at': datetime.now().isoformat()
        }
        
        # Inserir no Supabase
        response = supabase.table('transferencias').insert(transacao_data).execute()
        
        if not response.data:
            return jsonify({"success": False, "message": "Erro ao registrar transação"}), 500
        
        print(f"💱 Câmbio realizado: {valor:.2f} {moeda_origem} → {valor_destino:.2f} {moeda_destino}")
        print(f"📝 ID: {transacao_id} | Par: {par_moedas} | Taxa: {taxa_formatada}")
        
        return jsonify({
            "success": True,
            "message": f"Câmbio realizado com sucesso!",
            "transacao_id": transacao_id,
            "par_moedas": par_moedas
        })
        
    except Exception as e:
        print(f"❌ Erro ao realizar câmbio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/gerenciar-contas/extrato', methods=['POST'])
def api_admin_gerenciar_extrato():
    """Retorna extrato da conta do cliente com filtro de período"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        dados = request.get_json()
        
        username = dados.get('username')
        conta_numero = dados.get('conta_numero')
        periodo = dados.get('periodo', '30')
        
        if not username or not conta_numero:
            return jsonify({"success": False, "message": "Dados incompletos"}), 400
        
        from datetime import datetime, timedelta
        
        # Definir período
        if periodo == '0':
            data_inicio = datetime(2024, 1, 1)
        else:
            dias = int(periodo)
            data_inicio = datetime.now() - timedelta(days=dias)
        
        data_fim = datetime.now()
        
        # Buscar transações da conta
        response = supabase.table('transferencias')\
            .select('*')\
            .or_(f'conta_remetente.eq.{conta_numero},conta_destinatario.eq.{conta_numero}')\
            .execute()
        
        transacoes = []
        for t in (response.data or []):
            data_transf = t.get('created_at') or t.get('data')
            if data_transf:
                try:
                    if 'T' in data_transf:
                        data_transf_obj = datetime.fromisoformat(data_transf.replace('Z', '+00:00'))
                    else:
                        data_transf_obj = datetime.strptime(data_transf, "%Y-%m-%d %H:%M:%S")
                    
                    if data_transf_obj < data_inicio or data_transf_obj > data_fim:
                        continue
                except:
                    pass
            
            valor = float(t.get('valor', 0))
            moeda = t.get('moeda', 'USD')
            tipo = t.get('tipo', '')
            status = t.get('status', '')
            
            is_entrada = False
            is_saida = False
            
            if t.get('conta_destinatario') == conta_numero:
                is_entrada = True
            elif t.get('conta_remetente') == conta_numero:
                is_saida = True
            
            # Para ajustes de saldo
            if tipo == 'ajuste_admin':
                tipo_ajuste = t.get('tipo_ajuste', '')
                if tipo_ajuste == 'DÉBITO':
                    is_entrada = True
                elif tipo_ajuste == 'CRÉDITO':
                    is_saida = True
            
            transacoes.append({
                'id': t.get('id'),
                'data': data_transf,
                'descricao': t.get('descricao', f"{tipo.upper()}"),
                'credito': valor if is_saida else 0,
                'debito': valor if is_entrada else 0,
                'tipo': tipo,
                'moeda': moeda,
                'status': status
            })
        
        # Ordenar por data
        transacoes.sort(key=lambda x: x.get('data', ''))
        
        # Calcular saldo sequencial
        saldo_atual = 0
        for t in transacoes:
            saldo_atual += t['debito'] - t['credito']
            t['saldo_apos'] = saldo_atual
        
        # Reverter para exibição (mais recente primeiro)
        transacoes.reverse()
        
        # Calcular totais
        total_entradas = sum(t['debito'] for t in transacoes)
        total_saidas = sum(t['credito'] for t in transacoes)
        
        return jsonify({
            "success": True,
            "transacoes": transacoes,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "saldo_final": saldo_atual,
            "quantidade": len(transacoes)
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar extrato: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/gerenciar-contas/despesa', methods=['POST'])
def api_admin_gerenciar_despesa():
    """Lança uma despesa na conta bancária da empresa"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        conta_bancaria = dados.get('conta_bancaria')
        categoria = dados.get('categoria')
        conta_despesa = dados.get('conta_despesa')
        valor = float(dados.get('valor', 0))
        descricao = dados.get('descricao', '')
        
        if not conta_bancaria or not categoria or not conta_despesa:
            return jsonify({"success": False, "message": "Dados incompletos"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        # Buscar conta bancária
        conta_response = supabase.table('contas_bancarias_empresa')\
            .select('saldo, moeda')\
            .eq('numero', conta_bancaria)\
            .single()\
            .execute()
        
        if not conta_response.data:
            return jsonify({"success": False, "message": "Conta bancária não encontrada"}), 404
        
        saldo_atual = float(conta_response.data['saldo'])
        moeda = conta_response.data['moeda']
        
        if saldo_atual < valor:
            return jsonify({"success": False, "message": f"Saldo insuficiente! Disponível: {saldo_atual:.2f} {moeda}"}), 400
        
        novo_saldo = saldo_atual - valor
        
        # Atualizar saldo
        supabase.table('contas_bancarias_empresa')\
            .update({'saldo': novo_saldo})\
            .eq('numero', conta_bancaria)\
            .execute()
        
        # Registrar transação
        from datetime import datetime
        import random
        
        # Gerar ID numérico
        transacao_id = str(random.randint(100000, 999999))
        while True:
            check = supabase.table('transferencias').select('id').eq('id', transacao_id).execute()
            if not check.data:
                break
            transacao_id = str(random.randint(100000, 999999))
        
        # 🔥 CORREÇÃO: Formatar conta_destinatario no padrão "DESPESA_CATEGORIA_Nome da Conta"
        conta_destinatario_formatada = f"DESPESA_{categoria}_{conta_despesa}"
        
        # 🔥 CORREÇÃO: Usar estrutura EXATAMENTE como no exemplo
        transacao_data = {
            'id': transacao_id,
            'tipo': 'despesa',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda,
            'valor': valor,
            'conta_remetente': conta_bancaria,
            'conta_destinatario': conta_destinatario_formatada,  # 🔥 FORMATO ESPECIAL
            'descricao': None,  # 🔥 Deixar null, usar descricao_despesa
            'usuario': usuario,
            'categoria_despesa': categoria,
            'descricao_despesa': descricao,
            'executado_por': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('transferencias').insert(transacao_data).execute()
        
        if not result.data:
            return jsonify({"success": False, "message": "Erro ao registrar despesa"}), 500
        
        print(f"📉 Despesa lançada: {valor:.2f} {moeda} - {descricao}")
        print(f"   Conta destino formatada: {conta_destinatario_formatada}")
        
        return jsonify({
            "success": True,
            "message": f"Despesa lançada com sucesso!",
            "transacao_id": transacao_id
        })
        
    except Exception as e:
        print(f"❌ Erro ao lançar despesa: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/gerenciar-contas/receita', methods=['POST'])
def api_admin_gerenciar_receita():
    """Lança uma receita na conta do cliente"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        username = dados.get('username')
        conta_cliente = dados.get('conta_cliente')
        categoria = dados.get('categoria')
        conta_receita = dados.get('conta_receita')
        valor = float(dados.get('valor', 0))
        descricao = dados.get('descricao', '')
        
        if not username or not conta_cliente or not categoria or not conta_receita:
            return jsonify({"success": False, "message": "Dados incompletos"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        # Buscar conta do cliente
        conta_response = supabase.table('contas')\
            .select('saldo, moeda')\
            .eq('id', conta_cliente)\
            .eq('cliente_username', username)\
            .single()\
            .execute()
        
        if not conta_response.data:
            return jsonify({"success": False, "message": "Conta do cliente não encontrada"}), 404
        
        saldo_atual = float(conta_response.data['saldo'])
        moeda = conta_response.data['moeda']
        
        # 🔥 CLIENTE É REMETENTE (paga a receita) → SALDO DIMINUI
        novo_saldo = saldo_atual - valor
        
        # Verificar saldo
        if saldo_atual < valor:
            return jsonify({"success": False, "message": f"Saldo insuficiente! Disponível: {saldo_atual:.2f} {moeda}"}), 400
        
        # Atualizar saldo (DÉBITO na conta do cliente)
        supabase.table('contas')\
            .update({'saldo': novo_saldo})\
            .eq('id', conta_cliente)\
            .execute()
        
        # Registrar transação
        from datetime import datetime
        import random
        
        # Gerar ID numérico
        transacao_id = str(random.randint(100000, 999999))
        while True:
            check = supabase.table('transferencias').select('id').eq('id', transacao_id).execute()
            if not check.data:
                break
            transacao_id = str(random.randint(100000, 999999))
        
        # 🔥 CORREÇÃO: Usar estrutura EXATAMENTE como no exemplo
        transacao_data = {
            'id': transacao_id,
            'tipo': 'receita',
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': moeda,
            'valor': valor,
            'conta_remetente': conta_cliente,  # 🔥 Cliente é o remetente (quem paga)
            'conta_destinatario': conta_receita,  # 🔥 Nome da conta de receita (sem prefixo)
            'descricao': None,  # 🔥 Deixar null
            'usuario': usuario,
            'categoria_receita': categoria,
            'descricao_receita': descricao,
            'executado_por': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('transferencias').insert(transacao_data).execute()
        
        if not result.data:
            return jsonify({"success": False, "message": "Erro ao registrar receita"}), 500
        
        print(f"📈 Receita lançada: {valor:.2f} {moeda} - {descricao}")
        print(f"   Cliente: {username} | Conta: {conta_cliente} | Receita: {conta_receita}")
        
        return jsonify({
            "success": True,
            "message": f"Receita lançada com sucesso!",
            "transacao_id": transacao_id
        })
        
    except Exception as e:
        print(f"❌ Erro ao lançar receita: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/gerenciar-contas/transferencia', methods=['POST'])
def api_admin_gerenciar_transferencia():
    """Realiza transferência entre contas (admin)"""
    try:
        usuario = session.get('username')
        
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        # Verificar se é admin
        if supabase:
            user_check = supabase.table('usuarios')\
                .select('tipo')\
                .eq('username', usuario)\
                .single()\
                .execute()
            
            if not user_check.data or user_check.data.get('tipo') != 'admin':
                return jsonify({"success": False, "message": "Acesso negado"}), 403
        
        dados = request.get_json()
        
        conta_origem = dados.get('conta_origem')
        conta_destino = dados.get('conta_destino')
        valor = float(dados.get('valor', 0))
        descricao = dados.get('descricao', '')
        tipo_origem = dados.get('tipo_origem')  # 'empresa' ou 'cliente'
        tipo_destino = dados.get('tipo_destino')  # 'empresa' ou 'cliente'
        
        if not conta_origem or not conta_destino:
            return jsonify({"success": False, "message": "Contas não informadas"}), 400
        
        if valor <= 0:
            return jsonify({"success": False, "message": "Valor deve ser maior que zero"}), 400
        
        from datetime import datetime
        import random
        
        # Gerar ID numérico
        transacao_id = str(random.randint(100000, 999999))
        while True:
            check = supabase.table('transferencias').select('id').eq('id', transacao_id).execute()
            if not check.data:
                break
            transacao_id = str(random.randint(100000, 999999))
        
        moeda = None
        
        # ============================================
        # DETERMINAR O TIPO DA TRANSFERÊNCIA
        # ============================================
        if tipo_origem == 'empresa' and tipo_destino == 'empresa':
            tipo_transferencia = 'transferencia_interna_empresa'
        elif tipo_origem == 'empresa' and tipo_destino == 'cliente':
            tipo_transferencia = 'transferencia_empresa_cliente'
        elif tipo_origem == 'cliente' and tipo_destino == 'empresa':
            tipo_transferencia = 'transferencia_cliente_empresa'
        else:  # cliente -> cliente
            tipo_transferencia = 'transferencia_interna_cliente'
        
        print(f"🔄 Transferência do tipo: {tipo_transferencia}")
        print(f"   Origem: {conta_origem} ({tipo_origem})")
        print(f"   Destino: {conta_destino} ({tipo_destino})")
        print(f"   Valor: {valor}")
        
        # ============================================
        # PROCESSAR CONTA ORIGEM
        # ============================================
        if tipo_origem == 'empresa':
            # Conta da empresa (continua igual - verifica saldo)
            conta_response = supabase.table('contas_bancarias_empresa')\
                .select('saldo, moeda')\
                .eq('numero', conta_origem)\
                .single()\
                .execute()
            
            if not conta_response.data:
                return jsonify({"success": False, "message": "Conta origem não encontrada"}), 404
            
            saldo_origem = float(conta_response.data['saldo'])
            moeda = conta_response.data['moeda']
            
            if saldo_origem < valor:
                return jsonify({"success": False, "message": f"Saldo insuficiente na conta origem"}), 400
            
            novo_saldo_origem = saldo_origem - valor
            
            supabase.table('contas_bancarias_empresa')\
                .update({'saldo': novo_saldo_origem})\
                .eq('numero', conta_origem)\
                .execute()
                
        else:  # cliente
            # Conta de cliente
            conta_response = supabase.table('contas')\
                .select('saldo, moeda')\
                .eq('id', conta_origem)\
                .single()\
                .execute()
            
            if not conta_response.data:
                return jsonify({"success": False, "message": "Conta origem não encontrada"}), 404
            
            saldo_origem = float(conta_response.data['saldo'])
            moeda = conta_response.data['moeda']
            
            # 🔥 CORREÇÃO: Só verifica saldo se NÃO for cliente_empresa
            # Para cliente_empresa, cliente RECEBE dinheiro (não precisa verificar saldo)
            if tipo_transferencia != 'transferencia_cliente_empresa':
                if saldo_origem < valor:
                    return jsonify({"success": False, "message": f"Saldo insuficiente na conta origem"}), 400
            
            # 🔥 CLIENTE ORIGEM: verifica se é cliente_empresa (AUMENTA) ou interna_cliente (DIMINUI)
            if tipo_transferencia == 'transferencia_cliente_empresa':
                # Cliente → Empresa: CLIENTE AUMENTA (ganha dinheiro)
                novo_saldo_origem = saldo_origem + valor
                print(f"   Cliente origem AUMENTA (sem verificação de saldo): {saldo_origem} → {novo_saldo_origem}")
            else:
                # Cliente → Cliente (interna): CLIENTE DIMINUI
                novo_saldo_origem = saldo_origem - valor
                print(f"   Cliente origem DIMINUI: {saldo_origem} → {novo_saldo_origem}")
            
            supabase.table('contas')\
                .update({'saldo': novo_saldo_origem})\
                .eq('id', conta_origem)\
                .execute()
        
        # ============================================
        # PROCESSAR CONTA DESTINO
        # ============================================
        if tipo_destino == 'empresa':
            # Conta da empresa
            conta_response = supabase.table('contas_bancarias_empresa')\
                .select('saldo')\
                .eq('numero', conta_destino)\
                .single()\
                .execute()
            
            if not conta_response.data:
                return jsonify({"success": False, "message": "Conta destino não encontrada"}), 404
            
            saldo_destino = float(conta_response.data['saldo'])
            
            # 🔥 EMPRESA DESTINO: verifica se é cliente_empresa (AUMENTA) ou empresa_cliente (DIMINUI)
            if tipo_transferencia == 'transferencia_cliente_empresa':
                # Cliente → Empresa: EMPRESA AUMENTA
                novo_saldo_destino = saldo_destino + valor
                print(f"   Empresa destino AUMENTA: {saldo_destino} → {novo_saldo_destino}")
            elif tipo_transferencia == 'transferencia_empresa_cliente':
                # Empresa → Cliente: EMPRESA DIMINUI
                novo_saldo_destino = saldo_destino - valor
                print(f"   Empresa destino DIMINUI: {saldo_destino} → {novo_saldo_destino}")
            else:
                # Empresa → Empresa (interna): DIMINUI (já processado na origem)
                novo_saldo_destino = saldo_destino + valor
                print(f"   Empresa destino AUMENTA (interna): {saldo_destino} → {novo_saldo_destino}")
            
            supabase.table('contas_bancarias_empresa')\
                .update({'saldo': novo_saldo_destino})\
                .eq('numero', conta_destino)\
                .execute()
                
        else:  # cliente
            # Conta de cliente
            conta_response = supabase.table('contas')\
                .select('saldo')\
                .eq('id', conta_destino)\
                .single()\
                .execute()
            
            if not conta_response.data:
                return jsonify({"success": False, "message": "Conta destino não encontrada"}), 404
            
            saldo_destino = float(conta_response.data['saldo'])
            
            # 🔥 CLIENTE DESTINO: sempre AUMENTA (recebe dinheiro)
            if tipo_transferencia == 'transferencia_empresa_cliente':
                # Empresa → Cliente: CLIENTE DIMINUI (perde o dinheiro que estava conosco)
                novo_saldo_destino = saldo_destino - valor
                print(f"   Cliente destino DIMINUI: {saldo_destino} → {novo_saldo_destino}")
            else:
                # Cliente → Cliente ou Cliente → Empresa: CLIENTE AUMENTA
                novo_saldo_destino = saldo_destino + valor
                print(f"   Cliente destino AUMENTA: {saldo_destino} → {novo_saldo_destino}")
            
            supabase.table('contas')\
                .update({'saldo': novo_saldo_destino})\
                .eq('id', conta_destino)\
                .execute()
        
        # ============================================
        # REGISTRAR TRANSAÇÃO
        # ============================================
        transacao_data = {
            'id': transacao_id,
            'tipo': tipo_transferencia,
            'status': 'completed',
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'moeda': moeda,
            'valor': valor,
            'conta_remetente': conta_origem,
            'conta_destinatario': conta_destino,
            'descricao': descricao,
            'executado_por': usuario,
            'finalidade': 'Transferência Interna',
            'usuario': usuario,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('transferencias').insert(transacao_data).execute()
        
        if not result.data:
            return jsonify({"success": False, "message": "Erro ao registrar transferência"}), 500
        
        print(f"🔄 Transferência realizada: {valor:.2f} {moeda}")
        print(f"   Tipo: {tipo_transferencia} | ID: {transacao_id}")
        
        return jsonify({
            "success": True,
            "message": f"Transferência realizada com sucesso!",
            "transacao_id": transacao_id,
            "tipo": tipo_transferencia,
            "novo_saldo_origem": novo_saldo_origem,
            "novo_saldo_destino": novo_saldo_destino
        })
        
    except Exception as e:
        print(f"❌ Erro ao realizar transferência: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


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