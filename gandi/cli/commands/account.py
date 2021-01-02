""" Account namespace commands. """
import click

from gandi.cli.core.cli import cli
from gandi.cli.core.utils import output_account
from gandi.cli.core.params import pass_gandi


@cli.group(name='account')
@pass_gandi
def account(gandi):
    """Commands related to accounts."""


@account.command()
@click.option('--sharing_id', default=None, help='Sharing ID')
@pass_gandi
def info(gandi, sharing_id):
    """Display information about hosting account.
    """
    output_keys = ['handle', 'credit', 'prepaid']

    account = gandi.account.all(sharing_id)
    
    if 'prepaid' not in account:
        account['prepaid_info'] = gandi.contact.balance().get('prepaid', {})
    
    output_account(gandi, account, output_keys)
    
    return account
