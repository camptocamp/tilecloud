# FIXME port to requests

import UserDict
from base64 import b64encode
from datetime import datetime
import errno
import hashlib
import hmac
import httplib
from itertools import imap
import logging
from operator import itemgetter
import os
import re
import ssl
from urlparse import urlparse
import xml.etree.cElementTree as ElementTree


NAMESPACE_REPLACEMENT = r'{http://s3.amazonaws.com/doc/2006-03-01/}\1'
logger = logging.getLogger(__name__)


def namespacify(s):
    return re.sub(r'(\w+)', NAMESPACE_REPLACEMENT, s)


def parse_timestamp(s):
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})T' +
                     r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})Z\Z', s)
    return datetime(*map(int, match.groups()))


class HeaderDict(UserDict.DictMixin):
    """A dict for HTTP headers"""

    def __init__(self, items=None):
        if items is None:
            self.items = {}
        elif isinstance(items, dict):
            self.items = dict((k.lower(), (k, v))
                              for k, v in items.iteritems())
        else:
            self.items = dict((k.lower(), (k, v)) for k, v in items)

    def __contains__(self, key):
        return key.lower() in self.items

    def __delitem__(self, key):
        del self.items[key.lower()]

    def __getitem__(self, key):
        return self.items[key.lower()][1]

    def __iter__(self):
        return imap(itemgetter(0), self.items.itervalues())

    def __len__(self):
        return len(self.items)

    def __setitem__(self, key, value):
        self.items[key.lower()] = (key, value)

    def iteritems(self):
        return self.items.itervalues()

    def itervalues(self):
        return imap(itemgetter(1), self.items.itervalues())

    def keys(self):
        return list(iter(self))

    def copy(self):
        return self.__class__(self.iteritems())


class S3Error(RuntimeError):

    def __init__(self, method, url, body, headers, response):
        self.method = method
        self.url = url
        self.body = body
        self.headers = headers
        self.response = response
        self.response_body = self.response.read()
        if self.response_body:
            self.etree = ElementTree.fromstring(self.response_body)
            for key in 'Code Error Message RequestId Resource'.split():
                element = self.etree.find(key)
                setattr(self, key.lower(),
                        None if element is None else element.text)
            RuntimeError.__init__(self, '%s: %s' % (self.code, self.message))
        else:
            RuntimeError.__init__(self,
                                  '%d %s' % (self.response.status,
                                             httplib.responses[self.response.status]))


class S3Key(object):

    def __init__(self, name, bucket=None, headers=None, body=None, **kwargs):
        self.name = name
        self.bucket = bucket
        self.headers = HeaderDict() if headers is None else headers
        self.body = body
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __contains__(self, key):
        return key in self.headers

    def __getitem__(self, key):
        return self.headers[key]

    def __setitem__(self, key, value):
        self.headers[key] = value

    def delete(self):
        return self.bucket.delete(self.name, self.headers)

    def get(self):
        return self.bucket.get(self.name, self.headers)

    def head(self):
        return self.bucket.head(self.name, self.headers)

    def put(self):
        return self.bucket.put(self.name, self.headers, self.body)


class S3Bucket(object):

    CONTENTS_PATH = namespacify('Contents')
    ETAG_PATH = namespacify('ETag')
    IS_TRUNCATED_PATH = namespacify('IsTruncated')
    KEY_PATH = namespacify('Key')
    LAST_MODIFIED_PATH = namespacify('LastModified')
    OWNER_DISPLAY_NAME_PATH = namespacify('Owner/DisplayName')
    OWNER_ID_PATH = namespacify('Owner/ID')
    SIZE_PATH = namespacify('Size')
    STORAGE_CLASS_PATH = namespacify('StorageClass')

    def __init__(self, name, connection=None, **kwargs):
        self.name = name
        self.connection = connection
        for key, value in kwargs.items():
            setattr(self, key, value)

    def key(self, key_name):
        return S3Key(key_name, self)

    def delete(self, key_name, headers=None):
        return self.connection.delete(self.name, '/' + key_name, headers)

    def get(self, key_name, headers=None):
        headers, body = self.connection.get(self.name, '/' + key_name, headers)
        return S3Key(key_name, self, headers, body)

    def head(self, key_name, headers=None):
        headers, body = self.connection.head(self.name, '/' + key_name, headers)
        return S3Key(key_name, self, headers)

    def list_objects(self, marker=None, max_keys=None, prefix=None):
        while True:
            query = '&'.join('%s=%s' % (k, v) for k, v in (('marker', marker), ('max-keys', max_keys), ('prefix', prefix)) if v is not None)
            headers, body = self.connection.get(self.name, '/?' + query if query else '/')
            etree = ElementTree.fromstring(body)
            for contents_element in etree.findall(self.CONTENTS_PATH):
                key_name = contents_element.find(self.KEY_PATH).text
                kwargs = {}
                kwargs['last_modified'] = parse_timestamp(contents_element.find(self.LAST_MODIFIED_PATH).text)
                kwargs['etag'] = contents_element.find(self.ETAG_PATH).text
                kwargs['size'] = int(contents_element.find(self.SIZE_PATH).text)
                kwargs['storage_class'] = contents_element.find(self.STORAGE_CLASS_PATH).text
                kwargs['owner_id'] = contents_element.find(self.OWNER_ID_PATH).text
                kwargs['owner_display_name'] = contents_element.find(self.OWNER_DISPLAY_NAME_PATH).text
                yield S3Key(key_name, self, **kwargs)
            if etree.find(self.IS_TRUNCATED_PATH).text == 'true':
                marker = key_name
            else:
                break

    def put(self, key_name, headers=None, body=None):
        return self.connection.put(self.name, '/' + key_name, headers, body)


