#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado

import copy
import unittest

import structs
import test_common


class TypesTestCase(test_common.CogsTestCase):

    def setUp(self):
        super(TypesTestCase, self).setUp()

    def tearDown(self):
        super(TypesTestCase, self).tearDown()

    def subHashDirectHelper(self, hash_create, hash_list, input_dict):

        objects_in = set([])

        # List Objects (Empty DB)
        objects_out = hash_list()
        self.assertEqual(objects_in, objects_out)

        # Generate 10 Objects
        for i in range(10):
            d = copy.copy(input_dict)
            for k in d:
                d[k] = "{:s}_test_{:02d}".format(d[k], i)
            objects_in.add(str(hash_create(d).obj_key))

        # List Objects
        objects_out = hash_list()
        self.assertEqual(objects_in, objects_out)

    def hashCreateHelper(self, hash_create, input_dict):

        # Test Empty Dict
        d = {}
        self.assertRaises(KeyError, hash_create, d)

        # Test Bad Dict
        d = {'badkey': "test"}
        self.assertRaises(KeyError, hash_create, d)

        # Test Sub Dict
        d = copy.copy(input_dict)
        d.pop(d.keys()[0])
        self.assertRaises(KeyError, hash_create, d)

        # Test Super Dict
        d = copy.copy(input_dict)
        d['badkey'] = "test"
        self.assertRaises(KeyError, hash_create, d)

    def hashGetHelper(self, hash_create, hash_get, input_dict):

        # Test Invalid UUID
        self.assertRaises(structs.ObjectDNE,
                          hash_get,
                          'eb424026-6f54-4ef8-a4d0-bb658a1fc6cf')

        # Test Valid UUID
        d = copy.copy(input_dict)
        obj1 = hash_create(d)
        obj1_key = obj1.obj_key
        obj2 = hash_get(obj1_key)
        self.assertEqual(obj1, obj2)
        self.assertEqual(obj1.get_dict(), obj2.get_dict())


class ServerTestCase(TypesTestCase):

    def setUp(self):
        super(ServerTestCase, self).setUp()
        self.srv = structs.Server(db=self.db)

    def tearDown(self):
        del(self.srv)
        super(ServerTestCase, self).tearDown()

    def test_assignments(self):
        self.subHashDirectHelper(self.srv.create_assignment,
                                 self.srv.list_assignments,
                                 test_common.ASSIGNMENT_TESTDICT)

    def test_users(self):
        self.subHashDirectHelper(self.srv.create_user,
                                 self.srv.list_users,
                                 test_common.USER_TESTDICT)


class UserTestCase(TypesTestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()
        self.srv = structs.Server(self.db)

    def tearDown(self):
        super(UserTestCase, self).tearDown()

    def test_create_user(self):
        self.hashCreateHelper(self.srv.create_user,
                              test_common.USER_TESTDICT)

    def test_get_user(self):
        self.hashGetHelper(self.srv.create_user,
                           self.srv.get_user,
                           test_common.USER_TESTDICT)


class AssignmentTestCase(TypesTestCase):

    def setUp(self):
        super(AssignmentTestCase, self).setUp()
        self.srv = structs.Server(self.db)

    def tearDown(self):
        super(AssignmentTestCase, self).tearDown()

    def test_create_assignment(self):
        self.hashCreateHelper(self.srv.create_assignment,
                              test_common.ASSIGNMENT_TESTDICT)

    def test_get_assignment(self):
        self.hashGetHelper(self.srv.create_assignment,
                           self.srv.get_assignment,
                           test_common.ASSIGNMENT_TESTDICT)


class TestTestCase(TypesTestCase):

    def setUp(self):
        super(TestTestCase, self).setUp()
        self.srv = structs.Server(self.db)
        self.asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)

    def tearDown(self):
        super(TestTestCase, self).tearDown()

    def test_create_test(self):
        self.hashCreateHelper(self.asn.create_test,
                              test_common.TEST_TESTDICT)

    def test_get_test(self):
        self.hashGetHelper(self.asn.create_test,
                           self.asn.get_test,
                           test_common.TEST_TESTDICT)


# Main
if __name__ == '__main__':
    unittest.main()
