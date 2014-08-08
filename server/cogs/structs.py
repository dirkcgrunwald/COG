# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado

import copy

import auth

import backend_redis as backend
from backend_redis import BackendError, FactoryError, ObjectError, ObjectDNE


_TS_SCHEMA = ['created_time', 'modified_time']
_USER_SCHEMA = ['username', 'first', 'last', 'auth']
_GROUP_SCHEMA = ['name']
_ASSIGNMENT_SCHEMA = ['owner', 'name']
_TEST_SCHEMA = ['owner', 'assignment', 'name', 'type', 'maxscore']
_SUBMISSION_SCHEMA = ['owner', 'assignment']
_RUN_SCHEMA = ['owner', 'submission', 'test', 'status', 'score', 'output']
_FILE_SCHEMA = ['owner', 'key', 'name', 'type', 'encoding', 'path']

_FILES_DIR = "./files/"


### COGS Core Objects ###

## Top-Level Server Object ##
class Server(auth.AuthorizationAdminMixin, auth.AuthorizationMgmtMixin, object):
    """COGS Server Class"""

    # Override Constructor
    def __init__(self, db=None):
        """Base Constructor"""

        # Call Parent Construtor
        super(Server, self).__init__()

        # Save vars
        self.db = db
        self.srv = self

        # Setup Factories
        self.UserFactory = backend.UUIDFactory(UserBase, db=self.db, srv=self.srv)
        self.GroupFactory = backend.UUIDFactory(GroupBase, db=self.db, srv=self.srv)
        self.FileFactory = backend.UUIDFactory(FileBase, db=self.db, srv=self.srv)
        self.AssignmentFactory = backend.UUIDFactory(AssignmentBase, db=self.db, srv=self.srv)
        self.SubmissionFactory = backend.UUIDFactory(SubmissionBase, db=self.db, srv=self.srv)
        self.TestFactory = backend.UUIDFactory(TestBase, db=self.db, srv=self.srv)

        # Setup Admins
        self.init_admins()

    # User Methods
    @auth.requires_authorization()
    def create_user(self, d):
        return self._create_user(d)
    @auth.requires_authorization()
    def get_user(self, uuid_hex):
        return self._get_user(uuid_hex)
    @auth.requires_authorization()
    def list_users(self):
        return self._list_users()

    # Group Methods
    @auth.requires_authorization()
    def create_group(self, d):
        return self._create_group(d)
    @auth.requires_authorization()
    def get_group(self, uuid_hex):
        return self._get_group(uuid_hex)
    @auth.requires_authorization()
    def list_groups(self):
        return self._list_groups()

    # File Methods
    @auth.requires_authorization(pass_user=True)
    def create_file(self, d, file_obj, user=""):
        return self.FileFactory.from_new(d, file_obj, user="")
    @auth.requires_authorization()
    def get_file(self, uuid_hex):
        return self.FileFactory.from_existing(uuid_hex)
    @auth.requires_authorization()
    def list_files(self):
        return self.FileFactory.list_siblings()

    # Assignment Methods
    @auth.requires_authorization(pass_user=True)
    def create_assignment(self, d, user=""):
        return self.AssignmentFactory.from_new(d, user="")
    @auth.requires_authorization()
    def get_assignment(self, uuid_hex):
        return self.AssignmentFactory.from_existing(uuid_hex)
    @auth.requires_authorization()
    def list_assignments(self):
        return self.AssignmentFactory.list_siblings()

    # Test Methods
    @auth.requires_authorization()
    def get_test(self, uuid_hex):
        return self.TestFactory.from_existing(uuid_hex)
    @auth.requires_authorization()
    def list_tests(self):
        return self.TestFactory.list_siblings()

    # Submission Methods
    @auth.requires_authorization()
    def get_submission(self, uuid_hex):
        return self.SubmissionFactory.from_existing(uuid_hex)
    @auth.requires_authorization()
    def list_submissions(self):
        return self.SubmissionFactory.list_siblings()

    # Private User Methods
    def _create_user(self, d):
        return self.UserFactory.from_new(d)
    def _get_user(self, uuid_hex):
        return self.UserFactory.from_existing(uuid_hex)
    def _get_users(self):
        return self.UserFactory.get_siblings()
    def _list_users(self):
        return self.UserFactory.list_siblings()

    # Private Group Methods
    def _create_group(self, d):
        return self.GroupFactory.from_new(d)
    def _get_group(self, uuid_hex):
        return self.GroupFactory.from_existing(uuid_hex)
    def _get_groups(self):
        return self.GroupFactory.get_siblings()
    def _list_groups(self):
        return self.GroupFactory.list_siblings()


