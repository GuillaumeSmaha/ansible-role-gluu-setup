#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}


DOCUMENTATION = '''
---
filter: gluu_encrypt_password
author: "Guillaume Smaha"
short_description: Filter to encrypt password
description:
Filter to encrypt password
author:
  - Guillaume Smaha
options:
    name: secret
        required: true
        description: Key to crypt password
    name: key
        required: false
        description: Key to find the value in the input dict
    name: ignore_notfound
        required: false
        description: Ignore error if key is not found
'''

EXAMPLES = '''
---
- hosts: all
  gather_facts: no
  become: no

  tasks:
    - name: Encrypt password on user
      {{ user | gluu_encrypt_password(
          key='password', secret='key_to_crypt') }}
    - name: Encrypt password
      {{ password | gluu_encrypt_password(
          key='key_to_crypt', secret='secret_to_crypt') }}
'''

from ansible import errors
from ansible.module_utils.six import string_types
import base64
from pyDes import triple_des, ECB, PAD_PKCS5


class FilterModule(object):
    def filters(self):
        return {
            'gluu_encrypt_password': self.gluu_encrypt_password
        }

    def gluu_encrypt_password(self, content, secret=None, key=None, ignore_notfound=False, *args, **kw):

        if not secret:
            raise errors.AnsibleFilterError(
                '[gluu_encrypt_password] secret is required.')

        if isinstance(content, dict):
            return self.gluu_encrypt_password_dict(content, key, secret, ignore_notfound)
        elif isinstance(content, string_types):
            return self.gluu_encrypt_password_str(content, secret)

        return content

    def gluu_encrypt_password_dict(self, content, key, secret, ignore_notfound):
        if key not in content:
            if ignore_notfound:
                return content
            raise errors.AnsibleFilterError(
                '[gluu_encrypt_password] key is required for an input dict.')

        content[key] = self.encrypt(secret, content[key])

        return content

    def gluu_encrypt_password_str(self, content, secret):

        return self.encrypt(secret, content)

    def encrypt(self, key, password):
        key = self.key_padding(key.encode('ascii'))
        password = password.encode('ascii')

        deskey = triple_des(key, ECB, "\0\0\0\0\0\0\0\0",
                            pad=None, padmode=PAD_PKCS5)
        result = deskey.encrypt(password)

        return bytes.decode(base64.b64encode(result))

    def decrypt(self, key, password):
        key = self.key_padding(key.encode('ascii'))
        password = password.encode('ascii')

        deskey = triple_des(key, ECB, "\0\0\0\0\0\0\0\0",
                            pad=None, padmode=PAD_PKCS5)
        result = deskey.decrypt(password)

        return result.strip("\2")

    def key_padding(self, key):
        len_key = len(key)
        if len_key < 16:
            key = key + "\2" * (16 - len_key)
        elif len_key < 24:
            key = key + "\2" * (24 - len_key)
        else:
            key = key[:24]

        return key
