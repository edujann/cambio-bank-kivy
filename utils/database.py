"""
Database Manager for Cambio Bank
Gerencia operações de banco de dados para o sistema de câmbio
"""
import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """
    Gerenciador do banco de dados SQLite para operações de câmbio
    """
    
    def __init__(self, db_name="cambio_bank.db"):
        self.db_name = db_name
        self.connection = None
        self._create_tables()
    
    def _create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            cursor = self.connection.cursor()
            
            # Tabela de taxas de câmbio
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS taxas_cambio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    moeda_origem TEXT NOT NULL,
                    moeda_destino TEXT NOT NULL,
                    taxa_compra REAL NOT NULL,
                    taxa_venda REAL NOT NULL,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de transações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    moeda_origem TEXT NOT NULL,
                    moeda_destino TEXT NOT NULL,
                    valor_origem REAL NOT NULL,
                    valor_destino REAL NOT NULL,
                    taxa_aplicada REAL NOT NULL,
                    data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Inserir taxas iniciais se a tabela estiver vazia
            cursor.execute("SELECT COUNT(*) FROM taxas_cambio")
            if cursor.fetchone()[0] == 0:
                self._insert_initial_rates(cursor)
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
        finally:
            if self.connection:
                self.connection.close()
    
    def _insert_initial_rates(self, cursor):
        """Insere taxas de câmbio iniciais"""
        taxas_iniciais = [
            ('USD', 'BRL', 5.45, 5.55),  # Dólar para Real
            ('EUR', 'BRL', 6.20, 6.30),  # Euro para Real
            ('BRL', 'USD', 0.18, 0.17),  # Real para Dólar
            ('BRL', 'EUR', 0.16, 0.15),  # Real para Euro
            ('USD', 'EUR', 0.88, 0.90),  # Dólar para Euro
            ('EUR', 'USD', 1.10, 1.12),  # Euro para Dólar
        ]
        
        cursor.executemany('''
            INSERT INTO taxas_cambio (moeda_origem, moeda_destino, taxa_compra, taxa_venda)
            VALUES (?, ?, ?, ?)
        ''', taxas_iniciais)
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_name)
    
    def get_taxa_cambio(self, moeda_origem, moeda_destino, operacao='compra'):
        """
        Obtém a taxa de câmbio para um par de moedas
        
        Args:
            moeda_origem: Moeda de origem (ex: 'USD')
            moeda_destino: Moeda de destino (ex: 'BRL')
            operacao: 'compra' ou 'venda'
        
        Returns:
            float: Taxa de câmbio ou None se não encontrada
        """
        try:
            self.connection = self.get_connection()
            cursor = self.connection.cursor()
            
            coluna_taxa = 'taxa_venda' if operacao == 'venda' else 'taxa_compra'
            
            cursor.execute(f'''
                SELECT {coluna_taxa} FROM taxas_cambio 
                WHERE moeda_origem = ? AND moeda_destino = ?
            ''', (moeda_origem, moeda_destino))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar taxa: {e}")
            return None
        finally:
            if self.connection:
                self.connection.close()
    
    def registrar_transacao(self, tipo, moeda_origem, moeda_destino, 
                           valor_origem, valor_destino, taxa_aplicada):
        """
        Registra uma transação no banco de dados
        
        Args:
            tipo: Tipo de operação ('compra' ou 'venda')
            moeda_origem: Moeda de origem
            moeda_destino: Moeda de destino
            valor_origem: Valor na moeda de origem
            valor_destino: Valor na moeda de destino
            taxa_aplicada: Taxa aplicada na operação
        """
        try:
            self.connection = self.get_connection()
            cursor = self.connection.cursor()
            
            cursor.execute('''
                INSERT INTO transacoes 
                (tipo, moeda_origem, moeda_destino, valor_origem, valor_destino, taxa_aplicada)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tipo, moeda_origem, moeda_destino, valor_origem, valor_destino, taxa_aplicada))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao registrar transação: {e}")
            return False
        finally:
            if self.connection:
                self.connection.close()
    
    def get_historico_transacoes(self, limite=10):
        """
        Obtém o histórico de transações
        
        Args:
            limite: Número máximo de transações a retornar
        
        Returns:
            list: Lista de transações
        """
        try:
            self.connection = self.get_connection()
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT * FROM transacoes 
                ORDER BY data_transacao DESC 
                LIMIT ?
            ''', (limite,))
            
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
        finally:
            if self.connection:
                self.connection.close()


# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()