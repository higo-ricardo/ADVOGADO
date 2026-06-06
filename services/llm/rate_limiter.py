"""
services/llm/rate_limiter.py — Rate limiting para chamadas à API LLM.
Implementa controle de requisições por minuto/hora para evitar throttling.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional


@dataclass
class RateLimitConfig:
    """Configuração de rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10  # Máximo de requisições em rápida sucessão
    
    # Tempo de espera entre requisições (segundos)
    min_delay_between_requests: float = 0.5


@dataclass
class RequestRecord:
    """Registro de uma requisição."""
    timestamp: float
    endpoint: str = "chat_completion"


class RateLimiter:
    """
    Controlador de rate limiting para APIs LLM.
    
    Usa sliding window para contagem de requisições por minuto/hora.
    Thread-safe para uso em ambientes concorrentes.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Inicializa o rate limiter.
        
        Args:
            config: Configuração de rate limiting (usa defaults se None)
        """
        self.config = config or RateLimitConfig()
        self._lock = Lock()
        
        # Filas de requisições (timestamps)
        self._requests_minute: deque[float] = deque()
        self._requests_hour: deque[float] = deque()
        
        # Contadores de burst
        self._burst_window: deque[float] = deque()
        self._last_request_time: float = 0.0
        
        # Estatísticas
        self._total_requests: int = 0
        self._throttled_requests: int = 0
        self._last_reset_minute: float = time.time()
        self._last_reset_hour: float = time.time()
    
    def _cleanup_old_records(self, current_time: float) -> None:
        """Remove registros antigos das filas."""
        minute_cutoff = current_time - 60.0
        hour_cutoff = current_time - 3600.0
        burst_cutoff = current_time - 1.0  # Burst window de 1 segundo
        
        # Limpa fila de minuto
        while self._requests_minute and self._requests_minute[0] < minute_cutoff:
            self._requests_minute.popleft()
        
        # Limpa fila de hora
        while self._requests_hour and self._requests_hour[0] < hour_cutoff:
            self._requests_hour.popleft()
        
        # Limpa fila de burst
        while self._burst_window and self._burst_window[0] < burst_cutoff:
            self._burst_window.popleft()
    
    def _check_burst_limit(self, current_time: float) -> bool:
        """Verifica se excedeu o limite de burst."""
        return len(self._burst_window) >= self.config.burst_limit
    
    def _check_minute_limit(self) -> bool:
        """Verifica se excedeu o limite por minuto."""
        return len(self._requests_minute) >= self.config.requests_per_minute
    
    def _check_hour_limit(self) -> bool:
        """Verifica se excedeu o limite por hora."""
        return len(self._requests_hour) >= self.config.requests_per_hour
    
    def acquire(self, endpoint: str = "chat_completion", timeout: float = 30.0) -> bool:
        """
        Solicita permissão para fazer uma requisição.
        
        Args:
            endpoint: Nome do endpoint da API
            timeout: Tempo máximo de espera em segundos
        
        Returns:
            True se conseguiu adquirir permissão, False se timeout
        """
        start_time = time.time()
        
        while True:
            with self._lock:
                current_time = time.time()
                self._cleanup_old_records(current_time)
                
                # Verifica limites
                if self._check_hour_limit():
                    wait_time = 3600.0 - (current_time - self._requests_hour[0])
                elif self._check_minute_limit():
                    wait_time = 60.0 - (current_time - self._requests_minute[0])
                elif self._check_burst_limit(current_time):
                    wait_time = 1.0 - (current_time - self._burst_window[0])
                else:
                    # Verifica delay mínimo entre requisições
                    elapsed_since_last = current_time - self._last_request_time
                    if elapsed_since_last < self.config.min_delay_between_requests:
                        wait_time = self.config.min_delay_between_requests - elapsed_since_last
                    else:
                        # Permite a requisição
                        self._requests_minute.append(current_time)
                        self._requests_hour.append(current_time)
                        self._burst_window.append(current_time)
                        self._last_request_time = current_time
                        self._total_requests += 1
                        return True
                
                # Calcula tempo restante
                wait_time = max(0.1, min(wait_time, timeout))
            
            # Verifica timeout
            elapsed = time.time() - start_time
            if elapsed + wait_time > timeout:
                with self._lock:
                    self._throttled_requests += 1
                return False
            
            # Aguarda antes de tentar novamente
            time.sleep(wait_time)
    
    def try_acquire(self, endpoint: str = "chat_completion") -> bool:
        """
        Tenta adquirir permissão sem bloquear.
        
        Args:
            endpoint: Nome do endpoint da API
        
        Returns:
            True se conseguiu adquirir permissão imediatamente, False caso contrário
        """
        with self._lock:
            current_time = time.time()
            self._cleanup_old_records(current_time)
            
            # Verifica todos os limites
            if self._check_hour_limit():
                return False
            if self._check_minute_limit():
                return False
            if self._check_burst_limit(current_time):
                return False
            
            # Verifica delay mínimo entre requisições
            elapsed_since_last = current_time - self._last_request_time
            if elapsed_since_last < self.config.min_delay_between_requests:
                return False
            
            # Permite a requisição
            self._requests_minute.append(current_time)
            self._requests_hour.append(current_time)
            self._burst_window.append(current_time)
            self._last_request_time = current_time
            self._total_requests += 1
            return True
    
    def get_wait_time(self) -> float:
        """
        Retorna o tempo estimado de espera até a próxima requisição.
        
        Returns:
            Tempo em segundos (0.0 se pode requisitar agora)
        """
        with self._lock:
            current_time = time.time()
            self._cleanup_old_records(current_time)
            
            if self._check_hour_limit():
                return 3600.0 - (current_time - self._requests_hour[0])
            if self._check_minute_limit():
                return 60.0 - (current_time - self._requests_minute[0])
            if self._check_burst_limit(current_time):
                return 1.0 - (current_time - self._burst_window[0])
            
            elapsed_since_last = current_time - self._last_request_time
            if elapsed_since_last < self.config.min_delay_between_requests:
                return self.config.min_delay_between_requests - elapsed_since_last
            
            return 0.0
    
    def get_stats(self) -> dict:
        """
        Retorna estatísticas de uso do rate limiter.
        
        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            current_time = time.time()
            self._cleanup_old_records(current_time)
            
            return {
                "total_requests": self._total_requests,
                "throttled_requests": self._throttled_requests,
                "requests_last_minute": len(self._requests_minute),
                "requests_last_hour": len(self._requests_hour),
                "limit_per_minute": self.config.requests_per_minute,
                "limit_per_hour": self.config.requests_per_hour,
                "current_wait_time": self.get_wait_time(),
            }
    
    def reset(self) -> None:
        """Reseta todos os contadores e filas."""
        with self._lock:
            self._requests_minute.clear()
            self._requests_hour.clear()
            self._burst_window.clear()
            self._last_request_time = 0.0
            self._total_requests = 0
            self._throttled_requests = 0


# Instância global padrão (pode ser sobrescrita via config)
_default_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """
    Obtém a instância global do rate limiter.
    
    Args:
        config: Configuração opcional (só usada na primeira chamada)
    
    Returns:
        Instância do RateLimiter
    """
    global _default_limiter
    
    if _default_limiter is None:
        _default_limiter = RateLimiter(config)
    
    return _default_limiter


def reset_rate_limiter() -> None:
    """Reseta o rate limiter global."""
    global _default_limiter
    _default_limiter = None
