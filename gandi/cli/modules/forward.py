""" Forward commands module. """
import json

from gandi.cli.core.base import GandiModule


class Forward(GandiModule):

    """ Module to handle CLI commands.

    $ gandi forward create
    $ gandi forward delete
    $ gandi forward list
    $ gandi forward update

    """

    api_url = 'https://api.gandi.net/v5/email'

    @classmethod
    def list(cls, domain, options):
        """List forwards for a given domain name."""

        if cls.get('apirest.key'):
            if 'items_per_page' in options:
                options = '?per_page=%s' % options['items_per_page']
            else:
                options = ''

            return cls.json_get('%s/forwards/%s%s'
                                % (cls.api_url, domain, options))

        return cls.call('domain.forward.list', domain, options)

    @classmethod
    def delete(cls, domain, source):
        """Delete a domain mail forward."""

        if cls.get('apirest.key'):
            return cls.json_delete('%s/forwards/%s/%s'
                                   % (cls.api_url, domain, source))

        return cls.call('domain.forward.delete', domain, source)

    @classmethod
    def create(cls, domain, source, destinations):
        """Create a domain mail forward."""
        cls.echo('Creating mail forward %s@%s' % (source, domain))
        options = {'destinations': list(destinations)}

        if cls.get('apirest.key'):
            options['source'] = source
            return cls.json_post('%s/forwards/%s'
                                 % (cls.api_url, domain),
                                 data=json.dumps(options))

        result = cls.call('domain.forward.create', domain, source, options)

        return result

    @classmethod
    def get_destinations(cls, domain, source):
        """Retrieve forward information."""
        forwards = cls.list(domain, {'items_per_page': 500})
        for fwd in forwards:
            if fwd['source'] == source:
                return fwd['destinations']

        return []

    @classmethod
    def update(cls, domain, source, dest_add, dest_del):
        """Update a domain mail forward destinations."""
        result = None

        if dest_add or dest_del:
            current_destinations = cls.get_destinations(domain, source)
            fwds = current_destinations[:]
            if dest_add:
                for dest in dest_add:
                    if dest not in fwds:
                        fwds.append(dest)
            if dest_del:
                for dest in dest_del:
                    if dest in fwds:
                        fwds.remove(dest)

            if ((len(current_destinations) != len(fwds))
                    or (current_destinations != fwds)):
                cls.echo('Updating mail forward %s@%s' % (source, domain))
                options = {'destinations': fwds}

                if cls.get('apirest.key'):
                    result = cls.json_put('%s/forwards/%s/%s'
                                          % (cls.api_url, domain, source),
                                          data=json.dumps(options))
                else:
                    result = cls.call('domain.forward.update', domain, source,
                                      options)

        return result
