"""Recording profile names and ports; secrets live separately in ignored private/."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_NAME = 'resgrid-academy-capture'
DEFAULT_PORTS = {'web': 18867, 'api': 18868, 'eventing': 18869, 'mail': 18026, 'rabbit': 15674}

def profile(name=DEFAULT_NAME, web_port=18867):
    if not re.fullmatch(r'resgrid-academy-[a-z0-9][a-z0-9-]{0,40}', name):
        raise ValueError('Use a distinct name beginning resgrid-academy-; the original resgrid-academy stack is reserved.')
    delta = web_port - DEFAULT_PORTS['web']
    ports = {key: value + delta for key, value in DEFAULT_PORTS.items()}
    if any(port < 1024 or port > 65535 for port in ports.values()):
        raise ValueError('Recording ports must be between 1024 and 65535.')
    return {'name': name, 'ports': ports}

def load():
    path = ROOT / 'private/stack.json'
    data = json.loads(path.read_text()) if path.exists() else profile()
    expected = profile(data['name'], data['ports']['web'])
    if data != expected:
        raise ValueError('Invalid recording profile; do not mix ports or Docker volume names.')
    return data
