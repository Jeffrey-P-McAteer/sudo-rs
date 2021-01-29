#!/usr/bin/env python3

"""
Script dependencies:
 - python
 - rust/cargo
 - git
 - make/gcc/autoconf tools

Script overview:
 - compile sudo-rs in CWD
 - compile sudo in a temporary directory
 - get list of sudo-rs output binaries
 - get list of sudo output binaries
 - execute both binaries and compare outputs
   for a large+growing number of test cases

Environment variables to change behaviour:
 - SUDO_GIT_SOURCE=<git url>
    - if set AND the temporary directory is empty we will clone from the given URL
 - NO_PULL_LATEST
    - if set the script does not pull the latest sudo source code
 - TEST_AGAINST_COMMIT=<commit id>
    - if set we checkout this id from the sudo repo to test against

"""

import os, sys, subprocess
import tempfile
import random

SUDO_GIT_SOURCE = 'https://github.com/sudo-project/sudo.git'
if 'SUDO_GIT_SOURCE' in os.environ:
  SUDO_GIT_SOURCE = os.environ['SUDO_GIT_SOURCE']

SUDO_CWD = os.path.join(
  tempfile.gettempdir(), 'sudo'
)

# This should be used when calling compare_executions.
# We change it every execution to ensure it does not alter tests.
BINARY_PLACEHOLDER = 'BINARY_{}_ENDBINARY'.format(hex(random.randint(100000, 999999)))

def compile_sudo_rs():
  subprocess.run([
    'cargo', 'build', '--release'
  ], check=True)

def compile_sudo():
  if not os.path.exists(SUDO_CWD):
    subprocess.run([
      'git', 'clone', SUDO_GIT_SOURCE, SUDO_CWD
    ])

  # Quick helper to pass cwd=SUDO_CWD to commands
  def runin(*cmd):
    subprocess.run(list(cmd), check=True, cwd=SUDO_CWD)  

  # Pull the latest code unless the dev says no
  if not 'NO_PULL_LATEST' in os.environ:
    runin('git', 'pull')

  if 'TEST_AGAINST_COMMIT' in os.environ:
    runin('git', 'checkout', '-f', os.environ['TEST_AGAINST_COMMIT'])

  # _try_ to only run ./configure once
  configure_flag = os.path.join(SUDO_CWD, '.git', 'configure_finished.txt')
  if not os.path.exists(configure_flag):
    runin('./configure')
    subprocess.run(['touch', configure_flag])

  # Make should do dependency checking by itself
  runin('make')


def find_bin(search_dir, bin_name, max_depth=5):
  if max_depth < 1:
    return None

  for file in os.listdir(search_dir):
    if os.path.isdir(os.path.join(search_dir, file)):
      continue

    if file == bin_name:
      return os.path.join(search_dir, file)

  # if we did not find the binary recurse into sub-directories
  for file in os.listdir(search_dir):
    file = os.path.join(search_dir, file)
    if os.path.isdir(file):
      maybe_found = find_bin(file, bin_name, max_depth=max_depth-1)
      if maybe_found:
        return maybe_found

  return None


def find_sudo_rs_bin(bin_name):
  return find_bin(
    os.path.join('target', 'release'),
    bin_name,
    max_depth=1
  )

def find_sudo_bin(bin_name):
  return find_bin(
    SUDO_CWD,
    bin_name,
  )

def compare_executions(test_description, cmd_bin, cmd_list, env_dict={}):
  # cmd_list must have a {BINARY} string either as an argument or
  # as a sub-string in an argument (if /bin/sh is used to
  # print other info beyond a single command execution to check
  # eg files and directories being read/written by the command)
  if not BINARY_PLACEHOLDER in ''.join(cmd_list):
    raise ValueError('cmd_list must contain BINARY_PLACEHOLDER as an argument or as a sub-string of an argument')

  sudo_rs_bin = find_sudo_rs_bin(cmd_bin)
  sudo_bin = find_sudo_bin(cmd_bin)

  print('')
  print('Running test: {}'.format(test_description))
  print('Comparing output of {} and {}'.format(sudo_rs_bin, sudo_bin))

  def get_cmd_output(cmd_bin):
    our_cmd_list = cmd_list.copy()
    if BINARY_PLACEHOLDER in our_cmd_list:
      our_cmd_list[our_cmd_list.index(BINARY_PLACEHOLDER)] = cmd_bin
    else:
      i = 0
      for x in range(0, len(our_cmd_list)):
        if BINARY_PLACEHOLDER in our_cmd_list[x]:
          i = x

      our_cmd_list[i] = our_cmd_list[i].replace(BINARY_PLACEHOLDER, cmd_bin)

    # Now that {BINARY} has been substituted, run the command and return output
    try:
      return subprocess.check_output(
        our_cmd_list,
        stderr=subprocess.STDOUT,
        timeout=15, # Not 100% sure if this is good but nice to have for CI environments
        env=env_dict,
      )
    except subprocess.CalledProcessError as ex:
      return ex.output

  sudo_rs_out = get_cmd_output(sudo_rs_bin)
  sudo_out = get_cmd_output(sudo_bin)

  # Ignore leading and trailing whitespace
  sudo_rs_out = sudo_rs_out.decode('utf-8').strip()
  sudo_out = sudo_out.decode('utf-8').strip()

  if sudo_rs_out != sudo_out:
    print('Test Failed!')
    print('')
    print('===== sudo_rs_out =====')
    print(sudo_rs_out)
    print('')
    print('===== sudo_out =====')
    print(sudo_out)
    print('')

  else:
    print('Test Passed!')



def main():
  # Move up a directory until we hit a .git folder to ensure
  # our CWD == repository root
  for _ in range(0, 4):
    if not os.path.exists('.git'):
      os.chdir('..')

  # Process is now in the "sudo-rs" folder

  # Compile the programs we will be testing...
  compile_sudo_rs()
  compile_sudo()

  # Now we call compare_executions for all the behaviour
  # we want to test.

  all_binaries = [
    'cvtsudoers',
    'sudo',
    'sudo_logsrvd',
    'sudo_sendlog',
    #'sudoedit',
    'sudoreplay',
    'visudo',
  ]

  for b in all_binaries:
    compare_executions(
      'Test that help text is identical for {}'.format(b),
      b,
      [BINARY_PLACEHOLDER, '--help'],
    )




if __name__ == '__main__':
  main()
