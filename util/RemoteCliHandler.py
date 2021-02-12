# https://github.com/jquast/telnetlib3/blob/master/telnetlib3/server_shell.py
import asyncio

CR, LF, NUL = '\r\n\x00'
CRLF = '\r\n'

class RemoteCliHandler:

    @asyncio.coroutine
    def shell(reader, writer):
        writer.write("Connected to UniqueBible.app" + CR + LF)

        linereader = RemoteCliHandler.readline(reader, writer)
        linereader.send(None)

        command = None
        while True:
            if command:
                writer.write(CR + LF)
            writer.write('> ')
            command = None
            while command is None:
                inp = yield from reader.read(1)
                if not inp:
                    return
                command = linereader.send(inp)
            writer.write(CR + LF)
            if command.lower() in ('quit', 'exit', 'bye'):
                break
            elif command.lower() in ('help', '?'):
                writer.write("Type 'quit' to exit" + CRLF)
                writer.write("All other commands will be processed by UBA")
            elif command:
                writer.write('Executing ' + command)
        writer.close()

    @asyncio.coroutine
    def readline(reader, writer):
        """
        A very crude readline coroutine interface.
        This function is a :func:`~asyncio.coroutine`.
        """
        command, inp, last_inp = '', '', ''
        inp = yield None
        while True:
            if inp in (LF, NUL) and last_inp == CR:
                last_inp = inp
                inp = yield None

            elif inp in (CR, LF):
                # first CR or LF yields command
                last_inp = inp
                inp = yield command
                command = ''

            elif inp in ('\b', '\x7f'):
                # backspace over input
                if command:
                    command = command[:-1]
                    writer.echo('\b \b')
                last_inp = inp
                inp = yield None

            else:
                # buffer and echo input
                command += inp
                writer.echo(inp)
                last_inp = inp
                inp = yield None


