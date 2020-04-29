#!/usr/bin/env python3
import requests
import os
import sys
import json
from argparse import ArgumentParser
import subprocess
from libcxx_utils import util


class GithubActionsAPI(object):
  def __init__(self, token, substitutions=None):
    self.base_url = 'https://api.github.com/'
    self.session = requests.Session()
    self.session.headers['Authorization'] = 'token %s' % token
    self.session.headers['Accept'] = 'application/vnd.github.everest-preview+json'
    self.substitutions = substitutions or {}

  def addSubstitution(self, key, value):
    self.substitutions[key] = value


  def _createURL(self, endpoint, kwargs):
    parts = endpoint.split('/')
    new_parts = []
    for p in parts:
      if p.startswith(':'):
        value = kwargs.get(p[1:], self.substitutions.get(p[1:]))
        if value is None:
          raise Exception('Failed to find substitution for key "%s"' % p)
        new_parts += [value]
      else:
        new_parts += [p]
    return self.base_url + '/'.join(new_parts)

  def _get(self, api, **kwargs):
      return self.session.get(self._createURL(api, kwargs))

  def _post(self, api, replacements={}, json={}):
      return self.session.post(self._createURL(api, replacements), json=json)



  def _delete(self, api, **kwargs):
      return self.session.delete(self._createURL(api, kwargs))

  def getActionsDownloads(self, **kwargs):
    return self._get('repos/:owner/:repo/actions/runners/downloads', **kwargs)

  def getOrgActionsDownloads(self, **kwargs):
    return self._get('orgs/:owner/actions/runners/downloads', **kwargs)

  def getRunners(self, **kwargs):
    return self._get('repos/:owner/:repo/actions/runners', **kwargs)

  def getRunner(self, **kwargs):
    return self._get('repos/:owner/:repo/actions/runners/:runner_id', **kwargs)

  def getCreationToken(self, **kwargs):
    return self._post('repos/:owner/actions/runners/registration-token', **kwargs)

  def getCreationTokenForOrg(self, **kwargs):
    return self._post('orgs/:owner/actions/runners/registration-token', **kwargs)

  def getRemovalToken(self, **kwargs):
    return self._post('repos/:owner/:repo/actions/runners/remove-token', **kwargs)

  def removeRunner(self, **kwargs):
    return self._delete('repos/:owner/:repo/actions/runners/:runner_id', **kwargs)

  def getWorkflows(self, **kwargs):
    return self._get('repos/:owner/:repo/actions/workflows', **kwargs)

  def getWorkflow(self, **kwargs):
      return self._get('repos/:owner/:repo/actions/workflows/:workflow_id', **kwargs)

  def getWorkflowRuns(self, **kwargs):
    return self._get('repos/:owner/:repo/actions/runs', **kwargs)

  def getWorkflowRun(self, **kwargs):
    return self._get('repos/:owner/:repo/actions/runs/:run_id', **kwargs)

  def repoDispatchEvent(self, payload={}, **kwargs):
    payload = json.loads(payload)
    return self._post('repos/:owner/:repo/dispatches', replacements=kwargs, json=payload)

  def listBranches(self, **kwargs):
    return self._get('repos/:owner/:repo/branches', **kwargs)

  def listCredentials(self, **kwargs):
    return self._get('orgs/:owner/credential-authorizations', **kwargs)

  def getOrg(self, **kwargs):
    return self._get('orgs/:owner', **kwargs)


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
