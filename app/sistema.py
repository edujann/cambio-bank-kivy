from kivy.app import App
from supabase_manager import SupabaseManager
import threading
import json

import os
from dotenv import load_dotenv
from supabase import create_client

# Configurar Supabase
load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

import hashlib
import os
import datetime
import random
import string
import time

class SistemaCambioPremium:

    def __init__(self):
        # 🔥🔥🔥 ORDEM CORRETA DE INICIALIZAÇÃO:
        self.supabase = SupabaseManager()
        self.usuarios = {}
        self.contas = {}
        self.transferencias = {}
        self.beneficiarios = {}
        
        # 🔥 PRIMEIRO: Inicializar taxas_cambio
        self.taxas_cambio = {
            'USD_BRL': 5.20,
            'BRL_USD': 0.19,
            'EUR_BRL': 5.60,
            'BRL_EUR': 0.18,
            'USD_EUR': 0.92,
            'EUR_USD': 1.09,
            'GBP_BRL': 6.50,
            'BRL_GBP': 0.15,
            'USD_GBP': 0.79,
            'GBP_USD': 1.27,
            'EUR_GBP': 0.86,
            'GBP_EUR': 1.16
        }
        
        # 🔥 DEPOIS: Inicializar configuracoes (que usa taxas_cambio)
        self.configuracoes = self.configuracoes_padrao()
        
        # 🔥 🔥 🔥 ESTRUTURA CONTÁBIL MULTI-MOEDA (SERÁ CARREGADA DO SUPABASE)
        self.contas_contabeis = {
            'receitas': {},
            'despesas': {}
        }
        
        # CONTA DE AJUSTE DE SALDO
        self.contas['999999999'] = {
            'numero': '999999999',
            'cliente_nome': 'CONTA AJUSTE SALDO',
            'cliente_id': 'sistema',
            'moeda': 'USD',
            'saldo': 0.0,
            'tipo': 'sistema',
            'data_criacao': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 🔥 🔥 🔥 NOVO: INICIALIZAR CONTAS BANCÁRIAS COM SALDO ZERO
        self.inicializar_contas_bancarias_empresa()

        # 🔥🔥🔥 MUDANÇA CRÍTICA: Carregar apenas dados ESSENCIAIS primeiro
        self.carregar_dados_essenciais()
        
        self.usuario_logado = None   
        
        # 🔥 NOVAS ESTRUTURAS PARA CÂMBIO - AGORA INICIALIZADAS APÓS carregar_dados()
        self.spreads_clientes = {}  # ✅ INICIALIZA VAZIO - Supabase vai preencher
        self.permissoes_cambio = {} # ✅ INICIALIZA VAZIO - Supabase vai preencher
        self.limites_operacionais = {} # ✅ INICIALIZA VAZIO - Supabase vai preencher
        self.horarios_clientes = {}  # 🔥 ADICIONAR ESTA LINHA
        self.horario_comercial_padrao = {  # 🔥 ADICIONAR ESTA LINHA
            'dias_semana': [0, 1, 2, 3, 4],
            'inicio': '10:00',
            'fim': '15:00',
            'fuso_horario': 'America/Sao_Paulo'
        }
        
        # 🔥 ADICIONAR: Lock para sincronizar consultas
        self.cotacao_lock = threading.Lock()
        
        # Taxas padrão para novos clientes
        self.spread_padrao = 0.5
    
        # Cache para cotações da API
        self.cotacoes_cache = {}
        self.ultima_atualizacao = None 

        # 🔥 VERIFICAR SE ESTÁ CHAMANDO O MÉTODO
        print("🎯 INICIANDO CARREGAMENTO DE BENEFICIÁRIOS...")
        self.carregar_beneficiarios()
        print(f"🎯 BENEFICIÁRIOS CARREGADOS: {len(self.beneficiarios)} usuários")  

        # 🔥 FORÇAR CARREGAMENTO DAS CONTAS CONTÁBEIS
        print("🎯 INICIANDO CARREGAMENTO DAS CONTAS CONTÁBEIS...")
        self.carregar_contas_contabeis_forcado()
        
        # 🔥 MUDANÇA CRÍTICA: NÃO chamar carregar_dados() novamente aqui
        # self.carregar_dados()  # ← REMOVER ESTA LINHA
        
        # 🔥 FORÇAR CARREGAMENTO DE COTAÇÕES NO __init__
        print("🔍 INICIANDO SISTEMA - CARREGANDO COTAÇÕES")
        self.carregar_dados_cotacoes()  # ← ESTE MÉTODO JÁ CARREGA OS HORÁRIOS
        
        # Debug do estado
        self.debug_estado_cotacoes()

        # 🔥 NOVAS ESTRUTURAS PARA VERIFICAÇÃO
        self.usuarios_nao_verificados = {}  # Usuários pendentes de verificação
        self.codigos_verificacao = {}       # Códigos temporários
        self.carregar_dados_hibrido()  # 🔥 NOVO MÉTODO
    
    def criar_conta_supabase_direta(self, username, nome_cliente, moeda, saldo_inicial=0.0):
        """Cria uma conta diretamente no Supabase (para uso da tela de detalhes)"""
        try:
            if hasattr(self, 'supabase') and self.supabase.conectado:
                import random
                from datetime import datetime
                
                # Gerar número de conta único
                numero_conta = str(random.randint(100000000, 999999999))
                
                conta_data = {
                    'id': numero_conta,
                    'moeda': moeda,
                    'saldo': float(saldo_inicial),
                    'cliente_username': username,
                    'cliente_nome': nome_cliente,
                    'data_criacao': datetime.now().date().isoformat(),
                    'ativa': True,
                    'created_at': datetime.now().isoformat()
                }
                
                # Inserir conta no Supabase
                response = self.supabase.client.table('contas')\
                    .insert(conta_data)\
                    .execute()
                
                if response.data:
                    print(f"✅ Conta {numero_conta} criada no Supabase em {moeda} para {username}")
                    
                    # Atualizar lista de contas do usuário
                    self.atualizar_contas_usuario_supabase(username)
                    
                    return numero_conta
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao criar conta diretamente no Supabase: {e}")
            return None

    def carregar_dados_essenciais(self):
        """Carrega apenas dados essenciais para login rápido"""
        print("🔄 Carregando dados essenciais...")
        
        try:
            # 1. Primeiro: carregar usuários (crítico para login)
            self.carregar_usuarios_rapido()
            
            # 2. Inicializar estruturas vazias para o resto
            self.contas = {}
            self.transferencias = {}
            self.beneficiarios = {}
            
            # 3. Carregar o resto em background (não bloqueia o login)
            threading.Thread(target=self.carregar_dados_completos, daemon=True).start()
            
            print("✅ Dados essenciais carregados")
            
        except Exception as e:
            print(f"❌ Erro carregamento essencial: {e}")
            # Fallback rápido
            self.carregar_dados_local_rapido()

    def carregar_usuarios_rapido(self):
        """Carrega apenas usuários de forma rápida"""
        try:
            # Tentar Supabase primeiro
            if self.supabase.conectado:
                response = self.supabase.client.table('usuarios').select(
                    'username,senha_hash,tipo,nome,email'
                ).execute()
                
                if response.data:
                    self.usuarios = {}
                    for user in response.data:
                        self.usuarios[user['username']] = {
                            'senha': user.get('senha_hash', ''),
                            'tipo': user.get('tipo', 'cliente'),
                            'nome': user.get('nome', ''),
                            'email': user.get('email', ''),
                            'contas': []  # Será carregado depois
                        }
                    print(f"✅ {len(self.usuarios)} usuários carregados do Supabase")
                    return
            
            # Fallback para arquivo local
            usuarios_path = 'data/usuarios.json'
            if os.path.exists(usuarios_path):
                with open(usuarios_path, 'r', encoding='utf-8') as f:
                    self.usuarios = json.load(f)
                print(f"✅ {len(self.usuarios)} usuários carregados do JSON")
            else:
                # Usuários padrão
                self.usuarios = {
                    'admin': {
                        'senha': self.hash_senha('admin123'),
                        'tipo': 'admin',
                        'nome': 'Empresa de Câmbio',
                        'email': 'admin@cambiobank.com',
                        'data_cadastro': '2024-01-01'
                    }
                }
                print("✅ Usuário admin padrão criado")
                
        except Exception as e:
            print(f"❌ Erro carregar usuários: {e}")
            self.usuarios = {}

    def sincronizar_todos_saldos_com_supabase(self):
        """Sincroniza TODOS os saldos da memória com o Supabase"""
        try:
            print("🔄 Sincronizando TODOS os saldos com Supabase...")
            for conta_num, conta_info in self.contas.items():
                saldo_real = self.supabase.obter_saldo_conta(conta_num)
                if saldo_real is not None:
                    self.contas[conta_num]['saldo'] = saldo_real
                    print(f"✅ {conta_num}: {saldo_real}")
            
            self.salvar_contas()
            print("✅ Todos os saldos sincronizados!")
            
        except Exception as e:
            print(f"❌ Erro ao sincronizar saldos: {e}")

    def carregar_dados_completos(self):
        """Carrega todos os dados pesados em background"""
        print("🔄 Carregando dados completos em background...")
        
        try:
            # 1. Carregar contas (CRÍTICO - resolve o problema das contas)
            self.carregar_contas_background()
            
            # 2. Carregar transferências
            self.carregar_transferencias_background()
            
            # 3. Carregar beneficiários
            self.carregar_beneficiarios_background()
            
            # 4. Carregar configurações
            self.carregar_configuracoes_background()
            
            # 🔥 ADICIONAR ESTA LINHA:
            self.carregar_contas_contabeis()  # 🔥 CARREGAR CONTAS CONTÁBEIS
            
            print("✅ Todos os dados carregados em background")

            
        except Exception as e:
            print(f"⚠️ Erro em background: {e}")

    def carregar_dados_hibrido(self):
        """Carrega dados do Supabase se disponível, senão do JSON - VERSÃO OTIMIZADA"""
        print("🔄 Carregando dados (modo híbrido)...")
        
        # 🔥 REMOVER TODOS OS DEBUGs DETALHADOS - mantemos apenas 1 print essencial
        
        if self.supabase.conectado:
            try:
                # Tenta carregar do Supabase - MANTEM FUNCIONALIDADE, REDUZ DEBUG
                usuarios_supabase = self.supabase.obter_usuarios()
                if usuarios_supabase:
                    self.usuarios = usuarios_supabase
                    print(f"✅ {len(self.usuarios)} usuários carregados do Supabase")
                    return
            except Exception as e:
                print(f"⚠️ Erro ao carregar do Supabase: {e}")
        
        # Fallback para JSON
        print("🔄 Carregando do JSON (fallback)...")
        self.carregar_dados_rapido()  # 🔥 MUDAR PARA MÉTODO RÁPIDO

    def carregar_dados_rapido(self):
        """Versão rápida do carregar_dados original - SEM DEBUGs PESADOS"""
        try:
            # Criar pasta data se não existir
            if not os.path.exists('data'):
                os.makedirs('data')
            
            # 🔥 INICIALIZAR CONFIGURAÇÕES PRIMEIRO (CRÍTICO)
            self.configuracoes = self.configuracoes_padrao()
            
            # 🔥 CARREGAMENTO RÁPIDO DE USUÁRIOS
            usuarios_path = 'data/usuarios.json'
            if not os.path.exists(usuarios_path):
                # Apenas usuários essenciais
                self.usuarios = {
                    'admin': {
                        'senha': self.hash_senha('admin123'),
                        'tipo': 'admin',
                        'nome': 'Empresa de Câmbio',
                        'email': 'admin@cambiobank.com',
                        'data_cadastro': '2024-01-01'
                    }
                }
                self.salvar_usuarios()
            else:
                with open(usuarios_path, 'r', encoding='utf-8') as f:
                    self.usuarios = json.load(f)
                print(f"✅ {len(self.usuarios)} usuários carregados")
            
            # 🔥 INICIALIZAR ESTRUTURAS VAZIAS - O RESTO CARREGA EM BACKGROUND
            self.contas = {}
            self.beneficiarios = {}
            
            print("✅ Dados rápidos carregados")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados rápidos: {e}")
            # Estruturas vazias em caso de erro
            self.usuarios = {}
            self.contas = {}
            self.beneficiarios = {}
            self.configuracoes = self.configuracoes_padrao()  # 🔥 GARANTIR CONFIGURAÇÕES

    def obter_dados_cliente(self, username):
        """Obtém dados completos do cliente a partir do username"""
        try:
            # 🔥 CORREÇÃO: Usar o cliente Supabase correto
            response = self.supabase.client.table('usuarios')\
                .select('*')\
                .eq('username', username)\
                .execute()
            
            if response.data and len(response.data) > 0:
                usuario = response.data[0]
                print(f"✅ Dados do cliente encontrados: {usuario.get('nome')}")
                return usuario
            else:
                print(f"❌ Cliente não encontrado: {username}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar dados do cliente {username}: {e}")
            return None

    def carregar_contas_background(self):
        """Carrega contas do Supabase em background"""
        try:
            print("🔄 Carregando contas em background...")
            response = self.supabase.client.table('contas').select('*').execute()
            
            self.contas = {}
            for conta in response.data:
                self.contas[conta['id']] = {
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo']),
                    'cliente': conta['cliente_username'],
                    'cliente_nome': conta['cliente_nome'],
                    'data_criacao': conta['data_criacao']
                }
            
            print(f"✅ {len(self.contas)} contas carregadas em background")
            
            # 🔥 ATUALIZAR CONTAS DOS USUÁRIOS
            self.atualizar_contas_usuarios()
            
        except Exception as e:
            print(f"❌ Erro ao carregar contas em background: {e}")

    def atualizar_saldo_conta_supabase(self, conta_numero, novo_saldo):
        """Atualiza o saldo de uma conta no Supabase"""
        try:
            print(f"🔄 Atualizando saldo no Supabase: {conta_numero} = {novo_saldo:.2f}")
            
            # Atualizar no Supabase
            response = self.supabase.client.table('contas')\
                .update({'saldo': novo_saldo})\
                .eq('id', conta_numero)\
                .execute()
            
            if response.data:
                print(f"✅ Saldo atualizado no Supabase: {conta_numero} = {novo_saldo:.2f}")
                return True
            else:
                print(f"❌ Erro ao atualizar saldo no Supabase: Dados não retornados")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar saldo no Supabase: {e}")
            return False

    def atualizar_saldos_contas_em_tempo_real(self):
        """Atualiza TODOS os saldos das contas buscando do Supabase em tempo real - VERSÃO CORRIGIDA"""
        try:
            print("🔄 ATUALIZANDO SALDOS EM TEMPO REAL DO SUPABASE...")
            
            if not hasattr(self, 'supabase') or not self.supabase.conectado:
                print("⚠️ Supabase não disponível, usando cache local")
                return False
            
            # 1. Atualizar contas bancárias da empresa
            response_empresa = self.supabase.client.table('contas_bancarias_empresa')\
                .select('numero, saldo')\
                .execute()
            
            if response_empresa.data:
                for conta in response_empresa.data:
                    conta_num = conta['numero']
                    saldo_atual = float(conta['saldo'])
                    
                    if conta_num in self.contas_bancarias_empresa:
                        # Atualizar saldo no cache local
                        self.contas_bancarias_empresa[conta_num]['saldo'] = saldo_atual
                        print(f"   💼 Conta empresa {conta_num}: {saldo_atual:,.2f}")
            
            # 2. Atualizar contas dos clientes
            response_clientes = self.supabase.client.table('contas')\
                .select('id, saldo')\
                .execute()
            
            if response_clientes.data:
                contas_atualizadas = 0
                for conta in response_clientes.data:
                    conta_num = conta['id']
                    saldo_atual = float(conta['saldo'])
                    
                    if conta_num in self.contas:
                        # Atualizar saldo no cache local
                        self.contas[conta_num]['saldo'] = saldo_atual
                        contas_atualizadas += 1
                        
                        # Debug: mostrar algumas contas
                        if contas_atualizadas <= 5:
                            print(f"   👤 Conta cliente {conta_num}: {saldo_atual:,.2f}")
                
                print(f"✅ {contas_atualizadas} contas de clientes atualizadas")
            
            # 3. Atualizar contas dos usuários no cache
            self.atualizar_contas_usuarios()
            
            # 4. Salvar cache local para backup
            self.salvar_contas()
            self.salvar_contas_bancarias()
            
            print("✅ Todos os saldos atualizados em tempo real do Supabase!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar saldos em tempo real: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verificar_sincronizacao_saldos(self, conta_numero):
        """Verifica se o saldo local está sincronizado com o Supabase"""
        try:
            # Buscar saldo do Supabase
            response = self.supabase.client.table('contas')\
                .select('saldo')\
                .eq('id', conta_numero)\
                .execute()
            
            if response.data:
                saldo_supabase = float(response.data[0]['saldo'])
                saldo_local = self.contas[conta_numero]['saldo']
                
                print(f"🔍 VERIFICAÇÃO DE SINCRONIA:")
                print(f"   Conta: {conta_numero}")
                print(f"   Saldo Local: {saldo_local:.2f}")
                print(f"   Saldo Supabase: {saldo_supabase:.2f}")
                print(f"   Sincronizado: {abs(saldo_local - saldo_supabase) < 0.01}")
                
                return abs(saldo_local - saldo_supabase) < 0.01
            else:
                print(f"❌ Conta {conta_numero} não encontrada no Supabase")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar sincronização: {e}")
            return False

    def carregar_transferencias_background(self):
        """Carrega transferências em background"""
        try:
            print("🔄 Carregando transferências em background...")
            response = self.supabase.client.table('transferencias').select('*').execute()
            
            self.transferencias = {}
            for transf in response.data:
                self.transferencias[transf['id']] = transf
            
            print(f"✅ {len(self.transferencias)} transferências carregadas em background")
            
        except Exception as e:
            print(f"❌ Erro ao carregar transferências em background: {e}")

    def carregar_beneficiarios_background(self):
        """Carrega beneficiários em background"""
        try:
            print("🔄 Carregando beneficiários em background...")
            # Já carregamos no init, mas podemos recarregar se necessário
            print("✅ Beneficiários já carregados")
            
        except Exception as e:
            print(f"❌ Erro ao carregar beneficiários em background: {e}")

    def carregar_configuracoes_background(self):
        """Carrega configurações em background"""
        try:
            print("🔄 Carregando configurações em background...")
            configuracoes_path = 'data/configuracoes.json'
            if os.path.exists(configuracoes_path):
                with open(configuracoes_path, 'r', encoding='utf-8') as f:
                    novas_configuracoes = json.load(f)
                
                # Mesclar com configurações padrão
                self.configuracoes = self.mesclar_configuracoes(self.configuracoes, novas_configuracoes)
                print("✅ Configurações carregadas em background")
            else:
                print("ℹ️ Nenhum arquivo de configurações encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao carregar configurações em background: {e}")

    def atualizar_contas_usuarios(self):
        """Atualiza a lista de contas para cada usuário - COM ORDEM CORRETA"""
        try:
            print("🔄 Atualizando contas dos usuários...")
            
            for username, user_data in self.usuarios.items():
                # Encontrar todas as contas deste usuário
                contas_usuario = []
                for conta_id, conta_data in self.contas.items():
                    if conta_data['cliente'] == username:
                        contas_usuario.append((conta_id, conta_data))
                
                # 🔥 ORDENAR: USD → GBP → EUR → BRL
                ordem_moedas = ['USD', 'GBP', 'EUR', 'BRL']
                contas_ordenadas = sorted(contas_usuario, 
                                         key=lambda x: ordem_moedas.index(x[1]['moeda']) 
                                         if x[1]['moeda'] in ordem_moedas else 999)
                
                # Manter apenas os IDs na ordem correta
                user_data['contas'] = [conta_id for conta_id, conta_data in contas_ordenadas]
                
                print(f"👤 {username}: {len(contas_ordenadas)} contas ordenadas")
            
            print("✅ Contas dos usuários atualizadas e ordenadas")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar contas dos usuários: {e}")

    def mesclar_configuracoes(self, base, novas):
        """Mescla configurações mantendo a estrutura base"""
        resultado = base.copy()
        
        for chave, valor in novas.items():
            if chave in resultado and isinstance(resultado[chave], dict) and isinstance(valor, dict):
                resultado[chave] = self.mesclar_configuracoes(resultado[chave], valor)
            else:
                resultado[chave] = valor
                
        return resultado
    
    def salvar_usuarios_hibrido(self):
        """Salva usuários em ambos (Supabase + JSON) - VERSÃO CORRIGIDA"""
        print("💾 Salvando usuários (modo híbrido)...")
        
        # 1. Salva no JSON (método atual)
        self.salvar_usuarios()
        
        # 2. Se Supabase conectado, salva lá também
        if self.supabase.conectado:
            try:
                usuarios_supabase = self.supabase.obter_usuarios()
                usuarios_salvos = 0
                
                for username, dados in self.usuarios.items():
                    if username not in usuarios_supabase:
                        # 🔥 PREPARAR DADOS COMPATÍVEIS COM SUPABASE
                        dados_compatíveis = {
                            'username': username,
                            'senha_hash': dados.get('senha', ''),
                            'nome': dados.get('nome', ''),
                            'email': dados.get('email', ''),
                            'documento_hash': self.hash_documento(dados.get('documento', '')),
                            'telefone': dados.get('telefone', ''),
                            'tipo': dados.get('tipo', 'cliente'),
                            'data_cadastro': dados.get('data_cadastro', '2024-01-01')
                        }
                        
                        if self.supabase.salvar_usuario(dados_compatíveis):
                            usuarios_salvos += 1
                
                print(f"✅ {usuarios_salvos} usuários sincronizados com Supabase")
                
            except Exception as e:
                print(f"⚠️ Erro ao salvar no Supabase: {e}")

    def gerar_codigo_verificacao(self):
        """Gera código de 6 dígitos para verificação"""
        return ''.join(random.choices(string.digits, k=6))

    def cadastrar_usuario_pendente(self, usuario, email, senha_hash, dados_extras):
        """Cadastra usuário como pendente de verificação - PRIORIDADE SUPABASE"""
        try:
            codigo = self.gerar_codigo_verificacao()
            
            print(f"🔧 Cadastrando usuário pendente: {usuario} ({email})")
            print(f"🎯 Código gerado: {codigo}")
            
            # 🔥🔥🔥 IMPORTANTE: Salvar as moedas selecionadas para uso posterior
            moedas_selecionadas = dados_extras.get('moedas_selecionadas', [])
            print(f"🎯 Moedas selecionadas no cadastro: {moedas_selecionadas}")
            
            # 1. PRIMEIRO: TENTAR SALVAR NO SUPABASE
            print("📤 Prioridade: Tentando salvar no Supabase primeiro...")
            
            try:
                # Importar SupabaseManager da raiz
                import sys
                import os
                
                # Adicionar diretório raiz ao path
                current_dir = os.path.dirname(os.path.abspath(__file__))  # app/
                project_root = os.path.dirname(current_dir)  # cambio_bank_kivy/
                
                if project_root not in sys.path:
                    sys.path.append(project_root)
                
                from supabase_manager import SupabaseManager
                
                # Criar manager
                manager = SupabaseManager()
                
                if manager.conectado:
                    print("✅ SupabaseManager conectado ao Supabase")
                    
                    # 🔥 Preparar dados para Supabase (SEM moedas_selecionadas)
                    dados_manager = {
                        'username': usuario,
                        'email': email,
                        'senha_hash': senha_hash,
                        'nome': dados_extras.get('nome', ''),
                        'documento': dados_extras.get('documento', ''),
                        'telefone': dados_extras.get('telefone', ''),
                        'endereco': dados_extras.get('endereco', ''),
                        'cidade': dados_extras.get('cidade', ''),
                        'cep': dados_extras.get('cep', ''),
                        'estado': dados_extras.get('estado', ''),
                        'pais': dados_extras.get('pais', ''),
                        'codigo_verificacao': codigo,
                        'status': 'pendente',
                        'verificado': False,
                        'cambio_liberado': False
                    }
                    
                    # Usar o método salvar_usuario do manager
                    resultado = manager.salvar_usuario_com_verificacao(dados_manager)
                    
                    if resultado:
                        print(f"✅✅✅ USUÁRIO SALVO NO SUPABASE COM TODOS OS DADOS!")
                        print(f"   Username: {usuario}")
                        print(f"   Email: {email}")
                        print(f"   Endereço: {dados_extras.get('endereco', '')}")
                        print(f"   Cidade: {dados_extras.get('cidade', '')}")
                        print(f"   CEP: {dados_extras.get('cep', '')}")
                        print(f"   Estado: {dados_extras.get('estado', '')}")
                        print(f"   País: {dados_extras.get('pais', '')}")
                        print(f"   Código: {codigo}")
                        print(f"   Moedas selecionadas: {moedas_selecionadas}")
                        print(f"   Câmbio liberado: NÃO (padrão para novos clientes)")
                        
                        # 🔥 SALVAR MOEDAS NOS DADOS PENDENTES PARA USO POSTERIOR
                        self.usuarios_nao_verificados[email] = {
                            'usuario': usuario,
                            'senha_hash': senha_hash,
                            'dados': dados_extras,  # 🔥 JÁ TEM AS MOEDAS AQUI
                            'moedas_selecionadas': moedas_selecionadas,  # 🔥 GUARDAR SEPARADAMENTE
                            'timestamp': time.time()
                        }
                        
                        self.codigos_verificacao[email] = {
                            'codigo': codigo,
                            'timestamp': time.time()
                        }
                        
                        # 🔥 MODO SIMULAÇÃO
                        print(f"🎯 MODO SIMULAÇÃO: Código de verificação para {email}: {codigo}")
                        
                        return {
                            'sucesso': True,
                            'modo_simulacao': True,
                            'codigo': codigo,
                            'email': email,
                            'salvo_no_supabase': True,
                            'moedas_selecionadas': moedas_selecionadas  # 🔥 RETORNAR TAMBÉM
                        }
                    else:
                        print(f"❌ Falha ao salvar no Supabase via Manager")
                        # Vai para fallback local
                        raise Exception("Falha ao salvar no Supabase")
                else:
                    print("❌ SupabaseManager não conectado")
                    # Vai para fallback local
                    raise Exception("Supabase não conectado")
                    
            except Exception as e:
                print(f"⚠️ Erro com Supabase: {e}")
                print("🔄 Usando fallback local...")
                
                # 2. FALLBACK: Salvar localmente apenas se Supabase falhar
                usuario_id_local = f"user_{random.randint(100000, 999999)}"
                
                dados_local = {
                    'id': usuario_id_local,
                    'username': usuario,
                    'email': email,
                    'senha_hash': senha_hash,
                    'nome': dados_extras.get('nome', ''),
                    'documento': dados_extras.get('documento', ''),
                    'telefone': dados_extras.get('telefone', ''),
                    'endereco': dados_extras.get('endereco', ''),
                    'cidade': dados_extras.get('cidade', ''),
                    'cep': dados_extras.get('cep', ''),
                    'estado': dados_extras.get('estado', ''),
                    'pais': dados_extras.get('pais', ''),
                    'status': 'pendente',
                    'data_cadastro': datetime.datetime.now().isoformat(),
                    'verificado': False,
                    'codigo_verificacao': codigo,
                    'cambio_liberado': False
                }
                
                # 🔥 SALVAR MOEDAS LOCALMENTE
                if 'moedas_selecionadas' in dados_extras:
                    dados_local['moedas_selecionadas'] = dados_extras['moedas_selecionadas']
                
                # Salvar localmente (apenas como fallback)
                self.usuarios[usuario] = dados_local
                self.usuarios_nao_verificados[email] = {
                    'usuario': usuario,
                    'senha_hash': senha_hash,
                    'dados': dados_extras,  # 🔥 TEM AS MOEDAS
                    'moedas_selecionadas': moedas_selecionadas,  # 🔥 GUARDAR SEPARADAMENTE
                    'timestamp': time.time()
                }
                
                self.codigos_verificacao[email] = {
                    'codigo': codigo,
                    'timestamp': time.time()
                }
                
                print(f"✅ Usuário salvo LOCALMENTE (fallback): {usuario}")
                print(f"🎯 Moedas salvas localmente: {moedas_selecionadas}")
                
                # 🔥 MODO SIMULAÇÃO
                print(f"🎯 MODO SIMULAÇÃO: Código de verificação para {email}: {codigo}")
                
                return {
                    'sucesso': True,
                    'modo_simulacao': True,
                    'codigo': codigo,
                    'email': email,
                    'salvo_no_supabase': False,
                    'aviso': 'Usuário salvo apenas localmente (Supabase falhou)',
                    'moedas_selecionadas': moedas_selecionadas  # 🔥 RETORNAR TAMBÉM
                }
                
        except Exception as e:
            print(f"❌ Erro crítico ao cadastrar usuário pendente: {e}")
            import traceback
            traceback.print_exc()
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def salvar_usuario_pendente_supabase(self, dados_usuario):
        """Salva usuário pendente diretamente no Supabase"""
        try:
            if not hasattr(self, 'supabase_manager') or not self.supabase_manager:
                print("❌ SupabaseManager não disponível")
                return False
            
            # Conectar ao Supabase diretamente
            try:
                from app.supabase_client import supabase
                if not supabase:
                    print("❌ Conexão Supabase não disponível")
                    return False
            except ImportError:
                print("❌ Módulo supabase_client não encontrado")
                return False
            
            # Preparar dados para Supabase
            import hashlib
            from datetime import datetime
            
            dados_supabase = {
                'username': dados_usuario['username'],
                'email': dados_usuario['email'],
                'senha_hash': dados_usuario['senha'],  # Já está hashado
                'nome': dados_usuario['nome'],
                'documento_hash': hashlib.sha256(dados_usuario['documento'].encode()).hexdigest() if dados_usuario['documento'] else '',
                'telefone': dados_usuario.get('telefone', ''),
                'endereco': '',
                'cidade': '',
                'cep': '',
                'estado': '',
                'pais': '',
                'tipo': 'cliente',
                'contas': [],  # Vazio inicialmente
                'codigo_verificacao': dados_usuario['codigo_verificacao'],
                'status': 'pendente',
                'verificado': False,
                'data_cadastro': datetime.now().isoformat()
            }
            
            print(f"📤 Salvando diretamente no Supabase: {dados_usuario['username']}")
            
            # Verificar se já existe
            response_existe = supabase.table('usuarios')\
                .select('id')\
                .or_(f"username.eq.{dados_usuario['username']},email.eq.{dados_usuario['email']}")\
                .execute()
            
            if response_existe.data:
                print(f"⚠️ Usuário ou email já existe: {dados_usuario['username']}")
                return False
            
            # Inserir novo usuário
            response = supabase.table('usuarios')\
                .insert(dados_supabase)\
                .execute()
            
            if response.data:
                print(f"✅ Usuário {dados_usuario['username']} salvo no Supabase com código")
                print(f"   ID: {response.data[0]['id']}")
                print(f"   Código: {dados_usuario['codigo_verificacao']}")
                return True
            else:
                print(f"❌ Falha ao inserir usuário no Supabase")
                return False
                
        except Exception as e:
            print(f"🔥 ERRO ao salvar usuário pendente no Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def atualizar_codigo_verificacao_supabase(self, email, codigo):
        """Atualiza código de verificação no Supabase"""
        try:
            if hasattr(self, 'supabase_manager'):
                # Buscar usuário pelo email
                from app.supabase_client import supabase
                if supabase:
                    response = supabase.table('usuarios')\
                        .select('id, username')\
                        .eq('email', email)\
                        .execute()
                    
                    if response.data:
                        usuario_id = response.data[0]['id']
                        # Atualizar código
                        supabase.table('usuarios')\
                            .update({'codigo_verificacao': codigo})\
                            .eq('id', usuario_id)\
                            .execute()
                        print(f"✅ Código de verificação {codigo} salvo no Supabase para {email}")
                        return True
            return False
        except Exception as e:
            print(f"⚠️ Não foi possível salvar código no Supabase: {e}")
            return False

    def salvar_usuario_supabase(self, dados_usuario):
        """Salva usuário na tabela 'usuarios' do Supabase com a estrutura exata"""
        try:
            from app.supabase_client import supabase
            
            if supabase is None:
                print("❌ Supabase não está conectado")
                return False
            
            print(f"📤 Conectando ao Supabase para salvar usuário: {dados_usuario['username']}")
            
            # Verificar se usuário já existe pelo email
            try:
                response_existe = supabase.table('usuarios').select('id').eq('email', dados_usuario['email']).execute()
                
                if response_existe.data and len(response_existe.data) > 0:
                    print(f"⚠️ Usuário já existe no Supabase: {dados_usuario['email']}")
                    return False  # Não permitir cadastro duplicado
                
                # Inserir novo usuário
                print("➕ Inserindo novo usuário no Supabase...")
                
                # Remover campos que podem ser gerados automaticamente pelo Supabase
                # para evitar conflitos
                dados_para_inserir = dict(dados_usuario)
                
                # Não enviar se o Supabase gera automaticamente
                dados_para_inserir.pop('data_cadastro', None)
                dados_para_inserir.pop('created_at', None)
                
                response = supabase.table('usuarios').insert(dados_para_inserir).execute()
                
                if response.data and len(response.data) > 0:
                    usuario_id = response.data[0]['id']
                    print(f"✅ Usuário inserido no Supabase. ID: {usuario_id}")
                    return True
                else:
                    print(f"❌ Nenhum dado retornado do Supabase")
                    print(f"   Response: {response}")
                    return False
                    
            except Exception as e:
                print(f"🔥 Erro na comunicação com Supabase: {e}")
                import traceback
                traceback.print_exc()
                return False
            
        except ImportError:
            print("⚠️ Módulo supabase não encontrado")
            return False
        except Exception as e:
            print(f"🔥 Erro crítico ao salvar no Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def hash_documento(self, documento):
        """Cria hash do documento para privacidade"""
        if not documento:
            return ''
        
        # Usar o mesmo método de hash da senha
        documento_limpo = documento.strip().replace('.', '').replace('-', '').replace('/', '')
        return hashlib.sha256(documento_limpo.encode()).hexdigest()

    def verificar_codigo_email(self, email, codigo_digitado):
        """Verifica código de verificação de email - VERSÃO CORRIGIDA"""
        try:
            print(f"🔍 Verificando código para email: {email}")
            print(f"📧 Código digitado: {codigo_digitado}")
            
            # Conectar ao Supabase
            import sys
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                print("❌ Credenciais do Supabase não configuradas")
                return False, "Erro de configuração do sistema"
            
            from supabase import create_client
            supabase = create_client(url, key)
            
            # 🔥 PRIMEIRO: Verificar se o usuário foi realmente salvo
            print("🔍 Verificando todos os usuários no Supabase...")
            all_users = supabase.table('usuarios').select('email, username, status').execute()
            print(f"📊 Total de usuários no Supabase: {len(all_users.data) if all_users.data else 0}")
            
            if all_users.data:
                for user in all_users.data:
                    print(f"   👤 Email: {user.get('email')}, Username: {user.get('username')}, Status: {user.get('status')}")
            
            # Buscar usuário específico
            response = supabase.table('usuarios')\
                .select('codigo_verificacao, username, verificado, status, nome, email')\
                .eq('email', email)\
                .execute()
            
            print(f"🔍 Resultado da busca específica: {response.data}")
            
            if not response.data or len(response.data) == 0:
                print(f"❌ Email não encontrado no Supabase: {email}")
                
                # 🔥 VERIFICAR SE ESTÁ NA LISTA DE PENDENTES
                if hasattr(self, 'usuarios_nao_verificados') and email in self.usuarios_nao_verificados:
                    print(f"✅ Email encontrado na lista de pendentes LOCAIS")
                    dados_pendentes = self.usuarios_nao_verificados[email]
                    
                    # Verificar código local
                    if hasattr(self, 'codigos_verificacao') and email in self.codigos_verificacao:
                        codigo_local = self.codigos_verificacao[email].get('codigo')
                        print(f"📧 Código local: {codigo_local}, Código digitado: {codigo_digitado}")
                        
                        if str(codigo_local) == str(codigo_digitado):
                            print(f"✅✅✅ CÓDIGO CORRETO (verificação local)!")
                            
                            # 🔥 SALVAR NO SUPABASE AGORA (cadastro tardio)
                            try:
                                print("📤 Tentando salvar no Supabase agora...")
                                
                                # Preparar dados
                                from datetime import datetime
                                import hashlib
                                
                                dados_supabase = {
                                    'username': dados_pendentes['usuario'],
                                    'email': email,
                                    'senha_hash': dados_pendentes['senha_hash'],
                                    'nome': dados_pendentes['dados']['nome'],
                                    'telefone': dados_pendentes['dados'].get('telefone', ''),
                                    'endereco': dados_pendentes['dados'].get('endereco', ''),
                                    'cidade': dados_pendentes['dados'].get('cidade', ''),
                                    'cep': dados_pendentes['dados'].get('cep', ''),
                                    'estado': dados_pendentes['dados'].get('estado', ''),
                                    'pais': dados_pendentes['dados'].get('pais', ''),
                                    'tipo': 'cliente',
                                    'status': 'ativo',
                                    'verificado': True,
                                    'cambio_liberado': False,
                                    'data_cadastro': datetime.now().isoformat()
                                }
                                
                                # Hash do documento se existir
                                if 'documento' in dados_pendentes['dados'] and dados_pendentes['dados']['documento']:
                                    dados_supabase['documento_hash'] = hashlib.sha256(
                                        dados_pendentes['dados']['documento'].encode()
                                    ).hexdigest()
                                
                                # Inserir no Supabase
                                response_insert = supabase.table('usuarios')\
                                    .insert(dados_supabase)\
                                    .execute()
                                
                                if response_insert.data:
                                    print(f"✅✅✅ Usuário salvo NO SUPABASE com sucesso!")
                                    username = dados_pendentes['usuario']
                                    
                                    # 🔥 SALVAR CONFIGURAÇÃO DE CÂMBIO (DESATIVADO)
                                    config_data = {
                                        'tipo_config': 'permissoes',
                                        'cliente_username': username,
                                        'valor_config': False,  # CÂMBIO DESATIVADO
                                        'data_atualizacao': datetime.now().isoformat()
                                    }
                                    
                                    supabase.table('config_cotacoes')\
                                        .insert(config_data)\
                                        .execute()
                                    
                                    print(f"✅ Configuração salva: câmbio DESATIVADO para {username}")
                                    
                                    # 🔥 CRIAR CONTAS COM AS MOEDAS SELECIONADAS NO CADASTRO
                                    moedas_selecionadas = dados_pendentes.get('moedas_selecionadas', [])
                                    if not moedas_selecionadas and 'dados' in dados_pendentes:
                                        moedas_selecionadas = dados_pendentes['dados'].get('moedas_selecionadas', [])
                                    
                                    print(f"🎯 Moedas selecionadas para criar contas: {moedas_selecionadas}")
                                    
                                    if moedas_selecionadas:
                                        self.criar_contas_com_moedas(email, username, moedas_selecionadas)
                                    else:
                                        print("⚠️ Nenhuma moeda selecionada, usando padrão")
                                        self.criar_contas_apos_verificacao(email, username)
                                    
                                    # Limpar dados temporários
                                    self.completar_cadastro_local_verificacao(email, dados_pendentes, moedas_selecionadas)
                                    
                                    return True, f"Email verificado e conta criada! Bem-vindo, {username}!"
                                else:
                                    print(f"❌ Falha ao salvar no Supabase")
                                    return False, "Erro ao salvar conta no sistema"
                                    
                            except Exception as save_error:
                                print(f"❌ Erro ao salvar no Supabase: {save_error}")
                                return False, f"Erro técnico: {str(save_error)}"
                        else:
                            print(f"❌ Código incorreto (local)")
                            return False, "Código incorreto"
                    else:
                        print(f"❌ Nenhum código local encontrado")
                        return False, "Nenhum código de verificação encontrado"
                else:
                    print(f"❌ Email não encontrado em lugar nenhum")
                    return False, "Email não encontrado para verificação"
            
            # Se chegou aqui, o email foi encontrado no Supabase
            usuario_data = response.data[0]
            codigo_correto = usuario_data.get('codigo_verificacao')
            username = usuario_data.get('username')
            verificado = usuario_data.get('verificado', False)
            
            print(f"✅ Usuário encontrado no Supabase: {username}")
            print(f"   Código no Supabase: {codigo_correto}")
            print(f"   Verificado atual: {verificado}")
            
            # Verificar se já está verificado
            if verificado:
                print(f"⚠️ Usuário já está verificado")
                return True, f"Usuário {username} já está verificado"
            
            # Verificar código
            if not codigo_correto:
                print(f"❌ Nenhum código de verificação encontrado no Supabase")
                return False, "Nenhum código de verificação encontrado"
            
            if str(codigo_correto) != str(codigo_digitado):
                print(f"❌ Código incorreto")
                return False, "Código incorreto"
            
            # ✅ Código correto!
            print(f"🎯 Código correto!")
            
            # Atualizar status no Supabase
            from datetime import datetime
            update_response = supabase.table('usuarios')\
                .update({
                    'verificado': True,
                    'status': 'ativo',
                    'codigo_verificacao': None,
                    'cambio_liberado': False  # 🔥 CÂMBIO DESATIVADO
                })\
                .eq('email', email)\
                .execute()
            
            if not update_response.data:
                print(f"❌ Erro ao atualizar status no Supabase")
                return False, "Erro ao atualizar status"
            
            print(f"✅ Usuário {username} verificado no Supabase!")
            
            # 🔥 SALVAR CONFIGURAÇÃO DE CÂMBIO (SE NÃO EXISTIR)
            config_check = supabase.table('config_cotacoes')\
                .select('id')\
                .eq('tipo_config', 'permissoes')\
                .eq('cliente_username', username)\
                .execute()
            
            if not config_check.data:
                config_data = {
                    'tipo_config': 'permissoes',
                    'cliente_username': username,
                    'valor_config': False,  # CÂMBIO DESATIVADO
                    'data_atualizacao': datetime.now().isoformat()
                }
                
                supabase.table('config_cotacoes')\
                    .insert(config_data)\
                    .execute()
                
                print(f"✅ Configuração de câmbio salva: DESATIVADO para {username}")
            
            # 🔥 CRIAR CONTAS COM AS MOEDAS SELECIONADAS NO CADASTRO
            moedas_selecionadas = []
            if hasattr(self, 'usuarios_nao_verificados') and email in self.usuarios_nao_verificados:
                dados_pendentes = self.usuarios_nao_verificados[email]
                moedas_selecionadas = dados_pendentes.get('moedas_selecionadas', [])
                if not moedas_selecionadas and 'dados' in dados_pendentes:
                    moedas_selecionadas = dados_pendentes['dados'].get('moedas_selecionadas', [])
            
            print(f"🎯 Moedas selecionadas encontradas: {moedas_selecionadas}")
            
            if moedas_selecionadas:
                # Criar contas com moedas específicas
                self.criar_contas_com_moedas(email, username, moedas_selecionadas)
            else:
                # Usar método original (fallback para moedas padrão)
                self.criar_contas_apos_verificacao(email, username)
            
            return True, f"Email verificado com sucesso! Bem-vindo, {username}!"
                
        except Exception as e:
            print(f"🔥 ERRO na verificação: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Erro interno: {str(e)}"
        
    def completar_cadastro_local_verificacao(self, email, dados_pendentes, moedas_selecionadas=None):
        """Completa cadastro local após verificação bem-sucedida"""
        try:
            usuario = dados_pendentes['usuario']
            senha_hash = dados_pendentes['senha_hash']
            dados = dados_pendentes['dados']
            
            # Usar moedas passadas ou buscar dos dados
            if moedas_selecionadas is None:
                moedas_selecionadas = dados_pendentes.get('moedas_selecionadas', [])
                if not moedas_selecionadas:
                    moedas_selecionadas = dados.get('moedas_selecionadas', ['USD', 'BRL'])
            
            # Salvar localmente
            self.usuarios[usuario] = {
                'senha': senha_hash,
                'tipo': 'cliente',
                'nome': dados['nome'],
                'email': email,
                'documento': dados.get('documento', ''),
                'telefone': dados.get('telefone', ''),
                'endereco': dados.get('endereco', ''),
                'cidade': dados.get('cidade', ''),
                'cep': dados.get('cep', ''),
                'estado': dados.get('estado', ''),
                'pais': dados.get('pais', ''),
                'contas': [],
                'moedas_selecionadas': moedas_selecionadas,  # 🔥 SALVAR LOCALMENTE
                'data_cadastro': datetime.datetime.now().strftime('%Y-%m-%d'),
                'cambio_liberado': False
            }
            
            # Configurar permissões
            if not hasattr(self, 'permissoes_cambio'):
                self.permissoes_cambio = {}
            self.permissoes_cambio[usuario] = False
            
            # Criar contas localmente também
            if moedas_selecionadas:
                self.criar_contas_cliente(usuario, dados['nome'], moedas_selecionadas)
            
            # Limpar dados temporários
            if hasattr(self, 'usuarios_nao_verificados') and email in self.usuarios_nao_verificados:
                del self.usuarios_nao_verificados[email]
            
            if hasattr(self, 'codigos_verificacao') and email in self.codigos_verificacao:
                del self.codigos_verificacao[email]
            
            # Salvar dados
            self.salvar_usuarios()
            self.salvar_dados_cotacoes()
            
            print(f"✅ Cadastro local completado para {usuario} com moedas: {moedas_selecionadas}")
            
        except Exception as e:
            print(f"⚠️ Erro ao completar cadastro local: {e}")

    def criar_contas_com_moedas(self, email, username, moedas_selecionadas):
        """Cria contas com moedas específicas"""
        try:
            print(f"💰 Criando contas para {username} com moedas: {moedas_selecionadas}")
            
            import sys
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if url and key:
                from supabase import create_client
                supabase = create_client(url, key)
                
                # Buscar nome do cliente
                response = supabase.table('usuarios')\
                    .select('nome')\
                    .eq('username', username)\
                    .execute()
                
                if response.data:
                    nome_cliente = response.data[0].get('nome', username)
                    
                    # Usar SupabaseManager
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(current_dir)
                    
                    if project_root not in sys.path:
                        sys.path.append(project_root)
                    
                    from supabase_manager import SupabaseManager
                    manager = SupabaseManager()
                    
                    if manager.conectado:
                        contas_criadas = manager.criar_contas_supabase(
                            username, 
                            nome_cliente, 
                            moedas_selecionadas
                        )
                        
                        if contas_criadas:
                            print(f"✅ {len(contas_criadas)} contas criadas no Supabase")
                            
                            # Atualizar campo 'contas' do usuário
                            supabase.table('usuarios')\
                                .update({'contas': contas_criadas})\
                                .eq('username', username)\
                                .execute()
                            
                            print(f"✅ Usuário atualizado com IDs das contas")
                            
                            # 🔥 ATUALIZAR CACHE LOCAL
                            if username in self.usuarios:
                                self.usuarios[username]['contas'] = contas_criadas
                            
                            return True
                    
                print(f"⚠️ Não foi possível criar contas para {username}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao criar contas com moedas: {e}")
            import traceback
            traceback.print_exc()
            return False

    def criar_contas_apos_verificacao(self, email, username):
        """Cria contas no Supabase após verificação do email - VERSÃO CORRIGIDA"""
        try:
            print(f"💰 Criando contas para {username} após verificação...")
            
            # 🔥 PRIMEIRO: Buscar moedas dos dados pendentes
            moedas_selecionadas = []
            if hasattr(self, 'usuarios_nao_verificados') and email in self.usuarios_nao_verificados:
                dados_pendentes = self.usuarios_nao_verificados[email]
                moedas_selecionadas = dados_pendentes.get('moedas_selecionadas', [])
                if not moedas_selecionadas and 'dados' in dados_pendentes:
                    moedas_selecionadas = dados_pendentes['dados'].get('moedas_selecionadas', [])
            
            if not moedas_selecionadas:
                # Fallback: usar moedas padrão
                moedas_selecionadas = ['USD', 'BRL']
                print(f"⚠️ Nenhuma moeda encontrada, usando padrão: {moedas_selecionadas}")
            
            print(f"🎯 Moedas para criar contas: {moedas_selecionadas}")
            
            # Buscar dados do usuário no Supabase
            import sys
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if url and key:
                from supabase import create_client
                supabase = create_client(url, key)
                
                # Buscar nome do cliente
                response = supabase.table('usuarios')\
                    .select('nome')\
                    .eq('username', username)\
                    .execute()
                
                if response.data:
                    nome_cliente = response.data[0].get('nome', username)
                    
                    if moedas_selecionadas:
                        print(f"🎯 Criando contas com moedas: {moedas_selecionadas}")
                        
                        # Usar SupabaseManager para criar contas
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        project_root = os.path.dirname(current_dir)
                        
                        if project_root not in sys.path:
                            sys.path.append(project_root)
                        
                        from supabase_manager import SupabaseManager
                        manager = SupabaseManager()
                        
                        if manager.conectado:
                            # Criar contas
                            contas_criadas = manager.criar_contas_supabase(
                                username, 
                                nome_cliente, 
                                moedas_selecionadas
                            )
                            
                            if contas_criadas:
                                print(f"✅ {len(contas_criadas)} contas criadas no Supabase")
                                print(f"   IDs: {contas_criadas}")
                                
                                # Atualizar usuário com IDs das contas (campo 'contas' EXISTE)
                                supabase.table('usuarios')\
                                    .update({'contas': contas_criadas})\
                                    .eq('username', username)\
                                    .execute()
                                
                                print(f"✅ Usuário atualizado com IDs das contas")
                            else:
                                print(f"⚠️ Nenhuma conta criada")
                        else:
                            print(f"⚠️ SupabaseManager não conectado para criar contas")
                    else:
                        print(f"⚠️ Nenhuma moeda selecionada para {username}")
                else:
                    print(f"❌ Usuário não encontrado no Supabase: {username}")
            else:
                print(f"❌ Credenciais do Supabase não configuradas")
                
        except Exception as e:
            print(f"❌ Erro ao criar contas após verificação: {e}")
            import traceback
            traceback.print_exc()

    def completar_cadastro(self, email):
        """Completa o cadastro após verificação do email"""
        if email not in self.usuarios_nao_verificados:
            return False
        
        dados_usuario = self.usuarios_nao_verificados[email]
        
        # 🔥 ADICIONAR AO SISTEMA (usando método existente)
        sucesso, mensagem = self.cadastrar_usuario_existente(
            dados_usuario['usuario'],
            dados_usuario['senha'], 
            dados_usuario['dados']
        )
        
        if sucesso:
            # Limpar dados temporários
            del self.usuarios_nao_verificados[email]
            del self.codigos_verificacao[email]
            
        return sucesso

    def reenviar_codigo_verificacao(self, email):
        """Reenvia código de verificação"""
        if email not in self.usuarios_nao_verificados:
            return False, "Email não encontrado"
        
        codigo = self.gerar_codigo_verificacao()
        self.codigos_verificacao[email] = {
            'codigo': codigo,
            'timestamp': time.time()
        }
        
        # 🔥 MODO SIMULAÇÃO
        print(f"🎯 MODO SIMULAÇÃO: NOVO código para {email}: {codigo}")
        
        return True, "Código reenviado com sucesso!"
        
    def obter_spread_cliente(self, usuario, par_moedas):
        """Obtém spread configurado para o cliente - MANTENDO A LÓGICA EXISTENTE"""
        if usuario in self.spreads_clientes:
            if par_moedas in self.spreads_clientes[usuario]:
                return self.spreads_clientes[usuario][par_moedas]
        
        # Retornar spread padrão se não configurado
        return {'compra': self.spread_padrao, 'venda': self.spread_padrao}
    
    def cliente_tem_permissao_cambio(self, usuario):
        """Verifica se cliente tem permissão para câmbio"""
        return self.permissoes_cambio.get(usuario, True)  # True por padrão para novos clientes
    
    def obter_limite_operacional(self, usuario):
        """Obtém limite operacional do cliente"""
        # Se não existir a estrutura de limites, inicializar
        if not hasattr(self, 'limites_operacionais'):
            self.limites_operacionais = {}
        
        # Retornar limite do cliente ou padrão de R$ 10.000,00
        limite = self.limites_operacionais.get(usuario, 10000.00)
        
        print(f"DEBUG LIMITE: Usuário {usuario} - Limite: R$ {limite:.2f}")
        return limite

    def verificar_horario_comercial(self, usuario=None):
        """Verifica se está no horário comercial (Brasília)"""
        from datetime import datetime
        import pytz
        
        try:
            # Obter horário atual de Brasília
            tz_brasilia = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(tz_brasilia)
            
            # Verificar se cliente tem horário personalizado
            if usuario and usuario in self.horarios_clientes:
                horario_cliente = self.horarios_clientes[usuario]
                dias_semana = horario_cliente['dias_semana']
                inicio = horario_cliente['inicio']
                fim = horario_cliente['fim']
                tipo = "personalizado"
            else:
                # Usar horário padrão
                dias_semana = self.horario_comercial_padrao['dias_semana']
                inicio = self.horario_comercial_padrao['inicio']
                fim = self.horario_comercial_padrao['fim']
                tipo = "padrão"
            
            # Verificar dia da semana (0=Segunda, 6=Domingo)
            dia_atual = agora.weekday()  # 0=Segunda, 6=Domingo
            
            print(f"🔍 VERIFICAÇÃO HORÁRIO {tipo.upper()}:")
            print(f"   Cliente: {usuario}")
            print(f"   Dia atual: {dia_atual} (0=Seg, 6=Dom)")
            print(f"   Dias permitidos: {dias_semana}")
            print(f"   Horário atual: {agora.strftime('%H:%M')}")
            print(f"   Horário permitido: {inicio} às {fim}")
            
            if dia_atual not in dias_semana:
                dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                dias_permitidos = [dias_nomes[d] for d in dias_semana]
                return False, f"Fora do horário comercial. Disponível apenas: {', '.join(dias_permitidos)}"
            
            # Verificar horário
            hora_atual = agora.strftime('%H:%M')
            
            if hora_atual < inicio:
                return False, f"Fora do horário comercial. Disponível a partir das {inicio}"
            elif hora_atual > fim:
                return False, f"Fora do horário comercial. Disponível até às {fim}"
            
            print(f"   ✅ DENTRO DO HORÁRIO COMERCIAL")
            return True, "Dentro do horário comercial"
            
        except Exception as e:
            print(f"❌ Erro ao verificar horário: {e}")
            # Em caso de erro, permitir a operação (fail-open)
            return True, "Horário verificado com ressalvas"

    def carregar_dados(self):
        """Carrega usuários e contas - mesma lógica do Tkinter"""
        try:
            # Criar pasta data se não existir
            if not os.path.exists('data'):
                os.makedirs('data')
                print("Pasta 'data' criada")
            
            # 🔥🔥🔥 NOVO: PRIMEIRO CARREGAR CONTAS DO SUPABASE
            print("🔄 Carregando contas do Supabase...")
            try:
                response = supabase.table('contas').select('*').execute()
                self.contas = {}
                for conta in response.data:
                    self.contas[conta['id']] = {
                        'moeda': conta['moeda'],
                        'saldo': float(conta['saldo']),
                        'cliente': conta['cliente_username'],
                        'cliente_nome': conta['cliente_nome'],
                        'data_criacao': conta['data_criacao']
                    }
                print(f"✅ {len(self.contas)} contas carregadas do Supabase")
                
                # DEBUG: Mostrar contas da londrina
                contas_londrina = {k: v for k, v in self.contas.items() if v['cliente'] == 'londrina'}
                print(f"🎯 Contas da londrina: {len(contas_londrina)}")
                for conta_id, dados in contas_londrina.items():
                    print(f"   💳 {conta_id}: {dados['moeda']} - Saldo: {dados['saldo']:,.2f}")
                    
            except Exception as e:
                print(f"❌ Erro ao carregar contas do Supabase: {e}")
                # Fallback para o método original com JSON
                self.carregar_contas_json_fallback()
            
            # 🔥 CONTINUAÇÃO DO CÓDIGO ORIGINAL (SEM ALTERAÇÕES)
            # Verificar/criar arquivo de usuários
            usuarios_path = 'data/usuarios.json'
            if not os.path.exists(usuarios_path):
                print("Criando arquivo de usuários...")
                self.usuarios = {
                    'admin': {
                        'senha': self.hash_senha('admin123'),
                        'tipo': 'admin',
                        'nome': 'Empresa de Câmbio',
                        'email': 'admin@cambiobank.com',
                        'data_cadastro': '2024-01-01'
                    },
                    'joao.silva': {
                        'senha': self.hash_senha('cliente123'),
                        'tipo': 'cliente', 
                        'nome': 'João Silva Comércio Ltda',
                        'email': 'joao@empresa.com',
                        'contas': ['183860837', '487736769'],
                        'telefone': '(11) 9999-8888',
                        'documento': '12.345.678/0001-90',
                        'data_cadastro': '2024-01-15'
                    }
                }
                self.salvar_usuarios()
            else:
                with open(usuarios_path, 'r', encoding='utf-8') as f:
                    self.usuarios = json.load(f)
                print(f"✅ {len(self.usuarios)} usuários carregados")
            
            # 🔥 CARREGAR BENEFICIÁRIOS (MANTIDO ORIGINAL)
            beneficiarios_path = 'data/beneficiarios.json'
            if os.path.exists(beneficiarios_path):
                with open(beneficiarios_path, 'r', encoding='utf-8') as f:
                    self.beneficiarios = json.load(f)
                print(f"✅ {sum(len(b) for b in self.beneficiarios.values())} beneficiários carregados")
            else:
                self.beneficiarios = {}
                print("ℹ️ Nenhum arquivo de beneficiários encontrado, criando novo")
            
            # 🔥 CARREGAR CONTAS BANCÁRIAS DA EMPRESA (MANTIDO ORIGINAL)
            self.carregar_contas_bancarias()
            
            # 🔥 CARREGAR CONFIGURAÇÕES (MANTIDO ORIGINAL)
            configuracoes_path = 'data/configuracoes.json'
            if os.path.exists(configuracoes_path):
                with open(configuracoes_path, 'r', encoding='utf-8') as f:
                    self.configuracoes = json.load(f)
                print("✅ Configurações do sistema carregadas")
                
                # Aplicar taxas de câmbio das configurações se existirem
                if 'financeiras' in self.configuracoes and 'taxas_cambio' in self.configuracoes['financeiras']:
                    self.taxas_cambio = self.configuracoes['financeiras']['taxas_cambio']
                    print("✅ Taxas de câmbio das configurações aplicadas")
            else:
                # Usar configurações padrão
                self.configuracoes = self.configuracoes_padrao()
                print("✅ Configurações padrão carregadas")

            # 🔥 ADICIONAR CARREGAMENTO DAS CONTAS CONTÁBEIS (MANTIDO ORIGINAL)
            self.carregar_contas_contabeis()

        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            # Inicializar estruturas vazias em caso de erro
            self.beneficiarios = {}
            self.configuracoes = self.configuracoes_padrao()

            # 🔥 ADICIONAR DEBUG APÓS CARREGAR DADOS
            self.debug_carregamento_telas()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")

            # 🔥 INICIALIZAR ESTRUTURAS DE COTAÇÕES
            if not hasattr(self, 'spreads_clientes'):
                self.spreads_clientes = {}
            if not hasattr(self, 'permissoes_cambio'):
                self.permissoes_cambio = {}
            if not hasattr(self, 'limites_operacionais'):
                self.limites_operacionais = {}
                
            # 🔥 CARREGAR DADOS DE COTAÇÕES (FORA DO BLOCO EXCEPT!)
            self.carregar_dados_cotacoes()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")

    def salvar_dados(self):
        """Método vazio - todos os dados já são salvos em tempo real no Supabase"""
        print("💾 SistemaCambioPremium: Dados já persistidos em tempo real no Supabase")
        print("   ✅ Contas - Salvas em tempo real")
        print("   ✅ Transferências - Salvas em tempo real") 
        print("   ✅ Clientes - Salvos em tempo real")
        print("   ✅ Cotações - Salvas em tempo real")
        print("   ✅ Configurações - Salvas em tempo real")
        return True

    def carregar_contas_json_fallback(self):
        """Fallback para carregar contas do JSON se Supabase falhar"""
        contas_path = 'data/contas.json'
        if not os.path.exists(contas_path):
            print("📁 Criando arquivo de contas...")
            self.contas = {
                '183860837': {
                    'moeda': 'USD', 
                    'saldo': 10000.00,
                    'cliente': 'joao.silva', 
                    'cliente_nome': 'João Silva Comércio Ltda',
                    'data_criacao': '2024-01-15'
                },
                '487736769': {
                    'moeda': 'BRL', 
                    'saldo': 50000.00,
                    'cliente': 'joao.silva', 
                    'cliente_nome': 'João Silva Comércio Ltda',
                    'data_criacao': '2024-01-15'
                }
            }
            self.salvar_contas()
        else:
            with open(contas_path, 'r', encoding='utf-8') as f:
                self.contas = json.load(f)
            print(f"✅ {len(self.contas)} contas carregadas do arquivo JSON")

    def carregar_dados_cotacoes(self):
        """Carrega dados de cotações - PRIMEIRO Supabase, depois JSON fallback"""
        print("CARREGAR_DADOS_COTACOES CHAMADO!")
        
        try:
            # 🔥 NOVO: Tentar carregar do Supabase primeiro
            if hasattr(self, 'supabase') and self.supabase.conectado:
                self.carregar_cotacoes_supabase()
                return
            
            # 🔥 FALLBACK: Código original do JSON
            cotacoes_path = 'data/cotacoes_config.json'
            print(f"   Verificando arquivo: {cotacoes_path}")
            print(f"   Arquivo existe: {os.path.exists(cotacoes_path)}")
            
            if not os.path.exists(cotacoes_path):
                print("   Arquivo não existe - criando estruturas vazias")
                self.spreads_clientes = {}
                self.permissoes_cambio = {}
                self.limites_operacionais = {}
                self.horario_comercial_padrao = {
                    'dias_semana': [0, 1, 2, 3, 4],
                    'inicio': '10:00',
                    'fim': '15:00',
                    'fuso_horario': 'America/Sao_Paulo'
                }
                self.horarios_clientes = {}
                return
            
            print("   Lendo arquivo...")
            with open(cotacoes_path, 'r', encoding='utf-8') as f:
                dados_cotacoes = json.load(f)
            
            # ... (resto do código original permanece igual)
            # DEBUG DETALHADO DOS DADOS LIDOS
            print(f"   Dados lidos do arquivo:")
            print(f"      Spreads: {len(dados_cotacoes.get('spreads_clientes', {}))} clientes")
            print(f"      Permissões: {len(dados_cotacoes.get('permissoes_cambio', {}))} clientes")
            print(f"      Limites: {len(dados_cotacoes.get('limites_operacionais', {}))} clientes")
            print(f"      Horários: {len(dados_cotacoes.get('horarios_clientes', {}))} clientes")
            
            # ATRIBUIR DIRETAMENTE
            self.spreads_clientes = dados_cotacoes['spreads_clientes']
            self.permissoes_cambio = dados_cotacoes['permissoes_cambio'] 
            self.limites_operacionais = dados_cotacoes['limites_operacionais']
            
            # CARREGAR HORÁRIOS (com fallback)
            self.horario_comercial_padrao = dados_cotacoes.get('horario_comercial_padrao', {
                'dias_semana': [0, 1, 2, 3, 4],
                'inicio': '10:00',
                'fim': '15:00',
                'fuso_horario': 'America/Sao_Paulo'
            })
            
            self.horarios_clientes = dados_cotacoes.get('horarios_clientes', {})
            
            print("COTAÇÕES CARREGADAS DO JSON COM SUCESSO!")
            
        except Exception as e:
            print(f"ERRO CRÍTICO em carregar_dados_cotacoes: {e}")
            import traceback
            traceback.print_exc()
            # Garantir que as estruturas existam
            self.spreads_clientes = {}
            self.permissoes_cambio = {}
            self.limites_operacionais = {}
            self.horario_comercial_padrao = {
                'dias_semana': [0, 1, 2, 3, 4],
                'inicio': '10:00',
                'fim': '15:00',
                'fuso_horario': 'America/Sao_Paulo'
            }
            self.horarios_clientes = {}

    def salvar_dados_cotacoes(self):
        """Salva dados de cotações no arquivo - COM DEBUG DETALHADO"""
        try:
            dados = {
                'spreads_clientes': self.spreads_clientes,
                'permissoes_cambio': self.permissoes_cambio,
                'limites_operacionais': self.limites_operacionais,
                'horario_comercial_padrao': self.horario_comercial_padrao,
                'horarios_clientes': self.horarios_clientes
            }
            
            # Criar diretório se não existir
            os.makedirs('data', exist_ok=True)
            
            # Salvar arquivo
            caminho_arquivo = 'data/cotacoes_config.json'
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            
            print("💾 DADOS COTAÇÕES SALVOS:")
            print(f"   📊 Spreads: {len(self.spreads_clientes)} clientes")
            print(f"   🔒 Permissões: {len(self.permissoes_cambio)} clientes") 
            print(f"   💰 Limites: {len(self.limites_operacionais)} clientes")
            print(f"   🕒 Horários personalizados: {len(self.horarios_clientes)} clientes")
            print(f"   📁 Horários salvos: {list(self.horarios_clientes.keys())}")
            
            # 🔥 DEBUG EXTRA: Verificar conteúdo salvo
            print("🔍 CONTEÚDO SALVO:")
            for username, horario in self.horarios_clientes.items():
                print(f"   👤 {username}: {horario.get('dias_semana', [])} {horario.get('inicio', '')}-{horario.get('fim', '')}")
            
            # 🔥 VERIFICAR SE ARQUIVO FOI CRIADO
            if os.path.exists(caminho_arquivo):
                print(f"✅ Arquivo criado: {caminho_arquivo}")
                tamanho = os.path.getsize(caminho_arquivo)
                print(f"📏 Tamanho do arquivo: {tamanho} bytes")
            else:
                print(f"❌ Arquivo NÃO criado: {caminho_arquivo}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar dados de cotações: {e}")
            import traceback
            traceback.print_exc()
            return False

    def parse_data_unificada(self, data_str):
        """Parseia datas em vários formatos diferentes - VERSÃO SUPER TOLERANTE"""
        import datetime  # 🔥 Adicione esta linha se não tiver import
        
        if not data_str or data_str == 'None' or data_str == '':
            return None
        
        print(f"🔍 PARSING DATA: '{data_str}'")
        
        try:
            # Remover espaços extras
            data_str = str(data_str).strip()
            
            # Se já for datetime, retornar
            if isinstance(data_str, datetime.datetime):
                return data_str
            
            # 🔥🔥🔥 FORMATOS NA ORDEM CORRETA (mais comuns primeiro)
            formatos = [
                "%Y-%m-%d %H:%M:%S.%f",      # 2025-12-01 19:22:29.684899 (SEU CASO!)
                "%Y-%m-%dT%H:%M:%S.%f",      # 2025-12-01T19:22:29.684899
                "%Y-%m-%d %H:%M:%S",         # 2025-12-01 19:22:29
                "%Y-%m-%dT%H:%M:%S",         # 2025-12-01T19:22:29
                "%d/%m/%Y %H:%M:%S",         # 01/12/2025 19:22:29
                "%d/%m/%Y",                  # 01/12/2025
                "%Y-%m-%d",                  # 2025-12-01
            ]
            
            for formato in formatos:
                try:
                    parsed = datetime.datetime.strptime(data_str, formato)
                    print(f"✅ Data '{data_str}' parseada com formato '{formato}': {parsed}")
                    return parsed
                except ValueError:
                    continue
            
            print(f"⚠️ Nenhum formato funcionou para: '{data_str}'")
            return None
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO parseando data '{data_str}': {e}")
            return None

    def cadastrar_usuario_existente(self, usuario, senha_hash, dados):
        """Método auxiliar para cadastrar usuário já validado"""
        try:
            self.usuarios[usuario] = {
                'senha': senha_hash,
                'tipo': 'cliente',
                'nome': dados['nome'],
                'email': dados['email'],
                'documento': dados.get('documento', ''),
                'telefone': dados.get('telefone', ''),
                'endereco': dados.get('endereco', ''),        # 🔥
                'cidade': dados.get('cidade', ''),            # 🔥
                'cep': dados.get('cep', ''),                  # 🔥
                'estado': dados.get('estado', ''),            # 🔥
                'pais': dados.get('pais', ''),                # 🔥
                'contas': [],
                'data_cadastro': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            
            # Criar contas baseadas nas moedas selecionadas
            moedas_selecionadas = dados.get('moedas_selecionadas', [])
            if moedas_selecionadas:
                self.criar_contas_cliente(usuario, dados['nome'], moedas_selecionadas)
            
            # 🔥🔥🔥 CORREÇÃO: DESATIVAR CÂMBIO PARA NOVOS CLIENTES
            self.permissoes_cambio[usuario] = False
            
            # 🔥 SALVAR NO SUPABASE - AGORA COM DADOS COMPLETOS
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    # Preparar dados para Supabase
                    dados_supabase = {
                        'username': usuario,
                        'email': dados['email'],
                        'senha_hash': senha_hash,
                        'nome': dados['nome'],
                        'telefone': dados.get('telefone', ''),
                        'endereco': dados.get('endereco', ''),
                        'cidade': dados.get('cidade', ''),
                        'cep': dados.get('cep', ''),
                        'estado': dados.get('estado', ''),
                        'pais': dados.get('pais', ''),
                        'tipo': 'cliente',
                        'status': 'ativo',
                        'verificado': True,
                        'cambio_liberado': False,  # 🔥 Câmbio desativado
                        'data_cadastro': datetime.datetime.now().isoformat()
                    }
                    
                    # Adicionar hash do documento se existir
                    if 'documento' in dados and dados['documento']:
                        import hashlib
                        dados_supabase['documento_hash'] = hashlib.sha256(dados['documento'].encode()).hexdigest()
                    
                    # Verificar se já existe
                    response_existe = self.supabase.client.table('usuarios')\
                        .select('id')\
                        .eq('username', usuario)\
                        .execute()
                    
                    if response_existe.data:
                        # Atualizar existente
                        response = self.supabase.client.table('usuarios')\
                            .update(dados_supabase)\
                            .eq('username', usuario)\
                            .execute()
                    else:
                        # Inserir novo
                        response = self.supabase.client.table('usuarios')\
                            .insert(dados_supabase)\
                            .execute()
                    
                    if response.data:
                        print(f"✅ Usuário {usuario} salvo no Supabase com todos os dados!")
                        self.supabase.salvar_permissao_cambio(usuario, False)
                    else:
                        print(f"⚠️ Erro ao salvar usuário no Supabase")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao salvar usuário completo no Supabase: {e}")
            
            # 🔥 SALVAR LOCALMENTE
            self.salvar_dados_cotacoes()
            
            self.salvar_usuarios()
            print(f"✅ Usuário {usuario} cadastrado com sucesso via verificação")
            return True, "Usuário cadastrado com sucesso"
            
        except Exception as e:
            print(f"❌ Erro ao cadastrar usuário existente: {e}")
            return False, str(e)

    def reenviar_codigo_verificacao(self, email):
        """Reenvia código de verificação"""
        if email not in self.usuarios_nao_verificados:
            return False, "Email não encontrado"
        
        codigo = self.gerar_codigo_verificacao()
        self.codigos_verificacao[email] = {
            'codigo': codigo,
            'timestamp': time.time()
        }
        
        # 🔥 MODO SIMULAÇÃO
        print(f"🎯 MODO SIMULAÇÃO: NOVO código para {email}: {codigo}")
        
        return True, "Código reenviado com sucesso!"




    def configuracoes_padrao(self):
        """Configurações padrão do sistema - MESMA ESTRUTURA DA TELA"""
        return {
            'sistema': {
                'moedas_suportadas': ['USD', 'EUR', 'GBP', 'BRL'],
                'horario_abertura': '09:00',
                'horario_fechamento': '18:00',
                'dias_operacao': ['segunda', 'terca', 'quarta', 'quinta', 'sexta'],
                'timezone': 'America/Sao_Paulo'
            },
            'financeiras': {
                'limite_transferencia_diario': 10000.00,
                'limite_transferencia_mensal': 50000.00,
                'taxa_transferencia_internacional': 0.02,
                'comissao_minima': 10.00,
                'taxas_cambio': self.taxas_cambio  # 🔥 AGORA self.taxas_cambio JÁ EXISTE
            },
            'seguranca': {
                'tamanho_minimo_senha': 8,
                'expiracao_senha_dias': 90,
                'tentativas_login': 3,
                'bloqueio_temporario_minutos': 30,
                'requer_2fa': False,
                'notificacao_email': True
            },
            'interface': {
                'tema': 'escuro',
                'idioma': 'pt-BR',
                'moeda_padrao': 'USD',
                'casas_decimais': 2,
                'formato_data': 'DD/MM/AAAA'
            },
                'interface': {
                'tema': 'escuro',
                'temas_disponiveis': ['escuro', 'claro', 'azul', 'verde', 'roxo'],
                'idioma': 'pt-BR',
                'moeda_padrao': 'USD',
                'casas_decimais': 2,
                'formato_data': 'DD/MM/AAAA'
            }
        }
    
    def salvar_configuracoes(self):
        """Salva as configurações no arquivo"""
        try:
            with open('data/configuracoes.json', 'w', encoding='utf-8') as f:
                json.dump(self.configuracoes, f, indent=4, ensure_ascii=False)
            print("Configurações salvas com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def hash_documento(self, documento):
        """Hash para documentos sensíveis"""
        if not documento:
            return ""
        salt = "cambio_dev_salt_2024"
        import hashlib
        return hashlib.sha256(f"{documento}{salt}".encode()).hexdigest()

    def salvar_usuarios(self):
        with open('data/usuarios.json', 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, indent=4, ensure_ascii=False)
    
    def salvar_contas(self):
        """Salva as contas - COM ARREDONDAMENTO CORRETO"""
        try:
            # 🔥 ARREDONDAR TODOS OS SALDOS ANTES DE SALVAR
            for conta_num, conta_info in self.contas.items():
                if 'saldo' in conta_info:
                    conta_info['saldo'] = self.arredondar_valor(conta_info['saldo'])
            
            with open('data/contas.json', 'w', encoding='utf-8') as f:
                json.dump(self.contas, f, indent=4, ensure_ascii=False)
            
            print(f"✅ {len(self.contas)} contas salvas (valores arredondados)")
        except Exception as e:
            print(f"❌ Erro ao salvar contas: {e}")
    
    def fazer_login(self, usuario, senha):
        """Faz login do usuário - VERSÃO SUPABASE + LOCAL"""
        print(f"🔐 Tentando login para: {usuario}")
        
        # 1. PRIMEIRO: Tentar login via Supabase
        try:
            print("📤 Verificando no Supabase...")
            resultado_supabase = self.login_supabase(usuario, senha)
            
            if resultado_supabase['sucesso']:
                print(f"✅✅✅ LOGIN SUPABASE BEM-SUCEDIDO!")
                self.usuario_logado = usuario
                self.tipo_usuario_logado = resultado_supabase.get('tipo', 'cliente')
                
                # 🔥 ATUALIZAR CACHE LOCAL
                self.usuarios[usuario] = resultado_supabase.get('usuario_data', {})
                
                return True
            else:
                print(f"⚠️ Login Supabase falhou: {resultado_supabase.get('erro')}")
        except Exception as e:
            print(f"⚠️ Erro ao tentar Supabase: {e}")
        
        # 2. DEPOIS: Tentar login local (fallback)
        print("🔄 Tentando login local...")
        if usuario in self.usuarios:
            usuario_data = self.usuarios[usuario]
            
            # Verificar senha
            senha_armazenada = usuario_data.get('senha') or usuario_data.get('senha_hash', '')
            senha_hash = self.hash_senha(senha)
            
            if senha_armazenada == senha_hash:
                self.usuario_logado = usuario
                self.tipo_usuario_logado = usuario_data.get('tipo', 'cliente')
                print(f"✅ Login local bem-sucedido: {usuario}")
                return True
        
        print(f"❌ Login falhou para: {usuario}")
        return False
    
    def login_supabase(self, username, senha):
        """Faz login usando Supabase - RETORNA SIMPLES"""
        try:
            # Hash da senha para comparar
            senha_hash = self.hash_senha(senha)
            
            # Conectar ao Supabase
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                return {'sucesso': False, 'erro': 'Supabase não configurado'}
            
            from supabase import create_client
            supabase = create_client(url, key)
            
            # Buscar usuário
            response = supabase.table('usuarios')\
                .select('senha_hash, verificado, status, tipo, nome, email, contas')\
                .eq('username', username)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                return {'sucesso': False, 'erro': 'Usuário não encontrado'}
            
            usuario_data = response.data[0]
            
            # Verificar se está verificado
            if not usuario_data.get('verificado', False):
                return {'sucesso': False, 'erro': 'Email não verificado'}
            
            # Verificar senha
            if usuario_data['senha_hash'] != senha_hash:
                return {'sucesso': False, 'erro': 'Senha incorreta'}
            
            # ✅ Login bem-sucedido!
            return {
                'sucesso': True,
                'usuario_data': {
                    'username': username,
                    'nome': usuario_data.get('nome', ''),
                    'email': usuario_data.get('email', ''),
                    'senha_hash': usuario_data['senha_hash'],
                    'tipo': usuario_data.get('tipo', 'cliente'),
                    'verificado': usuario_data.get('verificado', False),
                    'status': usuario_data.get('status', 'ativo'),
                    'contas': usuario_data.get('contas', [])
                },
                'tipo': usuario_data.get('tipo', 'cliente')
            }
            
        except Exception as e:
            return {'sucesso': False, 'erro': f'Erro: {str(e)}'}
    
    def calcular_saldos_usuario(self):
        """Calcula saldos por moeda do usuário logado - VERSÃO SUPABASE + LOCAL"""
        if not self.usuario_logado:
            print("❌ Nenhum usuário logado para calcular saldos")
            return {}
        
        usuario_data = self.usuarios.get(self.usuario_logado, {})
        contas_usuario = usuario_data.get('contas', [])
        
        print(f"🔍 Calculando saldos para: {self.usuario_logado}")
        print(f"📋 IDs das contas do usuário: {contas_usuario}")
        
        saldos = {}
        
        # 1. PRIMEIRO: Tentar carregar do Supabase
        try:
            print("📤 Tentando carregar contas do Supabase...")
            
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if url and key and contas_usuario:
                from supabase import create_client
                supabase = create_client(url, key)
                
                # Buscar cada conta pelo ID no Supabase
                for conta_id in contas_usuario:
                    response = supabase.table('contas')\
                        .select('moeda, saldo')\
                        .eq('id', conta_id)\
                        .execute()
                    
                    if response.data and len(response.data) > 0:
                        conta_data = response.data[0]
                        moeda = conta_data['moeda']
                        saldo = float(conta_data['saldo'])
                        
                        print(f"   ✅ Conta {conta_id} no Supabase: {moeda} = {saldo}")
                        
                        # Atualizar cache local
                        if conta_id not in self.contas:
                            self.contas[conta_id] = {
                                'moeda': moeda,
                                'saldo': saldo,
                                'cliente_username': self.usuario_logado
                            }
                        
                        # Somar ao saldo total da moeda
                        if moeda in saldos:
                            saldos[moeda] += saldo
                        else:
                            saldos[moeda] = saldo
                    else:
                        print(f"   ⚠️ Conta {conta_id} não encontrada no Supabase")
                
                print(f"💰 Saldos do Supabase: {saldos}")
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar do Supabase: {e}")
        
        # 2. DEPOIS: Complementar com dados locais
        print("🔄 Complementando com dados locais...")
        for conta_num in contas_usuario:
            if conta_num in self.contas:
                conta = self.contas[conta_num]
                moeda = conta['moeda']
                saldo = conta['saldo']
                
                print(f"   💳 Conta {conta_num} local: {moeda} = {saldo}")
                
                if moeda in saldos:
                    # Só adiciona se ainda não foi carregado do Supabase
                    pass  # Já temos do Supabase
                else:
                    saldos[moeda] = saldo
            else:
                print(f"   ⚠️ Conta {conta_num} não encontrada localmente")
        
        # 3. Se ainda não encontrou nada, verificar se o usuário tem contas no Supabase
        if not saldos and contas_usuario:
            print("🔍 Nenhuma conta encontrada, verificando diretamente no Supabase...")
            # Podemos tentar buscar todas as contas do usuário de uma vez
            try:
                import os
                from dotenv import load_dotenv
                load_dotenv()
                
                url = os.getenv('SUPABASE_URL')
                key = os.getenv('SUPABASE_KEY')
                
                if url and key:
                    from supabase import create_client
                    supabase = create_client(url, key)
                    
                    # Buscar todas as contas do usuário
                    response = supabase.table('contas')\
                        .select('moeda, saldo')\
                        .eq('cliente_username', self.usuario_logado)\
                        .execute()
                    
                    if response.data:
                        for conta in response.data:
                            moeda = conta['moeda']
                            saldo = float(conta['saldo'])
                            
                            if moeda in saldos:
                                saldos[moeda] += saldo
                            else:
                                saldos[moeda] = saldo
                        
                        print(f"💰 Saldos diretos do Supabase: {saldos}")
            except Exception as e:
                print(f"⚠️ Erro na busca direta: {e}")
        
        # 4. Ordenar as moedas
        ordem_moedas = ['USD', 'GBP', 'EUR', 'BRL']
        saldos_ordenados = {}
        
        for moeda in ordem_moedas:
            if moeda in saldos:
                saldos_ordenados[moeda] = saldos[moeda]
        
        # Adicionar outras moedas que não estão na ordem padrão
        for moeda, saldo in saldos.items():
            if moeda not in saldos_ordenados:
                saldos_ordenados[moeda] = saldo
        
        print(f"💰 Saldos finais ordenados: {saldos_ordenados}")
        return saldos_ordenados
    
    def salvar_transferencias(self):
        """Salva as transferências no arquivo JSON"""
        try:
            with open('data/transferencias.json', 'w', encoding='utf-8') as f:
                json.dump(self.transferencias, f, indent=4, ensure_ascii=False)
            print("✅ Transferências salvas")
        except Exception as e:
            print(f"❌ Erro ao salvar transferências: {e}")

    def carregar_transferencias(self):
        """Carrega as transferências do Supabase"""
        try:
            print("🔄 Carregando transferências do Supabase...")
            response = supabase.table('transferencias').select('*').execute()
            
            self.transferencias = {}
            for transf in response.data:
                self.transferencias[transf['id']] = transf
            
            print(f"✅ {len(self.transferencias)} transferências carregadas do Supabase")
            
        except Exception as e:
            print(f"❌ Erro ao carregar transferências do Supabase: {e}")
            # Fallback para JSON
            transferencias_path = 'data/transferencias.json'
            if os.path.exists(transferencias_path):
                with open(transferencias_path, 'r', encoding='utf-8') as f:
                    self.transferencias = json.load(f)
                print(f"✅ {len(self.transferencias)} transferências carregadas do JSON (fallback)")
            else:
                self.transferencias = {}
                print("✅ Arquivo de transferências criado")

    def solicitar_transferencia_internacional(self, dados_transferencia, usuario_solicitante=None):
        """Solicita uma transferência internacional - VERSÃO CORRIGIDA COM SUPABASE"""
        try:
            # Carregar transferências existentes
            self.carregar_transferencias()
            
            # Validar saldo
            conta_origem = dados_transferencia['conta_origem']
            valor = dados_transferencia['valor']
            
            if conta_origem not in self.contas:
                return False, "Conta de origem não encontrada"
            
            saldo_atual = self.contas[conta_origem]['saldo']
            taxa = 0.00  # Por enquanto sem taxa
            total = valor + taxa
            
            if saldo_atual < total:
                return False, f"Saldo insuficiente. Disponível: {saldo_atual:.2f}, Necessário: {total:.2f}"
            
            # Gerar ID único
            transferencia_id = str(random.randint(100000, 999999))
            while transferencia_id in self.transferencias:
                transferencia_id = str(random.randint(100000, 999999))
            
            # 🔥 MODIFICAÇÃO: Determinar quem solicitou
            if usuario_solicitante:
                # Admin agindo em nome do cliente
                solicitado_por = usuario_solicitante
                executado_por = self.usuario_logado  # Admin que executou
            else:
                # Cliente solicitando normalmente
                solicitado_por = self.usuario_logado
                executado_por = self.usuario_logado 
            
            # Criar transferência
            transferencia_data = {
                'id': transferencia_id,
                'conta_remetente': conta_origem,
                'valor': valor,
                'moeda': self.contas[conta_origem]['moeda'],
                'tipo': 'internacional',
                'finalidade': dados_transferencia['finalidade'],
                'descricao': dados_transferencia.get('descricao', ''),
                'status': 'pending',
                'data_solicitacao': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'solicitado_por': solicitado_por,  # 🔥 Pode ser cliente ou admin em nome do cliente
                'executado_por': executado_por,    # 🔥 Quem realmente executou a ação
                'taxa': taxa,
                'beneficiario': dados_transferencia['beneficiario'],
                'endereco_beneficiario': dados_transferencia['endereco'],
                'cidade': dados_transferencia['cidade'],
                'pais': dados_transferencia['pais'],
                'nome_banco': dados_transferencia['banco'],
                'endereco_banco': dados_transferencia.get('endereco_banco', ''),
                'cidade_banco': dados_transferencia.get('cidade_banco', ''),  # 🔥 NOVO
                'pais_banco': dados_transferencia.get('pais_banco', ''),      # 🔥 NOVO
                'codigo_swift': dados_transferencia['swift'],
                'iban_account': dados_transferencia['iban'],
                'aba_routing': dados_transferencia.get('aba', '')
            }
            
            # 🔥🔥🔥 CORREÇÃO CRÍTICA: DEBITAR PRIMEIRO LOCALMENTE
            saldo_antes = self.contas[conta_origem]['saldo']
            self.contas[conta_origem]['saldo'] -= valor
            saldo_depois = self.contas[conta_origem]['saldo']
            
            print(f"💰 SALDO ATUALIZADO LOCALMENTE: {saldo_antes:.2f} -> {saldo_depois:.2f}")
            
            # 🔥🔥🔥 NOVO: ATUALIZAR SALDO NO SUPABASE
            sucesso_supabase_saldo = self.atualizar_saldo_conta_supabase(conta_origem, saldo_depois)
            
            if not sucesso_supabase_saldo:
                print("⚠️ ATENÇÃO: Saldo não atualizado no Supabase, mas operação continua localmente")
            
            # 🔥🔥🔥 SALVAR TRANSFERÊNCIA NO SUPABASE
            print(f"🌍 Tentando salvar transferência {transferencia_id} no Supabase...")
            try:
                dados_supabase = {
                    'id': transferencia_id,
                    'tipo': 'transferencia_internacional',
                    'status': 'solicitada',
                    'data': datetime.datetime.now().isoformat(),
                    'moeda': self.contas[conta_origem]['moeda'],
                    'valor': valor,
                    'conta_remetente': conta_origem,
                    'descricao': dados_transferencia.get('descricao', ''),
                    'executado_por': executado_por,
                    'beneficiario': dados_transferencia['beneficiario'],
                    'endereco_beneficiario': dados_transferencia['endereco'],
                    'cidade': dados_transferencia['cidade'],
                    'pais': dados_transferencia['pais'],
                    'nome_banco': dados_transferencia['banco'],
                    'endereco_banco': dados_transferencia.get('endereco_banco', ''),
                    'cidade_banco': dados_transferencia.get('cidade_banco', ''),  # 🔥 NOVO
                    'pais_banco': dados_transferencia.get('pais_banco', ''),      # 🔥 NOVO
                    'codigo_swift': dados_transferencia['swift'],
                    'iban_account': dados_transferencia['iban'],
                    'aba_routing': dados_transferencia.get('aba', ''),
                    'finalidade': dados_transferencia['finalidade'],
                    'created_at': datetime.datetime.now().isoformat()
                }
                
                # Inserir no Supabase
                response = self.supabase.client.table('transferencias').insert(dados_supabase).execute()
                
                if response.data:
                    print(f"✅ Transferência {transferencia_id} salva no Supabase!")
                else:
                    print(f"⚠️ Transferência NÃO salva no Supabase: Dados não retornados")
            except Exception as e:
                print(f"⚠️ Erro ao salvar transferência no Supabase: {e}")
            
            # 🔥 CONTINUAR PROCESSO LOCAL (MESMO SE SUPABASE FALHAR)
            self.transferencias[transferencia_id] = transferencia_data
            
            # 🔥 SALVAR TUDO LOCALMENTE
            self.salvar_contas()
            self.salvar_transferencias()
            
            print(f"✅ Transferência {transferencia_id} criada e valor debitado")
            print(f"👤 Solicitado por: {solicitado_por}")
            print(f"🔧 Executado por: {executado_por}")
            return True, transferencia_id
            
        except Exception as e:
            print(f"❌ Erro ao solicitar transferência: {e}")
            return False, str(e)

    def obter_beneficiarios_cliente(self):
        """Retorna lista de beneficiários do cliente - SIMULAÇÃO"""
        # Por enquanto retorna lista vazia - podemos implementar depois
        return []

    # No seu arquivo do sistema (sistema.py)
      
    # ===== nova função para salvar beneficiários =====
    def salvar_beneficiario(self, dados_beneficiario):
        """Salva um beneficiário para o usuário logado - AGORA COM SUPABASE"""
        try:
            print(f"🔍 DEBUG SALVAR_BENEFICIARIO - Tipo: {type(dados_beneficiario)}")
            print(f"🔍 DEBUG SALVAR_BENEFICIARIO - Dados: {dados_beneficiario}")
            print(f"🔍 TEM cidade_banco? {'cidade_banco' in dados_beneficiario}")
            print(f"🔍 TEM pais_banco? {'pais_banco' in dados_beneficiario}")
            
            # 🔥 CORREÇÃO: self.usuario_logado é string, usar diretamente
            usuario_atual = self.usuario_logado  # Já é o username como string
            
            print(f"🔍 Usuário atual: {usuario_atual} (tipo: {type(usuario_atual)})")
            print(f"🔍 Valor cidade_banco: {dados_beneficiario.get('cidade_banco', 'NÃO ENCONTRADO')}")
            print(f"🔍 Valor pais_banco: {dados_beneficiario.get('pais_banco', 'NÃO ENCONTRADO')}")
            
            # Verificar se é um dicionário
            if not isinstance(dados_beneficiario, dict):
                print(f"❌ ERRO: dados_beneficiario não é dicionário, é: {type(dados_beneficiario)}")
                return False
            
            if usuario_atual not in self.beneficiarios:
                self.beneficiarios[usuario_atual] = []
            
            # Verificar se o beneficiário já existe
            for benef in self.beneficiarios[usuario_atual]:
                if benef['nome'] == dados_beneficiario['nome'] and benef['iban'] == dados_beneficiario['iban']:
                    print(f"ℹ️ Beneficiário '{dados_beneficiario['nome']}' já existe")
                    return True
            
            # 🔥 PRIMEIRO: Salvar no Supabase
            sucesso_supabase = self.salvar_beneficiario_supabase(dados_beneficiario)
            
            # 🔥 SEGUNDO: Salvar localmente (mesmo se Supabase falhar)
            self.beneficiarios[usuario_atual].append(dados_beneficiario)
            self.salvar_beneficiarios()  # Salva no JSON
            
            if sucesso_supabase:
                print(f"✅ Beneficiário '{dados_beneficiario['nome']}' salvo no Supabase e localmente!")
            else:
                print(f"⚠️ Beneficiário '{dados_beneficiario['nome']}' salvo apenas localmente (Supabase falhou)")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar beneficiário: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def salvar_beneficiarios(self):
        """Salva os beneficiários no arquivo JSON"""
        try:
            with open('data/beneficiarios.json', 'w', encoding='utf-8') as f:
                json.dump(self.beneficiarios, f, indent=4, ensure_ascii=False)
            print(f"✅ {sum(len(b) for b in self.beneficiarios.values())} beneficiários salvos")
        except Exception as e:
            print(f"❌ Erro ao salvar beneficiários: {e}")   

    def cadastrar_cliente(self, dados_cliente):
        """Cadastra um novo cliente no sistema - ATUALIZADO PARA NOVO SISTEMA DE MOEDAS"""
        try:
            # Validar dados obrigatórios
            campos_obrigatorios = ['username', 'senha', 'nome', 'email', 'documento']
            for campo in campos_obrigatorios:
                if not dados_cliente.get(campo):
                    return False, f"Campo obrigatório faltando: {campo}"
            
            username = dados_cliente['username']
            
            # Verificar se usuário já existe
            if username in self.usuarios:
                return False, "Usuário já existe"
            
            # Criar cliente
            self.usuarios[username] = {
                'senha': self.hash_senha(dados_cliente['senha']),
                'tipo': 'cliente',
                'nome': dados_cliente['nome'],
                'email': dados_cliente['email'],
                'documento': dados_cliente['documento'],
                'telefone': dados_cliente.get('telefone', ''),
                'contas': [],
                'data_cadastro': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            
            # Criar contas baseadas nas moedas selecionadas
            moedas_selecionadas = dados_cliente.get('moedas_selecionadas', [])
            if moedas_selecionadas:
                self.criar_contas_cliente(username, dados_cliente['nome'], moedas_selecionadas)
            
            self.salvar_usuarios()
            print(f"✅ Cliente {username} cadastrado com sucesso")
            print(f"💰 Moedas criadas: {', '.join(moedas_selecionadas)}")
            return True, "Cliente cadastrado com sucesso"
            
        except Exception as e:
            print(f"❌ Erro ao cadastrar cliente: {e}")
            return False, str(e)
    
    def criar_contas_cliente(self, username, nome_cliente, moedas):
        """Cria contas para um cliente localmente e no Supabase"""
        contas_criadas = []
        
        for moeda in moedas:
            # Gerar número de conta único
            while True:
                numero_conta = str(random.randint(100000000, 999999999))
                if numero_conta not in self.contas:
                    break
            
            # Criar conta localmente
            self.contas[numero_conta] = {
                'numero': numero_conta,
                'cliente_nome': nome_cliente,
                'cliente_id': username,
                'moeda': moeda,
                'saldo': 0.0,
                'tipo': 'corrente',
                'data_criacao': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Adicionar conta ao usuário
            self.usuarios[username]['contas'].append(numero_conta)
            contas_criadas.append(numero_conta)
            
            print(f"✅ Conta {numero_conta} criada em {moeda} para {username}")
        
        # 🔥 NOVO: Criar contas no Supabase também
        if hasattr(self, 'supabase') and self.supabase.conectado:
            try:
                supabase_contas = self.supabase.criar_contas_supabase(username, nome_cliente, moedas)
                print(f"✅ {len(supabase_contas)} contas criadas no Supabase")
            except Exception as e:
                print(f"⚠️ Contas criadas localmente, mas erro no Supabase: {e}")
        
        return contas_criadas
    
    def listar_clientes(self):
        """Retorna lista de todos os clientes"""
        clientes = []
        for username, dados in self.usuarios.items():
            if dados['tipo'] == 'cliente':
                cliente_info = {
                    'username': username,
                    'nome': dados['nome'],
                    'email': dados['email'],
                    'documento': dados.get('documento', ''),
                    'telefone': dados.get('telefone', ''),
                    'data_cadastro': dados.get('data_cadastro', ''),
                    'quantidade_contas': len(dados.get('contas', [])),
                    'contas': dados.get('contas', [])
                }
                clientes.append(cliente_info)
        return clientes
    
# === MÉTODOS PARA O SISTEMA (adicionar ao arquivo do sistema) ===

    def adicionar_invoice_info_transferencia(self, transferencia_id, caminho_arquivo):
        """Adiciona informações da invoice à transferência - AGORA SALVA NO SUPABASE TAMBÉM"""
        try:
            if transferencia_id not in self.transferencias:
                return False
            
            print(f"🔍 ADICIONAR INVOICE INFO - Caminho recebido: {caminho_arquivo}")
            
            # 🔥 CORREÇÃO CRÍTICA: Verificar e converter caminho se necessário
            caminho_final = caminho_arquivo
            
            # Se o caminho for local (data/invoices), extrair apenas o nome do arquivo
            # e criar caminho do Supabase
            if caminho_arquivo and 'data/invoices' in caminho_arquivo:
                import os
                # Extrair nome do arquivo do caminho local
                nome_arquivo = os.path.basename(caminho_arquivo)
                # Criar caminho do Supabase no formato correto
                caminho_final = f"transferencias/{transferencia_id}/{nome_arquivo}"
                print(f"🔄 Convertendo caminho local para Supabase: {caminho_final}")
            
            # 🔥 DADOS DA INVOICE (usar caminho_final corrigido)
            invoice_data = {
                'status': 'pending',  # 🔥 SEMPRE VOLTA PARA PENDENTE NO REENVIO
                'caminho_arquivo': caminho_final,  # 🔥 AGORA SEMPRE CAMINHO DO SUPABASE
                'data_upload': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'motivo_recusa': None,  # 🔥 LIMPAR MOTIVO DA RECUSA ANTERIOR
                'data_recusa': None     # 🔥 LIMPAR DATA DA RECUSA ANTERIOR
            }
            
            print(f"📊 Dados da invoice a serem salvos:")
            print(f"   Status: {invoice_data['status']}")
            print(f"   Caminho: {invoice_data['caminho_arquivo']}")
            print(f"   Data Upload: {invoice_data['data_upload']}")
            
            # 1. SALVAR LOCALMENTE
            self.transferencias[transferencia_id]['invoice_info'] = invoice_data
            self.salvar_transferencias()
            
            # 2. 🔥 SALVAR NO SUPABASE TAMBÉM
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('transferencias')\
                        .update({'invoice_info': invoice_data})\
                        .eq('id', transferencia_id)\
                        .execute()
                    
                    if response.data:
                        print(f"✅ Invoice salva no Supabase também!")
                        print(f"   Caminho salvo: {invoice_data['caminho_arquivo']}")
                    else:
                        print(f"⚠️ Erro ao salvar invoice no Supabase: Dados não retornados")
                        print(f"   Error: {response.error if hasattr(response, 'error') else 'N/A'}")
                except Exception as e:
                    print(f"⚠️ Erro Supabase: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("ℹ️ Supabase não disponível, salvando apenas localmente")
            
            print(f"✅ Nova invoice adicionada para transferência {transferencia_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar invoice info: {e}")
            import traceback
            traceback.print_exc()
            return False

    def listar_arquivos_pasta(self, transferencia_id):
        """Lista todos os arquivos na pasta da transferência (para debug)"""
        try:
            sistema = App.get_running_app().sistema
            
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                # O Supabase não tem listagem direta por pasta via API Python
                # Mas podemos usar uma abordagem alternativa:
                
                # 🔥 ALTERNATIVA 1: Usar o campo invoice_info no banco
                info = sistema.obter_info_invoice(transferencia_id)
                if info and info.get('caminho_arquivo'):
                    print(f"📁 Arquivo na pasta {transferencia_id}:")
                    print(f"   • {info['caminho_arquivo']} (status: {info.get('status', 'unknown')})")
                    return [info['caminho_arquivo']]
                
                # 🔥 ALTERNATIVA 2: Se tiver muitos arquivos, precisaria de uma tabela de registro
                print(f"ℹ️ Nenhum arquivo registrado para {transferencia_id}")
                return []
                
            else:
                print("⚠️ Supabase não disponível")
                return []
                
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
            return []

    def aprovar_invoice(self, transferencia_id):
        """Aprova uma invoice - NÃO altera status da transferência - VERSÃO SUPABASE"""
        try:
            # 🔥 CORREÇÃO: Atualizar invoice_info no Supabase MANTENDO caminho_arquivo
            # 1. Buscar dados atuais da invoice
            invoice_atual = self.obter_info_invoice(transferencia_id)
            
            # 2. Manter todos os campos existentes + atualizar status
            invoice_data = {
                'status': 'approved',
                'motivo_recusa': '',
                'data_upload': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                # 🔥 CORREÇÃO CRÍTICA: MANTER O CAMINHO DO ARQUIVO
                'caminho_arquivo': invoice_atual.get('caminho_arquivo') if invoice_atual else None
            }
            
            update_data = {
                'invoice_info': invoice_data
            }
            
            response = self.supabase.client.table('transferencias')\
                .update(update_data)\
                .eq('id', transferencia_id)\
                .execute()
            
            if response.data:
                print(f"✅ Invoice aprovada no Supabase para transferência {transferencia_id}")
                
                # 🔥 CORREÇÃO: Sincronizar dados locais
                if transferencia_id in self.transferencias and 'invoice_info' in self.transferencias[transferencia_id]:
                    self.transferencias[transferencia_id]['invoice_info']['status'] = 'approved'
                    self.transferencias[transferencia_id]['invoice_info']['motivo_recusa'] = ''
                    self.salvar_transferencias()
                
                return True
            else:
                print(f"❌ Erro ao aprovar invoice no Supabase: Dados não retornados")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao aprovar invoice: {e}")
            return False

    def recusar_invoice(self, transferencia_id, motivo):
        """Recusa uma invoice e DELETA o arquivo do Storage"""
        try:
            sistema = App.get_running_app().sistema
            
            # 🔥 PRIMEIRO: Buscar dados atuais para guardar o caminho
            response = sistema.supabase.client.table('transferencias')\
                .select('invoice_info')\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response.data:
                print(f"❌ Transferência {transferencia_id} não encontrada")
                return False
            
            current_invoice_info = response.data[0].get('invoice_info', {})
            caminho_arquivo = current_invoice_info.get('caminho_arquivo')
            
            # 🔥 SEGUNDO: Deletar arquivo físico do Storage se existir
            if caminho_arquivo and sistema.supabase.conectado:
                print(f"🗑️ Recusa: Deletando arquivo físico: {caminho_arquivo}")
                
                # Extrair apenas o nome do arquivo do caminho
                try:
                    # Tenta deletar o arquivo
                    delete_response = sistema.supabase.client.storage.from_("invoices")\
                        .remove([caminho_arquivo])
                    
                    if delete_response:
                        print(f"✅ Arquivo deletado do Storage: {caminho_arquivo}")
                    else:
                        print(f"⚠️ Arquivo não encontrado no Storage (pode já ter sido deletado)")
                except Exception as delete_error:
                    print(f"⚠️ Erro ao deletar arquivo (continuando): {delete_error}")
            
            # 🔥 TERCEIRO: Atualizar status no banco (MANTÉM caminho vazio)
            update_data = {
                'invoice_info': {
                    'status': 'rejected',
                    'motivo_recusa': motivo,
                    'data_recusa': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'caminho_arquivo': None,  # 🔥 AGORA FICA None/NULL
                    'data_upload': current_invoice_info.get('data_upload'),
                    'caminho_antigo': caminho_arquivo  # 🔥 Guarda referência do que foi deletado
                }
            }
            
            response_update = sistema.supabase.client.table('transferencias')\
                .update(update_data)\
                .eq('id', transferencia_id)\
                .execute()
            
            if response_update.data:
                print(f"✅ Invoice recusada e arquivo deletado: {transferencia_id}")
                print(f"📝 Motivo: {motivo}")
                
                # Sincronizar dados locais
                if transferencia_id in sistema.transferencias:
                    sistema.transferencias[transferencia_id]['invoice_info'] = update_data['invoice_info']
                    sistema.salvar_transferencias()
                
                return True
            else:
                print(f"❌ Erro ao atualizar status no banco")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao recusar e deletar invoice: {e}")
            return False

    def obter_info_invoice(self, transferencia_id):
        """Obtém informações da invoice - SUPABASE (VERSÃO CORRIGIDA)"""
        try:
            # 1. PRIMEIRO: Buscar no Supabase (SEMPRE buscar dados atualizados)
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    print(f"🔍 BUSCANDO INVOICE NO SUPABASE: {transferencia_id}")
                    response = self.supabase.client.table('transferencias')\
                        .select('invoice_info')\
                        .eq('id', transferencia_id)\
                        .execute()
                    
                    print(f"🔍 RESPOSTA SUPABASE INVOICE: {response.data}")
                    
                    if response.data and len(response.data) > 0:
                        invoice_data = response.data[0].get('invoice_info')
                        
                        # 🔥 CORREÇÃO: Se invoice_data é None, criar estrutura vazia
                        if invoice_data is None:
                            print(f"ℹ️ INVOICE É None para: {transferencia_id}")
                            return None
                        
                        # 🔥 CORREÇÃO: Garantir que é um dicionário
                        if not isinstance(invoice_data, dict):
                            print(f"⚠️ INVOICE não é dicionário: {type(invoice_data)} - Convertendo...")
                            # Tentar converter se for string JSON
                            if isinstance(invoice_data, str):
                                import json
                                try:
                                    invoice_data = json.loads(invoice_data)
                                except:
                                    return None
                            else:
                                return None
                        
                        # 🔥 CORREÇÃO: Garantir estrutura mínima
                        if 'status' not in invoice_data:
                            invoice_data['status'] = 'no_invoice'
                        
                        print(f"✅ INVOICE ENCONTRADA: status={invoice_data.get('status')}, caminho={invoice_data.get('caminho_arquivo')}")
                        
                        # 🔥 CORREÇÃO: Retornar APENAS campos relevantes (sem motivo_recusa vazio)
                        info_limpa = {
                            'status': invoice_data.get('status'),
                            'data_upload': invoice_data.get('data_upload')
                        }
                        
                        # 🔥 Só incluir motivo_recusa se não for vazio
                        if invoice_data.get('motivo_recusa'):
                            info_limpa['motivo_recusa'] = invoice_data['motivo_recusa']
                        
                        # 🔥 Só incluir caminho_arquivo se existir
                        if invoice_data.get('caminho_arquivo'):
                            info_limpa['caminho_arquivo'] = invoice_data['caminho_arquivo']
                        
                        # 🔥 ATUALIZAR OS DADOS LOCAIS PARA SINCRONIZAÇÃO
                        if transferencia_id in self.transferencias:
                            self.transferencias[transferencia_id]['invoice_info'] = info_limpa
                        
                        return info_limpa
                    else:
                        print(f"❌ NENHUMA INVOICE NO SUPABASE PARA: {transferencia_id}")
                        return None
                        
                except Exception as e:
                    print(f"⚠️ Erro ao buscar invoice no Supabase: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
            
            print(f"❌ SUPABASE NÃO DISPONÍVEL PARA: {transferencia_id}")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter info invoice: {e}")
            import traceback
            traceback.print_exc()
            return None

    def transferencia_tem_invoice(self, transferencia_id):
        """Verifica se a transferência tem uma invoice VÁLIDA (não recusada)"""
        try:
            info_invoice = self.obter_info_invoice(transferencia_id)
            if not info_invoice:
                return False
            
            # 🔥 CONSIDERAR APENAS INVOICES COM ARQUIVOS EXISTENTES
            if info_invoice['status'] == 'rejected' and info_invoice.get('caminho_arquivo') is None:
                return False
            
            # 🔥 CORREÇÃO: Para invoices no Supabase, não verificar arquivo local
            # Se tem caminho no Supabase, considerar que existe
            if info_invoice.get('caminho_arquivo'):
                # Verificar se é caminho do Supabase (começa com 'transferencias/' ou 'invoices/')
                caminho = info_invoice['caminho_arquivo']
                if caminho.startswith(('transferencias/', 'invoices/', 'data/invoices')):
                    return True  # ✅ Arquivo existe no Supabase Storage
                else:
                    # Fallback: verificar se é arquivo local (durante transição)
                    import os
                    return os.path.exists(info_invoice['caminho_arquivo'])
            
            return info_invoice['status'] in ['pending', 'approved']
            
        except Exception:
            return False
        
# === MÉTODOS PARA O SISTEMA (metodos contábeis) ===

    def debug_contas_contabeis(self):
        """Debug para verificar o estado das contas contábeis"""
        print("=== 🔍 DEBUG CONTAS CONTÁBEIS ===")
        
        # Verificar contas de receita
        print("💰 CONTAS DE RECEITA:")
        for categoria, contas in self.contas_contabeis['receitas'].items():
            print(f"  📁 {categoria}:")
            for conta_nome, dados in contas.items():
                print(f"    • {conta_nome}: {dados['saldo']:,.2f} {dados['moeda']}")
        
        # Verificar wire fee especificamente
        if 'Wire Fee' in self.contas_contabeis['receitas']:
            print("🔍 WIRE FEE DETALHADO:")
            for conta_nome, dados in self.contas_contabeis['receitas']['Wire Fee'].items():
                print(f"    • {conta_nome}: {dados['saldo']:,.2f} {dados['moeda']}")
        
        print("=== 🎯 FIM DEBUG ===")

    def criar_conta_receita(self, categoria, nome_conta, moeda):
        """Cria uma nova conta de receita na categoria especificada"""
        try:
            # Verificar se a categoria existe
            if categoria not in self.contas_contabeis['receitas']:
                self.contas_contabeis['receitas'][categoria] = {}
            
            # Verificar se a conta já existe na moeda
            if nome_conta in self.contas_contabeis['receitas'][categoria]:
                if moeda in self.contas_contabeis['receitas'][categoria][nome_conta]:
                    print(f"⚠️ Conta '{nome_conta}' já existe na moeda {moeda}")
                    return False
            else:
                self.contas_contabeis['receitas'][categoria][nome_conta] = {}
            
            # Criar conta com saldo zero na moeda especificada
            self.contas_contabeis['receitas'][categoria][nome_conta][moeda] = 0.0
            print(f"✅ Conta receita criada: {categoria} -> {nome_conta} -> {moeda} = 0.00")
            
            # 🔥 CORREÇÃO: IMPLEMENTAR SALVAR NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    dados_conta = {
                        'nome': nome_conta,
                        'categoria': categoria,
                        'tipo': 'receita',
                        'moeda': moeda,
                        'saldo': 0.0
                    }
                    
                    response = self.supabase.client.table('contas_contabeis').insert(dados_conta).execute()
                    
                    if response.data:
                        print(f"💾 Conta receita salva no Supabase: {response.data[0]['id']}")
                        return True
                    else:
                        print("❌ Erro ao salvar conta receita no Supabase")
                        return False
                        
                except Exception as e:
                    print(f"❌ Erro Supabase ao criar conta receita: {e}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar conta receita: {e}")
            return False

    def criar_conta_despesa(self, categoria, nome_conta, moeda):
        """Cria uma nova conta de despesa na categoria especificada"""
        try:
            # Verificar se a categoria existe
            if categoria not in self.contas_contabeis['despesas']:
                self.contas_contabeis['despesas'][categoria] = {}
            
            # Verificar se a conta já existe na moeda
            if nome_conta in self.contas_contabeis['despesas'][categoria]:
                if moeda in self.contas_contabeis['despesas'][categoria][nome_conta]:
                    print(f"⚠️ Conta '{nome_conta}' já existe na moeda {moeda}")
                    return False
            else:
                self.contas_contabeis['despesas'][categoria][nome_conta] = {}
            
            # Criar conta com saldo zero na moeda especificada
            self.contas_contabeis['despesas'][categoria][nome_conta][moeda] = 0.0
            print(f"✅ Conta despesa criada: {categoria} -> {nome_conta} -> {moeda} = 0.00")
            
            # Salvar no Supabase (se implementado)
            if hasattr(self, 'supabase') and self.supabase.conectado:
                # Implementar inserção no Supabase aqui
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar conta despesa: {e}")
            return False

    def lancar_receita(self, conta_cliente, valor, conta_receita, categoria_receita, descricao, moeda_receita=None):
        """Registra um lançamento de receita - VERSÃO MULTI-MOEDA COMPATÍVEL"""
        try:
            print(f"🔍 SISTEMA - LANÇAR RECEITA (MULTI-MOEDA):")
            print(f"  Conta Cliente: {conta_cliente}")
            print(f"  Valor: {valor}")
            print(f"  Conta Receita: {conta_receita}")
            print(f"  Categoria: {categoria_receita}")
            print(f"  Moeda Receita: {moeda_receita}")
            print(f"  Descrição: {descricao}")
            
            # Verificar se a conta do cliente existe
            if conta_cliente not in self.contas:
                return False, "Conta do cliente não encontrada!"
            
            # 🔥 CORREÇÃO: Obter moeda da conta do cliente
            moeda_cliente = self.contas[conta_cliente]['moeda']
            
            # 🔥 CORREÇÃO: Se moeda_receita não foi passada, usar a moeda do cliente
            if moeda_receita is None:
                moeda_receita = moeda_cliente
                print(f"⚠️  Moeda não especificada, usando moeda do cliente: {moeda_cliente}")
            
            # 🔥 CORREÇÃO: Validar consistência de moedas
            if moeda_cliente != moeda_receita:
                return False, f"Moeda inconsistente! Conta cliente: {moeda_cliente}, Receita: {moeda_receita}"
            
            # Verificar saldo suficiente
            if self.contas[conta_cliente]['saldo'] < valor:
                return False, f"Saldo insuficiente! Saldo atual: {self.contas[conta_cliente]['saldo']:,.2f} {moeda_cliente}"
            
            # 🔥🔥🔥 CORREÇÃO CRÍTICA: Creditar na conta contábil de receita NA MOEDA CORRETA
            if categoria_receita in self.contas_contabeis['receitas']:
                if conta_receita in self.contas_contabeis['receitas'][categoria_receita]:
                    # Verificar se a conta contábil tem a moeda especificada
                    if moeda_receita in self.contas_contabeis['receitas'][categoria_receita][conta_receita]:
                        # CREDITAR na conta contábil de receita NA MOEDA CORRETA
                        saldo_anterior_receita = self.contas_contabeis['receitas'][categoria_receita][conta_receita][moeda_receita]
                        self.contas_contabeis['receitas'][categoria_receita][conta_receita][moeda_receita] += valor
                        saldo_novo_receita = self.contas_contabeis['receitas'][categoria_receita][conta_receita][moeda_receita]
                        
                        print(f"💰 CONTA RECEITA (CRÉDITO): {saldo_anterior_receita:,.2f} → {saldo_novo_receita:,.2f} (+{valor:,.2f}) {moeda_receita}")
                    else:
                        return False, f"Conta de receita '{conta_receita}' não suporta a moeda {moeda_receita}"
                else:
                    return False, f"Conta de receita '{conta_receita}' não encontrada na categoria '{categoria_receita}'"
            else:
                return False, f"Categoria de receita '{categoria_receita}' não encontrada"
            
            # DEBITAR da conta do cliente
            saldo_anterior = self.contas[conta_cliente]['saldo']
            self.contas[conta_cliente]['saldo'] -= valor
            saldo_novo = self.contas[conta_cliente]['saldo']
            
            print(f"💰 SALDO CLIENTE ATUALIZADO: {saldo_anterior:,.2f} -> {saldo_novo:,.2f} {moeda_cliente}")
            
            # 🔥 ATUALIZAR SALDO DO CLIENTE NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('contas')\
                        .update({'saldo': saldo_novo})\
                        .eq('id', conta_cliente)\
                        .execute()
                    
                    if response.data:
                        print(f"✅ Saldo do cliente atualizado no Supabase: {conta_cliente} = {saldo_novo:,.2f} {moeda_cliente}")
                    else:
                        print(f"⚠️ Erro ao atualizar saldo do cliente no Supabase")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar saldo do cliente no Supabase: {e}")
            
            # Criar ID da transação
            transacao_id = str(random.randint(100000, 999999))
            while transacao_id in self.transferencias:
                transacao_id = str(random.randint(100000, 999999))
            
            # Obter usuário
            usuario = 'sistema'
            if hasattr(self, 'usuario_logado'):
                if isinstance(self.usuario_logado, dict):
                    usuario = self.usuario_logado.get('username', 'sistema')
                elif isinstance(self.usuario_logado, str):
                    usuario = self.usuario_logado
                else:
                    usuario = 'sistema'
            
            # 🔥🔥🔥 CORREÇÃO: REMOVER COLUNAS NOVAS TEMPORARIAMENTE
            transacao_data = {
                'id': transacao_id,
                'conta_remetente': conta_cliente,
                'conta_destinatario': conta_receita,
                'valor': valor,
                'moeda': moeda_cliente,  # 🔥 Usar coluna existente
                'tipo': 'receita',
                'categoria_receita': categoria_receita,
                'descricao_receita': descricao,
                # 🔥 REMOVIDO TEMPORARIAMENTE: 'moeda_receita': moeda_receita,
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'usuario': usuario
            }
            
            print(f"🔍 TRANSAÇÃO MULTI-MOEDA:")
            print(f"  Cliente: {conta_cliente} ({moeda_cliente})")
            print(f"  Receita: {conta_receita} ({moeda_receita})")
            print(f"  Valor: {valor:,.2f}")
            
            # 🔥 SALVAR TRANSAÇÃO NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('transferencias')\
                        .insert(transacao_data)\
                        .execute()
                    
                    if response.data:
                        print(f"✅ Transação de receita salva no Supabase: {transacao_id}")
                    else:
                        print(f"⚠️ Erro ao salvar transação de receita no Supabase")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao salvar transação de receita no Supabase: {e}")
            
            # Registrar localmente
            self.transferencias[transacao_id] = transacao_data
            
            # 🔥 CORREÇÃO: Salvar contas contábeis (agora multi-moeda)
            self.salvar_contas_contabeis()
            self.salvar_contas()
            self.salvar_transferencias()
            
            return True, f"Receita de {valor:,.2f} {moeda_receita} debitada da conta do cliente e creditada na conta de receita com sucesso!"
            
        except Exception as e:
            print(f"❌ ERRO no sistema lancar_receita: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Erro ao lançar receita: {str(e)}"

    def lancar_despesa(self, conta_bancaria, valor, conta_despesa, categoria_despesa, descricao, moeda_despesa=None):
        """Lança despesa - VERSÃO MULTI-MOEDA COMPATÍVEL"""
        try:
            print(f"🔍 SISTEMA - LANÇAR DESPESA (MULTI-MOEDA):")
            print(f"  Conta Bancária: {conta_bancaria}")
            print(f"  Valor: {valor}")
            print(f"  Conta Despesa: {conta_despesa}")
            print(f"  Categoria: {categoria_despesa}")
            print(f"  Moeda Despesa: {moeda_despesa}")
            print(f"  Descrição: {descricao}")
            
            # Verificar se conta bancária existe
            if conta_bancaria not in self.contas_bancarias_empresa:
                return False, "Conta bancária não encontrada"
            
            # 🔥 CORREÇÃO: Obter moeda da conta bancária
            moeda_banco = self.contas_bancarias_empresa[conta_bancaria]['moeda']
            
            # 🔥 CORREÇÃO: Se moeda_despesa não foi passada, usar a moeda do banco
            if moeda_despesa is None:
                moeda_despesa = moeda_banco
                print(f"⚠️  Moeda não especificada, usando moeda do banco: {moeda_banco}")
            
            # 🔥 CORREÇÃO: Validar consistência de moedas
            if moeda_banco != moeda_despesa:
                return False, f"Moeda inconsistente! Conta banco: {moeda_banco}, Despesa: {moeda_despesa}"
            
            # Verificar saldo suficiente
            if self.contas_bancarias_empresa[conta_bancaria]['saldo'] < valor:
                return False, f"Saldo insuficiente! Saldo atual: {self.contas_bancarias_empresa[conta_bancaria]['saldo']:,.2f} {moeda_banco}"
            
            # 1. DEBITAR da conta bancária
            saldo_anterior_banco = self.contas_bancarias_empresa[conta_bancaria]['saldo']
            self.contas_bancarias_empresa[conta_bancaria]['saldo'] -= valor
            saldo_novo_banco = self.contas_bancarias_empresa[conta_bancaria]['saldo']
            
            print(f"🏦 BANCO (DÉBITO): {saldo_anterior_banco:,.2f} → {saldo_novo_banco:,.2f} (-{valor:,.2f}) {moeda_banco}")
            
            # 🔥 ATUALIZAR SALDO NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('contas_bancarias_empresa')\
                        .update({'saldo': saldo_novo_banco})\
                        .eq('numero', conta_bancaria)\
                        .execute()
                    
                    if response.data:
                        print(f"✅ Saldo bancário atualizado no Supabase: {conta_bancaria} = {saldo_novo_banco:,.2f} {moeda_banco}")
                    else:
                        print(f"⚠️ Erro ao atualizar saldo bancário no Supabase")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar saldo bancário no Supabase: {e}")
            
            # 2. 🔥🔥🔥 CORREÇÃO CRÍTICA: Creditar na conta contábil de despesa NA MOEDA CORRETA
            if categoria_despesa in self.contas_contabeis['despesas']:
                if conta_despesa in self.contas_contabeis['despesas'][categoria_despesa]:
                    # Verificar se a conta contábil tem a moeda especificada
                    if moeda_despesa in self.contas_contabeis['despesas'][categoria_despesa][conta_despesa]:
                        # CREDITAR na conta contábil de despesa NA MOEDA CORRETA
                        saldo_anterior_despesa = self.contas_contabeis['despesas'][categoria_despesa][conta_despesa][moeda_despesa]
                        self.contas_contabeis['despesas'][categoria_despesa][conta_despesa][moeda_despesa] += valor
                        saldo_novo_despesa = self.contas_contabeis['despesas'][categoria_despesa][conta_despesa][moeda_despesa]
                        
                        print(f"📊 DESPESA (CRÉDITO): {saldo_anterior_despesa:,.2f} → {saldo_novo_despesa:,.2f} (+{valor:,.2f}) {moeda_despesa}")
                    else:
                        return False, f"Conta de despesa '{conta_despesa}' não suporta a moeda {moeda_despesa}"
                else:
                    return False, f"Conta de despesa '{conta_despesa}' não encontrada na categoria '{categoria_despesa}'"
            else:
                return False, f"Categoria de despesa '{categoria_despesa}' não encontrada"
            
            # 3. Registrar transação
            transacao_id = str(random.randint(100000, 999999))
            while transacao_id in self.transferencias:
                transacao_id = str(random.randint(100000, 999999))
            
            # Obter usuário
            usuario = 'sistema'
            if hasattr(self, 'usuario_logado'):
                if isinstance(self.usuario_logado, dict):
                    usuario = self.usuario_logado.get('username', 'sistema')
                elif isinstance(self.usuario_logado, str):
                    usuario = self.usuario_logado
                else:
                    usuario = 'sistema'
            
            # 🔥🔥🔥 CORREÇÃO: REMOVER COLUNAS NOVAS TEMPORARIAMENTE
            transacao_data = {
                'id': transacao_id,
                'conta_remetente': conta_bancaria,
                'conta_destinatario': f"DESPESA_{categoria_despesa}_{conta_despesa}",
                'valor': valor,
                'moeda': moeda_banco,  # 🔥 Usar coluna existente
                'tipo': 'despesa',
                'categoria_despesa': categoria_despesa,
                'descricao_despesa': descricao,
                # 🔥 REMOVIDO TEMPORARIAMENTE: 'moeda_despesa': moeda_despesa,
                # 🔥 REMOVIDO TEMPORARIAMENTE: 'moeda_operacao': moeda_despesa,
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'usuario': usuario
            }
            
            # 🔥 SALVAR TRANSAÇÃO NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('transferencias')\
                        .insert(transacao_data)\
                        .execute()
                    
                    if response.data:
                        print(f"✅ Transação de despesa salva no Supabase: {transacao_id}")
                    else:
                        print(f"⚠️ Erro ao salvar transação de despesa no Supabase")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao salvar transação de despesa no Supabase: {e}")
            
            # Salvar dados localmente
            self.transferencias[transacao_id] = transacao_data
            self.salvar_contas_bancarias()
            self.salvar_contas_contabeis()  # 🔥 AGORA salva estrutura multi-moeda
            self.salvar_transferencias()
            
            return True, f"Despesa de {valor:,.2f} {moeda_despesa} paga com sucesso!"
            
        except Exception as e:
            print(f"❌ ERRO no sistema lancar_despesa: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Erro ao lançar despesa: {str(e)}"

    def registrar_transacao_contabil(self, tipo, debito, credito, valor, descricao):
        """Registra transação contábil no sistema"""
        transacao_id = str(random.randint(100000, 999999))
        while transacao_id in self.transferencias:
            transacao_id = str(random.randint(100000, 999999))
        
        self.transferencias[transacao_id] = {
            'id': transacao_id,
            'tipo': 'contabil',
            'tipo_operacao': tipo,
            'conta_debito': debito,
            'conta_credito': credito,
            'valor': valor,
            'descricao': descricao,
            'status': 'completed',
            'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'executado_por': self.usuario_logado['username'] if self.usuario_logado else 'sistema'
        }
        
        self.salvar_transferencias()

    def arredondar_valor(self, valor, casas_decimais=2):
        """Arredonda valores para evitar problemas de ponto flutuante - VERSÃO CORRIGIDA"""
        try:
            # Converter para float primeiro
            valor_float = float(valor)
            
            # 🔥 CORREÇÃO CRÍTICA: Tratar valores muito próximos de zero como zero
            if abs(valor_float) < 1e-10:  # Se for menor que 0.0000000001
                return 0.0
            
            # Arredondar para o número especificado de casas decimais
            valor_arredondado = round(valor_float, casas_decimais)
            
            # 🔥 CORREÇÃO EXTRA: Garantir que não há valores como -0.00
            if abs(valor_arredondado) < 1e-10:
                return 0.0
                
            return valor_arredondado
            
        except (ValueError, TypeError):
            return 0.0

    def salvar_contas_contabeis(self):
        """Salva as contas contábeis em arquivo - COM ARREDONDAMENTO"""
        try:
            # 🔥 ARREDONDAR TODOS OS SALDOS CONTÁBEIS
            for tipo_conta in ['receitas', 'despesas']:
                for categoria, contas in self.contas_contabeis[tipo_conta].items():
                    for conta_nome, dados in contas.items():
                        if 'saldo' in dados:
                            dados['saldo'] = self.arredondar_valor(dados['saldo'])
            
            with open('data/contas_contabeis.json', 'w', encoding='utf-8') as f:
                json.dump(self.contas_contabeis, f, indent=4, ensure_ascii=False)
            
            print("✅ Contas contábeis salvas (valores arredondados)")
        except Exception as e:
            print(f"Erro ao salvar contas contábeis: {e}")

    def salvar_contas_bancarias_empresa(self):
        """Salva as contas bancárias da empresa - VERSÃO COM DEBUG"""
        try:
            print(f"💾 SALVANDO CONTAS BANCÁRIAS EMPRESA...")
            print(f"  Total de contas: {len(self.contas_bancarias_empresa)}")
            
            for conta_num, conta_info in self.contas_bancarias_empresa.items():
                print(f"  💰 {conta_num}: {conta_info['saldo']:,.2f} {conta_info['moeda']}")
            
            with open('data/contas_bancarias.json', 'w', encoding='utf-8') as f:
                json.dump(self.contas_bancarias_empresa, f, indent=4, ensure_ascii=False)
            
            print("✅ Contas bancárias da empresa salvas COM SUCESSO!")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar contas bancárias empresa: {e}")
            import traceback
            traceback.print_exc()
            return False

    def carregar_contas_contabeis(self):
        """Carrega as contas contábeis do Supabase - NOVA VERSÃO MULTI-MOEDA"""
        try:
            print("🔄 Carregando contas contábeis do Supabase...")
            
            # PRIMEIRO: Tentar carregar do Supabase
            if hasattr(self, 'supabase') and self.supabase.conectado:
                print("🔍 Conectado ao Supabase, buscando contas contábeis...")
                response = self.supabase.client.table('contas_contabeis').select('*').execute()
                
                print(f"🔍 Resposta do Supabase: {len(response.data)} registros")
                
                if response.data:
                    # 🔥 DEBUG: Mostrar primeiros registros
                    for i, conta in enumerate(response.data[:3]):  # Mostrar apenas 3 para debug
                        print(f"   📋 Registro {i}: {conta}")
                    
                    self.contas_contabeis = self._organizar_contas_contabeis(response.data)
                    print(f"✅ {len(response.data)} contas contábeis carregadas do Supabase")
                    return
                else:
                    print("⚠️ Nenhum dado retornado do Supabase")
            
            # SEGUNDO: Fallback para JSON local
            if os.path.exists('data/contas_contabeis.json'):
                with open('data/contas_contabeis.json', 'r', encoding='utf-8') as f:
                    self.contas_contabeis = json.load(f)
                print("✅ Contas contábeis carregadas do JSON (fallback)")
            else:
                print("ℹ️ Nenhuma conta contábil encontrada")
                
        except Exception as e:
            print(f"❌ Erro ao carregar contas contábeis: {e}")
            import traceback
            traceback.print_exc()
            self.contas_contabeis = {'receitas': {}, 'despesas': {}}
        
        # 🔥 ADICIONAR ESTA LINHA NO FINAL DO MÉTODO:
        self.debug_contas_contabeis()

    # ========== MÉTODOS PARA CONTAS BANCÁRIAS DA EMPRESA ==========

    def inicializar_contas_bancarias_empresa(self):
        """Inicializa as contas bancárias da empresa com saldo zero"""
        self.contas_bancarias_empresa = {
            'BANK_USD_001': {
                'numero': 'BANK_USD_001',
                'banco': 'Banco Principal',
                'moeda': 'USD',
                'saldo': 0.00,  # 🔥 ALTERADO PARA ZERO
                'tipo': 'empresa',
                'agencia': '0001',
                'data_criacao': '2024-01-01',
                'saldo_inicial': 0.00  # 🔥 ADICIONAR CAMPO DE SALDO INICIAL
            },
            'BANK_EUR_001': {
                'numero': 'BANK_EUR_001',
                'banco': 'Banco Principal', 
                'moeda': 'EUR',
                'saldo': 0.00,  # 🔥 ALTERADO PARA ZERO
                'tipo': 'empresa',
                'agencia': '0001',
                'data_criacao': '2024-01-01',
                'saldo_inicial': 0.00  # 🔥 ADICIONAR CAMPO DE SALDO INICIAL
            },
            'BANK_GBP_001': {
                'numero': 'BANK_GBP_001',
                'banco': 'Banco Principal',
                'moeda': 'GBP', 
                'saldo': 0.00,  # 🔥 ALTERADO PARA ZERO
                'tipo': 'empresa',
                'agencia': '0001',
                'data_criacao': '2024-01-01',
                'saldo_inicial': 0.00  # 🔥 ADICIONAR CAMPO DE SALDO INICIAL
            },
            'BANK_BRL_001': {
                'numero': 'BANK_BRL_001',
                'banco': 'Banco Principal',
                'moeda': 'BRL',
                'saldo': 0.00,  # 🔥 ALTERADO PARA ZERO
                'tipo': 'empresa',
                'agencia': '0001',
                'data_criacao': '2024-01-01',
                'saldo_inicial': 0.00  # 🔥 ADICIONAR CAMPO DE SALDO INICIAL
            }
        }
        print("✅ Contas bancárias da empresa inicializadas com saldo zero")

    def salvar_contas_bancarias(self):
        """Salva as contas bancárias da empresa - COM ARREDONDAMENTO"""
        try:
            print(f"💾 SALVANDO CONTAS BANCÁRIAS...")
            print(f"  Total de contas: {len(self.contas_bancarias_empresa)}")
            
            # 🔥 ARREDONDAR TODOS OS SALDOS ANTES DE SALVAR
            for conta_num, conta_info in self.contas_bancarias_empresa.items():
                if 'saldo' in conta_info:
                    conta_info['saldo'] = self.arredondar_valor(conta_info['saldo'])
                print(f"  💰 {conta_num}: {conta_info['saldo']:,.2f} {conta_info['moeda']}")
            
            with open('data/contas_bancarias.json', 'w', encoding='utf-8') as f:
                json.dump(self.contas_bancarias_empresa, f, indent=4, ensure_ascii=False)
            
            print("✅ Contas bancárias da empresa salvas COM SUCESSO! (valores arredondados)")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar contas bancárias: {e}")
            import traceback
            traceback.print_exc()
            return False

    def carregar_contas_bancarias_despesa(self):
        """Carrega as contas bancárias da empresa no combo da aba despesas"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or 'combo_conta_bancaria_despesa' not in self.ids:
            return
        
        opcoes_contas = []
        for conta_num, dados_conta in sistema.contas_bancarias_empresa.items():
            opcoes_contas.append(f"{conta_num} - {dados_conta['banco']} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
        
        self.ids.combo_conta_bancaria_despesa.values = opcoes_contas
        if opcoes_contas:
            self.ids.combo_conta_bancaria_despesa.text = opcoes_contas[0]

    def atualizar_contas_despesa(self):
        """Atualiza as contas de despesa quando selecionar categoria"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or not self.ids.combo_categoria_despesa.text:
            return
        
        categoria_selecionada = self.ids.combo_categoria_despesa.text
        
        if categoria_selecionada in sistema.contas_contabeis['despesas']:
            contas_despesa = list(sistema.contas_contabeis['despesas'][categoria_selecionada].keys())
            self.ids.combo_conta_despesa.values = contas_despesa
            if contas_despesa:
                self.ids.combo_conta_despesa.text = contas_despesa[0]

    def obter_conta_bancaria_empresa(self, moeda):
        """Obtém uma conta bancária da empresa pela moeda"""
        for conta_num, conta_info in self.contas_bancarias_empresa.items():
            if conta_info['moeda'] == moeda:
                return conta_num
        return None

    def criar_conta_bancaria_empresa(self, banco, agencia, numero_conta, moeda):
        """Cria nova conta bancária da empresa - VERSÃO FINAL CORRIGIDA"""
        try:
            # Verificar se o número da conta já existe
            if numero_conta in self.contas_bancarias_empresa:
                return False, "Número da conta já existe!"
            
            # 🔥 VALIDAÇÃO DA MOEDA - 3 DÍGITOS E ALFANUMÉRICO
            if len(moeda) != 3 or not moeda.isalpha():
                return False, "Moeda inválida! Deve ter exatamente 3 letras.\nEx: USD, EUR, JPY, CAD, BRL, etc."
            
            moeda = moeda.upper()  # Garantir maiúsculas
            
            # 🔥 DADOS DA NOVA CONTA COM ARREDONDAMENTO
            saldo_arredondado = self.arredondar_valor(0.00)
            nova_conta = {
                'numero': numero_conta,
                'banco': banco,
                'agencia': agencia,
                'moeda': moeda,
                'saldo': saldo_arredondado,
                'tipo': 'empresa',
                'data_criacao': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'saldo_inicial': saldo_arredondado
            }
            
            # 🔥 PRIMEIRO: SALVAR NO SUPABASE (APENAS COLUNAS EXISTENTES)
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    # 🔥 CORREÇÃO: Usar APENAS colunas que existem na tabela
                    dados_supabase = {
                        'id': numero_conta,                    # ✅ EXISTE
                        'numero': numero_conta,                # ✅ EXISTE
                        'banco': banco,                        # ✅ EXISTE
                        'moeda': moeda,                        # ✅ EXISTE
                        'saldo': float(saldo_arredondado),     # ✅ EXISTE (numeric)
                        'tipo': 'empresa',                     # ✅ EXISTE
                        'agencia': agencia,                    # ✅ EXISTE
                        'data_criacao': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # ✅ EXISTE (timestamp)
                        'saldo_inicial': float(saldo_arredondado),  # ✅ EXISTE (numeric)
                        'created_at': datetime.datetime.now().isoformat()  # ✅ EXISTE (timestamp)
                    }
                    
                    print(f"🔍 Enviando para Supabase: {dados_supabase}")
                    
                    response = self.supabase.client.table('contas_bancarias_empresa')\
                        .insert(dados_supabase)\
                        .execute()
                    
                    if not response.data:
                        print(f"❌ Erro do Supabase: {response.error}")
                        return False, "Erro ao salvar conta no Supabase!"
                    
                    print(f"✅ Conta {numero_conta} salva no Supabase (Saldo: {saldo_arredondado:,.2f})")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao salvar conta no Supabase: {e}")
                    return False, f"Erro ao salvar conta no sistema: {str(e)}"
            
            # 🔥 DEPOIS: SALVAR LOCALMENTE
            self.contas_bancarias_empresa[numero_conta] = nova_conta
            self.salvar_contas_bancarias()
            
            print(f"✅ Nova conta bancária criada: {numero_conta} - {banco} - {moeda} - Saldo: {saldo_arredondado:,.2f}")
            return True, f"Conta {numero_conta} criada com sucesso! Saldo inicial: {saldo_arredondado:,.2f} {moeda}"
            
        except Exception as e:
            print(f"❌ Erro ao criar conta bancária: {e}")
            return False, f"Erro ao criar conta: {str(e)}"

    def confirmar_criacao_conta(self, instance):
        """Confirma e cria a nova conta bancária"""
        try:
            banco = self.entry_banco.text.strip()
            agencia = self.entry_agencia.text.strip()
            numero_conta = self.entry_numero_conta.text.strip()
            moeda = self.spinner_moeda.text
            
            # Validar campos obrigatórios
            if not banco:
                self.mostrar_erro("Informe o nome do banco!")
                return
                
            if not agencia:
                self.mostrar_erro("Informe o número da agência!")
                return
                
            if not numero_conta:
                self.mostrar_erro("Informe o número da conta!")
                return
            
            # 🔥 SEMPRE SALDO ZERO - não pedir saldo inicial
            saldo_inicial = 0.00
            
            sistema = App.get_running_app().sistema
            
            print(f"🔧 CRIANDO NOVA CONTA BANCÁRIA:")
            print(f"  Banco: {banco}")
            print(f"  Agência: {agencia}")
            print(f"  Número: {numero_conta}")
            print(f"  Moeda: {moeda}")
            print(f"  Saldo: {saldo_inicial:,.2f} (SEMPRE ZERO)")
            
            # Chamar método do sistema
            sucesso, mensagem = sistema.criar_conta_bancaria_empresa(
                banco, agencia, numero_conta, moeda
            )
            
            if sucesso:
                self.popup_nova_conta.dismiss()
                self.mostrar_sucesso(mensagem)
                
                # 🔥 FORÇAR RECARGA DAS CONTAS BANCÁRIAS
                sistema.carregar_contas_bancarias()
                
                # Atualizar a tela
                self.carregar_contas_bancarias()
            else:
                self.mostrar_erro(mensagem)
                
        except Exception as e:
            self.mostrar_erro(f"Erro ao criar conta: {str(e)}")

    def debitar_conta_bancaria_empresa(self, moeda, valor):
        """Debita (diminui saldo) de conta bancária da empresa - VERSÃO SUPABASE COM ARREDONDAMENTO"""
        conta_num = self.obter_conta_bancaria_empresa(moeda)
        if conta_num and conta_num in self.contas_bancarias_empresa:
            
            # 🔥 ARREDONDAR O VALOR ANTES DE DEBITAR
            valor_arredondado = self.arredondar_valor(valor)
            saldo_atual = self.contas_bancarias_empresa[conta_num]['saldo']
            
            if saldo_atual >= valor_arredondado:
                
                # 🔥 CALCULAR NOVO SALDO E ARREDONDAR
                novo_saldo = self.arredondar_valor(saldo_atual - valor_arredondado)
                self.contas_bancarias_empresa[conta_num]['saldo'] = novo_saldo
                
                # 🔥 ATUALIZAR NO SUPABASE (COM ARREDONDAMENTO)
                if hasattr(self, 'supabase') and self.supabase.conectado:
                    try:
                        response = self.supabase.client.table('contas_bancarias_empresa')\
                            .update({'saldo': novo_saldo})\
                            .eq('numero', conta_num)\
                            .execute()
                        
                        if not response.data:
                            print(f"⚠️ Erro ao atualizar saldo no Supabase: {conta_num}")
                        else:
                            print(f"✅ Saldo atualizado no Supabase: {conta_num} = {novo_saldo:,.2f}")
                            
                    except Exception as e:
                        print(f"⚠️ Erro ao atualizar saldo no Supabase: {e}")
                
                # 🔥 SALVAR LOCALMENTE (também com arredondamento)
                self.salvar_contas_bancarias()
                return True
        return False
    
    def carregar_contas_bancarias(self):
        """Carrega as contas bancárias da empresa - VERSÃO SUPABASE COM ARREDONDAMENTO"""
        try:
            # 🔥 PRIMEIRO: TENTAR CARREGAR DO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    print("📡 Buscando contas bancárias no Supabase...")
                    response = self.supabase.client.table('contas_bancarias_empresa')\
                        .select('*')\
                        .execute()
                    
                    print(f"🔍 DEBUG: {len(response.data)} contas encontradas no Supabase")
                    
                    # 🔥 DEBUG: Mostrar todas as contas encontradas
                    print("📋 CONTAS ENCONTRADAS:")
                    for idx, conta in enumerate(response.data):
                        print(f"  {idx+1}. Número: '{conta.get('numero')}' | Banco: {conta.get('banco')} | Moeda: {conta.get('moeda')} | Saldo: {conta.get('saldo')}")
                    
                    if response.data:
                        self.contas_bancarias_empresa.clear()
                        for conta in response.data:
                            conta_num = conta['numero']
                            
                            print(f"  ➕ Adicionando ao dicionário: chave = '{conta_num}'")
                            
                            # 🔥 ARREDONDAR SALDO AO CARREGAR DO SUPABASE
                            saldo_arredondado = self.arredondar_valor(float(conta['saldo']))
                            
                            self.contas_bancarias_empresa[conta_num] = {
                                'numero': conta['numero'],
                                'banco': conta['banco'],
                                'agencia': conta.get('agencia', ''),
                                'moeda': conta['moeda'],
                                'saldo': saldo_arredondado,
                                'tipo': conta.get('tipo', 'empresa'),
                                'data_criacao': conta.get('data_criacao', ''),
                                'saldo_inicial': self.arredondar_valor(float(conta.get('saldo_inicial', conta['saldo'])))
                            }
                        
                        print(f"✅ {len(response.data)} contas bancárias carregadas do Supabase")
                        print(f"🔍 CHAVES NO DICIONÁRIO: {list(self.contas_bancarias_empresa.keys())}")
                        
                        # 🔥 VERIFICAR ESPECIFICAMENTE A CONTA 'COFRE ESCRITÓRIO - GBP'
                        conta_procurada = 'COFRE ESCRITÓRIO - GBP'
                        if conta_procurada in self.contas_bancarias_empresa:
                            print(f"🎯 CONTA '{conta_procurada}' ENCONTRADA NO DICIONÁRIO!")
                            print(f"   Dados: {self.contas_bancarias_empresa[conta_procurada]}")
                        else:
                            print(f"⚠️ CONTA '{conta_procurada}' NÃO ENCONTRADA NO DICIONÁRIO!")
                        
                        # 🔥 SALVAR LOCALMENTE PARA BACKUP
                        self.salvar_contas_bancarias()
                        return
                    else:
                        print("⚠️ Nenhuma conta encontrada no Supabase")
                            
                except Exception as e:
                    print(f"⚠️ Erro ao carregar contas do Supabase: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 🔥 FALLBACK: CARREGAR DO ARQUIVO LOCAL
            if os.path.exists('data/contas_bancarias.json'):
                with open('data/contas_bancarias.json', 'r', encoding='utf-8') as f:
                    self.contas_bancarias_empresa = json.load(f)
                print(f"🔄 DASHBOARD: {len(self.contas_bancarias_empresa)} contas bancárias RECARREGADAS DO ARQUIVO LOCAL")
                print(f"🔍 CHAVES NO ARQUIVO LOCAL: {list(self.contas_bancarias_empresa.keys())}")
            else:
                print("⚠️ Arquivo local 'data/contas_bancarias.json' não encontrado")
                    
        except Exception as e:
            print(f"❌ Erro ao carregar contas bancárias: {e}")
            import traceback
            traceback.print_exc()

    def testar_despesa(self):
        """Método temporário para testar despesa"""
        print("🧪 TESTANDO DESPESA...")
        sistema = App.get_running_app().sistema
        
        # Preencher campos automaticamente para teste
        self.ids.combo_conta_bancaria_despesa.text = "BANK_USD_001 - Banco Principal - USD - Saldo: 1,000,000.00"
        self.ids.combo_categoria_despesa.text = "DESPESAS ADMINISTRATIVAS"
        self.ids.combo_conta_despesa.text = "Salários"
        self.ids.entry_valor_despesa.text = "100.00"
        self.ids.entry_descricao_despesa.text = "Teste de despesa"
        
        print("✅ Campos preenchidos automaticamente para teste")

    def deposito_conta_bancaria(self, conta_numero, valor, descricao):
        """Processa um depósito na conta bancária - VERSÃO SUPABASE COMPLETA CORRIGIDA"""
        try:
            if conta_numero not in self.contas_bancarias_empresa:
                print(f"❌ Conta {conta_numero} não encontrada!")
                return False
            
            # 🔥 ARREDONDAR VALOR
            valor_arredondado = self.arredondar_valor(valor)
            
            # 🔥 DEBUG: Mostrar saldo antes
            saldo_antes = self.contas_bancarias_empresa[conta_numero]['saldo']
            print(f"💰 DEPÓSITO - ANTES: {conta_numero} = {saldo_antes:,.2f}")
            
            # 🔥 CALCULAR NOVO SALDO COM ARREDONDAMENTO
            novo_saldo = self.arredondar_valor(saldo_antes + valor_arredondado)
            self.contas_bancarias_empresa[conta_numero]['saldo'] = novo_saldo
            
            # 🔥 DEBUG: Mostrar saldo depois
            print(f"💰 DEPÓSITO - DEPOIS: {conta_numero} = {novo_saldo:,.2f} (+{valor_arredondado:,.2f})")
            
            # 🔥 ATUALIZAR SALDO NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('contas_bancarias_empresa')\
                        .update({'saldo': novo_saldo})\
                        .eq('numero', conta_numero)\
                        .execute()
                    
                    if not response.data:
                        print(f"⚠️ Erro ao atualizar saldo no Supabase: {conta_numero}")
                    else:
                        print(f"✅ Saldo atualizado no Supabase: {conta_numero} = {novo_saldo:,.2f}")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar saldo no Supabase: {e}")
            
            # 🔥 REGISTRAR TRANSAÇÃO NO SUPABASE
            transacao_id = str(int(datetime.datetime.now().timestamp()))
            
            # 🔥 CORREÇÃO: Obter usuário de forma segura
            usuario = 'sistema'
            if hasattr(self, 'usuario_logado'):
                if isinstance(self.usuario_logado, dict):
                    usuario = self.usuario_logado.get('username', 'sistema')
                elif isinstance(self.usuario_logado, str):
                    usuario = self.usuario_logado
                else:
                    usuario = 'sistema'
            
            # Dados da transação para Supabase
            transacao_data = {
                'id': transacao_id,
                'conta_destinatario': conta_numero,
                'valor': valor_arredondado,
                'moeda': self.contas_bancarias_empresa[conta_numero]['moeda'],
                'tipo': 'deposito',
                'descricao': descricao,
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'usuario': usuario  # 🔥 CORREÇÃO AQUI
            }
            
            # 🔥 SALVAR TRANSAÇÃO NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('transferencias')\
                        .insert(transacao_data)\
                        .execute()
                    
                    if not response.data:
                        print(f"⚠️ Erro ao salvar transação no Supabase")
                    else:
                        print(f"✅ Transação de depósito salva no Supabase: {transacao_id}")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao salvar transação no Supabase: {e}")
            
            # 🔥 SALVAR LOCALMENTE TAMBÉM
            self.transferencias[transacao_id] = transacao_data
            self.salvar_contas_bancarias()
            self.salvar_transferencias()
            
            print(f"✅ Depósito de {valor_arredondado:,.2f} realizado na conta {conta_numero}")
            return True
            
        except Exception as e:
            print(f"❌ Erro no depósito: {e}")
            import traceback
            traceback.print_exc()
            return False

    def saque_conta_bancaria(self, conta_numero, valor, descricao):
        """Processa um saque da conta bancária - VERSÃO SUPABASE COMPLETA CORRIGIDA"""
        try:
            if conta_numero not in self.contas_bancarias_empresa:
                print(f"❌ Conta {conta_numero} não encontrada!")
                return False
            
            # 🔥 ARREDONDAR VALOR
            valor_arredondado = self.arredondar_valor(valor)
            
            # 🔥 DEBUG: Mostrar saldo antes
            saldo_antes = self.contas_bancarias_empresa[conta_numero]['saldo']
            print(f"💸 SAQUE - ANTES: {conta_numero} = {saldo_antes:,.2f}")
            
            # Verificar saldo (com valores arredondados)
            if saldo_antes < valor_arredondado:
                print(f"❌ Saldo insuficiente: {saldo_antes:,.2f} < {valor_arredondado:,.2f}")
                return False
            
            # 🔥 CALCULAR NOVO SALDO COM ARREDONDAMENTO
            novo_saldo = self.arredondar_valor(saldo_antes - valor_arredondado)
            self.contas_bancarias_empresa[conta_numero]['saldo'] = novo_saldo
            
            # 🔥 DEBUG: Mostrar saldo depois
            print(f"💸 SAQUE - DEPOIS: {conta_numero} = {novo_saldo:,.2f} (-{valor_arredondado:,.2f})")
            
            # 🔥 ATUALIZAR SALDO NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('contas_bancarias_empresa')\
                        .update({'saldo': novo_saldo})\
                        .eq('numero', conta_numero)\
                        .execute()
                    
                    if not response.data:
                        print(f"⚠️ Erro ao atualizar saldo no Supabase: {conta_numero}")
                    else:
                        print(f"✅ Saldo atualizado no Supabase: {conta_numero} = {novo_saldo:,.2f}")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar saldo no Supabase: {e}")
            
            # 🔥 REGISTRAR TRANSAÇÃO NO SUPABASE
            transacao_id = str(int(datetime.datetime.now().timestamp()))
            
            # 🔥 CORREÇÃO: Obter usuário de forma segura
            usuario = 'sistema'
            if hasattr(self, 'usuario_logado'):
                if isinstance(self.usuario_logado, dict):
                    usuario = self.usuario_logado.get('username', 'sistema')
                elif isinstance(self.usuario_logado, str):
                    usuario = self.usuario_logado
                else:
                    usuario = 'sistema'
            
            # Dados da transação para Supabase
            transacao_data = {
                'id': transacao_id,
                'conta_remetente': conta_numero,
                'valor': valor_arredondado,
                'moeda': self.contas_bancarias_empresa[conta_numero]['moeda'],
                'tipo': 'saque',
                'descricao': descricao,
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'usuario': usuario  # 🔥 CORREÇÃO AQUI
            }
            
            # 🔥 SALVAR TRANSAÇÃO NO SUPABASE
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('transferencias')\
                        .insert(transacao_data)\
                        .execute()
                    
                    if not response.data:
                        print(f"⚠️ Erro ao salvar transação no Supabase")
                    else:
                        print(f"✅ Transação de saque salva no Supabase: {transacao_id}")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao salvar transação no Supabase: {e}")
            
            # 🔥 SALVAR LOCALMENTE TAMBÉM
            self.transferencias[transacao_id] = transacao_data
            self.salvar_contas_bancarias()
            self.salvar_transferencias()
            
            print(f"✅ Saque de {valor_arredondado:,.2f} realizado da conta {conta_numero}")
            return True
            
        except Exception as e:
            print(f"❌ Erro no saque: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    # ========== MÉTODOS PARA COTAÇÕES DE MOEDAS ==========
        
    # 🔥 MÉTODOS PARA COMPRA E VENDA DE MOEDAS

    def inicializar_pares_cliente(self, username):
        """Inicializa alguns pares padrão para um novo cliente"""
        if username not in self.spreads_clientes:
            self.spreads_clientes[username] = {}
            
            # Pares padrão liberados para novos clientes
            pares_padrao = ['USD_BRL', 'EUR_BRL', 'GBP_BRL', 'BRL_USD']
            
            for par in pares_padrao:
                self.spreads_clientes[username][par] = {
                    'compra': 0.5,
                    'venda': 0.5
                }
            
            print(f"Pares padrão inicializados para {username}: {pares_padrao}")

    def verificar_horario_comercial(self, usuario=None):
        """Verifica se está no horário comercial (Brasília) - CORRIGIDO"""
        from datetime import datetime
        from datetime import timezone
        
        try:
            # Obter horário atual (Brasília é UTC-3)
            agora_utc = datetime.now(timezone.utc)
            # 🔥 CORREÇÃO: Brasília está 3 horas ATRÁS do UTC, então UTC = Brasília + 3
            # Portanto, Brasília = UTC - 3
            offset_brasilia = -3  # UTC-3 para Brasília
            hora_brasilia = (agora_utc.hour + offset_brasilia) % 24
            
            # Criar datetime com horário de Brasília correto
            agora_brasilia = agora_utc.replace(hour=hora_brasilia, minute=agora_utc.minute, second=agora_utc.second)
            
            # Verificar se cliente tem horário personalizado
            if usuario and usuario in self.horarios_clientes:
                horario_cliente = self.horarios_clientes[usuario]
                dias_semana = horario_cliente['dias_semana']
                inicio = horario_cliente['inicio']
                fim = horario_cliente['fim']
                tipo = "personalizado"
            else:
                # Usar horário padrão
                dias_semana = self.horario_comercial_padrao['dias_semana']
                inicio = self.horario_comercial_padrao['inicio']
                fim = self.horario_comercial_padrao['fim']
                tipo = "padrão"
            
            # Verificar dia da semana (0=Segunda, 6=Domingo)
            dia_atual = agora_brasilia.weekday()  # 0=Segunda, 6=Domingo
            
            print(f"=== VERIFICAÇÃO HORÁRIO {tipo.upper()} ===")
            print(f"   Cliente: {usuario}")
            print(f"   Data/hora UTC: {agora_utc}")
            print(f"   Data/hora Brasília: {agora_brasilia}")
            print(f"   Dia atual: {dia_atual} (0=Seg, 6=Dom)")
            print(f"   Dias permitidos: {dias_semana}")
            print(f"   Horário atual: {agora_brasilia.strftime('%H:%M')}")
            print(f"   Horário permitido: {inicio} às {fim}")
            
            # VERIFICAÇÃO 1: Dia da semana
            if dia_atual not in dias_semana:
                dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                dias_permitidos = [dias_nomes[d] for d in dias_semana]
                print(f"   ❌ FORA DO HORÁRIO: Dia {dia_atual} não permitido")
                return False, f"Fora do horário comercial. Disponível apenas: {', '.join(dias_permitidos)}"
            
            # VERIFICAÇÃO 2: Horário
            hora_atual = agora_brasilia.strftime('%H:%M')
            
            if hora_atual < inicio:
                print(f"   ❌ FORA DO HORÁRIO: {hora_atual} < {inicio}")
                return False, f"Fora do horário comercial. Disponível a partir das {inicio}"
            elif hora_atual > fim:
                print(f"   ❌ FORA DO HORÁRIO: {hora_atual} > {fim}")
                return False, f"Fora do horário comercial. Disponível até às {fim}"
            
            print(f"   ✅ DENTRO DO HORÁRIO COMERCIAL")
            return True, "Dentro do horário comercial"
            
        except Exception as e:
            print(f"❌ Erro ao verificar horário: {e}")
            import traceback
            traceback.print_exc()
            # Em caso de erro, permitir a operação (fail-open)
            return True, "Horário verificado com ressalvas"

    def verificar_dependencias(self):
        """Verifica se todas as dependências estão instaladas"""
        try:
            import requests
            print("Biblioteca 'requests' disponível")
            return True
        except ImportError:
            print("Biblioteca 'requests' não encontrada")
            print("Instale com: pip install requests")
            return False

    def obter_cotacao_simples(self, par_moedas):
        """Sempre retorna: 1 MOEDA_ESQUERDA = X MOEDA_DIREITA"""
        try:
            import requests
            import datetime
            
            moeda_esquerda = par_moedas[:3]  # BRL em BRL_USD
            moeda_direita = par_moedas[4:]    # USD em BRL_USD
            
            # 🔥 VERIFICAR CACHE PRIMEIRO
            cache_key = f"{par_moedas}_simple"
            if (self.ultima_atualizacao and 
                (datetime.datetime.now() - self.ultima_atualizacao).seconds < 30 and
                cache_key in self.cotacoes_cache):
                return self.cotacoes_cache[cache_key]
            
            with self.cotacao_lock:
                # Tentar consultar direto primeiro
                print(f"🌐 Tentando API: {moeda_esquerda}-{moeda_direita}")
                url_direto = f"https://economia.awesomeapi.com.br/json/last/{moeda_esquerda}-{moeda_direita}"
                response = requests.get(url_direto, timeout=10)
                
                if response.status_code == 200:
                    dados = response.json()
                    chave_direta = f"{moeda_esquerda}{moeda_direita}"
                    
                    if chave_direta in dados:
                        cotacao = float(dados[chave_direta]['bid'])
                        print(f"✅ Cotação DIRETA {par_moedas}: 1 {moeda_esquerda} = {cotacao} {moeda_direita}")
                        
                        # Cache
                        self.cotacoes_cache[cache_key] = cotacao
                        self.ultima_atualizacao = datetime.datetime.now()
                        return cotacao
                
                # Se não encontrou direto, tentar invertido
                print(f"🔄 Tentando API invertido: {moeda_direita}-{moeda_esquerda}")
                url_invertido = f"https://economia.awesomeapi.com.br/json/last/{moeda_direita}-{moeda_esquerda}"
                response = requests.get(url_invertido, timeout=10)
                
                if response.status_code == 200:
                    dados = response.json()
                    chave_invertida = f"{moeda_direita}{moeda_esquerda}"
                    
                    if chave_invertida in dados:
                        cotacao_invertida = float(dados[chave_invertida]['bid'])
                        cotacao = 1 / cotacao_invertida  # 🔥 INVERTEMOS MATEMATICAMENTE
                        print(f"✅ Cotação INVERTIDA {par_moedas}: 1 {moeda_esquerda} = {cotacao} {moeda_direita} (de 1 {moeda_direita} = {cotacao_invertida} {moeda_esquerda})")
                        
                        # Cache
                        self.cotacoes_cache[cache_key] = cotacao
                        self.ultima_atualizacao = datetime.datetime.now()
                        return cotacao
                
                # Fallback
                print(f"❌ Nenhum par encontrado, usando fallback")
                return self.taxas_cambio.get(par_moedas, 1.0)
                
        except Exception as e:
            print(f"❌ Erro ao obter cotação: {e}")
            return self.taxas_cambio.get(par_moedas, 1.0)

    def calcular_operacao_cambio(self, moeda_de, moeda_para, tipo_operacao, valor_digitado, usuario):
        """
        Fórmulas com perspectiva correta do cliente - VERSÃO FINAL CORRIGIDA
        """
        # 🔥 CORREÇÃO: Definir par baseado na operação
        if tipo_operacao == 'compra':
            # COMPRA: Cliente COMPRA moeda_para, PAGA moeda_de
            # Par: MOEDA_PARA_MOEDA_DE (1 moeda_para = X moeda_de)
            par_correto = f"{moeda_para}_{moeda_de}"
            direcao = f"COMPRA {moeda_para}, PAGA {moeda_de}"
        else:
            # VENDA: Cliente VENDE moeda_de, RECEBE moeda_para  
            # Par: MOEDA_DE_MOEDA_PARA (1 moeda_de = X moeda_para)
            par_correto = f"{moeda_de}_{moeda_para}"
            direcao = f"VENDE {moeda_de}, RECEBE {moeda_para}"
        
        cotacao_real = self.obter_cotacao_simples(par_correto)
        
        if not cotacao_real:
            return None, None
        
        print(f"   PERSPECTIVA CORRIGIDA:")
        print(f"   Par: {par_correto} (1 {par_correto[:3]} = {cotacao_real:.6f} {par_correto[4:]})")
        print(f"   Operação: {tipo_operacao}")
        print(f"   Cliente: {direcao}")
        
        # Obter spread
        spread_info = self.obter_spread_cliente(usuario, par_correto)
        spread = spread_info.get(tipo_operacao, self.spread_padrao)
        
        # Aplicar spread
        if tipo_operacao == 'compra':
            # COMPRA: Cliente PAGA MAIS
            cotacao_cliente = cotacao_real * (1 + spread/100)
            print(f"   CLIENTE PAGA MAIS -> Spread: +{spread}%")
        else:
            # VENDA: Cliente RECEBE MENOS
            cotacao_cliente = cotacao_real * (1 - spread/100)
            print(f"   CLIENTE RECEBE MENOS -> Spread: -{spread}%")
        
        print(f"   Cotação para cliente: {cotacao_cliente:.6f}")
        
        # 🔥 CORREÇÃO CRÍTICA: AMBAS OPERAÇÕES USAM MULTIPLICAÇÃO
        if tipo_operacao == 'compra':
            # COMPRA: Cliente RECEBE moeda_para (valor digitado), PAGA moeda_de
            valor_receber = valor_digitado
            valor_pagar = valor_receber * cotacao_cliente  # MULTIPLICAÇÃO ✅
            
            print(f"   CÁLCULO COMPRA CORRETO:")
            print(f"   Receber: {valor_receber:.2f} {moeda_para}")
            print(f"   Pagar: {valor_pagar:.2f} {moeda_de}")
            print(f"   Fórmula: {valor_receber:.2f} x {cotacao_cliente:.6f} = {valor_pagar:.2f}")
            
            return round(valor_pagar, 2), round(cotacao_cliente, 6)
            
        else:
            # VENDA: Cliente PAGA moeda_de (valor digitado), RECEBE moeda_para
            valor_pagar = valor_digitado
            valor_receber = valor_pagar * cotacao_cliente  # MULTIPLICAÇÃO ✅
            
            print(f"   CÁLCULO VENDA CORRETO:")
            print(f"   Pagar: {valor_pagar:.2f} {moeda_de}")
            print(f"   Receber: {valor_receber:.2f} {moeda_para}")
            print(f"   Fórmula: {valor_pagar:.2f} x {cotacao_cliente:.6f} = {valor_receber:.2f}")
            
            return round(valor_receber, 2), round(cotacao_cliente, 6)

    def calcular_cotacao_cliente(self, moeda_de, moeda_para, tipo_operacao, usuario):
        """Calcula cotação com spread - PERSPECTIVA CORRETA DO CLIENTE"""
        # 🔥 REGRA: MOEDA_QUE_CLIENTE_RECEBE_MOEDA_QUE_CLIENTE_PAGA
        par_correto = f"{moeda_para}_{moeda_de}"  # RECEBE_PAGA
        
        cotacao_real = self.obter_cotacao_simples(par_correto)
        
        if not cotacao_real:
            return None
        
        print(f"   PERSPECTIVA CLIENTE:")
        print(f"   Par: {par_correto} (1 {moeda_para} = {cotacao_real:.6f} {moeda_de})")
        print(f"   Operação: {tipo_operacao}")
        print(f"   Cliente: {tipo_operacao.upper()} {moeda_para}, PAGA {moeda_de}")
        
        # Obter spread
        spread_info = self.obter_spread_cliente(usuario, par_correto)
        spread = spread_info.get(tipo_operacao, self.spread_padrao)
        
        # 🔥 PERSPECTIVA CORRETA DO CLIENTE
        if tipo_operacao == 'compra':
            # COMPRA: Cliente COMPRA moeda_para → PAGA MAIS
            cotacao_cliente = cotacao_real * (1 + spread/100)
            print(f"   CLIENTE PAGA MAIS -> Spread: +{spread}%")
        else:
            # VENDA: Cliente VENDE moeda_de → RECEBE MENOS
            cotacao_cliente = cotacao_real * (1 - spread/100)
            print(f"   CLIENTE RECEBE MENOS -> Spread: -{spread}%")
        
        print(f"   Cotação para cliente: {cotacao_cliente:.6f}")
        
        # 🔥 CORREÇÃO APENAS PARA EXIBIÇÃO NA UI - SEM AFETAR CÁLCULOS
        # Para VENDA, retornamos a cotação INVERTIDA para exibição correta
        if tipo_operacao == 'venda':
            cotacao_exibicao = 1 / cotacao_cliente if cotacao_cliente != 0 else 0
            return round(cotacao_exibicao, 4)
        else:
            # COMPRA mantém igual (já está correto)
            return round(cotacao_cliente, 4)
    
    def obter_spread_cliente(self, usuario, par_moedas):
        """Obtém spread configurado para o cliente"""
        if usuario in self.spreads_clientes:
            if par_moedas in self.spreads_clientes[usuario]:
                return self.spreads_clientes[usuario][par_moedas]
        
        # Retornar spread padrão se não configurado
        return {'compra': self.spread_padrao, 'venda': self.spread_padrao}
    
    def obter_pares_disponiveis(self, usuario, tipo_operacao=None):
        """Retorna apenas os pares LIBERADOS para o cliente"""
        moedas = ['USD', 'EUR', 'GBP', 'BRL']
        todos_pares = []
        
        # GERAR TODOS OS 12 PARES POSSÍVEIS
        for moeda1 in moedas:
            for moeda2 in moedas:
                if moeda1 != moeda2:
                    todos_pares.append(f"{moeda1}_{moeda2}")
        
        # 🔥 FILTRAR APENAS OS PARES LIBERADOS PARA ESTE CLIENTE
        pares_liberados = []
        if usuario in self.spreads_clientes:
            pares_liberados = list(self.spreads_clientes[usuario].keys())
        else:
            # Se não tem spreads configurados, retorna todos (comportamento anterior)
            pares_liberados = todos_pares
        
        print(f"   PARES DISPONÍVEIS PARA {usuario}:")
        print(f"   Todos os pares: {len(todos_pares)}")
        print(f"   Pares liberados: {len(pares_liberados)}")
        print(f"   Pares: {pares_liberados}")
        
        return pares_liberados
    
    def executar_operacao_cambio(self, par_moedas, tipo_operacao, valor, usuario):
        """Executa operação - AGORA PERMITE SALDO NEGATIVO COM CONFIRMAÇÃO"""
        try:
            moeda_origem = par_moedas[:3]
            moeda_destino = par_moedas[4:]
            
            print(f" INICIANDO OPERAÇÃO {tipo_operacao.upper()}")
            print(f" Par: {par_moedas}")
            print(f" Valor: {valor}")
            print(f" Moeda origem: {moeda_origem}")
            print(f" Moeda destino: {moeda_destino}")
            
            # Verificar se usuário tem conta na moeda de origem
            usuario_data = self.usuarios.get(self.usuario_logado, {})
            contas_origem = [c for c in usuario_data.get('contas', []) 
                           if self.contas[c]['moeda'] == moeda_origem]
            
            if not contas_origem:
                return False, f"Você não possui conta em {moeda_origem}"
            
            conta_origem = contas_origem[0]
            
            # 🔥 CORREÇÃO: Usar nova assinatura com 4 parâmetros
            cotacao = self.calcular_cotacao_cliente(
                moeda_origem,
                moeda_destino,
                tipo_operacao, 
                usuario
            )
            
            if not cotacao:
                return False, "Erro ao obter cotação"
            
            print(f"Cotação com spread: {cotacao}")
            
            # 🔥 CORREÇÃO: Usar nova assinatura com 5 parâmetros
            if tipo_operacao == 'compra':
                # COMPRA: usuário RECEBE o valor digitado (moeda_destino)
                valor_receber = valor
                valor_pagar, cotacao_cliente = self.calcular_operacao_cambio(
                    moeda_origem,
                    moeda_destino,
                    tipo_operacao, 
                    valor_receber, 
                    usuario
                )
                print(f"COMPRA: Paga {valor_pagar:.2f} {moeda_origem}, Recebe {valor_receber:.2f} {moeda_destino}")
                valor_origem = valor_pagar
                valor_destino = valor_receber
            else:
                # VENDA: usuário PAGA o valor digitado (moeda_origem)
                valor_pagar = valor
                valor_receber, cotacao_cliente = self.calcular_operacao_cambio(
                    moeda_origem,
                    moeda_destino,
                    tipo_operacao, 
                    valor_pagar, 
                    usuario
                )
                print(f"VENDA: Paga {valor_pagar:.2f} {moeda_origem}, Recebe {valor_receber:.2f} {moeda_destino}")
                valor_origem = valor_pagar
                valor_destino = valor_receber
            
            # 🔥 MUDANÇA: NÃO VERIFICAR SALDO AQUI - DEIXAR PARA A CONFIRMAÇÃO
            saldo_origem_antes = self.contas[conta_origem]['saldo']
            print(f"Saldo origem antes: {saldo_origem_antes:.2f} {moeda_origem}")
            print(f"Valor a pagar: {valor_origem:.2f} {moeda_origem}")
            
            # 🔥 AGORA SEMPRE RETORNA OS VALORES PARA CONFIRMAÇÃO
            # A verificação de saldo será feita na interface com popup de confirmação
            
            # Verificar se usuário tem conta na moeda destino, se não, criar
            contas_destino = [c for c in self.usuario_logado['contas'] 
                            if self.contas[c]['moeda'] == moeda_destino]
            
            if not contas_destino:
                # Criar conta automaticamente na moeda destino
                nova_conta = self.criar_conta_automatica(moeda_destino, usuario)
                if not nova_conta:
                    return False, f"Erro ao criar conta em {moeda_destino}"
                conta_destino = nova_conta
                print(f"Nova conta criada: {conta_destino} em {moeda_destino}")
            else:
                conta_destino = contas_destino[0]
                print(f"Conta destino existente: {conta_destino}")
            
            saldo_destino_antes = self.contas[conta_destino]['saldo']
            print(f"Saldo destino antes: {saldo_destino_antes:.2f} {moeda_destino}")
            
            # 🔥 RETORNAR TODAS AS INFORMAÇÕES PARA A CONFIRMAÇÃO
            dados_operacao = {
                'conta_origem': conta_origem,
                'conta_destino': conta_destino,
                'valor_origem': valor_origem,
                'valor_destino': valor_destino,
                'moeda_origem': moeda_origem,
                'moeda_destino': moeda_destino,
                'cotacao_cliente': cotacao_cliente,
                'saldo_atual': saldo_origem_antes,
                'saldo_pos_operacao': saldo_origem_antes - valor_origem
            }
            
            return True, dados_operacao
            
        except Exception as e:
            print(f"Erro executar operação: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Erro: {str(e)}"
    
    def criar_conta_automatica(self, moeda, usuario):
        """Cria conta automaticamente para o usuário"""
        try:
            conta_numero = str(random.randint(100000000, 999999999))
            while conta_numero in self.contas:
                conta_numero = str(random.randint(100000000, 999999999))
            
            self.contas[conta_numero] = {
                'moeda': moeda,
                'saldo': 0.00,
                'cliente': usuario,
                'cliente_nome': self.usuarios[usuario]['nome'],
                'data_criacao': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Adicionar conta ao usuário
            self.usuarios[usuario]['contas'].append(conta_numero)
            
            print(f"Conta automática criada: {conta_numero} em {moeda}")
            return conta_numero
            
        except Exception as e:
            print(f"Erro criar conta automática: {e}")
            return None
    
    def registrar_transacao_cambio(self, par_moedas, tipo_operacao, valor_origem, valor_destino, cotacao, conta_origem, conta_destino, usuario):
        """Registra transação de câmbio - AGORA COM ID _nt"""
        from datetime import datetime
        import random
        
        # 🔥 MUDANÇA: GERAR ID COM SUFIXO "_nt" EM VEZ DE "_novatela"
        transacao_id = f"{random.randint(100000, 999999)}_nt"
        
        # Garantir que o ID é único
        while transacao_id in self.transferencias:
            transacao_id = f"{random.randint(100000, 999999)}_nt"
        
        # Registrar transação
        self.transferencias[transacao_id] = {
            'id': transacao_id,
            'tipo': 'cambio',
            'status': 'completed', 
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'moeda': par_moedas[:3],  # Moeda origem
            'valor': valor_origem,
            'conta_remetente': conta_origem,
            'conta_destinatario': conta_destino,
            'descricao': f'CÂMBIO - {tipo_operacao.upper()} {par_moedas}',
            'executado_por': usuario,
            'cliente': usuario,
            'usuario': usuario,
            'operacao': tipo_operacao,
            'par_moedas': par_moedas,
            'valor_origem': valor_origem,
            'valor_destino': valor_destino, 
            'cotacao': cotacao,
            'moeda_origem': par_moedas[:3],
            'moeda_destino': par_moedas[4:],
            'conta_origem': conta_origem  # 🔥 CAMPO ADICIONAL
        }
        
        print(f"📝 Transação de câmbio registrada: {transacao_id}")
        return transacao_id

    def testar_sistema_cambio(self):
        """Testa o sistema de câmbio - VERSÃO CORRIGIDA"""
        print("\nTESTANDO SISTEMA DE CÂMBIO...")
        
        # 🔥 CORREÇÃO: Usar a nova assinatura do método
        cotacao = self.obter_cotacao_simples('USD_BRL')
        print(f"Cotação USD_BRL: {cotacao}")
        
        # Testar cálculo com spread
        if self.usuario_logado:
            # 🔥 CORREÇÃO: Usar self.usuario_logado diretamente (sem ['username'])
            cotacao_cliente = self.calcular_cotacao_cliente(
                'USD',           # moeda_de
                'BRL',           # moeda_para  
                'compra',        # tipo_operacao
                self.usuario_logado  # usuario (já é string)
            )
            print(f"Cotação com spread: {cotacao_cliente}")
        
        # Testar pares disponíveis
        if self.usuario_logado:
            pares = self.obter_pares_disponiveis(self.usuario_logado)
            print(f"Pares disponíveis: {pares}")
        
        print("Teste completo!\n")

    def migrar_ids_antigos_para_novos(self):
        """Migra IDs antigos _novatela para _nt - para compatibilidade"""
        ids_para_migrar = []
        
        for transacao_id, dados in self.transferencias.items():
            if transacao_id.endswith('_novatela'):
                novo_id = transacao_id.replace('_novatela', '_nt')
                ids_para_migrar.append((transacao_id, novo_id))
        
        for id_antigo, novo_id in ids_para_migrar:
            if novo_id not in self.transferencias:
                self.transferencias[novo_id] = self.transferencias[id_antigo]
                self.transferencias[novo_id]['id'] = novo_id
                del self.transferencias[id_antigo]
                print(f"🔄 ID migrado: {id_antigo} -> {novo_id}")

    def carregar_beneficiarios(self):
        """Carrega beneficiários - PRIMEIRO Supabase, depois JSON"""
        try:
            print("🔄 CARREGAR_BENEFICIARIOS INICIADO")
            
            # 1. TENTAR CARREGAR DO SUPABASE
            print("🔍 Tentando carregar do Supabase...")
            beneficiarios_supabase = self.carregar_beneficiarios_supabase()
            
            if beneficiarios_supabase:
                self.beneficiarios = beneficiarios_supabase
                print("✅ Beneficiários carregados do Supabase")
                return
            
            # 2. FALLBACK PARA JSON
            print("🔍 Fallback para JSON...")
            beneficiarios_path = 'data/beneficiarios.json'
            if os.path.exists(beneficiarios_path):
                with open(beneficiarios_path, 'r', encoding='utf-8') as f:
                    self.beneficiarios = json.load(f)
                print(f"✅ {sum(len(b) for b in self.beneficiarios.values())} beneficiários carregados do JSON")
            else:
                self.beneficiarios = {}
                print("ℹ️ Nenhum arquivo de beneficiários encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao carregar beneficiários: {e}")
            self.beneficiarios = {}



# No sistema.py - ADICIONAR ESTES MÉTODOS (com 4 espaços de indentação):

    def carregar_beneficiarios_supabase(self):
        """Carrega beneficiários do Supabase - VERSÃO CORRIGIDA COM COLUNAS EXATAS"""
        try:
            print("🔄 Carregando beneficiários do Supabase...")
            
            response = self.supabase.client.table('beneficiarios').select('*').execute()
            
            print(f"🔍 RESPOSTA DO SUPABASE: {len(response.data)} registros")
            
            if response.data:
                print("🔍 PRIMEIRO REGISTRO (amostra):")
                primeiro = response.data[0]
                print(f"   👤 Cliente: {primeiro.get('cliente_username', 'N/A')}")
                print(f"   📋 Nome: {primeiro.get('nome', 'N/A')}")
                print(f"   🏦 Banco: {primeiro.get('banco', 'N/A')}")
            
            # Reorganizar dados: {usuario: [lista_de_beneficiarios]}
            beneficiarios_organizados = {}
            for ben in response.data:
                # 🔥 CORREÇÃO: Usar 'cliente_username' que é a coluna correta
                usuario = ben.get('cliente_username')
                
                if not usuario:
                    print(f"⚠️  Beneficiário sem cliente_username: {ben.get('nome', 'N/A')}")
                    continue
                
                if usuario not in beneficiarios_organizados:
                    beneficiarios_organizados[usuario] = []
                
                # 🔥 CORREÇÃO: Mapeamento exato das colunas
                beneficiario_formatado = {
                    'nome': ben.get('nome', ''),
                    'banco': ben.get('banco', ''),
                    'swift': ben.get('swift', ''),
                    'iban': ben.get('iban', ''),
                    'endereco': ben.get('endereco', ''),
                    'cidade': ben.get('cidade', ''),
                    'pais': ben.get('pais', ''),
                    'endereco_banco': ben.get('endereco_banco', ''),
                    'cidade_banco': ben.get('cidade_banco', ''),  # 🔥 NOVO
                    'pais_banco': ben.get('pais_banco', ''),      # 🔥 NOVO
                    'aba': ben.get('aba', '')
                }
                beneficiarios_organizados[usuario].append(beneficiario_formatado)
            
            print(f"✅ {len(response.data)} beneficiários carregados do Supabase")
            print(f"🔍 USUÁRIOS COM BENEFICIÁRIOS: {list(beneficiarios_organizados.keys())}")
            
            # Mostrar quantos beneficiários por usuário
            for usuario, lista in beneficiarios_organizados.items():
                print(f"   👤 {usuario}: {len(lista)} beneficiários")
            
            return beneficiarios_organizados
            
        except Exception as e:
            print(f"❌ Erro ao carregar beneficiários do Supabase: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def salvar_beneficiario_supabase(self, dados_beneficiario):
        """Salva beneficiário no Supabase - VERSÃO CORRIGIDA"""
        try:
            print(f"🔍 SALVAR_BENEFICIARIO_SUPABASE CHAMADO")
            print(f"🔍 Dados recebidos: {dados_beneficiario}")
            print(f"🔍 Tem cidade_banco? {'cidade_banco' in dados_beneficiario}")
            print(f"🔍 Tem pais_banco? {'pais_banco' in dados_beneficiario}")
            
            # 🔥 CORREÇÃO: self.usuario_logado é string, usar diretamente
            usuario_atual = self.usuario_logado  # Já é o username como string
            
            # 🔥 CORREÇÃO: Mapeamento exato das colunas - ADICIONANDO OS NOVOS CAMPOS
            dados_supabase = {
                'cliente_username': usuario_atual,
                'nome': dados_beneficiario['nome'],
                'banco': dados_beneficiario['banco'],
                'swift': dados_beneficiario['swift'],
                'iban': dados_beneficiario['iban'],
                'endereco': dados_beneficiario['endereco'],
                'cidade': dados_beneficiario['cidade'],
                'pais': dados_beneficiario['pais'],
                'endereco_banco': dados_beneficiario.get('endereco_banco', ''),
                'cidade_banco': dados_beneficiario.get('cidade_banco', ''),  # 🔥 NOVO
                'pais_banco': dados_beneficiario.get('pais_banco', ''),      # 🔥 NOVO
                'aba': dados_beneficiario.get('aba', ''),
                'data_criacao': datetime.datetime.now().isoformat(),
                'ativo': True
            }
            
            print(f"🔍 Dados para Supabase: {dados_supabase}")
            
            response = self.supabase.client.table('beneficiarios').insert(dados_supabase).execute()
            
            if response.data:
                print(f"✅ Beneficiário salvo no Supabase: {dados_beneficiario['nome']}")
                print(f"🔍 cidade_banco salvo: {dados_supabase['cidade_banco']}")
                print(f"🔍 pais_banco salvo: {dados_supabase['pais_banco']}")
                return True
            else:
                print(f"❌ Erro ao salvar no Supabase: Dados não retornados")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar beneficiário no Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False


    def debug_carregamento_telas(self):
        """Debug do carregamento das telas"""
        print("\n DEBUG CARREGAMENTO TELAS:")
        print(f" Total de usuários: {len(self.usuarios)}")
        print(f" Total de contas: {len(self.contas)}")
        
        # Verificar se o usuário joao.silva existe
        if 'joao.silva' in self.usuarios:
            print("Usuário joao.silva encontrado")
            user = self.usuarios['joao.silva']
            print(f"   Tipo: {user['tipo']}")
            print(f"   Contas: {user.get('contas', [])}")
        else:
            print("Usuário joao.silva NÃO encontrado")
        
        # Verificar spreads
        print(f"Spreads configurados: {len(self.spreads_clientes)}")
        if 'joao.silva' in self.spreads_clientes:
            print(f"Spreads para joao.silva: {self.spreads_clientes['joao.silva']}")

    def debug_estado_cotacoes(self):
        """Debug completo do estado das cotações"""
        print("🔍 DEBUG COMPLETO COTAÇÕES:")
        print(f"📁 Arquivo existe: {os.path.exists('data/cotacoes_config.json')}")
        print(f"👥 Clientes em memória: {len(self.spreads_clientes)}")
        
        # Ler o arquivo diretamente para comparar
        try:
            if os.path.exists('data/cotacoes_config.json'):
                with open('data/cotacoes_config.json', 'r', encoding='utf-8') as f:
                    dados_arquivo = json.load(f)
                print(f"📁 Clientes no arquivo: {len(dados_arquivo.get('spreads_clientes', {}))}")
                
                # Comparar memória vs arquivo
                for username in set(list(self.spreads_clientes.keys()) + list(dados_arquivo.get('spreads_clientes', {}).keys())):
                    spreads_memoria = self.spreads_clientes.get(username, {})
                    spreads_arquivo = dados_arquivo.get('spreads_clientes', {}).get(username, {})
                    
                    print(f"👤 {username}:")
                    print(f"   💾 Memória: {len(spreads_memoria)} spreads")
                    print(f"   📁 Arquivo: {len(spreads_arquivo)} spreads")
                    
                    # Verificar diferenças
                    if spreads_memoria != spreads_arquivo:
                        print(f"   ⚠️  DIFERENÇA DETECTADA!")
                        for par in set(list(spreads_memoria.keys()) + list(spreads_arquivo.keys())):
                            if spreads_memoria.get(par) != spreads_arquivo.get(par):
                                print(f"      📊 {par}:")
                                print(f"         💾 Memória: {spreads_memoria.get(par)}")
                                print(f"         📁 Arquivo: {spreads_arquivo.get(par)}")
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")

    def _organizar_contas_contabeis(self, dados_supabase):
        """Organiza dados do Supabase na estrutura do sistema multi-moeda - VERSÃO CORRIGIDA"""
        contas_organizadas = {
            'receitas': {},
            'despesas': {}
        }
        
        print(f"🔍 Organizando {len(dados_supabase)} contas contábeis...")
        
        for conta in dados_supabase:
            try:
                # 🔥 CORREÇÃO: Usar .get() com valores padrão para evitar KeyError
                tipo = conta.get('tipo', '').strip().lower()
                categoria = conta.get('categoria', '').strip()
                nome = conta.get('nome', '').strip()
                moeda = conta.get('moeda', 'USD').strip().upper()
                
                # 🔥 CORREÇÃO: Tratar saldo como string primeiro e depois converter
                saldo_str = str(conta.get('saldo', '0')).strip()
                saldo = float(saldo_str) if saldo_str else 0.0
                
                # Validar dados obrigatórios
                if not tipo or not categoria or not nome:
                    print(f"⚠️ Conta inválida ignorada - Tipo: '{tipo}', Categoria: '{categoria}', Nome: '{nome}'")
                    continue
                
                # 🔥 CORREÇÃO: Mapear tipos para as chaves corretas
                if tipo == 'receita':
                    tipo_organizado = 'receitas'
                elif tipo == 'despesa':
                    tipo_organizado = 'despesas'
                else:
                    print(f"⚠️ Tipo desconhecido '{tipo}' ignorado")
                    continue
                
                # Criar estrutura se não existir
                if categoria not in contas_organizadas[tipo_organizado]:
                    contas_organizadas[tipo_organizado][categoria] = {}
                
                if nome not in contas_organizadas[tipo_organizado][categoria]:
                    contas_organizadas[tipo_organizado][categoria][nome] = {}
                
                # 🔥 CORREÇÃO: Adicionar moeda ao saldo
                contas_organizadas[tipo_organizado][categoria][nome][moeda] = saldo
                
                print(f"✅ {tipo_organizado.upper()} -> {categoria} -> {nome} -> {moeda} = {saldo:,.2f}")
                
            except Exception as e:
                print(f"❌ Erro ao organizar conta {conta}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 🔥 DEBUG FINAL
        total_receitas = sum(len(contas) for contas in contas_organizadas['receitas'].values())
        total_despesas = sum(len(contas) for contas in contas_organizadas['despesas'].values())
        print(f"🎯 ORGANIZAÇÃO CONCLUÍDA: {total_receitas} contas de receita, {total_despesas} contas de despesa")
        
        return contas_organizadas

    def carregar_contas_contabeis_forcado(self):
        """Força o carregamento das contas contábeis - MÉTODO ALTERNATIVO"""
        try:
            print("🔄 CARREGAMENTO FORÇADO de contas contábeis...")
            
            if hasattr(self, 'supabase') and self.supabase.conectado:
                # Buscar TODOS os registros
                response = self.supabase.client.table('contas_contabeis').select('*').execute()
                
                print(f"📊 Total de registros encontrados: {len(response.data)}")
                
                if response.data:
                    # Mostrar amostra dos dados
                    print("🔍 AMOSTRA DOS DADOS (primeiros 5 registros):")
                    for i, conta in enumerate(response.data[:5]):
                        print(f"   {i+1}. Tipo: {conta.get('tipo')}, Categoria: {conta.get('categoria')}, "
                              f"Nome: {conta.get('nome')}, Moeda: {conta.get('moeda')}, Saldo: {conta.get('saldo')}")
                    
                    # Organizar dados
                    self.contas_contabeis = self._organizar_contas_contabeis(response.data)
                    return True
                else:
                    print("❌ Nenhum dado encontrado na tabela contas_contabeis")
                    return False
            else:
                print("❌ Supabase não conectado")
                return False
                
        except Exception as e:
            print(f"❌ Erro no carregamento forçado: {e}")
            import traceback
            traceback.print_exc()
            return False
        



    def carregar_cotacoes_supabase(self):
        """Carrega dados de cotações do Supabase - mantém fallback para JSON"""
        try:
            if not hasattr(self, 'supabase') or not self.supabase.conectado:
                print("ℹ️ Supabase não disponível, usando JSON local")
                self.carregar_dados_cotacoes()  # Fallback para JSON
                return
            
            print("🔄 Carregando cotações do Supabase...")
            
            # 🔥 GARANTIR QUE AS ESTRUTURAS EXISTEM
            if not hasattr(self, 'spreads_clientes'):
                self.spreads_clientes = {}
            if not hasattr(self, 'permissoes_cambio'):
                self.permissoes_cambio = {}
            if not hasattr(self, 'limites_operacionais'):
                self.limites_operacionais = {}
            if not hasattr(self, 'horarios_clientes'):
                self.horarios_clientes = {}
            if not hasattr(self, 'horario_comercial_padrao'):
                self.horario_comercial_padrao = {
                    'dias_semana': [0, 1, 2, 3, 4],
                    'inicio': '10:00',
                    'fim': '15:00',
                    'fuso_horario': 'America/Sao_Paulo'
                }
            
            # 1. Carregar spreads
            spreads = self.supabase.obter_spreads_clientes()
            if spreads:
                self.spreads_clientes = spreads
                print(f"✅ {len(spreads)} clientes com spreads carregados do Supabase")
            else:
                print("ℹ️ Nenhum spread encontrado no Supabase")
            
            # 2. Carregar permissões (pode estar vazio inicialmente)
            permissoes = self.supabase.obter_permissoes_cambio()
            if permissoes:
                self.permissoes_cambio = permissoes
                print(f"✅ {len(permissoes)} permissões carregadas do Supabase")
            # Se não tiver permissões no Supabase, mantém as atuais (não limpa)
            
            # 3. Carregar limites (pode estar vazio inicialmente)
            limites = self.supabase.obter_limites_operacionais()
            if limites:
                self.limites_operacionais = limites
                print(f"✅ {len(limites)} limites carregados do Supabase")
            # Se não tiver limites no Supabase, mantém os atuais
            
            # 4. Carregar horários clientes (pode estar vazio inicialmente)
            horarios = self.supabase.obter_horarios_clientes()
            if horarios:
                self.horarios_clientes = horarios
                print(f"✅ {len(horarios)} horários de clientes carregados do Supabase")
            # Se não tiver horários no Supabase, mantém os atuais
            
            # 5. Carregar horário padrão
            horario_padrao = self.supabase.obter_horario_comercial_padrao()
            if horario_padrao:
                self.horario_comercial_padrao = horario_padrao
                print("✅ Horário padrão carregado do Supabase")
            # Se não tiver horário padrão, mantém o atual
            
            print("🎯 Cotações carregadas do Supabase com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar cotações do Supabase: {e}")
            print("🔄 Fallback para JSON local...")
            self.carregar_dados_cotacoes()  # Fallback

    def salvar_cotacoes_supabase(self):
        """Salva dados de cotações no Supabase - apenas se conectado"""
        try:
            if not hasattr(self, 'supabase') or not self.supabase.conectado:
                print("ℹ️ Supabase não disponível, salvando apenas localmente")
                return self.salvar_dados_cotacoes()  # Fallback para JSON
            
            print("💾 Salvando cotações no Supabase...")
            sucesso_total = True
            
            # 1. Salvar spreads
            for username, spreads in self.spreads_clientes.items():
                sucesso = self.supabase.salvar_spreads_cliente(username, spreads)
                if not sucesso:
                    sucesso_total = False
                    print(f"⚠️ Erro ao salvar spreads para {username}")
                else:
                    print(f"✅ Spreads salvos para {username}")
            
            # 2. Salvar permissões
            for username, permitido in self.permissoes_cambio.items():
                sucesso = self.supabase.salvar_permissao_cambio(username, permitido)
                if not sucesso:
                    sucesso_total = False
                    print(f"⚠️ Erro ao salvar permissão para {username}")
                else:
                    print(f"✅ Permissão salva para {username}")
            
            # 3. Salvar limites
            for username, limite in self.limites_operacionais.items():
                sucesso = self.supabase.salvar_limite_operacional(username, limite)
                if not sucesso:
                    sucesso_total = False
                    print(f"⚠️ Erro ao salvar limite para {username}")
                else:
                    print(f"✅ Limite salvo para {username}")
            
            # 4. Salvar horários clientes
            for username, horario in self.horarios_clientes.items():
                sucesso = self.supabase.salvar_horario_cliente(username, horario)
                if not sucesso:
                    sucesso_total = False
                    print(f"⚠️ Erro ao salvar horário para {username}")
                else:
                    print(f"✅ Horário salvo para {username}")
            
            # 5. Salvar horário padrão (se existir)
            if hasattr(self, 'horario_comercial_padrao'):
                sucesso = self.supabase.salvar_horario_comercial_padrao(self.horario_comercial_padrao)
                if sucesso:
                    print("✅ Horário padrão salvo")
            
            if sucesso_total:
                print("🎯 Todas as cotações salvas no Supabase!")
            else:
                print("⚠️ Algumas cotações não foram salvas no Supabase")
            
            # SEMPRE salva localmente também (backup)
            self.salvar_dados_cotacoes()
            return sucesso_total
            
        except Exception as e:
            print(f"❌ Erro ao salvar cotações no Supabase: {e}")
            print("🔄 Salvando apenas localmente...")
            return self.salvar_dados_cotacoes()  # Fallback

    def gerar_descricao_cambio_inteligente(self, dados_cambio, conta_num):
        """Gera descrição clara para operações de câmbio - VERSÃO CORRIGIDA"""
        
        # 1. Identificar tipo de câmbio automaticamente
        tipo_cambio = self.identificar_tipo_cambio(dados_cambio, conta_num)
        
        # 2. Obter informações básicas
        operacao = dados_cambio.get('operacao', '')
        moeda_origem = dados_cambio.get('moeda_origem', '')
        moeda_destino = dados_cambio.get('moeda_destino', '')
        valor_origem = dados_cambio.get('valor_origem', 0)
        valor_destino = dados_cambio.get('valor_destino', 0)
        
        # 3. Obter taxa correta
        taxa = self.obter_taxa_correta(dados_cambio, tipo_cambio)
        
        # 4. Gerar descrição baseada no tipo
        if tipo_cambio == 'cliente':
            return self._descricao_cambio_cliente(dados_cambio, conta_num, taxa)
        elif tipo_cambio == 'admin_geral':
            return self._descricao_cambio_admin_geral(dados_cambio, conta_num, taxa)
        elif tipo_cambio == 'admin_contas_bancarias':
            return self._descricao_cambio_admin_bancario(dados_cambio, conta_num, taxa)
        else:
            return self._descricao_cambio_padrao(dados_cambio, conta_num, taxa)

    def identificar_tipo_cambio(self, dados_cambio, conta_num):
        """Identifica automaticamente o tipo de operação de câmbio - VERSÃO INTELIGENTE"""
        
        id_transacao = dados_cambio.get('id', '')
        conta_remetente = dados_cambio.get('conta_remetente', '') or ''
        conta_origem = dados_cambio.get('conta_origem', '') or ''
        conta_destino = dados_cambio.get('conta_destino', '') or ''
        executado_por = dados_cambio.get('executado_por', '')
        usuario = dados_cambio.get('usuario', '')
        tipo = dados_cambio.get('tipo', '')
        
        print(f"🔍 DEBUG IDENTIFICAÇÃO: id={id_transacao}, tipo={tipo}, conta_origem={conta_origem}, conta_destino={conta_destino}")
        
        # 1. CÂMBIO ENTRE CONTAS DA EMPRESA (PRIORIDADE MÁXIMA)
        # Verifica se as contas envolvidas são contas bancárias da empresa
        sistema = App.get_running_app().sistema
        
        def is_conta_empresa(conta):
            if not conta:
                return False
            # Verifica se a conta existe na lista de contas bancárias da empresa
            return conta in sistema.contas_bancarias_empresa
        
        # Verifica se PELO MENOS UMA das contas envolvidas é da empresa
        contas_envolvidas = [conta_origem, conta_destino, conta_remetente, dados_cambio.get('conta_destinatario', '')]
        tem_conta_empresa = any(is_conta_empresa(conta) for conta in contas_envolvidas if conta)
        
        if tem_conta_empresa:
            print(f"✅ IDENTIFICADO: admin_contas_bancarias - Conta da empresa detectada")
            return 'admin_contas_bancarias'
        
        # 2. CÂMBIO ENTRE CONTAS DA EMPRESA pelo tipo específico
        elif tipo == 'cambio_contas_empresa':
            print(f"✅ IDENTIFICADO: admin_contas_bancarias - Tipo específico detectado")
            return 'admin_contas_bancarias'
        
        # 3. CÂMBIO CLIENTE (Nova tela)
        elif '_nt' in id_transacao or 'conta_origem' in dados_cambio:
            print(f"✅ IDENTIFICADO: cliente")
            return 'cliente'
        
        # 4. CÂMBIO ADMIN GERAL (Gerenciar Contas)
        elif (executado_por == 'admin' or usuario == 'admin' or 
              'taxa_principal_exibicao' in dados_cambio):
            print(f"✅ IDENTIFICADO: admin_geral")
            return 'admin_geral'
        
        # 5. PADRÃO (fallback)
        else:
            print(f"✅ IDENTIFICADO: cliente (padrão)")
            return 'cliente'

    def obter_taxa_correta(self, dados_cambio, tipo_cambio):
        """Obtém a taxa correta para cada tipo de câmbio - VERSÃO ROBUSTA"""
        
        print(f"🔍 DEBUG TAXA - Tipo: {tipo_cambio}")
        
        if tipo_cambio == 'cliente':
            # Câmbio cliente: usa 'cotacao' (já com spread)
            taxa = dados_cambio.get('cotacao', 0)
            print(f"🔍 DEBUG TAXA CLIENTE: {taxa}")
            return taxa
        
        elif tipo_cambio == 'admin_geral':
            # Câmbio admin: prioriza taxa_principal_exibicao
            taxa = dados_cambio.get('taxa_principal_exibicao', 0)
            if taxa == 0:
                taxa = dados_cambio.get('cotacao', 0)
            if taxa == 0:
                taxa = dados_cambio.get('taxa_cambio', 0)
            print(f"🔍 DEBUG TAXA ADMIN GERAL: {taxa}")
            return taxa
        
        elif tipo_cambio == 'admin_contas_bancarias':
            # Câmbio contas bancárias: BUSCA EM MÚLTIPLOS CAMPOS
            campos_taxa = [
                'taxa_principal_registro',
                'taxa_cambio', 
                'cotacao',
                'taxa_principal_exibicao'
            ]
            
            for campo in campos_taxa:
                taxa = dados_cambio.get(campo, 0)
                if taxa and taxa > 0:
                    print(f"✅ TAXA ENCONTRADA no campo '{campo}': {taxa}")
                    return taxa
            
            # Fallback: calcular baseado nos valores
            valor_origem = dados_cambio.get('valor_origem', 0)
            valor_destino = dados_cambio.get('valor_destino', 0)
            if valor_origem > 0 and valor_destino > 0:
                taxa_calculada = valor_destino / valor_origem
                print(f"🔧 TAXA CALCULADA: {valor_destino} / {valor_origem} = {taxa_calculada}")
                return taxa_calculada
            
            print(f"⚠️ NENHUMA TAXA ENCONTRADA para admin_contas_bancarias")
            return 0
        
        else:
            taxa = dados_cambio.get('cotacao', 0)
            print(f"🔍 DEBUG TAXA PADRÃO: {taxa}")
            return taxa

    def _descricao_cambio_cliente(self, dados_cambio, conta_num, taxa):
        """Gera descrição para câmbio do cliente"""
        
        operacao = dados_cambio.get('operacao', '')
        moeda_origem = dados_cambio.get('moeda_origem', '')
        moeda_destino = dados_cambio.get('moeda_destino', '')
        valor_origem = dados_cambio.get('valor_origem', 0)
        valor_destino = dados_cambio.get('valor_destino', 0)
        
        if operacao == 'compra':
            return f"COMPRA {moeda_destino} - Pagou {valor_origem:,.2f} {moeda_origem} --> Recebeu {valor_destino:,.2f} {moeda_destino} (Taxa: {taxa:.4f})"
        else:  # venda
            return f"VENDA {moeda_origem} - Vendeu {valor_origem:,.2f} {moeda_origem} --> Recebeu {valor_destino:,.2f} {moeda_destino} (Taxa: {taxa:.4f})"

    def _descricao_cambio_admin_geral(self, dados_cambio, conta_num, taxa):
        """Gera descrição para câmbio admin geral"""
        
        moeda_origem = dados_cambio.get('moeda_origem', '')
        moeda_destino = dados_cambio.get('moeda_destino', '')
        valor_origem = dados_cambio.get('valor_origem', 0)
        valor_destino = dados_cambio.get('valor_destino', 0)
        
        return f"CONVERSÃO ADMIN - {moeda_origem} {valor_origem:,.2f} --> {moeda_destino} {valor_destino:,.2f} (Taxa: {taxa:.4f})"

    def _descricao_cambio_admin_bancario(self, dados_cambio, conta_num, taxa):
        """Gera descrição para câmbio entre contas bancárias"""
        
        moeda_origem = dados_cambio.get('moeda_origem', '')
        moeda_destino = dados_cambio.get('moeda_destino', '')
        valor_origem = dados_cambio.get('valor_origem', 0)
        valor_destino = dados_cambio.get('valor_destino', 0)
        
        return f"CÂMBIO ENTRE CONTAS - {moeda_origem} {valor_origem:,.2f} --> {moeda_destino} {valor_destino:,.2f} (Taxa: {taxa:.6f})"

    def _descricao_cambio_padrao(self, dados_cambio, conta_num, taxa):
        """Descrição padrão (fallback)"""
        
        moeda_origem = dados_cambio.get('moeda_origem', '')
        moeda_destino = dados_cambio.get('moeda_destino', '')
        valor_origem = dados_cambio.get('valor_origem', 0)
        valor_destino = dados_cambio.get('valor_destino', 0)
        
        return f"CÂMBIO - {moeda_origem} {valor_origem:,.2f} --> {moeda_destino} {valor_destino:,.2f} (Taxa: {taxa:.4f})"


    # No arquivo sistema.py, adicione estes métodos DENTRO da classe SistemaCambioPremium:

    def atualizar_contas_usuario_supabase(self, username, conta_id_remover=None):
        """Wrapper para atualizar contas do usuário no Supabase"""
        if hasattr(self, 'supabase') and self.supabase.conectado:
            return self.supabase.atualizar_contas_usuario_supabase(username, conta_id_remover)
        return False

    def excluir_usuario_completo_supabase(self, username):
        """Wrapper para excluir usuário completo do Supabase"""
        if hasattr(self, 'supabase') and self.supabase.conectado:
            return self.supabase.excluir_usuario_completo_supabase(username)
        return False

    def obter_contas_cliente_supabase(self, username):
        """Wrapper para obter contas do cliente do Supabase"""
        if hasattr(self, 'supabase') and self.supabase.conectado:
            return self.supabase.obter_contas_cliente_supabase(username)
        return []

    def atualizar_dados_cliente_supabase(self, username, dados_atualizados):
        """Wrapper para atualizar dados do cliente no Supabase"""
        if hasattr(self, 'supabase') and self.supabase.conectado:
            return self.supabase.atualizar_dados_cliente_supabase(username, dados_atualizados)
        return False

    # No sistema.py, adicione este método:

    def excluir_cliente_preservando_transferencias(self, username):
        """Exclui cliente preservando transferências para histórico contábil"""
        try:
            print(f"🗑️ Excluindo cliente {username} (preservando transferências)...")
            
            # 🔥 PRIORIDADE: Excluir do Supabase (soft delete)
            sucesso_supabase = False
            if hasattr(self, 'supabase') and self.supabase.conectado:
                sucesso_supabase = self.supabase.excluir_usuario_completo_supabase(username)
            
            # 🔥 FALLBACK: Excluir localmente também
            self._excluir_cliente_local_preservando_transferencias(username)
            
            mensagem = f"✅ Cliente {username} excluído"
            if sucesso_supabase:
                mensagem += " do Supabase (soft delete)"
            else:
                mensagem += " apenas localmente"
            
            mensagem += "\n⚠️ Transferências preservadas para histórico contábil"
            
            print(mensagem)
            return True, mensagem
            
        except Exception as e:
            print(f"❌ Erro ao excluir cliente: {e}")
            return False, f"Erro: {str(e)}"

    def _excluir_cliente_local_preservando_transferencias(self, username):
        """Exclui cliente localmente preservando transferências"""
        try:
            # 1. Marcar contas como excluídas (soft delete no cache local)
            contas_cliente = []
            for conta_num, dados_conta in self.contas.items():
                if dados_conta.get('cliente') == username:
                    # Marcar como excluída no cache
                    self.contas[conta_num]['cliente_nome'] = f"[EXCLUÍDO] {dados_conta.get('cliente_nome', username)}"
                    self.contas[conta_num]['ativo'] = False
                    contas_cliente.append(conta_num)
            
            print(f"   🔄 {len(contas_cliente)} contas marcadas como excluídas no cache")
            
            # 2. Remover usuário do cache local
            if username in self.usuarios:
                # Criar backup dos dados antes de remover (opcional)
                dados_backup = {
                    'username': username,
                    'nome': self.usuarios[username].get('nome', ''),
                    'email': self.usuarios[username].get('email', ''),
                    'data_exclusao': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Remover do cache
                del self.usuarios[username]
                print(f"   🗑️ Usuário removido do cache local")
            
            # 3. Remover beneficiários do cache local
            if username in self.beneficiarios:
                del self.beneficiarios[username]
                print(f"   🗑️ Beneficiários removidos do cache")
            
            # 4. Remover configurações de cotações do cache
            for estrutura in [self.spreads_clientes, self.permissoes_cambio, self.limites_operacionais, self.horarios_clientes]:
                if username in estrutura:
                    del estrutura[username]
            
            # 5. 🔥 NÃO REMOVER TRANSFERÊNCIAS - preservar histórico
            print(f"   📊 Transferências preservadas para histórico contábil")
            
            # 6. Salvar dados locais
            self.salvar_usuarios()
            self.salvar_contas()
            self.salvar_beneficiarios()
            self.salvar_dados_cotacoes()
            
            print(f"   💾 Dados locais salvos")
            
        except Exception as e:
            print(f"❌ Erro ao excluir cliente localmente: {e}")
            raise e



    def debug_atributos_sistema(self):
        """Debug para verificar os atributos disponíveis no sistema"""
        print("=== 🔍 DEBUG ATRIBUTOS SISTEMA ===")
        print(f"Horários: {hasattr(self.sistema, 'horarios_clientes')}")
        print(f"Limites: {hasattr(self.sistema, 'limites_operacionais')}")
        print(f"Permissões: {hasattr(self.sistema, 'permissoes_cambio')}")
        print(f"Spreads: {hasattr(self.sistema, 'spreads_clientes')}")
        
        if hasattr(self.sistema, 'limites_operacionais'):
            print(f"Limites disponíveis: {list(self.sistema.limites_operacionais.keys())}")
        if hasattr(self.sistema, 'permissoes_cambio'):
            print(f"Permissões disponíveis: {list(self.sistema.permissoes_cambio.keys())}")
        print("=== 🎯 FIM DEBUG ===")

    def debug_contas_contabeis(self):
        """Debug para verificar o estado das contas contábeis"""
        print("=== 🔍 DEBUG CONTAS CONTÁBEIS ===")
        print(f"Receitas carregadas: {len(self.contas_contabeis['receitas'])} categorias")
        print(f"Despesas carregadas: {len(self.contas_contabeis['despesas'])} categorias")
        
        # Listar categorias de receita
        if self.contas_contabeis['receitas']:
            print("📊 Categorias de RECEITA:")
            for categoria in self.contas_contabeis['receitas']:
                print(f"  📁 {categoria}: {len(self.contas_contabeis['receitas'][categoria])} contas")
        
        # Listar categorias de despesa
        if self.contas_contabeis['despesas']:
            print("📊 Categorias de DESPESA:")
            for categoria in self.contas_contabeis['despesas']:
                print(f"  📁 {categoria}: {len(self.contas_contabeis['despesas'][categoria])} contas")
        
        print("=== 🎯 FIM DEBUG ===")

    def testar_conexao_beneficiarios(self):
        """Testa a conexão com a tabela beneficiários"""
        try:
            print("🧪 TESTANDO CONEXÃO COM BENEFICIÁRIOS...")
            print(f"Supabase conectado: {self.supabase.conectado}")
            print(f"Cliente disponível: {self.supabase.client is not None}")
            
            # Testar consulta simples
            response = self.supabase.client.table('beneficiarios').select('count').execute()
            print(f"Resposta da contagem: {response.data}")
            
            return True
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
