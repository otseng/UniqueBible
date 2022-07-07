import html
import os
import re
from urllib import request
import config

if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QClipboard
else:
    from qtpy.QtWidgets import QApplication
    from qtpy.QtGui import QClipboard

def remove_tags(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

if ":::" in config.eventCommand:
    commandList = config.eventCommand.split(":::")
    strongs = commandList[1].lower().strip()

    hebrew = False
    greek = False
    first = strongs[0]
    if (first == 'h'):
        hebrew = True
    elif (first == 'h'):
        greek = True
    else:
        first = 'g'
        greek = True
    results = re.findall(r'\d+', strongs)
    if results:
        number = results[0]

    TRLIT_DIR = "/home/oliver/dev/transliteral_bible"
    file = TRLIT_DIR + "/strongs/" + first + "/" + first + number + ".md"
    if os.path.isfile(file):
        with open(file, 'r') as myfile:
            filedata = myfile.read()
        re_transliteral = re.compile(r'\[(.*)\]\(https:\/\/www.blueletterbible.org')
        s_transliteral = html.unescape(re_transliteral.search(filedata).group(1))
        s_transliteral = s_transliteral.replace('`', "'")
        text = "[" + s_transliteral + "](../" + file + ")"
        text = text.replace(TRLIT_DIR, "")
        text = text.replace("//", "/../")
        config.mainWindow.setClipboardText(text)
    else:
        url = "https://www.blueletterbible.org/lexicon/" + strongs
        try:
            response = request.urlopen(url)
            pagedata = response.read().decode("utf-8")
            re_transliteral = re.compile('<title>.* - (.*) - .*</title>')
            s_transliteral = html.unescape(re_transliteral.search(pagedata).group(1))

            if first == 'g':
                re_original = re.compile('lexTitleGk.*>(.*)<')
                s_original = re_original.search(pagedata).group(1)
            elif first == 'h':
                re_original = re.compile('lexTitleHb.*>(.*)<')
                s_original = re_original.search(pagedata).group(1)

            re_count = re.compile('which occurs (.*) times in .*>(.*)<')
            g_count = re_count.search(pagedata)
            s_count1 = g_count.group(1)
            s_count2 = g_count.group(2)

            re_speech = re.compile('Part of Speech</div>[\s\S]*<div class="small-text-right">(.*)</div>')
            g_speech = re_speech.search(pagedata)
            s_speech = g_speech.group(1).strip()

            re_definition = re.compile('following manner:(.*)</div>')
            g_definition = re_definition.search(pagedata)
            s_definition = g_definition.group(1).strip()
            s_definition = remove_tags(s_definition)
            s_definition = s_definition.replace('&nbsp;', ' ')

            outfile = open(file, "w")

            outfile.write("# " + s_original + "\n\n")
            outfile.write("[" + s_transliteral + "](" + url + ")\n\n")
            outfile.write("Definition:" + s_definition + "\n\n")
            outfile.write("Part of speech: " + s_speech + "\n\n")
            outfile.write("Occurs " + s_count1 + " times in " + s_count2 + " verses\n\n")
            outfile.write("## Articles\n\n")

            if first == 'g':
                outfile.write("[Study Light](https://www.studylight.org/lexicons/greek/" + number + ".html)\n\n")
                outfile.write("[Bible Hub](https://biblehub.com/str/greek/" + number + ".htm)\n\n")
                outfile.write("[LSJ](https://lsj.gr/wiki/" + s_original + ")\n\n")
                outfile.write("[NET Bible](http://classic.net.bible.org/strong.php?id=" + number + ")\n\n")
                outfile.write("[Bible Bento](https://biblebento.com/dictionary/G" + number + ".html)\n\n")
                outfile.write("[Bible Study Company](https://biblestudycompany.com/reader/strongs/" + number + "/greek)\n\n")
                outfile.write("[Lexicon Concordance](http://lexiconcordance.com/greek/" + number + ".html)\n\n")
                outfile.write("[New Jerusalem](http://www.newjerusalem.org/Strongs/g" + number + ")\n\n")
            if first == 'h':
                outfile.write("[Study Light](https://www.studylight.org/lexicons/hebrew/" + number + ".html)\n\n")
                outfile.write("[Bible Hub](https://biblehub.com/str/hebrew/" + number + ".htm)\n\n")
                outfile.write("[NET Bible](http://classic.net.bible.org/strong.php?id=0" + number + ")\n\n")
                outfile.write("[Bible Bento](https://biblebento.com/dictionary/H" + number + ".html)\n\n")
                outfile.write("[Bible Study Company](https://biblestudycompany.com/reader/strongs/" + number + "/hebrew)\n\n")
                outfile.write("[Lexicon Concordance](http://lexiconcordance.com/hebrew/" + number + ".html)\n\n")
                outfile.write("[New Jerusalem](http://www.newjerusalem.org/Strongs/h" + number + ")\n")

            outfile.close()

            # https://www.url-encode-decode.com/
            encoded = s_transliteral.replace("ō", "%C5%8D")
            encoded = s_transliteral.replace("ē", "%C4%93")

            s_transliteral = s_transliteral.replace('`', "'")
            text = "[" + s_transliteral + "](../" + file + ")"
            text = text.replace(TRLIT_DIR, "")
            text = text.replace("//", "/../")
            config.mainWindow.setClipboardText(text)
            QApplication.clipboard().setText(text)
            QApplication.clipboard().setText(text, QClipboard.Selection)
            QApplication.clipboard().setText(text, QClipboard.Clipboard)

            # config.mainWindow.openBrowser(url)
        except Exception as ex:
            print(ex)
