# Meshify Python API

A python library for interacting with the Meshify API

## Requirements

-   [python3](https://www.python.org/downloads/)

## Installation

1.  Install the python package

    ```Shell
    pip3 install meshify
    ```

## Authentication

In order to retrieve data from Meshify, you must have a username and password to access the Meshify API. The username and password should be stored in environment variables MESHIFY_USERNAME nad MESHIFY_PASSWORD. If not stored, you will be prompted to enter username and password each time the script is run. You must also store or set MESHIFY_BASE_URL.

## Usage

### Help

Describes the usage of the function.

```Shell
meshify --help
Usage: meshify [OPTIONS] COMMAND [ARGS]...

  Command Line Interface.

Options:
  --help  Show this message and exit.

Commands:
  create_modbusmap       Create modbusMap.p from channel csv file.
  get_channel_csv        Query the meshify API and create a CSV of the...
  post_channel_csv       Post values from a CSV to Meshify Channel...
  print_channel_options  Print channel options for use with the csv...
```

### Getting Channel CSV file

Generates a CSV file of the existing channels for a devicetype. This function will check to see if there is a modbusMap.p file in order to generate the full configuration of the channels (for M1 Data Collection).

```Shell
meshify get_channel_csv --help
Usage: meshify get_channel_csv [OPTIONS] DEVICE_TYPE_NAME

  Query the meshify API and create a CSV of the current channels.

Options:
  -o, --output-file TEXT     Where to put the CSV of channels.
  -m, --modbusmap-file TEXT  The location of the modbusMap.p file
  --help                     Show this message and exit.
```

### Post Channel CSV

This function will examine a CSV file and POST all the channels to Meshify.

```Shell
meshify post_channel_csv --help
Usage: meshify post_channel_csv [OPTIONS] DEVICE_TYPE_NAME CSV_FILE

  Post values from a CSV to Meshify Channel API.

Options:
  --help  Show this message and exit.
```

### Print Channel Options

Helper function to print all posible options to enumerations within the CSV file.

```Shell
meshify print_channel_options --help
Usage: meshify print_channel_options [OPTIONS]

  Print channel options for use with the csv files.

Options:
  --help  Show this message and exit.
```


## Contributors

-   [Patrick McDonagh](https://github.com/patrickjmcd) - Owner
