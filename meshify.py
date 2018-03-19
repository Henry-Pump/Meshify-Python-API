"""Query Meshify for data."""
import requests
import json
import csv
import click
from os import getenv, putenv
import getpass

MESHIFY_BASE_URL = "https://henrypump.meshify.com/api/v3/"
MESHIFY_USERNAME = getenv("MESHIFY_USERNAME")
MESHIFY_PASSWORD = getenv("MESHIFY_PASSWORD")


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


if not MESHIFY_USERNAME or not MESHIFY_PASSWORD:
    print("Simplify the usage by setting the meshify username and password as environment variables MESHIFY_USERNAME and MESHIFY_PASSWORD")
    MESHIFY_USERNAME = raw_input("Meshify Username: ")
    MESHIFY_PASSWORD = getpass.getpass("Meshify Password: ")

MESHIFY_AUTH = requests.auth.HTTPBasicAuth(MESHIFY_USERNAME, MESHIFY_PASSWORD)


def find_by_name(name, list_of_stuff):
    """Find an object in a list of stuff by its name parameter."""
    for x in list_of_stuff:
        if x['name'] == name:
            return x
    raise NameNotFound("Name not found!", name, list_of_stuff)


def query_meshify_api(endpoint):
    """Make a query to the meshify API."""
    if endpoint[0] == "/":
        endpoint = endpoint[1:]
    q_url = MESHIFY_BASE_URL + endpoint
    q_req = requests.get(q_url, auth=MESHIFY_AUTH)
    return json.loads(q_req.text) if q_req.status_code == 200 else []


def post_meshify_api(endpoint, data):
    """Post data to the meshify API."""
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


@click.group()
def cli():
    """Command Line Interface."""
    pass


@click.command()
@click.argument("device_type_name")
@click.option("-o", '--output-file', default=None, help="Where to put the CSV of channels.")
def get_channel_csv(device_type_name, output_file):
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
        'regexErrMsg'
    ]
    devicetypes = query_meshify_api('devicetypes')
    this_devicetype = find_by_name(device_type_name, devicetypes)
    channels = query_meshify_api('devicetypes/{}/channels'.format(this_devicetype['id']))

    if not output_file:
        output_file = 'channels_{}.csv'.format(device_type_name)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=channel_fieldnames)

        writer.writeheader()
        for ch in channels:
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


cli.add_command(get_channel_csv)
cli.add_command(post_channel_csv)

if __name__ == '__main__':
    cli()
