'''Ansible Deploy Service
'''
import argparse
import datetime as dt
import json
import logging
import logging.handlers
import os
import subprocess
import sys
from pathlib import Path
from time import sleep
from typing import Dict, Optional

import platformdirs
from git import Repo
from prometheus_client import Gauge, start_http_server

import docker


class Service:
    def __init__(self, period: int,
                 prometheus_port: int,
                 project_root: Path,
                 project_branch: str,
                 check: bool):
        self.PERIOD = dt.timedelta(seconds=period)
        self.PROM_PORT = prometheus_port

        self.PROJECT_ROOT = project_root
        self.repo = Repo(self.PROJECT_ROOT)
        self.__project_branch_name = project_branch
        self.PROJECT_BRANCH = {
            head.name: head for head in self.repo.heads}[self.__project_branch_name]
        self.CHECK_FLAG = check

        self.__app_dirs = platformdirs.PlatformDirs('ansible_deploy_service')
        log_dest = self.__app_dirs.user_log_path
        self.__last_time_path = self.__app_dirs.user_data_path.joinpath(
            'last_time')
        self.__last_deploy_time_path = self.__app_dirs.user_data_path.joinpath(
            'last_deploy_time')
        self.__last_run_retvals_path = self.__app_dirs.user_data_path / 'last_retvals'

        self.__app_dirs.user_data_path.mkdir(parents=True, exist_ok=True)
        log_dest.mkdir(parents=True, exist_ok=True)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        master_log_file = logging.handlers.TimedRotatingFileHandler(
            log_dest.joinpath('ansible_service.log'),
            when='d',
            interval=1,
            backupCount=15)
        master_log_file.setLevel(logging.DEBUG)

        date_fmt = '%Y-%m-%dT%H:%M:%S'
        log_fmt: str = '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s'
        root_formatter = logging.Formatter(log_fmt,
                                           datefmt=date_fmt)
        master_log_file.setFormatter(root_formatter)
        root_logger.addHandler(master_log_file)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        error_formatter = logging.Formatter(log_fmt,
                                            datefmt=date_fmt)
        console_handler.setFormatter(error_formatter)
        root_logger.addHandler(console_handler)

        self.__log = logging.getLogger('Ansible Deploy')

        self.__log.info('Invoked with %s', sys.orig_argv)

    def run(self):
        try:
            self.__log.debug('Running')
            start_http_server(self.PROM_PORT)

            self.last_run_gauge = Gauge('ads_last_run', 'Last Run Timestamp')
            self.last_deploy_gauge = Gauge(
                'ads_last_deploy', 'Last Deploy Timestamp')

            if self.last_run:
                self.last_run_gauge.set(self.last_run.timestamp())

            if self.last_deploy_time:
                self.last_deploy_gauge.set(self.last_deploy_time.timestamp())

            self.subprocess_retval_gauge = Gauge(
                'ads_subprocess_retval', 'Subprocess return values', labelnames=['command'])

            self.get_retvals()

            while True:
                if self.last_run:
                    next_run = self.last_run + self.PERIOD
                    self.__log.debug('Sleeping until %s', next_run.isoformat())
                    self.sleep_until(next_run)

                self.PROJECT_BRANCH.checkout(True)
                self.repo.remote().update()

                remote_head = {ref.remote_head: ref for ref in self.repo.remote().refs}[
                    self.__project_branch_name]

                origin_diff = self.PROJECT_BRANCH.commit.diff(
                    remote_head.commit)
                if len(origin_diff) != 0:
                    # Install
                    self.__log.info('Installing')
                    self.repo.remote().pull()
                    new_env = os.environ
                    galaxy_install = subprocess.check_call(['.venv/bin/ansible-galaxy', 'collection', 'install',
                                                            '-r', 'requirements.yml'], env=new_env)
                    self.__log.info(
                        'Galaxy install returned %d', galaxy_install)
                    self.set_retval('ansible-galaxy', galaxy_install)
                    new_env['ANSIBLE_CONFIG'] = self.PROJECT_ROOT.joinpath(
                        'ansible.cfg').absolute().as_posix()
                    new_env['ANSIBLE_INVENTORY'] = self.PROJECT_ROOT.joinpath(
                        'inventory.yaml').absolute().as_posix()
                    
                    self.__log.info("Getting bitwarden session.")
                    bw_session_path = self.PROJECT_ROOT.joinpath('.bw_session')
                    with open(bw_session_path, 'r', encoding='utf-8') as handle:
                        bw_session = handle.read()
                    new_env['BW_SESSION'] = bw_session

                    self.__log.info("Getting ansible playbook executable")
                    playbook_cmd = [
                        '.venv/bin/ansible-playbook',
                    ]
                    if self.CHECK_FLAG:
                        playbook_cmd.append('--check')

                    self.__log.info("Running Ansible Playbook.")
                    playbook_cmd.append('playbook.yaml')
                    playbook_run = subprocess.check_call(
                        playbook_cmd, env=new_env, cwd=self.PROJECT_ROOT)
                    self.set_retval('ansible-playbook', playbook_run)

                    # docker_client = docker.from_env()
                    # docker_client.images.prune()

                    self.__log.info("Installing poetry.")
                    poetry_install = subprocess.check_call(
                        ['.venv/bin/poetry', 'install'], env=new_env)
                    self.set_retval('poetry-install', poetry_install)
                    self.last_run = dt.datetime.now()
                    self.last_deploy_time = dt.datetime.now()

                    self.__log("Redeploying...")
                    exec_args = sys.executable, os.path.abspath(
                        __file__), *sys.argv[1:]
                    self.__log.info('Redeploy with args %s', exec_args)
                    os.execle(*exec_args, os.environ)
                self.last_run = dt.datetime.now()
        except Exception as exc:
            self.__log.exception('Fails due to %s', exc)

    def sleep_until(self, until: dt.datetime):
        """Sleeps until the specified datetime

        Args:
            until (dt.datetime): Datetime to sleep until
        """
        now = dt.datetime.now()
        delta = (until - now).total_seconds()
        if delta < 0:
            return
        sleep(delta)

    @property
    def last_run(self) -> Optional[dt.datetime]:
        try:
            with open(self.__last_time_path, 'r', encoding='utf-8') as handle:
                return dt.datetime.fromisoformat(handle.read())
        except:
            return None

    @last_run.setter
    def last_run(self, date_time: dt.datetime):
        with open(self.__last_time_path, 'w', encoding='utf-8') as handle:
            handle.write(date_time.isoformat())
        self.last_run_gauge.set(date_time.timestamp())

    @property
    def last_deploy_time(self) -> Optional[dt.datetime]:
        try:
            with open(self.__last_deploy_time_path, 'r', encoding='utf-8') as handle:
                return dt.datetime.fromisoformat(handle.read())
        except:
            return None

    @last_deploy_time.setter
    def last_deploy_time(self, date_time: dt.datetime):
        with open(self.__last_deploy_time_path, 'w', encoding='utf-8') as handle:
            handle.write(date_time.isoformat())
        self.last_deploy_gauge.set(date_time.timestamp())

    def set_retval(self, command: str, retval: int):
        try:
            with open(self.__last_run_retvals_path, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
        except:
            data = {}
        data[command] = retval
        self.subprocess_retval_gauge.labels(command=command).set(retval)
        with open(self.__last_run_retvals_path, 'w', encoding='utf-8') as handle:
            json.dump(data, handle)

    def get_retvals(self):
        try:
            with open(self.__last_run_retvals_path, 'r', encoding='utf-8') as handle:
                data: Dict[str, int] = json.load(handle)
            for command, retval in data.items():
                self.subprocess_retval_gauge.labels(
                    command=command).set(retval)
        except:
            pass


def main():
    """Main entry point
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--period', type=int,
                        help='Seconds between runs', default=60)
    parser.add_argument('--prometheus_port', type=int,
                        help='Prometheus port', default=9000)
    parser.add_argument('--project_root', type=Path,
                        help='Ansible project root', default=Path('.'))
    parser.add_argument('--project_branch', type=str,
                        help='Project branch', default='main')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()

    Service(period=args.period,
            prometheus_port=args.prometheus_port,
            project_root=args.project_root,
            project_branch=args.project_branch,
            check=args.check).run()


if __name__ == '__main__':
    main()
