// variable declarations: gets every element by it's unique ID
const goButton = document.getElementById('go-button')
const inputBar = document.getElementById('input-bar')
const inputBox = document.getElementById('input-box')
const singleButton = document.getElementById('single-button')
const listButton = document.getElementById('list-button')
const csvCheck = document.getElementById('csv-check')
const outputBox = document.getElementById('outputbox')
const massOutput = document.getElementById('mass-output')
const learnMoreArrow = document.getElementById('learn-more-arrow')
const explanationModal = document.getElementById('explanation-modal')
const goBackButton = document.getElementById('go-back-button')
const introBox = document.getElementById('intro-box')
const closeIntro = document.getElementById('close-intro')

// function definitions

// handleGoCick : makes output box visible and generates output based on input
async function handleGoClick (event) {
  inputBox.classList.add('moved')
  goButton.textContent = 'Go Again!'
  if (outputBox.classList.contains('hidden')) {
    outputBox.classList.toggle('hidden')
    learnMoreArrow.classList.toggle('hidden')
  }
  // if the user clicks go without typing any input
  const userInput = inputBar.value.trim()
  if (!userInput) {
    massOutput.textContent = 'no input'
    return
  }

  // while waiting for response
  massOutput.textContent = 'Checking species name...'

  // interacting with the microservice (prototype_lookup.py)
  try {
    const data = await myLookupMicroservice(userInput)

    if (data.status === 'success') {
      massOutput.textContent = `success: ${data.message}`
    } else {
      massOutput.textContent = `not success: ${data.error}`
    }
  } catch (error) {
    console.error(error)
    massOutput.textContent = 'Error'
  }
  // clears input bar
  inputBar.value = ''
}

// uses render to interact with the microservice
async function myLookupMicroservice (query) {
  const url = `https://haileystaxonbodymassml.onrender.com/single_species?species_name=${encodeURIComponent(query)}`

  try {
    const response = await fetch(url)
    const data = await response.json()

    if (response.ok) {
      return {
        status: 'success',
        message: `${data.species_name} mass = ${data.mass_g} g`
      }
    } else {
      return { status: 'error', error: data.error || 'Unknown error' }
    }
  } catch (error) {
    console.error('Network error:', error)
    return { status: 'error', error: 'Network error' }
  }
}

// reveals the csv checkbox
function handleListClick (event) {
  if (csvCheck.classList.contains('hidden')) {
    csvCheck.classList.toggle('hidden')
  }
}

// hides the csv check box
function handleSingleClick (event) {
  if (!csvCheck.classList.contains('hidden')) {
    csvCheck.classList.toggle('hidden')
  }
}

// hides the input box and reveals the explanation modal
function handleLearnMoreClick (event) {
  outputBox.classList.add('moved')
  learnMoreArrow.classList.toggle('hidden')
  explanationModal.classList.toggle('hidden')
  inputBox.classList.add('hidden')
  goBackButton.classList.toggle('hidden')
}

// hides the explanation modal and reveals the input box
function handleGoBackClick (event) {
  goBackButton.classList.toggle('hidden')
  outputBox.classList.remove('moved')
  inputBox.classList.toggle('hidden')
  explanationModal.classList.toggle('hidden')
  learnMoreArrow.classList.toggle('hidden')
}

// hides the introduction modal
function handleCloseIntro (event) {
  introBox.classList.add('hidden')
}

// event listener declarations: attaching all functions to their appropriate elements

goButton.addEventListener('click', handleGoClick)
inputBar.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleGoClick()
})

listButton.addEventListener('click', handleListClick)
singleButton.addEventListener('click', handleSingleClick)
learnMoreArrow.addEventListener('click', handleLearnMoreClick)
goBackButton.addEventListener('click', handleGoBackClick)
closeIntro.addEventListener('click', handleCloseIntro)
