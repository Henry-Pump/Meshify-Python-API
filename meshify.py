"""Query Meshify for data."""
import requests
import json
import csv
import click
from os import getenv
import getpass
import pickle
from pathlib import Path


MESHIFY_BASE_URL = getenv("MESHIFY_BASE_URL")
MESHIFY_USERNAME = getenv("MESHIFY_USERNAME")
MESHIFY_PASSWORD = getenv("MESHIFY_PASSWORD")
MESHIFY_AUTH = None


class NameNotFound(Exception):
    """Thrown when a name is not found in a list of stuff."""

    def __init__(self, message, name, list_of_stuff, *args):
        """Initialize the NameNotFound Exception."""
        self.message = message
        self.name = name
        self.list_of_stuff = list_of_stuff
        super(NameNotFound, self).__init__(message, name, list_of_stuff, *args)


def dict_filter(it, *keys):
    """Filter dictionary results."""
    for d in it:
        yield dict((k, d[k]) for k in keys)


def check_setup():
    """Check the global parameters."""
    global MESHIFY_USERNAME, MESHIFY_PASSWORD, MESHIFY_AUTH, MESHIFY_BASE_URL
    if not MESHIFY_USERNAME or not MESHIFY_PASSWORD:
        print("Simplify the usage by setting the meshify username and password as environment variables MESHIFY_USERNAME and MESHIFY_PASSWORD")
        MESHIFY_USERNAME = input("Meshify Username: ")
        MESHIFY_PASSWORD = getpass.getpass("Meshify Password: ")

    MESHIFY_AUTH = requests.auth.HTTPBasicAuth(MESHIFY_USERNAME, MESHIFY_PASSWORD)

    if not MESHIFY_BASE_URL:
        print("Simplify the usage by setting the environment variable MESHIFY_BASE_URL")
        MESHIFY_BASE_URL = input("Meshify Base URL: ")


def find_by_name(name, list_of_stuff):
    """Find an object in a list of stuff by its name parameter."""
    for x in list_of_stuff:
        if x['name'] == name:
            return x
    raise NameNotFound("Name not found!", name, list_of_stuff)


def query_meshify_api(endpoint):
    """Make a query to the meshify API."""
    check_setup()
    if endpoint[0] == "/":
        endpoint = endpoint[1:]
    q_url = MESHIFY_BASE_URL + endpoint
    q_req = requests.get(q_url, auth=MESHIFY_AUTH)
    return json.loads(q_req.text) if q_req.status_code == 200 else []


def post_meshify_api(endpoint, data):
    """Post data to the meshify API."""
    check_setup()
    q_url = MESHIFY_BASE_URL + endpoint
    q_req = requests.post(q_url, data=json.dumps(data), auth=MESHIFY_AUTH)
    if q_req.status_code != 200:
        print(q_req.status_code)
    return json.loads(q_req.text) if q_req.status_code == 200 else []


def decode_channel_parameters(channel):
    """Decode a channel object's parameters into human-readable format."""
    channel_types = {
        1: 'device',
        5: 'static',
        6: 'user input',
        7: 'system'
    }

    io_options = {
        0: 'readonly',
        1: 'readwrite'
    }

    datatype_options = {
        1: "float",
        2: 'string',
        3: 'integer',
        4: 'boolean',
        5: 'datetime',
        6: 'timespan',
        7: 'file',
        8: 'latlng'
    }

    channel['channelType'] = channel_types[channel['channelType']]
    channel['io'] = io_options[channel['io']]
    channel['dataType'] = datatype_options[channel['dataType']]
    return channel


def encode_channel_parameters(channel):
    """Encode a channel object from human-readable format."""
    channel_types = {
        'device': 1,
        'static': 5,
        'user input': 6,
        'system': 7
    }

    io_options = {
        'readonly': False,
        'readwrite': True
    }

    datatype_options = {
        "float": 1,
        'string': 2,
        'integer': 3,
        'boolean': 4,
        'datetime': 5,
        'timespan': 6,
        'file': 7,
        'latlng': 8
    }

    channel['deviceTypeId'] = int(channel['deviceTypeId'])
    channel['fromMe'] = channel['fromMe'].lower() == 'true'
    channel['channelType'] = channel_types[channel['channelType'].lower()]
    channel['io'] = io_options[channel['io'].lower()]
    channel['dataType'] = datatype_options[channel['dataType'].lower()]
    # channel['id'] = 1
    return channel


def make_modbusmap_channel(i, chan, device_type_name):
    """Make a channel object for a row in the CSV."""
    json_obj = {
        "ah": "",
        "bytary": None,
        "al": "",
        "vn": chan['subTitle'],  # Name
        "ct": "number",  # ChangeType
        "le": "16",   # Length(16 or 32)
        "grp": str(chan['guaranteedReportPeriod']),  # GuaranteedReportPeriod
        "la": None,
        "chn": chan['name'],  # ChannelName
        "un": "1",  # DeviceNumber
        "dn": device_type_name,  # deviceName
        "vm": None,
        "lrt": "0",
        "da": "300",  # DeviceAddress
        "a": chan['helpExplanation'],  # TagName
        "c": str(chan['change']),  # Change
        "misc_u": str(chan['units']),  # Units
        "f": "1",  # FunctionCode
        "mrt": str(chan['minReportTime']),  # MinimumReportTime
        "m": "none",  # multiplier
        "m1ch": "2-{}".format(i),
        "mv": "0",  # MultiplierValue
        "s": "On",
        "r": "{}-{}".format(chan['min'], chan['max']),  # range
        "t": "int"  # type
    }
    return json_obj


