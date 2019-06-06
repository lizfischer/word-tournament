#!/usr/bin/python

import cgi

form = cgi.FieldStorage()


keys = form.keys()
name = form.getfirst("uid")

print("Content-type:text/html\r\n\r\n")
print("<html>")
print("<head>")
print("<title>Oh hey</title>")
print("</head>")
print("<body>")
print("<h2> %s selected these words:</h2>" % name)
for key in keys:
    if key != "uid":
        print(form.getvalue(key), "<br>")

print("</body>")
print("</html>")
