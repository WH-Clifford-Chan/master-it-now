let flipped = false;

function flipCard() {
    const card = document.getElementById("flashcard");

    flipped = !flipped;

    if (flipped) {
        card.classList.add("flipped");
    } else {
        card.classList.remove("flipped");
    }
}

function playAudio() {
    const text = document.getElementById("term").innerText;

    speechSynthesis.cancel();
    speechSynthesis.speak(
        new SpeechSynthesisUtterance(text)
    );
}

function openModal() {
    document.getElementById("editModal").classList.add("show");
}

function closeModal() {
    document.getElementById("editModal").classList.remove("show");
}