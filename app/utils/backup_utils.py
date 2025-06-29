import os
import shutil
import sqlite3
import zipfile
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
class DatabaseBackup:
    def __init__(self, app_config: Dict, backup_dir: str = 'backups'):
        self.backup_dir = os.path.abspath(backup_dir)
        self.db_path = app_config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        self.setup_logging()
        self.setup_backup_directory()

    def setup_logging(self) -> None:
        log_dir = 'logs'
        Path(log_dir).mkdir(exist_ok=True)

        logging.basicConfig(
            filename=os.path.join(log_dir, 'backup.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DatabaseBackup')

    def setup_backup_directory(self) -> None:
        Path(self.backup_dir).mkdir(exist_ok=True)

        # Cria subdiretórios para diferentes tipos de backup
        for subdir in ['daily', 'weekly', 'monthly', 'manual']:
            Path(os.path.join(self.backup_dir, subdir)).mkdir(exist_ok=True)

    def create_backup(self, backup_type: str = 'manual') -> Tuple[bool, str]:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_subdir = os.path.join(self.backup_dir, backup_type)
            backup_base = f'cadastro_backup_{timestamp}'
            backup_db = os.path.join(backup_subdir, f'{backup_base}.db')
            backup_zip = os.path.join(backup_subdir, f'{backup_base}.zip')

            # Verifica se o banco existe
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Banco de dados não encontrado em {self.db_path}")

            # Cria o backup do banco
            source = sqlite3.connect(self.db_path)
            dest = sqlite3.connect(backup_db)

            with dest:
                source.backup(dest)

            source.close()
            dest.close()

            # Cria arquivo ZIP com o backup e metadados
            with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Adiciona o arquivo do banco
                zf.write(backup_db, os.path.basename(backup_db))

                # Adiciona metadados
                metadata = {
                    'timestamp': timestamp,
                    'type': backup_type,
                    'db_size': os.path.getsize(backup_db),
                    'backup_date': datetime.now().isoformat()
                }

                zf.writestr('metadata.json', json.dumps(metadata, indent=2))

            # Remove o arquivo .db após criar o ZIP
            os.remove(backup_db)

            self.logger.info(f"Backup criado com sucesso: {backup_zip}")
            self.cleanup_old_backups(backup_type)

            return True, f"Backup criado com sucesso em {backup_zip}"

        except Exception as e:
            error_msg = f"Erro ao criar backup: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        try:
            backup_path = os.path.normpath(backup_path)
            self.logger.info(f"Original backup path: {backup_path}")
            backup_path = os.path.normpath(backup_path)
            self.logger.info(f"Normalized backup path: {backup_path}")

            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_path}")

            safety_backup = self.create_safety_backup()
            if not safety_backup[0]:
                raise Exception("Falha ao criar backup de segurança")

            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    db_file = next(f for f in zf.namelist() if f.endswith('.db'))
                    temp_dir = os.path.join(self.backup_dir, 'temp')
                    Path(temp_dir).mkdir(exist_ok=True)
                    zf.extract(db_file, temp_dir)
                    backup_db_path = os.path.join(temp_dir, db_file)
            else:
                backup_db_path = backup_path

            source = sqlite3.connect(backup_db_path)
            dest = sqlite3.connect(self.db_path)

            with dest:
                source.backup(dest)

            source.close()
            dest.close()

            if backup_path.endswith('.zip'):
                shutil.rmtree(temp_dir)

            self.logger.info(f"Backup restaurado com sucesso de {backup_path}")
            return True, "Backup restaurado com sucesso"

        except Exception as e:
            error_msg = f"Erro ao restaurar backup: {str(e)}"
            self.logger.error(error_msg)

            if 'safety_backup' in locals():
                self.restore_safety_backup(safety_backup[1])

            return False, error_msg

    def create_safety_backup(self) -> Tuple[bool, str]:

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_dir = os.path.join(self.backup_dir, 'safety')
        Path(safety_dir).mkdir(exist_ok=True)

        backup_path = os.path.join(safety_dir, f'pre_restore_backup_{timestamp}.db')

        try:
            shutil.copy2(self.db_path, backup_path)
            return True, backup_path
        except Exception as e:
            self.logger.error(f"Erro ao criar backup de segurança: {str(e)}")
            return False, ""

    def restore_safety_backup(self, safety_backup_path: str) -> bool:
        """
        Restaura o backup de segurança em caso de falha

        Args:
            safety_backup_path: Caminho para o backup de segurança

        Returns:
            bool indicando sucesso da operação
        """
        try:
            if os.path.exists(safety_backup_path):
                shutil.copy2(safety_backup_path, self.db_path)
                self.logger.info("Backup de segurança restaurado com sucesso")
                return True
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup de segurança: {str(e)}")
        return False

    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict]:
        """
        Lista todos os backups disponíveis

        Args:
            backup_type: Tipo específico de backup para listar (opcional)

        Returns:
            Lista de dicionários com informações dos backups
        """
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
                    continue

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
                    except Exception as e:
                        self.logger.warning(f"Erro ao ler metadados de {file}: {str(e)}")

            return sorted(backups, key=lambda x: x['created'], reverse=True)

        except Exception as e:
            self.logger.error(f"Erro ao listar backups: {str(e)}")
            return []

    def cleanup_old_backups(self, backup_type: str) -> None:
        """
        Remove backups antigos baseado em regras de retenção

        Args:
            backup_type: Tipo de backup para limpar
        """
        try:
            retention_rules = {
                'daily': 7,  # Mantém 7 dias
                'weekly': 4,  # Mantém 4 semanas
                'monthly': 12,  # Mantém 12 meses
                'manual': 0  # Mantém todos os backups manuais
            }

            if backup_type not in retention_rules or retention_rules[backup_type] == 0:
                return

            backups = self.list_backups(backup_type)
            max_keep = retention_rules[backup_type]

            # Remove backups excedentes
            for backup in backups[max_keep:]:
                try:
                    os.remove(backup['path'])
                    self.logger.info(f"Backup antigo removido: {backup['path']}")
                except Exception as e:
                    self.logger.error(f"Erro ao remover backup antigo {backup['path']}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Erro na limpeza de backups antigos: {str(e)}")