# Fluentbit Charmed Operator

Charmed Operator for [Fluentbit](https://fluentbit.io). This subordinate charm
allows to forward logs to a centralized service.

## Quickstart

To deploy Fluentbit and forward logs from your Juju Application:

```bash
$ juju deploy fluentbit
$ juju relate fluentbit my-application
```

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
[file a
bug](https://github.com/omnivector-solutions/charm-fluentbit/issues).

## License

The charm is maintained under the MIT license. See `LICENSE` file in this
directory for full preamble.

Copyright &copy; Omnivector Solutions 2021
