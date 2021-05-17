function submitTextCommand(id) {
    el = document.getElementById(id);
    submitCommand("TEXT:::" + el.value);
}

function submitBookCommand(id) {
    el = document.getElementById(id);
    value = el.options[el.selectedIndex].text;
    submitCommand(value);
}

function submitCommand(cmd) {
    el = document.getElementById('commandInput');
    el.value = cmd;
    document.getElementById("commandForm").submit();
}

function loadBible() {}

function getMobileOperatingSystem() {
    var userAgent = navigator.userAgent || navigator.vendor || window.opera;
    // Windows Phone must come first because its UA also contains "Android"
    if (/windows phone/i.test(userAgent)) {
        return "Windows Phone";
    }
    if (/android/i.test(userAgent)) {
        return "Android";
    }
    // iOS detection from: http://stackoverflow.com/a/9039885/177710
    if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
        return "iOS";
    }
    return "unknown";
}


function resizeSite() {
    // For iPhone ONLY, if ((/iPhone|iPod/.test(navigator.userAgent)) && (!window.MSStream)) { }
    if (getMobileOperatingSystem() == 'iOS') { disableIOSScrolling(); }

    var screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;

    var screenHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    if (screenWidth >= screenHeight) {landscape = 1;}
    else if (screenHeight >= screenWidth) {landscape = 0;}

    var contentHeight = screenHeight - 52;

    var addSpace;
    if ((landscape == 0) && (paraWin == 2)) {addSpace = (contentHeight / 2) - 110;}
    else {addSpace = contentHeight - 110;}
    if (addSpace <= 0) {addSpace = 1;}

    var bibleFrame = document.getElementById('bibleFrame');
    var bibleDoc = bibleFrame.contentDocument || bibleFrame.contentWindow.document;
    var bibleLastElement = bibleDoc.getElementById('lastElement');
    if (bibleLastElement) {
        bibleLastElement.style.display = 'block';
        bibleLastElement.style.height = addSpace + 'px';
    }
    if (getMobileOperatingSystem() == 'iOS') {
        var bBODY = bibleDoc.body; var bHTML = bibleDoc.documentElement;
        var bHeight = Math.max( bBODY.scrollHeight, bBODY.offsetHeight, bHTML.clientHeight, bHTML.scrollHeight, bHTML.offsetHeight );
        bibleFrame.height = bHeight;
        bibleFrame.style.height = bHeight + 'px';
    }

    var toolFrame = document.getElementById('toolFrame');
    var toolDoc = toolFrame.contentDocument || toolFrame.contentWindow.document;
    if ((paraWin == 2) && (paraContent == 'bible')) {
    var toolLastElement = toolDoc.getElementById('lastElement');
    toolLastElement.style.display = 'block';
    toolLastElement.style.height = addSpace + 'px';
    }
    if (getMobileOperatingSystem() == 'iOS') {
        var tBODY = toolDoc.body; var tHTML = toolDoc.documentElement;
        var tHeight = Math.max( tBODY.scrollHeight, tBODY.offsetHeight, tHTML.clientHeight, tHTML.scrollHeight, tHTML.offsetHeight );
        toolFrame.height = tHeight;
        toolFrame.style.height = tHeight + 'px';
    }

    var bibleDiv = document.getElementById('bibleDiv');
    var toolDiv = document.getElementById('toolDiv');

    switch(paraWin) {
        case 1:
        bibleDiv.style.borderBottom = 'none';
        toolDiv.style.borderTop = 'none';
        bibleDiv.style.width = screenWidth + 'px';
        bibleDiv.style.height = contentHeight + 'px';
        break;
        case 2:
        if (landscape == 1) {
        bibleDiv.style.borderBottom = 'none';
        toolDiv.style.borderTop = 'none';
        bibleDiv.style.width = (screenWidth / 2) + 'px';
        toolDiv.style.width = (screenWidth / 2) + 'px';
        bibleDiv.style.height = contentHeight + 'px';
        toolDiv.style.height = contentHeight + 'px';
        }
        else if (landscape == 0) {
        bibleDiv.style.width = screenWidth + 'px';
        toolDiv.style.width = screenWidth + 'px';
        bibleDiv.style.height = ((contentHeight - 4) / 2) + 'px';
        toolDiv.style.height = ((contentHeight - 4) / 2) + 'px';
        bibleDiv.style.borderBottom = '2px solid lightgrey';
        toolDiv.style.borderTop = '2px solid lightgrey';
        }
        break;
    }

    if (getMobileOperatingSystem() == 'iOS') { setTimeout(enableIOSScrolling,100); }

    // align content in view
    setTimeout(function() {
    if (activeB != undefined) { fixBibleVerse(); }
    if ((paraWin == 2) && (paraContent == 'tool')) {
        if (getMobileOperatingSystem() == 'iOS') {toolDiv.scrollTop = 0;}
        else {toolFrame.contentWindow.scrollTo(0,0);}
    }
    else if ((paraWin == 2) && (paraContent == 'bible') && (syncBible == 0)) {
        fixToolVerse(toolB,toolC,toolV);
    }
    },500);

    // workaround for iPhone; problem: navigation bar hide under "tabs" after changing from portrait to landscape
    setTimeout(function(){window.scrollTo(0, 1);}, 500);
}

function enableIOSScrolling() {
    var contentDiv = document.getElementById("content");
    var bibleDiv = document.getElementById("bibleDiv");
    var toolDiv = document.getElementById("toolDiv");
    contentDiv.style.overflowY = "scroll";
    contentDiv.style.overflowX = "auto";
    bibleDiv.style.overflowY = "scroll";
    bibleDiv.style.overflowX = "auto";
    toolDiv.style.overflowY = "scroll";
    toolDiv.style.overflowX = "auto";
    contentDiv.style.webkitOverflowScrolling = "touch";
    bibleDiv.style.webkitOverflowScrolling = "touch";
    toolDiv.style.webkitOverflowScrolling = "touch";
}

function disableIOSScrolling() {
    var contentDiv = document.getElementById("content");
    var bibleDiv = document.getElementById("bibleDiv");
    var toolDiv = document.getElementById("toolDiv");
    contentDiv.style.overflow = "auto";
    bibleDiv.style.overflow = "auto";
    toolDiv.style.overflow = "auto";
    contentDiv.style.webkitOverflowScrolling = "auto";
    bibleDiv.style.webkitOverflowScrolling = "auto";
    toolDiv.style.webkitOverflowScrolling = "auto";
}

function fixBibleVerse() {
}

function fixToolVerse(b,c,v) {
}
