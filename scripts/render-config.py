#!/usr/bin/env python3
"""Render a reviewed signer to a NEW local file. Never installs or runs it."""
import argparse
from pathlib import Path
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]


def render(linux_esp, windows_esp, signer_cn):
    linux_esp, windows_esp = str(uuid.UUID(linux_esp)), str(uuid.UUID(windows_esp))
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}', signer_cn):
        raise ValueError('Use a 1–80 character ASCII certificate CN: letters, digits, spaces, ._-')
    result = (ROOT / 'templates/local-secure-boot-sign.py.in').read_text()
    for key, value in {'@LINUX_ESP_PARTUUID@': linux_esp,
                       '@WINDOWS_ESP_PARTUUID@': windows_esp,
                       '@SIGNER_CN@': signer_cn}.items():
        result = result.replace(key, value)
    if re.search(r'@[A-Z_]+@', result):
        raise ValueError('Unresolved template placeholder')
    compile(result, '<rendered signer>', 'exec')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--linux-esp-partuuid', required=True)
    parser.add_argument('--windows-esp-partuuid', required=True)
    parser.add_argument('--signer-cn', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        content = render(args.linux_esp_partuuid, args.windows_esp_partuuid, args.signer_cn)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(content)
    print(f'Created {args.output}. Review before installing; no system configuration changed.')


if __name__ == '__main__':
    main()
