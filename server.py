from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import http

from reportdb import getMostArticleAuthors
from reportdb import getMostPopularArticle
from reportdb import getRequestCount

import threading
from socketserver import ThreadingMixIn


# HTML template for the news page
HTML_WRAP = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>DB Forum</title>
    <style>
      h1, form { text-align: center; }
      textarea { width: 400px; height: 100px; }
      div.post { border: 1px solid #999;
                 padding: 10px 10px;
                 margin: 10px 20%%; }
      hr.postbound { width: 50%%; }
      em.date { color: #999 }
    </style>
  </head>
  <body style="text-align:center" >
    <h1>News Report</h1>
    <!-- post content will go here -->
    <h3>Articles</h3>
    <div id="pa">
    Loading Popular articles...
    </div>
    <h3>Authors</h3>
    <div id="aa">
    Loading Popular authors...
    </div>
    <h3>High Failed Dates</h3>    
    <div id="rc">
    Loading Failed records...
    </div>
%s

    <script
  src="https://code.jquery.com/jquery-3.2.1.min.js"
  integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
  crossorigin="anonymous"></script>

  <script>
  $(window).ready(function(){
      $.ajax({url:"/pa", success:function(result){
          $('#pa').html(result);
      }})
      $.ajax({url:"/aa", success:function(result){
          $('#aa').html(result);
      }})
      $.ajax({url:"/rc", success:function(result){
          $('#rc').html(result);
      }})
  });
  </script>
  </body>
</html
'''

# HTML template for an individual comment
POST = '''\
    <div class=post><em class=date>%s</em><br>%s</div>
'''


class ThreadHttpServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."


class RequestHandler (BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            print(self.path)
            self.send_response(200)
            self.send_header("content-type", "text/html")
            self.end_headers()
            if self.path.endswith("/pa"):
                posts = "".join(
                    POST % (title, num) for title, num
                    in getMostPopularArticle())
                self.wfile.write(posts.encode())
                return
            if self.path.endswith("/aa"):
                authors = "".join(
                    POST % (name, num) for name, num
                    in getMostArticleAuthors())
                self.wfile.write(authors.encode())
                return
            if self.path.endswith("/rc"):
                requests = "".join(
                    POST % (date, data_item.evaluate_precent())
                    for date, data_item in getRequestCount().items())
                self.wfile.write(requests.encode())
                return
            body = ""
            html = HTML_WRAP % body
            self.wfile.write(html.encode())
        except IOError:
            self.send_error(404, "File not found %s" % self.path)

if __name__ == '__main__':
    try:
        port = 3000
        server_address = ('', port)
        httpd = ThreadHttpServer(server_address, RequestHandler)
        print("Web server is running on ports %s" % port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("^C entered, stopping web server ...")
        httpd.socket.close()
