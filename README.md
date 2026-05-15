# logextractor

A CLI tool for extracting relevant log lines from large application log files.

The tool parses supported log formats, applies configurable keyword-based filtering, and writes matching log entries to an output file or prints them to the console.

## Features

- Parse ISO-style and syslog-style log files
- Filter log entries using configurable JSON keyword filters
- Include lines containing specific keywords
- Exclude unwanted log entries globally
- Start time windows from trigger keywords
- Process all `.log` files in the `logs/` directory automatically
- Extract matching entries to a readable output file
- Run directly from the command line

## Installation and usage

Install the package in editable mode:
```bash
    python -m pip install -e .
```

Run the tool from the command line:  
```bash
    python -m logextractor -c config.json
```
This extracts log entries matching the selected configuration and writes the results
to the output file.

The tool reads all .log files from the logs/ directory in the project root.
If any file in that directory is not a .log file, the program raises an exception.

Configuration files are located in the config/ directory and can be referenced by name.

The tool can also be run without a configuration file by using manual arguments. Example:
```bash
    python -m logextractor -m --include error --print
```
Arguments:

| Argument        | Description |
|----------------|------------|
| `-c, --config` | Path to the JSON configuration |
| `-m, --manual` | Use manual CLI arguments instead of a configuration file |
| `--include`    | Keywords for lines that should be included |
| `--trigger`    | Keywords for lines that should start a time window |
| `--exclude`    | Keywords for lines that should always be excluded |
| `--duration`   | Number of seconds to include after a trigger match |
| `-o, --output` | Path to the output file |
| `-y, --year`   | Year used when parsing syslog timestamps (defaults to current year) |
| `--print`      | Print matching lines to the console instead of writing to file |

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

Early-stage development. Core log parsing, keyword-based filtering, trigger-based time window extraction, and CLI-based execution are implemented.