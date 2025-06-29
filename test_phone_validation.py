#!/usr/bin/env python3
"""
Script para testar a validação de telefone
"""

import re

def normalizePhone(phone):
    """Remove formatação e zeros à esquerda do DDD"""
    normalized = re.sub(r'\D', '', phone)
    
    # Remove zeros à esquerda do DDD
    if len(normalized) > 2 and normalized.startswith('0'):
        normalized = normalized[1:]
    
    return normalized

def validatePhone(phone):
    """Valida telefone brasileiro"""
    phone = re.sub(r'\D', '', phone)

    # Remove zeros à esquerda do DDD
    if len(phone) > 2 and phone.startswith('0'):
        phone = phone[1:]

    # Aceita números de 10 ou 11 dígitos
    if len(phone) < 10 or len(phone) > 11:
        return False

    # DDD deve estar entre 11 e 99
    ddd = int(phone[:2])
    if ddd < 11 or ddd > 99:
        return False

    # Lista de DDDs válidos no Brasil (atualizada)
    validDDDs = [
        11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62, 63, 64, 65, 66, 67, 68, 69,
        71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99
    ]
    
    if ddd not in validDDDs:
        return False

    # Para números de 11 dígitos, verifica se o terceiro dígito é 8 ou 9
    if len(phone) == 11:
        terceiroDigito = int(phone[2])
        if terceiroDigito != 8 and terceiroDigito != 9:
            return False

    # Para números de 10 dígitos, verifica se o terceiro dígito é 2, 3, 4, 5, 6, 7
    if len(phone) == 10:
        terceiroDigito = int(phone[2])
        if terceiroDigito < 2 or terceiroDigito > 7:
            return False

    return True

def formatPhone(phone):
    """Formata telefone brasileiro"""
    value = re.sub(r'\D', '', phone)

    # Remove zeros à esquerda do DDD
    if len(value) > 2 and value.startswith('0'):
        value = value[1:]

    if len(value) > 11:
        value = value[:11]

    # Formata baseado no número de dígitos
    if len(value) == 11:
        # Celular: (61) 99244-5034
        value = re.sub(r'^(\d{2})(\d{5})(\d{4}).*', r'(\1) \2-\3', value)
    elif len(value) == 10:
        # Fixo: (61) 3244-5034
        value = re.sub(r'^(\d{2})(\d{4})(\d{4}).*', r'(\1) \2-\3', value)
    elif len(value) > 2:
        # Formato parcial
        value = re.sub(r'^(\d{2})(\d{0,5}).*', r'(\1) \2', value)

    return value

def test_phone_validation():
    """Testa diferentes formatos de telefone"""
    
    test_cases = [
        # Casos válidos
        ("61992445034", True, "(61) 99244-5034"),  # Celular com 0 no início
        ("61992445034", True, "(61) 99244-5034"),  # Celular normal
        ("6132445034", True, "(61) 3244-5034"),    # Fixo
        ("11987654321", True, "(11) 98765-4321"),  # Celular SP
        ("1132445678", True, "(11) 3244-5678"),    # Fixo SP
        ("21987654321", True, "(21) 98765-4321"),  # Celular RJ
        ("3132445678", True, "(31) 3244-5678"),    # Fixo MG
        
        # Casos inválidos
        ("1234567890", False, ""),                 # DDD inválido (12)
        ("12345678901", False, ""),                # DDD inválido (12)
        ("123456789", False, ""),                  # Muito curto
        ("123456789012", False, ""),               # Muito longo
        ("2032445678", False, ""),                 # DDD 20 não existe
        ("2332445678", False, ""),                 # DDD 23 não existe
        ("2532445678", False, ""),                 # DDD 25 não existe
        ("2632445678", False, ""),                 # DDD 26 não existe
        ("2932445678", False, ""),                 # DDD 29 não existe
        ("3032445678", False, ""),                 # DDD 30 não existe
        ("3632445678", False, ""),                 # DDD 36 não existe
        ("3932445678", False, ""),                 # DDD 39 não existe
        ("4032445678", False, ""),                 # DDD 40 não existe
        ("5032445678", False, ""),                 # DDD 50 não existe
        ("5232445678", False, ""),                 # DDD 52 não existe
        ("5632445678", False, ""),                 # DDD 56 não existe
        ("5732445678", False, ""),                 # DDD 57 não existe
        ("5832445678", False, ""),                 # DDD 58 não existe
        ("5932445678", False, ""),                 # DDD 59 não existe
        ("6032445678", False, ""),                 # DDD 60 não existe
        ("7032445678", False, ""),                 # DDD 70 não existe
        ("7232445678", False, ""),                 # DDD 72 não existe
        ("7632445678", False, ""),                 # DDD 76 não existe
        ("7832445678", False, ""),                 # DDD 78 não existe
        ("8032445678", False, ""),                 # DDD 80 não existe
        ("9032445678", False, ""),                 # DDD 90 não existe
    ]
    
    print("🧪 TESTANDO VALIDAÇÃO DE TELEFONE")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for phone, expected_valid, expected_format in test_cases:
        is_valid = validatePhone(phone)
        formatted = formatPhone(phone) if is_valid else ""
        
        status = "✅ PASSOU" if is_valid == expected_valid else "❌ FALHOU"
        
        print(f"📞 {phone}")
        print(f"   Esperado: {'Válido' if expected_valid else 'Inválido'}")
        print(f"   Obtido: {'Válido' if is_valid else 'Inválido'}")
        print(f"   Formatado: {formatted}")
        print(f"   Status: {status}")
        print()
        
        if is_valid == expected_valid:
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"📊 RESULTADO: {passed} passaram, {failed} falharam")
    
    if failed == 0:
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️  Alguns testes falharam. Verifique a implementação.")

if __name__ == "__main__":
    test_phone_validation() 