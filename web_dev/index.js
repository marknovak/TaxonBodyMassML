let goButton, inputBar, inputBox, singleButton, listButton, csvCheck, outputBox, massOutput, learnMoreArrow, explanationModal, goBackButton, introBox, closeIntro;

export function initializeDOM(doc = document) {
  goButton = doc.getElementById("go-button");
  inputBar = doc.getElementById("inputBar");
  inputBox = doc.getElementById("input-box");
  singleButton = doc.getElementById("single-button");
  listButton = doc.getElementById("list-button");
  csvCheck = doc.getElementById("csv-check");
  outputBox = doc.getElementById("output-box");
  massOutput = doc.getElementById("massOutput");
  learnMoreArrow = doc.getElementById("learn-more-arrow");
  explanationModal = doc.getElementById("explanation-modal");
  goBackButton = doc.getElementById("go-back-button");
  introBox = doc.getElementById("intro-box");
  closeIntro = doc.getElementById("close-intro");

  Object.assign(globalThis, {
    goButton,
    inputBar,
    inputBox,
    singleButton,
    listButton,
    csvCheck,
    outputBox,
    massOutput,
    learnMoreArrow,
    explanationModal,
    goBackButton,
    introBox,
    closeIntro,
  });
}

export async function handleGoClick() {
  inputBox.classList.add("moved");
  goButton.textContent = "Go Again!";

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
    // ✅ dynamically reference exported function (so mock works)
    const data = await exports.myLookupMicroservice(userInput);

    if (data.status === "success") {
      massOutput.textContent = `success: ${data.message}`;
    } else {
      massOutput.textContent = `not success: ${data.error}`;
    }
  } catch (error) {
    console.error(error);
    massOutput.textContent = "Error";
  }

  inputBar.value = "";
}

export async function myLookupMicroservice(query) {
  const url = `https://haileystaxonbodymassml.onrender.com/single_species?species_name=${encodeURIComponent(query)}`;
  try {
    const response = await fetch(url);
    const data = await response.json();
    if (response.ok) {
      return {
        status: "success",
        message: `${data.species_name} mass = ${data.mass_g} g`,
      };
    } else {
      return { status: "error", error: data.error || "Unknown error" };
    }
  } catch (error) {
    console.error("Network error:", error);
    return { status: "error", error: "Network error" };
  }
}

export function handleListClick() {
  if (csvCheck.classList.contains("hidden")) csvCheck.classList.toggle("hidden");
}

export function handleSingleClick() {
  if (!csvCheck.classList.contains("hidden")) csvCheck.classList.toggle("hidden");
}

export function handleLearnMoreClick() {
  outputBox.classList.add("moved");
  learnMoreArrow.classList.toggle("hidden");
  explanationModal.classList.toggle("hidden");
  inputBox.classList.add("hidden");
  goBackButton.classList.toggle("hidden");
}

export function handleGoBackClick() {
  goBackButton.classList.toggle("hidden");
  outputBox.classList.remove("moved");
  inputBox.classList.toggle("hidden");
  explanationModal.classList.toggle("hidden");
  learnMoreArrow.classList.toggle("hidden");
}

export function handleCloseIntro() {
  introBox.classList.add("hidden");
}

if (typeof window !== "undefined") {
  window.addEventListener("DOMContentLoaded", () => {
    initializeDOM(document);
    goButton?.addEventListener("click", handleGoClick);
    inputBar?.addEventListener("keypress", (e) => e.key === "Enter" && handleGoClick());
    listButton?.addEventListener("click", handleListClick);
    singleButton?.addEventListener("click", handleSingleClick);
    learnMoreArrow?.addEventListener("click", handleLearnMoreClick);
    goBackButton?.addEventListener("click", handleGoBackClick);
    closeIntro?.addEventListener("click", handleCloseIntro);
  });
}
