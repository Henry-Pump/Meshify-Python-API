"""Query Meshify for data."""
import requests
import json
import csv
import click
from os import getenv
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


if not MESHIFY_USERNAME or not MESHIFY_PASSWORD:
    print("Simplify the usage by setting the meshify username and password as environment variables MESHIFY_USERNAME and MESHIFY_PASSWORD")
    MESHIFY_USERNAME = input("Meshify Username: ")
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
            writer.writerow(ch)

    click.echo("Wrote channels to {}".format(output_file))


cli.add_command(get_channel_csv)

if __name__ == '__main__':
    cli()
