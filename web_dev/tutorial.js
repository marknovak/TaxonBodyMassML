const tutorialSegment = document.getElementById('tutorial-segment')
const tutorialStart = document.getElementById('tutorial-start')
const inputBarTutorial = document.getElementById('input-bar-tutorial')
const inputBarNext = document.getElementById('input-bar-next')
const singleTutorial = document.getElementById('single-tutorial')
const singleNext = document.getElementById('single-next')
const listTutorial = document.getElementById('list-tutorial')
const listNext = document.getElementById('list-next')
const csvCheckTutorial = document.getElementById('csv-check-tutorial')
const csvCheckNext = document.getElementById('csv-check-next')
const goTutorial = document.getElementById('go-tutorial')
const goNext = document.getElementById('go-next')
const outputTutorial = document.getElementById('output-tutorial')
const outputNext = document.getElementById('output-next')
const changeInputTutorial = document.getElementById('change-input-tutorial')
const changeInputNext = document.getElementById('change-input-next')
const goAgainTutorial = document.getElementById('go-again-tutorial')
const goAgainNext = document.getElementById('go-again-next')
const learnMoreTutorial = document.getElementById('learn-more-tutorial')
const learnMoreNext = document.getElementById('learn-more-next')
const dataTutorial = document.getElementById('data-tutorial')
const dataNext = document.getElementById('data-next')
const informationTutorial = document.getElementById('information-tutorial')
const informationNext = document.getElementById('information-next')
const helpPageTutorial = document.getElementById('help-page-tutorial')
const cancels = document.getElementsByClassName('cancel')
const toolTips = document.getElementsByClassName('tool-tip')


const handleBeginTutorialClick = (event) => {
  for (var i = 0; i < toolTips.length; i++) {
    if (!toolTips[i].classList.contains("hidden")) {
      toolTips[i].classList.add("hidden")
    }
  }
  if (inputBarTutorial.classList.contains("hidden")) {
    inputBarTutorial.classList.remove("hidden")
  }
}

const handleInputNextClick = (event) => {
  inputBarTutorial.classList.add("hidden")
  singleTutorial.classList.remove("hidden")
}

const handleSingleNextClick = (event) => {
  singleTutorial.classList.add("hidden")
  listTutorial.classList.remove("hidden")
}

const handleListNextClick = (event) => {
  listTutorial.classList.add("hidden")
  csvCheckTutorial.classList.remove("hidden")
}

const handleCsvCheckNextClick = (event) => {
  csvCheckTutorial.classList.add("hidden")
  goTutorial.classList.remove("hidden")
}

const handleGoNextClick = (event) => {
  goTutorial.classList.add("hidden")
  outputTutorial.classList.remove("hidden")
}

const handleOutputNextClick = (event) => {
  outputTutorial.classList.add("hidden")
  changeInputTutorial.classList.remove("hidden")
}

const handleChangeInputNextClick = (event) => {
  changeInputTutorial.classList.add("hidden")
  goAgainTutorial.classList.remove("hidden")
}

const handleGoAgainNextClick = (event) => {
  goAgainTutorial.classList.add("hidden")
  learnMoreTutorial.classList.remove("hidden")
}

const handleLearnMoreNextClick = (event) => {
  learnMoreTutorial.classList.add("hidden")
  dataTutorial.classList.remove("hidden")
}

const handleDataNextClick = (event) => {
  dataTutorial.classList.add("hidden")
  informationTutorial.classList.remove("hidden")
}

const handleInformationNextClick = (event) => {
  informationTutorial.classList.add("hidden")
  helpPageTutorial.classList.remove("hidden")
}

const handleExitTutorialClick = (event) => {
  for (var i = 0; i < toolTips.length; i++) {
    if (!toolTips[i].classList.contains("hidden")) {
      toolTips[i].classList.add("hidden")
    }
  }
}

for (let i = 0; i < cancels.length; i++) {
  cancels[i].addEventListener("click", handleExitTutorialClick)
}

beginTutorialButton.addEventListener("click", handleBeginTutorialClick)

inputBarNext.addEventListener("click", handleInputNextClick)
singleNext.addEventListener("click", handleSingleNextClick)
listNext.addEventListener("click", handleListNextClick)
csvCheckNext.addEventListener("click", handleCsvCheckNextClick)
outputNext.addEventListener("click", handleOutputNextClick)
goNext.addEventListener("click", handleGoNextClick)
changeInputNext.addEventListener("click", handleChangeInputNextClick)
goAgainNext.addEventListener("click", handleGoAgainNextClick)
learnMoreNext.addEventListener("click", handleLearnMoreNextClick)
dataNext.addEventListener("click", handleDataNextClick)
informationNext.addEventListener("click", handleInformationNextClick)

