#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado


import base64
import copy
import json
import unittest
import uuid
import os
import time

import cogs.test_common

import api


class CogsApiTestCase(cogs.test_common.CogsTestCase):

    def setUp(self):

        # Call Parent
        super(CogsApiTestCase, self).setUp()

        # Set App to Testing Mode
        api.app.testing = True
        api.app.debug = True

        # Create Test Client
        self.app = api.app.test_client()

        # Setup Admin
        self.admin = api.auth.create_user(cogs.test_common.USER_TESTDICT,
                                          username=cogs.test_common.ADMIN_USERNAME,
                                          password=cogs.test_common.ADMIN_PASSWORD,
                                          authmod=cogs.test_common.ADMIN_AUTHMOD)
        self.admin_uuid = str(self.admin.uuid).lower()
        api.auth.add_admins([self.admin_uuid])

    def tearDown(self):

        # Remove User
        self.admin.delete()

        # Call Parent
        super(CogsApiTestCase, self).tearDown()

    ## Auth Helpers ##

    def open_auth(self, method, url, username=None, password=None, **kwargs):

        headers = kwargs.pop('headers', {})

        if username:
            if not password:
                password = ""
            auth_str = "{:s}:{:s}".format(username, password)
            b64_auth_str = base64.b64encode(auth_str)
            key = "Authorization"
            val = "Basic {:s}".format(b64_auth_str)
            headers[key] = val

        return self.app.open(url, method=method, headers=headers, **kwargs)

    def open_user(self, method, url, user=None, **kwargs):

        if user:
            username = user['token']
        else:
            username = None

        return self.open_auth(method, url, username=username, **kwargs)

class CogsApiObjectHelpers(object):

    ## Object Helpers ##

    def create_objects(self, url, key, data, json_data=True, user=None):
        if json_data:
            data = json.dumps(data)
        res = self.open_user('POST', url, user=user, data=data)
        self.assertEqual(res.status_code, 200)
        res_obj = json.loads(res.data)
        self.assertTrue(res_obj)
        res_keys = res_obj.keys()
        self.assertEqual(len(res_keys), 1)
        self.assertEqual(res_keys[0], key)
        res_lst = res_obj[key]
        self.assertGreaterEqual(len(res_lst), 1)
        return set(res_lst)

    def lst_objects(self, url, key, user=None):
        res = self.open_user('GET', url, user=user)
        self.assertEqual(res.status_code, 200)
        res_obj = json.loads(res.data)
        self.assertTrue(res_obj)
        res_keys = res_obj.keys()
        self.assertEqual(len(res_keys), 1)
        self.assertEqual(res_keys[0], key)
        res_lst = res_obj[key]
        return set(res_lst)

    def add_objects(self, url, key, lst, user=None):
        data = json.dumps({str(key): list(lst)})
        res = self.open_user('PUT', url, data=data, user=user)
        self.assertEqual(res.status_code, 200)
        res_obj = json.loads(res.data)
        self.assertTrue(res_obj)
        res_keys = res_obj.keys()
        self.assertEqual(len(res_keys), 1)
        self.assertEqual(res_keys[0], key)
        res_lst = res_obj[key]
        self.assertSubset(set(lst), set(res_lst))
        return set(res_lst)

    def rem_objects(self, url, key, lst, user=None):
        data = json.dumps({str(key): list(lst)})
        res = self.open_user('DELETE', url, data=data, user=user)
        self.assertEqual(res.status_code, 200)
        res_obj = json.loads(res.data)
        self.assertTrue(res_obj)
        res_keys = res_obj.keys()
        self.assertEqual(len(res_keys), 1)
        self.assertEqual(res_keys[0], key)
        res_lst = res_obj[key]
        self.assertTrue((set(lst) - set(res_lst)) == set(lst))
        return set(res_lst)

    def get_object(self, url, obj_uuid, user=None):
        res = self.open_user('GET', '{:s}{:s}/'.format(url, obj_uuid), user=user)
        if (res.status_code == 200):
            self.assertEqual(res.status_code, 200)
            res_obj = json.loads(res.data)
            self.assertTrue(res_obj)
            res_keys = res_obj.keys()
            self.assertEqual(len(res_keys), 1)
            self.assertEqual(res_keys[0], obj_uuid)
            res_hash = res_obj[obj_uuid]
            self.assertTrue(res_hash)
            return res_hash
        elif (res.status_code == 404):
            return None
        else:
            self.fail("Bad HTTP status code {:d}".format(res.status_code))

    def set_object(self, url, obj_uuid, data, json_data=True, user=None):
        if json_data:
            data = json.dumps(data)
        res = self.open_user('PUT', '{:s}{:s}/'.format(url, obj_uuid), user=user, data=data)
        if (res.status_code == 200):
            self.assertEqual(res.status_code, 200)
            res_obj = json.loads(res.data)
            self.assertTrue(res_obj)
            res_keys = res_obj.keys()
            self.assertEqual(len(res_keys), 1)
            self.assertEqual(res_keys[0], obj_uuid)
            res_hash = res_obj[obj_uuid]
            self.assertTrue(res_hash)
            return res_hash
        elif (res.status_code == 404):
            return None
        else:
            self.fail("Bad HTTP status code {:d}".format(res.status_code))

    def delete_object(self, url, obj_uuid, user=None):
        res = self.open_user('DELETE', '{:s}{:s}/'.format(url, obj_uuid), user=user)
        if (res.status_code == 200):
            self.assertEqual(res.status_code, 200)
            res_obj = json.loads(res.data)
            self.assertTrue(res_obj)
            res_keys = res_obj.keys()
            self.assertEqual(len(res_keys), 1)
            self.assertEqual(res_keys[0], obj_uuid)
            res_hash = res_obj[obj_uuid]
            self.assertTrue(res_hash)
            return res_hash
        elif (res.status_code == 404):
            return None
        else:
            self.fail("Bad HTTP status code {:d}".format(res.status_code))

    def list_uuids_test(self, url, key, lst):

        # Get UUID List (Empty)
        uuids_out = self.lst_objects(url, key, user=self.user)
        self.assertEqual(set([]), uuids_out)

        # Add UUID List
        uuids_in = set(lst)
        uuids_out = self.add_objects(url, key, uuids_in, user=self.user)
        self.assertEqual(uuids_in, uuids_out)

        # Get UUID List
        uuids_out = self.lst_objects(url, key, user=self.user)
        self.assertEqual(uuids_in, uuids_out)

        # Delete Some UUIDs
        for i in range(5):
            uuids_rem = set([uuids_in.pop()])
            uuids_out = self.rem_objects(url, key, uuids_rem, user=self.user)
            self.assertEqual(uuids_in, uuids_out)

        # Get UUID List
        uuids_out = self.lst_objects(url, key, user=self.user)
        self.assertEqual(uuids_in, uuids_out)

        # Delete Remaining UUIDs
        uuids_rem = set(uuids_in)
        uuids_in = set([])
        uuids_out = self.rem_objects(url, key, uuids_rem, user=self.user)
        self.assertEqual(uuids_in, uuids_out)

        # Get UUID List
        uuids_out = self.lst_objects(url, key, user=self.user)
        self.assertEqual(uuids_in, uuids_out)


