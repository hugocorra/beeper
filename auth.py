#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    A simple flask app to authenticate with Google's OAuth 2.0 API

    Requirements:
        Flask>=0.10.0
        requests-oauthlib>=0.5.0
        To install, run: "pip install Flask>=0.10.0 requests-oauthlib>=0.5.0"

    Running:
        export GOOGLE_CLIENT_ID="123456789-jhkgljk2g34lkjg24.apps.googleusercontent.com"
        export GOOGLE_CLIENT_SECRET="SDfKsdflkSJDFSFDHhjsdfIUWER"
        export SECRET_KEY="SECRET_KEY_OF_YOUR_CHOOSING"
        ./google_login.py

        NB: OAuth 2 requires HTTPS. This app will override that if DEBUG is set in
            the environment.

    Misc:
        tox.ini:
        [flake8]
        ignore = F999,E128,E124,F403,E121,W503
        max-line-length = 99
"""

from __future__ import (
  absolute_import,
  unicode_literals,
)
import os
try:
    from flask import (
      Flask,
      flash,
      redirect,
      render_template_string,
      request,
      session,
      url_for,
    )
    import requests
    from requests_oauthlib import OAuth2Session
except ImportError:
    raise RuntimeError('Requirements not set up, see "Requirements":\n' + __doc__)


app = Flask(__name__)
app.config.update({
  'DEBUG': bool(os.environ.get('DEBUG')),
  'SECRET_KEY': os.environ.get('SECRET_KEY', 'CHANGEME'),
  'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
  'GOOGLE_CLIENT_SECRET': os.environ.get('GOOGLE_CLIENT_SECRET'),
})

if app.debug:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

if not app.config['GOOGLE_CLIENT_ID'] or not app.config['GOOGLE_CLIENT_SECRET']:
    raise RuntimeError('Environment not set up, see "Running":\n' + __doc__)


@app.route('/auth', defaults={'action': 'login'})
@app.route('/auth/<action>')
def auth(action):
    """ All-purpose authentication view.
        Stores `next` GET param in session (to persist around OAuth redirects)
        Stores referrer in session (to redirect back to on error)
        Refreshes token for logged in user if action == 'refresh'
        Revokes the token for logged in user if action == 'revoke'
        Logs out already logged-in users if action == 'logout'
        Handles initial redirect off to Google to being OAuth 2.0 flow
        Handles redirect back from Google & retreiving OAuth token
        Stores user info & OAuth token in `session['user']`
    """

    # Store some useful destinations in session
    if not request.args.get('state'):
        session['last'] = request.referrer or url_for('index')
        if 'next' in request.args:
            session['next'] = url_for(request.args['next'])
        else:
            session['next'] = session['last']

    # User logged in, refresh
    if session.get('user') and action == 'refresh':
        if 'refresh_token' not in session['user']['token']:
            flash('Could not refresh, token not present', 'danger')
            return redirect(session['last'])
        google = OAuth2Session(
          app.config['GOOGLE_CLIENT_ID'],
          token=session['user']['token']
        )
        session['user']['token'] = google.refresh_token(
          'https://accounts.google.com/o/oauth2/token',
          client_id=app.config['GOOGLE_CLIENT_ID'],
          client_secret=app.config['GOOGLE_CLIENT_SECRET']
        )
        flash('Token refreshed', 'success')
        return redirect(session['next'])

    # User loggedin - logout &/or revoke
    if session.get('user'):
        if action == 'revoke':
            response = requests.get(
              'https://accounts.google.com/o/oauth2/revoke',
              params={'token': session['user']['token']['access_token']}
            )
            if response.status_code == 200:
                flash('Authorization revoked', 'warning')
            else:
                flash('Could not revoke token: {}'.format(response.content), 'danger')
        if action in ['logout', 'revoke']:
            del session['user']
            flash('Logged out', 'success')
        return redirect(session['last'])

    google = OAuth2Session(
      app.config['GOOGLE_CLIENT_ID'],
      scope=[
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
      ],
      redirect_uri=url_for('auth', _external=True),
      state=session.get('state')
    )

    # Initial client request, no `state` from OAuth redirect
    if not request.args.get('state'):
        url, state = google.authorization_url(
          'https://accounts.google.com/o/oauth2/auth',
          access_type='offline'
        )
        session['state'] = state
        return redirect(url)

    # Error returned from Google
    if request.args.get('error'):
        error = request.args['error']
        if error == 'access_denied':
            error = 'Not logged in'
        flash('Error: {}'.format(error), 'danger')
        return redirect(session['last'])

    # Redirect from google with OAuth2 state
    token = google.fetch_token(
      'https://accounts.google.com/o/oauth2/token',
      client_secret=app.config['GOOGLE_CLIENT_SECRET'],
      authorization_response=request.url
    )
    user = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    user['token'] = token
    session['user'] = user
    flash('Logged in', 'success')
    return redirect(session['next'])


@app.route('/')
def index():
    """
    Simple view to display info returned from Google (or a link to login)
    """
    return render_template_string(
      '''
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <meta http-equiv="x-ua-compatible" content="ie=edge">
            <title>Login with Google</title>
            <link
              rel="stylesheet"
              href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.2/css/bootstrap.min.css"
              integrity="sha384-y3tfxAZXuh4HwSYylfB+J125MxIs6mR5FOHamPBG064zB+AFeWH94NdvaCBm8qnd"
              crossorigin="anonymous">
          </head>
          <body>
            <div class="container">
              {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
              <div class="row m-t-2">
                <div class="col-md-6 col-md-offset-3">
                    {% for category, message in messages %}
                    <div
                      class="alert alert-{{ category }} alert-dismissible fade in"
                      role="alert">
                      <button
                        type="button"
                        class="close"
                        data-dismiss="alert"
                        aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                      </button>
                      {{ message }}
                    </div>
                    {% endfor %}
                </div>
              </div>
              {% endif %}
              {% endwith %}
              <div class="row m-t-2">
                <div class="col-md-6 col-md-offset-3">
                  <div class="card">
                    {% if user %}
                    <img
                      class="card-img-top img-fluid center-block"
                      style="min-width: 100%"
                      data-src="{{ user.picture }}"
                      src="{{ user.picture }}"
                      alt="{{ user.name }} Profile Picture">
                    <div class="card-header text-xs-center">
                      <h4>{{ user.name }}</h4>
                    </div>
                    <div class="card-block text-muted">
                      <dl class="card-text">
                        <dt>email</dt>
                        <dd class="p-l-1">{{ user.email }}</dd>
                        <dt>id</dt>
                        <dd class="p-l-1">{{ user.id }}</dd>
                        <dt>access token</dt>
                        <dd class="p-l-1" title="{{ user.token.access_token }}">
                          {{ user.token.access_token|truncate(16) }}</dd>
                        <dt>gender</dt>
                        <dd class="p-l-1">{{ user.gender }}</dd>
                        <dt>locale</dt>
                        <dd class="p-l-1">{{ user.locale }}</dd>
                      </dl>
                    </div>
                    <div class="card-footer text-xs-center">
                      <a
                        href="{{ url_for('auth', action='logout') }}"
                        class="btn btn-primary">Logout</a>
                      <a
                        href="{{ url_for('auth', action='refresh') }}"
                        class="btn btn-success">Refresh</a>
                      <a
                        href="{{ url_for('auth', action='revoke') }}"
                        class="btn btn-danger">Revoke</a>
                    </div>
                    {% else %}
                    <div class="card-header text-xs-center">
                      <h4>Google Login</h4>
                    </div>
                    <div class="card-block text-xs-center text-muted">
                      This app will attempt to authenticate you through Google
                      OAuth 2.0
                    </div>
                    <div class="card-footer text-xs-center">
                        <a href="{{ url_for('auth') }}" class="btn btn-primary">Login</a>
                    </div>
                    {% endif %}
                  </div>
                </div>
              </div>
            </div>
            <script
              src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
            <script
              src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.1.1/js/tether.min.js"></script>
            <script
              src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.2/js/bootstrap.min.js"
              integrity="sha384-vZ2WRJMwsjRMW/8U7i6PWi6AlO1L79snBrmgiDpgIWJ82z8eA5lenwvxbMV1PAh7"
              crossorigin="anonymous"></script>
          </body>
        </html>
      ''',
      user=session.get('user')
    )


if __name__ == '__main__':
    app.run('0.0.0.0', 5000, use_reloader=app.debug, use_debugger=app.debug)