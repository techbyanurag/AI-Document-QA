async function sendQuestion() {
    const questionInput = document.getElementById("question");
    const chat = document.getElementById("chat");
    const fileInput = document.getElementById("fileInput");

    const question = questionInput.value;

    // Upload files first
    if (fileInput.files.length > 0) {
        const formData = new FormData();

        for (let file of fileInput.files) {
            formData.append("files", file);
        }

        await fetch("/upload", {
            method: "POST",
            body: formData
        });

        fileInput.value = "";
    }

    // USER MESSAGE
    const userMsg = document.createElement("div");
    userMsg.className = "user-msg";
    userMsg.innerText = question;
    chat.appendChild(userMsg);

    // ASK API
    const res = await fetch(`/ask?question=${encodeURIComponent(question)}`, {
        method: "POST"
    });

    const data = await res.json();

    // AI MESSAGE
    const aiMsg = document.createElement("div");
    aiMsg.className = "ai-msg";
    aiMsg.innerText = data.answer;
    chat.appendChild(aiMsg);

    questionInput.value = "";
    chat.scrollTop = chat.scrollHeight;
}