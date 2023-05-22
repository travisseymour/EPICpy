"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating 
human performance tasks using the EPIC computational cognitive architecture 
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import importlib
import inspect
import gc
from weakref import ref
from enum import EnumMeta

_readonly_attrs = {
    "__annotations__",
    "__call__",
    "__class__",
    "__closure__",
    "__code__",
    "__defaults__",
    "__delattr__",
    "__dict__",
    "__dir__",
    "__doc__",
    "__eq__",
    "__format__",
    "__func__",
    "__ge__",
    "__get__",
    "__getattribute__",
    "__globals__",
    "__gt__",
    "__hash__",
    "__init__",
    "__init_subclass__",
    "__kwdefaults__",
    "__le__",
    "__lt__",
    "__module__",
    "__name__",
    "__ne__",
    "__new__",
    "__qualname__",
    "__reduce__",
    "__reduce_ex__",
    "__repr__",
    "__self__",
    "__setattr__",
    "__sizeof__",
    "__str__",
    "__subclasshook__",
    "__weakref__",
    "__members__",
    "__mro__",
    "__itemsize__",
    "__isabstractmethod__",
    "__basicsize__",
    "__base__",
}


def reset_module(module, inner_modules_also=True):
    """
    This function is a stronger form of importlib's `reload` function. What it does, is
    that aside from reloading a module, it goes to the old instance of the module, and
    sets all the (not read-only) attributes, functions and classes to be the
    reloaded-module's
    :param module: The module to reload (module reference, not the name)
    :param inner_modules_also: Whether to treat ths module as a package as well,
    and reload all the modules within it.
    """

    # For the case when the module is actually a package
    if inner_modules_also:
        submods = {
            submod
            for _, submod in inspect.getmembers(module)
            if (type(submod).__name__ == "module")
            and (submod.__package__.startswith(module.__name__))
        }
        for submod in submods:
            reset_module(submod, True)

    # First, log all the references before reloading (because some references may be
    #  changed by the reload operation).
    module_tree = _get_tree_references_to_reset_recursively(module, module.__name__)

    new_module = importlib.reload(module)
    _reset_item_recursively(module, module_tree, new_module)


def _update_referrers(item, new_item):
    refs = gc.get_referrers(item)

    weak_ref_item = ref(item)
    for coll in refs:
        if type(coll) == dict:
            enumerator = coll.keys()
        elif type(coll) == list:
            enumerator = range(len(coll))
        else:
            continue

        for key in enumerator:
            if weak_ref_item() is None:
                # No refs are left in the GC
                return

            if coll[key] is weak_ref_item():
                coll[key] = new_item


def _get_tree_references_to_reset_recursively(
    item, module_name, grayed_out_item_ids=None
):
    if grayed_out_item_ids is None:
        grayed_out_item_ids = set()

    item_tree = {}
    attr_names = set(dir(item)) - _readonly_attrs
    for sub_item_name in attr_names:
        sub_item = getattr(item, sub_item_name)
        item_tree[sub_item_name] = [sub_item, None]

        try:
            # Will work for classes and functions defined in that module.
            mod_name = sub_item.__module__
        except AttributeError:
            mod_name = None

        # If this item was defined within this module, deep-reset
        if (
            (mod_name is None)
            or (mod_name != module_name)
            or (id(sub_item) in grayed_out_item_ids)
            or isinstance(sub_item, EnumMeta)
        ):
            continue

        grayed_out_item_ids.add(id(sub_item))
        item_tree[sub_item_name][1] = _get_tree_references_to_reset_recursively(
            sub_item, module_name, grayed_out_item_ids
        )

    return item_tree


def _reset_item_recursively(item, item_subtree, new_item):
    # Set children first so we don't lose the current references.
    if item_subtree is not None:
        for sub_item_name, (sub_item, sub_item_tree) in item_subtree.items():
            try:
                new_sub_item = getattr(new_item, sub_item_name)
            except AttributeError:
                # The item doesn't exist in the reloaded module. Ignore.
                continue

            try:
                # Set the item
                _reset_item_recursively(sub_item, sub_item_tree, new_sub_item)
            except Exception as ex:
                pass

    _update_referrers(item, new_item)

    # FIXME: WHY IS THIS STILL HERE? vvv

    # ==============================================================================
    # This is another approach, but it's not working on realoading different devices
    # ==============================================================================

    # def reload_package(self, root_module):
    #     package_name = root_module.__name__
    #     import types
    #
    #     # get a reference to each loaded module
    #     loaded_package_modules = dict(
    #         [
    #             (key, value)
    #             for key, value in sys.modules.items()
    #             if key.startswith(package_name) and isinstance(value, types.ModuleType)
    #         ]
    #     )
    #
    #     # delete references to these loaded modules from sys.modules
    #     for key in loaded_package_modules:
    #         del sys.modules[key]
    #
    #     # load each of the modules again;
    #     # make old modules share state with new modules
    #     for key in loaded_package_modules:
    #         print("loading %s" % key)
    #         newmodule = __import__(key)
    #         oldmodule = loaded_package_modules[key]
    #         oldmodule.__dict__.clear()
    #         oldmodule.__dict__.update(newmodule.__dict__)
