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

const getRequestData = () => {
    const url = document.getElementById("original-url")
    const aliasType = document.getElementById("alias-type")
    let slug = ""

    if (aliasType == "custom") {
        slug = document.getElementById("custom-slug")
    }

    return {
        "url": url,
        "aliasType": aliasType,
        "slug": slug
    }
}

async function shorten() {
    let requestData = getRequestData()

    await fetch("/shorten", {
        method: 'GET',
        cache: 'no-cache', 
        headers: {
            'Content-Type': 'application/json',
            'original-url': requestData["url"],
            'alias-type': requestData["aliasType"],
            'slug': requestData["slug"]
        },
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

let copyBtn = document.getElementById("copyBtn")
copyBtn.addEventListener("click", copyToClipboard)