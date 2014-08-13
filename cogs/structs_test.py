#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado

import copy
import unittest
import werkzeug
import os
import time

os.environ['COGS_REDIS_HOST'] = "localhost"
os.environ['COGS_REDIS_PORT'] = str(6379)
os.environ['COGS_REDIS_DB'] = str(5)

import structs

import test_common
import test_common_backend


class StructsTestCase(test_common.CogsTestCase):

    def setUp(self):

        # Call Parent
        super(StructsTestCase, self).setUp()

        # Setup Server
        self.srv = structs.Server()

    def tearDown(self):

        # Cleanup Server
        self.srv.close()

        # Call parent
        super(StructsTestCase, self).tearDown()


class ServerTestCase(test_common_backend.SubMixin,
                     StructsTestCase):

    def setUp(self):
        super(ServerTestCase, self).setUp()

    def tearDown(self):
        super(ServerTestCase, self).tearDown()

    def test_files(self):
        src_file = open("./Makefile", 'rb')
        file_obj = werkzeug.datastructures.FileStorage(stream=src_file, filename="Makefile")
        self.subHashDirectHelper(self.srv.create_file,
                                 self.srv.get_file,
                                 self.srv.list_files,
                                 test_common.FILE_TESTDICT,
                                 extra_kwargs={'file_obj': file_obj, 'owner': })
        file_obj.close()

    def test_assignments(self):
        self.subHashDirectHelper(self.srv.create_assignment,
                                 self.srv.get_assignment,
                                 self.srv.list_assignments,
                                 test_common.ASSIGNMENT_TESTDICT)

    def test_asn_tests(self):
        asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)
        self.subHashDirectHelper(asn.create_test,
                                 self.srv.get_test,
                                 asn.list_tests,
                                 test_common.TEST_TESTDICT)
        asn.delete()

    def test_srv_tests(self):
        asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)
        self.subHashDirectHelper(asn.create_test,
                                 self.srv.get_test,
                                 self.srv.list_tests,
                                 test_common.TEST_TESTDICT)
        asn.delete()

    def test_asn_submissions(self):
        asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)
        self.subHashDirectHelper(asn.create_submission,
                                 self.srv.get_submission,
                                 asn.list_submissions,
                                 test_common.SUBMISSION_TESTDICT)
        asn.delete()

    def test_srv_submissions(self):
        asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)
        self.subHashDirectHelper(asn.create_submission,
                                 self.srv.get_submission,
                                 self.srv.list_submissions,
                                 test_common.SUBMISSION_TESTDICT)
        asn.delete()


class FileTestCase(test_common_backend.UUIDHashMixin,
                   StructsTestCase):

    def setUp(self):
        super(FileTestCase, self).setUp()
        src_file = open("./Makefile", 'rb')
        self.file_obj = werkzeug.datastructures.FileStorage(stream=src_file, filename="Makefile")

    def tearDown(self):
        self.file_obj.close()
        super(FileTestCase, self).tearDown()

    def test_create_file(self):
        self.hashCreateHelper(self.srv.create_file,
                              test_common.FILE_TESTDICT,
                              extra_kwargs={'file_obj': self.file_obj})

    def test_get_file(self):
        self.hashGetHelper(self.srv.create_file,
                           self.srv.get_file,
                           test_common.FILE_TESTDICT,
                              extra_kwargs={'file_obj': self.file_obj})

    def test_update_file(self):
        self.hashUpdateHelper(self.srv.create_file,
                              test_common.FILE_TESTDICT,
                              extra_kwargs={'file_obj': self.file_obj})

    def test_delete_file(self):
        self.hashDeleteHelper(self.srv.create_file,
                              test_common.FILE_TESTDICT,
                              extra_kwargs={'file_obj': self.file_obj})


class AssignmentTestCase(test_common_backend.UUIDHashMixin,
                         StructsTestCase):

    def setUp(self):
        super(AssignmentTestCase, self).setUp()

    def tearDown(self):
        super(AssignmentTestCase, self).tearDown()

    def test_create_assignment(self):
        self.hashCreateHelper(self.srv.create_assignment,
                              test_common.ASSIGNMENT_TESTDICT)

    def test_get_assignment(self):
        self.hashGetHelper(self.srv.create_assignment,
                           self.srv.get_assignment,
                           test_common.ASSIGNMENT_TESTDICT)

    def test_update_assignment(self):
        self.hashUpdateHelper(self.srv.create_assignment,
                              test_common.ASSIGNMENT_TESTDICT)

    def test_delete_assignment(self):
        self.hashDeleteHelper(self.srv.create_assignment,
                              test_common.ASSIGNMENT_TESTDICT)


