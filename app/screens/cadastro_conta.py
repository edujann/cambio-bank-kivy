# cadastro_conta.py
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
import random
import datetime
import hashlib

class TelaCadastroConta(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        Window.size = (500, 1000)
        self.posicionar_janela()
        print(f"🎯 Cadastro Conta: Tamanho ajustado para {Window.size}")
        self.limpar_formulario()

    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("📝 Tela de cadastro de conta carregada")
        
        # 🔥 CONFIGURAR ORDEM DE NAVEGAÇÃO COM TAB (igual ao cadastro cliente)
        self.ids.username.focus_next = self.ids.senha
        self.ids.senha.focus_next = self.ids.confirmar_senha
        self.ids.confirmar_senha.focus_next = self.ids.nome
        self.ids.nome.focus_next = self.ids.email
        self.ids.email.focus_next = self.ids.documento
        self.ids.documento.focus_next = self.ids.telefone
        self.ids.telefone.focus_next = self.ids.endereco
        self.ids.endereco.focus_next = self.ids.cidade
        self.ids.cidade.focus_next = self.ids.cep
        self.ids.cep.focus_next = self.ids.estado
        self.ids.estado.focus_next = self.ids.pais
        self.ids.pais.focus_next = self.ids.outras_moedas
        self.ids.outras_moedas.focus_next = self.ids.username  # Loop
        
        # Focar no primeiro campo
        self.ids.username.focus = True

    def posicionar_janela(self):
        """Centraliza a janela na tela"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            window_width, window_height = Window.size
            x = (screen_width - window_width) // 4
            y = (screen_height - window_height) // 6
            
            x = max(x, 20)
            y = max(y, 20)
            
            Window.top = y
            Window.left = x
            
            print(f"📍 Cadastro Conta: Janela posicionada em ({x}, {y})")
            
        except Exception as e:
            print(f"⚠️ Não foi possível posicionar: {e}")
            Window.top = 30
            Window.left = 50
            print("📍 Cadastro Conta: Posição fallback definida")

    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        campos = [
            'username', 'senha', 'confirmar_senha', 'nome', 
            'email', 'documento', 'telefone', 'endereco', 
            'cidade', 'cep', 'estado', 'pais', 'outras_moedas'
        ]
        
        for campo_id in campos:
            if hasattr(self, 'ids') and campo_id in self.ids:
                self.ids[campo_id].text = ''
        
        # Resetar checkboxes das moedas (todas marcadas por padrão)
        moedas_checkboxes = ['moeda_usd', 'moeda_eur', 'moeda_gbp', 'moeda_brl']
        for checkbox_id in moedas_checkboxes:
            if hasattr(self, 'ids') and checkbox_id in self.ids:
                self.ids[checkbox_id].active = True

    def validar_formulario(self):
        """Valida todos os campos do formulário"""
        sistema = App.get_running_app().sistema
        
        # Verificar campos obrigatórios
        campos_obrigatorios = {
            'username': 'Usuário',
            'senha': 'Senha', 
            'confirmar_senha': 'Confirmar Senha',
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'documento': 'CPF/CNPJ',
            'endereco': 'Endereço',
            'cidade': 'Cidade', 
            'cep': 'CEP',
            'estado': 'Estado',
            'pais': 'País'
        }
        
        for campo_id, nome_campo in campos_obrigatorios.items():
            if not self.ids[campo_id].text.strip():
                return False, f"Preencha o campo: {nome_campo}"
        
        # Verificar se senhas coincidem
        if self.ids.senha.text != self.ids.confirmar_senha.text:
            return False, "As senhas não coincidem"
        
        # Verificar tamanho mínimo da senha
        if len(self.ids.senha.text) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres"
        
        # Validar email básico
        if '@' not in self.ids.email.text or '.' not in self.ids.email.text:
            return False, "Digite um e-mail válido"
        
        # 🔥 CORREÇÃO: Verificar se usuário JÁ EXISTE (não deve existir)
        username = self.ids.username.text.strip()
        if username in sistema.usuarios:
            return False, f"Usuário '{username}' já existe no sistema. Escolha outro nome."
        
        # Validar que pelo menos uma moeda foi selecionada
        moedas_selecionadas = self.obter_moedas_selecionadas()
        if not moedas_selecionadas:
            return False, "Selecione pelo menos uma moeda"
        
        return True, ""

    def obter_moedas_selecionadas(self):
        """Retorna lista de moedas selecionadas"""
        moedas_selecionadas = []
        
        # Moedas padrão
        if self.ids.moeda_usd.active:
            moedas_selecionadas.append('USD')
        if self.ids.moeda_eur.active:
            moedas_selecionadas.append('EUR')
        if self.ids.moeda_gbp.active:
            moedas_selecionadas.append('GBP')
        if self.ids.moeda_brl.active:
            moedas_selecionadas.append('BRL')
        
        # Outras moedas personalizadas
        outras_moedas_texto = self.ids.outras_moedas.text.strip()
        if outras_moedas_texto:
            outras_moedas = [moeda.strip().upper() for moeda in outras_moedas_texto.split(',') if moeda.strip()]
            moedas_selecionadas.extend(outras_moedas)
        
        return moedas_selecionadas

    def criar_conta(self):
        """Processa a criação do novo cliente e contas COM VERIFICAÇÃO POR EMAIL"""
        sistema = App.get_running_app().sistema
        
        print("👥 Processando cadastro de novo cliente e contas...")
        
        # Validar formulário
        valido, mensagem = self.validar_formulario()
        if not valido:
            print(f"❌ {mensagem}")
            self.mostrar_erro_cadastro(mensagem)
            return
        
        try:
            # Coletar dados
            username = self.ids.username.text.strip()
            senha = self.ids.senha.text
            nome_cliente = self.ids.nome.text.strip()
            email = self.ids.email.text.strip()
            documento = self.ids.documento.text.strip()
            telefone = self.ids.telefone.text.strip()
            endereco = self.ids.endereco.text.strip()
            cidade = self.ids.cidade.text.strip()
            cep = self.ids.cep.text.strip()
            estado = self.ids.estado.text.strip()
            pais = self.ids.pais.text.strip()
            
            # Coletar moedas selecionadas
            moedas_selecionadas = self.obter_moedas_selecionadas()
            
            print(f"📋 DADOS COLETADOS:")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Nome: {nome_cliente}")
            print(f"   Documento: {documento}")
            print(f"   Moedas: {moedas_selecionadas}")
            
            # Verificar se usuário já existe
            if username in sistema.usuarios:
                self.mostrar_erro_cadastro("Usuário já existe! Escolha outro nome.")
                return
            
            # Verificar se email já existe
            for user_data in sistema.usuarios.values():
                if user_data.get('email') == email:
                    self.mostrar_erro_cadastro("Email já cadastrado! Use outro email.")
                    return
            
            # Criar hash da senha
            senha_hash = sistema.hash_senha(senha)
            print(f"🔐 Senha hash criada: {senha_hash[:20]}...")
            
            # Preparar dados extras
            dados_usuario = {
                'nome': nome_cliente,
                'email': email,
                'documento': documento,
                'telefone': telefone,
                'endereco': endereco,
                'cidade': cidade,
                'cep': cep,
                'estado': estado,
                'pais': pais,
                'moedas_selecionadas': moedas_selecionadas
            }
            
            print(f"📤 Chamando cadastrar_usuario_pendente...")
            resultado = sistema.cadastrar_usuario_pendente(username, email, senha_hash, dados_usuario)
            
            print(f"📥 RESULTADO: {resultado}")
            
            if resultado['sucesso']:
                if resultado.get('modo_simulacao'):
                    print(f"✅ Cadastro pendente criado para {username}. Código: {resultado['codigo']}")
                    
                    # 🔥 CORREÇÃO: Navegar para verificação
                    self.ir_para_verificacao(email, resultado['codigo'])
                    
                else:
                    # Modo produção
                    self.ir_para_verificacao(email, None)
            else:
                erro_msg = resultado.get('erro', 'Erro desconhecido')
                print(f"❌ ERRO NO CADASTRO: {erro_msg}")
                self.mostrar_erro_cadastro(f"Erro ao criar conta: {erro_msg}")
            
        except Exception as e:
            print(f"🔥 ERRO CRÍTICO ao criar conta: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro_cadastro(f"Erro interno: {str(e)}")
    
    def ir_para_verificacao(self, email, codigo):
        """Navega para tela de verificação - VERSÃO MELHORADA"""
        try:
            print(f"🔗 Navegando para tela de verificação...")
            print(f"   Email: {email}")
            print(f"   Código: {codigo}")
            
            # 1. Verificar se o manager existe
            if not hasattr(self, 'manager') or not self.manager:
                print("❌ Manager não disponível")
                self.mostrar_erro_cadastro("Erro interno: tela não configurada")
                return
            
            # 2. Obter tela de verificação
            try:
                tela_verificacao = self.manager.get_screen('verificacao_email')
            except:
                print("❌ Tela 'verificacao_email' não encontrada no manager")
                self.mostrar_erro_cadastro("Erro: tela de verificação não disponível")
                return
            
            # 3. Verificar se o método configurar_dados existe
            if not hasattr(tela_verificacao, 'configurar_dados'):
                print("❌ Método configurar_dados não existe na tela de verificação")
                self.mostrar_erro_cadastro("Erro interno: tela mal configurada")
                return
            
            # 4. Configurar dados
            print("⚙️ Configurando dados na tela de verificação...")
            tela_verificacao.configurar_dados(email, codigo)
            
            print(f"✅ Dados configurados:")
            print(f"   Email: {email}")
            print(f"   Código: {codigo}")
            
            # 5. Navegar para a tela
            print("🎯 Navegando para tela de verificação...")
            self.manager.current = 'verificacao_email'
            
            print(f"✅ TELA DE VERIFICAÇÃO ABERTA para {email}")
            
        except Exception as e:
            print(f"🔥 ERRO CRÍTICO ao navegar para verificação: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro_cadastro(f"Erro ao abrir tela de verificação")

    def mostrar_sucesso_cadastro(self, username, nome_cliente, contas_criadas, moedas_selecionadas):
        """Mostra um popup de sucesso quando o cliente e contas são criados"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_sucesso = Label(
            text='CLIENTE E CONTAS CRIADOS COM SUCESSO!',
            color=(0.2, 0.8, 0.2, 1),
            font_size='16sp',
            bold=True,
            text_size=(400, None),
            halign='center'
        )
        
        # Detalhes do cadastro (igual ao cadastro cliente)
        detalhes = f"""
Usuário: {username}
Nome: {nome_cliente}
Moedas: {', '.join(moedas_selecionadas)}

CONTAS CRIADAS:
"""
        for conta_numero, moeda in contas_criadas:
            detalhes += f"• {conta_numero} | {moeda} | Saldo: 0.00\n"
        
        lbl_detalhes = Label(
            text=detalhes,
            color=(0.9, 0.9, 0.9, 1),
            font_size='12sp',
            text_size=(400, None),
            halign='left'
        )
        
        btn_ok = Button(
            text='VOLTAR AO LOGIN',
            size_hint_y=None,
            height=45,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(lbl_detalhes)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='✅ Cadastro Concluído',
            title_color=(0.2, 0.8, 0.2, 1),
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(450, 400),
            background_color=(0.12, 0.16, 0.23, 1),
            separator_color=(0.55, 0.36, 0.96, 1),
            auto_dismiss=False
        )
        
        def voltar_login(instance):
            popup.dismiss()
            self.manager.current = 'login'
        
        btn_ok.bind(on_press=voltar_login)
        popup.open()

    def mostrar_erro_cadastro(self, mensagem):
        """Mostra um popup de erro para cadastro falho"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='TENTAR NOVAMENTE',
            size_hint_y=None,
            height=40,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='❌ Erro no Cadastro',
            title_color=(1, 0.3, 0.3, 1),
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def cancelar_cadastro(self):
        """Volta para a tela de login"""
        print("❌ Criação de conta cancelada")
        self.manager.current = 'login'