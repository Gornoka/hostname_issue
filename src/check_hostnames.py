"""
check hostname issues
"""
import logging
import os
import pathlib
import random
import socket
import time

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
# global good enough for this script
logger = logging.getLogger()


def check_hostname(hostname) -> (bool, str):
    """
    check if hostname is correct
    Returns:
        status message of the hostname and a failure state
    """
    try:
        resolved_hostname = socket.getaddrinfo(hostname, 80)
        # only returning the ip of the results
        return True, ([x[4][0] for x in resolved_hostname])
    except socket.gaierror:
        return False, None


def get_hostnames_from_file(filename) -> list:
    """
    gets hostnames from a file, expects 1 hostname per line
    """
    fp = pathlib.Path(filename)
    if not fp.exists():
        return []
    with fp.open() as f:
        host_lines = f.readlines()
        # thanks windows
        return [x.strip() for x in host_lines]


def get_hostnames_from_files(filenames) -> list:
    """
    gets hostnames from a list of files
    """
    hostnames = []
    for filename in filenames.split("|"):
        hostnames.extend(get_hostnames_from_file(filename))
    return hostnames


def check_hostnames(hostnames) -> list:
    """
    check a list of hostnames
    """
    results = []
    for hn in hostnames:
        check_result = check_hostname(hn)
        if check_result[0]:
            logger.info(f"{hn} was resolved to {check_result[1]}")
        else:
            logger.warning(f"{hn} was not resolved")
        results.append(check_result)
    return results


def main():
    """
    continuously loop until user exits
    """
    logger.warning("script started")
    hostnames = get_hostnames_from_file(os.getenv("HOSTNAME_FILE", "None"))
    hostnames.extend(get_hostnames_from_files(os.getenv("HOSTNAME_FILES", "None")))
    initial_wait_time = int(os.getenv("INITIAL_WAIT_TIME", 0))
    loop_wait_time = int(os.getenv("LOOP_WAIT_TIME", 10))
    logger.info(f"Waiting {initial_wait_time} seconds before starting")
    time.sleep(initial_wait_time)
    restart_chance = float(os.getenv("RESTART_CHANCE", "0"))  # random chance to restart the script
    while True:
        try:
            loop_start = time.time()
            cr = check_hostnames(hostnames)
            successful_checks = [x for x in cr if x[0]]
            failed_checks = [x for x in cr if not x[0]]
            log_level = logging.WARNING
            if len(failed_checks) > 0:
                log_level = logging.ERROR
            logger.log(
                log_level,
                f"Checked {len(hostnames)} hostnames, "
                f"{len(successful_checks)} were successful, "
                f"{len(failed_checks)} failed",
            )
            sleep_time = max(loop_wait_time - (time.time() - loop_start), 0)
            logger.info(f"Sleeping for {sleep_time} seconds")
            if random.random() < restart_chance:
                logger.warning("Restarting script due to random chance")
                break

            # allow exiting during sleep, looses accuracy but is good enough for this
            for _ in range(int(sleep_time)):
                time.sleep(1)
        except KeyboardInterrupt:
            logger.warning("Exiting as requested by user")
            break


if __name__ == "__main__":
    main()
