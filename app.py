"""
DD Tools - Flask Web Application
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import io

from libs import encoding_converter

app = Flask(__name__)
app.secret_key = 'dd-tools-secret-key-change-in-production'  # Změň v produkci!

# Konfigurace
UPLOAD_FOLDER = '/tmp/dd-tools-uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Registrace nástrojů pro menu
TOOLS = [
    {
        'id': 'encoding',
        'name': 'Převod kódování',
        'description': 'Převod textových souborů mezi různými kódováními',
        'route': 'encoding_converter_page'
    }
    # Zde přidávej další nástroje
]


@app.route('/')
def index():
    """Úvodní stránka"""
    return render_template('index.html', tools=TOOLS)


@app.route('/encoding')
def encoding_converter_page():
    """Stránka pro převod kódování"""
    encodings = encoding_converter.get_encodings()
    error_modes = encoding_converter.get_error_modes()
    return render_template('encoding.html', 
                         encodings=encodings, 
                         error_modes=error_modes,
                         tools=TOOLS)


@app.route('/encoding/convert', methods=['POST'])
def encoding_convert():
    """Zpracování převodu kódování"""
    
    # Kontrola nahraného souboru
    if 'file' not in request.files:
        flash('Nebyl vybrán žádný soubor', 'error')
        return redirect(url_for('encoding_converter_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nebyl vybrán žádný soubor', 'error')
        return redirect(url_for('encoding_converter_page'))
    
    # Získání parametrů
    source_encoding = request.form.get('source_encoding')
    target_encoding = request.form.get('target_encoding')
    error_mode = request.form.get('error_mode', 'replace')
    
    # Validace
    if not source_encoding or not target_encoding:
        flash('Musíte vybrat zdrojové i cílové kódování', 'error')
        return redirect(url_for('encoding_converter_page'))
    
    try:
        # Načti obsah souboru
        content = file.read()
        
        # Převeď kódování
        converted, error = encoding_converter.convert_content(
            content, source_encoding, target_encoding, error_mode
        )
        
        if error:
            flash(error, 'error')
            return redirect(url_for('encoding_converter_page'))
        
        # Vytvoř název výstupního souboru
        original_filename = secure_filename(file.filename)
        output_filename = encoding_converter.generate_output_filename(
            original_filename, target_encoding
        )
        
        # Vrať soubor ke stažení
        return send_file(
            io.BytesIO(converted),
            mimetype='text/plain',
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        flash(f'Chyba při zpracování: {str(e)}', 'error')
        return redirect(url_for('encoding_converter_page'))


@app.context_processor
def inject_app_name():
    """Vloží název aplikace do všech šablon"""
    return {'app_name': 'DD Tools'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