### COGS Base Objects ###

## User Account Object ##
class UserBase(backend.TSHashBase):
    """COGS User Class"""
    schema = set(_TS_SCHEMA + _USER_SCHEMA)


## User List Object ##
class UserListBase(backend.SetBase):
    """COGS User List Class"""
    pass


## User Group Object ##
class GroupBase(backend.TSHashBase):
    """COGS Group Class"""

    schema = set(_TS_SCHEMA + _GROUP_SCHEMA)

    # Override Constructor
    def __init__(self, uuid_obj):
        """Base Constructor"""

        # Call Parent Construtor
        super(GroupBase, self).__init__(uuid_obj)

        # Setup Lists
        sf = backend.Factory(UserListBase, prefix=self.full_key, db=self.db, srv=self.srv)
        self.members = sf.from_raw('members')

    # Members Methods
    @auth.requires_authorization()
    def add_users(self, user_uuids):
        return self._add_users(user_uuids)
    @auth.requires_authorization()
    def rem_users(self, user_uuids):
        return self._rem_users(user_uuids)
    @auth.requires_authorization()
    def list_users(self):
        return self._list_users()

    # Private Members Methods
    def _add_users(self, user_uuids):
        return self.members.add_vals(user_uuids)
    def _rem_users(self, user_uuids):
        return self.members.del_vals(user_uuids)
    def _list_users(self):
        return self.members.get_set()


## Assignment Object ##
class AssignmentBase(backend.TSHashBase):
    """
    COGS Assignment Class

    """

    schema = set(_TS_SCHEMA + _ASSIGNMENT_SCHEMA)

    # Override Constructor
    def __init__(self, key=None):
        """Base Constructor"""

        # Call Parent Construtor
        super(AssignmentBase, self).__init__(key)

        # Setup Factories
        self.TestFactory = backend.UUIDFactory(TestBase, db=self.db, srv=self.srv)
        self.SubmissionFactory = backend.UUIDFactory(SubmissionBase, db=self.db, srv=self.srv)

        # Setup Lists
        TestListFactory = backend.Factory(TestListBase, prefix=self.full_key,
                                          db=self.db, srv=self.srv)
        self.tests = TestListFactory.from_raw('tests')
        SubmissionListFactory = backend.Factory(SubmissionListBase, prefix=self.full_key,
                                                db=self.db, srv=self.srv)
        self.submissions = SubmissionListFactory.from_raw('submissions')

    # Override from_new
    @classmethod
    def from_new(cls, dictionary, user="", **kwargs):
        """New Constructor"""

        # Copy Data
        data = copy.copy(dictionary)

        # Add Data
        data['owner'] = user

        # Create Test
        asn = super(AssignmentBase, cls).from_new(data, **kwargs)

        # Return Run
        return asn

    # Public Test Methods
    @auth.requires_authorization(pass_user=True)
    def create_test(self, dictionary, user=""):
        tst = self.TestFactory.from_new(dictionary, str(self.uuid), user="")
        self._add_tests(str(tst.uuid))
        return tst
    @auth.requires_authorization()
    def list_tests(self):
        return self._list_tests()

    # Public Submission Methods
    @auth.requires_authorization(pass_user=True)
    def create_submission(self, dictionary, user=""):
        sub = self.SubmissionFactory.from_new(dictionary, str(self.uuid), user="")
        self._add_submissions(str(sub.uuid))
    @auth.requires_authorization()
    def list_submissions(self):
        return self._list_submissions()

    # Private Test Methods
    def _add_tests(self, test_uuids):
        return self.tests.add_vals(test_uuids)
    def _rem_tests(self, test_uuids):
        return self.tests.del_vals(test_uuids)
    def _list_tests(self):
        return self.tests.get_set()

    # Private Submission Methods
    def _add_submissions(self, submission_uuids):
        return self.submissions.add_vals(submission_uuids)
    def _rem_submissions(self, submission_uuids):
        return self.submissions.del_vals(submission_uuids)
    def _list_submissions(self):
        return self.submissions.get_set()


