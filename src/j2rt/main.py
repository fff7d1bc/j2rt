import argparse
import json
import sys
from pathlib import Path

import jinja2


def process_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-t', '--template-from', action='store', type=str, required=True,
        help="Path to template file to use"
    )

    parser.add_argument(
        '-v', '--variables-from', action='append', nargs='+', required=True,
        help="The path(s) for JSON files from which variables will be taken from, if variable in file is already defined, it will be overwritten."
    )

    parser.add_argument(
        '-o', '--output', action='store', required=False,
        help="Output file, if not set, result is printed to stdout."
    )

    args, extra_args = parser.parse_known_args()
    if extra_args:
        if extra_args[0] != '--':
            parser.error("Custom arguments are to be passed after '--'.")
        extra_args.remove('--')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args, extra_args


def read_file(path, providers):
    if path.startswith('s3://'):
        bucket, key = path.replace('s3://', '').split('/', 1)

        object = providers['s3'].get_object(Bucket=bucket, Key=key)

        return object['Body'].read().decode('utf-8')
    else:
        return Path(path).read_text()


def collect_input(template_from, variables_from):
    variables = {}

    providers = {}
    if template_from.startswith('s3://') or any(item.startswith('s3://') for item in variables_from):
        # Late initialize boto3's s3 client, only if s3 is in use
        # to make sure script works without boto3 if no s3 is required.
        import boto3
        providers['s3'] = boto3.client('s3')

    template = read_file(template_from, providers)

    for path in variables_from:
        variables.update(
            json.loads(
                read_file(path, providers)
            )
        )

    return template, variables


def render(args):
    # Python before 3.8 did not had action='extend' in argsparse, so to make it just work
    # we will flatten the list of lists from action='append'.
    variables_from = [item for sublist in args.variables_from for item in sublist]

    template, variables = collect_input(args.template_from, variables_from)

    result = jinja2.Environment(
        loader=jinja2.BaseLoader(),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True
    ).from_string(template).render(**variables)

    if args.output:
        Path(args.output).write_text(result)
    else:
        print(result, end='')


def main():
    args, extra_args = process_args()

    render(args)
