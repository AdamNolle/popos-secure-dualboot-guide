#!/usr/bin/env python3
"""Optional rEFInd 0.14.2 offline label edit. Output requires fresh signing."""
import argparse
from pathlib import Path

OLD = 'Reboot to Computer Setup Utility'.encode('utf-16le')
NEW = 'BIOS'.encode('utf-16le')


def patch_image(data):
    if not data.startswith(b'MZ') or data.count(OLD) != 1:
        raise ValueError('Expected a PE image with exactly one known title; refusing unknown input')
    return data.replace(OLD, NEW + bytes(len(OLD) - len(NEW)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = patch_image(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(data)
    print('Staged BIOS label. Existing signatures are INVALID: remove them on this copy,')
    print('re-sign with your enrolled key, and verify before installation. Original unchanged.')


if __name__ == '__main__':
    main()
