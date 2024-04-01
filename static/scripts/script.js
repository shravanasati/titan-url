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

let copyBtn = document.getElementById("copyBtn")
copyBtn.addEventListener("click", copyToClipboard)

const getRequestData = () => {
    const url = document.getElementById("original-url").value
    let alias = document.getElementById("alias").value
    let aliasType = (alias) ? "custom" : "random";

    console.log(url);
    console.log(aliasType);
    console.log(alias);

    return {
        "original-url": url,
        "alias-type": aliasType,
        "alias": alias
    }
}

async function shorten(ev) {
    ev.preventDefault();
    console.log("shortening...");
    let requestData = getRequestData()
    if (!requestData["original-url"]) {
        let urlText = document.querySelector("#result-url");
        urlText.innerText = "Please enter a URL.";
        urlText.scrollIntoView();
        return;
    }

    console.log(typeof JSON.stringify(requestData));
    console.log(JSON.stringify(requestData));

    await fetch("/shorten", {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData),
    })

        .then(response => { return response.json() })

        .then(data => {
            let urlText = document.getElementById("result-url")
            urlText.innerText = data["message"]
            urlText.scrollIntoView()
        })

        .catch(err => {
            let urlText = document.getElementById("result-url")
            urlText.innerText = "An error occured! Check your internet connection."
            urlText.scrollIntoView()
        })

}


let shortenBtn = document.getElementById("shortenBtn")
shortenBtn.addEventListener("click", shorten)