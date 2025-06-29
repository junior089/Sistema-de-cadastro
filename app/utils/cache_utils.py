import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import threading
import logging

class CacheItem:
    """Item individual do cache"""
    
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl  # Time to live em segundos
    
    def is_expired(self) -> bool:
        """Verifica se o item expirou"""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def get_age(self) -> float:
        """Retorna a idade do item em segundos"""
        return (datetime.now() - self.created_at).total_seconds()

class Cache:
    """Sistema de cache simples em memória"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._cache: Dict[str, CacheItem] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._logger = logging.getLogger('Cache')
        
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém um valor do cache
        
        Args:
            key: Chave do item
            
        Returns:
            Valor do item ou None se não existir ou expirou
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            if item.is_expired():
                del self._cache[key]
                self._logger.debug(f"Item expirado removido: {key}")
                return None
            
            self._logger.debug(f"Cache hit: {key}")
            return item.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Define um valor no cache
        
        Args:
            key: Chave do item
            value: Valor a ser armazenado
            ttl: Time to live em segundos (opcional)
        """
        with self._lock:
            # Remove itens expirados primeiro
            self._cleanup_expired()
            
            # Verifica se o cache está cheio
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
            
            ttl = ttl or self._default_ttl
            self._cache[key] = CacheItem(value, ttl)
            self._logger.debug(f"Item adicionado ao cache: {key}")
    
    def delete(self, key: str) -> bool:
        """
        Remove um item do cache
        
        Args:
            key: Chave do item
            
        Returns:
            True se o item foi removido, False se não existia
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._logger.debug(f"Item removido do cache: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            self._logger.info("Cache limpo")
    
    def exists(self, key: str) -> bool:
        """
        Verifica se uma chave existe no cache (não expirada)
        
        Args:
            key: Chave a ser verificada
            
        Returns:
            True se a chave existe e não expirou
        """
        return self.get(key) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            self._cleanup_expired()
            
            total_items = len(self._cache)
            total_size = sum(len(str(item.value)) for item in self._cache.values())
            
            # Calcula idade média dos itens
            ages = [item.get_age() for item in self._cache.values()]
            avg_age = sum(ages) / len(ages) if ages else 0
            
            return {
                'total_items': total_items,
                'max_size': self._max_size,
                'usage_percent': (total_items / self._max_size) * 100,
                'total_size_bytes': total_size,
                'average_age_seconds': avg_age,
                'default_ttl': self._default_ttl
            }
    
    def _cleanup_expired(self) -> None:
        """Remove itens expirados do cache"""
        expired_keys = [
            key for key, item in self._cache.items()
            if item.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            self._logger.debug(f"Removidos {len(expired_keys)} itens expirados")
    
    def _evict_oldest(self) -> None:
        """Remove o item mais antigo do cache"""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        
        del self._cache[oldest_key]
        self._logger.debug(f"Item mais antigo removido: {oldest_key}")

# Instância global do cache
cache = Cache(max_size=500, default_ttl=300)

class CacheDecorator:
    """Decorator para cachear resultados de funções"""
    
    def __init__(self, ttl: int = 300, key_prefix: str = ""):
        self.ttl = ttl
        self.key_prefix = key_prefix
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Cria uma chave única baseada na função e argumentos
            cache_key = f"{self.key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Tenta obter do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executa a função e armazena no cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, self.ttl)
            
            return result
        
        return wrapper

# Decorators úteis
def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Decorator para cachear resultados de funções"""
    return CacheDecorator(ttl, key_prefix)

def cache_query(ttl: int = 300):
    """Decorator específico para cachear consultas ao banco"""
    return CacheDecorator(ttl, "query")

def cache_stats(ttl: int = 60):
    """Decorator para cachear estatísticas"""
    return CacheDecorator(ttl, "stats") 