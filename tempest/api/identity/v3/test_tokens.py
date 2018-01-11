# Copyright 2015 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_utils import timeutils
import six

from tempest.api.identity import base
from tempest.lib import decorators
from tempest.lib import exceptions as lib_exc


class TokensV3Test(base.BaseIdentityV3Test):

    @decorators.idempotent_id('a9512ac3-3909-48a4-b395-11f438e16260')
    def test_validate_token(self):
        creds = self.os_primary.credentials
        user_id = creds.user_id
        username = creds.username
        password = creds.password
        user_domain_id = creds.user_domain_id
        # GET and validate token
        subject_token, token_body = self.non_admin_token.get_token(
            user_id=user_id,
            username=username,
            user_domain_id=user_domain_id,
            password=password,
            auth_data=True)
        authenticated_token = self.non_admin_client.show_token(
            subject_token)['token']
        # sanity checking to make sure they are indeed the same token
        self.assertEqual(authenticated_token, token_body)
        # test to see if token has been properly authenticated
        self.assertEqual(authenticated_token['user']['id'], user_id)
        self.assertEqual(authenticated_token['user']['name'], username)
        self.non_admin_client.delete_token(subject_token)
        self.assertRaises(
            lib_exc.NotFound, self.non_admin_client.show_token, subject_token)

    @decorators.idempotent_id('6f8e4436-fc96-4282-8122-e41df57197a9')
    def test_create_token(self):

        creds = self.os_primary.credentials
        user_id = creds.user_id
        username = creds.username
        password = creds.password
        user_domain_id = creds.user_domain_id

        # 'user_domain_id' needs to be specified otherwise tempest.lib assumes
        # it to be 'default'
        token_id, resp = self.non_admin_token.get_token(
            user_id=user_id,
            username=username,
            user_domain_id=user_domain_id,
            password=password,
            auth_data=True)

        self.assertNotEmpty(token_id)
        self.assertIsInstance(token_id, six.string_types)

        now = timeutils.utcnow()
        expires_at = timeutils.normalize_time(
            timeutils.parse_isotime(resp['expires_at']))
        self.assertGreater(resp['expires_at'],
                           resp['issued_at'])
        self.assertGreater(expires_at, now)

        subject_id = resp['user']['id']
        if user_id:
            self.assertEqual(subject_id, user_id)
        else:
            # Expect a user ID, but don't know what it will be.
            self.assertIsNotNone(subject_id, 'Expected user ID in token.')

        subject_name = resp['user']['name']
        if username:
            self.assertEqual(subject_name, username)
        else:
            # Expect a user name, but don't know what it will be.
            self.assertIsNotNone(subject_name, 'Expected user name in token.')

        self.assertEqual(resp['methods'][0], 'password')
