# logextractor

A rule-based CLI tool for extracting relevant events and context from large application log files.

The tool parses syslog-style log files, applies configurable filtering rules, and writes matching log entries to an output file.

## Features

- Parse syslog-style application logs
- Filter log entries using configurable JSON rules
- Match by log level, process, logger, or message fragments
- Exclude unwanted log entries globally
- Extract matching entries to a readable output file
- Run directly from the command line

## Project structure
src/logextractor  
├─ config       # configuration loading  
├─ domain       # data models  
├─ extraction   # log processing pipeline  
├─ filtering    # rule matching  
├─ parsing      # log parsing  
├─ reporting    # output writer  
├─ cli.py       # command line interface  
└─ __main__.py  # module entry point  

## Installation and usage

Install the package in editable mode:
```bash
  python -m pip install -e .
```

Run the tool from the command line:

```bash
    python -m logextractor --input sample.log --config config/example-config.json --year 2026
```

Arguments:

| Argument | Description |
|----------|-------------|
| `--input` | Path to the log file |
| `--config` | Path to the JSON configuration |
| `--year` | Year used when parsing syslog timestamps |

## Status

Early-stage development. Core log parsing, rule matching, and CLI-based extraction are implemented. 