class CogsApiObjectTests(CogsApiObjectHelpers):

    ## Object Tests ##

    def test_create_object(self):

        # Set URLs
        url = getattr(self, 'url', None)
        url_lst = getattr(self, 'url_lst', url)
        url_obj = getattr(self, 'url_obj', url)

        # Create Object
        objs = self.create_objects(url_lst, self.key, self.data,
                                   json_data=self.json_data, user=self.user)
        for obj in objs:
            obj_uuid = uuid.UUID(obj)
            self.assertTrue(obj_uuid)

        # Delete Object
        for obj_uuid in objs:
            obj = self.delete_object(url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

    def test_list_objects(self):

        objects_in = set([])

        # Set URLs
        url = getattr(self, 'url', None)
        url_lst = getattr(self, 'url_lst', url)
        url_obj = getattr(self, 'url_obj', url)

        # Get Object List (Empty)
        objects_out = self.lst_objects(url_lst, self.key, user=self.user)
        self.assertEqual(objects_in, objects_out)

        # Create Objects
        for i in range(10):
            objs = self.create_objects(url_lst, self.key, self.data,
                                       json_data=self.json_data, user=self.user)
            for obj_uuid in objs:
                objects_in.add(obj_uuid)

        # Get Object List
        objects_out = self.lst_objects(url_lst, self.key, user=self.user)
        self.assertEqual(objects_in, objects_out)

        # Delete Some Objects
        for i in range(5):
            obj_uuid = objects_in.pop()
            obj = self.delete_object(url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

        # Get Object List
        objects_out = self.lst_objects(url_lst, self.key, user=self.user)
        self.assertEqual(objects_in, objects_out)

        # Delete Remaining Objects
        for obj_uuid in list(objects_in):
            objects_in.remove(obj_uuid)
            obj = self.delete_object(url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

        # Get Object List
        objects_out = self.lst_objects(url_lst, self.key, user=self.user)
        self.assertEqual(objects_in, objects_out)

    def test_get_object(self):

        # Set URLs
        url = getattr(self, 'url', None)
        url_lst = getattr(self, 'url_lst', url)
        url_obj = getattr(self, 'url_obj', url)

        # Create Object
        objs = self.create_objects(url_lst, self.key, self.data,
                                   json_data=self.json_data, user=self.user)
        for obj_uuid in objs:

            # Get Object
            obj = self.get_object(url_obj, obj_uuid, user=self.user)
            self.assertSubset(self.data, obj)

            # Delete Object
            obj = self.delete_object(url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

    def test_set_object(self):

        # Set URLs
        url = getattr(self, 'url', None)
        url_lst = getattr(self, 'url_lst', url)
        url_obj = getattr(self, 'url_obj', url)

        # Create Object
        objs = self.create_objects(url_lst, self.key, self.data,
                                   json_data=self.json_data, user=self.user)

        for obj_uuid in objs:

            # Update Object
            data = copy.copy(self.data)
            if data:
                for key in data:
                    data[key] = data[key] + "_updated"
                self.assertNotEqual(self.data, data)
            obj = self.set_object(url_obj, obj_uuid, data,
                                  json_data=self.json_data, user=self.user)
            self.assertSubset(data, obj)

            # Get Object
            obj = self.get_object(url_obj, obj_uuid, user=self.user)
            self.assertSubset(data, obj)

            # Delete Object
            obj = self.delete_object(url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

    def test_delete_object(self):

        # Set URLs
        url = getattr(self, 'url', None)
        url_lst = getattr(self, 'url_lst', url)
        url_obj = getattr(self, 'url_obj', url)

        # Create Object
        objs = self.create_objects(url_lst, self.key, self.data,
                                   json_data=self.json_data, user=self.user)

        for obj_uuid in objs:

            # Get Object
            obj = self.get_object(url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

            # Delete Object
            obj = self.delete_object(url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

            # Get Object
            obj = self.get_object(url_lst, obj_uuid, user=self.user)
            self.assertIsNone(obj)


## Root Tests ##
class CogsApiRootTestCase(CogsApiTestCase):

    def setUp(self):
        super(CogsApiRootTestCase, self).setUp()

    def tearDown(self):
        super(CogsApiRootTestCase, self).tearDown()

    def test_root_get(self):
        res = self.open_user('GET', '/', user=self.admin)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data)

## Auth Tests ##
class CogsApiAuthTestCase(CogsApiTestCase):

    def setUp(self):
        super(CogsApiAuthTestCase, self).setUp()

    def tearDown(self):
        super(CogsApiAuthTestCase, self).tearDown()

    def test_token_get(self):
        res = self.open_user('GET', '/tokens/', user=self.admin)
        self.assertEqual(res.status_code, 200)
        res_obj = json.loads(res.data)
        self.assertTrue(res_obj)
        res_keys = res_obj.keys()
        self.assertEqual(len(res_keys), 1)
        token = res_obj['token']
        self.assertEqual(token, self.admin['token'])

## File Tests ##
class CogsApiFileTestCase(CogsApiObjectTests, CogsApiTestCase):

    def setUp(self):
        super(CogsApiFileTestCase, self).setUp()
        self.user = self.admin
        self.url = '/files/'
        self.key = 'files'
        self.file_key = "test"
        self.file_name = "test1.txt"
        self.file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, self.file_name)
        self.data = {self.file_key: (self.file_path, self.file_name)}
        self.json_data = False

    def tearDown(self):
        super(CogsApiFileTestCase, self).tearDown()

    # Override default test_get_object
    def test_get_object(self):

        # Create Object
        obj_uuids = self.create_objects(self.url, self.key, self.data,
                                   json_data=self.json_data, user=self.user)

        for obj_uuid in obj_uuids:

            # Get Object
            obj = self.get_object(self.url, obj_uuid, user=self.user)
            self.assertEqual(self.file_key, obj['key'])
            self.assertEqual(self.file_name, obj['name'])
            self.assertTrue(os.path.exists(obj['path']))
            self.assertEqual(os.path.getsize(obj['path']), os.path.getsize(self.file_path))
            self.assertEqual(str(self.user.uuid), obj['owner'])

            # Delete Object
            obj = self.delete_object(self.url, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)

    # Override default test_set_object
    def test_set_object(self):

        # Create Object
        obj_uuids = self.create_objects(self.url, self.key, self.data,
                                   json_data=self.json_data, user=self.user)

        for obj_uuid in obj_uuids:

            # Update Object (Not Allowed on Files - Should Fail with a 405 Error)
            try:
                obj = self.set_object(self.url, obj_uuid, self.data,
                                      json_data=self.json_data, user=self.user)
            except AssertionError as e:
                if int(str(e).split()[-1]) != 405:
                    raise

            # Delete Object
            obj = self.delete_object(self.url, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)


## Reporter Tests ##
class CogsApiReporterTestCase(CogsApiObjectTests, CogsApiTestCase):

    def setUp(self):
        super(CogsApiReporterTestCase, self).setUp()
        self.user = self.admin
        self.url = '/reporters/'
        self.key = 'reporters'
        self.data = copy.copy(cogs.test_common.REPORTER_TESTDICT)
        self.data['mod'] = "moodle"
        self.data['asn_id'] = cogs.test_common.REPMOD_MOODLE_ASN
        self.json_data = True

    def tearDown(self):
        super(CogsApiReporterTestCase, self).tearDown()


## Assignment Tests ##
class CogsApiAssignmentTestCase(CogsApiObjectTests, CogsApiTestCase):

    def setUp(self):
        super(CogsApiAssignmentTestCase, self).setUp()
        self.user = self.admin
        self.url = '/assignments/'
        self.key = 'assignments'
        self.data = copy.copy(cogs.test_common.ASSIGNMENT_TESTDICT)
        self.json_data = True

    def tearDown(self):
        super(CogsApiAssignmentTestCase, self).tearDown()


## Test Tests ##
class CogsApiTestTestCase(CogsApiObjectTests, CogsApiTestCase):

    def setUp(self):

        # Call Parent
        super(CogsApiTestTestCase, self).setUp()

        # Set User
        self.user = self.admin

        # Create Assignment
        asn_uuids = self.create_objects('/assignments/', 'assignments',
                                        cogs.test_common.ASSIGNMENT_TESTDICT,
                                        json_data=True, user=self.user)
        self.assertEqual(len(asn_uuids), 1)
        self.asn_uuid = asn_uuids.pop()

        # Set Params
        self.url_lst = '/assignments/{:s}/tests/'.format(self.asn_uuid)
        self.url_obj = '/tests/'
        self.key = 'tests'
        self.data = copy.copy(cogs.test_common.TEST_TESTDICT)
        self.json_data = True

    def tearDown(self):

        # Delete Assignment
        self.delete_object('/assignments/', self.asn_uuid, user=self.user)

        # Call Parent
        super(CogsApiTestTestCase, self).tearDown()

    def test_list_uuids_files(self):

        # Create Files
        file_lst = []
        file_key = "test_file"
        file_name = "test1.txt"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, file_name)
        for i in range(10):
            file_uuids = self.create_objects('/files/', 'files',
                                             {file_key: (file_path, file_name)},
                                             json_data=False, user=self.user)
            for file_uuid in file_uuids:
                file_lst.append(file_uuid)

        # Create Test
        tst_uuids = self.create_objects(self.url_lst, self.key,
                                        cogs.test_common.TEST_TESTDICT,
                                        json_data=True, user=self.user)

        for tst_uuid in tst_uuids:

            # Test File List/Add/Remove
            url = '/tests/{:s}/files/'.format(tst_uuid)
            self.list_uuids_test(url, 'files', file_lst)

            # Delete Test
            self.delete_object(self.url_obj, tst_uuid, user=self.user)

            # Delete Files
            for file_uuid in file_lst:
                self.delete_object('/files/', file_uuid, user=self.user)

    def test_list_uuids_reporters(self):

        # Create Reporters
        reporter_lst = []
        reporter_data = copy.copy(cogs.test_common.REPORTER_TESTDICT)
        reporter_data['mod'] = "moodle"
        reporter_data['asn_id'] = cogs.test_common.REPMOD_MOODLE_ASN
        for i in range(10):
            reporter_uuids = self.create_objects('/reporters/', 'reporters',
                                                 data=reporter_data,
                                                 json_data=True, user=self.user)
            for reporter_uuid in reporter_uuids:
                reporter_lst.append(reporter_uuid)

        # Create Test
        tst_uuids = self.create_objects(self.url_lst, self.key,
                                        cogs.test_common.TEST_TESTDICT,
                                        json_data=True, user=self.user)

        for tst_uuid in tst_uuids:

            # Test Reporter List/Add/Remove
            url = '/tests/{:s}/reporters/'.format(tst_uuid)
            self.list_uuids_test(url, 'reporters', reporter_lst)

            # Delete Test
            self.delete_object(self.url_obj, tst_uuid, user=self.user)

            # Delete Reporters
            for reporter_uuid in reporter_lst:
                self.delete_object('/reporters/', reporter_uuid, user=self.user)


## Submission Tests ##
class CogsApiSubmissionTestCase(CogsApiObjectTests, CogsApiTestCase):

    def setUp(self):

        # Call Parent
        super(CogsApiSubmissionTestCase, self).setUp()

        # Set User
        self.user = self.admin

        # Create Assignment
        asn_uuids = self.create_objects('/assignments/', 'assignments',
                                        cogs.test_common.ASSIGNMENT_TESTDICT,
                                        json_data=True, user=self.user)
        self.assertEqual(len(asn_uuids), 1)
        self.asn_uuid = asn_uuids.pop()

        # Set Params
        self.url_lst = '/assignments/{:s}/submissions/'.format(self.asn_uuid)
        self.url_obj = '/submissions/'
        self.key = 'submissions'
        self.data = copy.copy(cogs.test_common.SUBMISSION_TESTDICT)
        self.json_data = True

    def tearDown(self):

        # Delete Assignment
        self.delete_object('/assignments/', self.asn_uuid, user=self.user)

        # Call Parent
        super(CogsApiSubmissionTestCase, self).tearDown()

    def test_list_uuids_files(self):

        # Create Files
        file_lst = []
        file_key = "test_file"
        file_name = "test1.txt"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, file_name)
        for i in range(10):
            file_uuids = self.create_objects('/files/', 'files',
                                             {file_key: (file_path, file_name)},
                                             json_data=False, user=self.user)
            for file_uuid in file_uuids:
                file_lst.append(file_uuid)

        # Create Submission
        sub_uuids = self.create_objects(self.url_lst, self.key,
                                        cogs.test_common.SUBMISSION_TESTDICT,
                                        json_data=True, user=self.user)

        for sub_uuid in sub_uuids:

            # Test File List/Add/Remove
            url = '/submissions/{:s}/files/'.format(sub_uuid)
            self.list_uuids_test(url, 'files', file_lst)

            # Delete Submission
            self.delete_object(self.url_obj, sub_uuid, user=self.user)

            # Delete Files
            for file_uuid in file_lst:
                self.delete_object('/files/', file_uuid, user=self.user)


## Run Tests Base ##
class CogsApiRunBase(CogsApiObjectHelpers, CogsApiTestCase):

    def setUp(self):

        # Call Parent
        super(CogsApiRunBase, self).setUp()

        # Setup Moodle Student
        self.student = api.auth.create_user(cogs.test_common.USER_TESTDICT,
                                            username=cogs.test_common.AUTHMOD_MOODLE_STUDENT_USERNAME,
                                            password=cogs.test_common.AUTHMOD_MOODLE_STUDENT_PASSWORD,
                                            authmod='moodle')

        # Create Assignment
        self.asn_key = 'assignments'
        self.asn_url = "/{:s}/".format(self.asn_key)
        asn_uuids = self.create_objects(self.asn_url, self.asn_key,
                                        cogs.test_common.ASSIGNMENT_TESTDICT,
                                        json_data=True, user=self.admin)
        self.assertEqual(len(asn_uuids), 1)
        self.asn_uuid = asn_uuids.pop()

        # Create Test
        self.tst_key = 'tests'
        self.tst_url = "/{:s}/{:s}/{:s}/".format(self.asn_key, self.asn_uuid, self.tst_key)
        tst_uuids = self.create_objects(self.tst_url, self.tst_key,
                                        cogs.test_common.TEST_TESTDICT,
                                        json_data=True, user=self.admin)
        self.assertEqual(len(tst_uuids), 1)
        self.tst_uuid = tst_uuids.pop()

        # Create Submission
        self.sub_key = 'submissions'
        self.sub_url = "/{:s}/{:s}/{:s}/".format(self.asn_key, self.asn_uuid, self.sub_key)
        # Set Submit Permissions to Any
        api.auth.add_allowed_groups('POST', self.sub_url, [api.cogs.auth.SPECIAL_GROUP_ANY])
        sub_uuids = self.create_objects(self.sub_url, self.sub_key,
                                        cogs.test_common.SUBMISSION_TESTDICT,
                                        json_data=True, user=self.student)
        self.assertEqual(len(sub_uuids), 1)
        self.sub_uuid = sub_uuids.pop()

        # Set Params
        self.key = 'runs'
        self.url_lst = '/{:s}/{:s}/{:s}/'.format(self.sub_key, self.sub_uuid, self.key)
        self.url_obj = '/{:s}/'.format(self.key)
        self.data = copy.copy(cogs.test_common.RUN_TESTDICT)
        self.data['test'] = self.tst_uuid
        self.json_data = True

    def tearDown(self):

        # Delete Submission
        url = "/{:s}/".format(self.sub_key)
        self.delete_object(url, self.sub_uuid, user=self.student)

        # Delete Test
        url = "/{:s}/".format(self.tst_key)
        self.delete_object(url, self.tst_uuid, user=self.admin)

        # Delete Assignment
        url = "/{:s}/".format(self.asn_key)
        self.delete_object(url, self.asn_uuid, user=self.admin)

        # Delete Student
        self.student.delete()

        # Call Parent
        super(CogsApiRunBase, self).tearDown()


## Run Tests ##
class CogsApiRunTestCase(CogsApiObjectTests, CogsApiRunBase):

    def setUp(self):

        # Call Parent
        super(CogsApiRunTestCase, self).setUp()

        # Set Default User
        self.user = self.admin

    def tearDown(self):

        # Call Parent
        super(CogsApiRunTestCase, self).tearDown()

    # Override default test_set_object
    def test_set_object(self):

        # Create Object
        obj_uuids = self.create_objects(self.url_lst, self.key, self.data,
                                        json_data=self.json_data, user=self.user)

        for obj_uuid in obj_uuids:

            # Update Object (Not Allowed on Runs - Should Fail with a 405 Error)
            try:
                obj = self.set_object(self.url_obj, obj_uuid, self.data,
                                      json_data=self.json_data, user=self.user)
            except AssertionError as e:
                if int(str(e).split()[-1]) != 405:
                    raise

            # Delete Object
            obj = self.delete_object(self.url_obj, obj_uuid, user=self.user)
            self.assertIsNotNone(obj)


## Run Execute Tests ##
class CogsApiRunExecuteTestCase(CogsApiRunBase):

    def setUp(self):

        # Call Parent
        super(CogsApiRunExecuteTestCase, self).setUp()

        # Setup Reporter and Attach to Test
        data = copy.copy(cogs.test_common.REPORTER_TESTDICT)
        data['mod'] = "moodle"
        data['asn_id'] = cogs.test_common.REPMOD_MOODLE_ASN
        self.rpt_key = 'reporters'
        self.rpt_url = "/{:s}/".format(self.rpt_key)
        rpt_uuids = self.create_objects(self.rpt_url, self.rpt_key, data,
                                        json_data=True, user=self.admin)
        self.assertEqual(len(rpt_uuids), 1)
        self.rpt_uuid = rpt_uuids.pop()
        url = '/{:s}/{:s}/{:s}/'.format(self.tst_key, self.tst_uuid, self.rpt_key)
        self.add_objects(url, self.rpt_key, [self.rpt_uuid], user=self.admin)

        # Set File Permissions to Any
        api.auth.add_allowed_groups('POST', '/files/', [api.cogs.auth.SPECIAL_GROUP_ANY])

    def tearDown(self):

        # Delete Reporter
        url = "/{:s}/".format(self.rpt_key)
        self.delete_object(url, self.rpt_uuid, user=self.admin)

        # Call Parent
        super(CogsApiRunExecuteTestCase, self).tearDown()

    def test_run_script_good(self):

        # Update Test
        data = copy.copy(cogs.test_common.TEST_TESTDICT)
        data['tester'] = 'script'
        tst = self.set_object('/tests/', self.tst_uuid, data,
                              json_data=True, user=self.admin)
        self.assertTrue(tst)

        # Upload Script File and Attach to Test
        file_key = "script"
        file_name = "grade_add_args.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, file_name)
        url = '/files/'
        fle_uuids_script = self.create_objects(url, 'files',
                                               {file_key: (file_path, file_name)},
                                               json_data=False, user=self.admin)
        self.assertEqual(len(fle_uuids_script), 1)
        fle_uuid_script = fle_uuids_script.pop()
        self.assertTrue(fle_uuid_script)
        url = '/tests/{:s}/files/'.format(self.tst_uuid)
        fle_lst_tst = self.add_objects(url, 'files', [fle_uuid_script], user=self.admin)
        self.assertTrue(fle_lst_tst)

        # Upload Submission File and Attach to Submission
        file_key = "submission"
        file_name = "add.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, "add_good.py")
        url = '/files/'
        fle_uuids_sub = self.create_objects(url, 'files',
                                            {file_key: (file_path, file_name)},
                                            json_data=False, user=self.student)
        self.assertEqual(len(fle_uuids_sub), 1)
        fle_uuid_sub = fle_uuids_sub.pop()
        self.assertTrue(fle_uuid_sub)
        url = '/submissions/{:s}/files/'.format(self.sub_uuid)
        fle_lst_sub = self.add_objects(url, 'files', [fle_uuid_sub], user=self.student)
        self.assertTrue(fle_lst_sub)

        # Create Run
        run_uuids = self.create_objects(self.url_lst, self.key, self.data,
                                        json_data=self.json_data, user=self.student)

        for run_uuid in run_uuids:

            # Wait for Run Completion
            run = None
            status = ""
            while not status.startswith('complete'):
                run = self.get_object(self.url_obj, run_uuid, user=self.student)
                self.assertTrue(run)
                self.assertTrue(run['status'])
                status = run['status']
                time.sleep(1)

            # Check Object
            try:
                self.assertEqual(run['status'], 'complete')
                self.assertEqual(int(run['retcode']), 0)
                self.assertEqual(float(run['score']), 10)
                self.assertTrue(run['output'])
            except AssertionError:
                print("run = {:s}".format(run))
                raise

            # Delete Run
            run = self.delete_object(self.url_obj, run_uuid, user=self.student)
            self.assertIsNotNone(run)

        # Delete Submission File
        fle_sub = self.delete_object('/files/', fle_uuid_sub, user=self.student)
        self.assertIsNotNone(fle_sub)

        # Delete Script File
        fle_script = self.delete_object('/files/', fle_uuid_script, user=self.admin)
        self.assertIsNotNone(fle_script)

    def test_run_script_bad(self):

        # Update Test
        data = copy.copy(cogs.test_common.TEST_TESTDICT)
        data['tester'] = 'script'
        tst = self.set_object('/tests/', self.tst_uuid, data,
                              json_data=True, user=self.admin)
        self.assertTrue(tst)

        # Upload Script File and Attach to Test
        file_key = "script"
        file_name = "grade_add_args.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, file_name)
        url = '/files/'
        fle_uuids_script = self.create_objects(url, 'files',
                                              {file_key: (file_path, file_name)},
                                              json_data=False, user=self.admin)
        self.assertEqual(len(fle_uuids_script), 1)
        fle_uuid_script = fle_uuids_script.pop()
        self.assertTrue(fle_uuid_script)
        url = '/tests/{:s}/files/'.format(self.tst_uuid)
        fle_lst_tst = self.add_objects(url, 'files', [fle_uuid_script], user=self.admin)
        self.assertTrue(fle_lst_tst)

        # Upload Submission File and Attach to Submission
        file_key = "submission"
        file_name = "add.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, "add_bad.py")
        url = '/files/'
        fle_uuids_sub = self.create_objects(url, 'files',
                                           {file_key: (file_path, file_name)},
                                           json_data=False, user=self.student)
        self.assertEqual(len(fle_uuids_sub), 1)
        fle_uuid_sub = fle_uuids_sub.pop()
        self.assertTrue(fle_uuid_sub)
        url = '/submissions/{:s}/files/'.format(self.sub_uuid)
        fle_lst_sub = self.add_objects(url, 'files', [fle_uuid_sub], user=self.student)
        self.assertTrue(fle_lst_sub)

        # Create Run
        run_uuids = self.create_objects(self.url_lst, self.key, self.data,
                                       json_data=self.json_data, user=self.student)

        for run_uuid in run_uuids:

            # Wait for Run Completion
            run = None
            status = ""
            while not status.startswith('complete'):
                run = self.get_object(self.url_obj, run_uuid, user=self.student)
                self.assertTrue(run)
                self.assertTrue(run['status'])
                status = run['status']
                time.sleep(1)

            # Check Object
            try:
                self.assertEqual(run['status'], 'complete')
                self.assertEqual(int(run['retcode']), 0)
                self.assertLess(float(run['score']), 10)
                self.assertTrue(run['output'])
            except AssertionError:
                print("run = {:s}".format(run))
                raise

            # Delete Run
            run = self.delete_object(self.url_obj, run_uuid, user=self.student)
            self.assertIsNotNone(run)

        # Delete Submission File
        fle_sub = self.delete_object('/files/', fle_uuid_sub, user=self.student)
        self.assertIsNotNone(fle_sub)

        # Delete Script File
        fle_script = self.delete_object('/files/', fle_uuid_script, user=self.admin)
        self.assertIsNotNone(fle_script)

    def test_run_io_good(self):

        # Update Test
        data = copy.copy(cogs.test_common.TEST_TESTDICT)
        data['tester'] = 'io'
        tst = self.set_object('/tests/', self.tst_uuid, data,
                              json_data=True, user=self.admin)
        self.assertTrue(tst)

        # Upload Solution File and Attach to Test
        file_key = "solution"
        file_name = "add.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, "add_good.py")
        url = '/files/'
        fle_uuids_sol = self.create_objects(url, 'files',
                                           {file_key: (file_path, file_name)},
                                           json_data=False, user=self.admin)
        self.assertEqual(len(fle_uuids_sol), 1)
        fle_uuid_sol = fle_uuids_sol.pop()
        self.assertTrue(fle_uuid_sol)
        url = '/tests/{:s}/files/'.format(self.tst_uuid)
        fle_lst = self.add_objects(url, 'files', [fle_uuid_sol], user=self.admin)
        self.assertTrue(fle_lst)

        # Upload Input File
        file_key = "input"
        file_name = "add_input1.txt"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, file_name)
        url = '/files/'
        fle_uuids_in1 = self.create_objects(url, 'files',
                                           {file_key: (file_path, file_name)},
                                           json_data=False, user=self.admin)
        self.assertEqual(len(fle_uuids_in1), 1)
        fle_uuid_in1 = fle_uuids_in1.pop()
        self.assertTrue(fle_uuid_in1)
        url = '/tests/{:s}/files/'.format(self.tst_uuid)
        fle_lst = self.add_objects(url, 'files', [fle_uuid_in1], user=self.admin)
        self.assertTrue(fle_lst)

        # Upload Submission File and Attach to Submission
        file_key = "submission"
        file_name = "add.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, "add_good.py")
        url = '/files/'
        fle_uuids_sub = self.create_objects(url, 'files',
                                           {file_key: (file_path, file_name)},
                                           json_data=False, user=self.student)
        self.assertEqual(len(fle_uuids_sub), 1)
        fle_uuid_sub = fle_uuids_sub.pop()
        self.assertTrue(fle_uuid_sub)
        url = '/submissions/{:s}/files/'.format(self.sub_uuid)
        fle_lst_sub = self.add_objects(url, 'files', [fle_uuid_sub], user=self.student)
        self.assertTrue(fle_lst_sub)

        # Create Run
        run_uuids = self.create_objects(self.url_lst, self.key, self.data,
                                       json_data=self.json_data, user=self.student)

        for run_uuid in run_uuids:

            # Wait for Run Completion
            run = None
            status = ""
            while not status.startswith('complete'):
                run = self.get_object(self.url_obj, run_uuid, user=self.student)
                self.assertTrue(run)
                self.assertTrue(run['status'])
                status = run['status']
                time.sleep(1)

            # Check Object
            try:
                self.assertEqual(run['status'], 'complete')
                self.assertEqual(int(run['retcode']), 0)
                self.assertEqual(float(run['score']), 10)
                self.assertTrue(run['output'])
            except AssertionError:
                print("run = {:s}".format(run))
                raise

            # Delete Run
            run = self.delete_object(self.url_obj, run_uuid, user=self.student)
            self.assertIsNotNone(run)

        # Delete Submission
        fle_sub = self.delete_object('/files/', fle_uuid_sub, user=self.student)
        self.assertIsNotNone(fle_sub)

        # Delete Input
        fle_in1 = self.delete_object('/files/', fle_uuid_in1, user=self.admin)
        self.assertIsNotNone(fle_sub)

        # Delete Solution
        fle_sol = self.delete_object('/files/', fle_uuid_sol, user=self.admin)
        self.assertIsNotNone(fle_sol)

    def test_run_io_bad(self):

        # Update Test
        data = copy.copy(cogs.test_common.TEST_TESTDICT)
        data['tester'] = 'io'
        tst = self.set_object('/tests/', self.tst_uuid, data,
                              json_data=True, user=self.admin)
        self.assertTrue(tst)

        # Upload Solution File and Attach to Test
        file_key = "solution"
        file_name = "add.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, "add_good.py")
        url = '/files/'
        fle_uuids_sol = self.create_objects(url, 'files',
                                           {file_key: (file_path, file_name)},
                                           json_data=False, user=self.admin)
        self.assertEqual(len(fle_uuids_sol), 1)
        fle_uuid_sol = fle_uuids_sol.pop()
        self.assertTrue(fle_uuid_sol)
        url = '/tests/{:s}/files/'.format(self.tst_uuid)
        fle_lst = self.add_objects(url, 'files', [fle_uuid_sol], user=self.admin)
        self.assertTrue(fle_lst)

        # Upload Input File
        file_key = "input"
        file_name = "add_input1.txt"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, file_name)
        url = '/files/'
        fle_uuids_in1 = self.create_objects(url, 'files',
                                           {file_key: (file_path, file_name)},
                                           json_data=False, user=self.admin)
        self.assertEqual(len(fle_uuids_in1), 1)
        fle_uuid_in1 = fle_uuids_in1.pop()
        self.assertTrue(fle_uuid_in1)
        url = '/tests/{:s}/files/'.format(self.tst_uuid)
        fle_lst = self.add_objects(url, 'files', [fle_uuid_in1], user=self.admin)
        self.assertTrue(fle_lst)

        # Upload Submission File and Attach to Submission
        file_key = "submission"
        file_name = "add.py"
        file_path = "{:s}/{:s}".format(cogs.test_common.TEST_INPUT_PATH, "add_bad.py")
        url = '/files/'
        fle_uuids_sub = self.create_objects(url, 'files',
                                           {file_key: (file_path, file_name)},
                                           json_data=False, user=self.student)
        self.assertEqual(len(fle_uuids_sub), 1)
        fle_uuid_sub = fle_uuids_sub.pop()
        self.assertTrue(fle_uuid_sub)
        url = '/submissions/{:s}/files/'.format(self.sub_uuid)
        fle_lst_sub = self.add_objects(url, 'files', [fle_uuid_sub], user=self.student)
        self.assertTrue(fle_lst_sub)

        # Create Run
        run_uuids = self.create_objects(self.url_lst, self.key, self.data,
                                       json_data=self.json_data, user=self.student)

        for run_uuid in run_uuids:

            # Wait for Run Completion
            run = None
            status = ""
            while not status.startswith('complete'):
                run = self.get_object(self.url_obj, run_uuid, user=self.student)
                self.assertTrue(run)
                self.assertTrue(run['status'])
                status = run['status']
                time.sleep(1)

            # Check Object
            try:
                self.assertEqual(run['status'], 'complete')
                self.assertEqual(int(run['retcode']), 0)
                self.assertLess(float(run['score']), 10)
                self.assertTrue(run['output'])
            except AssertionError:
                print("run = {:s}".format(run))
                raise

            # Delete Run
            run = self.delete_object(self.url_obj, run_uuid, user=self.student)
            self.assertIsNotNone(run)

        # Delete Submission
        fle_sub = self.delete_object('/files/', fle_uuid_sub, user=self.student)
        self.assertIsNotNone(fle_sub)

        # Delete Input
        fle_in1 = self.delete_object('/files/', fle_uuid_in1, user=self.admin)
        self.assertIsNotNone(fle_sub)

        # Delete Solution
        fle_sol = self.delete_object('/files/', fle_uuid_sol, user=self.admin)
        self.assertIsNotNone(fle_sol)


### Main ###
if __name__ == '__main__':
    unittest.main()
