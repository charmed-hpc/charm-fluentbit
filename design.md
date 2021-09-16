# Design considerations

## Configuration

Configuration must encode inputs, filters, parsers, and outputs. Examples:

```bash
# td-agent-bit.conf
[INPUT]
    name     tail
    path     /var/log/slurm/slurmd.log
    path_key filename
    tag      slurmd
    parser   slurm

[OUTPUT]
    Name                   gelf
    Match                  slurmd
    Host                   10.220.130.119
    Port                   12201
    Mode                   udp
    Gelf_Short_Message_Key message

[PARSER]
    Name        slurm
    Format      regex
    Regex       ^\[(?<time>[^\]]*)\] (?<message>.*)$
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L

[MULTILINE_PARSER]
    Name               nhc
    Type               regex
    Flush_timeout      1000
    Rule "start_state" "/^([\d]{8} [\d:]*) (.*)/" "cont"
    Rule "cont"        "/^([^\d].*)/"             "cont"
```

Note: the configuration file is white-space sensitive. If one of the lines have
a different indentation (one empty space different) than the others, the
service crashes.

Note: Fluentbit requires two configuration files: one for the parsers, and one
for the other topics. They cannot be mixed: if the main configuration file
includes a `PARSER` entry, the configuration file will crash the service.

The Charm must accept a configuration "object" in two situations: via charm
config and via charm-relation. They should be compatible to each other.

### Attempt 1 - relation data

My first attempt to configure the charm was to pass the configuration as a list
of dictionaries. This has the advantage of not having to validate indentation
from user's input, as well as having 1 option to configure the two files.

Each dictionary would then encode an input/filter/parser/output:

```python
cfg = [{"input": {"name":     "tail",
                  "path":     "/var/log/slurm/slurmd.log",
                  "path_key": "filename",
                  "tag":      "slurmd",
                  "parser":   "slurm"}},
       {"parser": {"name":        "slurm",
                   "format":      "regex",
                   "regex":       "^\[(?<time>[^\]]*)\] (?<message>.*)$",
                   "time_key":    "time",
                   "time_format": "%Y-%m-%dT%H:%M:%S.%L"}},
       {"input": {"name":             "tail",
                  "path":             "/var/log/nhc.log",
                  "path_key":         "filename",
                  "tag":              "nhc",
                  "multiline.parser": "nhc"}},
       {"multiline_parser": {"name":          "nhc",
                             "format":        "regex",
                             "flush_timeout": "1000",
                             "rule":          '"start_state" "/^([\d]{8} [\d:]*) (.*)/" "cont"',
                             "rule":          '"cont"        "/^([^\d].*)/"             "cont"'}}]
```

But this has a problem: we can't have repeated keys in a dictionary. See last
two lines in the example above.

### Attempt 2 - relation data

Solution: use a list of dictionaries, where each dictionary encode an
input/filter/parser/output as a list of tuples:

```python
cfg = [{"input": [("name",     "tail"),
                  ("path",     "/var/log/slurm/slurmd.log"),
                  ("path_key", "filename"),
                  ("tag",      "slurmd"),
                  ("parser",   "slurm")]},
       {"parser": [("name",        "slurm"),
                   ("format",      "regex"),
                   ("regex",       "^\[(?<time>[^\]]*)\] (?<message>.*)$"),
                   ("time_key",    "time"),
                   ("time_format", "%Y-%m-%dT%H,%M,%S.%L")]},
       {"input": [("name",             "tail"),
                  ("path",             "/var/log/nhc.log"),
                  ("path_key",         "filename"),
                  ("tag",              "nhc"),
                  ("multiline.parser", "nhc")]},
       {"multiline_parser": [("name",          "nhc"),
                             ("format",        "regex"),
                             ("flush_timeout", "1000"),
                             ("rule",          '"start_state" "/^([\d]{8} [\d:]*) (.*)/" "cont"'),
                             ("rule",          '"cont"        "/^([^\d].*)/"             "cont"')]}]
```

Why not a list of `defaultdict(list)`? IMO, using "obscure" (in the sense that
it is not commonly used) data structures increases the difficulty using the
code. This is a charm library, that will (hopefully) be used by other charm
authors as well.
