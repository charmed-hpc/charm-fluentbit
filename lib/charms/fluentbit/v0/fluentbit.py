"""TODO: Add a proper docstring here.

This is a placeholder docstring for this charm library. Docstrings are
presented on Charmhub and updated whenever you push a new version of the
library.

Complete documentation about creating and documenting libraries can be found
in the SDK docs at https://juju.is/docs/sdk/libraries.

See `charmcraft publish-lib` and `charmcraft fetch-lib` for details of how to
share and consume charm libraries. They serve to enhance collaboration
between charmers. Use a charmer's libraries for classes that handle
integration with their charm.

Bear in mind that new revisions of the different major API versions (v0, v1,
v2 etc) are maintained independently.  You can continue to update v0 and v1
after you have pushed v3.

Markdown is supported, following the CommonMark specification.
"""

import logging
import json
from typing import List

from ops.relation import ConsumerBase, EventBase, EventSource, ObjectEvents, ProviderBase

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


class FluentbitProvides(ProviderBase):
    """Implement the provider side of the relation."""

    _state = StoredState()
    on = FluentbitEvents()

    def __init__(self, charm, relation_name: str, service: str, version: str):
        """Initialize the service provider.

        Arguments:
            charm: a `CharmBase` instance that manages this instance of the
                   Fluentbit service.
            relation_name: string name of the relation that provides the
                           Fluentbit logging service.
            service: string name of service provided. This is used by
                     `FluentbitClient` to validate this service as acceptable.
                     Hence the string name must match one of the acceptable
                     service names in the `FluentbitClient`s `consumes`
                     argument. Typically this string is just "fluentbit".
            version: a string providing the semantic version of the Fluentbit
                     application being provided.
        """
        super().__init__(charm, relation_name, service, version)

        self.charm = charm
        self._relation_name = relation_name

        self._state.set_default(cfg=list())

        events = self.charm.on[relation_name]
        self.framework.observe(events.relation_changed, self._on_relation_changed)
        # TODO relation_broken should reconfigure with empty/default values

    def _on_relation_changed(self, event):
        """Get configuration from the client and trigger a reconfiguration."""
        cfg = event.relation.data[event.unit].get("configuration")
        logger.debug(f"## relation-changed: received: {cfg}")
        if cfg:
            self._state.cfg = json.loads(cfg)
            self.on.configuration_available.emit()

    @property
    def configuration(self) -> List[dict]:
        """Get the stored configuration."""
        return self._stored.cfg.copy()


class FluentbitClient(ConsumerBase):
    """A client to relate to a Fluentbit Charm.

    This class implements the `requires` end of the relation, to configure
    Fluentbit.
    """
    def __init__(self, charm, relation_name: str, consumes: str, multi: bool = False):
        """Initialize Fluentbit client.

        Arguments:
            charm: a `CharmBase` object that manages this `FluentbitClient`
                   object. Typically this is `self` in the instantiating class.
            relation_name: string name of the relation between `charm` and the
                           Fluentbit charmed service.
            consumes: a dictionary of acceptable logging service providers. The
                      keys of the dictionary are string names of logging
                      service providers. For Fluentbit, this is typically
                      "fluentbit". The values of the dictionary are
                      corresponding minimal acceptable semantic version
                      specfications for the logging service.
        """
        super().__init__(charm, relation_name, consumes, multi)

        self._charm = charm
        self._relation_name = relation_name

    def configure(self, cfg: List[dict]):
        r"""Configure Fluentbit.

        Arguments:
            cfg: a list of stuff to setup. Example:
                [{"input": {"name": "gelf",
                            "path": "/var/log/foo.log",
                            "path_key": "filename",
                            "tag": "foo",
                            "parser": "foo"}},
                 {"parser": {"name": "foo",
                             "format": "regex",
                             "regex": "^\[(?<time>[^\]]*)\] (?<message>.*)$",
                             "time_key": "time",
                             "time_format": "%Y-%m-%dT%H:%M:%S.%L"}},
                ]
        """
        # should we validate the input? how?
        logging.debug(f"## Seding configuration data to Fluentbit: {cfg}")
        self._relation.data[self.model.unit]["configuration"] = json.dumps(cfg)
