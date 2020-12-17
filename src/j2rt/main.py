import argparse
import json
import sys
from pathlib import Path

import jinja2

from .custom_filters import custom_filters
from .version import version


def process_args():
    parser = argparse.ArgumentParser(prog='j2rt')

    parser.add_argument(
        '-t', '--template-from', action='store', type=str, required=True,
        help="Path to template file to use"
    )

    parser.add_argument(
        '-v', '--variables-from', action='append', nargs=1,
        help="The path(s) for JSON files from which variables will be taken from, if variable in file is already defined, it will be overwritten."
    )

    parser.add_argument(
        '-V', '--variable', action='append', nargs=1,
        help="Set variable from command line, in the format name=value, prefix value with @ to read file into variable, one can escape @ by writting it as @@foo for @foo value. Variables specified at command line have highest priority and will overrride the same variable set in any of --variables-from."
    )

    parser.add_argument(
        '-o', '--output', action='store', required=False,
        help="Output file, if not set, result is printed to stdout."
    )

    parser.add_argument(
        '--version', action='version', help='Show version and exit', version=version
    )

    args, extra_args = parser.parse_known_args()
    if extra_args:
        if extra_args[0] != '--':
            parser.error("Custom arguments are to be passed after '--'.")
        extra_args.remove('--')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if not (args.variables_from or args.variable):
        parser.error('At least one of --variables-from or --variable is required')

    return args, extra_args


def read_file(path, providers):
    if path.startswith('s3://'):
        bucket, key = path.replace('s3://', '').split('/', 1)
        object = providers['s3'].get_object(Bucket=bucket, Key=key)
        return object['Body'].read().decode('utf-8')
    elif path.startswith('s3://'):
        param_name = path[6:]
        param = providers['ssm'].get_parameter(
            Name=param_name,
            WithDecryption=True
        )
        return param['Parameter']['Value']
    else:
        return Path(path).read_text()


def ssm_get_parameters(ssm_variables, providers):
    # Tier 3 hackery only to send single API request if there are multiple ssm:// parameters.
    # Individual get_parameter API requests would be way too slow and abuse AWS API too much.

    results = {}

    ssm_params = {}

    for param in providers['ssm'].get_parameters(
        Names=[ssm_variables[key][6:] for key in ssm_variables],
        WithDecryption=True
    )['Parameters']:
        ssm_params.update(
            {param['Name']: param['Value']}
        )

    for param in ssm_variables:
        ssm_param_name = ssm_variables[param][6:]
        results.update(
            {param: ssm_params[ssm_param_name]}
        )

    return results


def collect_input(template_from, variables_from, single_variables):
    variables = {}

    providers = {}
    if (
        template_from.startswith(('s3://', 'ssm://')) or
        any(item.startswith(('s3://', 'ssm://')) for item in variables_from) or
        any('=@s3://' in item for item in single_variables) or
        any('=@ssm://' in item for item in single_variables)
    ):
        # Late initialize boto3's s3 client, only if s3 is in use
        # to make sure script works without boto3 if no s3 is required.
        import boto3
        providers['s3'] = boto3.client('s3')
        providers['ssm'] = boto3.client('ssm')

    template = read_file(template_from, providers)

    # The overwrite logic goes as follow
    #     variables-from1 < variables-from2 < ... < variables-fromN < single_variables

    # Load variables from files in the order they were passed,
    # Next file can overwrite keys set by previous one.
    for path in variables_from:
        variables.update(
            json.loads(
                read_file(path, providers)
            )
        )

    # Collect SSM variables so we can get their values in a single API call.
    ssm_variables = {}

    for variable in single_variables:
        if '=' not in variable:
            raise ValueError("Wrong format '{}'".format(variable))

        name, value = variable.split("=", 1)

        if value[:1] == '@':
            value = value[1:]
            if value[:1] == '@':
                variables.update({name: value})
            else:
                if value.startswith('ssm://'):
                    ssm_variables.update(
                        {name: value}
                    )
                else:
                    variables.update({name: read_file(value, providers)})
        else:
            variables.update({name: value})

    if ssm_variables:
        variables.update(
            ssm_get_parameters(ssm_variables, providers)
        )

    return template, variables


def render(args):
    # Python before 3.8 did not had action='extend' in argsparse, so to make it just work
    # we will flatten the list of lists from action='append'.

    if args.variables_from:
        variables_from = [item for sublist in args.variables_from for item in sublist]
    else:
        variables_from = []

    if args.variable:
        single_variables = [item for sublist in args.variable for item in sublist]
    else:
        single_variables = []

    template, variables = collect_input(args.template_from, variables_from, single_variables)

    env = jinja2.Environment(
        loader=jinja2.BaseLoader(),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
    )

    env.filters.update(**custom_filters)

    result = env.from_string(template).render(**variables)

    if args.output:
        Path(args.output).write_text(result)
    else:
        print(result, end='')


def main():
    args, extra_args = process_args()

    render(args)