class TestTestCase(test_common_backend.SubMixin,
                   test_common_backend.UUIDHashMixin,
                   StructsTestCase):

    def setUp(self):

        # Call Parent
        super(TestTestCase, self).setUp()

        # Create Assignment
        self.asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)

        # Create Files
        src_file = open("./Makefile", 'rb')
        file_obj = werkzeug.datastructures.FileStorage(stream=src_file, filename="Makefile")
        self.files = set([])
        for i in range(10):
            data = copy.copy(test_common.FILE_TESTDICT)
            for k in data:
                data[k] = "test_{:s}_{:02d}".format(k, i)
            self.files.add(str(self.srv.create_file(data, file_obj=file_obj).uuid))
        file_obj.close()

    def tearDown(self):

        # Delete Files
        for fle_uuid in self.files:
            fle = self.srv.get_file(fle_uuid)
            fle.delete()

        # Call Parent
        super(TestTestCase, self).tearDown()

    def test_create_test(self):
        self.hashCreateHelper(self.asn.create_test,
                              test_common.TEST_TESTDICT)

    def test_get_test(self):
        self.hashGetHelper(self.asn.create_test,
                           self.srv.get_test,
                           test_common.TEST_TESTDICT)

    def test_update_test(self):
        self.hashUpdateHelper(self.asn.create_test,
                              test_common.TEST_TESTDICT)

    def test_delete_test(self):
        self.hashDeleteHelper(self.asn.create_test,
                              test_common.TEST_TESTDICT)

    def test_files(self):
        tst = self.asn.create_test(test_common.TEST_TESTDICT)
        self.subSetReferenceHelper(tst.add_files, tst.rem_files, tst.list_files, self.files)
        tst.delete()


class SubmissionTestCase(test_common_backend.SubMixin,
                         test_common_backend.UUIDHashMixin,
                         StructsTestCase):

    def setUp(self):

        # Call Parent
        super(SubmissionTestCase, self).setUp()

        # Create Assignment
        self.asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)

        # Create Files
        src_file = open("./Makefile", 'rb')
        file_obj = werkzeug.datastructures.FileStorage(stream=src_file, filename="Makefile")
        self.files = set([])
        for i in range(10):
            data = copy.copy(test_common.FILE_TESTDICT)
            for k in data:
                data[k] = "test_{:s}_{:02d}".format(k, i)
            self.files.add(str(self.srv.create_file(data, file_obj=file_obj).uuid))
        file_obj.close()

    def tearDown(self):

        # Delete Files
        for fle_uuid in self.files:
            fle = self.srv.get_file(fle_uuid)
            fle.delete()

        # Call Parent
        super(SubmissionTestCase, self).tearDown()

    def test_create_submission(self):
        self.hashCreateHelper(self.asn.create_submission,
                              test_common.SUBMISSION_TESTDICT)

    def test_get_submission(self):
        self.hashGetHelper(self.asn.create_submission,
                           self.srv.get_submission,
                           test_common.SUBMISSION_TESTDICT)

    def test_update_submission(self):
        self.hashUpdateHelper(self.asn.create_submission,
                              test_common.SUBMISSION_TESTDICT)

    def test_delete_submission(self):
        self.hashDeleteHelper(self.asn.create_submission,
                              test_common.SUBMISSION_TESTDICT)

    def test_files(self):
        sub = self.asn.create_submission(test_common.SUBMISSION_TESTDICT)
        self.subSetReferenceHelper(sub.add_files, sub.rem_files, sub.list_files, self.files)
        sub.delete()


class RunTestCase(test_common_backend.SubMixin,
                  test_common_backend.UUIDHashMixin,
                  StructsTestCase):

    def setUp(self):

        # Call Parent
        super(RunTestCase, self).setUp()

        # Create Test File
        tst_file = open("{:s}/script_1.py".format(test_common.COGS_TEST_FILE_PATH), 'rb')
        tst_file_obj = werkzeug.datastructures.FileStorage(stream=tst_file, filename="script.py")
        data = copy.copy(test_common.FILE_TESTDICT)
        data['key'] = 'script'
        self.tst_file = self.srv.create_file(data, file_obj=tst_file_obj)
        tst_file_obj.close()

        # Create Sub File
        sub_file = open("{:s}/pgm_good.py".format(test_common.COGS_TEST_FILE_PATH), 'rb')
        sub_file_obj = werkzeug.datastructures.FileStorage(stream=sub_file, filename="pgm.py")
        data = copy.copy(test_common.FILE_TESTDICT)
        data['key'] = 'submission'
        self.sub_file = self.srv.create_file(data, file_obj=sub_file_obj)
        sub_file_obj.close()

        # Create Assignment
        self.asn = self.srv.create_assignment(test_common.ASSIGNMENT_TESTDICT)

        # Create Test
        self.tst = self.asn.create_test(test_common.TEST_TESTDICT)
        self.tst.add_files([str(self.tst_file.uuid)])

        # Create Submission
        self.sub = self.asn.create_submission(test_common.SUBMISSION_TESTDICT)
        self.sub.add_files([str(self.sub_file.uuid)])

    def tearDown(self):

        # Cleanup Structs
        self.sub.delete()
        self.tst.delete()
        self.asn.delete()
        self.sub_file.delete()
        self.tst_file.delete()

        # Call Parent
        super(RunTestCase, self).tearDown()

    def test_create_run(self):
        run = self.sub.execute_run(self.tst)


# Main
if __name__ == '__main__':
    unittest.main()