def combine_modbusmap_and_channel(channel_obj, modbus_map):
    """Add the parameters from the modbus map to the channel object."""
    channel_part = modbus_map["1"]["addresses"]["300"]
    for c in channel_part:
        if channel_part[c]["chn"] == channel_obj['name']:
            min_max_range = channel_part[c]["r"].split("-")
            channel_obj['units'] = channel_part[c]["misc_u"]
            channel_obj['min'] = int(min_max_range[0])
            channel_obj['max'] = int(min_max_range[1])
            channel_obj['change'] = float(channel_part[c]["c"])
            channel_obj['guaranteedReportPeriod'] = int(channel_part[c]["grp"])
            channel_obj['minReportTime'] = int(channel_part[c]["mrt"])
            return channel_obj
    return False


@click.group()
def cli():
    """Command Line Interface."""
    pass


@click.command()
@click.argument("device_type_name")
@click.option("-o", '--output-file', default=None, help="Where to put the CSV of channels.")
@click.option("-m", '--modbusmap-file', default="modbusMap.p", help="The location of the modbusMap.p file")
def get_channel_csv(device_type_name, output_file, modbusmap_file):
    """Query the meshify API and create a CSV of the current channels."""
    channel_fieldnames = [
        'id',
        'name',
        'deviceTypeId',
        'fromMe',
        'io',
        'subTitle',
        'helpExplanation',
        'channelType',
        'dataType',
        'defaultValue',
        'regex',
        'regexErrMsg',
        'units',
        'min',
        'max',
        'change',
        'guaranteedReportPeriod',
        'minReportTime'
    ]
    devicetypes = query_meshify_api('devicetypes')
    this_devicetype = find_by_name(device_type_name, devicetypes)
    channels = query_meshify_api('devicetypes/{}/channels'.format(this_devicetype['id']))
    modbusMap = None

    if Path(modbusmap_file):
        with open(modbusmap_file, 'rb') as open_mbs_file:
            modbusMap = pickle.load(open_mbs_file)

    if not output_file:
        output_file = 'channels_{}.csv'.format(device_type_name)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=channel_fieldnames)

        writer.writeheader()
        for ch in channels:
            if not modbusMap:
                ch['units'] = None
                ch['min'] = None
                ch['max'] = None
                ch['change'] = None
                ch['guaranteedReportPeriod'] = None
                ch['minReportTime'] = None
            else:
                combined = combine_modbusmap_and_channel(ch, modbusMap)
                if combined:
                    ch = combined
            writer.writerow(decode_channel_parameters(ch))

    click.echo("Wrote channels to {}".format(output_file))


@click.command()
@click.argument("device_type_name")
@click.argument("csv_file")
def post_channel_csv(device_type_name, csv_file):
    """Post values from a CSV to Meshify Channel API."""
    devicetypes = query_meshify_api('devicetypes')
    this_devicetype = find_by_name(device_type_name, devicetypes)

    with open(csv_file, 'r') as inp_file:
        reader = csv.DictReader(inp_file)
        for row in dict_filter(reader, 'name',
                               'deviceTypeId',
                               'fromMe',
                               'io',
                               'subTitle',
                               'helpExplanation',
                               'channelType',
                               'dataType',
                               'defaultValue',
                               'regex',
                               'regexErrMsg'):
            # print(row)
            # print(encode_channel_parameters(row))
            # click.echo(json.dumps(encode_channel_parameters(row), indent=4))
            if post_meshify_api('devicetypes/{}/channels'.format(this_devicetype['id']), encode_channel_parameters(row)):
                click.echo("Successfully added channel {}".format(row['name']))
            else:
                click.echo("Unable to add channel {}".format(row['name']))


@click.command()
def print_channel_options():
    """Print channel options for use with the csv files."""
    channel_types = ['device', 'static', 'user input', 'system']
    io_options = ['readonly', 'readwrite']
    datatype_options = ["float", 'string', 'integer', 'boolean', 'datetime', 'timespan', 'file', 'latlng']

    click.echo("\n\nchannelType options")
    click.echo("===================")
    for c in channel_types:
        click.echo(c)

    click.echo("\n\nio options")
    click.echo("==========")
    for i in io_options:
        click.echo(i)

    click.echo("\n\ndataType options")
    click.echo("================")
    for d in datatype_options:
        click.echo(d)


@click.command()
@click.argument("device_type_name")
@click.argument("csv_file")
def create_modbusMap(device_type_name, csv_file):
    """Create modbusMap.p from channel csv file."""
    modbusMap = {
        "1": {
            "c": "ETHERNET/IP",
            "b": "192.168.1.10",
            "addresses": {
                "300": {}
            },
            "f": "Off",
            "p": "",
            "s": "1"
        },
        "2": {
            "c": "M1-485",
            "b": "9600",
            "addresses": {},
            "f": "Off",
            "p": "None",
            "s": "1"
        }
    }
    ind = 1
    with open(csv_file, 'r') as inp_file:
        reader = csv.DictReader(inp_file)
        for row in reader:
            modbusMap["1"]["addresses"]["300"]["2-{}".format(ind)] = make_modbusmap_channel(ind, row, device_type_name)
            ind += 1
    with open("modbusMap.p", 'wb') as mod_map_file:
        pickle.dump(modbusMap, mod_map_file, protocol=0)

    with open("modbusMap.json", 'w') as json_file:
        json.dump(modbusMap, json_file, indent=4)


cli.add_command(get_channel_csv)
cli.add_command(post_channel_csv)
cli.add_command(print_channel_options)
cli.add_command(create_modbusMap)

if __name__ == '__main__':
    cli()
