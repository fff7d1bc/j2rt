import base64


def b64decode(string):
    return base64.b64decode(string.encode('utf8')).decode('utf8')


def b64encode(string):
    return base64.b64encode(string.encode('utf8')).decode('utf8')


custom_filters = {
    'b64decode': b64decode,
    'b64encode': b64encode
}
