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

## Installation and usage

Install the package in editable mode:
```bash
    python -m pip install -e .
```

Run the tool from the command line:

```bash
    python -m logextractor -i example.log -c message-patterns.json
```
This extracts log entries matching the selected profile and writes the results
to the configured output file.  

Configuration files are located in the config/ directory and can be referenced by name.  
Example profiles include:
* ```error-focused.json```
* ```warning-focused.json```
* ```source-focused.json```
* ```message-patterns.json```
* ```noise-reduction.json```
* ```broad-analysis.json```

Arguments:

| Argument       | Description |
|----------------|------------|
| `-i, --input`  | Path to the log file |
| `-c, --config` | Path to the JSON configuration |
| `-y, --year`   | Year used when parsing syslog timestamps (defaults to current year) |

## Project structure
src/logextractor  
├─ config       # configuration loading  
├─ domain       # data models  
├─ extraction   # log processing pipeline  
├─ filtering    # rule matching  
├─ parsing      # log parsing  
├─ reporting    # output writer  
├─ cli.py       # command line interface  
├─ constants.py # shared constant values 
└─ __main__.py  # module entry point 

## Status

Early-stage development. Core log parsing, rule matching, and CLI-based extraction are implemented. 
