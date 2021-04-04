import os, re

if __name__ == '__main__':
    from util.ConfigUtil import ConfigUtil
    ConfigUtil.setup()

from ThirdParty import Converter


class BibleDataConverter:

    # New Heart Bible
    # https://nheb.net/
    def convertNewHeartBible(self, filename):

        if not os.path.isfile(filename):
            print("{0} does not exist".format(filename))
            exit()

        text = "NHEB"
        description = "New Heart English Bible"

        bookNumDict = {
            "Gen": "1",
            "Exo": "2",
            "Lev": "3",
            "Num": "4",
            "Deu": "5",
            "Jos": "6",
            "Jdg": "7",
            "Rut": "8",
            "1Sa": "9",
            "2Sa": "10",
            "1Ki": "11",
            "2Ki": "12",
            "1Ch": "13",
            "2Ch": "14",
            "Ezr": "15",
            "Neh": "16",
            "Est": "17",
            "Job": "18",
            "Psa": "19",
            "Pro": "20",
            "Ecc": "21",
            "Sol": "None",
            "Isa": "23",
            "Jer": "24",
            "Lam": "25",
            "Eze": "26",
            "Dan": "27",
            "Hos": "28",
            "Joe": "29",
            "Amo": "30",
            "Oba": "31",
            "Jon": "32",
            "Mic": "33",
            "Nah": "34",
            "Hab": "35",
            "Zep": "36",
            "Hag": "37",
            "Zec": "38",
            "Mal": "39",
            "Mat": "40",
            "Mar": "41",
            "Luk": "42",
            "Joh": "43",
            "Act": "44",
            "Rom": "45",
            "1Co": "46",
            "2Co": "47",
            "Gal": "48",
            "Eph": "49",
            "Phi": "50",
            "Col": "51",
            "1Th": "52",
            "2Th": "53",
            "1Ti": "54",
            "2Ti": "55",
            "Tit": "56",
            "Phm": "57",
            "Heb": "58",
            "Jam": "59",
            "1Pe": "60",
            "2Pe": "61",
            "1Jo": "62",
            "2Jo": "63",
            "3Jo": "64",
            "Jud": "65",
            "Rev": "66",
        }

        count = 0
        versesData = []
        file = open(filename, "r", encoding="ISO-8859-1")
        lines = file.readlines()
        for line in lines:
            count += 1
            if line.startswith("//"):
                if "Update" in line:
                    update = re.search(r"Update (.*) \(a\)", line).group(1)
                    description += " - " + update
            else:
                (bookName, chapterNum, verseNum, scripture) = re.search(r"(\S*) (\S*):(\S*) (.*$)", line).groups()
                bookNum = bookNumDict[bookName]
                row = [bookNum, chapterNum, verseNum, scripture]
                versesData.append(row)

        print("Read {0} lines".format(count))

        Converter().mySwordBibleToRichFormat(description, text, versesData)
        Converter().mySwordBibleToPlainFormat(description, text, versesData)


if __name__ == '__main__':

    BibleDataConverter().convertNewHeartBible("/Users/otseng/Downloads/NHEB.txt")

    print("Done")
