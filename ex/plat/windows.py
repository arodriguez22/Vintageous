import subprocess
from subprocess import PIPE
import os
import tempfile


try:
    import ctypes
except ImportError:
    import plat
    if plat.HOST_PLATFORM == plat.WINDOWS:
        raise EnvironmentError("ctypes module missing for Windows.")
    ctypes = None


def get_startup_info():
    # Hide the child process window.
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startupinfo


def run_and_wait(view, cmd):
    subprocess.Popen(['cmd.exe', '/c', cmd + '&& pause']).wait()


def run_and_read(view, cmd):
    out, err = subprocess.Popen(['cmd.exe', '/c', cmd],
                                stdout=PIPE,
                                stderr=PIPE,
                                shell=True,
                                startupinfo=get_startup_info()).communicate()
    try:
        return (out or err).decode(get_oem_cp()).replace('\r\n', '\n')
    except AttributeError:
        return ''


def filter_region(view, txt, command):
    try:
        contents = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        contents.write(txt.encode('utf-8'))
        contents.close()

        script = tempfile.NamedTemporaryFile(suffix='.bat', delete=False)
        script.write(('@echo off\ntype %s | %s' % (contents.name, command)).encode('utf-8'))
        script.close()

        p = subprocess.Popen([script.name],
                             stdout=PIPE,
                             stderr=PIPE,
                             startupinfo=get_startup_info())

        our, err = p.communicate()
        return (out or err).decode(get_oem_cp()).replace('\r\n', '\n')[:-1].strip()
    finally:
        os.remove(script.name)
        os.remove(contents.name)


def get_oem_cp():
    codepage = ctypes.windll.kernel32.GetOEMCP()
    return str(codepage)
