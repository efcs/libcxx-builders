from libcxx_utils.github.api import GithubAPI
import libcxx_utils.util as util

from argparse import ArgumentParser

class GithubActions(object):
  def __init__(self):
    self.parser = self._initMainParser()
    self.subparsers = self._initCommandParsers()
    self.args = self.parser.parse_args()
    self.api = GithubAPI(self.args.token)

  def _initMainParser(self):
    parser = ArgumentParser(
        description='Utilities for using the github API')
    parser.add_argument('--token', required=('GITHUB_TOKEN' not in os.environ), default=os.environ.get('GITHUB_TOKEN'))
    return parser

  def _initCommandParsers(self, parser):
    subparser = self.parser.add_subparsers(help='subcommand help')
    return subparser

  def _initCmd(self, name, requires=[]):
    parser = self.subparsers.add_parser(name)
    for f in requires:
      if f == 'repo':

  def run(self):

def main():

