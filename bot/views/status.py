from typing import Any, Dict, Tuple

from bot import types

def build_response(status: types.Status, config: Dict[str, Any]) -> Tuple[str, str]:
    if 'ssh_user_hint' in config:
        prefix = '{}@'.format(config['ssh_user_hint'])
    else:
        prefix = ''

    if 'ssh_port_hint' in config:
        port = '-p {}'.format(config['ssh_port_hint'])
    else:
        port = ''

    time_text = status.time.isoformat()

    text = (
        'Server ip: <b>{ip}</b>\n'
        'Updated at (UTC): {time}\n'
        '\n'
        'SSH to host: \n'
        '<code>ssh {port} {prefix}{ip}</code>'
    ).format(ip=status.ip, port=port, time=time_text, prefix=prefix)

    return text, 'HTML'

