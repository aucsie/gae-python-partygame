import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users
import json

admin = 'au4451@au.edu.tw'

MAIN_PAGE_HTML = """\
<html>
  <body>
    <h1>Pass Gate</h1>
    <h2> API List<h2>
    <table border=1px text-align=left style="font-size: 26px">
        <tr>
            <th>URL</th>
            <th>Description</th>
        </tr>
        <tr>
            <td>/passgate/</td>
            <td>Introduction</td>
        </tr>
        <tr>
            <td>/passgate/create?level=hell&pwd=guard&loc=au</td>
            <td>Create a gate.</td>
        </tr>
        <tr>
            <td>/passgate/login?level=hell&pwd=guard</td>
            <td>Login gate.</td>
        </tr>
        <tr>
            <td>/passgate/submit?team=hero&level=hell&score=10</td>
            <td>Give hero a score (1-10) by gate keeper.</td>
        </tr>
        <tr>
            <td>/passgate/delete?level=hell</td>
            <td>Delete gate.</td>
        </tr>
        <tr>
            <td>
            /passgate/show<br>
            /passgate/show?team=[name]<br>
            /passgate/show?level=[name]<br>
            </td>
            <td>Show the status.</td>
        </tr>
        <tr>
            <td>/passgate/clear</td>
            <td>Clear game. (Need admin)</td>
        </tr>
    </table>
  </body>
</html>
"""

def getPassGate(level):
    qry = PassGate.query(PassGate.level == level).get()
    if qry:
        return qry
    else:
        return None

def getPassScore(level, team):
    if team != None:
        qry = PassScore.query(ndb.AND(PassScore.team==team, PassScore.level==level)).get()
    else:
        qry = PassScore.query(PassScore.level==level)
        
    if qry:
        return qry
    else:
        return None

def createLogoutUrl():
    logout_url = users.create_logout_url('/')
    url = '(<a href="{}">sign out</a>)'.format(logout_url)
    return url

def createHomeUrl():
    url = '<a href="/passgate/">PassGate</a>'
    return url

# Declare the structure of entity
class PassGate(ndb.Model):
    level = ndb.StringProperty()
    pwd = ndb.StringProperty()
    loc = ndb.StringProperty()

class PassScore(ndb.Model):
    team = ndb.StringProperty()
    level = ndb.StringProperty()
    score = ndb.IntegerProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(MAIN_PAGE_HTML)

class CreateGate(webapp2.RequestHandler):
    def post(self):
        mlevel = self.request.get("level")
        mpwd = self.request.get("pwd")
        mloc = self.request.get("loc")

        passgate = getPassGate(mlevel)
        if passgate:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('FAIL')
        else:
            new_gate = PassGate(level=mlevel, pwd=mpwd, loc=mloc)
            new_gate_key = new_gate.put()
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('OK')
        return None
    
    get = post

class LoginGate(webapp2.RequestHandler):
    def post(self):
        mlevel = self.request.get("level")
        mpwd = self.request.get("pwd")
        passgate = getPassGate(mlevel)
        
        if passgate.pwd == mpwd:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('OK')
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('FAIL')
        return None

    get = post

class SubmitScore(webapp2.RequestHandler):
    def post(self):
        mteam = self.request.get("team")
        mlevel = self.request.get("level")
        mscore = int(self.request.get("score"))
        passscore = getPassScore(mlevel, mteam)
        
        if passscore:
            passscore.score = mscore
            passscore.put()
        else:
            new_passscore = PassScore(team=mteam,level=mlevel,score=mscore)
            new_passscore_key = new_passscore.put()

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('OK')
        return None

    get = post

class DeleteGate(webapp2.RequestHandler):
    def post(self):
        mlevel = self.request.get("level")
        passgate = getPassGate(mlevel)
        
        if passgate:
            passscores = getPassScore(mlevel, None)
            for passscore in passscores:
                passscore.key.delete()
            passgate.key.delete()
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('OK')
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('FAIL')
        return None

    get = post

class ShowStatus(webapp2.RequestHandler):
    def post(self):
      
        mlevel = self.request.get("level")
        mteam = self.request.get("team")

        status = dict()
        result = dict()
        
        if mlevel and mteam == '':
            passscores = PassScore.query(PassScore.level==mlevel)
            passscores = PassScore.query()
            for passscore in passscores:
                team = passscore.team
                score = int(passscore.score)
                status[team] = score
            result['level'] = mlevel
            result['status'] = status
            result = json.dumps(result, ensure_ascii=False)
        elif mteam  and mlevel == '':
            passscores = PassScore.query(PassScore.team==mteam)
            for passscore in passscores:
                level = passscore.level
                score = int(passscore.score)
                status[level] = score
            result['team'] = mteam
            result['status'] = status
            result = json.dumps(result, ensure_ascii=False)
        elif mteam == '' and mlevel == '':
            passscores = PassScore.query()
            for passscore in passscores:
                level = passscore.level
                team = passscore.team
                score = int(passscore.score)
                if team in status:
                    status[team] = status[team] + score
                else:
                    status[team] = score
            result = status
            result = json.dumps(result, ensure_ascii=False)
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('FAIL'+mlevel+mteam)
            return None

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(result)
        return None

    get = post

class ClearGame(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        #if user == None:
        #    self.response.headers['Content-Type'] = 'text/html'
        #    self.response.write('You need to login to clear game. {}'.format(createLogoutUrl()))
        #    return None
        if user.email() != admin:
            nickname = user.nickname()
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('You ({}) don\'t have permission to clear game. {}'.format(nickname, createLogoutUrl()))
            return None

        qry = PassGate.query()
    
        for passgate in qry:
            passgate.key.delete()
        
        qry = PassScore.query()
    
        for passscore in qry:
            passscore.key.delete()
        
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('Game has been cleared successfully. {}'.format(createHomeUrl()))

    get = post

app = webapp2.WSGIApplication([
	('/passgate/create', CreateGate),
        ('/passgate/login', LoginGate),
	('/passgate/submit', SubmitScore),
	('/passgate/delete', DeleteGate),
	('/passgate/show', ShowStatus),
	('/passgate/clear', ClearGame),
	('/passgate/.*', MainPage)
], debug=True)
