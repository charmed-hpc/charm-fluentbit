"""Fluentbit charm libraries.

To ship logs from your charm to a centralized place using Fluentbit,
instantiate the `FluentbitClient()` class and relate your charm to Fluentbit
charm.
"""

import logging
import json
from typing import List

from ops.framework import EventBase, EventSource, Object, ObjectEvents, StoredState
from ops.model import Relation

# The unique Charmhub library identifier, never change it
LIBID = "e7b5ae1460034b9fb67cd4ec6aa3e87f"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1

logger = logging.getLogger(__name__)


class FluentbitConfigurationAvailable(EventBase):
    """Emitted when configuration is available."""


class FluentbitEvents(ObjectEvents):
    """Fluentbit emitted events."""

    configuration_available = EventSource(FluentbitConfigurationAvailable)


class FluentbitProvider(Object):
    """Implement the provider side of the relation."""

    _state = StoredState()
    on = FluentbitEvents()

    def __init__(self, charm, relation_name: str):
        """Initialize the service provider.

        Arguments:
            charm: a `CharmBase` instance that manages this instance of the
                   Fluentbit service.
            relation_name: string name of the relation that provides the
                           Fluentbit logging service.
        """
        super().__init__(charm, relation_name)

        self.charm = charm
        self._relation_name = relation_name

        self._state.set_default(cfg=str())

        events = self.charm.on[relation_name]
        self.framework.observe(events.relation_changed, self._on_relation_changed)
        # TODO relation_broken should reconfigure with empty/default values,
        #      with care to not remove other entries from other relations

    def _on_relation_changed(self, event):
        """Get configuration from the client and trigger a reconfiguration."""
        cfg = event.relation.data[event.unit].get("configuration")
        logger.debug(f"## relation-changed: received: {cfg}")
        # TODO this only works for 1 relation, should extend for any number of
        #      relations, so it can support multiple outputs easily?
        if cfg:
            self._state.cfg = cfg
            self.on.configuration_available.emit()

    @property
    def configuration(self) -> List[dict]:
        """Get the stored configuration."""
        cfg = json.loads(self._state.cfg or '[]')
        logger.debug(f"## Fluentbit stored configuration: {cfg}")
        return cfg


class FluentbitClient(Object):
    """A client to relate to a Fluentbit Charm.

    This class implements the `requires` end of the relation, to configure
    Fluentbit.

    The instantiating class must handle the `relation_created` event to
    configure Fluentbit:
    """
    def __init__(self, charm, relation_name: str):
        """Initialize Fluentbit client.

        Arguments:
            charm: a `CharmBase` object that manages this `FluentbitClient`
                   object. Typically this is `self` in the instantiating class.
            relation_name: string name of the relation between `charm` and the
                           Fluentbit charmed service.
        """
        super().__init__(charm, relation_name)

        self._charm = charm
        self._relation_name = relation_name

    def configure(self, cfg: List[dict]):
        r"""Configure Fluentbit.

        Arguments:
            cfg: a list of stuff to setup. Example:
                [{"input": [("name",     "tail"),
                            ("path",     "/var/log/slurm/slurmd.log"),
                            ("path_key", "filename"),
                            ("tag",      "slurmd"),
                            ("parser",   "slurm")]},
                 {"parser": [("name",        "slurm"),
                             ("format",      "regex"),
                             ("regex",       "^\[(?<time>[^\]]*)\] (?<message>.*)$"),
                             ("time_key",    "time"),
                             ("time_format", "%Y-%m-%dT%H,%M,%S.%L")]},
        """
        # should we validate the input? how?
        logging.debug(f"## Seding configuration data to Fluentbit: {cfg}")
        self._relation.data[self.model.unit]["configuration"] = json.dumps(cfg)

    @property
    def _relation(self) -> Relation:
        """Return the relation."""
        return self.framework.model.get_relation(self._relation_name)
