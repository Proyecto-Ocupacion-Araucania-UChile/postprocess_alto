import click


class RequiredOption(click.Option):
    """
    Required option class to click library

    :source: https://stackoverflow.com/a/44349292
    """
    def __init__(self, *args, **kwargs):
        self.required_if = kwargs.pop('required_if')
        assert self.required_if, "'required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is required with %s' %
            self.required_if
        ).strip()
        super(RequiredOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.required_if in opts

        if other_present:
            if not we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is required with `%s`" % (
                        self.name, self.required_if))
            else:
                self.prompt = None

        return super(RequiredOption, self).handle_parse_result(
            ctx, opts, args)