function getCookie(name) {
    const match = document.cookie.match(
        "(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"
    );

    return match ? match.pop() : "";
}


document.addEventListener("DOMContentLoaded", () => {

    const toggle = document.getElementById("ai-toggle");
    const panel = document.getElementById("ai-panel");
    const close = document.getElementById("ai-close");

    const summarizeBtn = document.getElementById("summarize-btn");

    const startSection = document.getElementById("ai-start");
    const loadingSection = document.getElementById("ai-loading");
    const summaryResult = document.getElementById("summary-result");

    const summaryBox = document.getElementById("summary-box");


    /*
    --------------------------------------------------
    OPEN AI PANEL
    --------------------------------------------------
    */

    toggle.addEventListener("click", () => {

        panel.classList.add("ai-panel-open");

        toggle.classList.add("ai-toggle-hidden");

    });


    /*
    --------------------------------------------------
    CLOSE AI PANEL
    --------------------------------------------------
    */

    function closeAIPanel() {

        panel.classList.remove("ai-panel-open");

        toggle.classList.remove("ai-toggle-hidden");


        /*
        Clear the current summary from the UI.
        The database summary is NOT deleted.
        */

        summaryBox.textContent = "";

        summaryResult.style.display = "none";

        loadingSection.style.display = "none";

        startSection.style.display = "block";


        summarizeBtn.disabled = false;

        summarizeBtn.textContent = "✨ Summarize Article";
    }


    close.addEventListener("click", closeAIPanel);


    /*
    --------------------------------------------------
    SUMMARIZE ARTICLE
    --------------------------------------------------
    */

    summarizeBtn.addEventListener("click", async () => {

        const url = summarizeBtn.dataset.url;


        // Disable button while processing
        summarizeBtn.disabled = true;


        // Hide initial section
        startSection.style.display = "none";


        // Show loading
        loadingSection.style.display = "block";


        try {

            const response = await fetch(url, {

                method: "POST",

                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest",
                },

            });


            const data = await response.json();


            console.log("Status:", response.status);
            console.log("Response:", data);


            /*
            --------------------------------------------------
            SUCCESS
            --------------------------------------------------
            */

            if (response.ok && data.summary) {

                loadingSection.style.display = "none";

                summaryBox.textContent = data.summary;

                summaryResult.style.display = "block";

            }


            /*
            --------------------------------------------------
            ERROR
            --------------------------------------------------
            */

            else {

                loadingSection.style.display = "none";

                startSection.style.display = "block";

                summaryBox.textContent =
                    data.error ||
                    "Could not generate summary right now. Please try again later.";

                summaryResult.style.display = "block";

                summarizeBtn.disabled = false;

            }

        }


        /*
        --------------------------------------------------
        NETWORK ERROR
        --------------------------------------------------
        */

        catch (error) {

            console.error("Summarization request failed:", error);


            loadingSection.style.display = "none";

            startSection.style.display = "block";


            summaryBox.textContent =
                "Something went wrong. Please try again later.";


            summaryResult.style.display = "block";


            summarizeBtn.disabled = false;

        }

    });

});