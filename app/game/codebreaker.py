import random
import string

def generate_mission():
    answer = random.choice(['GHOST', 'RAVEN', 'CIPHER', 'SHADOW', 'ORION', 'TARGET', 'DANGER'])
    shift = random.randint(1, 25)
    
    # Encrypt the word
    ciphertext = ''.join(chr((ord(c) - 65 + shift) % 26 + 65) if c.isupper() else c for c in answer)
    
    # Generate the decoder ring (Top row is normal, bottom row is shifted)
    normal_alphabet = string.ascii_uppercase
    shifted_alphabet = ''.join(chr((ord(c) - 65 + shift) % 26 + 65) for c in normal_alphabet)
    
    return {
        'ciphertext': ciphertext,
        'answer': answer,
        'shift': shift,
        'normal': normal_alphabet,
        'shifted': shifted_alphabet,
        'hint': f'Caesar shift detected. Key: {shift}'
    }

def check_answer(user_input, correct_answer):
    return user_input.strip().upper() == correct_answer.upper()
