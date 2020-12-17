j2rt - Jinja2 rendering tool
============================

j2rt is a tool meant to simplify Jinja2 usage for CLI, be that with shell scripts, continuous integration pipelines or anything else, where ``m4`` is not a good fit, with all the whistles and bells that Jinja2 offers, if statements, for loops, filters and many more, see Jinja2's `syntax <https://jinja.palletsprojects.com/en/2.11.x/templates/>`_ for list of features. The tool can take template and variable files from local filesystem as well as remote like S3 and SSM. The S3 integration makes it easy to create a secure secrets store for your configuration files, since S3 can be encrypted (KMS or regular server side AES), it's viable to place secrets.json in S3 and then load it during deployment process for the configuration files to be generated, as one of use cases.

Multiple variable files can be used, in a way that one can, for example, specify one base variables file, and then append some keys, or override others, if needed.

Python dependencies
-------------------
- jinja2
- boto3 (optional, provides support for s3:// and ssm://)
- python-gnupg (optional, used with gpg_decrypt jinja2 filter)

Custom filters
--------------

Filters that are supported but are not part of official Jinja2 specification

- b64decode - decode base64 encoded string into it's original form.
- b64encode - encode string into base64.
- gpg_decrypt - decrypt string with GnuPG

Installation
------------

From PYPI::

  pip install j2rt

From master branch::

  pip install https://github.com/slashbeast/j2rt/archive/master.zip

Note: it's generally unwise to install packages with ``pip`` outside of ``virtualenv``, if however this is what you want, append ``--user`` to the ``pip`` invocation to install it locally for logged user only.

Usage
-----

The template and variable file(s) can be either local, or remote s3, if prefixed with s3://. Template is to be written in jinja2 and variable files are to be JSON formatted. One or more variable files can be specified, the same variable can be set in multiple variable files, the last one to be defined will be used.

::

  usage: j2rt [-h] -t TEMPLATE_FROM [-v VARIABLES_FROM] [-V VARIABLE]
              [-o OUTPUT] [--version]

  optional arguments:
    -h, --help            show this help message and exit
    -t TEMPLATE_FROM, --template-from TEMPLATE_FROM
                          Path to template file to use
    -v VARIABLES_FROM, --variables-from VARIABLES_FROM
                          The path(s) for JSON files from which variables will
                          be taken from, if variable in file is already defined,
                          it will be overwritten.
    -V VARIABLE, --variable VARIABLE
                          Set variable from command line, in the format
                          name=value, prefix value with @ to read file into
                          variable, one can escape @ by writting it as @@foo for
                          @foo value. Variables specified at command line have
                          highest priority and will overrride the same variable
                          set in any of --variables-from.
    -o OUTPUT, --output OUTPUT
                          Output file, if not set, result is printed to stdout.
    --version             Show version and exit

Examples
--------

Generate nginx.conf
::

  j2rt \
    -t s3://somebucket/nginx.conf.j2 \
    -v /etc/nginx.conf.base.json -v s3://somebucket/nginx.conf.webserver.json \
    -V base_domain=@ssm:///config/basedomain
    >/etc/nginx.conf

(Re)generate configuration for all the nginx's vhosts
::

  true >/etc/nginx/conf.d/vhosts.conf && \
  for vhost in vhosts/*.json; do 
    j2rt -t nginx.vhost.conf.j2 -v "$vhost" >>/etc/nginx/conf.d/vhosts.conf
  done && nginx -s reload

Generate .env with production configuration and secrets, taking secrets from (encrypted) S3 bucket.
::

  j2rt \
    -t .env.j2 \
    -v .env.base.json -v .env.prod.json -v s3://somebucket/.env.prod.secrets.json \
    -o .env

Generate OpenVPN client config file, taking CA.crt from S3 bucket, while client certificate and other keys taken from local file system::

  j2rt \
    --template-from /etc/openvpn/client.ovpn.j2 \
    --variables-from /etc/openvpn/base_configuration_subnets_routing_tables_etc.json \
    --variable server_name=TEST_SERVER \
    --variable CA_CRT=@s3://somebucket/ca.crt \
    --variable client_crt=@/path/to/pki/certs/client1.crt \
    --variable client_key=@/path/to/pki/keys/client1.key \
    --variable ta_key=@/etc/openvpn/ta.key \
    -o /root/client1.ovpn
