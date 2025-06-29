import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging(app_name='mutirao_mulher', log_level=logging.INFO):
    """
    Configura o sistema de logging para toda a aplicação
    
    Args:
        app_name: Nome da aplicação para identificação nos logs
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Cria diretório de logs se não existir
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = log_dir / f'{app_name}_{timestamp}.log'
    
    # Configuração do formato dos logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configuração do logger principal
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Handler para arquivo
            logging.FileHandler(log_file, encoding='utf-8'),
            # Handler para console
            logging.StreamHandler()
        ]
    )
    
    # Cria logger específico para a aplicação
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # Evita duplicação de logs
    if not logger.handlers:
        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Configura loggers específicos para diferentes módulos
    loggers = {
        'app': logging.getLogger(f'{app_name}.app'),
        'database': logging.getLogger(f'{app_name}.database'),
        'auth': logging.getLogger(f'{app_name}.auth'),
        'cadastro': logging.getLogger(f'{app_name}.cadastro'),
        'api': logging.getLogger(f'{app_name}.api'),
        'admin': logging.getLogger(f'{app_name}.admin'),
        'models': logging.getLogger(f'{app_name}.models'),
        'scripts': logging.getLogger(f'{app_name}.scripts'),
        'backup': logging.getLogger(f'{app_name}.backup'),
        'scheduler': logging.getLogger(f'{app_name}.scheduler')
    }
    
    # Configura todos os loggers com o mesmo nível
    for name, logger_instance in loggers.items():
        logger_instance.setLevel(log_level)
    
    logger.info(f"Sistema de logging configurado - Arquivo: {log_file}")
    logger.info(f"Nível de logging: {logging.getLevelName(log_level)}")
    
    return logger, loggers

def get_logger(module_name='app'):
    """
    Retorna um logger específico para o módulo
    
    Args:
        module_name: Nome do módulo (app, database, auth, etc.)
    
    Returns:
        Logger configurado para o módulo
    """
    return logging.getLogger(f'mutirao_mulher.{module_name}')

def log_function_call(func):
    """
    Decorator para logar entrada e saída de funções
    
    Args:
        func: Função a ser decorada
    
    Returns:
        Função decorada com logs
    """
    def wrapper(*args, **kwargs):
        logger = get_logger('app')
        func_name = func.__name__
        module_name = func.__module__
        
        logger.debug(f"ENTRADA: {module_name}.{func_name} - Args: {args} - Kwargs: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"SAÍDA: {module_name}.{func_name} - Resultado: {result}")
            return result
        except Exception as e:
            logger.error(f"ERRO: {module_name}.{func_name} - Exceção: {str(e)}")
            raise
    
    return wrapper

def log_database_operation(operation, table, record_id=None, user=None):
    """
    Função utilitária para logar operações de banco de dados
    
    Args:
        operation: Tipo de operação (CREATE, READ, UPDATE, DELETE)
        table: Nome da tabela
        record_id: ID do registro (opcional)
        user: Usuário que executou a operação (opcional)
    """
    logger = get_logger('database')
    user_info = f" - Usuário: {user}" if user else ""
    record_info = f" - ID: {record_id}" if record_id else ""
    
    logger.info(f"DB {operation}: Tabela {table}{record_info}{user_info}")

def log_api_request(method, endpoint, user=None, status_code=None, error=None):
    """
    Função utilitária para logar requisições da API
    
    Args:
        method: Método HTTP (GET, POST, PUT, DELETE)
        endpoint: Endpoint da API
        user: Usuário que fez a requisição (opcional)
        status_code: Código de status da resposta (opcional)
        error: Erro ocorrido (opcional)
    """
    logger = get_logger('api')
    user_info = f" - Usuário: {user}" if user else ""
    status_info = f" - Status: {status_code}" if status_code else ""
    error_info = f" - Erro: {error}" if error else ""
    
    if error:
        logger.error(f"API {method} {endpoint}{user_info}{status_info}{error_info}")
    else:
        logger.info(f"API {method} {endpoint}{user_info}{status_info}")

def log_security_event(event_type, user=None, details=None, ip_address=None):
    """
    Função utilitária para logar eventos de segurança
    
    Args:
        event_type: Tipo do evento (LOGIN, LOGOUT, ACCESS_DENIED, etc.)
        user: Usuário envolvido (opcional)
        details: Detalhes adicionais (opcional)
        ip_address: Endereço IP (opcional)
    """
    logger = get_logger('auth')
    user_info = f" - Usuário: {user}" if user else ""
    ip_info = f" - IP: {ip_address}" if ip_address else ""
    details_info = f" - Detalhes: {details}" if details else ""
    
    logger.warning(f"SEGURANÇA {event_type}{user_info}{ip_info}{details_info}")

def log_system_event(event_type, details=None, severity='INFO'):
    """
    Função utilitária para logar eventos do sistema
    
    Args:
        event_type: Tipo do evento
        details: Detalhes do evento
        severity: Severidade (INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger('app')
    details_info = f" - {details}" if details else ""
    
    if severity == 'ERROR':
        logger.error(f"SISTEMA {event_type}{details_info}")
    elif severity == 'WARNING':
        logger.warning(f"SISTEMA {event_type}{details_info}")
    elif severity == 'CRITICAL':
        logger.critical(f"SISTEMA {event_type}{details_info}")
    else:
        logger.info(f"SISTEMA {event_type}{details_info}") 