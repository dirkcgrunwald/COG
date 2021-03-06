# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado

import os
import copy
import logging
import traceback

import config

import tester


EXTRA_TEST_SCHEMA = ['path_script']
EXTRA_TEST_DEFAULTS = {'path_script': ""}

KEY_SCRIPT = 'script'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


class Tester(tester.Tester):

    def test(self):

        # Call Parent
        super(Tester, self).test()
        msg = "testmod_script: Running test"
        logger.info(self._format_msg(msg))

        # Find Grading Script
        tst_fle = None

        # If user provided path_script, use that
        if self.tst['path_script']:
            script_path = "{:s}/{:s}".format(self.env.wd_tst, self.tst['path_script'])
            script_path = os.path.normpath(script_path)
            for fle in self.env.tst_files:
                fle_path = os.path.normpath(fle['path'])
                if fle_path == script_path:
                    tst_fle = fle
                    break
            if not tst_fle:
                msg = "testmod_script: User specified 'path_script', "
                msg += "but file {:s} not found".format(script_path)
                logger.warning(self._format_msg(msg))

        # Next look for any files with the script key
        if not tst_fle:
            count = 0
            for fle in self.env.tst_files:
                key = fle['key']
                if (key == KEY_SCRIPT):
                    tst_fle = fle
                    count += 1
            if (count > 1):
                msg = "testmod_script: Module only supports single test script, "
                msg += "but {:d} found".format(count)
                logger.error(self._format_msg(msg))
                raise Exception(msg)

        # Finally, if there is only a single test file, use that
        if not tst_fle:
            if (len(self.env.tst_files) == 1):
                tst_fle = fle

        # Raise error if not found
        if not tst_fle:
            msg = "testmod_script: Module requires a test script file, but none found"
            logger.error(self._format_msg(msg))
            raise Exception(msg)

        # Setup Cmd
        tst_path = tst_fle['path']
        tst_cmd = [tst_path, self.env.wd_sub, self.env.wd_tst, self.env.wd_wrk]
        os.chmod(tst_path, 0775)
        cmd = tst_cmd

        # Run Script
        score = float(0)
        try:
            ret, stdout, stderr = self.env.run_cmd(cmd)
        except Exception as e:
            msg = "testmod_script: run_cmd raised error: {:s}".format(traceback.format_exc())
            logger.error(self._format_msg(msg))
            ret = 1
            stdout = ""
            stderr = msg

        # Process Results
        if (ret == 0):
            stdout_clean = stdout.rstrip().lstrip()
            try:
                score = float(stdout_clean)
            except Exception as err:
                msg = "testmod_script: Could not convert score "
                msg += "'{:s}' to float: {:s}".format(stdout_clean, str(err))
                logger.error(self._format_msg(msg))
                stderr = stderr + "\n\n" + msg
                ret = 1
        else:
            msg = "testmod_script: Script returned non-zero value: {:d}".format(ret)
            logger.warning(self._format_msg(msg))
            stderr = stderr + "\n\n" + msg

        # Log Results
        msg = "testmod_script: retval='{:d}', score='{:.2f}'".format(ret, score)
        logger.info(self._format_msg(msg))

        # Return
        return ret, score, stderr
