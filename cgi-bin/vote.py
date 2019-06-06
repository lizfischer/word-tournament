#!/usr/bin/python
from jinja2 import FileSystemLoader, Environment
import cgi


form = cgi.FieldStorage()
name = form.getvalue("uid")
name = name.lower().strip()

matches = [
    ["apple", "orange"],
    ["orange", "blue"],
    ["blue", "bleu"],
    ["bleu", "rouge"],
    ["rouge", "rogue"],
    ["rogue", "wizard"],
    ["wizard", "lizard"],
    ["lizard", "blizzard"],
    ["blizzard", "microsoft"],
    ["microsoft", "apple"]
]

TEMPLATE_FILE = "page2.html"
templateLoader = FileSystemLoader(searchpath="./")
templateEnv = Environment(loader=templateLoader)
temp = templateEnv.get_template(TEMPLATE_FILE)

print("Content-type:text/html\r\n\r\n")
print(temp.render(locals()))