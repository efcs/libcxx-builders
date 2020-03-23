#!/usr/bin/env python3
from argparse import ArgumentParser
import sys
import subprocess
import json
import requests
from libcxx_utils.github import api as api


class GithubActionsUtil(object):
  def __init__(self):
    self.parser = self._create_parser()
    self.api = api.GithubActionsAPI()

  def run_command(self):
    args = self.parser.parse_args()
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

  def _create_parser(self):
    parser = ArgumentParser(
        description='Utilities for using the github API')
    api.addCommandLineAuth(parser.add_argument_group('auth'))

    subparsers = parser.add_subparsers(help='subcommand help')


    parser_downloads = subparsers.add_parser('downloads')
    parser_downloads.add_argument('-o', '--os', dest='os',
                                  help='the OS to download',
                                  default='linux')
    parser_downloads.add_argument('-a', '--arch',
                                  help='the architecture to download',
                                  dest='arch', default='x64')
    parser_downloads.set_defaults(func=self._downloads_cmd)

    parser_registration_token = subparsers.add_parser('registration-token')
    parser_registration_token.set_defaults(func=self._registration_token_cmd)

    parser_workflows = subparsers.add_parser('workflows')
    parser_workflows.set_defaults(func=self._workflows_cmd)

    parser_workflow = subparsers.add_parser('workflow')
    parser_workflow.add_argument('workflow_id')
    parser_workflow.set_defaults(func=self._workflow_cmd)

    parser_workflow_runs = subparsers.add_parser('workflow-runs')
    parser_workflow_runs.set_defaults(func=self._workflow_runs_cmd)

    parser_workflow_run = subparsers.add_parser('workflow-run')
    parser_workflow_run.add_argument('run_id')
    parser_workflow_run.set_defaults(func=self._workflow_run_cmd)

    parser_runners = subparsers.add_parser('runners')
    parser_runners.set_defaults(func=self._runners_cmd)

    parser_repo_event = subparsers.add_parser('push-event')
    parser_repo_event.add_argument('-f', '--file', action='store_true',
                                    help="Read the payload from a file")
    parser_repo_event.add_argument('payload')
    parser_repo_event.set_defaults(func=self._push_event_cmd)

    return parser

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

  def _downloads_cmd(self, args):
    res = self._api_call(self.api.getActionsDownloads)
    jres = res.json()
    for entry in jres:
      if entry['os'] == args.os and entry['architecture'] == args.arch:
        self._print_result(entry)
        return
    print('failed to find download for os=%s and arch=%s' % (
    args.os, args.arch))
    sys.exit(1)

  def _registration_token_cmd(self, args):
    res = self._api_call(self.api.getCreationToken)
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
