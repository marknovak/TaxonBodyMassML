var goButton = document.getElementById("goButton")
var inputBar = document.getElementById("inputBar")
var inputBox = document.getElementById("inputBox")
var singleButton = document.getElementById("singleButton")
var listButton = document.getElementById("listButton")
var singleOrList = document.getElementById("singleOrList")
var csvCheck = document.getElementById("csvCheck")
var outputBox = document.getElementById("outputBox")
var massOutput = document.getElementById("massOutput")
var confidenceOutput = document.getElementById("confidenceOutput")
var learnMoreArrow = document.getElementById("learnMoreArrow")
var explanationModal = document.getElementById("explanationModal")
var goBackButton = document.getElementById("goBackButton")

function handleGoClick(event){
	inputBox.classList.add("moved")
	if (outputBox.classList.contains("hidden")){
		outputBox.classList.toggle("hidden")
		learnMoreArrow.classList.toggle("hidden")
	}

	const userInput = inputBar.value.trim();
        if (userInput) {
                massOutput.textContent = userInput
                inputBar.value = ''
        }
        else {
                massOutput.textContent = "input something"
        }

}

function handleListClick(event){
        if (csvCheck.classList.contains("hidden")){
		csvCheck.classList.toggle("hidden")
	}
}

function handleSingleClick(event){
        if (csvCheck.classList.contains("hidden")){
	}
	else{
		csvCheck.classList.toggle("hidden")
	}
}

function handleLearnMoreClick(event){
	outputBox.classList.add("moved")
	learnMoreArrow.classList.toggle("hidden")
	explanationModal.classList.toggle("hidden")
	inputBox.classList.add("hidden")
	goBackButton.classList.toggle("hidden")
}

function handleGoBackClick(event){
	goBackButton.classList.toggle("hidden")
	outputBox.classList.remove("moved")
	inputBox.classList.toggle("hidden")
	explanationModal.classList.toggle("hidden")
	learnMoreArrow.classList.toggle("hidden")
}


goButton.addEventListener("click", handleGoClick)
inputBar.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleGoClick();
  });

listButton.addEventListener("click", handleListClick)
singleButton.addEventListener("click", handleSingleClick)
learnMoreArrow.addEventListener("click", handleLearnMoreClick)
goBackButton.addEventListener("click", handleGoBackClick)


