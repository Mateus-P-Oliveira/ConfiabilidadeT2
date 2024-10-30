from sys import argv
import re
import math
from collections import Counter

# Função para o teste de Kasiski que determina o comprimento da chave
def kasiski(s, min_num=3):
    matches = []  # Lista para substrings repetidas
    found = {}    # Dicionário para contar ocorrências

    for k in range(min_num, len(s) // 2):
        found[k] = {}
        shouldbreak = True
        
        # Conta ocorrências de substrings de comprimento k
        for i in range(len(s) - k):
            v = s[i:i+k]
            if v not in found[k]:
                found[k][v] = 1
            else:
                found[k][v] += 1
                shouldbreak = False

        if shouldbreak:
            break  # Sai se não encontrar mais repetições

        # Adiciona substrings que aparecem mais de duas vezes
        for v in found[k]:
            if found[k][v] > 2:
                matches.append(v)

    key_lengths = []
    for v in matches:
        k = len(v)
        p = [i for i in range(len(s)) if s[i:i+k] == v]
        factor = p[1] - p[0]
        for i in range(2, len(p)):
            factor = math.gcd(factor, p[i] - p[i - 1])
        key_lengths.append(factor)

    if key_lengths:
        best_length = Counter(key_lengths).most_common(1)[0][0]
    else:
        best_length = None

    return best_length

# Função para gerar tabela de frequências dos caracteres alfabéticos
def ftable(s, skip=0, period=1):
    slen = 0
    count = [0 for _ in range(26)]  # Contador para cada letra do alfabeto
    for i in range(skip, len(s), period):
        if s[i].isalpha():  # Verifica se é uma letra
            slen += 1
            count[ord(s[i].upper()) - 65] += 1  # Incrementa o contador para a letra correspondente

    out = f"Total chars: {slen}\n"
    for c, n in enumerate(count):
        c = chr(c + 65)
        percent = 100.0 * n / slen if slen > 0 else 0
        out += f"{c}: {n:10d} ({percent:6.2f}%) {'*' * math.ceil(percent)}\n"

    ic = (1.00 / (slen * (slen - 1))) * sum(f * (f - 1) for f in count) if slen > 1 else 0
    out += f"\nIndex of Coincidence: {ic:.4f}\n"

    return out

# Função para analisar a frequência de letras em uma string
def analyze_frequency(s):
    count = Counter(s)
    total = sum(count.values())
    freq = {chr(i + 65): 0 for i in range(26)}  # Inicializa frequências para cada letra
    for letter, num in count.items():
        if letter.isalpha():  # Verifica se é uma letra
            freq[letter.upper()] = num / total * 100  # Calcula a frequência percentual
    return freq

# Função para calcular o deslocamento necessário para alinhar frequências
def calculate_shift(segment_freq, expected_freq):
    max_letter = max(segment_freq, key=segment_freq.get)  # Letra mais frequente do segmento
    max_expected = max(expected_freq, key=expected_freq.get)  # Letra mais frequente esperada
    shift = (ord(max_letter) - ord(max_expected)) % 26  # Calcula o deslocamento
    return shift

# Função para decifrar um texto cifrado usando a cifra de Vigenère
def decipher_vigenere(ciphertext, key):
    decrypted = []
    key_length = len(key)
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            shift = ord(key[i % key_length]) - ord('A')  # Calcula o deslocamento usando a chave
            decrypted_char = chr((ord(char.upper()) - shift - 65) % 26 + 65)
            decrypted.append(decrypted_char)
        else:
            decrypted.append(char)  # Mantém não alfabéticos inalterados
    return ''.join(decrypted)

# Função para derivar a chave a partir do texto cifrado
def derive_key(ciphertext, key_length, expected_freq):
    segments = ['' for _ in range(key_length)]  # Cria listas para segmentos

    for i, char in enumerate(ciphertext):
        if char.isalpha():
            segments[i % key_length] += char.upper()  # Adiciona letras a segmentos correspondentes

    key = []
    for segment in segments:
        segment_freq = analyze_frequency(segment)  # Analisa a frequência do segmento
        shift = calculate_shift(segment_freq, expected_freq)  # Calcula o deslocamento
        key.append(chr(shift + 65))  # Converte o deslocamento em letra
    
    return ''.join(key)  # Retorna a chave como uma string

# Função principal que controla o fluxo do programa
def main():
    i, k = 1, 0
    min_num = 3
    skip = 0
    period = 1
    infile = None
    outfile = None
    analysis_type = None
    expected_freq = {
        'A': 14.7154, 'B': 0.9926, 'C': 3.8775, 'D': 4.7958,
        'E': 12.7879, 'F': 0.9868, 'G': 1.1435, 'H': 1.4840,
        'I': 6.1426, 'J': 0.2787, 'K': 0.0044, 'L': 3.3069,
        'M': 4.8531, 'N': 4.7498, 'O': 10.5498, 'P': 2.6743,
        'Q': 1.2897, 'R': 6.3127, 'S': 7.5612, 'T': 4.2199,
        'U': 4.7630, 'V': 1.6736, 'W': 0.0011, 'X': 0.2845,
        'Y': 0.0686, 'Z': 0.4824
    }

    out = ""  # Inicializa 'out' para evitar UnboundLocalError

    while i < len(argv):
        # Processa argumentos da linha de comando
        if argv[i] == '-m':
            i += 1
            min_num = int(argv[i])
        elif argv[i] == '-s':
            i += 1
            skip = int(argv[i])
        elif argv[i] == '-p':
            i += 1
            period = int(argv[i])
        elif argv[i] == '-k':
            analysis_type = 'kasiski'
        elif argv[i] == '-f':
            analysis_type = 'ftable'
        elif argv[i][0] != '-':
            if k == 0:
                infile = argv[i]  # Nome do arquivo de entrada
            elif k == 1:
                outfile = argv[i]  # Nome do arquivo de saída
            k += 1
        i += 1

    s = None
    # Lê o texto cifrado de um arquivo ou da entrada padrão
    if infile is None:
        s = input("Enter the text: ")
    else:
        with open(infile, 'r') as f:
            s = f.read()

    # Realiza análise de Kasiski se especificado
    if analysis_type == 'kasiski':
        key_length = kasiski(s, min_num)
        if key_length is not None:
            print(f"Best key length: {key_length}")
            key = derive_key(s, key_length, expected_freq)
            print(f"Derived Key: {key}")
            decrypted_text = decipher_vigenere(s, key)
            print("Decrypted Text:", decrypted_text)

            # Salva o texto decifrado e a chave em um arquivo
            output_filename = input("Enter the output filename (with .txt): ")
            with open(output_filename, 'w') as output_file:
                output_file.write(decrypted_text)
                output_file.write(f"\nKey: {key}\n")
                output_file.write(f"Key Length: {key_length}\n")
            print(f"Decrypted text, key, and key length saved to {output_filename}")

        else:
            print("No key length found.")
    else:
        out = ftable(s, skip, period)  # Gera a tabela de frequências

    if outfile is None:
        print(out)  # Exibe resultado na tela
    else:
        with open(outfile, 'w') as f:
            f.write(out)  # Salva resultado em arquivo

if __name__ == "__main__":
    main()
