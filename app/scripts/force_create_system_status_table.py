import sqlite3
import os
from app.utils.logger_config import get_logger, log_system_event

logger = get_logger('scripts')

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'cadastro.db'))

def force_create_system_status_table():
    logger.info("Iniciando criação forçada da tabela system_status")
    logger.info(f"Caminho do banco: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        logger.warning(f"Arquivo de banco não encontrado: {DB_PATH}. Criando...")
        try:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            open(DB_PATH, 'a').close()
            logger.info(f"Arquivo de banco criado: {DB_PATH}")
        except Exception as e:
            logger.error(f"Erro ao criar arquivo de banco: {str(e)}")
            raise
    
    try:
        logger.info("Conectando ao banco de dados...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logger.info("Conexão estabelecida com sucesso")
        
        # Verificar se a tabela já existe
        logger.debug("Verificando se a tabela system_status já existe...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_status';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            logger.warning("Tabela system_status já existe. Removendo...")
            cursor.execute("DROP TABLE IF EXISTS system_status;")
            logger.info("Tabela system_status removida")
        
        logger.info("Criando tabela system_status...")
        cursor.execute('''
            CREATE TABLE system_status (
                id INTEGER PRIMARY KEY,
                status VARCHAR(64) NOT NULL DEFAULT 'OK',
                last_update DATETIME,
                maintenance_mode BOOLEAN DEFAULT 0,
                maintenance_message VARCHAR(500) DEFAULT 'Sistema em manutenção. Por favor, tente novamente mais tarde.'
            );
        ''')
        
        logger.info("Tabela system_status criada com sucesso")
        
        # Verificar se a tabela foi criada corretamente
        logger.debug("Verificando estrutura da tabela criada...")
        cursor.execute("PRAGMA table_info(system_status);")
        columns = cursor.fetchall()
        logger.info(f"Colunas da tabela system_status: {[col[1] for col in columns]}")
        
        # Inserir registro inicial
        logger.info("Inserindo registro inicial na tabela system_status...")
        cursor.execute('''
            INSERT INTO system_status (status, last_update, maintenance_mode, maintenance_message)
            VALUES ('OK', datetime('now'), 0, 'Sistema em manutenção. Por favor, tente novamente mais tarde.')
        ''')
        
        conn.commit()
        logger.info("Registro inicial inserido com sucesso")
        
        # Verificar se o registro foi inserido
        cursor.execute("SELECT * FROM system_status;")
        record = cursor.fetchone()
        if record:
            logger.info(f"Registro inicial verificado - ID: {record[0]}, Status: {record[1]}")
        else:
            logger.warning("Registro inicial não encontrado após inserção")
        
        conn.close()
        logger.info("Conexão com banco fechada")
        
        log_system_event("TABELA_CRIADA", "Tabela system_status criada com sucesso", "INFO")
        print("Tabela 'system_status' criada com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao criar tabela system_status: {str(e)}")
        log_system_event("ERRO_TABELA", f"Erro ao criar tabela system_status: {str(e)}", "ERROR")
        print(f"Erro ao criar tabela: {e}")
        raise
    finally:
        if 'conn' in locals():
            try:
                conn.close()
                logger.debug("Conexão fechada no finally")
            except Exception as e:
                logger.error(f"Erro ao fechar conexão no finally: {str(e)}")

if __name__ == "__main__":
    logger.info("Executando script force_create_system_status_table.py")
    try:
        force_create_system_status_table()
        logger.info("Script executado com sucesso")
    except Exception as e:
        logger.error(f"Script falhou: {str(e)}")
        raise
