import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class Validator:
    """Sistema de validação centralizado para o sistema"""
    
    @staticmethod
    def validate_cpf(cpf: str) -> Tuple[bool, str]:
        """
        Valida um CPF brasileiro
        
        Args:
            cpf: CPF a ser validado (apenas números)
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem_erro)
        """
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^\d]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False, "CPF deve ter 11 dígitos"
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False, "CPF inválido (dígitos repetidos)"
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf[9]) != digito1:
            return False, "CPF inválido"
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        if int(cpf[10]) != digito2:
            return False, "CPF inválido"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Valida um número de telefone brasileiro (padrão: (12)912345678)
        
        Args:
            phone: Telefone a ser validado
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem_erro)
        """
        # Remove caracteres não numéricos
        phone = re.sub(r'[^\d]', '', phone)
        
        # Verifica se tem 11 dígitos (DDD + 9 dígitos)
        if len(phone) != 11:
            return False, "Telefone deve ter 11 dígitos (DDD + 9 dígitos)"
        
        # Verifica se começa com DDD válido (11-99)
        ddd = int(phone[:2])
        if ddd < 11 or ddd > 99:
            return False, "DDD inválido"
        
        # Verifica se o 9º dígito é 9 (padrão brasileiro)
        if phone[2] != '9':
            return False, "Telefone deve começar com 9 após o DDD"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Valida um nome de pessoa
        
        Args:
            name: Nome a ser validado
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem_erro)
        """
        if not name or not name.strip():
            return False, "Nome é obrigatório"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Nome deve ter pelo menos 2 caracteres"
        
        if len(name) > 100:
            return False, "Nome deve ter no máximo 100 caracteres"
        
        # Verifica se contém apenas letras, espaços e caracteres especiais comuns
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', name):
            return False, "Nome contém caracteres inválidos"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Valida um nome de usuário
        
        Args:
            username: Nome de usuário a ser validado
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem_erro)
        """
        if not username or not username.strip():
            return False, "Nome de usuário é obrigatório"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Nome de usuário deve ter pelo menos 3 caracteres"
        
        if len(username) > 50:
            return False, "Nome de usuário deve ter no máximo 50 caracteres"
        
        # Verifica se contém apenas letras, números e underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Nome de usuário deve conter apenas letras, números e underscore"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Valida uma senha
        
        Args:
            password: Senha a ser validada
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem_erro)
        """
        if not password:
            return False, "Senha é obrigatória"
        
        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"
        
        if len(password) > 128:
            return False, "Senha deve ter no máximo 128 caracteres"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valida um endereço de email
        
        Args:
            email: Email a ser validado
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem_erro)
        """
        if not email:
            return False, "Email é obrigatório"
        
        # Padrão básico de validação de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Email inválido"
        
        return True, ""
    
    @staticmethod
    def format_cpf(cpf: str) -> str:
        """
        Formata um CPF para exibição (XXX.XXX.XXX-XX)
        
        Args:
            cpf: CPF sem formatação
            
        Returns:
            str: CPF formatado
        """
        cpf = re.sub(r'[^\d]', '', cpf)
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Formata um telefone para exibição ((XX)9XXXX-XXXX)
        
        Args:
            phone: Telefone sem formatação
            
        Returns:
            str: Telefone formatado
        """
        phone = re.sub(r'[^\d]', '', phone)
        if len(phone) == 11:
            return f"({phone[:2]}){phone[2:7]}-{phone[7:]}"
        return phone
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitiza entrada de texto removendo caracteres perigosos
        
        Args:
            text: Texto a ser sanitizado
            
        Returns:
            str: Texto sanitizado
        """
        if not text:
            return ""
        
        # Remove caracteres de controle exceto quebras de linha
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Remove tags HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove scripts
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()

# Instância global do validador
validator = Validator() 