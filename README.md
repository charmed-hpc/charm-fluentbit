# Fluentbit Charmed Operator

Charmed Operator for [Fluentbit](https://fluentbit.io). This subordinate charm
allows to forward logs to a centralized service.

## Quickstart

To deploy Fluentbit and forward logs from your Juju Application:

```bash
$ juju deploy fluentbit
$ juju relate fluentbit my-application
```

## Forwarding logs

This charm provides a library to facilitate forwarding logs from your charm to
a centralized place. To use it, pull the library (with `charmcraft fetch-lib
charmms.fluentbit.v0.fluentbit`) and instantiate a `FluentbitClient` class in
your charm:

```python
class MyCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)

        self._fluentbit = FluentbitClient(self, "fluentbit")

        self.framework.observe(self.on.fluentbit.relation_created,
                               self._fluentbit_relation_created)

    def _fluentbit_relation_created(self, event):
        cfg = [{"input": [("name",     "tail"),
                          ("path",     "/var/log/foo/bar.log"),
                          ("path_key", "filename"),
                          ("tag",      "foo"),
                          ("parser",   "bar")]},
               {"parser": [("name",        "bar"),
                           ("format",      "regex"),
                           ("regex",       "^\[(?<time>[^\]]*)\] (?<log>.*)$"),
                           ("time_key",    "time"),
                           ("time_format", "%Y-%m-%dT%H,%M,%S.%L")]}]
        self._fluentbit.configure(cfg)
```

Please see the library documentation for more details.

## Developing

The code follows PEP8 and PEP257. The supplied `Makefile` allows one to easily
lint and build the charm:

```bash
$ make lint
$ make charm
```

To deploy the locally built charm:

```bash
$ juju deploy ./fluentbit_ubuntu-20.04-amd64_centos-7-amd64.charm
```

## Contact

**We want to hear from you!**

Email us @ [info@omnivector.solutions](mailto:info@omnivector.solutions)

## Bugs

In the case things aren't working as expected, please
[file a bug](https://github.com/omnivector-solutions/charm-fluentbit/issues).

## License

The charm is maintained under the MIT license. See `LICENSE` file in this
directory for full preamble.

Copyright &copy; Omnivector Solutions 2021
