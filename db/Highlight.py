import os, sqlite3, re
import config

class Highlight:

    CREATE_HIGHLIGHT_TABLE = "CREATE TABLE IF NOT EXISTS Highlight (Book INT, Chapter INT, Verse INT, Code NVARCHAR(5))"

    def __init__(self):
        self.filename = os.path.join(config.marvelData, "highlights.bible")
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists():
            self.createHighlightTable()

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def createHighlightTable(self):
        self.cursor.execute(Highlight.CREATE_HIGHLIGHT_TABLE)

    def checkTableExists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Highlight'")
        if self.cursor.fetchone():
            return True
        else:
            return False

    def highlightVerse(self, b, c, v, code):
        delete = "DELETE FROM Highlight WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(delete, (b, c, v))
        self.connection.commit()
        if code:
            insert = "INSERT INTO Highlight (Book, Chapter, Verse, Code) VALUES (?, ?, ?, ?)"
            self.cursor.execute(insert, (b, c, v, code))
            self.connection.commit()
            
    def getVerseDict(self, b, c):
        query = "SELECT Verse, Code FROM Highlight WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return {res[0]: res[1] for res in self.cursor.fetchall()}

    def highlightChapter(self, b, c, text):
        highlightDict = self.getVerseDict(b, c)
        for v in highlightDict.keys():
            find = '<verse>(<vid id="v' + str(b) + '\.' + str(c) + '\.' + str(v) + '".*?)</verse>'
            text = re.sub(find, "<verse class='hl_{0}'>\\1</verse".format(highlightDict[v]), text)
        return text

if __name__ == "__main__":

    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
    hl = Highlight()
    hl.highlightVerse(43, 3, 16, 'h1')
    hl.highlightVerse(43, 3, 22, 'h1')
    hl.highlightVerse(1, 1, 1, 'h2')
    hl.highlightVerse(1, 1, 2, 'h3')

    text = '''<verse><vid id="v43.3.16" onclick="luV(16)" onmouseover="qV(16)" ondblclick="mV(16)">16</vid> for God did so love the world, that His Son--the only begotten--He gave, that every one who is believing in him may not perish, but may have life age-during.</verse><verse><vid id="v43.3.17" onclick="luV(17)" onmouseover="qV(17)" ondblclick="mV(17)"> 17</vid> For God did not send His Son to the world that he may judge the world, but that the world may be saved through him;</verse><verse><vid id="v43.3.18" onclick="luV(18)" onmouseover="qV(18)" ondblclick="mV(18)"> 18</vid> he who is believing in him is not judged, but he who is not believing hath been judged already, because he hath not believed in the name of the only begotten Son of God.</verse><verse><vid id="v43.3.19" onclick="luV(19)" onmouseover="qV(19)" ondblclick="mV(19)"> 19</vid> 'And this is the judgment, that the light hath come to the world, and men did love the darkness rather than the light, for their works were evil;</verse><verse><vid id="v43.3.20" onclick="luV(20)" onmouseover="qV(20)" ondblclick="mV(20)">20</vid> for every one who is doing wicked things hateth the light, and doth not come unto the light, that his works may not be detected;</verse><verse><vid id="v43.3.21" onclick="luV(21)" onmouseover="qV(21)" ondblclick="mV(21)">21</vid> but he who is doing the truth doth come to the light, that his works may be manifested, that in God they are having been wrought.'<br><br></verse><verse><vid id="v43.3.22" onclick="luV(22)" onmouseover="qV(22)" ondblclick="mV(22)"> 22</vid> After these things came Jesus and his disciples to the land of Judea, and there he did tarry with them, and was baptizing;</verse><verse><vid id="v43.3.23" onclick="luV(23)" onmouseover="qV(23)" ondblclick="mV(23)"> 23</vid> and John was also baptizing in Aenon, nigh to Salem, because there were many waters there, and they were coming and were being baptized--</verse><verse><vid id="v43.3.24" onclick="luV(24)" onmouseover="qV(24)" ondblclick="mV(24)"> 24</vid> for John was not yet cast into the prison--</verse>'''

    text = hl.highlightChapter(43, 3, text)
    print(text)