from sys import argv
import math

def kasiski(s, min_num=3):
    out = ''
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

    out += "Length  Count  Word        Factor  Location (distance)\n"
    out += "======  =====  ==========  ======  ===================\n"
    
    for v in matches:
        k = len(v)
        p = [i for i in range(len(s)) if s[i:i+k] == v]

        factor = p[1] - p[0]
        for i in range(2, len(p)):
            factor = math.gcd(factor, p[i] - p[i - 1])

        locations = " ".join(f"{p[i]} ({p[i] - p[i-1]})" if i > 0 else str(p[i]) for i in range(len(p)))

        out += f"{k:6d}  {found[k][v]:5d}  {v:10s}  {factor:6d}  {locations}\n"

    return out

def get_input_and_run_kasiski(min_num):
    infile = input("Enter the input file name (or press Enter for manual input): ")
    
    if infile:
        with open(infile, 'r') as f:
            s = f.read()
    else:
        s = input("Enter the text: ")

    out = kasiski(s, min_num)
    print(out)

def main():
    i, k = 1, 0
    min_num = 3
    
    while i < len(argv):
        if argv[i] == '-m':
            i += 1
            min_num = int(argv[i])
        i += 1

    get_input_and_run_kasiski(min_num)

if __name__ == "__main__":
    main()