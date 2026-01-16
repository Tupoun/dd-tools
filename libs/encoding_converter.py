"""
Knihovna pro převod kódování textových souborů
"""

# Podporovaná kódování
ENCODINGS = [
    ('utf-8', 'UTF-8'),
    ('windows-1250', 'Windows-1250'),
    ('cp852', 'CP852 (DOS)'),
    ('iso-8859-1', 'ISO-8859-1 (Latin-1)'),
    ('iso-8859-2', 'ISO-8859-2 (Latin-2)'),
    ('iso-8859-15', 'ISO-8859-15 (Latin-9)')
]

ERROR_MODES = [
    ('replace', 'Nahradit otazníkem (?)'),
    ('ignore', 'Ignorovat (vynechat)')
]


def get_encodings():
    """Vrátí seznam dostupných kódování"""
    return ENCODINGS


def get_error_modes():
    """Vrátí seznam režimů chyb"""
    return ERROR_MODES


def convert_content(content, source_encoding, target_encoding, error_mode='replace'):
    """
    Převede textový obsah mezi kódováními
    
    Args:
        content: Binární obsah souboru (bytes)
        source_encoding: Zdrojové kódování (str)
        target_encoding: Cílové kódování (str)
        error_mode: Režim pro chyby ('replace' nebo 'ignore')
    
    Returns:
        tuple: (převedený obsah v bytes, chybová zpráva nebo None)
    """
    try:
        # Dekóduj ze zdrojového kódování
        text = content.decode(source_encoding)
        
        # Enkóduj do cílového kódování
        converted = text.encode(target_encoding, errors=error_mode)
        
        return converted, None
        
    except UnicodeDecodeError as e:
        return None, f"Chyba při dekódování: Zdrojové kódování '{source_encoding}' pravděpodobně není správné."
    except UnicodeEncodeError as e:
        return None, f"Chyba při enkódování: Některé znaky nelze převést do '{target_encoding}'."
    except Exception as e:
        return None, f"Neočekávaná chyba: {str(e)}"


def generate_output_filename(original_filename, target_encoding):
    """
    Vytvoří název výstupního souboru
    
    Args:
        original_filename: Původní název souboru
        target_encoding: Cílové kódování
    
    Returns:
        str: Nový název souboru
    """
    import os
    name, ext = os.path.splitext(original_filename)
    return f"{name}_{target_encoding}{ext}"
