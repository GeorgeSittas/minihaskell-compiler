##############################################################################################################################
#
# Usage: python3 test_script.py
# Requirements: 1) Place this script in the "test" directory.
#               2) Adjust path in "custom_exec_name" to reflect the path of your custom interpreter 
#                  executable, relative to the directory where your tests exist.
#               3) Adjust the main() function taking into account the naming scheme of your tests.
#                  eg. if the naming scheme is "test{index}.txt" leave the main as is, and update the "num_tests" variable.
#               4) [Optionally] Adjust the "max_timeout" variable to reflect the max time that the custom interpeter or ghc
#                               are allowed to run before being interrupted.
##############################################################################################################################

import subprocess

custom_exec_name = '../TestAll'
num_tests = 10
max_timeout = 20

def main():  # Output failed tests
    num_tests_to_check = num_tests
    i = 0
    tests_failed = 0
    print ("> Begin testing...")
    while i <= num_tests_to_check:
        filename = 'test' + str(i) + '.txt'
        success = test_custom_vs_ghc(filename)
        if not success:
            print("> Fail: " + filename)
            tests_failed += 1
        i+=1
    print ("> Finished testing...")
    print ("> Tests failed: ", tests_failed)
    print ("> Bye!")


def check_with_custom(filename):
    exec_name = custom_exec_name
    try:
        res = subprocess.check_output(
            f'{exec_name} < {filename}; exit 0',
            stderr=subprocess.STDOUT,
            timeout=max_timeout,
            shell=True
        )
    except:
        res = b'error'

    res = res.decode().strip()  # Byte to Str
    try:
        res = str(int(res))  # Check if result can be converted to integer (aka if int or error was returned)
    except:
        res = 'error'
    return res


def check_with_ghc(filename):
    tmpname = 'tmp_' + filename
    rm_cmd = f'rm -f ./{tmpname} ./{tmpname}.hi ./{tmpname}.o ./{tmpname}.hs'
    try:
        res = subprocess.check_output(
            f'cp {filename} {tmpname}.hs && printf "\n\nmain = print result\n\n" >> {tmpname}.hs \
                && ghc {tmpname}.hs && ./{tmpname} && {rm_cmd}; exit 0',
            stderr=subprocess.STDOUT,
            timeout=max_timeout,
            shell=True
        )
    except:
        subprocess.check_output(rm_cmd, shell=True) # Cleanup leftovers
        res = b'error'

    res = res.decode().strip()  # Byte to Str
    if 'error' in res.lower():
        res = 'error'
    else:
        res = res.split('\n')[-1]
        try:
            res = str(int(res))
        except:
            res = 'error'
    return res


def test_custom_vs_ghc(filename):  # Filename of test
    ghc_res = check_with_ghc(filename)
    cus_res = check_with_custom(filename)
    if ghc_res == 'error' or cus_res == 'error':
        return False
    if int(ghc_res) != int(cus_res):
        return False
    return True

main()