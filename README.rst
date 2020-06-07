j2rt - Jinja2 rendering tool
============================

j2rt is a tool meant to simplify Jinja2 usage for CLI, be that with shell scripts, continuous integration pipelines or anything else, where `m4` is not a good fit, with all the whistles and bells that Jinja2 offers, if statements, for loops, filters and many more, see Jinja2's `syntax <https://jinja.palletsprojects.com/en/2.11.x/templates/>`_ for list of features. The tool can take template and variable files from local filesystem as well as remote S3. The S3 integration makes it easy to create a secure secrets store for your configuration files, since S3 can be encrypted (KMS or regular server side AES), it's viable to place secrets.json in S3 and then load it during deployment process for the configuration files to be generated, as one of use cases.

Multiple variable files can be used, in a way that one can, for example, specify one base variables file, and then append some keys, or override others, if needed.

Python dependencies
-------------------
- jinja2
- boto3 (only if s3 is used)

Usage
-----

The template and variable file(s) can be either local, or remote s3, if prefixed with s3://. Template is to be written in jinja2 and variable files are to be JSON formatted. One or more variable files can be specified, the same variable can be set in multiple variable files, the last one to be defined will be used.

The help
::

  usage: j2rt [-h] -t TEMPLATE_FROM -v VARIABLES_FROM [VARIABLES_FROM ...] [-o OUTPUT]

  optional arguments:
    -h, --help            show this help message and exit
    -t TEMPLATE_FROM, --template-from TEMPLATE_FROM
                          Path to template file to use
    -v VARIABLES_FROM [VARIABLES_FROM ...], --variables-from VARIABLES_FROM [VARIABLES_FROM ...]
                          The path(s) for JSON files from which variables will be taken
                          from, if variable in file is already defined, it will be
                          overwritten.
    -o OUTPUT, --output OUTPUT
                          Output file, if not set, result is printed to stdout.

Examples
--------

Generate nginx.conf
::

  j2rt \
    -t s3://somebucket/nginx.conf.j2 \
    -v /etc/nginx.conf.base.json s3://somebucket/nginx.conf.webserver.json \
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
    -v .env.base.json .env.prod.json s3://somebucket/.env.prod.secrets.json \
    -o .env
