from itertools import *
import string, re

def main():
    try:
        expression = input().replace(" ", "")
        if not is_valid_expression(expression):
            return 'ERROR' # Zwrócenie "ERROR" w przypadku nieprawidłowego wyrażenia
        
        reduced_expression = reduce_expression(expression)
        return reduced_expression # Zwrócenie zredukowanego wyrażenia  
         
    except Exception as e:
        return 'ERROR'

def is_valid_expression(expr):
    var = set('abcdefghijklmnopqrstuvwxyz') | set('TF')
    oper = set('~^&|/>')  # Zestaw wszystkich operatorów

    expecting_operand = True  # oczekujemy zmiennej, stałej, negacji lub otwarcia nawiasu
    parentheses_count = 0
    
    for char in expr:
        if expecting_operand:
            if char in var:
                expecting_operand = False  # Po zmiennej/stałej oczekujemy operatora
            elif char == '(':
                parentheses_count += 1
            elif char == '~':  # Negacja jest operatorem unarnym i nadal oczekujemy operanda
                continue
            else:
                return False  # Nieoczekiwany znak
        else:
            if char in oper - set('~'):  # Negacja nie może wystąpić jako operator binarny
                expecting_operand = True  # Po operatorze binarnym oczekujemy operanda
            elif char == ')':
                if parentheses_count == 0:
                    return False  # Zamykający nawias bez otwarcia
                parentheses_count -= 1
                expecting_operand = False  # Po zamknięciu nawiasu oczekujemy operatora
            else:
                return False  # Nieoczekiwany znak

    return not expecting_operand and parentheses_count == 0

def ekstraktuj_zmienne(expr):
    wzor = r"[a-z]"
    zmienne = re.findall(wzor, expr)
    unikalne_zmienne = sorted(set(zmienne))

    return unikalne_zmienne

def reduce_expression(expr):
    # Generowanie wektorów prawdy z wyrażenia
    truth_vectors = generate_truth_vectors(bracket(expr))

    # Zwróć 'F' jeśli wektory prawdy są puste (wyrażenie zawsze fałszywe)
    if not truth_vectors:
        return 'F'
    
    # Zestaw wszystkich możliwych wektorów dla długości danego wyrażenia
    all_possible_vectors = {''.join(seq) for seq in product('01', repeat=len(truth_vectors[0]))}

    # Zwróć 'T' jeśli wektory prawdy pokrywają wszystkie możliwości (wyrażenie zawsze prawdziwe)
    if set(truth_vectors) == all_possible_vectors:
        return 'T'
    
    # Minimalizacja wektorów
    minimal_vectors = minp(truth_vectors, redukuj(truth_vectors))
    
    # Zwróć 'F' jeśli nie ma minimalnych wektorów (brak spełniających wartości)
    if not minimal_vectors:
        return 'F'
    
    # Zwróć oryginalne wyrażenie jeśli minimalizacja nie zmienia wektorów
    if minimal_vectors == truth_vectors:
        return expr
    
    # Wyodrębnienie zmiennych z wyrażenia
    zmienne = ekstraktuj_zmienne(expr)
    # Budowanie zredukowanego wyrażenia z minimalnych wektorów
    reduced_expr = build_expression_from_vectors(minimal_vectors, zmienne)

    # Zwróć oryginalne wyrażenie jeśli zredukowane ma taką samą długość
    if len(reduced_expr) == len(expr):
        return expr
    
    # Zwróć zredukowane wyrażenie bez zbędnych nawiasów
    return bracket(reduced_expr)

def bracket(expr):
    if expr[0] == "(" and expr[-1] == ")" and is_valid_expression(expr[1:-1]):
        return bracket(expr[1:-1])
    return expr

# Funkcja generująca wszystkie wektory prawdy dla danego wyrazenia
def generate_truth_vectors(expr):
    variables = sorted(set(filter(str.isalpha, expr)) - {'T', 'F'})
    onp_expr = onp(bracket(expr))
    
    all_value_vectors = gen(len(variables))

    truth_vectors = []

    for value_vector in all_value_vectors:
        mapped_onp_expr = map(onp_expr, value_vector)
        if val(mapped_onp_expr) == 1:
            truth_vectors.append(value_vector)

    return truth_vectors

def lacz(s1,s2):
  lr = 0
  w = ""
  for i in range(len(s1)):
    if s1[i]==s2[i]: 
      w+=s1[i]
    else: 
      w+='-'
      lr+=1 
  if lr==1: return w
  return None

def redukuj(s):
    while True:
        s2 = set()
        changed = False
        for e1 in s:
            for e2 in s:
                if e1 != e2:
                    n = lacz(e1, e2)
                    if n:
                        changed = True
                        s2.add(n)
        s2.update(e1 for e1 in s if all(lacz(e1, e2) is None for e2 in s if e1 != e2))
        if not changed:
            break
        s = s2
    return s

# Funkcje sprawdzające czy wektory minimalne pasują do danego wzorca
def detect_xor(wektory, zmienne):
    if len(wektory) == 2 and len(zmienne) == 2:
        if sorted(wektory) == ['01','10']:
            return f"{zmienne[0]}^{zmienne[1]}"
    return None

def detect_imp(wektory,zmienne):
    if len(wektory) == 2 and len(zmienne) == 2:
        if sorted(wektory) == ['-1','0-']:
            return f"{zmienne[0]}>{zmienne[1]}"
    return None