## Test Object ##
class TestBase(backend.TSHashBase):
    """COGS Test Class"""

    schema = set(_TS_SCHEMA + _TEST_SCHEMA)

    # Override from_new
    @classmethod
    def from_new(cls, dictionary, asn_uuid, user="", **kwargs):
        """New Constructor"""

        # Copy Data
        data = copy.copy(dictionary)

        # Add Data
        data['assignment'] = asn_uuid
        data['owner'] = user

        # Create Test
        tst = super(TestBase, cls).from_new(data)

        # Return Run
        return tst


## Test List Object ##
class TestListBase(backend.SetBase):
    """COGS Test List Class"""
    pass


## Submission Object ##
class SubmissionBase(backend.TSHashBase):
    """COGS Submission Class"""

    schema = set(_TS_SCHEMA + _SUBMISSION_SCHEMA)

    # Override Constructor
    def __init__(self, key=None):
        """Base Constructor"""
        super(SubmissionBase, self).__init__(key)
        self.RunFactory = backend.UUIDFactory(RunBase, prefix=self.full_key,
                                              db=self.db, srv=self.srv)

    # Run Methods
    @auth.requires_authorization()
    def execute_run(self, tst, sub):
        return self.RunFactory.from_new(tst, sub)


## Test List Object ##
class SubmissionListBase(backend.SetBase):
    """COGS Submission List Class"""
    pass


## Test Run Object ##
class RunBase(backend.TSHashBase):
    """
    COGS Run Class

    """

    schema = set(_TS_SCHEMA + _RUN_SCHEMA)

    # Override from_new
    @classmethod
    def from_new(cls, tst, sub, **kwargs):
        """New Constructor"""

        # Create New Object
        data = {}

        # Setup Dict
        data['test'] = repr(tst)
        data['status'] = ""
        data['score'] = ""
        data['output'] = ""

        # Create Run
        run = super(RunBase, cls).from_new(data, **kwargs)

        # Get Files
        tst_fls = tst.get_files()
        sub_fls = sub.get_files()

        # Grade Run
        env = environment.Env(run, tst_fls, sub_fls)
        tester = tester_script.Tester(env)
        ret, score, output = tester.test()
        env.close()

        # Set Results
        run['status'] = str(ret)
        run['score'] = str(score)
        run['output'] = str(output)

        # Return Run
        return run


## File Object ##
class FileBase(backend.TSHashBase):
    """
    COGS File Class

    """

    schema = set(_TS_SCHEMA + _FILE_SCHEMA)

    # Override from_new
    @classmethod
    def from_new(cls, d, file_obj=None, dst=None, **kwargs):
        """New Constructor"""

        # Create New Object
        data = copy.deepcopy(d)

        # Setup file_obj
        if file_obj is None:
            src_path = os.path.abspath("{:s}".format(data['path']))
            src_file = open(src_path, 'rb')
            file_obj = werkzeug.datastructures.FileStorage(stream=src_file, filename=data['name'])
        else:
            data['name'] = str(file_obj.filename)
            data['path'] = ""

        # Get Type
        typ = mimetypes.guess_type(file_obj.filename)
        data['type'] = str(typ[0])
        data['encoding'] = str(typ[1])

        # Create File
        fle = super(FileBase, cls).from_new(data, **kwargs)

        # Set Path
        if dst is None:
            fle['path'] = os.path.abspath("{:s}/{:s}".format(_FILES_DIR, repr(fle)))
        else:
            fle['path'] = os.path.abspath("{:s}".format(dst))

        # Save File
        try:
            file_obj.save(fle['path'])
            file_obj.close()
        except IOError:
            # Clean up on failure
            fle.delete(force=True)
            raise

        # Return File
        return fle

    # Override Delete
    def delete(self, force=False):
        """Delete Object"""

        # Delete File
        try:
            os.remove(self['path'])
        except OSError:
            if force:
                pass
            else:
                raise

        # Delete Self
        super(FileBase, self).delete()