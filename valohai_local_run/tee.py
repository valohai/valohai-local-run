import subprocess
from select import select


def tee_spawn(command, stdout_files, stderr_files):
    """
    Spawn `command` as a subprocess and tee its stdout and/or stderr
    to the given files.

    :param command: Command to spawn (see `subprocess.Popen`)
    :param stdout_files: Iterable of writable files for stdout
    :param stderr_files: Iterable of writable files for stderr
    :return: The process object after it has quit.
    """
    proc = subprocess.Popen(
        command,
        bufsize=0,
        stdout=(subprocess.PIPE if stdout_files else None),
        stderr=(subprocess.PIPE if stderr_files else None),
    )
    fd_map = {}
    if stdout_files:
        fd_map[proc.stdout] = list(stdout_files)
    if stderr_files:
        fd_map[proc.stderr] = list(stderr_files)

    while proc.poll() is None:
        try:
            r_fds, w_fds, x_fds = select(fd_map.keys(), [], [], 0.1)
            for from_fd in r_fds:
                data = from_fd.read(10240)
                if not data:  # EOF? Weird!
                    continue
                for to_file in fd_map.get(from_fd, ()):
                    try:
                        to_file.write(data)
                    except:  # pragma: no cover
                        pass
        except:
            proc.kill()
            proc.wait(timeout=10)
            raise
    return proc
