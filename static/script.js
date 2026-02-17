let loadTimer = null;

/* ================= AUTO LOAD ================= */
function autoLoad() {
    clearTimeout(loadTimer);

    loadTimer = setTimeout(() => {
        loadInfo();
    }, 800); // wait after typing
}


/* ================= LOAD VIDEO INFO ================= */
async function loadInfo() {
    const url = document.getElementById("url").value.trim();
    const status = document.getElementById("status");
    const thumb = document.getElementById("thumb");
    const quality = document.getElementById("quality");

    if (!url) return;

    status.innerText = "Loading video info...";
    thumb.style.display = "none";

    try {
        const res = await fetch("/info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!res.ok) {
            status.innerText = "Error loading video info";
            return;
        }

        const data = await res.json();

        if (data.error) {
            status.innerText = "Error loading video info";
            return;
        }

        /* ----- THUMBNAIL ----- */
        if (data.thumbnail) {
            thumb.src = data.thumbnail;
            thumb.style.display = "block";
        }

        /* ----- RESOLUTIONS ----- */
        quality.innerHTML = "<option>Best</option>";

        if (Array.isArray(data.resolutions)) {
            data.resolutions.forEach(r => {
                quality.innerHTML += `<option>${r}</option>`;
            });
        }

        status.innerText = "Ready to download";

    } catch (error) {
        console.error("LoadInfo Error:", error);
        status.innerText = "Error loading video info";
    }
}


/* ================= DOWNLOAD ================= */
async function download() {
    const url = document.getElementById("url").value.trim();
    const quality = document.getElementById("quality").value;
    const mode = document.querySelector("input[name='mode']:checked").value;

    const loader = document.getElementById("loaderContainer");
    const status = document.getElementById("status");
    const button = document.querySelector("button");

    if (!url) return;

    loader.style.display = "flex";
    status.innerText = "Preparing download...";
    button.disabled = true;

    try {
        const response = await fetch("/download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, mode, quality })
        });

        if (!response.ok) {
            throw new Error("Download failed");
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = "";  // let browser choose file name
        document.body.appendChild(link);
        link.click();

        link.remove();
        window.URL.revokeObjectURL(downloadUrl);

        status.innerText = "Download started!";
    } catch (error) {
        console.error("Download Error:", error);
        status.innerText = "Download failed!";
    }

    loader.style.display = "none";
    button.disabled = false;
}
