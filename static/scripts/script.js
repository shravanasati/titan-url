console.log("grubgrbui");
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function copyToClipboard() {
    let resultURL = document.getElementById("result-url").innerText
    await navigator.clipboard.writeText(resultURL)
    let copybtn = document.getElementById("copyBtn")
    copybtn.innerText = "Copied!"
    await sleep(3000)
    copybtn.innerText = "Copy"
}

function shorten() {
    console.log("request");
    let url = document.getElementById("original-url").innerText
    if(url.trim() == "") {return}
    fetch("/shorten")
    .then(resp => resp.json())
    .then(json => console.log(json))
}
let copyBtn = document.getElementById("copyBtn")

copyBtn.addEventListener("click", copyToClipboard)

let shortenBtn = document.getElementById("shortenBtn")
console.log(shortenBtn);
shortenBtn.addEventListener("click", shorten)