class S3Connection(object):

    SIGN_IGNORE_HEADERS = set('content-disposition content-encoding content-length content-md5 content-type date host user-agent'.split())

    BUCKETS_BUCKET_PATH = namespacify('Buckets/Bucket')
    CREATION_DATE_PATH = namespacify('CreationDate')
    NAME_PATH = namespacify('Name')

    def __init__(self, host='s3.amazonaws.com',
                 access_key=None, secret_access_key=None):
        self.host = host
        self.access_key = access_key
        if self.access_key is None:
            self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        if self.access_key is None:
            self.access_key = ''
        self.secret_access_key = secret_access_key
        if self.secret_access_key is None:
            self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        if self.secret_access_key is None:
            self.secret_access_key = ''
        self.connection = None

    def bucket(self, bucket_name, **kwargs):
        connection = S3Connection('.'.join((bucket_name, self.host)),
                                  self.access_key,
                                  self.secret_access_key)
        return S3Bucket(bucket_name, connection, **kwargs)

    def buckets(self):
        headers, body = self.get(url='/')
        etree = ElementTree.fromstring(body)
        for bucket_element in etree.findall(self.BUCKETS_BUCKET_PATH):
            bucket_name = bucket_element.find(self.NAME_PATH).text
            kwargs = {}
            kwargs['creation_date'] = \
                parse_timestamp(bucket_element.find(
                    self.CREATION_DATE_PATH).text)
            yield self.bucket(bucket_name, **kwargs)

    def delete(self, bucket_name=None, url=None, headers=None):
        return self.request('DELETE', bucket_name, url, headers)

    def get(self, bucket_name=None, url=None, headers=None):
        return self.request('GET', bucket_name, url, headers)

    def head(self, bucket_name=None, url=None, headers=None):
        return self.request('HEAD', bucket_name, url, headers)

    def put(self, bucket_name=None, url=None, headers=None, body=None):
        headers = HeaderDict() if headers is None else headers.copy()
        if 'Content-MD5' not in headers:
            headers['Content-MD5'] = b64encode(hashlib.md5(body).digest())
        return self.request('PUT', bucket_name, url, body=body, headers=headers)

    def request(self, method, bucket_name=None, url=None, headers=None,
                body=None, sub_resources=None):
        headers = HeaderDict() if headers is None else headers.copy()
        if 'x-amz-date' not in headers:
            headers['x-amz-date'] = \
                datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
        headers['Authorization'] = self.sign(method, bucket_name, url, headers,
                                             sub_resources)
        while True:
            try:
                if self.connection is None:
                    self.connection = httplib.HTTPConnection(self.host)
                self.connection.request(method, url, body, headers)
                response = self.connection.getresponse()
                if response.status not in xrange(200, 300):
                    raise S3Error(method, url, body, headers, response)
                headers = HeaderDict(response.getheaders())
                body = response.read()
                return (headers, body)
            except httplib.BadStatusLine as exc:
                logger.warn(exc)
                self.connection = None
            except httplib.CannotSendRequest as exc:
                logger.warn(exc)
                self.connection = None
            except ssl.SSLError as exc:
                logger.warn(exc)
                self.connection = None
            except IOError as exc:
                if exc.errno == errno.ECONNRESET:
                    logger.warn(exc)
                    self.connection = None
                else:
                    raise

    def sign(self, method, bucket_name=None, url=None, headers=None,
             sub_resources=None):
        headers = HeaderDict() if headers is None else headers.copy()
        string_to_sign = []
        string_to_sign.append('%s\n' % (method,))
        string_to_sign.append('%s\n' % headers.get('content-md5', ('',)))
        string_to_sign.append('%s\n' % headers.get('content-type', ('',)))
        if 'x-amz-date' in headers:
            string_to_sign.append('\n')
        else:
            string_to_sign.append('%s\n' % headers.get('date', ('',)))
        for key in sorted(set(imap(str.lower, headers.keys())) - self.SIGN_IGNORE_HEADERS):
            string_to_sign.append('%s:%s\n' % (key, headers[key]))
        if bucket_name is not None:
            string_to_sign.append('/%s' % (bucket_name,))
        if url is not None:
            string_to_sign.append(urlparse(url).path)
        if sub_resources:
            query_params = []
            for key in sorted(sub_resources.keys()):
                value = sub_resources[key]
                if value is None:
                    query_param = key
                else:
                    query_param = '%s=%s' % (key, value)
                query_params.append(query_param)
            string_to_sign.append('?%s' % ('&'.join(query_params),))
        signature = hmac.new(self.secret_access_key, ''.join(string_to_sign), hashlib.sha1)
        return 'AWS %s:%s' % (self.access_key, b64encode(signature.digest()))
