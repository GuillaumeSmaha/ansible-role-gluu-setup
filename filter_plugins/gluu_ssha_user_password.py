#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}

DOCUMENTATION = '''
---
filter: gluu_ssha_user_password
author: "Guillaume Smaha"
short_description: Filter to hash password with salt (SSHA in ldap)
description:
Filter to encrypt password
author:
  - Guillaume Smaha
options:
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
      {{ user | gluu_ssha_user_password(
          key='password') }}
    - name: Encrypt password
      {{ password | gluu_ssha_user_password(
          key='key_to_crypt') }}
'''


from ansible import errors
from ansible.module_utils.basic import *
import os
import base64


class FilterModule(object):
    def filters(self):
        return {
            'gluu_ssha_user_password': self.gluu_ssha_user_password
        }

    def gluu_ssha_user_password(self, content, key=None, ignore_notfound=False, *args, **kw):

        if isinstance(content, dict):
            return self.gluu_ssha_user_password_dict(content, key, ignore_notfound)
        elif isinstance(content, str):
            return self.gluu_ssha_user_password_str(content)

        return content

    def gluu_ssha_user_password_dict(self, content, key, ignore_notfound):
        if key not in content:
            if ignore_notfound:
                return content
            raise errors.AnsibleFilterError(
                '[gluu_ssha_user_password] key is required for an input dict.')

        content[key] = self.encrypt(content[key])

        return content

    def gluu_ssha_user_password_str(self, content):

        return self.encrypt(content)

    def encrypt(self, password):
        password = password.encode('ascii')
        salt = os.urandom(4)
        sha_password = hashlib.sha1(password)
        sha_password.update(salt)
        sha_digest = sha_password.digest()
        password_salted = sha_digest + salt
        b64encoded = base64.b64encode(password_salted).strip().decode('ascii')
        return '{SSHA}' + b64encoded
