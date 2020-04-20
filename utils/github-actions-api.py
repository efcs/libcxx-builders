#!/usr/bin/env python3
from argparse import ArgumentParser
import sys
import subprocess
import json
import requests
import os
from libcxx_utils.github import api as api


class GithubActionsUtil(object):
  def __init__(self):
    self.parser = ArgumentParser(
        description='Utilities for using the github API')
    self.parser.add_argument('--token', required=('GITHUB_TOKEN' not in os.environ), default=os.environ.get('GITHUB_TOKEN'))
    self.subparsers = self.parser.add_subparsers(help='subcommand help')
    self._create_parser()
    self.args = self.parser.parse_args()
    auth = api.ManualAuth(repo=self.args.repo, owner=self.args.owner, token=self.args.token)
    self.api = api.GithubActionsAPI(auth=auth)

  def run_command(self):
    args = self.args
    try:
      args.func(args)
    except requests.exceptions.HTTPError as err:
      print(err)
      sys.exit(1)

  def _api_call(self, func, **kwargs):
    result = func(**kwargs)
    result.raise_for_status()
    return result

  def _print_result(self, result):
    print(json.dumps(result, indent=2))

  def _add_default_arguments(self, parser):
    parser.add_argument('--owner', dest='owner', default=os.environ.get('GITHUB_OWNER'))
    parser.add_argument('--repo', dest='repo', default=os.environ.get('GITHUB_REPO'))

    return parser

  def _cmd_parser(self, name, func):
    p = self.subparsers.add_parser(name)
    p = self._add_default_arguments(p)
    p.set_defaults(func=func)
    return p


  def _create_parser(self):
    def add_download_args(parser_downloads):
      parser_downloads.add_argument('-o', '--os', dest='os',
                                    help='the OS to download',
                                    default='linux')
      parser_downloads.add_argument('-a', '--arch',
                                    help='the architecture to download',
                                    dest='arch', default='x64')
      return parser_downloads

    add_download_args(self._cmd_parser('downloads', self._downloads_cmd))
    add_download_args(self._cmd_parser('org-downloads', self._org_downloads_cmd))

    self._cmd_parser('registration-token', self._registration_token_cmd)
    self._cmd_parser('org-registration-token', self._org_registration_token_cmd)
    self._cmd_parser('workflows', self._workflows_cmd)
    self._cmd_parser('workflow', self._workflow_cmd).add_argument('workflow_id')
    self._cmd_parser('workflow-runs', self._workflow_runs_cmd)
    self._cmd_parser('workflow-run', self._workflow_run_cmd).add_argument('run_id')
    self._cmd_parser('runners', self._runners_cmd)
    self._cmd_parser('get-org', self._get_org)
    self._cmd_parser('list-creds', self._list_creds)
    self._cmd_parser('list-branches', self._list_branches_cmd)
    self._cmd_parser('runners', self._runners_cmd)

    event_parser = self._cmd_parser('push-event', self._push_event_cmd)
    event_parser.add_argument('payload')
    event_parser.add_argument('-f', '--file', action='store_true',
                                    help="Read the payload from a file")


  def _get_org(self, args):
    res = self._api_call(self.api.getOrg)
    self._print_result(res.json())

  def _list_branches_cmd(self, args):
    res = self._api_call(self.api.listBranches)
    self._print_result(res.json())

  def _list_creds(self, args):
    res = self._api_call(self.api.listCredentials)
    self._print_result(res.json())

  def _push_event_cmd(self, args):
    payload = args.payload
    if args.file:
      with open(payload, 'r') as f:
        payload = f.read()
    res = self._api_call(self.api.repoDispatchEvent,
                         payload=payload)
    if res.status_code == 204:
      print("Success!")
    else:
      print('%r' % res)
      sys.exit(1)

  def _download_commands_base(self, endpoint, args):
    res = self._api_call(endpoint)
    jres = res.json()
    for entry in jres:
      if entry['os'] == args.os and entry['architecture'] == args.arch:
        self._print_result(entry)
        return
    print('failed to find download for os=%s and arch=%s' % (
    args.os, args.arch))
    sys.exit(1)

  def _downloads_cmd(self, args):
    return self._download_commands_base(self.api.getActionsDownloads, args)


  def _org_downloads_cmd(self, args):
    return self._download_commands_base(self.api.getOrgActionsDownloads, args)


  def _registration_token_cmd(self, args):
    res = self._api_call(self.api.getCreationToken)
    self._print_result(res.json())

  def _org_registration_token_cmd(self, args):
    res = self._api_call(self.api.getCreationTokenForOrg)
    self._print_result(res.json())

  def _workflows_cmd(self, args):
    res = self._api_call(self.api.getWorkflows)
    self._print_result(res.json())

  def _workflow_cmd(self, args):
    res = self._api_call(self.api.getWorkflow, workflow_id=args.workflow_id)
    self._print_result(res.json())

  def _workflow_runs_cmd(self, args):
    res = self._api_call(self.api.getWorkflowRuns)
    self._print_result(res.json())

  def _workflow_run_cmd(self, args):
    res = self._api_call(self.api.getWorkflowRun, run_id=args.run_id)
    self._print_result(res.json())

  def _runners_cmd(self, args):
    res = self._api_call(self.api.getRunners)
    self._print_result(res.json())



def main():
  actions_cmd = GithubActionsUtil()
  actions_cmd.run_command()


if __name__ == '__main__':
  main()
