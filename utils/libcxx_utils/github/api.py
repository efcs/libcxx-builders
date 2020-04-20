#!/usr/bin/env python3
import requests
import os
import sys
import json
from argparse import ArgumentParser
import subprocess
from libcxx_utils import util

def get_default_auth():
  auth_env = AuthFromEnv()
  if auth_env:
    return auth_env
  return AuthFromFile()

def get_default_auth_file():
  auth_file = os.environ.get('GITHUB_AUTH_FILE', None)
  if auth_file is not None:
    return auth_file
  current_scope = os.path.expanduser(os.path.join('~', '.github_auth', 'current.json'))
  if os.path.exists(current_scope):
    return current_scope
  return None


class AuthFromEnv(object):
  @staticmethod
  def _getToken():
    tk = os.environ['GITHUB_TOKEN']
    if tk is not None:
      return tk
    tk_name = os.environ['GITHUB_TOKEN_NAME']
    if tk_name is not None:
      return util.capture(['lpass', 'show', '--notes', tk_name]).strip()
    return None

  @staticmethod
  def _getRepo():
    return os.environ['GITHUB_REPO']

  @staticmethod
  def _getOwner():
    return os.environ['GITHUB_OWNER']

  def __bool__(self):
    return self.repo is not None and self.owner is not None and self.token is not None

  def __init__(self):
    self.repo = self._getRepo()
    self.owner = self._getOwner()
    self.token = self._getToken()


class AuthFromFile(object):
  def __init__(self, auth_file=None):
    if auth_file is None:
      auth_file = get_default_auth_file()
    if auth_file is None or not os.path.exists(auth_file):
      print("Invalid auth file: %s" % auth_file)
      sys.exit(1)
    with open(auth_file, 'r') as f:
      cfg = json.load(f)
    self.repo = cfg['repo']
    self.token_name = cfg['token_name']
    self.token = self._readToken(cfg['token_name'])
    self.owner = cfg['owner']

  def _readToken(self, token_name):
    return util.capture(['lpass', 'show', '--notes', token_name]).strip()


class ManualAuth(object):
  def __init__(self, token, repo, owner):
    self.token = token
    self.repo = repo
    self.owner = owner

  def __bool__(self):
    return True

def addCommandLineAuth(parser):
  parser.add_argument('--token', type=str, required=False, default=None)
  parser.add_argument('--owner', type=str, required=False, default=None)
  parser.add_argument('--repo', type=str, required=False, default=None)
  return parser

def tryCommandLineAuth(argv=sys.argv):
    parser = ArgumentParser('auth params')
    addCommandLineAuth(parser)
    args = parser.parse_known_args(argv)
    if args.token is None and args.owner is None and args.repo is None:
      return False
    if args.token is None or args.owner is None or args.repo is None:
      raise Exception('args only partially specified')
    return ManualAuth(token=args.token, repo=args.repo, owner=args.owner)



class GithubActionsAPI(object):
  def __init__(self, auth):
    self.base_url = 'https://api.github.com/'
    self.session = requests.Session()
    self.session.headers['Authorization'] = 'token %s' % auth.token
    self.session.headers['Accept'] = 'application/vnd.github.everest-preview+json'
    self.substitutions = dict()
    self.substitutions[':owner'] = auth.owner
    self.substitutions[':repo'] = auth.repo

  def _createURL(self, request, kwargs):
    # do stuff with args
    url = self.base_url + request
    for k,v in self.substitutions.items():
      if v is None:
        continue
      url = url.replace(k, v)
    for k,v in kwargs.items():
      url = url.replace(':%s' % k, v)
    return url

  def _get(self, api, **kwargs):
      return self.session.get(self._createURL(api, kwargs))

  def _post(self, api, replacements={}, json={}):
      return self.session.post(self._createURL(api, replacements), json=json)


  def _delete(self, api, **kwargs):
      return self.session.delete(self._createURL(api, kwargs))

  def getActionsDownloads(self):
    return self._get('repos/:owner/:repo/actions/runners/downloads')

  def getOrgActionsDownloads(self):
    return self._get('orgs/:owner/actions/runners/downloads')

  def getRunners(self):
    return self._get('repos/:owner/:repo/actions/runners')

  def getRunner(self, runner_id):
    return self._get('repos/:owner/:repo/actions/runners/:runner_id', runner_id=runner_id)

  def getCreationToken(self):
    return self._post('repos/:owner/actions/runners/registration-token')

  def getCreationTokenForOrg(self):
    return self._post('orgs/:owner/actions/runners/registration-token')

  def getRemovalToken(self):
    return self._post('repos/:owner/:repo/actions/runners/remove-token')

  def removeRunner(self, runner_id):
    return self._delete('repos/:owner/:repo/actions/runners/:runner_id', runner_id=runner_id)

  def getWorkflows(self):
    return self._get('repos/:owner/:repo/actions/workflows')

  def getWorkflow(self, workflow_id):
      return self._get('repos/:owner/:repo/actions/workflows/:workflow_id', workflow_id=workflow_id)

  def getWorkflowRuns(self):
    return self._get('repos/:owner/:repo/actions/runs')

  def getWorkflowRun(self, run_id):
    return self._get('repos/:owner/:repo/actions/runs/:run_id', run_id=run_id)

  def repoDispatchEvent(self, payload={}):
    payload = json.loads(payload)
    return self._post('repos/:owner/:repo/dispatches', replacements={}, json=payload)

  def listBranches(self):
    return self._get('repos/:owner/:repo/branches')

  def listCredentials(self):
    return self._get('orgs/:owner/credential-authorizations')

  def getOrg(self):
    return self._get('orgs/:owner')


if __name__ == '__main__':
  g = GithubActionsAPI()
  res = g.getActionsDownloads()
  print(res.json())
  res = g.getRunners()
  print(res.json())
  res = g.getCreationToken()
  print(res.json())
  res = g.getRemovalToken()
  print(res.json())
