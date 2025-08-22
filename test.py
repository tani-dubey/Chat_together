import random
from string import ascii_uppercase,digits,ascii_lowercase

def generate_unique_code(length):
    characters=ascii_uppercase+digits+ascii_lowercase
    return ''.join(random.choices(characters,k=length))
trye=generate_unique_code(4)
print(trye)