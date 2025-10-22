#!/bin/python3

import sys
import shutil
from subprocess import run, PIPE, TimeoutExpired
import os
import json
import time
import argparse
from abc import ABC, abstractmethod

MAX_SOLUTIONS = '925'

def dispatch_question(args):
    pass

def call_clingo(clingo, input_names, timeout):
    cmd = [clingo, "--warn=no-atom-undefined", "--warn=no-file-included", "--warn=no-operation-undefined", "--warn=no-global-variable", "--outf=2"] + input_names
    start = time.time()
    output = run(cmd, stdout=PIPE, stderr=PIPE, timeout=timeout, text=True)
    end = time.time()
    if output.stderr:
        raise RuntimeError("Clingo: %s" % output.stderr)
    return output.stdout, end-start


def generate_solutions_for_instance(args, instance):
    opt = [args.encoding, args.instances+instance, "925"]
    try:
        stdout, time = call_clingo(args.clingo, opt, args.timeout)
        output = json.loads(stdout)
    except RuntimeError as e:
        raise e
    if output['Models']['More'] == 'no':
        for v in output['Call'][0]['Witnesses']:
            v['Value'].sort()
        inst_sol = instance[:-2]+"json"
        with open(os.path.join(args.generate_solutions,inst_sol),"w+") as outfile:
            outfile.write(json.dumps(output, indent = 2))

def generate_solutions(args):
    instances_dir= os.listdir(args.instances)
    instances_dir.sort()
    for instance in instances_dir:
        generate_solutions_for_instance(args, instance)

def check_result(output, expected):
    result = output['Result']
    solutions = []
    if not result.startswith('UNSAT'):
        solutions = [w['Value'] for w in output['Call'][len(output['Call'])-1]['Witnesses']]
    return result.startswith(expected), solutions

def get_solutions(output):
    _, solutions = check_result(output, "SAT")
    return solutions

class Question(ABC):

    @abstractmethod
    def eval(self):
        pass


class QuestionALL(Question):

    def __init__(self, args, question_data, silent_print=False):
        self._args = args
        path = question_data['path']
        self._questions = [ os.path.join(path, q) for q in  question_data['questions'] ]
        self._points   = question_data.get('points', None)
        self._silent_print = silent_print

    def eval(self):
        success = True
        message = ""
        for question_path in self._questions:
            self._args.question = question_path
            question = dispatch_question(self._args)
            s,m = question.eval()
            success = success & s
            message = message + m
        return success, message

class QuestionSAT(Question):

    def __init__(self, args, question_data, silent_print=False):
        self._args = args
        path = question_data['path']
        self._instance_path = os.path.join(path, question_data['instance-path'])
        if 'instances' in question_data:
             self._instances = question_data['instances']
        else:
            self._instances = os.listdir(self._instance_path)
            self._instances.sort()
        self._encoding = question_data['encoding']
        if isinstance(self._encoding, str):
            self._encoding = [self._encoding]
        self._points   = question_data.get('points', None)
        self._silent_print = silent_print


    @staticmethod
    def _load_solution(path, instance):
        inst_sol = instance[:-2]+"json"
        with open(os.path.join(path, inst_sol),"r") as infile:
            output = json.load(infile)
        ref_solutions = get_solutions(output)
        for s in ref_solutions:
            s.sort()
        ref_solutions.sort()
        return ref_solutions

    def _test_instance_eval(self, solutions, instance):
        ref_solutions = self._load_solution(self._solution_path, instance)
        return solutions == ref_solutions

    def _test_instance(self, instance):
        expected = "SAT"
        opt = list(self._encoding)
        opt.extend([os.path.join(self._instance_path,instance), MAX_SOLUTIONS])
        try:
            stdout, time = call_clingo(self._args.clingo, opt, self._args.timeout)
            output = json.loads(stdout)
        except RuntimeError as e:
            raise e

        ok, solutions = check_result(output, expected)
        if not ok:
            return False, time

        for s in solutions:
            s.sort()

        solutions.sort()
        return self._test_instance_eval(solutions, instance), time

    def _test_all_instances(self):
        success = True
        message = ""
        for file in self._encoding:
            if not os.path.isfile(file):
                success = False
                message = f'Encoding not found: {file} \n'
                break
        if not success:
            return success, message
        for instance in self._instances:
            result = 0
            error = False
            try:
                res, time = self._test_instance(instance)
                if not res:
                    success = False
            except Exception as e:
                success = False
                if isinstance(e, TimeoutExpired):
                    result = "timeout\n"
                else:
                    result = "error\n"
                    error = e
            message += "$"+instance + ": "
            if result:
                message += result
                if error:
                    message += str(error)+"\n"
            else:
                message += "success" if res else "failure"
                message += " in "+str(1000*time)[:7]+" ms\n"
        return success, message

    def eval(self):
        return self._test_all_instances()


