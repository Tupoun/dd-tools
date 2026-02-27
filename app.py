"""
DD Tools - Flask Web Application
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import io

from libs import encoding_converter, bytes_converter, text_encoder, jwt_decoder, hash_generator, cron_parser, formatter, utilities, diff_tool, csv_json, uuid_generator, yaml_json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

if not app.secret_key:
    raise ValueError("SECRET_KEY environment variable is not set!")

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
    },
    {
        'id': 'bytes',
        'name': 'Převod bajtů',
        'description': 'Převod Unicode escape sekvencí na čísla a zpět',
        'route': 'bytes_converter_page'
    },
    {
        'id': 'encoder',
        'name': 'Encoder',
        'description': 'Base64, URL encode, Hex a další převody',
        'route': 'text_encoder_page'
    },
    {
        'id': 'jwt',
        'name': 'JWT Decoder',
        'description': 'Dekódování JWT tokenů',
        'route': 'jwt_decoder_page'
    },
    {
        'id': 'hash',
        'name': 'Hash generátor',
        'description': 'MD5, SHA-1, SHA-256, SHA-512',
        'route': 'hash_generator_page'
    },
    {
        'id': 'cron',
        'name': 'Cron',
        'description': 'Parser a generátor cron výrazů',
        'route': 'cron_page'
    },
    {
        'id': 'formatter',
        'name': 'Formatter',
        'description': 'Formátování JSON a XML',
        'route': 'formatter_page'
    },
    {
        'id': 'utilities',
        'name': 'Utilities',
        'description': 'Unix timestamp, JSON unescape, Unicode unescape',
        'route': 'utilities_page'
    },
    {
        'id': 'diff',
        'name': 'Diff',
        'description': 'Porovnání dvou textů',
        'route': 'diff_page'
    },
    {
        'id': 'csv_json',
        'name': 'CSV ↔ JSON',
        'description': 'Konverze mezi CSV a JSON',
        'route': 'csv_json_page'
    },
    {
        'id': 'uuid',
        'name': 'UUID',
        'description': 'Generátor UUID v1 a v4',
        'route': 'uuid_page'
    },
    {
        'id': 'yaml_json',
        'name': 'YAML ↔ JSON',
        'description': 'Konverze mezi YAML a JSON',
        'route': 'yaml_json_page'
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

    if 'file' not in request.files:
        flash('Nebyl vybrán žádný soubor', 'error')
        return redirect(url_for('encoding_converter_page'))

    file = request.files['file']
    if file.filename == '':
        flash('Nebyl vybrán žádný soubor', 'error')
        return redirect(url_for('encoding_converter_page'))

    source_encoding = request.form.get('source_encoding')
    target_encoding = request.form.get('target_encoding')
    error_mode = request.form.get('error_mode', 'replace')

    if not source_encoding or not target_encoding:
        flash('Musíte vybrat zdrojové i cílové kódování', 'error')
        return redirect(url_for('encoding_converter_page'))

    try:
        content = file.read()
        converted, error = encoding_converter.convert_content(
            content, source_encoding, target_encoding, error_mode
        )

        if error:
            flash(error, 'error')
            return redirect(url_for('encoding_converter_page'))

        original_filename = secure_filename(file.filename)
        output_filename = encoding_converter.generate_output_filename(
            original_filename, target_encoding
        )

        return send_file(
            io.BytesIO(converted),
            mimetype='text/plain',
            as_attachment=True,
            download_name=output_filename
        )

    except Exception as e:
        flash(f'Chyba při zpracování: {str(e)}', 'error')
        return redirect(url_for('encoding_converter_page'))


@app.route('/bytes', methods=['GET', 'POST'])
def bytes_converter_page():
    """Stránka pro převod bajtů"""
    result = None
    form_data = {}

    if request.method == 'POST':
        direction = request.form.get('direction')
        divisor = float(request.form.get('divisor', 1) or 1)
        form_data = {'direction': direction, 'divisor': divisor}

        if direction == 'to_number':
            escapes = request.form.get('escapes', '')
            form_data['escapes'] = escapes
            output, error = bytes_converter.escapes_to_number(escapes, divisor)
            result = {'direction': direction, 'output': output, 'error': error}
        elif direction == 'to_escapes':
            number = request.form.get('number', '')
            form_data['number'] = number
            output, error = bytes_converter.number_to_escapes(number, divisor)
            result = {'direction': direction, 'output': output, 'error': error}

    return render_template('bytes_converter.html', tools=TOOLS, result=result, form_data=form_data)


@app.route('/encoder', methods=['GET', 'POST'])
def text_encoder_page():
    """Stránka pro enkódování textu"""
    result = None
    form_data = {}

    if request.method == 'POST':
        algorithm = request.form.get('algorithm', 'base64')
        action = request.form.get('action', 'encode')
        text = request.form.get('input', '')
        form_data = {'algorithm': algorithm, 'action': action, 'input': text}

        if action == 'encode':
            output, error = text_encoder.encode(text, algorithm)
        else:
            output, error = text_encoder.decode(text, algorithm)

        result = {'output': output, 'error': error}

    return render_template('text_encoder.html', tools=TOOLS,
                           result=result, form_data=form_data,
                           algorithms=text_encoder.ALGORITHMS)


@app.route('/jwt', methods=['GET', 'POST'])
def jwt_decoder_page():
    """Stránka pro dekódování JWT tokenů"""
    result = None
    form_data = {}

    if request.method == 'POST':
        token = request.form.get('token', '')
        form_data = {'token': token}
        decoded, error = jwt_decoder.decode(token)
        if error:
            result = {'error': error}
        else:
            result = decoded

    return render_template('jwt_decoder.html', tools=TOOLS, result=result, form_data=form_data)


@app.route('/hash', methods=['GET', 'POST'])
def hash_generator_page():
    """Stránka pro generování hashů"""
    result = None
    form_data = {}

    if request.method == 'POST':
        text = request.form.get('text', '')
        form_data = {'text': text}
        result = hash_generator.compute_all(text)

    return render_template('hash_generator.html', tools=TOOLS, result=result, form_data=form_data)


@app.route('/cron', methods=['GET', 'POST'])
def cron_page():
    """Stránka pro cron parser a generátor"""
    parse_result = None
    build_result = None
    parse_form = {}
    build_form = {}

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'parse':
            expression = request.form.get('expression', '').strip()
            parse_form = {'expression': expression}

            description, error = cron_parser.describe(expression)
            if error:
                parse_result = {'error': error}
            else:
                runs, err2 = cron_parser.next_runs(expression)
                parse_result = {
                    'description': description,
                    'next_runs': runs or [],
                    'error': err2,
                }

        elif action == 'build':
            fields = {
                'minute':  request.form.get('minute', '*'),
                'hour':    request.form.get('hour', '*'),
                'day':     request.form.get('day', '*'),
                'month':   request.form.get('month', '*'),
                'weekday': request.form.get('weekday', '*'),
            }
            build_form = fields
            expression = cron_parser.build(**fields)
            description, error = cron_parser.describe(expression)
            build_result = {
                'expression': expression,
                'description': description,
                'error': error,
            }

    return render_template('cron.html', tools=TOOLS,
                           parse_result=parse_result,
                           build_result=build_result,
                           parse_form=parse_form,
                           build_form=build_form,
                           presets=cron_parser.PRESETS)


@app.route('/formatter', methods=['GET', 'POST'])
def formatter_page():
    """Stránka pro formátování JSON a XML"""
    json_result = None
    xml_result = None
    json_form = {}
    xml_form = {}

    if request.method == 'POST':
        action = request.form.get('action')

        if action in ('pretty', 'minify', 'sort'):
            text = request.form.get('json_input', '')
            json_form = {'input': text}
            if action == 'pretty':
                output, error = formatter.format_json(text)
            elif action == 'minify':
                output, error = formatter.minify_json(text)
            elif action == 'sort':
                output, error = formatter.format_json(text, sort_keys=True)
            json_result = {'output': output, 'error': error}

        elif action == 'xml_format':
            text = request.form.get('xml_input', '')
            xml_form = {'input': text}
            output, error = formatter.format_xml(text)
            xml_result = {'output': output, 'error': error}

    return render_template('formatter.html', tools=TOOLS,
                           json_result=json_result, xml_result=xml_result,
                           json_form=json_form, xml_form=xml_form)


@app.route('/utilities', methods=['GET', 'POST'])
def utilities_page():
    """Stránka pro utility"""
    ts_result = None
    json_unescape_result = None
    unicode_unescape_result = None
    html_entity_result = None
    form_data = {}

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'ts_to_dt':
            ts = request.form.get('timestamp', '')
            form_data = {'action': action, 'timestamp': ts}
            output, error = utilities.timestamp_to_datetime(ts)
            ts_result = {'output': output, 'error': error, 'direction': 'to_dt'}

        elif action == 'dt_to_ts':
            dt_str = request.form.get('datetime', '')
            form_data = {'action': action, 'datetime': dt_str}
            output, error = utilities.datetime_to_timestamp(dt_str)
            ts_result = {'output': output, 'error': error, 'direction': 'to_ts'}

        elif action == 'json_unescape':
            text = request.form.get('json_escaped', '')
            form_data = {'action': action, 'json_escaped': text}
            output, error = utilities.unescape_json_string(text)
            json_unescape_result = {'output': output, 'error': error}

        elif action == 'unicode_unescape':
            text = request.form.get('unicode_escaped', '')
            form_data = {'action': action, 'unicode_escaped': text}
            output, error = utilities.unescape_unicode(text)
            unicode_unescape_result = {'output': output, 'error': error}

        elif action == 'html_encode':
            text = request.form.get('html_input', '')
            form_data = {'action': action, 'html_input': text}
            output, error = utilities.encode_html_entities(text)
            html_entity_result = {'output': output, 'error': error, 'direction': 'encode'}

        elif action == 'html_decode':
            text = request.form.get('html_input', '')
            form_data = {'action': action, 'html_input': text}
            output, error = utilities.decode_html_entities(text)
            html_entity_result = {'output': output, 'error': error, 'direction': 'decode'}

    return render_template('utilities.html', tools=TOOLS,
                           ts_result=ts_result,
                           json_unescape_result=json_unescape_result,
                           unicode_unescape_result=unicode_unescape_result,
                           html_entity_result=html_entity_result,
                           form_data=form_data)


@app.route('/diff', methods=['GET', 'POST'])
def diff_page():
    """Stránka pro porovnání textů"""
    result = None
    form_data = {}

    if request.method == 'POST':
        text1 = request.form.get('text1', '')
        text2 = request.form.get('text2', '')
        form_data = {'text1': text1, 'text2': text2}
        lines, identical = diff_tool.compare(text1, text2)
        result = {'lines': lines, 'identical': identical}

    return render_template('diff.html', tools=TOOLS, result=result, form_data=form_data)


@app.route('/csv-json', methods=['GET', 'POST'])
def csv_json_page():
    """Stránka pro konverzi CSV ↔ JSON"""
    result = None
    form_data = {}

    if request.method == 'POST':
        action = request.form.get('action')
        delimiter = request.form.get('delimiter', ',')
        if len(delimiter) != 1:
            delimiter = ','

        if action == 'csv_to_json':
            text = request.form.get('csv_input', '')
            form_data = {'action': action, 'csv_input': text}
            output, error = csv_json.csv_to_json(text, delimiter)
            result = {'action': action, 'output': output, 'error': error}

        elif action == 'json_to_csv':
            text = request.form.get('json_input', '')
            form_data = {'action': action, 'json_input': text}
            output, error = csv_json.json_to_csv(text, delimiter)
            result = {'action': action, 'output': output, 'error': error}

    return render_template('csv_json.html', tools=TOOLS, result=result, form_data=form_data)


@app.route('/uuid', methods=['GET', 'POST'])
def uuid_page():
    """Stránka pro generování UUID"""
    result = None
    form_data = {}

    if request.method == 'POST':
        version = request.form.get('version', '4')
        count = request.form.get('count', '1')
        form_data = {'version': version, 'count': count}
        uuids, error = uuid_generator.generate(version, count)
        result = {'uuids': uuids, 'error': error}

    return render_template('uuid.html', tools=TOOLS, result=result,
                           form_data=form_data, versions=uuid_generator.VERSIONS)


@app.route('/yaml-json', methods=['GET', 'POST'])
def yaml_json_page():
    """Stránka pro konverzi YAML ↔ JSON"""
    result = None
    form_data = {}

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'yaml_to_json':
            text = request.form.get('yaml_input', '')
            form_data = {'action': action, 'yaml_input': text}
            output, error = yaml_json.yaml_to_json(text)
            result = {'action': action, 'output': output, 'error': error}

        elif action == 'json_to_yaml':
            text = request.form.get('json_input', '')
            form_data = {'action': action, 'json_input': text}
            output, error = yaml_json.json_to_yaml(text)
            result = {'action': action, 'output': output, 'error': error}

    return render_template('yaml_json.html', tools=TOOLS, result=result, form_data=form_data)


@app.context_processor
def inject_app_name():
    """Vloží název aplikace do všech šablon"""
    return {'app_name': 'DD Tools'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
