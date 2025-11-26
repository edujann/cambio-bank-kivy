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

    def cadastrar_usuario_pendente(self, usuario, email, senha, dados_extras):
        """Cadastra usuário como pendente de verificação - MODO SIMULAÇÃO"""
        codigo = self.gerar_codigo_verificacao()
        
        # Armazenar dados temporários
        self.usuarios_nao_verificados[email] = {
            'usuario': usuario,
            'senha': senha,
            'dados': dados_extras,
            'timestamp': time.time()
        }
        
        self.codigos_verificacao[email] = {
            'codigo': codigo,
            'timestamp': time.time()
        }
        
        # 🔥 MODO SIMULAÇÃO - Mostra código na tela em vez de enviar email
        print(f"🎯 MODO SIMULAÇÃO: Código de verificação para {email}: {codigo}")
        
        return {
            'sucesso': True,
            'modo_simulacao': True,
            'codigo': codigo,
            'email': email
        }

    def verificar_codigo_email(self, email, codigo_digitado):
        """Verifica se o código digitado está correto"""
        if email not in self.codigos_verificacao:
            return False, "Email não encontrado para verificação"
        
        dados_codigo = self.codigos_verificacao[email]
        codigo_correto = dados_codigo['codigo']
        timestamp = dados_codigo['timestamp']
        
        # Verificar expiração (15 minutos)
        if time.time() - timestamp > 900:  # 15 minutos
            del self.codigos_verificacao[email]
            return False, "Código expirado. Solicite um novo."
        
        if codigo_digitado == codigo_correto:
            # Código correto - completar cadastro
            return self.completar_cadastro(email), "Cadastro verificado com sucesso!"
        else:
            return False, "Código incorreto. Tente novamente."

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
                'contas': [],
                'data_cadastro': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            
            # Criar contas baseadas nas moedas selecionadas
            moedas_selecionadas = dados.get('moedas_selecionadas', [])
            if moedas_selecionadas:
                self.criar_contas_cliente(usuario, dados['nome'], moedas_selecionadas)
            
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
        """
        Converte string de data para objeto datetime - VERSÃO UNIFICADA
        USAR EM TODO O SISTEMA para consistência
        """
        import datetime
        
        # 1. 🔥 SE DATA É VAZIA/NULA: Usa data ATUAL (não 2000-01-01)
        if not data_str or data_str in ['None', 'null', '']:
            return datetime.datetime.now()  # ✅ Data atual como fallback
        
        # Converter para string se necessário
        data_str = str(data_str).strip()
        
        try:
            # 2. 📅 FORMATO 1: "2025-11-19 14:44:24" (com espaço)
            if ' ' in data_str and ':' in data_str:
                return datetime.datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
            
            # 3. 🌐 FORMATO 2: "2025-11-19T14:44:24" (formato ISO)
            elif 'T' in data_str:
                # Remove timezone: "2025-11-19T14:44:24.21892Z" → "2025-11-19T14:44:24.21892"
                data_str = data_str.split('+')[0].split('Z')[0]
                
                # Se tem microssegundos, usar formato completo
                if '.' in data_str:
                    return datetime.datetime.strptime(data_str, "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    return datetime.datetime.strptime(data_str, "%Y-%m-%dT%H:%M:%S")
            
            # 4. 📆 FORMATO 3: "2025-11-19" (apenas data)
            else:
                return datetime.datetime.strptime(data_str, "%Y-%m-%d")
                
        except Exception as e:
            print(f"⚠️ Erro ao parse data '{data_str}': {e}")
            # 5. 🆘 SE TUDO FALHAR: Usa data ATUAL
            return datetime.datetime.now()

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
                'contas': [],
                'data_cadastro': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            
            # Criar contas baseadas nas moedas selecionadas
            moedas_selecionadas = dados.get('moedas_selecionadas', ['USD', 'BRL'])
            if moedas_selecionadas:
                self.criar_contas_cliente(usuario, dados['nome'], moedas_selecionadas)
            
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
        """Faz login do usuário - VERSÃO COMPATÍVEL SUPABASE"""
        if usuario in self.usuarios:
            # 🔥 COMPATIBILIDADE: Supabase usa 'senha_hash', JSON usa 'senha'
            usuario_data = self.usuarios[usuario]
            
            # Verificar se a senha está em 'senha' (JSON) ou 'senha_hash' (Supabase)
            senha_armazenada = usuario_data.get('senha') or usuario_data.get('senha_hash', '')
            
            senha_hash = self.hash_senha(senha)
            
            if senha_armazenada == senha_hash:
                self.usuario_logado = usuario
                self.tipo_usuario_logado = usuario_data.get('tipo', 'cliente')
                print(f"✅ Login bem-sucedido: {usuario} ({self.tipo_usuario_logado})")
                return True
        
        print(f"❌ Login falhou para: {usuario}")
        return False
    
    def calcular_saldos_usuario(self):
        """Calcula saldos por moeda do usuário logado - VERSÃO ORIGINAL"""
        if not self.usuario_logado:
            print("❌ Nenhum usuário logado para calcular saldos")
            return {}
        
        usuario_data = self.usuarios.get(self.usuario_logado, {})
        contas_usuario = usuario_data.get('contas', [])
        
        saldos = {}
        username = self.usuario_logado
        
        print(f"🔍 Calculando saldos para: {username}")
        print(f"📋 Contas do usuário: {contas_usuario}")
        
        for conta_num in contas_usuario:
            if conta_num in self.contas:
                conta = self.contas[conta_num]
                moeda = conta['moeda']
                saldo = conta['saldo']
                
                print(f"   💳 Conta {conta_num}: {moeda} = {saldo}")
                
                if moeda in saldos:
                    saldos[moeda] += saldo
                else:
                    saldos[moeda] = saldo
            else:
                print(f"   ⚠️ Conta {conta_num} não encontrada no sistema")
        
        print(f"💰 Saldos finais: {saldos}")
        return saldos  # 🔥 VOLTAR PARA O ORIGINAL - SEM ORDENAÇÃO
        
        # 🔥🔥🔥 ADICIONAR APENAS ESTA PARTE PARA ORDENAR
        ordem_moedas = ['USD', 'GBP', 'EUR', 'BRL']
        saldos_ordenados = {}
        
        for moeda in ordem_moedas:
            if moeda in saldos:
                saldos_ordenados[moeda] = saldos[moeda]
        
        # Adicionar outras moedas que não estão na ordem padrão
        for moeda, saldo in saldos.items():
            if moeda not in saldos_ordenados:
                saldos_ordenados[moeda] = saldo
        
        print(f"💰 Saldos ORDENADOS: {saldos_ordenados}")
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
            
            # 🔥 CORREÇÃO: self.usuario_logado é string, usar diretamente
            usuario_atual = self.usuario_logado  # Já é o username como string
            
            print(f"🔍 Usuário atual: {usuario_atual} (tipo: {type(usuario_atual)})")
            
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
            
            # 🔥 DADOS DA INVOICE
            invoice_data = {
                'status': 'pending',  # 🔥 SEMPRE VOLTA PARA PENDENTE NO REENVIO
                'caminho_arquivo': caminho_arquivo,
                'data_upload': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'motivo_recusa': None,  # 🔥 LIMPAR MOTIVO DA RECUSA ANTERIOR
                'data_recusa': None     # 🔥 LIMPAR DATA DA RECUSA ANTERIOR
            }
            
            # 1. SALVAR LOCALMENTE
            self.transferencias[transferencia_id]['invoice_info'] = invoice_data
            self.salvar_transferencias()
            
            # 2. 🔥 AGORA SALVAR NO SUPABASE TAMBÉM
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('transferencias')\
                        .update({'invoice_info': invoice_data})\
                        .eq('id', transferencia_id)\
                        .execute()
                    
                    if response.error:
                        print(f"⚠️ Erro ao salvar invoice no Supabase: Dados não retornados")
                    else:
                        print(f"✅ Invoice salva no Supabase também!")
                except Exception as e:
                    print(f"⚠️ Erro Supabase: {e}")
            
            print(f"✅ Nova invoice adicionada para transferência {transferencia_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar invoice info: {e}")
            return False

    def aprovar_invoice(self, transferencia_id):
        """Aprova uma invoice - NÃO altera status da transferência - VERSÃO SUPABASE"""
        try:
            # 🔥 CORREÇÃO: Atualizar invoice_info no Supabase
            update_data = {
                'invoice_info': {
                    'status': 'approved',
                    'motivo_recusa': '',
                    'data_upload': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
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
        """Recusa uma invoice - VERSÃO SUPABASE (NÃO deleta arquivo do Storage)"""
        try:
            # 🔥 CORREÇÃO: Buscar invoice_info atual do Supabase
            response = self.supabase.client.table('transferencias')\
                .select('invoice_info')\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response.data:
                print(f"❌ Transferência {transferencia_id} não encontrada no Supabase")
                return False
            
            current_invoice_info = response.data[0].get('invoice_info', {})
            
            # 🔥 CORREÇÃO: Atualizar invoice_info no Supabase (NÃO deletar arquivo)
            update_data = {
                'invoice_info': {
                    'status': 'rejected',
                    'motivo_recusa': motivo,
                    'data_recusa': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'caminho_arquivo': current_invoice_info.get('caminho_arquivo'),  # 🔥 MANTER caminho
                    'data_upload': current_invoice_info.get('data_upload')
                }
            }
            
            response = self.supabase.client.table('transferencias')\
                .update(update_data)\
                .eq('id', transferencia_id)\
                .execute()
            
            if response.data:
                print(f"✅ Invoice recusada no Supabase para transferência {transferencia_id}")
                print(f"📝 Motivo: {motivo}")
                
                # 🔥 CORREÇÃO: Sincronizar dados locais
                if transferencia_id in self.transferencias:
                    self.transferencias[transferencia_id]['invoice_info'] = update_data['invoice_info']
                    self.salvar_transferencias()
                
                return True
            else:
                print(f"❌ Erro ao recusar invoice no Supabase: Dados não retornados")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao recusar invoice: {e}")
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
                        
                        # 🔥 ATUALIZAR OS DADOS LOCAIS PARA SINCRONIZAÇÃO
                        if transferencia_id in self.transferencias:
                            self.transferencias[transferencia_id]['invoice_info'] = invoice_data
                        
                        return invoice_data
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
        """Cria nova conta bancária da empresa - VERSÃO SUPABASE COM ARREDONDAMENTO"""
        try:
            # Verificar se o número da conta já existe
            if numero_conta in self.contas_bancarias_empresa:
                return False, "Número da conta já existe!"
            
            # 🔥 VALIDAÇÃO DA MOEDA - 3 DÍGITOS E ALFANUMÉRICO
            if len(moeda) != 3 or not moeda.isalpha():
                return False, "Moeda inválida! Deve ter exatamente 3 letras.\nEx: USD, EUR, JPY, CAD, BRL, etc."
            
            moeda = moeda.upper()  # Garantir maiúsculas
            
            # 🔥 DADOS DA NOVA CONTA COM ARREDONDAMENTO
            saldo_arredondado = self.arredondar_valor(0.00)  # 🔥 ARREDONDADO
            nova_conta = {
                'numero': numero_conta,
                'banco': banco,
                'agencia': agencia,
                'moeda': moeda,
                'saldo': saldo_arredondado,  # 🔥 JÁ ARREDONDADO
                'tipo': 'empresa',
                'data_criacao': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'saldo_inicial': saldo_arredondado  # 🔥 JÁ ARREDONDADO
            }
            
            # 🔥 PRIMEIRO: SALVAR NO SUPABASE (COM ARREDONDAMENTO)
            if hasattr(self, 'supabase') and self.supabase.conectado:
                try:
                    response = self.supabase.client.table('contas_bancarias_empresa')\
                        .insert(nova_conta)\
                        .execute()
                    
                    if not response.data:
                        return False, "Erro ao salvar conta no Supabase!"
                    
                    print(f"✅ Conta {numero_conta} salva no Supabase (Saldo: {saldo_arredondado:,.2f})")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao salvar conta no Supabase: {e}")
                    return False, f"Erro ao salvar conta no sistema: {str(e)}"
            
            # 🔥 DEPOIS: SALVAR LOCALMENTE (também com arredondamento)
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
                    
                    if response.data:
                        self.contas_bancarias_empresa.clear()
                        for conta in response.data:
                            conta_num = conta['numero']
                            
                            # 🔥 ARREDONDAR SALDO AO CARREGAR DO SUPABASE
                            saldo_arredondado = self.arredondar_valor(float(conta['saldo']))
                            
                            self.contas_bancarias_empresa[conta_num] = {
                                'numero': conta['numero'],
                                'banco': conta['banco'],
                                'agencia': conta.get('agencia', ''),
                                'moeda': conta['moeda'],
                                'saldo': saldo_arredondado,  # 🔥 ARREDONDADO
                                'tipo': conta.get('tipo', 'empresa'),
                                'data_criacao': conta.get('data_criacao', ''),
                                'saldo_inicial': self.arredondar_valor(float(conta.get('saldo_inicial', conta['saldo'])))  # 🔥 ARREDONDADO
                            }
                        
                        print(f"✅ {len(response.data)} contas bancárias carregadas do Supabase (valores arredondados)")
                        
                        # 🔥 SALVAR LOCALMENTE PARA BACKUP (já arredondado)
                        self.salvar_contas_bancarias()
                        return
                        
                except Exception as e:
                    print(f"⚠️ Erro ao carregar contas do Supabase: {e}")
            
            # 🔥 FALLBACK: CARREGAR DO ARQUIVO LOCAL (já vem arredondado)
            if os.path.exists('data/contas_bancarias.json'):
                with open('data/contas_bancarias.json', 'r', encoding='utf-8') as f:
                    self.contas_bancarias_empresa = json.load(f)
                print(f"🔄 DASHBOARD: {len(self.contas_bancarias_empresa)} contas bancárias RECARREGADAS")
                
        except Exception as e:
            print(f"❌ Erro ao carregar contas bancárias: {e}")

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
        """Salva um beneficiário no Supabase - VERSÃO CORRIGIDA"""
        try:
            # 🔥 CORREÇÃO: self.usuario_logado é string, usar diretamente
            usuario_atual = self.usuario_logado  # Já é o username como string
            
            # 🔥 CORREÇÃO: Mapeamento exato das colunas
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
                'aba': dados_beneficiario.get('aba', ''),
                'data_criacao': datetime.datetime.now().isoformat(),
                'ativo': True
            }
            
            response = self.supabase.client.table('beneficiarios').insert(dados_supabase).execute()
            
            if response.data:
                print(f"✅ Beneficiário salvo no Supabase: {dados_beneficiario['nome']}")
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
