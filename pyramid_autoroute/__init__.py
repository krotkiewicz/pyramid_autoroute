import inspect
import re
import sys
from random import choice
from string import letters
from pyramid.path import caller_package

from pyramid.exceptions import ConfigurationError

class FakeConfig(object):
    def __init__(self, application_package):
        self.application_package = application_package
        self.views = []

    def with_package(self, *arg, **kwargs):
        return self

    def add_view(self, *args, **kwargs):
        route_name = kwargs.get('route_name')
        view = kwargs['view']
        self.views.append((route_name, view))


class RouteResolver(object):

    def __init__(self, config, root_module, views):
        self.root_module = root_module
        self.config = config
        self.views = views

    def resolveAll(self):
        resolved = []
        longest_len = 0
        for view_name, view in self.views:
            result = self.resolve(view_name, view)
            if result:
                maybe_longest_len = len(result[0])
                if maybe_longest_len > longest_len:
                    longest_len = maybe_longest_len
                resolved.append(result)


        print '\nAuto generated routes:\n'
        print 'Name'.ljust(longest_len+6, ' '), 'Path'
        print '----------------------------------------------------------------'
        for view_name, path in resolved:
            print view_name.ljust(longest_len+6, ' '), path

        print '\n'


    def get_callable_name(self, callable):
        if inspect.isfunction(callable):
            return callable.__module__, callable.func_name.lower()
        elif inspect.isclass(callable):
            return callable.__module__, callable.__name__.lower()
        else:
            raise NotImplementedError('Not implemented')

    def resolve(self, name, callable):
        callable_module, callable_name = self.get_callable_name(callable)
        if not self.root_module in callable_module:
            return

        pos = callable_module.find(self.root_module)
        alen = len(self.root_module)
        rest = callable_module[pos+alen:].replace('.', '/')

        path = '%s/%s' % (rest, callable_name)
        if name:
            self.config.add_route(name, path)
            return name, path



def includeme(config):
    root_module = config.registry.settings['pyramid.autoroute.root_module']
    caller = caller_package(level=3)
    fake_config = FakeConfig(caller)
    scanner = config.venusian.Scanner(config=fake_config)
    scanner.scan(caller)

    RouteResolver(config, root_module, fake_config.views).resolveAll()
