import base64

try:
    import gnupg
    gpg = gnupg.GPG()
except ImportError:
    pass


def b64decode(string):
    return base64.b64decode(string.encode('utf8')).decode('utf8')


def b64encode(string):
    return base64.b64encode(string.encode('utf8')).decode('utf8')


def gpg_decrypt(string):
    return gpg.decrypt(string).data.decode('utf-8')


custom_filters = {
    'b64decode': b64decode,
    'b64encode': b64encode,
    'gpg_decrypt': gpg_decrypt
}
