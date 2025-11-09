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
var introBox = document.getElementById("introBox")
var closeIntro = document.getElementById("closeIntro")

async function handleGoClick(event) {
	inputBox.classList.add("moved");

	if (outputBox.classList.contains("hidden")) {
    		outputBox.classList.toggle("hidden");
    		learnMoreArrow.classList.toggle("hidden");
  	}

  	const userInput = inputBar.value.trim();
  	if (!userInput) {
    		massOutput.textContent = "no input";
    		return;
  	}

  	massOutput.textContent = "Checking species name...";

  	try {
    		// I will replace this with Grant's microservice when it's ready
   		const data = await myFakeMicroservice(userInput);

   		if (data.status === "success") {
      			massOutput.textContent = `success: ${data.message}`;
    		}
		else {
      			massOutput.textContent = `not success: ${data.error}`;
    		}
	}
	catch (error) {
        	console.error(error);
        	massOutput.textContent = "Error";
    	}

  	inputBar.value = "";
}

//get rid of this later
async function myFakeMicroservice(query) {
  	const speciesList = ["Homo sapiens", "Canis lupus", "Felis catus"];

  	if (speciesList.includes(query)) {
    		return { status: "success", message: `${query}` };
 	 } 	
	else {
    		return { status: "error", error: `not found` };
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

function handleCloseIntro(event){
	introBox.classList.add("hidden")
}

goButton.addEventListener("click", handleGoClick)
inputBar.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleGoClick();
  });

listButton.addEventListener("click", handleListClick)
singleButton.addEventListener("click", handleSingleClick)
learnMoreArrow.addEventListener("click", handleLearnMoreClick)
goBackButton.addEventListener("click", handleGoBackClick)
closeIntro.addEventListener("click", handleCloseIntro)


