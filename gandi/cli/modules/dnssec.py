""" Dnssec commands module. """
import json

from gandi.cli.core.base import GandiModule


class DNSSEC(GandiModule):

    """ Module to handle CLI commands.

    $ gandi dnssec create
    $ gandi dnssec list
    $ gandi dnssec delete

    """

    api_url = 'https://api.gandi.net/v5/livedns'

    @classmethod
    def list(cls, fqdn):
        """List operation."""

        if cls.get('apirest.key'):
            return cls.json_get('%s/domains/%s/keys'
                                  % (cls.api_url, fqdn))

        return cls.call('domain.dnssec.list', fqdn)

    @classmethod
    def create(cls, fqdn, flags, algorithm, public_key):
        """Create a dnssec key."""
        fqdn = fqdn.lower()

        params = {
            'flags': flags,
            'algorithm': algorithm,
            'public_key': public_key,
        }

        if cls.get('apirest.key'):
            return cls.json_post('%s/domains/%s/keys'
                                  % (cls.api_url, fqdn),
                                  data=json.dumps({'flags': flags}))

        result = cls.call('domain.dnssec.create', fqdn, params)

        return result

    @classmethod
    def delete(cls, fqdn, id):
        """Delete this dnssec key."""

        if cls.get('apirest.key'):
            return cls.json_delete('%s/domains/%s/keys/%s'
                                  % (cls.api_url, fqdn, id))

        return cls.call('domain.dnssec.delete', id)
