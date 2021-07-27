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
    let aliasType = document.getElementById("alias").value
    let slug = document.getElementById("slug").value

    console.log(url);
    console.log(aliasType);
    console.log(slug);

    return {
        "original-url": url,
        "alias-type": aliasType,
        "slug": slug
    }
}

async function shorten() {
    console.log("shortening...");
    let requestData = getRequestData()

    let data = new FormData()
    data.append("original-url", requestData["original-url"])
    data.append("alias-type", requestData["alias-type"])
    data.append("slug", requestData["slug"])

    await fetch("/shorten", {
        method: 'POST',
        cache: 'no-cache',
        body: data,
    })

    .then(response => {return response.json()})

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