class QuestionSATExact(QuestionSAT):
    
    def __init__(self, args, question_data):
        super().__init__(args, question_data)
        path = question_data['path']
        self._solution_path = os.path.join(path, question_data['solutions'])

def dispatch_question(args):
    question = os.path.join('questions',f'question{args.question}.json')
    try:
        with open(question) as question_file:
            question_data = json.load(question_file)
    except IOError as error:
        raise Exception('Question not found', args.question)

    question_data['path'] = os.path.dirname(args.question)
    if 'type' not in question_data:
        raise Exception('Wrong question format. Argument "type" is required.')
    else:
        type = question_data['type']
        if type == 'exact':
            return QuestionSATExact(args, question_data)
        if type == 'all':
            return QuestionALL(args, question_data)
        # elif type == 'lower-upper':
        #     return QuestionSATLowerUpper(args, question_data)
        raise Exception(f'Unrecognised type ({type}).')

def parse():
    parser = argparse.ArgumentParser(
        description="Test ASP encodings"
    )
    parser.add_argument('--question', metavar='<file>',
                        help='Path to a question file.',
                        required=False, default=None)

    parser.add_argument('--clingo', '-c', metavar='<path>', 
                        help='Clingo to use.', 
                        default="clingo",
                        required=False)

    parser.add_argument('--encoding', '-e', metavar='<file>',
                        help='ASP encoding to test.', 
                        required=False, default=None)

    parser.add_argument('--instances', '-i', metavar='<path>',
                        help='Directory of the instances.', 
                        required=False, default=None)

    parser.add_argument('--solutions', '-s', metavar='<path>',
                        help='Directory of the solutions.',
                        required=False, default=None)

    parser.add_argument('--timeout', '-t', metavar='N', type=int,
                        help='Time allocated to each instance.',
                        required=False, default=180)

    parser.add_argument('--generate-solutions', metavar='<dir>',
                        help='Path to a directory to write solutions. If does not exist, it will be created.',
                        required=False, default=None)
    args = parser.parse_args()
    if shutil.which(args.clingo) is None:
        raise IOError("file %s not found!" % args.clingo)

    if args.question is not None and (args.encoding is not None or
                                      args.instances is not None or
                                      args.solutions is not None or
                                      args.generate_solutions is not None):
        raise Exception('Flag  --solutions and --generatesolutions cannot be used together.')

    if args.solutions is not None and args.generate_solutions is not None:
        raise Exception('Flags --question cannot be used in combination with --encoding, --instances, --solutions nor --generatesolutions.')

    if args.generate_solutions is not None and (args.encoding is None or
                                                args.instances is None):
        raise Exception('Flag --generatesolutions requires flags --encoding and --instances.')
    
    if args.encoding is not None and not os.path.isfile(args.encoding):
        raise IOError("file %s not found!" % args.encoding)
    
    if args.instances is not None and not os.path.isdir(args.instances):
        raise IOError("directory %s not found!" % args.instances)
    
    if args.solutions is not None and not os.path.isdir(args.solutions):
        raise IOError("directory %s not found!" % args.solutions)
    
    if args.generate_solutions is not None and not os.path.isdir(args.generate_solutions):
        os.mkdir(args.generate_solutions)
        args.solutions = None
    if args.instances is not None and args.instances[-1] != "/":
        args.instances+="/"
    if args.solutions is not None and args.solutions[-1] != "/":
        args.solutions+="/"
    if args.generate_solutions is not None and args.generate_solutions[-1] != "/":
            args.generate_solutions+="/"

    if args.generate_solutions is None and  args.question is None:
        args.question ="ALL"

    return args

def main():
    if sys.version_info < (3, 6):
        raise SystemExit('Sorry, this code need Python 3.6 or higher')
    try:
        args=parse()
        if args.generate_solutions:
            generate_solutions(args)
            return 0
        if args.question:
            question = dispatch_question(args)
            success, message = question.eval()
            if success:
                message += "SUCCESS\n"
                ret = 0
            else:
                message += "FAILURE\n"
                ret = 1
            sys.stdout.write(message)
            return ret

        question_data = { "type"          : "exact",
                          "instance-path" : args.instances,
                          "solutions"     : args.solutions,
                          "encoding"      : args.encoding,
                          "path"          : os.getcwd()
                        }
        question = QuestionSATExact(args, question_data)
        success, message = question.eval()
        if success:
            message += "SUCCESS\n"
            ret = 0
        else:
            message += "FAILURE\n"
            ret = 1
        sys.stdout.write(message)
        return 1

    except Exception as e:
        if len(e.args) >= 1:
            if e.args[0] == 'Question not found':
                sys.stderr.write(f"ERROR: {e.args[0]} {e.args[1]}\n")
                return 1
        raise e
        sys.stderr.write("ERROR: %s\n" % str(e))
        return 1

if __name__ == '__main__':
    sys.exit(main())