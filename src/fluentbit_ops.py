"""Fluentbit operations."""

import logging
import shlex
import subprocess
import shutil
from pathlib import Path

from utils import operating_system

logger = logging.getLogger()


class FluentbitOps:
    """Fluentbit ops."""

    def __init__(self):
        """Initialize class."""
        logger.debug("## Initializing FluentBitOps")

        self._template_dir = Path(__file__).parent.parent / "templates"
        self._systemd_service = "td-agent-bit.service"

    def install(self) -> bool:
        """Install fluentbit on the machine.

        Returns:
            bool: whether the installation was succesfull or not
        """
        os_ = operating_system()
        if "ubuntu" == os_[0]:
            return self._install_on_ubuntu()
        elif "centos" == os_[0]:
            return self._install_on_centos()
        else:
            logger.error(f"## Unsupported operating system: {os_}")
            return False

    def _install_on_ubuntu(self) -> bool:
        """Install fluentbit on Ubuntu 20.04.

        Returns:
            bool: whether the installation was succesfull or not
        """
        logger.debug("## Configuring APT to install fluentbit on Ubuntu")

        try:
            key = self._template_dir / "fluentbit.key"
            cmd = f"apt-key add {key.as_posix()}"
            subprocess.check_output(shlex.split(cmd))

            repo = "deb https://packages.fluentbit.io/ubuntu/focal focal main"
            cmd = f'add-apt-repository "{repo}"'
            subprocess.check_output(shlex.split(cmd))

            logger.debug("## Installing fluentbit")
            cmd = "apt-get install --yes td-agent-bit"
            subprocess.check_output(shlex.split(cmd))

            logger.debug("## Fluentbit installed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"## Error installing fluentbit: {e}")
            return False

    def _install_on_centos(self) -> bool:
        """Install fluentbit on CentOS 7.

        Returns:
            bool: whether the installation was succesfull or not
        """
        logger.debug("## Configuring yum to install fluentbit on Centos")

        try:
            repo = self._template_dir / "td-agent-bit.yum.repo"
            target = Path("/etc/yum.repos.d/td-agent-bit.repo")
            shutil.copyfile(repo, target)
        except OSError as e:
            logger.error(f"## Error setting yum repo: {e}")
            return False

        try:
            logger.debug("## Installing fluentbit")
            cmd = "yum install --assumeyes td-agent-bit"
            subprocess.check_output(shlex.split(cmd))

            logger.debug("## Fluentbit installed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"## Error installing fluentbit: {e}")
            return False

    def restart(self) -> bool:
        """Restart the fluebtbit service.

        If the service is not running, start it.

        Returns:
            bool: wether the process (re)started successfully.
        """
        logger.debug(f"## Restarting {self._systemd_service}")
        try:
            cmd = f"systemctl restart {self._systemd_service}"
            subprocess.check_output(shlex.split(cmd))
        except subprocess.CalledProcessError as e:
            logger.error(f"## Error restarting fluentbit: {e}")
            return False

        return self.is_active()

    def is_active(self) -> bool:
        """Check wether the service is running."""

        try:
            cmd = f"systemctl is-active {self._systemd_service}"
            r = subprocess.check_output(shlex.split(cmd))
            return "active" == r.decode().strip().lower()
        except subprocess.CalledProcessError as e:
            logger.error(f'## Error checking fluentbit service: {e}')
            return False

    def stop(self):
        """Stop and disable the fluentbit service."""
        logger.debug(f"## Stoping {self._systemd_service}")
        try:
            cmd = f"systemctl disable --now {self._systemd_service}"
            subprocess.check_output(shlex.split(cmd))
        except subprocess.CalledProcessError as e:
            logger.error(f"## Error stoping fluentbit: {e}")

    def uninstall(self):
        """Uninstall package.

        Also removes custom repositories but not custom configuration files.
        """
        os_ = operating_system()
        if "ubuntu" == os_[0]:
            self._uninstall_on_ubuntu()
        elif "centos" == os_[0]:
            self._uninstall_on_centos()
        else:
            logger.error(f"## Unsupported operating system: {os_}")

    def _uninstall_on_ubuntu(self):
        logger.debug("## Removing fluentbit package")
        cmd = "apt-get purge --yes td-agent-bit"
        subprocess.check_output(shlex.split(cmd))

        logger.debug("## Removing fluentbit repository")
        repo = "deb https://packages.fluentbit.io/ubuntu/focal focal main"
        cmd = f'add-apt-repository --remove "{repo}"'
        subprocess.check_output(shlex.split(cmd))

    def _uninstall_on_centos(self):
        logger.debug("## Removing fluentbit package")
        cmd = "yum remove --assumeyes td-agent-bit"
        subprocess.check_output(shlex.split(cmd))

        logger.debug("## Removing fluentbit repository")
        Path("/etc/yum.repos.d/td-agent-bit.repo").unlink()
