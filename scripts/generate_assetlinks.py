#!/usr/bin/env python3
"""Create Digital Asset Links exclusively from a verified, signed Android APK.

The certificate fingerprint is read from the APK itself rather than an assumed
keystore path, preventing invalid association statements in CI environments.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def tool_output(command: list[str], description: str) -> str:
    try:
        process = subprocess.run(
            command,
            text=True,
            encoding='utf-8',
            errors='replace',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise SystemExit(f'{description}: cannot execute {command[0]!r}: {exc}') from exc
    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip()
        raise SystemExit(
            f'{description}: exit status {process.returncode}.\n{detail[-3000:]}'
        )
    return process.stdout


def build_statement(apk: Path, package: str, apksigner: str, aapt: str) -> list[dict]:
    if not apk.is_file():
        raise SystemExit(f'APK is missing: {apk}')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+', package):
        raise SystemExit(f'Invalid Android package name: {package!r}')

    # aapt reads the actual final APK manifest, including debug app ID suffixes.
    package_info = tool_output([aapt, 'dump', 'badging', str(apk)], 'APK manifest inspection')
    package_match = re.search(r"^package:\s+name='([^']+)'", package_info, re.MULTILINE)
    if package_match is None:
        raise SystemExit('Cannot locate APK package name from aapt output')
    actual_package = package_match.group(1)
    if actual_package != package:
        raise SystemExit(
            f'Package mismatch: APK contains {actual_package!r}, '
            f'but workflow expects {package!r}'
        )

    # apksigner verifies the signed binary, supporting APK Signature Scheme v2+.
    certificate_info = tool_output(
        [apksigner, 'verify', '--verbose', '--print-certs', str(apk)],
        'APK signature verification',
    )
    fingerprints = re.findall(
        r'^Signer #\d+ certificate SHA-256 digest:\s*([0-9a-fA-F:]+)\s*$',
        certificate_info,
        re.MULTILINE,
    )
    if len(fingerprints) != 1:
        raise SystemExit(
            f'Expected exactly one APK signer certificate, found {len(fingerprints)}'
        )
    hex_fingerprint = fingerprints[0].replace(':', '').upper()
    if not re.fullmatch(r'[0-9A-F]{64}', hex_fingerprint):
        raise SystemExit('Invalid SHA-256 signing certificate fingerprint')
    fingerprint = ':'.join(hex_fingerprint[i:i + 2] for i in range(0, 64, 2))

    return [{
        'relation': ['delegate_permission/common.handle_all_urls'],
        'target': {
            'namespace': 'android_app',
            'package_name': actual_package,
            'sha256_cert_fingerprints': [fingerprint],
        },
    }]


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate assetlinks.json from the real APK signing certificate'
    )
    parser.add_argument('--apk', type=Path, required=True)
    parser.add_argument('--package', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--apksigner', default='apksigner')
    parser.add_argument('--aapt', default='aapt')
    args = parser.parse_args()

    statements = build_statement(args.apk, args.package, args.apksigner, args.aapt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(statements, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(f'Digital Asset Links: {args.output}')
    print(f'Package verified: {args.package}')
    print('Certificate fingerprint verified against signed APK')


if __name__ == '__main__':
    main()
