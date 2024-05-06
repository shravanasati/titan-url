(()=>{"use strict";function e(){return"undefined"!=typeof window}function t(){try{const e="production";if("development"===e||"test"===e)return"development"}catch(e){}return"production"}function n(){return"development"===((e()?window.vam:t())||"production")}document.getElementById("copyBtn").addEventListener("click",(async function(){let e=document.getElementById("result-url").innerText;await navigator.clipboard.writeText(e);let t=document.getElementById("copyBtn");t.innerText="Copied!",await(3e3,new Promise((e=>setTimeout(e,3e3)))),t.innerText="Copy"})),document.getElementById("shortenBtn").addEventListener("click",(async function(e){e.preventDefault(),console.log("shortening...");let t=(()=>{const e=document.getElementById("original-url").value;let t=document.getElementById("alias").value;return{"original-url":e,"alias-type":t?"custom":"random",alias:t,qr:!0}})(),n=document.querySelector("#result-url"),o=document.querySelector("#shortenBtn"),r=document.querySelector("#result-stat");return o.disabled=!0,o.value="Please wait...",r.innerText="",t["original-url"]?"custom"!==t["alias-type"]||t.alias.match(/^(?=.*[A-Za-z0-9])[\w\-]{1,50}$/gm)?void await fetch("/shorten",{method:"POST",cache:"no-cache",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)}).then((e=>e.json())).then((e=>{if(console.log(e),n.innerText=e.message,o.scrollIntoView(),o.disabled=!1,o.value="Shorten",e.ok){let n=t["original-url"].length,o=n-e.message.length;r.innerText=o>=0?`Link shortened by ${Math.round(o/n*100)}% 🤠`:`Link made longer by ${Math.round(Math.abs(o)/n*100)}% 😞`;const a=document.createElement("img");a.src=e.qr_code,a.alt="QR Code",a.classList.add("object-cover","object-center","rounded"),document.querySelector("#skullImg").remove(),document.querySelector("#qrContainer").appendChild(a)}})).catch((e=>{console.error(e),n.innerText="An error occured! Please try again later.",o.scrollIntoView()})):(n.innerText="Invalid alias! It must only contain alphanumeric characters, hyphens (-), underscores (_), and not be longer than 50 characters.",void o.scrollIntoView()):(n.innerText="Please enter a URL.",void o.scrollIntoView())})),function(o={debug:!0}){var r;if(!e())return;!function(e="auto"){window.vam="auto"!==e?e:t()}(o.mode),window.va||(window.va=function(...e){(window.vaq=window.vaq||[]).push(e)}),o.beforeSend&&(null==(r=window.va)||r.call(window,"beforeSend",o.beforeSend));const a=o.scriptSrc||(n()?"https://va.vercel-scripts.com/v1/script.debug.js":"/_vercel/insights/script.js");if(document.head.querySelector(`script[src*="${a}"]`))return;const c=document.createElement("script");c.src=a,c.defer=!0,c.dataset.sdkn="@vercel/analytics"+(o.framework?`/${o.framework}`:""),c.dataset.sdkv="1.2.2",o.disableAutoTrack&&(c.dataset.disableAutoTrack="1"),o.endpoint&&(c.dataset.endpoint=o.endpoint),o.dsn&&(c.dataset.dsn=o.dsn),c.onerror=()=>{const e=n()?"Please check if any ad blockers are enabled and try again.":"Be sure to enable Web Analytics for your project and deploy again. See https://vercel.com/docs/analytics/quickstart for more information.";console.log(`[Vercel Web Analytics] Failed to load script from ${a}. ${e}`)},n()&&!1===o.debug&&(c.dataset.debug="false"),document.head.appendChild(c)}({mode:"production"})})();