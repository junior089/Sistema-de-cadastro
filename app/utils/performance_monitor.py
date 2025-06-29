import time
import threading
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import logging
import json

class PerformanceMonitor:
    """Sistema de monitoramento de performance"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self._lock = threading.RLock()
        self._logger = logging.getLogger('PerformanceMonitor')
        
        # Histórico de métricas
        self._cpu_history = deque(maxlen=history_size)
        self._memory_history = deque(maxlen=history_size)
        self._disk_history = deque(maxlen=history_size)
        self._request_history = deque(maxlen=history_size)
        
        # Contadores
        self._request_count = 0
        self._error_count = 0
        self._start_time = datetime.now()
        
        # Configurações
        self._monitoring_enabled = True
        self._collection_interval = 30  # segundos
        
        # Thread de coleta
        self._collection_thread = None
        self._stop_collection = threading.Event()
    
    def start_monitoring(self):
        """Inicia o monitoramento em background"""
        if self._collection_thread and self._collection_thread.is_alive():
            return
        
        self._stop_collection.clear()
        self._collection_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        self._collection_thread.start()
        self._logger.info("Monitoramento de performance iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self._stop_collection.set()
        if self._collection_thread:
            self._collection_thread.join(timeout=5)
        self._logger.info("Monitoramento de performance parado")
    
    def _collect_metrics(self):
        """Coleta métricas do sistema em loop"""
        while not self._stop_collection.wait(self._collection_interval):
            try:
                self._collect_system_metrics()
            except Exception as e:
                self._logger.error(f"Erro ao coletar métricas: {e}")
    
    def _collect_system_metrics(self):
        """Coleta métricas do sistema"""
        timestamp = datetime.now()
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self._cpu_history.append({
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'cpu_count': psutil.cpu_count()
        })
        
        # Memória
        memory = psutil.virtual_memory()
        self._memory_history.append({
            'timestamp': timestamp,
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        })
        
        # Disco
        disk = psutil.disk_usage('/')
        self._disk_history.append({
            'timestamp': timestamp,
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': (disk.used / disk.total) * 100
        })
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      response_time: float, user_id: Optional[int] = None):
        """Registra uma requisição HTTP"""
        with self._lock:
            self._request_count += 1
            
            if status_code >= 400:
                self._error_count += 1
            
            self._request_history.append({
                'timestamp': datetime.now(),
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'response_time': response_time,
                'user_id': user_id
            })
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Processo atual
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'process_rss': process_memory.rss,
                    'process_vms': process_memory.vms
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'requests': {
                    'total': self._request_count,
                    'errors': self._error_count,
                    'error_rate': (self._error_count / self._request_count * 100) if self._request_count > 0 else 0
                },
                'uptime': (datetime.now() - self._start_time).total_seconds()
            }
        except Exception as e:
            self._logger.error(f"Erro ao obter métricas atuais: {e}")
            return {}
    
    def get_historical_metrics(self, hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna métricas históricas"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cpu_data = [
                {
                    'timestamp': item['timestamp'].isoformat(),
                    'cpu_percent': item['cpu_percent']
                }
                for item in self._cpu_history
                if item['timestamp'] > cutoff_time
            ]
            
            memory_data = [
                {
                    'timestamp': item['timestamp'].isoformat(),
                    'memory_percent': item['percent'],
                    'used_gb': item['used'] / (1024**3)
                }
                for item in self._memory_history
                if item['timestamp'] > cutoff_time
            ]
            
            disk_data = [
                {
                    'timestamp': item['timestamp'].isoformat(),
                    'disk_percent': item['percent'],
                    'used_gb': item['used'] / (1024**3)
                }
                for item in self._disk_history
                if item['timestamp'] > cutoff_time
            ]
            
            return {
                'cpu': cpu_data,
                'memory': memory_data,
                'disk': disk_data
            }
    
    def get_request_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna estatísticas de requisições"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_requests = [
                req for req in self._request_history
                if req['timestamp'] > cutoff_time
            ]
            
            if not recent_requests:
                return {
                    'total_requests': 0,
                    'error_count': 0,
                    'avg_response_time': 0,
                    'endpoints': {},
                    'status_codes': {}
                }
            
            # Estatísticas gerais
            total_requests = len(recent_requests)
            error_count = len([r for r in recent_requests if r['status_code'] >= 400])
            avg_response_time = sum(r['response_time'] for r in recent_requests) / total_requests
            
            # Endpoints mais acessados
            endpoints = {}
            for req in recent_requests:
                endpoint = req['endpoint']
                endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
            
            # Códigos de status
            status_codes = {}
            for req in recent_requests:
                status = req['status_code']
                status_codes[status] = status_codes.get(status, 0) + 1
            
            return {
                'total_requests': total_requests,
                'error_count': error_count,
                'error_rate': (error_count / total_requests * 100) if total_requests > 0 else 0,
                'avg_response_time': avg_response_time,
                'endpoints': dict(sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:10]),
                'status_codes': status_codes
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Retorna status de saúde do sistema"""
        current = self.get_current_metrics()
        
        if not current:
            return {'status': 'unknown', 'issues': ['Não foi possível obter métricas']}
        
        issues = []
        warnings = []
        
        # Verifica CPU
        if current['cpu']['percent'] > 90:
            issues.append('CPU muito alta (>90%)')
        elif current['cpu']['percent'] > 70:
            warnings.append('CPU alta (>70%)')
        
        # Verifica memória
        if current['memory']['percent'] > 90:
            issues.append('Memória muito alta (>90%)')
        elif current['memory']['percent'] > 80:
            warnings.append('Memória alta (>80%)')
        
        # Verifica disco
        if current['disk']['percent'] > 90:
            issues.append('Disco muito cheio (>90%)')
        elif current['disk']['percent'] > 80:
            warnings.append('Disco cheio (>80%)')
        
        # Verifica taxa de erro
        if current['requests']['error_rate'] > 10:
            issues.append('Taxa de erro alta (>10%)')
        elif current['requests']['error_rate'] > 5:
            warnings.append('Taxa de erro elevada (>5%)')
        
        # Determina status
        if issues:
            status = 'critical'
        elif warnings:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'issues': issues,
            'warnings': warnings,
            'timestamp': current['timestamp']
        }
    
    def export_metrics(self, filepath: str):
        """Exporta métricas para arquivo JSON"""
        try:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'current_metrics': self.get_current_metrics(),
                'historical_metrics': self.get_historical_metrics(),
                'request_stats': self.get_request_stats(),
                'system_health': self.get_system_health()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self._logger.info(f"Métricas exportadas para {filepath}")
            
        except Exception as e:
            self._logger.error(f"Erro ao exportar métricas: {e}")

# Instância global do monitor
performance_monitor = PerformanceMonitor()

# Decorator para monitorar performance de funções
def monitor_performance(func):
    """Decorator para monitorar performance de funções"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # Registra erro
            performance_monitor.record_request(
                endpoint=f"{func.__module__}.{func.__name__}",
                method="FUNCTION",
                status_code=500,
                response_time=time.time() - start_time
            )
            raise
        finally:
            # Registra sucesso
            performance_monitor.record_request(
                endpoint=f"{func.__module__}.{func.__name__}",
                method="FUNCTION",
                status_code=200,
                response_time=time.time() - start_time
            )
    
    return wrapper 