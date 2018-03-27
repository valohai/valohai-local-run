import subprocess
from select import select


def tee_spawn(command, stdout_fds, stderr_fds):
    """
    Spawn `command` as a subprocess and tee its stdout and/or stderr
    to the given files.

    :param command: Command to spawn (see `subprocess.Popen`)
    :param stdout_fds: Iterable of writable fds for stdout
    :param stderr_fds: Iterable of writable fds for stderr
    :return: The process object after it has quit.
    """
    proc = subprocess.Popen(
        command,
        bufsize=0,
        stdout=(subprocess.PIPE if stdout_fds else None),
        stderr=(subprocess.PIPE if stderr_fds else None),
    )
    fd_map = {}
    if stdout_fds:
        fd_map[proc.stdout] = list(stdout_fds)
    if stderr_fds:
        fd_map[proc.stderr] = list(stderr_fds)

    while proc.poll() is None:
        try:
            r_fds, w_fds, x_fds = select(fd_map.keys(), [], [], 0.1)
            for from_fd in r_fds:
                data = from_fd.read(10240)
                if not data:  # EOF? Weird!
                    continue
                for to_fd in fd_map.get(from_fd, ()):
                    try:
                        to_fd.write(data)
                    except:
                        pass
        except:
            proc.kill()
            proc.wait(timeout=10)
            raise
    return proc
