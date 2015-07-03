# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from distutils.command.build import build as du_build
import distutils.core
import distutils.errors

from setuptools.command.build_py import build_py as st_build_py

from . import excludes
from . import resource_building


class BuildCommand(du_build):
    command_name = 'build'

    def get_sub_commands(self):
        super_cmds = du_build.get_sub_commands(self)
        my_cmds = [
            BuildProductionResourcesCommand.command_name,
        ]
        return my_cmds + super_cmds


class BuildPyCommand(st_build_py):
    command_name = 'build_py'

    def find_package_modules(self, package, package_dir):
        modules = st_build_py.find_package_modules(
            self, package, package_dir)
        return list(filter(_is_included_module, modules))


def _is_included_module(package_module_file):
    module = package_module_file[1]
    return not excludes.is_excluded_filename(module + '.py')


class BuildResourcesCommand(distutils.core.Command):
    command_name = 'build_resources'
    description = "build Javascript and CSS resources"
    mode = 'development'
    clean = False
    force = False
    directory = '.'
    user_options = [
        ('mode=', 'm', "build mode: 'development' (default) or 'production'"),
        ('clean', 'c', "clean intermediate files before building"),
        ('force', 'f', "force rebuild even if cached result exists"),
        ('directory=', 'd', "directory to build in, or '.' for all (default)"),
    ]
    boolean_options = ['clean', 'force']

    def initialize_options(self):
        pass

    def finalize_options(self):
        # Allow abbreviated mode, like d, dev, p, or prod
        for mode in ['development', 'production']:
            if self.mode and mode.startswith(self.mode):
                self.mode = mode
        if self.mode not in ['development', 'production']:
            raise distutils.errors.DistutilsArgError(
                "Mode must be 'development' or 'production'")

    def run(self):
        opts = resource_building.Options()
        opts.directories = [self.directory]
        opts.production = (self.mode == 'production')
        opts.clean = self.clean
        opts.force = self.force
        resource_building.build_resources(opts)


class BuildProductionResourcesCommand(BuildResourcesCommand):
    command_name = 'build_production_resources'
    description = "build Javascript and CSS resources for production"
    mode = 'production'
    clean = True


COMMANDS = dict((x.command_name, x) for x in [
    BuildCommand,
    BuildPyCommand,
    BuildResourcesCommand,
    BuildProductionResourcesCommand,
])