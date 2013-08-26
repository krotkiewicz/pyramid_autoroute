import inspect
import re
import sys
from pyramid.url import urlencode
from random import choice
from string import letters
from pyramid.path import caller_package

from pyramid.exceptions import ConfigurationError

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

def convert(name):
    """
    From CamelCase to snake_case
    https://gist.github.com/3660565/f2e285d2e249b0ff042f524f0b74360e5d3535aa
    """
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class UnresolvedRoute(Exception):
    pass

class FakeConfig(object):
    def __init__(self, application_package):
        self.application_package = application_package
        self.views = []

    def with_package(self, *arg, **kwargs):
        return self

    def add_subscriber(self, *arg, **kwargs):
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
        return resolved


    def get_callable_name(self, callable):
        if inspect.isfunction(callable):
            return callable.__module__, callable.func_name.lower()
        elif inspect.isclass(callable):
            name =  callable.__name__
            name = convert(name)
            return callable.__module__, name
        else:
            raise NotImplementedError('Not implemented')

    def resolve(self, name, callable):
        callable_module, callable_name = self.get_callable_name(callable)
        if not self.root_module in callable_module:
            return

        pos = callable_module.find(self.root_module)
        alen = len(self.root_module)
        rest = callable_module[pos+alen:].replace('.', '/')

        if name:
            if name == 'root':
                path = '/'
            else:
                path = '%s/%s' % (rest, callable_name)
            self.config.add_route(name, path)
            return name, path

def prepare_url_for(resolved):
    paths = [path for view_name, path in resolved ]
    def url_for(request, name, **kwargs):
        if name in paths:
            if kwargs:
                params = dict((k, v) for k, v in kwargs.iteritems() if v != None)
                return '%s?%s' % (name, urlencode(params))
            return name
        else:
            raise UnresolvedRoute('Can\'t resolved %s route' % name)
    return url_for

def includeme(config):
    root_module_str = config.registry.settings['pyramid.autoroute.root_module']
    last = root_module_str.split('.')[-1]
    root_module = __import__(root_module_str)
    root_module = getattr(root_module, last)

    fake_config = FakeConfig(None)
    scanner = config.venusian.Scanner(config=fake_config)
    if 'venusian.ignore' in config.registry.settings:
        venusian_ingore = config.registry.settings['venusian.ignore']
    else:
        venusian_ingore = None

    t1 = time.time()
    scanner.scan(root_module, ignore=venusian_ingore)
    diff = time.time() - t1

    resolved = RouteResolver(config, root_module_str, fake_config.views).resolveAll()
    config.add_request_method(prepare_url_for(resolved), name='url_for')
    print 'Routes generated in %ss' % round(diff, 2)

