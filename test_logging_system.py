#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de logging
"""

import sys
import os
import logging
from datetime import datetime

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logging_system():
    """Testa o sistema de logging"""
    print("=" * 60)
    print("🧪 TESTE DO SISTEMA DE LOGGING")
    print("=" * 60)
    
    try:
        # Importa o sistema de logging
        from app.utils.logger_config import setup_logging, get_logger, log_system_event, log_database_operation, log_api_request, log_security_event
        
        print("✅ Módulo de logging importado com sucesso")
        
        # Configura o logging
        print("\n📝 Configurando sistema de logging...")
        logger, loggers = setup_logging('test_logging', log_level=logging.DEBUG)
        print("✅ Sistema de logging configurado")
        
        # Testa diferentes tipos de log
        print("\n🔍 Testando diferentes tipos de log...")
        
        # Logs de sistema
        log_system_event("TESTE", "Teste de evento do sistema", "INFO")
        log_system_event("AVISO", "Teste de aviso do sistema", "WARNING")
        log_system_event("ERRO", "Teste de erro do sistema", "ERROR")
        
        # Logs de banco de dados
        log_database_operation("CREATE", "test_table", 123, "test_user")
        log_database_operation("READ", "test_table", 123, "test_user")
        log_database_operation("UPDATE", "test_table", 123, "test_user")
        log_database_operation("DELETE", "test_table", 123, "test_user")
        
        # Logs de API
        log_api_request("GET", "/api/test", "test_user", 200)
        log_api_request("POST", "/api/test", "test_user", 201)
        log_api_request("PUT", "/api/test", "test_user", 400, "Bad Request")
        log_api_request("DELETE", "/api/test", "test_user", 500, "Internal Server Error")
        
        # Logs de segurança
        log_security_event("LOGIN", "test_user", "Login bem-sucedido", "192.168.1.1")
        log_security_event("LOGOUT", "test_user", "Logout realizado", "192.168.1.1")
        log_security_event("ACCESS_DENIED", "test_user", "Tentativa de acesso negado", "192.168.1.1")
        
        # Logs diretos do logger
        logger.debug("Mensagem de debug")
        logger.info("Mensagem de informação")
        logger.warning("Mensagem de aviso")
        logger.error("Mensagem de erro")
        logger.critical("Mensagem crítica")
        
        # Testa loggers específicos
        print("\n🔧 Testando loggers específicos...")
        
        db_logger = get_logger('database')
        db_logger.info("Teste do logger de banco de dados")
        
        api_logger = get_logger('api')
        api_logger.info("Teste do logger de API")
        
        auth_logger = get_logger('auth')
        auth_logger.info("Teste do logger de autenticação")
        
        models_logger = get_logger('models')
        models_logger.info("Teste do logger de modelos")
        
        backup_logger = get_logger('backup')
        backup_logger.info("Teste do logger de backup")
        
        scripts_logger = get_logger('scripts')
        scripts_logger.info("Teste do logger de scripts")
        
        print("✅ Todos os loggers específicos testados")
        
        # Verifica se os arquivos de log foram criados
        print("\n📁 Verificando arquivos de log...")
        
        log_files = []
        if os.path.exists('logs'):
            for file in os.listdir('logs'):
                if file.endswith('.log'):
                    log_files.append(file)
                    file_path = os.path.join('logs', file)
                    file_size = os.path.getsize(file_path)
                    print(f"  📄 {file} - {file_size} bytes")
        
        if log_files:
            print(f"✅ {len(log_files)} arquivo(s) de log encontrado(s)")
        else:
            print("⚠️  Nenhum arquivo de log encontrado")
        
        # Testa o decorator de função
        print("\n🎯 Testando decorator de função...")
        
        from app.utils.logger_config import log_function_call
        
        @log_function_call
        def test_function(param1, param2, kwarg1="default"):
            return f"Resultado: {param1} + {param2} + {kwarg1}"
        
        result = test_function("valor1", "valor2", kwarg1="teste")
        print(f"✅ Função decorada executada: {result}")
        
        print("\n" + "=" * 60)
        print("🎉 TESTE DO SISTEMA DE LOGGING CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\n📋 Resumo:")
        print("  ✅ Sistema de logging configurado")
        print("  ✅ Logs de sistema testados")
        print("  ✅ Logs de banco de dados testados")
        print("  ✅ Logs de API testados")
        print("  ✅ Logs de segurança testados")
        print("  ✅ Loggers específicos testados")
        print("  ✅ Decorator de função testado")
        print(f"  📄 {len(log_files)} arquivo(s) de log criado(s)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_log_file_content():
    """Testa o conteúdo dos arquivos de log"""
    print("\n" + "=" * 60)
    print("📖 VERIFICANDO CONTEÚDO DOS ARQUIVOS DE LOG")
    print("=" * 60)
    
    if not os.path.exists('logs'):
        print("❌ Diretório de logs não encontrado")
        return
    
    log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
    
    for log_file in log_files:
        file_path = os.path.join('logs', log_file)
        print(f"\n📄 Arquivo: {log_file}")
        print("-" * 40)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"Total de linhas: {len(lines)}")
            
            if lines:
                print("Últimas 5 linhas:")
                for line in lines[-5:]:
                    print(f"  {line.strip()}")
            else:
                print("Arquivo vazio")
                
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {str(e)}")

if __name__ == "__main__":
    print(f"🚀 Iniciando teste do sistema de logging - {datetime.now()}")
    
    success = test_logging_system()
    
    if success:
        test_log_file_content()
        print(f"\n✅ Teste concluído com sucesso - {datetime.now()}")
    else:
        print(f"\n❌ Teste falhou - {datetime.now()}")
        sys.exit(1) 