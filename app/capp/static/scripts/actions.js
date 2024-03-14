
// function to show password
function showPassword() {

    let x = document.getElementById("password");

    if ( x.type == "password") {

        x.type = "text";
    } else {

        x.type = "password";
    }
}


// remove flashedMessage
function removeFlash() {

    let x = document.querySelector("#e-message-container > div");

    setTimeout(() => {
        x.remove()
    }, 3000)
}


// day clicked
const dayClicked = (element) => {
    window.location ="/displayEvents" + "?date=" + element.id
}

// event clicked
const eventClicked = (element) => {
    window.location ="/ve" + "?eidd=" + element.id
}

// delete event
const delEvent = (element) => {
    window.location ="/de" + "?eid=" + element.id
}

// edit event
const modEvent = (element) => {
    window.location ="/mode" + "?eid=" + element.id
}