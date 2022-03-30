"""
Munch is a subclass of dict with attribute-style access.

Normal, I would just pip-install Munch, but there is some issue with this when
a constituent project is frozen with Pyinstaller. So, this is a local copy of the
relevant code.
"""

import pkg_resources

from six import u, iteritems, iterkeys

try:
    from collections.abc import Mapping
except ImportError:
    # Legacy Python
    from collections import Mapping

# from python3_compat import iterkeys, iteritems, Mapping, u

__version__ = "2.5.0"
VERSION = tuple(map(int, __version__.split(".")[:3]))

__all__ = (
    "Munch",
    "munchify",
    "DefaultMunch",
    "DefaultFactoryMunch",
    "RecursiveMunch",
    "unmunchify",
)


class Munch(dict):
    """A dictionary that provides attribute-style access."""

    def __init__(self, *args, **kwargs):  # pylint: disable=super-init-not-called
        self.update(*args, **kwargs)

    # only called if k not found in normal places
    def __getattr__(self, k):
        """Gets key if it exists, otherwise throws AttributeError."""
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        """Sets attribute k if it exists, otherwise sets key k. A KeyError
        raised by set-item (only likely if you subclass Munch) will
        propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        """Deletes attribute k if it exists, otherwise deletes key k. A KeyError
        raised by deleting the key--such as when the key is missing--will
        propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def toDict(self):
        """Recursively converts a munch back into a dictionary."""
        return unmunchify(self)

    @property
    def __dict__(self):
        return self.toDict()

    def __repr__(self):
        """Invertible* string-form of a Munch."""
        return "{0}({1})".format(self.__class__.__name__, dict.__repr__(self))

    def __dir__(self):
        return list(iterkeys(self))

    def __getstate__(self):
        """Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        return {k: v for k, v in self.items()}

    def __setstate__(self, state):
        """Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        self.clear()
        self.update(state)

    __members__ = __dir__  # for python2.x compatibility

    @classmethod
    def fromDict(cls, d):
        """Recursively transforms a dictionary into a Munch via copy."""
        return munchify(d, cls)

    def copy(self):
        return type(self).fromDict(self)

    def update(self, *args, **kwargs):
        """
        Override built-in method to call custom __setitem__ method that may
        be defined in subclasses.
        """
        for k, v in iteritems(dict(*args, **kwargs)):
            self[k] = v

    def get(self, k, d=None):
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        if k not in self:
            return d
        return self[k]

    def setdefault(self, k, d=None):
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        if k not in self:
            self[k] = d
        return self[k]


class AutoMunch(Munch):
    def __setattr__(self, k, v):
        """Works the same as Munch.__setattr__ but if you supply
        a dictionary as value it will convert it to another Munch.
        """
        if isinstance(v, Mapping) and not isinstance(v, (AutoMunch, Munch)):
            v = munchify(v, AutoMunch)
        super(AutoMunch, self).__setattr__(k, v)


class DefaultMunch(Munch):
    """
    A Munch that returns a user-specified value for missing keys.
    """

    def __init__(self, *args, **kwargs):
        """Construct a new DefaultMunch. Like collections.defaultdict, the
        first argument is the default value; subsequent arguments are the
        same as those for dict.
        """
        # Mimic collections.defaultdict constructor
        if args:
            default = args[0]
            args = args[1:]
        else:
            default = None
        super(DefaultMunch, self).__init__(*args, **kwargs)
        self.__default__ = default

    def __getattr__(self, k):
        """Gets key if it exists, otherwise returns the default value."""
        try:
            return super(DefaultMunch, self).__getattr__(k)
        except AttributeError:
            return self.__default__

    def __setattr__(self, k, v):
        if k == "__default__":
            object.__setattr__(self, k, v)
        else:
            super(DefaultMunch, self).__setattr__(k, v)

    def __getitem__(self, k):
        """Gets key if it exists, otherwise returns the default value."""
        try:
            return super(DefaultMunch, self).__getitem__(k)
        except KeyError:
            return self.__default__

    def __getstate__(self):
        """Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        return (self.__default__, {k: v for k, v in self.items()})

    def __setstate__(self, state):
        """Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        self.clear()
        default, state_dict = state
        self.update(state_dict)
        self.__default__ = default

    @classmethod
    def fromDict(cls, d, default=None):
        # pylint: disable=arguments-differ
        return munchify(d, factory=lambda d_: cls(default, d_))

    def copy(self):
        return type(self).fromDict(self, default=self.__default__)

    def __repr__(self):
        return "{0}({1!r}, {2})".format(
            type(self).__name__, self.__undefined__, dict.__repr__(self)
        )


