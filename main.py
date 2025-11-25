import logging
import os

# 🔇 SILENCIAR SUPABASE - COLOCAR NO TOPO ABSOLUTO
os.environ['SUPABASE_LOG_LEVEL'] = 'ERROR'
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('supabase').setLevel(logging.WARNING)
logging.getLogger('hpack').setLevel(logging.WARNING)

import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock import Clock

Config.set('graphics', 'position', 'custom')

# Configurar caminhos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'app'))

# 🔥 IMPORTAR TODAS AS TELAS
from sistema import SistemaCambioPremium
from screens.login import TelaLogin
from screens.dashboard import TelaDashboard
from screens.transferencia import TelaTransferencia
from screens.cadastro_cliente import TelaCadastroCliente
from screens.aprovar_operacoes import TelaAprovarOperacoes
from screens.minhas_transferencias import TelaMinhasTransferencias
from screens.meus_beneficiarios import TelaMeusBeneficiarios
from screens.cadastro_beneficiario import TelaCadastroBeneficiario
from screens.gerenciar_contas import TelaGerenciarContas
from screens.meu_extrato import TelaMeuExtrato
from screens.meus_dados import TelaMeusDados
from screens.cadastro_conta import TelaCadastroConta
from screens.suporte import TelaSuporte  
from screens.gerenciar_transferencias import TelaGerenciarTransferencias
from screens.gerenciar_cliente_detalhe import TelaGerenciarClienteDetalhe
from screens.listar_clientes import TelaListarClientes
from screens.configuracoes import TelaConfiguracoes
from screens.contas_bancarias import TelaContasBancarias
from screens.confirmar_depositos import TelaConfirmarDepositos
from screens.cambio_moedas import TelaCambioMoedas
from screens.cotacoes_admin import TelaCotacoesAdmin  
from temas import GerenciadorTemas
from screens.verificacao_email import TelaVerificacaoEmail

class CambioBankApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sistema = SistemaCambioPremium()
        self.gerenciador_temas = GerenciadorTemas()
        self.title = "CAMBIO BANK"
    
    def build(self):
        print("Iniciando aplicação...")

        # 🔥 APLICAR TEMA AO INICIAR
        tema_atual = self.sistema.configuracoes['interface'].get('tema', 'escuro')
        self.gerenciador_temas.aplicar_tema(tema_atual, self)        
        
        Window.clearcolor = (0.06, 0.09, 0.16, 1)
        Window.size = (400, 700)
        
        # Carregar KV files
        kv_path = os.path.join(current_dir, 'app', 'screens', 'kv')
        
        # 🔍 VERIFICAÇÃO DOS ARQUIVOS KV
        kv_files = [
            'telaLogin.kv', 'telaDashboard.kv', 'telaTransferencia.kv',
            'telaCadastroCliente.kv', 'telaAprovarOperacoes.kv', 
            'telaMinhasTransferencias.kv', 'telaMeusBeneficiarios.kv',
            'telaCadastroBeneficiario.kv', 'telaGerenciarContas.kv',
            'telaMeuExtrato.kv', 'telaMeusDados.kv', 'telaSuporte.kv',
            'telaGerenciarTransferencias.kv', 'telaGerenciarClienteDetalhe.kv',
            'telaCadastroConta.kv', 'telaListarClientes.kv',
            'telaConfiguracoes.kv', 'telaContasBancarias.kv',
            'telaExtratoContaBancaria.kv',
            'telaConfirmarDepositos.kv',
            'telaCambioMoedas.kv',
            'telaCotacoesAdmin.kv',
            'telaVerificacaoEmail.kv'
        ]

        for kv_file in kv_files:
            file_path = os.path.join(kv_path, kv_file)
            if os.path.exists(file_path):
                try:
                    Builder.load_file(file_path)
                    print(f" {kv_file} carregado")
                except Exception as e:
                    print(f"❌ ERRO ao carregar {kv_file}: {e}")
            else:
                print(f" Arquivo KV não encontrado: {kv_file}")

        print(" Telas carregadas!")
        
        sm = ScreenManager()
        sm.add_widget(TelaLogin(name='login'))
        sm.add_widget(TelaDashboard(name='dashboard'))
        sm.add_widget(TelaTransferencia(name='transferencia'))
        sm.add_widget(TelaCadastroCliente(name='cadastro_cliente'))
        sm.add_widget(TelaAprovarOperacoes(name='aprovar_operacoes'))
        sm.add_widget(TelaMinhasTransferencias(name='minhas_transferencias'))
        sm.add_widget(TelaMeusBeneficiarios(name='meus_beneficiarios'))
        sm.add_widget(TelaCadastroBeneficiario(name='cadastro_beneficiario'))
        sm.add_widget(TelaGerenciarContas(name='gerenciar_contas'))
        sm.add_widget(TelaMeuExtrato(name='meu_extrato'))
        sm.add_widget(TelaMeusDados(name='meus_dados'))
        sm.add_widget(TelaCadastroConta(name='cadastro_conta'))
        sm.add_widget(TelaSuporte(name='suporte'))
        sm.add_widget(TelaGerenciarTransferencias(name='gerenciar_transferencias'))
        sm.add_widget(TelaGerenciarClienteDetalhe(name='gerenciar_cliente_detalhe'))
        sm.add_widget(TelaListarClientes(name='listar_clientes'))
        sm.add_widget(TelaConfiguracoes(name='configuracoes'))
        sm.add_widget(TelaContasBancarias(name='contas_bancarias'))
        sm.add_widget(TelaConfirmarDepositos(name='confirmar_depositos'))
        sm.add_widget(TelaCambioMoedas(name='cambio_moedas'))
        sm.add_widget(TelaCotacoesAdmin(name='cotacoes_admin'))
        sm.add_widget(TelaVerificacaoEmail(name='verificacao_email'))
        
        print(f" {len(sm.screens)} telas registradas")

        # 🔥 FORÇAR CARREGAMENTO COMPLETO ANTES DE MOSTRAR
        print("🔄 Forçando carregamento completo da interface...")
        Window.create_window()
        Clock.schedule_once(lambda dt: None, 0.1)  # Força um ciclo de atualização
        
        print("✅ Interface completamente carregada")
        return sm

    def on_stop(self):
        """Chamado quando o aplicativo está fechando - SALVA TUDO"""
        print("🚪 APLICATIVO FECHANDO - SALVANDO TODOS OS DADOS...")
        
        try:
            # Salvar dados de cotações (spreads, limites, horários)
            if hasattr(self, 'sistema'):
                sucesso = self.sistema.salvar_dados_cotacoes()
                if sucesso:
                    print("✅ Dados de cotações salvos ao fechar")
                else:
                    print("❌ Falha ao salvar dados de cotações ao fechar")
            
            # Salvar dados principais (contas, transferências, etc.)
            if hasattr(self, 'sistema'):
                self.sistema.salvar_dados()
                print("✅ Dados principais salvos ao fechar")
                
        except Exception as e:
            print(f"❌ Erro ao salvar dados ao fechar: {e}")

if __name__ == '__main__':
    CambioBankApp().run()