def detect_dys(wektory, zmienne):
    if len(wektory) == 2 and len(zmienne) == 2:
        if sorted(wektory) == ['-0', '0-']:
            return f"{zmienne[0]}/{zmienne[1]}"
    return None

def detect_xor2(wektory, zmienne):
    if len(wektory) == 4 and len(zmienne) == 3:
        if sorted(wektory) == ['001', '010', '100', '111']:
            return f"{zmienne[0]}^{zmienne[1]}^{zmienne[2]}"
    return None

def detect_imp2(wektory,zmienne):
    if len(wektory) == 2 and len(zmienne) == 3:
        if sorted(wektory) == ['--1','10-']:
            return f"{zmienne[0]}>{zmienne[1]}>{zmienne[2]}"
    return None

def detect_dys2(wektory, zmienne):
    if len(wektory) == 2 and len(zmienne) == 3:
        if sorted(wektory) == ['--0', '11-']:
            return f"{zmienne[0]}/{zmienne[1]}/{zmienne[2]}"
    return None

# Funkcja budująca wyrazenie z minimalnych wektorów
def build_expression_from_vectors(wektory, zmienne):
    wyrażenia = []

    xor_expression = detect_xor(wektory, zmienne)
    if xor_expression:
        return xor_expression
    
    imp_expression = detect_imp(wektory, zmienne)
    if imp_expression:
        return imp_expression
    
    dys_expression = detect_dys(wektory, zmienne)
    if dys_expression:
        return dys_expression
    
    xor_expression2 = detect_xor2(wektory, zmienne)
    if xor_expression2:
        return xor_expression2
    
    imp_expression2 = detect_imp2(wektory, zmienne)
    if imp_expression2:
        return imp_expression2
    
    dys_expression2 = detect_dys2(wektory, zmienne)
    if dys_expression2:
        return dys_expression2
    
    for wektor in wektory:
        części_wyrażenia = []

        for i, wartość in enumerate(wektor):
            if wartość == '1':
                części_wyrażenia.append(f"{zmienne[i]}")
            elif wartość == '0':
                części_wyrażenia.append(f"~{zmienne[i]}")

        if len(części_wyrażenia) > 1:
            część_wyrażenia = f"({'&'.join(części_wyrażenia)})"
        else:
            część_wyrażenia = '&'.join(części_wyrażenia)

        if część_wyrażenia: 
            wyrażenia.append(część_wyrażenia)

    wynikowe_wyrażenie = "|".join(wyrażenia)
    return wynikowe_wyrażenie

def match(x,w):
  for i in range(len(x)):
    if w[i]=='-': continue
    if w[i]!=x[i]: return False
  return True

def minp(d, w):
    for r in range(1, len(w)+1):
        for c in combinations(w, r):
            nowy = set()
            for el in d:
                for wz in c: 
                    if match(el, wz): nowy.add(el)
            if len(nowy) == len(d): return set(c)
    return None

# Zamiana na ONP
def onp(expr):
    output = []
    stack = []
    precedence = {'~': 4, '^': 3, '&': 2, '|': 2, '/': 2, '>': 1}

    for token in expr:
        if token.isalpha() or token in 'TF': 
            output.append(token)
        elif token == '~':
            stack.append(token)
        elif token in precedence:
            while stack and precedence.get(stack[-1], 0) >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()

    while stack:
        output.append(stack.pop())

    return ''.join(output)

def bal(expr, op):
    ln = 0  # Licznik nawiasów
    for i in range(len(expr)-1, -1, -1):
        if expr[i] == ")":
            ln += 1
        elif expr[i] == "(":
            ln -= 1
        elif expr[i] == op and ln == 0:
            return i
    return None

def bracket(expr):
    if expr[0] == "(" and expr[-1] == ")" and is_valid_expression(expr[1:-1]):
        return bracket(expr[1:-1])
    return expr

def map(expr, ver):

    t = {sorted(list(set(expr).intersection(set(string.ascii_lowercase))))[i]:ver[i] for i in range(len(ver))}

    for k in t: 
        expr = expr.replace(k, t[k])

    return expr

def gen(n):
    return [''.join(seq) for seq in product('01', repeat=n)]

def val(expr):
    st = []
    for z in expr:
        if z in '01':
            st.append(int(z))
        elif z == 'T':
            st.append(1) 
        elif z == 'F':
            st.append(0)
        elif z == '|':
            b = st.pop()
            a = st.pop()
            st.append(a | b)
        elif z == '&':
            b = st.pop()
            a = st.pop()
            st.append(a & b)
        elif z == '>':
            b = st.pop()
            a = st.pop()
            st.append((not a) | b)
        elif z == '^':
            b = st.pop()
            a = st.pop()
            st.append(a ^ b)
        elif z == '~':
            a = st.pop()
            st.append(not a)
        elif z == '/':
            b = st.pop()
            a = st.pop()
            st.append(not(a and b))
        else:
            raise ValueError(f"Nieznany operator: {z}")

    if len(st) != 1:
        raise ValueError("Nieprawidłowe wyrażenie ONP - nieoczekiwana liczba elementów na stosie")

    return int(st.pop())

if __name__ == "__main__":
    result = main()
    print(result)