class DefaultFactoryMunch(Munch):
    """A Munch that calls a user-specified function to generate values for
    missing keys like collections.defaultdict.
    """

    def __init__(self, default_factory, *args, **kwargs):
        super(DefaultFactoryMunch, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

    @classmethod
    def fromDict(cls, d, default_factory):
        # pylint: disable=arguments-differ
        return munchify(d, factory=lambda d_: cls(default_factory, d_))

    def copy(self):
        return type(self).fromDict(self, default_factory=self.default_factory)

    def __repr__(self):
        factory = self.default_factory.__name__
        return "{0}({1}, {2})".format(type(self).__name__, factory, dict.__repr__(self))

    def __setattr__(self, k, v):
        if k == "default_factory":
            object.__setattr__(self, k, v)
        else:
            super(DefaultFactoryMunch, self).__setattr__(k, v)

    def __missing__(self, k):
        self[k] = self.default_factory()
        return self[k]


class RecursiveMunch(DefaultFactoryMunch):
    """A Munch that calls an instance of itself to generate values for
    missing keys.
    """

    def __init__(self, *args, **kwargs):
        super(RecursiveMunch, self).__init__(RecursiveMunch, *args, **kwargs)

    @classmethod
    def fromDict(cls, d):
        # pylint: disable=arguments-differ
        return munchify(d, factory=cls)

    def copy(self):
        return type(self).fromDict(self)


# While we could convert abstract types like Mapping or Iterable, I think
# munchify is more likely to "do what you mean" if it is conservative about
# casting (ex: isinstance(str,Iterable) == True ).
#
# Should you disagree, it is not difficult to duplicate this function with
# more aggressive coercion to suit your own purposes.


def munchify(x, factory=Munch):
    """Recursively transforms a dictionary into a Munch via copy."""
    # Munchify x, using `seen` to track object cycles
    seen = dict()

    def munchify_cycles(obj):
        # If we've already begun munchifying obj, just return the already-created munchified obj
        try:
            return seen[id(obj)]
        except KeyError:
            pass

        # Otherwise, first partly munchify obj (but without descending into any lists or dicts) and save that
        seen[id(obj)] = partial = pre_munchify(obj)
        # Then finish munchifying lists and dicts inside obj (reusing munchified obj if cycles are encountered)
        return post_munchify(partial, obj)

    def pre_munchify(obj):
        # Here we return a skeleton of munchified obj, which is enough to save for later (in case
        # we need to break cycles) but it needs to filled out in post_munchify
        if isinstance(obj, Mapping):
            return factory({})
        elif isinstance(obj, list):
            return type(obj)()
        elif isinstance(obj, tuple):
            type_factory = getattr(obj, "_make", type(obj))
            return type_factory(munchify_cycles(item) for item in obj)
        else:
            return obj

    def post_munchify(partial, obj):
        # Here we finish munchifying the parts of obj that were deferred by pre_munchify because they
        # might be involved in a cycle
        if isinstance(obj, Mapping):
            partial.update((k, munchify_cycles(obj[k])) for k in iterkeys(obj))
        elif isinstance(obj, list):
            partial.extend(munchify_cycles(item) for item in obj)
        elif isinstance(obj, tuple):
            for (item_partial, item) in zip(partial, obj):
                post_munchify(item_partial, item)

        return partial

    return munchify_cycles(x)


def unmunchify(x):
    """Recursively converts a Munch into a dictionary."""

    # Munchify x, using `seen` to track object cycles
    seen = dict()

    def unmunchify_cycles(obj):
        # If we've already begun unmunchifying obj, just return the already-created unmunchified obj
        try:
            return seen[id(obj)]
        except KeyError:
            pass

        # Otherwise, first partly unmunchify obj (but without descending into any lists or dicts) and save that
        seen[id(obj)] = partial = pre_unmunchify(obj)
        # Then finish unmunchifying lists and dicts inside obj (reusing unmunchified obj if cycles are encountered)
        return post_unmunchify(partial, obj)

    def pre_unmunchify(obj):
        # Here we return a skeleton of unmunchified obj, which is enough to save for later (in case
        # we need to break cycles) but it needs to filled out in post_unmunchify
        if isinstance(obj, Mapping):
            return dict()
        elif isinstance(obj, list):
            return type(obj)()
        elif isinstance(obj, tuple):
            type_factory = getattr(obj, "_make", type(obj))
            return type_factory(unmunchify_cycles(item) for item in obj)
        else:
            return obj

    def post_unmunchify(partial, obj):
        # Here we finish unmunchifying the parts of obj that were deferred by pre_unmunchify because they
        # might be involved in a cycle
        if isinstance(obj, Mapping):
            partial.update((k, unmunchify_cycles(obj[k])) for k in iterkeys(obj))
        elif isinstance(obj, list):
            partial.extend(unmunchify_cycles(v) for v in obj)
        elif isinstance(obj, tuple):
            for (value_partial, value) in zip(partial, obj):
                post_unmunchify(value_partial, value)

        return partial

    return unmunchify_cycles(x)


# Serialization

try:
    try:
        import json
    except ImportError:
        import simplejson as json

    def toJSON(self, **options):
        """Serializes this Munch to JSON. Accepts the same keyword options as `json.dumps()`."""
        return json.dumps(self, **options)

    def fromJSON(cls, stream, *args, **kwargs):
        """Deserializes JSON to Munch or any of its subclasses."""
        factory = lambda d: cls(*(args + (d,)), **kwargs)
        return munchify(json.loads(stream), factory=factory)

    Munch.toJSON = toJSON
    Munch.fromJSON = classmethod(fromJSON)

except ImportError:
    pass

try:
    # Attempt to register ourself with PyYAML as a representer
    import yaml
    from yaml.representer import Representer, SafeRepresenter

    def from_yaml(loader, node):
        """PyYAML support for Munches using the tag `!munch` and `!munch.Munch`."""
        data = Munch()
        yield data
        value = loader.construct_mapping(node)
        data.update(value)

    def to_yaml_safe(dumper, data):
        """Converts Munch to a normal mapping node, making it appear as a
        dict in the YAML output.
        """
        return dumper.represent_dict(data)

    def to_yaml(dumper, data):
        """Converts Munch to a representation node."""
        return dumper.represent_mapping(u("!munch.Munch"), data)

    for loader_name in (
        "BaseLoader",
        "FullLoader",
        "SafeLoader",
        "Loader",
        "UnsafeLoader",
        "DangerLoader",
    ):
        LoaderCls = getattr(yaml, loader_name, None)
        if LoaderCls is None:
            # This code supports both PyYAML 4.x and 5.x versions
            continue
        yaml.add_constructor(u("!munch"), from_yaml, Loader=LoaderCls)
        yaml.add_constructor(u("!munch.Munch"), from_yaml, Loader=LoaderCls)

    SafeRepresenter.add_representer(Munch, to_yaml_safe)
    SafeRepresenter.add_multi_representer(Munch, to_yaml_safe)

    Representer.add_representer(Munch, to_yaml)
    Representer.add_multi_representer(Munch, to_yaml)

    # Instance methods for YAML conversion
    def toYAML(self, **options):
        """Serializes this Munch to YAML, using `yaml.safe_dump()` if
        no `Dumper` is provided. See the PyYAML documentation for more info.
        """
        opts = dict(indent=4, default_flow_style=False)
        opts.update(options)
        if "Dumper" not in opts:
            return yaml.safe_dump(self, **opts)
        else:
            return yaml.dump(self, **opts)

    def fromYAML(cls, stream, *args, **kwargs):
        factory = lambda d: cls(*(args + (d,)), **kwargs)
        loader_class = kwargs.pop("Loader", yaml.FullLoader)
        return munchify(yaml.load(stream, Loader=loader_class), factory=factory)

    Munch.toYAML = toYAML
    Munch.fromYAML = classmethod(fromYAML)

except ImportError:
    pass
