import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users

# Google account of admin
admin = 'xxx@xx.xx.xx' 

MAIN_PAGE_HTML = """\
<html>
  <body>
    <h1>Run Code</h1>
    <h2> API List<h2>
    <table border=1px text-align=left style="font-size: 26px">
        <tr>
            <th>URL</th>
            <th>Description</th>
        </tr>
        <tr>
            <td>/runcode/</td>
            <td>Introduction</td>
        </tr>
        <tr>
            <td>/runcode/set?name=A&code=1</td>
            <td>Set code as 1 for team A. (Need admin)</td>
        </tr>
        <tr>
            <td>/runcode/list</td>
            <td>List all names and code if login as admin.</td>
        </tr>
        <tr>
            <td>/runcode/clear</td>
            <td>Clear game. (Need admin)</td>
        </tr>
        <tr>
            <td>/runcode/check?name=A&code=1</td>
            <td>check if the code of team A is 1.</td>
        </tr>
    </table>
  </body>
</html>
"""

def getRunCode(name):
    qry = RunCode.query(RunCode.name == name).get()
    if qry:
        return qry
    else:
        return None

def createLogoutUrl():
    logout_url = users.create_logout_url('/')
    url = '(<a href="{}">sign out</a>)'.format(logout_url)
    return url

def createHomeUrl():
    url = '<a href="/runcode/">RunCode</a>'
    return url

# Declare the structure of entity
class RunCode(ndb.Model):
    name = ndb.StringProperty()
    code = ndb.IntegerProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(MAIN_PAGE_HTML)

class SetCode(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        n = self.request.get("name")
        c = int(self.request.get("code"))

        if user.email() != admin:
            nickname = user.nickname()
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('You ({}) don\'t have permission to set code. {}'.format(nickname, createLogoutUrl()))
            return None

        runcode = getRunCode(n)
        if runcode:
            runcode.code = c
            runcode.put()
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('Code has been updated successfully. {}'.format(createHomeUrl()))
        else:
            new_code = RunCode(name=n, code=c)
            new_code_key = new_code.put()
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('Code has been set successfully. {}'.format(createHomeUrl()))
        return None
    
    get = post

class ClearGame(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user.email() != admin:
            nickname = user.nickname()
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('You ({}) don\'t have permission to clear code. {}'.format(nickname, createLogoutUrl()))
            return None

        qry = RunCode.query()
    
        for code in qry:
            code.key.delete()
        
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('Game has been cleared successfully. {}'.format(createHomeUrl()))

    get = post

class ListName(webapp2.RequestHandler):
    def post(self):
        qry = RunCode.query()
        if qry.count() != 0:
            self.response.headers['Content-Type'] = 'text/html'
            for runcode in qry:
                self.response.write('{}<br>'.format(runcode.name))
            self.response.write('{}'.format(createHomeUrl()))
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('No runcode exists. {}'.format(createHomeUrl()))

    get = post

class CheckCode(webapp2.RequestHandler):
    def post(self):
        n = self.request.get("name")
        c = int(self.request.get("code"))
        qry = RunCode.query(RunCode.name == n).get()
        
        if qry:
            self.response.headers['Content-Type'] = 'text/html'
            if qry.code == c:
                self.response.write("YES")
            else:
                self.response.write("NO")
        else:
            self.response.write('name {} does not exist.'.format(n))

    get = post

app = webapp2.WSGIApplication([
	('/runcode/set', SetCode),
	('/runcode/clear', ClearGame),
	('/runcode/list', ListName),
	('/runcode/check', CheckCode),
	('/runcode/.*', MainPage)
], debug=True)
