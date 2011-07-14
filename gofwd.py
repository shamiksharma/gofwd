import tornado.web
import tornado.ioloop
import tornado.httpserver
import database
import getopt, sys
import urlparse

#-------------------------------------------------

class BaseHandler(tornado.web.RequestHandler):
  @property
  def db(self):
    return self.application.db

#-------------------------------------------------

class AliasHandler(BaseHandler):

  def get(self, slug):
    self.render("form.html", title="Create Alias", alias=slug)

#-------------------------------------------------

class NewHandler(BaseHandler):

  def _update(self, alias, link):
    sqlString = 'insert or replace into gofwd (alias, link) values ("%s","%s");' % (alias, link)
    id = self.db.execute(sqlString)
    print "%d : %s " % (id, sqlString)
    self.render("created.html", title="Added Alias", alias=alias, link=link) 
    

  def post(self):
    alias = self.get_argument("alias")
    link  = self.get_argument("link")
    forceUpdate = self.get_argument("forceUpdate", False)

    if forceUpdate:
      self._update(alias, link)
    else:
      sqlString = 'select * from gofwd where alias = "%s" ' % (alias)
      record = self.db.get(sqlString)
      if record is None:
        self._update(alias, link)
      else:
        self.render("verify.html", title="Alias update", alias=alias, oldlink=record.link, link=link)
    return
    

#-------------------------------------------------

class GoHandler(BaseHandler):

  def get(self, slug):
    alias = slug  
    self.write("Redirecting for alias : " + slug)
    print "in go handler"

    sqlString = 'select * from gofwd where alias = "%s" ' % (alias)
    print sqlString

    record = self.db.get(sqlString)

    if record is None:
      print "No record"
      self.redirect("/alias/" + alias)
    else:
      link = urlparse.urljoin("http://", record.link)   # add the scheme in case its missing
      print link
      self.redirect(link)
      
#-------------------------------------------------

class Application(tornado.web.Application):
  def __init__(self, dbFile):
    handlers =  [ (r"/([^/]+)", GoHandler), (r"/alias/([^/]+)", AliasHandler), (r"/new", NewHandler)  ]
    settings = {}
    tornado.web.Application.__init__(self, handlers, **settings)
    self.db = database.Connection(dbFile)

#-------------------------------------------------

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg

#-------------------------------------------------

def main(argv=None):
    if argv is None:  argv = sys.argv
    try:
      try:
        opts, args = getopt.getopt(argv[1:], "d:p:",["database=","port="])
      except getopt.GetoptError, msg:
        raise Usage(msg)

      db = None
      port = 8080

      for o,a in opts:
        if o in ("-d", "--database"): 
          db = a
        if o in ("-p", "--port"): 
          port = a

      if db is None:
        raise Usage("No database specified")

      settings = { } 
      
      http_server = tornado.httpserver.HTTPServer(Application(db))
      http_server.listen(port)
      tornado.ioloop.IOLoop.instance().start()

    except Usage, err:
      print >>sys.stderr, "Usage: %s -d=[database]" % argv[0]
      return 2

#-------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())

#-------------------------------------------------
