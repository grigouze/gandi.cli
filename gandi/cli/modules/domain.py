""" Domain commands module. """

import time
import json

from gandi.cli.core.base import GandiModule
from gandi.cli.core.utils import DomainNotAvailable


class Domain(GandiModule):

    """ Module to handle CLI commands.

    $ gandi domain create
    $ gandi domain info
    $ gandi domain list

    """

    api_url = 'https://api.gandi.net/v5/domain'
    orga_url = 'https://api.gandi.net/v5/organization'

    @classmethod
    def list(cls, options):
        """List operation."""
        if cls.get('apirest.key'):
            return cls.json_get('%s/domains?per_page=%s'
                                % (cls.api_url, options['items_per_page']))
        return cls.call('domain.list', options)

    @classmethod
    def info(cls, fqdn):
        """Display information about a domain."""
        if cls.get('apirest.key'):
            ret = cls.json_get('%s/domains/%s' % (cls.api_url, fqdn))
            ret['expires'] = ret['dates']['registry_ends_at']
            ret['date_created'] = ret['dates']['created_at']
            ret['date_registry_end'] = ret['dates']['registry_ends_at']
            ret['date_updated'] = ret['dates']['updated_at']
            return ret

        return cls.call('domain.info', fqdn)

    @classmethod
    def create(cls, fqdn, duration, owner, admin, tech, bill, nameserver,
               extra_parameter, background):
        """Create a domain."""
        fqdn = fqdn.lower()
        if not background and not cls.intty():
            background = True

        if cls.get('apirest.key'):
            ret = cls.json_get('%s/check?name=%s' % (cls.api_url, fqdn))
            products = ret.get('products', [])
            if len(products) > 0:
                result = {fqdn: products[0].get('status', 'unavailable')}
        else:
            result = cls.call('domain.available', [fqdn])
            while result[fqdn] == 'pending':
                time.sleep(1)
                result = cls.call('domain.available', [fqdn])

        if result[fqdn] == 'unavailable':
            raise DomainNotAvailable('%s is not available' % fqdn)

        if cls.get('apirest.key'):
            user_handle = cls.json_get('%s/user-info' % (cls.orga_url))

            del user_handle['id']
            del user_handle['username']

            user_handle['family'] = user_handle['lastname']
            user_handle['given'] = user_handle['firstname']
            del user_handle['lastname']
            del user_handle['firstname']

            del user_handle['name']
            del user_handle['lang']

            user_handle['type'] = 0
        else:
            # retrieve handle of user and save it to configuration
            user_handle = cls.call('contact.info')['handle']
            cls.configure(True, 'api.handle', user_handle)

        owner_ = owner or user_handle
        admin_ = admin or user_handle
        tech_ = tech or user_handle
        bill_ = bill or user_handle

        domain_params = {
            'duration': duration,
            'owner': owner_,
            'admin': admin_,
            'tech': tech_,
            'bill': bill_,
        }

        if nameserver:
            domain_params['nameservers'] = nameserver

        if extra_parameter:
            domain_params['extra'] = {}
            for extra in extra_parameter:
                domain_params['extra'][extra[0]] = extra[1]

        if cls.get('apirest.key'):
            domain_params['fqdn'] = fqdn
            result = cls.json_post('%s/domains' % (cls.api_url),
                                   data=json.dumps(domain_params))
            if result:
                result = result['message']
        else:
            result = cls.call('domain.create', fqdn, domain_params)

        if background:
            return result

        # interactive mode, run a progress bar
        cls.echo('Creating your domain.')
        cls.display_progress(result)
        cls.echo('Your domain %s has been created.' % fqdn)

    @classmethod
    def renew(cls, fqdn, duration, background):
        """Renew a domain."""
        fqdn = fqdn.lower()
        if not background and not cls.intty():
            background = True

        domain_info = cls.info(fqdn)

        try:
            current_year = domain_info['date_registry_end'].year
        except AttributeError:
            current_year = False

        domain_params = {
            'duration': duration,
            'current_year': current_year,
        }

        if cls.get('apirest.key'):
            del domain_params['current_year']
            result = cls.json_post('%s/domains/%s/renew' % (cls.api_url, fqdn),
                                   data=json.dumps(domain_params))
            if result:
                result = result['message']
        else:
            result = cls.call('domain.renew', fqdn, domain_params)

        if background:
            return result

        # interactive mode, run a progress bar
        cls.echo('Renewing your domain.')
        cls.display_progress(result)
        cls.echo('Your domain %s has been renewed.' % fqdn)

    @classmethod
    def autorenew_deactivate(cls, fqdn):
        """Activate deautorenew"""
        fqdn = fqdn.lower()

        result = cls.call('domain.autorenew.deactivate', fqdn)

        return result

    @classmethod
    def autorenew_activate(cls, fqdn):
        """Activate autorenew"""
        fqdn = fqdn.lower()

        result = cls.call('domain.autorenew.activate', fqdn)

        return result

    @classmethod
    def from_fqdn(cls, fqdn):
        """Retrieve domain id associated to a FQDN."""
        result = cls.list({'fqdn': fqdn})
        if len(result) > 0:
            return result[0]['id']

    @classmethod
    def usable_id(cls, id):
        """Retrieve id from input which can be fqdn or id."""
        # Check if it's already an integer.
        try:
            qry_id = int(id)
        except Exception:
            # Otherwise, assume it's a FQDN.
            # This will return `None` if the FQDN is not found.
            qry_id = cls.from_fqdn(id)

        if not qry_id:
            msg = 'unknown identifier %s' % id
            cls.error(msg)

        return qry_id
