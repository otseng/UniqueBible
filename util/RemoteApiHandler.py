import json
import logging
import config
from http import HTTPStatus

from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from db.BiblesSqlite import BiblesSqlite
from db.ToolsSqlite import Commentary, LexiconData, IndexesSqlite
from util.BibleBooks import BibleBooks


class ApiRequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(
            HTTPStatus.NOT_FOUND,
            "Not found")
        return None

class RemoteApiHandler(ApiRequestHandler):

    jsonData = {}

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('uba')
        config.internet = True
        try:
            super().__init__(*args, directory="htmlResources", **kwargs)
        except Exception as ex:
            print("Could not run init")
            print(ex)

    def do_POST(self):
        self.handleBadRequests()

    def do_HEAD(self):
        self.handleBadRequests()

    def handleBadRequests(self):
        self.jsonData = {'status': 'Error', 'message': 'Unsupported method'}
        self.sendJsonData()

    def sendJsonData(self):
        data = json.dumps(self.jsonData)
        self.commonHeader()
        self.wfile.write(bytes(data, "utf8"))

    def commonHeader(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.send_header("charset", "UTF-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate"),
        self.send_header("Pragma", "no-cache"),
        self.send_header("Expires", "0")
        self.end_headers()

    def send_error(self, code, message=None, explain=None):
        self.jsonData = {'status': 'Error', 'message': message}
        self.sendJsonData()

    def sendError(self, message):
        self.send_error("", message)

    def do_GET(self):
        try:
            self.clientIP = self.client_address[0]
            self.processRequest(self.path)
        except Exception as ex:
            self.jsonData = {'status': 'Error', 'exception': str(ex)}
        self.sendJsonData()

    def processRequest(self, request):
        query = parse_qs(urlparse(request).query)
        self.jsonData = {'status': "OK"}
        if "?" in request:
            request = request.split("?")[0]
        self.jsonData['request'] = request
        if query:
            self.jsonData['query'] = query
        cmd = request[1:].split("/")
        if len(cmd) > 0:
            if cmd[0].lower() == "data":
                self.processDataCommand(cmd, query)
            elif cmd[0].lower() == "list":
                self.processListCommand(cmd)
            elif cmd[0].lower() == "bible":
                self.processBibleCommand(cmd)

    # /data/bible/abbreviations?lang=[eng,sc,tc]
    # /data/bible/chapters
    # /data/bible/verses
    def processDataCommand(self, cmd, query):
        if cmd[1].lower() == "bible":
            if cmd[2].lower() == "abbreviations":
                lang = "eng"
                if query:
                    lang = query["lang"][0]
                data = []
                for key, value in BibleBooks().abbrev[lang].items():
                    data.append({'i': key, 'a': value[0], 'n': value[1]})
                self.jsonData['data'] = data
            elif cmd[2].lower() == "chapters":
                self.jsonData['data'] = BibleBooks.chapters
            elif cmd[2].lower() == "verses":
                self.jsonData['data'] = BibleBooks.verses

    # /list/bibles
    # /list/commentaries
    # /list/lexicons
    # /list/dictionaries
    def processListCommand(self, cmd):
        if cmd[1].lower() == "bibles":
            self.jsonData['data'] = [bible for bible in BiblesSqlite().getBibleList()]
        elif cmd[1].lower() == "commentaries":
            self.jsonData['data'] = [commentary for commentary in Commentary().getCommentaryList()]
        elif cmd[1].lower() == "lexicons":
            self.jsonData['data'] = [lexicon for lexicon in LexiconData().lexiconList]
        elif cmd[1].lower() == "dictionaries":
            self.jsonData['data'] = [dictionary[0] for dictionary in IndexesSqlite().dictionaryList]

    # /bible/KJV/43/3
    # /bible/KJV/44/3/16
    def processBibleCommand(self, cmd):
        if len(cmd) < 4:
            self.sendError("Invalid command")
            return
        if len(cmd) == 4:
            verses = BiblesSqlite().readTextChapter(cmd[1], cmd[2], cmd[3])
        elif len(cmd) == 5:
            verses = [BiblesSqlite().readTextVerse(cmd[1], cmd[2], cmd[3], cmd[4])]
        rows = []
        for verse in verses:
            rows.append({'b': verse[0], 'c': verse[1], 'v': verse[2], 't': verse[3]})
        self.jsonData['data'] = rows






