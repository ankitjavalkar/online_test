#!/usr/bin/env python
import sys
import traceback
import os
from os.path import join
import importlib
from contextlib import contextmanager


# local imports
from code_evaluator import CodeEvaluator


TESTER_BACKEND = {
    "stdout_testcase": "StdoutTesterBackend",
    "assertion_testcase": "AssertionTesterBackend",
    "argument_based_testcase": "ArgumentBasedTesterBackend"
}


def detect_backend(test_case_type):
    """
        Detect the right backend for a test case.
    """
    backend_name = TESTER_BACKEND.get(test_case_type)
    backend = getattr(backend_name)
    return backend


@contextmanager
def redirect_stdout():
    """
        Context replace stdout with a string buffer
    """
    from StringIO import StringIO
    new_target = StringIO()

    old_target, sys.stdout = sys.stdout, new_target # replace sys.stdout
    try:
        yield new_target # run some code with the replaced stdout
    finally:
        sys.stdout = old_target # restore to the previous value


class PythonCodeEvaluator(CodeEvaluator):
    """
        Tests the Python code obtained from Code Server
    """
    # Private Protocol ##########
    def _check_code(self):
        # from tester.python.verifier import PythonPrintTesterBackend #@@@
        # backend = PythonPrintTesterBackend() #@@@
        success = False
        backend = detect_backend(self.tester_type)

        try:
            tb = None
            #@@@ Updated upstream
            # test_code = self._create_test_case()
            # submitted = compile(self.user_answer, '<string>', mode='exec')
            # g = {}
            # exec submitted in g
            # _tests = compile(test_code, '<string>', mode='exec')
            # exec _tests in g

            submitted = compile(self.user_answer, '<string>', mode='exec')
            backend_object = backend.from_args({'submitted': submitted,
                                                'test': self.test,
                                                'test_case_data': self.test_case_data})
            backend.test_code(submitted)
            # g = {}
            # exec submitted in g
            # for t in self.test_case_data:
            #     tdata = backend.unpack(t)
            #     test_code = backend.create()
            #     _tests = compile(test_code, '<string>', mode='exec')
            #     exec _tests in g
            # backend.test_code(submitted, self.test)
        except AssertionError:
            type, value, tb = sys.exc_info()
            info = traceback.extract_tb(tb)
            fname, lineno, func, text = info[-1]
            text = str(test_code).splitlines()[lineno-1]
            err = "{0} {1} in: {2}".format(type.__name__, str(value), text)
        else:
            success = True
            err = 'Correct answer'

        del tb
        return success, err

    def _create_test_case(self):
        """
            Create assert based test cases in python
        """
        test_code = ""
        if self.test:
            return self.test
        elif self.test_case_data:
            for test_case in self.test_case_data:
                pos_args = ", ".join(str(i) for i in test_case.get('pos_args')) \
                                    if test_case.get('pos_args') else ""
                kw_args = ", ".join(str(k+"="+a) for k, a
                                 in test_case.get('kw_args').iteritems()) \
                                if test_case.get('kw_args') else ""
                args = pos_args + ", " + kw_args if pos_args and kw_args \
                                                    else pos_args or kw_args
                function_name = test_case.get('func_name')
                expected_answer = test_case.get('expected_answer')

                tcode = "assert {0}({1}) == {2}".format(function_name, args,
                                             expected_answer)
                test_code += tcode + "\n"
            return test_code

class AssertionTesterBackend(object):
    def __init__(self, submitted, test):
        self.submitted = submitted
        self.test = test

    @classmethod
    def from_args(cls, **kwargs):
        submitted = kwargs.get('submitted')
        test = kwargs.get('test')
        instance = cls(submitted, test)

    def test_code(self):
        """
            execute an assertion test to verify the user answer
        """
        g = {}
        compiled_tests = compile(self.test, '<string>', mode='exec')
        exec self.submitted in g
        exec _tests in g

class StdoutTesterBackend(object):
    def __init__(self, submitted, test):
        self.submitted = submitted
        self.test = test

    @classmethod
    def from_args(cls, **kwargs):
        submitted = kwargs.get('submitted')
        tests = kwargs.get('test')
        instance = cls(submitted, tests)

    def test_code(self):
        """
            execute a test to verify the user answer
        """
        with redirect_stdout() as output_buffer: 
            g = {}
            exec self.submitted in g

        # return_buffer = out.encode('string_escape')
        raw_output_value = output_buffer.getvalue()
        output_value = raw_output_value.encode('string_escape').strip()
        if output_value == str(reference_output):
            return True
        else:
            raise ValueError("Incorrect Answer")

class ArgumentBasedTesterBackend(object):
    def __init__(self, submitted, test_case_data):
        self.submitted = submitted
        self.test_case_data = test_case_data

    @classmethod
    def from_args(cls, **kwargs):
        submitted = kwargs.get('submitted')
        test_case_data = kwargs.get('test_case_data')
        instance = cls(submitted, test_case_data)

    def test_code(self, submitted, test_case_data):
        """
            execute a test to verify the user answer
        """
        g = {}
        tests = self.unpack()
        compiled_tests = compile(tests, '<string>', mode='exec')
        exec submitted in g
        exec _tests in g
        # test_code = "assert {0}({1}) == {2}".format(self.test_case_parameters['function_name'], self.test_case_parameters['args'],
        #                              self.test_case_parameters['expected_answer'])
        # return test_code

    def pack(self, test_case):
        kw_args_dict = {}
        pos_args_list = []
        test_case_data = {}
        test_case_data['test_id'] = test_case.id
        test_case_data['func_name'] = test_case.func_name
        test_case_data['expected_answer'] = test_case.expected_answer

        if test_case.kw_args:
            for args in test_case.kw_args.split(","):
                arg_name, arg_value = args.split("=")
                kw_args_dict[arg_name.strip()] = arg_value.strip()

        if test_case.pos_args:
            for args in test_case.pos_args.split(","):
                pos_args_list.append(args.strip())

        test_case_data['kw_args'] = kw_args_dict
        test_case_data['pos_args'] = pos_args_list

        return test_case_data

    # def unpack(self, test_case_data): #@@@OLD
    #     pos_args = ", ".join(str(i) for i in test_case_data.get('pos_args')) \
    #                         if test_case_data.get('pos_args') else ""
    #     kw_args = ", ".join(str(k+"="+a) for k, a
    #                      in test_case_data.get('kw_args').iteritems()) \
    #                     if test_case_data.get('kw_args') else ""
    #     args = pos_args + ", " + kw_args if pos_args and kw_args \
    #                                         else pos_args or kw_args
    #     function_name = test_case_data.get('func_name')
    #     expected_answer = test_case_data.get('expected_answer')

    #     self.test_case_parameters = {
    #         'args': args,
    #         'function_name': function_name,
    #         'expected_answer': expected_answer
    #     }

    #     return self.test_case_parameters

    def unpack(self):
        for test_case in self.test_case_data:
            pos_args = ", ".join(str(i) for i in test_case.get('pos_args')) \
                                if test_case.get('pos_args') else ""
            kw_args = ", ".join(str(k+"="+a) for k, a
                             in test_case.get('kw_args').iteritems()) \
                            if test_case.get('kw_args') else ""
            args = pos_args + ", " + kw_args if pos_args and kw_args \
                                                else pos_args or kw_args
            function_name = test_case.get('func_name')
            expected_answer = test_case.get('expected_answer')

            tcode = "assert {0}({1}) == {2}".format(function_name, args,
                                         expected_answer)
            test_code += tcode + "\n"
        return test_code
