import os
import signal
import sys
import time


from integritybackend import config
from integritybackend.asset_helper import AssetHelper
from integritybackend.fs_watcher import FsWatcher
from integritybackend.log_helper import LogHelper


_logger = LogHelper.getLogger()
_procs = list()


def signal_handler(signum, frame):
    """
    SIGINT handler for the main process.
    """
    _logger.info("Terminating processes...")
    kill_processes(_procs)
    sys.exit(0)


def kill_processes(procs):
    for proc in procs:
        if proc.is_alive():
            try:
                proc.terminate()

                # Allow up to 10 seconds for the process to terminate
                i = 0
                while proc.is_alive() and i < 20:
                    time.sleep(0.5)
                    i += 1
            except os.error as err:
                _logger.warning("Caught error while killing processes: %s", err)

        if proc.is_alive():
            _logger.info("Process %s [%s] is not terminated" % (proc.pid, proc.name))
        else:
            _logger.info("Process %s [%s] is terminated" % (proc.pid, proc.name))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    # Configure asset directories.
    for org_id in config.ORGANIZATION_CONFIG.all_orgs():
        AssetHelper(org_id).init_dirs()

    # Start up processes for services.
    _procs = FsWatcher.init_all(config.ORGANIZATION_CONFIG)

    for proc in _procs:
        proc.start()
