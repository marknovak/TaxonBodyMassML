const questionBar = document.getElementById('question-bar')
const submitQuestion = document.getElementById('submit-question')
const questionBarDiv = document.getElementById('question-bar-div')
const questionsContent = document.getElementById('questions-content')


function loadQuestions() {
    const saved = JSON.parse(localStorage.getItem("questions")) || [];
    questionsContent.innerHTML = saved
        .map(q => `<p class="user-question">${q}</p>`)
        .join("");
}

function saveQuestion(question) {
    const saved = JSON.parse(localStorage.getItem("questions")) || [];
    saved.push(question);
    localStorage.setItem("questions", JSON.stringify(saved));
}

submitQuestion.addEventListener("click", () => {
    const text = questionBar.value.trim();
    if (text === "") return;

    const p = document.createElement("p");
    p.classList.add("user-question");
    p.textContent = text;

    const statusLabel = document.createElement("span");
    statusLabel.classList.add("unanswered");
    statusLabel.textContent = "- (unanswered)";
    p.appendChild(statusLabel)

    questionsContent.appendChild(p);
    saveQuestion(text);
    questionBar.value = "";
});

loadQuestions();

// to clear saved questions, use 'localStorage.clear()' in the inspect mode console



