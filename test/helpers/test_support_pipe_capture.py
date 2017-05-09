"""
Code from test.test_support.
Documentation: http://docs.python.org/2/library/test.html

Source: http://stackoverflow.com/a/18844643/1910555

Usage:
    from test.test_support_pipe_capture import captured_stdout, captured_output, captured_stderr, captured_stdin

    with captured_stdout() as stdout:
        my_functions_that_write_to_stdout()

    captured_stdout_strings = stdout.getvalue()

    print( captured_stdout_strings )
"""
import contextlib
import sys


@contextlib.contextmanager
def captured_output(stream_name):
    """Return a context manager used by captured_stdout and captured_stdin
    that temporarily replaces the sys stream *stream_name* with a StringIO."""
    import StringIO
    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, StringIO.StringIO())
    try:
        yield getattr(sys, stream_name)
    finally:
        setattr(sys, stream_name, orig_stdout)


def captured_stdout():
    """Capture the output of sys.stdout:

       with captured_stdout() as s:
           print "hello"
       self.assertEqual(s.getvalue(), "hello")
    """
    return captured_output("stdout")

def captured_stderr():
    return captured_output("stderr")

def captured_stdin():
    return captured_output("stdin")