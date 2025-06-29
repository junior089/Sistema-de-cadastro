import os
import shutil
import sqlite3
import zipfile
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
from app.utils.logger_config import get_logger, log_system_event

logger = get_logger('backup')

class DatabaseBackup:
    def __init__(self, app_config: Dict, backup_dir: str = 'backups'):
        logger.info("Inicializando sistema de backup")
        self.backup_dir = os.path.abspath(backup_dir)
        self.db_path = app_config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        logger.info(f"Diretório de backup: {self.backup_dir}")
        logger.info(f"Caminho do banco: {self.db_path}")
        
        self.setup_logging()
        self.setup_backup_directory()

    def setup_logging(self) -> None:
        logger.debug("Configurando logging específico do backup")
        log_dir = 'logs'
        Path(log_dir).mkdir(exist_ok=True)

        # Configuração específica para logs de backup
        backup_logger = logging.getLogger('DatabaseBackup')
        backup_logger.setLevel(logging.INFO)
        
        # Evita duplicação de handlers
        if not backup_logger.handlers:
            file_handler = logging.FileHandler(os.path.join(log_dir, 'backup.log'), encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            backup_logger.addHandler(file_handler)
        
        self.logger = backup_logger
        logger.info("Logging de backup configurado")

    def setup_backup_directory(self) -> None:
        logger.info("Configurando diretórios de backup")
        Path(self.backup_dir).mkdir(exist_ok=True)

        # Cria subdiretórios para diferentes tipos de backup
        subdirs = ['daily', 'weekly', 'monthly', 'manual', 'safety']
        for subdir in subdirs:
            subdir_path = os.path.join(self.backup_dir, subdir)
            Path(subdir_path).mkdir(exist_ok=True)
            logger.debug(f"Subdiretório criado/verificado: {subdir_path}")
        
        logger.info("Diretórios de backup configurados com sucesso")

    def validate_database(self) -> bool:
        """Valida se o banco de dados está acessível e íntegro"""
        logger.info("Iniciando validação do banco de dados")
        
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"Banco de dados não encontrado: {self.db_path}")
                return False
            
            logger.debug("Testando conexão com o banco de dados...")
            # Testa a conexão e integridade
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verifica se as tabelas principais existem
            logger.debug("Verificando existência das tabelas principais...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Tabelas encontradas: {tables}")
            
            required_tables = ['cadastro', 'user', 'system_status']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.warning(f"Tabelas ausentes: {missing_tables}")
            else:
                logger.info("Todas as tabelas principais encontradas")
            
            # Verifica integridade do banco
            logger.debug("Verificando integridade do banco...")
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            if integrity_result[0] != 'ok':
                logger.error(f"Falha na verificação de integridade: {integrity_result[0]}")
                return False
            
            logger.info("Verificação de integridade passou com sucesso")
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar banco de dados: {str(e)}")
            return False

    def create_backup(self, backup_type: str = 'manual') -> Tuple[bool, str]:
        logger.info(f"Iniciando criação de backup - Tipo: {backup_type}")
        
        try:
            # Valida o banco antes de fazer backup
            logger.debug("Validando banco antes do backup...")
            if not self.validate_database():
                error_msg = "Banco de dados inválido ou inacessível"
                logger.error(error_msg)
                return False, error_msg

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_subdir = os.path.join(self.backup_dir, backup_type)
            backup_base = f'cadastro_backup_{timestamp}'
            backup_db = os.path.join(backup_subdir, f'{backup_base}.db')
            backup_zip = os.path.join(backup_subdir, f'{backup_base}.zip')

            logger.info(f"Arquivos de backup serão criados:")
            logger.info(f"  - Backup DB: {backup_db}")
            logger.info(f"  - Backup ZIP: {backup_zip}")

            # Verifica se o banco existe
            if not os.path.exists(self.db_path):
                error_msg = f"Banco de dados não encontrado em {self.db_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # Cria o backup do banco
            logger.debug("Criando backup do banco de dados...")
            source = sqlite3.connect(self.db_path)
            dest = sqlite3.connect(backup_db)

            with dest:
                source.backup(dest)

            source.close()
            dest.close()
            logger.info("Backup do banco criado com sucesso")

            # Verifica se o backup foi criado corretamente
            if not os.path.exists(backup_db) or os.path.getsize(backup_db) == 0:
                error_msg = "Falha ao criar arquivo de backup"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info(f"Tamanho do backup: {os.path.getsize(backup_db)} bytes")

            # Cria arquivo ZIP com o backup e metadados
            logger.debug("Criando arquivo ZIP com metadados...")
            with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Adiciona o arquivo do banco
                zf.write(backup_db, os.path.basename(backup_db))

                # Adiciona metadados
                metadata = {
                    'timestamp': timestamp,
                    'type': backup_type,
                    'db_size': os.path.getsize(backup_db),
                    'backup_date': datetime.now().isoformat(),
                    'original_db_path': self.db_path,
                    'backup_version': '1.0'
                }

                zf.writestr('metadata.json', json.dumps(metadata, indent=2))

            logger.info("Arquivo ZIP criado com sucesso")

            # Remove o arquivo .db após criar o ZIP
            os.remove(backup_db)
            logger.debug("Arquivo .db temporário removido")

            self.logger.info(f"Backup criado com sucesso: {backup_zip}")
            logger.info(f"Backup criado com sucesso: {backup_zip}")
            
            # Limpeza de backups antigos
            logger.debug("Iniciando limpeza de backups antigos...")
            self.cleanup_old_backups(backup_type)

            log_system_event("BACKUP_CRIADO", f"Backup {backup_type} criado: {backup_zip}", "INFO")
            return True, f"Backup criado com sucesso em {backup_zip}"

        except Exception as e:
            error_msg = f"Erro ao criar backup: {str(e)}"
            self.logger.error(error_msg)
            logger.error(error_msg)
            log_system_event("ERRO_BACKUP", error_msg, "ERROR")
            return False, error_msg

    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        logger.info(f"Iniciando restauração de backup: {backup_path}")
        
        try:
            backup_path = os.path.normpath(backup_path)
            self.logger.info(f"Original backup path: {backup_path}")
            backup_path = os.path.normpath(backup_path)
            self.logger.info(f"Normalized backup path: {backup_path}")

            if not os.path.exists(backup_path):
                error_msg = f"Arquivo de backup não encontrado: {backup_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # Cria backup de segurança antes de restaurar
            logger.info("Criando backup de segurança antes da restauração...")
            safety_backup = self.create_safety_backup()
            if not safety_backup[0]:
                error_msg = "Falha ao criar backup de segurança"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info("Backup de segurança criado com sucesso")

            if backup_path.endswith('.zip'):
                logger.debug("Processando arquivo ZIP...")
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    # Verifica se o ZIP contém o arquivo do banco
                    db_files = [f for f in zf.namelist() if f.endswith('.db')]
                    if not db_files:
                        error_msg = "Arquivo ZIP não contém banco de dados"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    db_file = db_files[0]
                    temp_dir = os.path.join(self.backup_dir, 'temp')
                    Path(temp_dir).mkdir(exist_ok=True)
                    zf.extract(db_file, temp_dir)
                    backup_db_path = os.path.join(temp_dir, db_file)
                    logger.info(f"Arquivo extraído: {backup_db_path}")
            else:
                backup_db_path = backup_path
                logger.debug("Usando arquivo de backup direto")

            # Valida o backup antes de restaurar
            logger.debug("Validando arquivo de backup...")
            if not self.validate_backup_file(backup_db_path):
                error_msg = "Arquivo de backup inválido ou corrompido"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info("Arquivo de backup validado com sucesso")

            # Restaura o backup
            logger.debug("Iniciando restauração do banco...")
            source = sqlite3.connect(backup_db_path)
            dest = sqlite3.connect(self.db_path)

            with dest:
                source.backup(dest)

            source.close()
            dest.close()
            logger.info("Restauração concluída com sucesso")

            # Limpa arquivos temporários
            if backup_path.endswith('.zip'):
                shutil.rmtree(temp_dir)
                logger.debug("Arquivos temporários removidos")

            self.logger.info(f"Backup restaurado com sucesso de {backup_path}")
            logger.info(f"Backup restaurado com sucesso de {backup_path}")
            
            log_system_event("BACKUP_RESTAURADO", f"Backup restaurado: {backup_path}", "INFO")
            return True, "Backup restaurado com sucesso"

        except Exception as e:
            error_msg = f"Erro ao restaurar backup: {str(e)}"
            self.logger.error(error_msg)
            logger.error(error_msg)
            log_system_event("ERRO_RESTAURACAO", error_msg, "ERROR")

            if 'safety_backup' in locals():
                logger.info("Tentando restaurar backup de segurança...")
                self.restore_safety_backup(safety_backup[1])

            return False, error_msg

    def validate_backup_file(self, backup_path: str) -> bool:
        """Valida se o arquivo de backup é válido"""
        logger.debug(f"Validando arquivo de backup: {backup_path}")
        
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Arquivo de backup não encontrado: {backup_path}")
                return False
            
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Verifica se as tabelas principais existem
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            logger.debug(f"Tabelas no backup: {tables}")
            
            required_tables = ['cadastro', 'user', 'system_status']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.warning(f"Backup com tabelas ausentes: {missing_tables}")
            
            # Verifica integridade
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            conn.close()
            
            is_valid = integrity_result[0] == 'ok'
            if is_valid:
                logger.info("Arquivo de backup validado com sucesso")
            else:
                logger.error(f"Arquivo de backup inválido: {integrity_result[0]}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Erro ao validar arquivo de backup: {str(e)}")
            return False

    def create_safety_backup(self) -> Tuple[bool, str]:
        logger.info("Criando backup de segurança...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_dir = os.path.join(self.backup_dir, 'safety')
        Path(safety_dir).mkdir(exist_ok=True)

        backup_path = os.path.join(safety_dir, f'pre_restore_backup_{timestamp}.db')

        try:
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Backup de segurança criado: {backup_path}")
            logger.info(f"Backup de segurança criado: {backup_path}")
            return True, backup_path
        except Exception as e:
            error_msg = f"Erro ao criar backup de segurança: {str(e)}"
            self.logger.error(error_msg)
            logger.error(error_msg)
            return False, ""

    def restore_safety_backup(self, safety_backup_path: str) -> bool:
        """
        Restaura o backup de segurança em caso de falha

        Args:
            safety_backup_path: Caminho para o backup de segurança

        Returns:
            bool indicando sucesso da operação
        """
        logger.info(f"Restaurando backup de segurança: {safety_backup_path}")
        
        try:
            if os.path.exists(safety_backup_path):
                shutil.copy2(safety_backup_path, self.db_path)
                self.logger.info("Backup de segurança restaurado com sucesso")
                logger.info("Backup de segurança restaurado com sucesso")
                log_system_event("BACKUP_SEGURANCA_RESTAURADO", f"Backup de segurança restaurado: {safety_backup_path}", "WARNING")
                return True
            else:
                logger.error(f"Arquivo de backup de segurança não encontrado: {safety_backup_path}")
                return False
        except Exception as e:
            error_msg = f"Erro ao restaurar backup de segurança: {str(e)}"
            self.logger.error(error_msg)
            logger.error(error_msg)
            return False

    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict]:
        """
        Lista todos os backups disponíveis

        Args:
            backup_type: Tipo específico de backup para listar (opcional)

        Returns:
            Lista de dicionários com informações dos backups
        """
        logger.info(f"Listando backups - Tipo: {backup_type or 'todos'}")
        backups = []

        try:
            # Define quais diretórios pesquisar
            if backup_type:
                dirs_to_search = [os.path.join(self.backup_dir, backup_type)]
            else:
                dirs_to_search = [
                    os.path.join(self.backup_dir, d)
                    for d in ['daily', 'weekly', 'monthly', 'manual']
                ]

            # Busca backups em cada diretório
            for directory in dirs_to_search:
                if not os.path.exists(directory):
                    logger.debug(f"Diretório não existe: {directory}")
                    continue

                logger.debug(f"Procurando backups em: {directory}")
                for file in os.listdir(directory):
                    if not file.endswith('.zip'):
                        continue

                    file_path = os.path.join(directory, file)

                    try:
                        # Lê metadados do ZIP
                        with zipfile.ZipFile(file_path, 'r') as zf:
                            if 'metadata.json' in zf.namelist():
                                metadata = json.loads(zf.read('metadata.json'))
                            else:
                                metadata = {}

                        backups.append({
                            'filename': file,
                            'path': file_path,
                            'type': metadata.get('type', 'unknown'),
                            'created': metadata.get('backup_date', ''),
                            'size': os.path.getsize(file_path),
                            'metadata': metadata
                        })
                        
                        logger.debug(f"Backup encontrado: {file} - Tipo: {metadata.get('type', 'unknown')}")
                    except Exception as e:
                        logger.warning(f"Erro ao ler metadados de {file}: {str(e)}")

            sorted_backups = sorted(backups, key=lambda x: x['created'], reverse=True)
            logger.info(f"Total de backups encontrados: {len(sorted_backups)}")
            return sorted_backups

        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            return []

    def cleanup_old_backups(self, backup_type: str) -> None:
        """
        Remove backups antigos baseado em regras de retenção

        Args:
            backup_type: Tipo de backup para limpar
        """
        logger.info(f"Iniciando limpeza de backups antigos - Tipo: {backup_type}")
        
        try:
            retention_rules = {
                'daily': 7,  # Mantém 7 dias
                'weekly': 4,  # Mantém 4 semanas
                'monthly': 12,  # Mantém 12 meses
                'manual': 0  # Mantém todos os backups manuais
            }

            if backup_type not in retention_rules or retention_rules[backup_type] == 0:
                logger.debug(f"Nenhuma limpeza necessária para tipo: {backup_type}")
                return

            backups = self.list_backups(backup_type)
            max_keep = retention_rules[backup_type]

            logger.info(f"Regra de retenção: manter {max_keep} backups do tipo {backup_type}")
            logger.info(f"Backups encontrados: {len(backups)}")

            # Remove backups excedentes
            backups_to_remove = backups[max_keep:]
            for backup in backups_to_remove:
                try:
                    os.remove(backup['path'])
                    self.logger.info(f"Backup antigo removido: {backup['path']}")
                    logger.info(f"Backup antigo removido: {backup['path']}")
                except Exception as e:
                    logger.error(f"Erro ao remover backup antigo {backup['path']}: {str(e)}")

            logger.info(f"Limpeza concluída - {len(backups_to_remove)} backups removidos")

        except Exception as e:
            logger.error(f"Erro na limpeza de backups antigos: {str(e)}")

    def get_backup_stats(self) -> Dict:
        """Retorna estatísticas dos backups"""
        logger.info("Gerando estatísticas dos backups")
        
        try:
            stats = {
                'total_backups': 0,
                'total_size': 0,
                'by_type': {},
                'latest_backup': None,
                'oldest_backup': None
            }

            all_backups = self.list_backups()
            stats['total_backups'] = len(all_backups)

            for backup in all_backups:
                stats['total_size'] += backup['size']
                backup_type = backup['type']
                
                if backup_type not in stats['by_type']:
                    stats['by_type'][backup_type] = {
                        'count': 0,
                        'size': 0
                    }
                
                stats['by_type'][backup_type]['count'] += 1
                stats['by_type'][backup_type]['size'] += backup['size']

            if all_backups:
                stats['latest_backup'] = all_backups[0]['created']
                stats['oldest_backup'] = all_backups[-1]['created']

            logger.info(f"Estatísticas geradas - Total: {stats['total_backups']} backups, Tamanho: {stats['total_size']} bytes")
            return stats

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de backup: {str(e)}")
            return {}