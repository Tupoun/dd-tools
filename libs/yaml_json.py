import json
import yaml

MAX_INPUT = 1_000_000


def yaml_to_json(text):
    if len(text) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 1 MB)'
    try:
        data = yaml.safe_load(text)
        return json.dumps(data, indent=2, ensure_ascii=False), None
    except yaml.YAMLError as e:
        return None, f'Chyba v YAML: {e}'
    except Exception as e:
        return None, str(e)


def json_to_yaml(text):
    if len(text) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 1 MB)'
    try:
        data = json.loads(text)
        return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False), None
    except json.JSONDecodeError as e:
        return None, f'Chyba v JSON: {e}'
    except Exception as e:
        return None, str(e)
