from sys import argv
import re
import math
from collections import Counter

# Função para normalizar texto
def normalize(s):
    s = s.strip().upper()
    s = re.sub(r'[^A-Z]+', '', s)
    return s

# Função para o teste de Kasiski
def kasiski(s, min_num=3):
    matches = []
    found = {}

    for k in range(min_num, len(s) // 2):
        found[k] = {}
        shouldbreak = True
        
        for i in range(len(s) - k):
            v = s[i:i+k]
            if v not in found[k]:
                found[k][v] = 1
            else:
                found[k][v] += 1
                shouldbreak = False

        if shouldbreak:
            break

        for v in found[k]:
            if found[k][v] > 2:
                matches.append(v)

    # Calcula fatores e encontra o melhor comprimento de chave
    key_lengths = []
    for v in matches:
        k = len(v)
        p = [i for i in range(len(s)) if s[i:i+k] == v]
        factor = p[1] - p[0]
        for i in range(2, len(p)):
            factor = math.gcd(factor, p[i] - p[i - 1])
        key_lengths.append(factor)

    # Seleciona o comprimento de chave mais frequente
    if key_lengths:
        best_length = Counter(key_lengths).most_common(1)[0][0]
    else:
        best_length = None

    return best_length

# Função para gerar tabela de frequências
def ftable(s, skip=0, period=1):
    s = normalize(s)

    slen = 0
    count = [0 for _ in range(26)]
    for i in range(skip, len(s), period):
        slen += 1
        count[ord(s[i]) - 65] += 1

    out = f"Total chars: {slen}\n"
    for c, n in enumerate(count):
        c = chr(c + 65)
        percent = 100.0 * n / slen
        out += f"{c}: {n:10d} ({percent:6.2f}%) {'*' * math.ceil(percent)}\n"

    ic = (1.00 / (slen * (slen - 1))) * sum(f * (f - 1) for f in count)
    out += f"\nIndex of Coincidence: {ic:.4f}\n"

    return out

# Função para análise de frequência
def analyze_frequency(s):
    s = normalize(s)
    count = Counter(s)
    total = sum(count.values())
    freq = {chr(i + 65): 0 for i in range(26)}
    for letter, num in count.items():
        freq[letter] = num / total * 100
    return freq

# Função para calcular o deslocamento da letra
def calculate_shift(segment_freq, expected_freq):
    max_letter = max(segment_freq, key=segment_freq.get)
    max_expected = max(expected_freq, key=expected_freq.get)
    shift = (ord(max_letter) - ord(max_expected)) % 26
    return shift

# Função para decifrar a cifra de Vigenère
def decipher_vigenere(ciphertext, key):
    decrypted = []
    key_length = len(key)
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            shift = ord(key[i % key_length]) - ord('A')
            decrypted_char = chr((ord(char) - shift - 65) % 26 + 65)
            decrypted.append(decrypted_char)
        else:
            decrypted.append(char)  # Manter não alfabéticos inalterados
    return ''.join(decrypted)

# Função para tentar decifrar com chave derivada
def derive_key(ciphertext, key_length, expected_freq):
    segments = ['' for _ in range(key_length)]
    
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            segments[i % key_length] += char

    key = []
    for segment in segments:
        segment_freq = analyze_frequency(segment)
        shift = calculate_shift(segment_freq, expected_freq)
        key.append(chr(shift + 65))  # Convert shift to letter
    
    return ''.join(key)

# Função principal
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
                infile = argv[i]
            elif k == 1:
                outfile = argv[i]
            k += 1
        i += 1

    s = None
    if infile is None:
        s = input("Enter the text: ")
    else:
        with open(infile, 'r') as f:
            s = f.read()

    if analysis_type == 'kasiski':
        key_length = kasiski(normalize(s), min_num)
        if key_length is not None:
            print(f"Best key length: {key_length}")
            key = derive_key(s, key_length, expected_freq)
            print(f"Derived Key: {key}")
            decrypted_text = decipher_vigenere(s, key)
            print("Decrypted Text:", decrypted_text)
        else:
            print("No key length found.")
    else:
        out = ftable(s, skip, period)

    if outfile is None:
        print(out)
    else:
        with open(outfile, 'w') as f:
            f.write(out)

if __name__ == "__main__":
    main()
