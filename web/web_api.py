"""
API Web para o Cambio Bank
Versão inicial - apenas endpoints básicos
"""
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from flask import render_template, send_from_directory
from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, session  # ← ADICIONE 'session' AQUI

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
    # ✅ Pega usuário da SESSÃO (correto!)
    usuario = session.get('username')
    
    if not usuario:
        # Se não estiver logado, redireciona para login
        return redirect('/login')
    
    try:
        # Busca dados básicos do usuário
        email = f'{usuario}@exemplo.com'
        nome = usuario.upper()
        
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
    
    # Dados para o template
    dados = {
        'usuario': usuario,
        'email': email,
        'nome': nome
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
        print("🔍 DEBUG - INICIANDO CRIAÇÃO DE TRANSFERÊNCIA")
        print("="*60)
        
        import json
        
        # DEBUG 1: Verificar tipo de requisição
        print(f"📨 Método: {request.method}")
        print(f"📨 Content-Type: {request.content_type}")
        print(f"📨 Tem JSON: {request.is_json}")
        print(f"📨 Tem Form: {request.form}")
        print(f"📨 Tem Files: {request.files}")
        
        # Obter dados da requisição
        dados = {}

        if request.is_json:
            dados = request.json
            print("✅ Dados recebidos como JSON")
        elif request.form:
            dados_json_str = request.form.get('dados', '{}')
            print(f"📦 String JSON do FormData: {dados_json_str}")
            
            dados = json.loads(dados_json_str)
            print("✅ Dados convertidos de FormData JSON")
            
        else:
            print("⚠️ Nenhum dado recebido ou formato desconhecido")
        
        # DEBUG 2: Mostrar TODOS os campos recebidos
        print("\n📋 TODOS OS CAMPOS RECEBIDOS:")
        for campo, valor in dados.items():
            print(f"   {campo}: '{valor}'")
        
        # DEBUG 3: Verificar os 3 CAMPOS PROBLEMÁTICOS
        print("\n🎯 CAMPOS CRÍTICOS VERIFICAÇÃO:")
        campos_criticos = ['endereco_banco', 'cidade_banco', 'pais_banco']
        for campo in campos_criticos:
            valor = dados.get(campo, 'NÃO ENCONTRADO')
            print(f"   {campo}: '{valor}' {'✅' if valor != 'NÃO ENCONTRADO' else '❌'}")
        
        # ✅ PRIMEIRO: Verificar quem está logado (SESSÃO)
        usuario_logado = session.get('username')
        
        if not usuario_logado:
            print(f"❌ USUÁRIO NÃO AUTENTICADO NA SESSÃO")
            return jsonify({
                "success": False,
                "message": "Usuário não autenticado"
            }), 401
        
        # ✅ SEGUNDO: Validar campos obrigatórios (SEM 'usuario' - pegamos da sessão!)
        campos_obrigatorios = ['conta_origem', 'valor', 'moeda', 'beneficiario']
        for campo in campos_obrigatorios:
            if campo not in dados:
                print(f"❌ CAMPO OBRIGATÓRIO FALTANDO: {campo}")
                return jsonify({
                    "success": False,
                    "message": f"Campo '{campo}' é obrigatório"
                }), 400
        
        # ✅ TERCEIRO: Se vier 'usuario' nos dados, IGNORAR e usar o da sessão
        if 'usuario' in dados:
            print(f"⚠️  Campo 'usuario' recebido nos dados: '{dados['usuario']}' - Usando da sessão: '{usuario_logado}'")
        
        # ✅ QUARTO: Sobrescrever com usuário da sessão (SEGURANÇA!)
        dados['usuario'] = usuario_logado
        print(f"✅ Usuário da transferência definido como: {usuario_logado}")
            
        # Buscar saldo atual da conta E verificar se pertence ao usuário
        print(f"🔍 Buscando conta: {dados['conta_origem']} para usuário: {usuario_logado}")

        response_conta = supabase.table('contas')\
            .select('id, saldo, cliente_username, moeda')\
            .eq('id', dados['conta_origem'])\
            .eq('cliente_username', usuario_logado)\
            .eq('ativa', True)\
            .execute()

        if not response_conta.data:
            print(f"❌ Conta não encontrada ou não pertence ao usuário: {dados['conta_origem']}")
            return jsonify({
                "success": False,
                "message": "Conta de origem não encontrada ou não autorizada"
            }), 400

        conta = response_conta.data[0]
        saldo_atual = float(conta['saldo']) if conta['saldo'] else 0.0
        
        print(f"✅ Conta encontrada: ID {conta['id']}, Moeda: {conta.get('moeda', 'N/A')}, Saldo: {saldo_atual}")
        
        # ✅ GARANTIR que a moeda da conta bate com a moeda da transferência
        if 'moeda' in conta and conta['moeda'] != dados['moeda']:
            print(f"❌ Moeda da conta ({conta['moeda']}) diferente da transferência ({dados['moeda']})")
            return jsonify({
                "success": False,
                "message": f"Moeda da conta ({conta['moeda']}) não corresponde à moeda da transferência ({dados['moeda']})"
            }), 400
        valor_transferencia = float(dados['valor'])

        print(f"💰 Saldo atual: {saldo_atual}, Valor transferência: {valor_transferencia}") 

        # Verificar saldo suficiente
        if valor_transferencia > saldo_atual:
            print(f"❌ Saldo insuficiente! Disponível: {saldo_atual}, Necessário: {valor_transferencia}")
            return jsonify({
                "success": False,
                "message": f"Saldo insuficiente! Disponível: {saldo_atual:.2f}"
            }), 400         
        
        # Criar ID único
        import random
        from datetime import datetime
        transferencia_id = f"{random.randint(100000, 999999)}"
        
        # 🔍 DEFINIR 'agora' AQUI
        agora = datetime.now()
        
        # 8. Preparar dados para Supabase
        dados_supabase = {
            'id': transferencia_id,
            'tipo': 'transferencia_internacional',
            'status': 'solicitada',
            'data': agora.strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': dados['moeda'],
            'valor': valor_transferencia,  # ← CORRIGIDO
            'conta_remetente': dados['conta_origem'],  # ← CORRIGIDO
            'descricao': dados.get('descricao', ''),
            'usuario': usuario_logado,  # ← CORRIGIDO
            'cliente': usuario_logado,  # ← CORRIGIDO
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
            'solicitado_por': usuario_logado  # ← CORRIGIDO
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
            
            # DEBUG 5: Verificar dados salvos
            print(f"\n📊 VERIFICANDO DADOS SALVOS NO SUPABASE:")
            check = supabase.table('transferencias').select('endereco_banco, cidade_banco, pais_banco').eq('id', transferencia_id).execute()
            if check.data:
                saved = check.data[0]
                print(f"   endereco_banco salvo: '{saved.get('endereco_banco', 'VAZIO')}'")
                print(f"   cidade_banco salvo: '{saved.get('cidade_banco', 'VAZIO')}'")
                print(f"   pais_banco salvo: '{saved.get('pais_banco', 'VAZIO')}'")
            
            # Upload de arquivo se existir
            if 'invoice' in request.files:
                arquivo = request.files['invoice']
                if arquivo and arquivo.filename:
                    try:
                        caminho = f"transferencias/{transferencia_id}/{arquivo.filename}"
                        arquivo_bytes = arquivo.read()
                        
                        print(f"📎 Upload de invoice: {arquivo.filename}")
                        
                        # Upload para bucket 'documentos'
                        supabase.storage.from_("invoices").upload(
                            caminho,
                            arquivo_bytes,
                            file_options={"content-type": arquivo.content_type}
                        )
                        print(f"✅ Invoice salvo no Storage: {caminho}")
                        
                        # Atualizar transferência com info do invoice
                        supabase.table('transferencias').update({
                            'invoice_info': {
                                'caminho_arquivo': caminho,
                                'nome_arquivo': arquivo.filename,
                                'tipo': arquivo.content_type,
                                'tamanho': len(arquivo_bytes),
                                'status': 'pending',
                                'data_upload': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'motivo_recusa': ''
                            }
                        }).eq('id', transferencia_id).execute()
                        
                    except Exception as upload_error:
                        print(f"⚠️ Erro no upload do arquivo: {upload_error}")
            
            print("="*60)
            print("🎉 TRANSFERÊNCIA FINALIZADA COM SUCESSO")
            print("="*60 + "\n")
            
            return jsonify({
                "success": True,
                "message": "Transferência solicitada com sucesso!",
                "transferencia_id": transferencia_id
            })
        else:
            print(f"❌ ERRO: Nenhum dado retornado do Supabase")
            print(f"❌ Response: {response}")
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
            # Listar beneficiários do usuário
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
    
@app.route('/api/transferencias/<transferencia_id>/invoice')
def download_invoice(transferencia_id):
    """Download da invoice do Supabase Storage - VERSÃO CORRIGIDA"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    print(f"📄 [INVOICE] Buscando invoice para transferência {transferencia_id}")
    
    try:
        # 1. VERIFICAR PERMISSÃO
        response = supabase.table('transferencias')\
            .select('id, cliente, usuario, invoice_info')\
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
        
        print(f"✅ Usuário autorizado")
        
        # 2. VERIFICAR SE TEM INVOICE
        invoice_info = transferencia.get('invoice_info')
        if not invoice_info:
            return jsonify({'error': 'Nenhuma invoice encontrada'}), 404
        
        # 3. OBTER CAMINHO
        caminho_arquivo = invoice_info.get('caminho_arquivo')
        if not caminho_arquivo:
            return jsonify({'error': 'Caminho do arquivo não configurado'}), 404
        
        print(f"📄 Caminho: {caminho_arquivo}")
        
        # 4. VERIFICAR STATUS
        invoice_status = invoice_info.get('status', 'pending')
        if invoice_status not in ['approved', 'rejected']:
            return jsonify({'error': f'Invoice com status {invoice_status}'}), 403
        
        # 5. 🔥 BAIXAR DO STORAGE - VERSÃO CORRETA
        print(f"⬇️  Baixando: {caminho_arquivo}")
        
        # ⚠️ IMPORTANTE: Use supabase.storage (NÃO supabase.client.storage)
        response_storage = supabase.storage.from_("invoices").download(caminho_arquivo)
        
        if response_storage is None:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        print(f"✅ Baixado! Tamanho: {len(response_storage)} bytes")
        
        # 6. DETERMINAR TIPO DO ARQUIVO
        nome_arquivo = caminho_arquivo.split('/')[-1]
        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
        
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        
        content_type = mime_types.get(extensao, 'application/octet-stream')
        
        # 7. RETORNAR ARQUIVO
        from flask import Response
        return Response(
            response_storage,
            content_type=content_type,
            headers={
                'Content-Disposition': f'inline; filename="{nome_arquivo}"',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ROTA ALTERNATIVA PARA VERIFICAR DISPONIBILIDADE DA INVOICE
@app.route('/api/transferencias/<transferencia_id>/invoice/status')
def check_invoice_status(transferencia_id):
    """Verifica status da invoice sem baixar o arquivo"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    
    try:
        response = supabase.table('transferencias')\
            .select('invoice_info, cliente, usuario')\
            .eq('id', transferencia_id)\
            .execute()
        
        if not response.data:
            return jsonify({'available': False, 'error': 'Transferência não encontrada'}), 404
        
        transferencia = response.data[0]
        
        # Verificar permissão
        usuario_permitido = (
            transferencia.get('cliente') == usuario_nome or
            transferencia.get('usuario') == usuario_nome
        )
        
        if not usuario_permitido:
            return jsonify({'available': False, 'error': 'Acesso não autorizado'}), 403
        
        invoice_info = transferencia.get('invoice_info')
        if not invoice_info:
            return jsonify({'available': False, 'error': 'Nenhuma invoice encontrada'})
        
        return jsonify({
            'available': True,
            'status': invoice_info.get('status', 'pending'),
            'filename': invoice_info.get('caminho_arquivo', '').split('/')[-1] if invoice_info.get('caminho_arquivo') else '',
            'upload_date': invoice_info.get('data_upload', ''),
            'rejection_reason': invoice_info.get('motivo_recusa', '')
        })
        
    except Exception as e:
        return jsonify({'available': False, 'error': str(e)}), 500
    
@app.route('/api/transferencias/<transferencia_id>/invoice/reenviar', methods=['POST'])
def reenviar_invoice(transferencia_id):
    """Reenvia/atualiza uma invoice recusada"""
    
    if 'username' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario_nome = session['username']
    print(f"📤 [REENVIAR INVOICE] Iniciando para transferência {transferencia_id}")
    
    try:
        # 1. VERIFICAR SE A TRANSFERÊNCIA EXISTE E TEM PERMISSÃO
        response = supabase.table('transferencias')\
            .select('id, cliente, usuario, invoice_info')\
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
        
        # 2. VERIFICAR SE A INVOICE ESTÁ RECUSADA (só pode reenviar se recusada)
        invoice_info = transferencia.get('invoice_info') or {}
        current_status = invoice_info.get('status', 'pending')
        
        if current_status != 'rejected':
            return jsonify({
                'error': f'Não é possível reenviar invoice com status {current_status}',
                'current_status': current_status
            }), 400
        
        motivo_recusa_anterior = invoice_info.get('motivo_recusa', '')
        
        # 3. VERIFICAR SE TEM ARQUIVO NO UPLOAD
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['file']
        
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # 4. VALIDAR O ARQUIVO
        nome_arquivo = arquivo.filename
        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
        
        extensoes_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
        if extensao not in extensoes_permitidas:
            return jsonify({
                'error': f'Extensão não permitida: .{extensao}',
                'permitidas': extensoes_permitidas
            }), 400
        
        # Verificar tamanho (limite de 5MB)
        arquivo.seek(0, 2)  # Ir para o final
        tamanho = arquivo.tell()
        arquivo.seek(0)  # Voltar ao início
        
        if tamanho > 5 * 1024 * 1024:  # 5MB
            return jsonify({'error': 'Arquivo muito grande. Máximo: 5MB'}), 400
        
        print(f"📁 Arquivo validado: {nome_arquivo} ({tamanho} bytes, .{extensao})")
        
        # 5. CRIAR CAMINHO ÚNICO NO SUPABASE STORAGE
        import time
        timestamp = int(time.time() * 1000)
        nome_base = nome_arquivo.rsplit('.', 1)[0]
        novo_nome = f"{transferencia_id}_{timestamp}_{nome_base}.{extensao}"
        caminho_supabase = f"transferencias/{transferencia_id}/{novo_nome}"
        
        print(f"📤 Enviando para: {caminho_supabase}")
        
        # 6. FAZER UPLOAD PARA O SUPABASE STORAGE
        arquivo_bytes = arquivo.read()
        
        upload_response = supabase.storage.from_("invoices")\
            .upload(caminho_supabase, arquivo_bytes)
        
        if upload_response is None:
            return jsonify({'error': 'Erro ao fazer upload para o storage'}), 500
        
        print(f"✅ Upload realizado com sucesso!")
        
        # 7. ATUALIZAR A TRANSFERÊNCIA COM NOVA INVOICE INFO
        nova_invoice_info = {
            'status': 'pending',  # Volta para pendente
            'data_upload': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'motivo_recusa': '',  # Limpa o motivo anterior
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
            print(f"✅ Invoice info atualizada no banco de dados")
            
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
        print(f"❌ [REENVIAR INVOICE] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    
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