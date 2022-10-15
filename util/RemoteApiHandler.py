import hashlib
import json
import logging
import os, re, config, pprint, glob
import subprocess
import urllib
from http import HTTPStatus

import requests
from http.server import SimpleHTTPRequestHandler
from time import gmtime
from util.BibleBooks import BibleBooks
from util.BibleVerseParser import BibleVerseParser
from db.BiblesSqlite import BiblesSqlite, Bible
from util.GitHubRepoInfo import GitHubRepoInfo
from util.TextCommandParser import TextCommandParser
from util.RemoteCliMainWindow import RemoteCliMainWindow
from urllib.parse import urlparse, parse_qs
from util.FileUtil import FileUtil
from util.LanguageUtil import LanguageUtil
from pathlib import Path
from util.HtmlGeneratorUtil import HtmlGeneratorUtil


class ApiRequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(
            HTTPStatus.NOT_FOUND,
            "Not found")
        return None

class RemoteApiHandler(ApiRequestHandler):

    parser = None
    textCommandParser = None
    bibles = None
    books = None
    bookMap = None
    abbreviations = None
    session = None
    users = []
    adminUsers = []
    whiteListFile = "ip_whitelist.txt"
    whiteListIPs = []
    blackListFile = "ip_blacklist.txt"
    blackListIPs = []

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('uba')
        if RemoteApiHandler.textCommandParser is None:
            RemoteApiHandler.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.textCommandParser = RemoteApiHandler.textCommandParser
        config.internet = True
        config.mainWindow = self
        self.runStartupPlugins()
        if RemoteApiHandler.bibles is None:
            RemoteApiHandler.bibles = [(bible, bible) for bible in BiblesSqlite().getBibleList()]
        self.bibles = RemoteApiHandler.bibles
        if RemoteApiHandler.parser is None:
            RemoteApiHandler.parser = BibleVerseParser(config.parserStandarisation)
        self.parser = RemoteApiHandler.parser
        if RemoteApiHandler.abbreviations is None:
            RemoteApiHandler.abbreviations = self.parser.standardAbbreviation
        self.abbreviations = RemoteApiHandler.abbreviations
        if RemoteApiHandler.books is None:
            RemoteApiHandler.books = [(k, v) for k, v in self.abbreviations.items() if int(k) <= 69]
            RemoteApiHandler.bookMap = {k: v for k, v in self.abbreviations.items() if int(k) <= 69}
        self.books = RemoteApiHandler.books
        self.bookMap = RemoteApiHandler.bookMap
        self.users = RemoteApiHandler.users
        self.adminUsers = RemoteApiHandler.adminUsers
        self.primaryUser = False
        if config.httpServerViewerGlobalMode:
            try:
                urllib.request.urlopen(config.httpServerViewerBaseUrl)
            except:
                config.httpServerViewerGlobalMode = False
        try:
            if os.path.exists(self.whiteListFile):
                self.whiteListIPs = [ip.strip() for ip in open(self.whiteListFile, "r").readlines()]
            else:
                Path(self.whiteListFile).touch()
            if os.path.exists(self.blackListFile):
                self.blackListIPs = [ip.strip() for ip in open(self.blackListFile, "r").readlines()]
        except Exception as ex:
            print("Could not read white/blacklists")
            print(ex)
        try:
            super().__init__(*args, directory="htmlResources", **kwargs)
        except Exception as ex:
            print("Could not run init")
            print(ex)

    def runStartupPlugins(self):
        config.bibleWindowContentTransformers = []
        config.customCommandShortcuts = {}
        if config.enablePlugins:
            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
                if not plugin in config.excludeStartupPlugins:
                    script = os.path.join(os.getcwd(), "plugins", "startup", "{0}.py".format(plugin))
                    config.mainWindow.execPythonFile(script)

    def execPythonFile(self, script):
        self.textCommandParser.parent.execPythonFile(script)

    def do_POST(self):
        self.handleBadRequests()

    def do_HEAD(self):
        self.handleBadRequests()

    def handleBadRequests(self):
        jsonData = {'status': 'Error', 'message': 'Unsupported method'}
        self.sendJson(jsonData)

    def sendJson(self, jsonData):
        data = json.dumps(jsonData)
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
        jsonData = {'status': 'Error', 'message': f'{message}'}
        data = json.dumps(jsonData)
        self.commonHeader()
        self.wfile.write(bytes(data, "utf8"))

    def do_GET(self):
        try:
            self.clientIP = self.client_address[0]
            jsonData = self.processRequest(self.path)
        except Exception as ex:
            jsonData = {'status': 'Error', 'exception': f'{ex}'}
        self.sendJson(jsonData)

    def processRequest(self, request):
        query_components = parse_qs(urlparse(request).query)
        jsonData = {'status': "OK"}
        return jsonData

