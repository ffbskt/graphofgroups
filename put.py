import argparse
import pprint
import sys

from apiclient import discovery
import httplib2
import oauth2client
from oauth2client import tools

CLIENT_ID = '100345890791-plkg6r45qth7lr88biovfmnd2loopl68.apps.googleusercontent.com'
CLIENT_SECRET = 'ROZNmJd2FNIDfivZqwf39Xxk'
SCOPE = 'https://www.googleapis.com/auth/userinfo.email'
USER_AGENT = 'my-cmdline-tool/1.0'
OAUTH_DISPLAY_NAME = 'My Commandline Tool'

def main(argv):
  # Parse command line flags used by the oauth2client library.
  parser = argparse.ArgumentParser(
      description='Auth sample',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args(argv[1:])
  print 'parser', parser
  # Acquire and store oauth token.
  storage = oauth2client.file.Storage('guestbook.dat')
  credentials = storage.get()
  print 'st, cr', storage, credentials
  if credentials is None or credentials.invalid:
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        user_agent=USER_AGENT,
        oauth_displayname=OAUTH_DISPLAY_NAME)
    credentials = tools.run_flow(flow, storage, flags)
  http = httplib2.Http()
  http = credentials.authorize(http)
  print 123
  # Build a service object for interacting with the API.
  api_root = 'https://universitygim.appspot.com/_ah/api'
  api = 'universitygim'
  version = 'v1'
  discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
  service = discovery.build(
      api, version, discoveryServiceUrl=discovery_url, http=http)

  # Fetch all greetings and print them out.
  response = service.greetings().list().execute()
  pprint.pprint(response)

  # Fetch a single greeting and print it out.
  response = service.greetings().get(id='9001').execute()
  pprint.pprint(response)

if __name__ == '__main__':
  main(sys.argv)
