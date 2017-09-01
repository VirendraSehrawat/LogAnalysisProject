#!/usr/bin/python3
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
    body{
    font-family: Helvetica, Arial ,sans-serif;
    box-sizing: border-box;
    background: white;
    margin: 0;
    }
    .container{
    max-width: 750px;
    margin: auto;
    padding: 0px 10px;
    background: darkgrey;
    min-height: 100vh;
    }

.container > ul{
    border: 1px solid grey;
    background-color:white;
    border-radius: 15px;
    padding: 0px;
    margin:0px;
}

.container >ul >li{
    margin: 0;
    display: flex;
    padding: 10px 10px;
    border-bottom: 1px solid grey;
}

.container >h1{
    background-color: blueviolet;
    margin:-1px -10px;
    padding:15px 0px;
    border-bottom:1px solid voilet;
    text-align: center;
    box-shadow: 0 1px 0 #888888;
}
.container >h4{
    margin: 15px 0;
}
.container >ul :last-child{
    border:0;
}

.name {
    width: 70%%;
}
.value{
    width: 30%%;
}

.value{
    text-align: right;
}

.loading{
    padding: 10px;
}

    </style>
  </head>
  <body >
  <div class='container'>
    <h1>News Report</h1>
    <!-- post content will go here -->
    <h4>Articles</h4>
    <ul id="pa">
     <div class="loading">Loading Popular articles...</div>
    </ul>
    <h4>Authors</h4>
    <ul id="aa">
    <div class="loading">Loading Popular authors...</div>
    </ul>
    <h4>High Failed Dates</h4>
    <ul id="rc">
    <div class="loading">Loading Failed records...</div>
    </ul>
%s
</div>
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
    <li><div class=name>%s</div> <div class=value> %s </div></li>
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
                    POST % (date, str(error_percentage) + ' %')
                    for date, error_percentage in getRequestCount())
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
