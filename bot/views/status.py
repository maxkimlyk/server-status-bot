from typing import Any, Dict, Tuple

from bot import types

def build_response(status: types.Status, config: Dict[str, Any]) -> Tuple[str, str]:
    if 'ssh_user_hint' in config:
        prefix = '{}@'.format(config['ssh_user_hint'])
    else:
        prefix = ''

    time_text = status.time.isoformat()

    text = (
        'Server ip: <b>{ip}</b>\n'
        'Updated at (UTC): {time}\n'
        '\n'
        'SSH to host: '
        '<code>ssh {prefix}{ip}</code>'
    ).format(ip=status.ip, time=time_text, prefix=prefix)

    return text, 'HTML'

