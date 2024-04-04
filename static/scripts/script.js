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
    let urlText = document.querySelector("#result-url");
    let shortenBtn = document.querySelector("#shortenBtn")
    let resultStat = document.querySelector("#result-stat");

    shortenBtn.disabled = true;
    shortenBtn.value = "Please wait...";
    resultStat.innerText = "";

    if (!requestData["original-url"]) {
        urlText.innerText = "Please enter a URL.";
        shortenBtn.scrollIntoView();
        return;
    }
    if (requestData["alias-type"] === "custom" && !requestData["alias"].match(/^(?=.*[A-Za-z0-9])[\w\-]{1,50}$/gm)) {
        urlText.innerText = "Invalid alias! It must only contain alphanumeric characters, hyphens (-), underscores (_), and not be longer than 50 characters.";
        shortenBtn.scrollIntoView();
        return;
    }

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
            console.log(data);
            urlText.innerText = data["message"]
            shortenBtn.scrollIntoView()
            shortenBtn.disabled = false;
            shortenBtn.value = "Shorten";

            if (data["ok"]) {
                let lenOriginal = requestData["original-url"].length;
                let lenShortened = data["message"].length;
                let diff = lenOriginal - lenShortened;
                if (diff >= 0) {
                    resultStat.innerText = `Link shortened by ${Math.round(diff / lenOriginal * 100)}% 🤠`;
                } else {
                    resultStat.innerText = `Link made longer by ${Math.round(Math.abs(diff) / lenOriginal * 100)}% 😞`;
                }
            }
        })

        .catch(err => {
            urlText.innerText = "An error occured! Check your internet connection."
            shortenBtn.scrollIntoView()
        })

}


let shortenBtn = document.getElementById("shortenBtn")
shortenBtn.addEventListener("click", shorten)