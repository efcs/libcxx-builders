#!/usr/bin/env python3
from argparse import ArgumentParser
import sys
import subprocess
import json
import requests
import os


class GithubAuthUtil(object):
  def __init__(self):
    self.parser = self._create_parser()


  def run_command(self):
    args = self.parser.parse_args()
    args.func(args)


  def _create_parser(self):
    parser = ArgumentParser(
        description='Utilities setting the auth enviroment')
    subparsers = parser.add_subparsers(help='subcommand help')


    parser_create = subparsers.add_parser('create')
    parser_create.add_argument('--repo',
                                  required=True,
                                  help='the repository')
    parser_create.add_argument('--owner',
                                  help='the repository owner',
                                  required=True)
    parser_create.add_argument('--token-name', required=True,
                              dest='token_name',
                              help='the auth token_name to use')
    parser_create.add_argument('-f', '--file',
                               action='store_true',
                               help='the output file to write to')
    parser_create.add_argument('--set', action='store_true',
                               help='Also set as the current scope')
    parser_create.add_argument('name')
    parser_create.set_defaults(func=self._create)

    parser_list = subparsers.add_parser('list')
    parser_list.set_defaults(func=self._list)
    
    parser_current = subparsers.add_parser('current')
    parser_current.set_defaults(func=self._current)
    

    parser_set = subparsers.add_parser('set')
    parser_set.add_argument('name')
    parser_set.add_argument('-f', '--file', action='store_true',
                            help='read from file')
    parser_set.set_defaults(func=self._set)

    return parser

  def _config_path(self, config_name=None):
    root = os.path.expanduser(os.path.join('~', '.github_auth/'))
    if os.path.exists(root) and not os.path.isdir(root):
      print('Config path %s is not a directory' % root)
      sys.exit(1)
    if not os.path.exists(root):
      os.mkdir(root)
    if config_name is None:
      return root
    return os.path.join(root, '%s.json' % config_name)


  def _current(self, args):
    current = self._config_path('current')
    if not os.path.exists(current):
      print('No current configuration')
      sys.exit(1)
    link_to = os.readlink(current)
    if os.path.normpath(os.path.dirname(os.path.realpath(current))) == os.path.normpath(self._config_path()):
      fname, ext = os.path.splitext(link_to)
      print('%s' % fname)
    else:
      print('%s' % link_to)

  def _set(self, args):
    if args.name == 'current':
      print("current cannot be used as a name")
      sys.exit(1)
    if args.file:
      config_path = os.path.abspath(args.name)
    else:
      config_path = self._config_path(args.name)
    if not os.path.isfile(config_path):
      print("auth file '%s' does not exist" % config_path)
      sys.exit(1)
    current_path = self._config_path('current')
    if os.path.islink(current_path):
      os.unlink(current_path)
    os.symlink(config_path, current_path)
    print('Setting current auth scope to %s' % args.name)


  def _create(self, args):
    if args.name == 'current':
      print("current cannot be used as a name")
      sys.exit(1)
    if args.file:
      config_path = os.path.abspath(args.name)
    else:
      config_path = self._config_path(args.name)
    template = """
{{
  "token_name": "{token_name}",
  "repo": "{repo}",
  "owner": "{owner}"
}}
    """.format(token_name=args.token_name, repo=args.repo, owner=args.owner).strip()
    with open(config_path, 'w') as f:
      f.write(template)

    print('Creating auth scope %s' % args.name)
    if not args.set:
      print("Use 'github-auth.py set %s' to activate..." % args.name)
    else:
      self._set(args)



  def _list(self, args):
    config_path = self._config_path()
    empty = True
    for filename in os.listdir(config_path):
      if not filename.endswith('.json') or filename == 'current.json':
        continue
      print('%s' % os.path.splitext(filename)[0])
      empty = False
    if empty:
      print("No auth scopes...")


def main():
  actions_cmd = GithubAuthUtil()
  actions_cmd.run_command()


if __name__ == '__main__':
  main()
