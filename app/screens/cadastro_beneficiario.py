from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import datetime

class TelaCadastroBeneficiario(Screen):
    """Tela para cadastrar ou editar beneficiários"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modo_edicao = False
        self.nome_original = ""
    
    def on_pre_enter(self):
        from kivy.core.window import Window
        Window.size = (550, 800)
        
        if not self.modo_edicao:
            self.limpar_formulario()
            if hasattr(self, 'ids') and 'lbl_titulo' in self.ids:
                self.ids.lbl_titulo.text = 'CADASTRAR BENEFICIÁRIO'
                self.ids.btn_salvar.text = 'SALVAR BENEFICIÁRIO'
    
    def on_enter(self):
        print("📝 Tela de cadastro de beneficiário carregada")
    
    def carregar_dados_edicao(self, nome_beneficiario, dados):
        self.modo_edicao = True
        self.nome_original = nome_beneficiario
        
        if not hasattr(self, 'ids'):
            return
        
        # 🔥 GARANTIR que os novos campos existam (mesmo que vazios)
        dados_completos = dados.copy()
        dados_completos.setdefault('cidade_banco', '')
        dados_completos.setdefault('pais_banco', '')
        
        # Agora todos os campos existem
        self.ids.lbl_titulo.text = 'EDITAR BENEFICIÁRIO'
        self.ids.btn_salvar.text = 'ATUALIZAR BENEFICIÁRIO'
        
        self.ids.entry_beneficiario.text = dados_completos.get('nome', '')
        self.ids.entry_endereco.text = dados_completos.get('endereco', '')
        self.ids.entry_cidade.text = dados_completos.get('cidade', '')
        self.ids.entry_pais.text = dados_completos.get('pais', '')
        self.ids.entry_banco.text = dados_completos.get('banco', '')
        self.ids.endereco_banco.text = dados_completos.get('endereco_banco', '')
        self.ids.cidade_banco.text = dados_completos.get('cidade_banco', '')  # ✅ SEMPRE EXISTE
        self.ids.pais_banco.text = dados_completos.get('pais_banco', '')      # ✅ SEMPRE EXISTE
        self.ids.entry_swift.text = dados_completos.get('swift', '')
        self.ids.entry_iban.text = dados_completos.get('iban', '')
        self.ids.entry_aba.text = dados_completos.get('aba', '')
    
    def limpar_formulario(self):
        if hasattr(self, 'ids'):
            campos = [
                'entry_beneficiario', 'entry_endereco', 'entry_cidade', 'entry_pais',
                'entry_banco', 'endereco_banco', 'entry_swift', 'entry_iban', 'entry_aba'
            ]
            
            for campo_id in campos:
                if campo_id in self.ids:
                    self.ids[campo_id].text = ''
    
    def validar_formulario(self):
        """Valida os dados do formulário"""
        if not hasattr(self, 'ids'):
            return False, "Erro interno: Formulário não carregado"
        
        campos_obrigatorios = [
            ('entry_beneficiario', 'Nome do Beneficiário'),
            ('entry_endereco', 'Endereço'),
            ('entry_cidade', 'Cidade'),
            ('entry_pais', 'País'),
            ('entry_banco', 'Banco'),
            ('cidade_banco', 'Cidade do Banco'),  # 🔥 NOVO
            ('pais_banco', 'País do Banco'),      # 🔥 NOVO
            ('entry_swift', 'Código SWIFT'),
            ('entry_iban', 'IBAN')
        ]
        
        for campo_id, campo_nome in campos_obrigatorios:
            if campo_id not in self.ids:
                return False, f"Campo {campo_nome} não encontrado"
            
            valor = self.ids[campo_id].text.strip()
            if not valor:
                return False, f"⚠️ {campo_nome} é obrigatório"
        
        # 🔥 REMOVIDAS as validações específicas de SWIFT e IBAN
        # SWIFT não precisa ter 8 ou 11 caracteres
        # IBAN não precisa ter pelo menos 15 caracteres
        
        return True, ""
       
    def atualizar_beneficiario_existente(self, novos_dados):
        """Atualiza um beneficiário existente - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        usuario_atual = sistema.usuario_logado['username']
        
        try:
            if usuario_atual not in sistema.beneficiarios:
                print(f"❌ Usuário {usuario_atual} não tem beneficiários cadastrados")
                return False
            
            lista_beneficiarios = sistema.beneficiarios[usuario_atual]
            print(f"🔍 Buscando beneficiário: {self.nome_original}")
            print(f"🔍 Lista de beneficiários: {[b['nome'] for b in lista_beneficiarios]}")
            
            # Encontrar o beneficiário pelo nome original
            for i, beneficiario in enumerate(lista_beneficiarios):
                if beneficiario['nome'] == self.nome_original:
                    print(f"✅ Beneficiário encontrado na posição {i}")
                    
                    # 🔥 CORREÇÃO: Garantir que todos os campos obrigatórios existam
                    dados_atualizados = beneficiario.copy()  # Começa com os dados originais
                    
                    # Atualiza apenas os campos que foram modificados
                    for campo, valor in novos_dados.items():
                        dados_atualizados[campo] = valor
                    
                    # 🔥 GARANTIR que data_cadastro existe
                    if 'data_cadastro' not in dados_atualizados:
                        dados_atualizados['data_cadastro'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Substitui na lista
                    lista_beneficiarios[i] = dados_atualizados
                    
                    # Salva no sistema
                    sucesso = sistema.salvar_beneficiarios()
                    print(f"💾 Salvamento no sistema: {sucesso}")
                    
                    print(f"✅ Beneficiário atualizado: {self.nome_original} -> {dados_atualizados['nome']}")
                    return True
            
            print(f"❌ Beneficiário '{self.nome_original}' não encontrado para atualização")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao atualizar beneficiário: {e}")
            import traceback
            traceback.print_exc()
            return False

    def salvar_beneficiario_local(self):  # 🔥 MUDAR O NOME AQUI
        sistema = App.get_running_app().sistema
        
        print("💾 Iniciando salvamento de beneficiário...")
        print(f"🔍 Modo edição: {self.modo_edicao}")
        print(f"🔍 Nome original: {self.nome_original}")
        
        valido, mensagem = self.validar_formulario()
        if not valido:
            print(f"❌ Validação falhou: {mensagem}")
            self.mostrar_erro(mensagem)
            return
        
        try:
            # Coletar dados do formulário
            dados_beneficiario = {
                'nome': self.ids.entry_beneficiario.text.strip(),
                'endereco': self.ids.entry_endereco.text.strip(),
                'cidade': self.ids.entry_cidade.text.strip(),
                'pais': self.ids.entry_pais.text.strip(),
                'banco': self.ids.entry_banco.text.strip(),
                'endereco_banco': self.ids.endereco_banco.text.strip(),
                'cidade_banco': self.ids.cidade_banco.text.strip(),  # 🔥 NOVO
                'pais_banco': self.ids.pais_banco.text.strip(),      # 🔥 NOVO
                'swift': self.ids.entry_swift.text.strip(),
                'iban': self.ids.entry_iban.text.strip(),
                'aba': self.ids.entry_aba.text.strip(),
                'data_cadastro': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"📝 Dados coletados: {dados_beneficiario}")
            
            if self.modo_edicao:
                print("🔄 Modo EDIÇÃO - Chamando atualizar_beneficiario_existente")
                sucesso = self.atualizar_beneficiario_existente(dados_beneficiario)
                if sucesso:
                    print("✅ Atualização bem-sucedida!")
                    self.mostrar_sucesso(f"✅ Beneficiário '{dados_beneficiario['nome']}' atualizado com sucesso!")
                    self.voltar_beneficiarios()
                else:
                    print("❌ Falha na atualização!")
                    self.mostrar_erro("❌ Erro ao atualizar beneficiário!")
            else:
                print("🆕 Modo NOVO - Chamando sistema.salvar_beneficiario")
                sucesso = sistema.salvar_beneficiario(dados_beneficiario)
                if sucesso:
                    print("✅ Salvamento bem-sucedido!")
                    self.mostrar_sucesso(f"✅ Beneficiário '{dados_beneficiario['nome']}' salvo com sucesso!")
                    self.voltar_beneficiarios()
                else:
                    print("❌ Falha no salvamento!")
                    self.mostrar_erro("❌ Erro ao salvar beneficiário!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar beneficiário: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro interno: {str(e)}")
    
    def voltar_beneficiarios(self):
        """Volta para a tela de beneficiários"""
        self.manager.current = 'meus_beneficiarios'
    
    def mostrar_erro(self, mensagem):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp'
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
            title='❌ Erro',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def mostrar_sucesso(self, mensagem):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='14sp'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='✅ Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def fechar_e_voltar(instance):
            popup.dismiss()
        
        btn_ok.bind(on_press=fechar_e_voltar)
        popup.open()