#!/usr/bin/env python3
"""Generate a verified TWA Digital Asset Links JSON from a signing certificate."""
import argparse
import json
import pathlib
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keystore', required=True)
    parser.add_argument('--alias', required=True)
    parser.add_argument('--storepass', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--package', default='ir.afishu.app')
    args = parser.parse_args()
    result = subprocess.run([
        'keytool', '-list', '-v', '-keystore', args.keystore,
        '-alias', args.alias, '-storepass', args.storepass,
    ], text=True, capture_output=True, check=True)
    fingerprint = re.search(r'^\s*SHA256:\s*((?:[0-9A-Fa-f]{2}:){31}[0-9A-Fa-f]{2})\s*$', result.stdout, re.MULTILINE)
    if fingerprint is None:
        sys.exit('Cannot extract the SHA256 fingerprint from keytool output')
    statements = [{
        'relation': ['delegate_permission/common.handle_all_urls'],
        'target': {
            'namespace': 'android_app',
            'package_name': args.package,
            'sha256_cert_fingerprints': [fingerprint.group(1).upper()],
        },
    }]
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(statements, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Digital Asset Links created:', str(output))
    print('SHA256:', fingerprint.group(1).upper())


if __name__ == '__main__':
    main()
