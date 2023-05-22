import logging
import os
import subprocess
from collections import namedtuple

logger = logging.getLogger('instance-flavor-check')


class Command:
    """
    **Implements command invocation**
    An instance of Command provides methods to invoke external
    commands in blocking and non blocking mode. Control of
    stdout and stderr is given to the caller
    """
    @staticmethod
    def run(command, custom_env=None, raise_on_error=True):
        """
        Execute a program and block the caller. The return value
        is a hash containing the stdout, stderr and return code
        information. Unless raise_on_error is set to false an
        exception is thrown if the command exits with an error
        code not equal to zero
        Example:
        .. code:: python
            result = Command.run(['ls', '-l'])
        :param list command: command and arguments
        :param list custom_env: custom os.environ
        :param bool raise_on_error: control error behaviour
        :return:
            Contains call results in command type
            .. code:: python
                command(output='string', error='string', returncode=int)
        :rtype: namedtuple
        """
        command_type = namedtuple(
            'command', ['output', 'error', 'returncode']
        )
        environment = os.environ
        if custom_env:
            environment = custom_env
        try:
            logger.debug('Calling: {0}'.format(command))
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment
            )
        except Exception as issue:
            raise Exception(
                '{0}: {1}: {2}'.format(command[0], type(issue).__name__, issue)
            )
        output, error = process.communicate()
        if process.returncode != 0 and not error:
            error = bytes(b'(no output on stderr)')
        if process.returncode != 0 and not output:
            output = bytes(b'(no output on stdout)')
        if process.returncode != 0 and raise_on_error:
            logger.error(
                'EXEC: Failed with stderr: {0}, stdout: {1}'.format(
                    error.decode(), output.decode()
                )
            )
            raise Exception(
                '{0}: stderr: {1}, stdout: {2}'.format(
                    command[0], error.decode(), output.decode()
                )
            )
        return command_type(
            output=output.decode(),
            error=error.decode(),
            returncode=process.returncode
        )
