# Copy this file into secrets.py and set keys, secrets and scopes.

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here: 
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = "\xb4\x144\xbf\xa6?m?]W\xdd\x03j\xec\xb7\xdb\xf5\xc3E\xab\xb7Z\xe0a\xce\xea\xfb\r\xed\x89\xb2\xbaq\xe0`^\xd5\x8b\x1d#\xdb\xc1N\x18\x9eo\x80\xc3;ac4\xcc\xb9\x1c\xebZ_\xa2\x8c\x95\xa5zX"

# Google APIs
GOOGLE_APP_ID = '15796694514-ebss75hnifu0qgcmd9m8r478sp7e7fds.apps.googleusercontent.com'
GOOGLE_APP_SECRET = '3lflJmio1mB69mgzbBNlyTwg'

# Facebook auth apis
FACEBOOK_APP_ID = '320961788060528'
FACEBOOK_APP_SECRET = '79cdd29de58d62388712429e4466a906'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'nB9fkeo8HVd5iAAJpu1ffPHtb'
TWITTER_CONSUMER_SECRET = '4vXyF42HCpyLE5RTUMwwML9bB8rpQaAOkMZ8sugxHfL6wjoMua'


# config that summarizes the above
AUTH_CONFIG = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.profile'),

  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'user_about_me'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)

  # OpenID doesn't need any key/secret
}
