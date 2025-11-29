import re

def test_regex():
    replacements = {
        "@nomeCliente": "Fulano da Silva",
        "@arqlamp": "ARQUITETO TESTE",
        "@CpfCnpj": "123.456.789-00"
    }
    
    test_cases = [
        ("Nome: @nomeCliente.", "Nome: Fulano da Silva."),
        ("Email: contato@arqlamp.com", "Email: contato@arqlamp.com"),
        ("Chave: @arqlamp", "Chave: ARQUITETO TESTE"),
        ("CPF: @CpfCnpj", "CPF: 123.456.789-00"),
        ("Email2: teste@nomeCliente.com", "Email2: teste@nomeCliente.com")
    ]
    
    print("--- Testing Regex Logic ---")
    sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
    
    for original, expected in test_cases:
        text = original
        for key in sorted_keys:
            if key in text:
                # The regex used in DOCXHandler
                pattern = r'(?<![\w.])' + re.escape(key) + r'(?!\.[a-z]{2,}\b)'
                new_val = str(replacements[key])
                text = re.sub(pattern, new_val, text)
        
        status = "PASS" if text == expected else "FAIL"
        print(f"[{status}] '{original}' -> '{text}'")
        if status == "FAIL":
            print(f"   Expected: '{expected}'")

if __name__ == "__main__":
    test_regex()
