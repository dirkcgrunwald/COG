# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado

import os
import stat
import subprocess
import mimetypes
import shutil
import copy

import config

KEY_SOLUTION = 'solution'
KEY_SUBMISSION = 'submission'
KEY_INPUT = 'input'

class Tester(object):

    def __init__(self, env, data):
        self.env = env
        self.data = data

    def test(self):

        # Find Reference Submission
        sol_fle = None
        count = 0
        for fle in self.env.tst_files:
            key = fle['key']
            if (key == KEY_SOLUTION):
                sol_fle = fle
                count += 1
        if not sol_fle:
            raise Exception("Tester module requires a reference solution file")
        if (count > 1):
            raise Exception("Tester module only supports suppling one solution file")

        # Find Test Submission
        sub_fle = None
        count = 0
        for fle in self.env.sub_files:
            key = fle['key']
            if (key == KEY_SUBMISSION):
                sub_fle = fle
                count += 1
        if not sub_fle:
            raise Exception("Tester module requires a submission file")
        if (count > 1):
            raise Exception("Tester module only supports suppling one submission file")

        # Find Input Files
        input_fles = []
        for fle in self.env.tst_files:
            key = fle['key']
            if (key == KEY_INPUT):
                input_fles.append(fle)
        if not input_fles:
            input_fles.append(None)

        # Setup Cmd
        sudo_cmd = ['sudo', '-u', config.TESTER_SCRIPT_USER, '-g', config.TESTER_SCRIPT_GROUP]
        sandbox_path = self.env.sandbox['path']
        sandbox_cmd = [sandbox_path]
        os.chmod(sandbox_path, 0775)
        sol_path = sol_fle['path']
        sol_cmd = [sol_path]
        os.chmod(sol_path, 0775)
        sub_path = sub_fle['path']
        sub_cmd = [sub_path]
        os.chmod(sub_path, 0775)

        # Change WD
        owd = os.getcwd()
        try:
            os.chdir(self.env.wd)
        except:
            raise

        ret_val = 0
        pts = 0
        output = ""
        for input_fle in input_fles:

            if input_fle:
                output += "Testing {:s}...\n".format(input_fle['name'])
            else:
                output += "Testing...\n"

            # Test Reference Solution
            if input_fle:
                input_file = open(input_fle['path'], 'r')
            else:
                input_file = None
            cmd = sudo_cmd + sandbox_cmd + sol_cmd
            ret = 1
            stdout = ""
            stderr = ""
            try:
                p = subprocess.Popen(cmd, env=self.env.env,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=input_file)
                stdout, stderr = p.communicate()
                ret = p.returncode
            except Exception as e:
                output += "Exception running reference solution: {:s}\n".format(str(e))
            finally:
                if input_file:
                    input_file.close()

            # Process Solution Output
            if stderr:
                output += "Error output running reference solution: {:s}\n".format(stderr)
            if (ret != 0):
                output += "Non-zero exit running reference solution: {:d}\n".format(ret)
                ret_val += ret
                continue
            exp = stdout.rstrip().lstrip()

            # Test Submission
            if input_fle:
                input_file = open(input_fle['path'], 'r')
            else:
                input_file = None
            cmd = sudo_cmd + sandbox_cmd + sub_cmd
            ret = 1
            stdout = ""
            stderr = ""
            try:
                p = subprocess.Popen(cmd, env=self.env.env,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=input_file)
                stdout, stderr = p.communicate()
                ret = p.returncode
            except Exception as e:
                output += "Exception running submission: {:s}\n".format(str(e))
            finally:
                if input_file:
                    input_file.close()

            # Process Solution Output
            if stderr:
                output += "Error output running submission: {:s}\n".format(stderr)
            if (ret != 0):
                output += "Non-zero exit running submission: {:d}\n".format(ret)
            rec = stdout.rstrip().lstrip()

            output += "Expected: '{:s}', Received: '{:s}'".format(exp, rec)
            if (rec == exp):
                output += "   +1 pts\n"
                pts += 1
            else:
                output += "   +0 pts\n"

        # Change Back to OWD
        try:
            os.chdir(owd)
        except:
            raise

        # Calculate Score
        score = (pts / float(len(input_fles))) * float(self.data['maxscore'])

        # Return
        return ret_val, score, output