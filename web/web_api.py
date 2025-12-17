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
import re
import requests
import datetime
import threading
from datetime import timezone           

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
    """Exporta extrato para PDF (mesma lógica do Kivy)"""
    try:
        usuario = session.get('username')
        if not usuario:
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        
        dados = request.get_json()
        
        # 🔥 IMPLEMENTAR GERAÇÃO DE PDF AQUI
        # Você pode usar a mesma biblioteca PDF do Kivy ou outra
        
        # Por enquanto, retornar URL fictícia
        pdf_url = "/static/extratos/extrato_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf"
        
        return jsonify({
            "success": True,
            "pdf_url": pdf_url,
            "message": "PDF gerado com sucesso"
        })
        
    except Exception as e:
        print(f"❌ Erro em exportar_extrato_pdf: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

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

                    # 🔥 DEBUG ESPECÍFICO PARA 850030
                    if str(transf_id) == '850030':
                        print(f"\n🎯🎯🎯 DEBUG 850030 - SEÇÃO REMETENTE 🎯🎯🎯")
                        print(f"   Tipo: {transf_tipo}")
                        print(f"   Status: {transf_status}")
                        print(f"   Conta remetente: {transf.get('conta_remetente')}")
                        print(f"   Conta destinatario: {transf.get('conta_destinatario')}")
                        print(f"   Nossa conta: {conta_num}")
                        print(f"   É remetente? {transf.get('conta_remetente') == conta_num}")
                        print(f"   É destinatário? {transf.get('conta_destinatario') == conta_num}")
                        print(f"   Vai entrar na seção REMETENTE? SIM")

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

                    # 🔥 CORREÇÃO CRÍTICA: TRANSFERÊNCIA INTERNA CLIENTE (TIPO ESPECIAL)
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
                            solicitação_dentro = (
                                data_solicitacao and 
                                data_inicio_filtro <= data_solicitacao <= data_fim_filtro
                            )
                            estorno_dentro = (
                                data_estorno and 
                                data_inicio_filtro <= data_estorno <= data_fim_filtro
                            )
                            
                            # 🔥 CASO 1: Solicitação DENTRO + Estorno DENTRO → mostrar AMBAS
                            if solicitação_dentro and estorno_dentro:
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
                            elif solicitação_dentro and not estorno_dentro:
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
                            elif not solicitação_dentro and estorno_dentro:
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
                            
                            # DEBUG
                            print(f"💰 ESTORNO CRIADO: {descricao_credito} | +{valor:,.2f}")
                            
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
                    
                    # 🔥 OUTROS TIPOS DE TRANSAÇÕES (quando cliente é destinatário em transferências normais)
                    elif transf_tipo not in ['ajuste_admin', 'deposito', 'cambio']:
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
    """MESMA LÓGICA DO KIVY: Retorna 1 MOEDA_ESQUERDA = X MOEDA_DIREITA"""
    try:
        moeda_esquerda = par_moedas[:3]  # BRL em BRL_USD
        moeda_direita = par_moedas[4:]   # USD em BRL_USD
        
        # 🔥 VERIFICAR CACHE (igual ao Kivy)
        global ultima_atualizacao
        cache_key = f"{par_moedas}_simple"
        
        with cotacao_lock:
            if (ultima_atualizacao and 
                (datetime.datetime.now() - ultima_atualizacao).seconds < 30 and
                cache_key in cotacoes_cache):
                print(f"📊 Retornando cotação do cache: {cotacoes_cache[cache_key]}")
                return cotacoes_cache[cache_key]
            
            # 🔥 API REAL (MESMA DO KIVY: economia.awesomeapi.com.br)
            print(f"🌐 Buscando cotação REAL: {moeda_esquerda}-{moeda_direita}")
            url_direto = f"https://economia.awesomeapi.com.br/json/last/{moeda_esquerda}-{moeda_direita}"
            
            try:
                response = requests.get(url_direto, timeout=10)
                
                if response.status_code == 200:
                    dados = response.json()
                    chave_direta = f"{moeda_esquerda}{moeda_direita}"
                    
                    if chave_direta in dados:
                        cotacao = float(dados[chave_direta]['bid'])
                        print(f"✅ Cotação DIRETA {par_moedas}: 1 {moeda_esquerda} = {cotacao} {moeda_direita}")
                        
                        # Cache
                        cotacoes_cache[cache_key] = cotacao
                        ultima_atualizacao = datetime.datetime.now()
                        return cotacao
            except Exception as api_error:
                print(f"⚠️ Erro na API direta: {api_error}")
            
            # 🔥 TENTAR INVERTIDO (igual ao Kivy)
            print(f"🔄 Tentando API invertido: {moeda_direita}-{moeda_esquerda}")
            url_invertido = f"https://economia.awesomeapi.com.br/json/last/{moeda_direita}-{moeda_esquerda}"
            
            try:
                response = requests.get(url_invertido, timeout=10)
                
                if response.status_code == 200:
                    dados = response.json()
                    chave_invertida = f"{moeda_direita}{moeda_esquerda}"
                    
                    if chave_invertida in dados:
                        cotacao_invertida = float(dados[chave_invertida]['bid'])
                        cotacao = 1 / cotacao_invertida  # 🔥 INVERTEMOS MATEMATICAMENTE
                        print(f"✅ Cotação INVERTIDA {par_moedas}: 1 {moeda_esquerda} = {cotacao} {moeda_direita}")
                        
                        # Cache
                        cotacoes_cache[cache_key] = cotacao
                        ultima_atualizacao = datetime.datetime.now()
                        return cotacao
            except Exception as api_error:
                print(f"⚠️ Erro na API invertida: {api_error}")
        
        # Fallback: buscar do Supabase (se existir)
        print(f"🔄 Fallback: buscando cotação no Supabase")
        try:
            if supabase:
                response = supabase.table('config_cotacoes')\
                    .select('valor_config')\
                    .eq('tipo_config', 'cotacao')\
                    .eq('par_moeda', par_moedas)\
                    .order('data_atualizacao', desc=True)\
                    .limit(1)\
                    .execute()
                
                if response.data:
                    cotacao_supabase = float(response.data[0]['valor_config'])
                    print(f"✅ Cotação do Supabase: {cotacao_supabase}")
                    return cotacao_supabase
        except Exception as supabase_error:
            print(f"⚠️ Erro ao buscar no Supabase: {supabase_error}")
        
        print(f"❌ Nenhuma cotação encontrada, retornando 1.0")
        return 1.0
        
    except Exception as e:
        print(f"❌ Erro crítico em obter_cotacao_simples: {e}")
        import traceback
        traceback.print_exc()
        return 1.0

def obter_spread_cliente(usuario, par_moedas):
    """Obtém spread configurado para o cliente (igual ao Kivy)"""
    try:
        if not supabase:
            print("⚠️ Supabase não disponível para buscar spread")
            return {'compra': 0.5, 'venda': 0.5}
        
        # 🔥 BUSCAR SPREAD NO SUPABASE
        # Primeiro tentar buscar do cliente específico
        response = supabase.table('config_cotacoes')\
            .select('valor_config')\
            .eq('tipo_config', 'spread')\
            .eq('cliente_username', usuario)\
            .eq('par_moeda', par_moedas)\
            .order('data_atualizacao', desc=True)\
            .limit(1)\
            .execute()
        
        if response.data:
            spread_valor = float(response.data[0]['valor_config'])
            print(f"✅ Spread específico encontrado: {spread_valor}%")
            return {'compra': spread_valor, 'venda': spread_valor}
        
        # 🔥 Se não encontrar, buscar spread padrão do sistema
        response_padrao = supabase.table('config_sistema')\
            .select('valor')\
            .eq('chave', 'spread_padrao')\
            .single()\
            .execute()
        
        if response_padrao.data:
            spread_padrao = float(response_padrao.data['valor'])
            print(f"✅ Spread padrão encontrado: {spread_padrao}%")
            return {'compra': spread_padrao, 'venda': spread_padrao}
        
        # 🔥 Fallback: 0.5% (igual ao Kivy)
        print(f"⚠️ Nenhum spread encontrado, usando padrão 0.5%")
        return {'compra': 0.5, 'venda': 0.5}
        
    except Exception as e:
        print(f"⚠️ Erro ao obter spread: {e}")
        return {'compra': 0.5, 'venda': 0.5}

def verificar_horario_comercial(usuario=None):
    """Verifica horário comercial EXATAMENTE como o Kivy"""
    try:
        # Obter horário atual (Brasília)
        agora_utc = datetime.datetime.now(timezone.utc)
        offset_brasilia = -3  # UTC-3 para Brasília
        hora_brasilia = (agora_utc.hour + offset_brasilia) % 24
        
        agora_brasilia = agora_utc.replace(hour=hora_brasilia, 
                                         minute=agora_utc.minute, 
                                         second=agora_utc.second)
        
        print(f"📅 Verificação horário para {usuario}:")
        print(f"   Hora Brasília: {agora_brasilia.strftime('%H:%M')}")
        
        # 🔥 BUSCAR HORÁRIO DO CLIENTE NO SUPABASE (se existir)
        # Por enquanto usar horário padrão: Seg-Sex 09:00-18:00
        dias_semana = [0, 1, 2, 3, 4]  # Segunda(0) a Sexta(4)
        inicio = "09:00"
        fim = "18:00"
        
        # Verificar dia da semana
        dia_atual = agora_brasilia.weekday()  # 0=Segunda
        
        if dia_atual not in dias_semana:
            print(f"   ❌ Fora do horário: dia {dia_atual} não permitido")
            dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            dias_permitidos = [dias_nomes[d] for d in dias_semana]
            return False, f"Fora do horário comercial. Disponível apenas: {', '.join(dias_permitidos)}"
        
        # Verificar horário
        hora_atual = agora_brasilia.strftime('%H:%M')
        
        if hora_atual < inicio:
            print(f"   ❌ Fora do horário: {hora_atual} < {inicio}")
            return False, f"Fora do horário comercial. Disponível a partir das {inicio}"
        elif hora_atual > fim:
            print(f"   ❌ Fora do horário: {hora_atual} > {fim}")
            return False, f"Fora do horário comercial. Disponível até às {fim}"
        
        print(f"   ✅ Dentro do horário comercial")
        return True, "Dentro do horário comercial"
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar horário: {e}")
        # Fail-open (permitir em caso de erro) - igual ao Kivy
        return True, "Horário verificado com ressalvas"


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
    """API para obter limite operacional do cliente"""
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        if supabase:
            # 🔥 BUSCAR LIMITE NO SUPABASE
            response = supabase.table('config_sistema')\
                .select('valor')\
                .eq('chave', 'limite_operacional')\
                .single()\
                .execute()
            
            if response.data:
                limite = float(response.data['valor'])
            else:
                limite = 10000.00  # Default
        else:
            limite = 10000.00  # Default
        
        return jsonify({
            'success': True,
            'limite': limite,
            'usuario': usuario
        })
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar limite: {e}")
        return jsonify({
            'success': True,
            'limite': 10000.00,  # Fallback
            'usuario': usuario
        })

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