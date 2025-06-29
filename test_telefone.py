#!/usr/bin/env python3
"""
Teste para verificar a normalização do telefone
"""

def test_telefone_normalization():
    """Testa a normalização do telefone"""
    
    print("🧪 TESTE DE NORMALIZAÇÃO DE TELEFONE")
    print("=" * 50)
    
    # Simula o que o backend faz
    def normalize_telefone(telefone):
        return telefone.strip().replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
    
    # Testes
    test_cases = [
        "(61) 99244-5034",
        "61992445034", 
        "(61)992445034",
        "61 99244 5034",
        "61-99244-5034"
    ]
    
    for telefone in test_cases:
        normalized = normalize_telefone(telefone)
        is_valid = len(normalized) == 11 and normalized.isdigit()
        print(f"📞 '{telefone}' -> '{normalized}' -> {'✅ Válido' if is_valid else '❌ Inválido'}")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_telefone_normalization() 