function submitTextCommand(id) {
    el = document.getElementById(id);
    submitCommand("TEXT:::" + el.value);
}

function submitCommand(cmd) {
    el = document.getElementById('commandBar');
    el.innerHtml = cmd;
//    document.getElementById("commandForm").submit();
}