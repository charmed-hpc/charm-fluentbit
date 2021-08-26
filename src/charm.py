#!/usr/bin/env python3
"""FluentbitCharm."""

import logging
from pathlib import Path

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus

from fluentbit_ops import FluentbitOps

logger = logging.getLogger(__name__)


class FluentbitCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize charm."""

        super().__init__(*args)

        self._fluentbit = FluentbitOps()

        self._stored.set_default(installed=False)

        # juju core hooks
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.stop, self._on_stop)
        self.framework.observe(self.on.remove, self._on_remove)
        self.framework.observe(self.on.update_status, self._on_update_status)

    def _on_install(self, event):
        logger.debug("## Installing charm")
        self.unit.status = MaintenanceStatus("Installing Fluentbit")
        if self.model.unit.is_leader():
            self.unit.set_workload_version(Path("version").read_text().strip())

        if self._fluentbit.install():
            self.unit.status = ActiveStatus("Fluentbit installed")
            self._stored.installed = True
        else:
            self.unit.status = BlockedStatus("Error installing Fluentbit")
            event.defer()
            return

    def _on_upgrade_charm(self, event):
        """Perform charm upgrade operations."""
        logger.debug("## Upgrading charm")
        self.unit.status = MaintenanceStatus("Upgrading Fluentbit")
        if self.model.unit.is_leader():
            self.unit.set_workload_version(Path("version").read_text().strip())

        self.unit.status = ActiveStatus("Fluentbit upgraded")

    def _on_config_changed(self, event):
        """Handle configuration updates."""
        logger.debug("## TODO Configuring charm")
        # TODO
        #   - assemble basic config
        #   - assemble input, parsers
        #   - assemble outputs
        #   - restart daemon
        self._check_status()

    def _on_start(self, event):
        logger.debug("## Starting daemon")
        if not self._fluentbit.restart():
            event.defer()
        self._check_status()

    def _on_stop(self, event):
        logger.debug("## Stopping daemon")
        self._fluentbit.stop()

    def _on_remove(self, event):
        logger.debug("## TODO Uninstalling Fluentbit")
        self._fluentbit.uninstall()

    def _on_update_status(self, event):
        logger.debug("## Updating status")
        self._check_status()

    def _check_status(self):
        """Check status of the system.

        Returns:
            bool: True if the system is ready.
        """
        if not self._stored.installed:
            self.unit.status = MaintenanceStatus("Fluentbit not installed")
            return False

        if not self._fluentbit.is_active():
            self.unit.status = MaintenanceStatus("Fluentbit installed but not running")
            return False

        self.unit.status = ActiveStatus("Fluentbit started")
        return True


if __name__ == "__main__":
    main(FluentbitCharm)
