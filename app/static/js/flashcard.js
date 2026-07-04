let flipped = false;
const keyboardShortcutsEnabledKey = 'keyboardShortcutsEnabled';
let keyboardShortcutsEnabled = true;

function flipCard() {
    const card = document.getElementById("flashcard");

    flipped = !flipped;

    if (flipped) {
        card.classList.add("flipped");
    } else {
        card.classList.remove("flipped");
    }
}

function setKeyboardShortcutsEnabled(enabled) {
    keyboardShortcutsEnabled = enabled;
    localStorage.setItem(keyboardShortcutsEnabledKey, String(enabled));
}

function initKeyboardShortcutToggle() {
    const savedValue = localStorage.getItem(keyboardShortcutsEnabledKey);
    keyboardShortcutsEnabled = savedValue === null ? true : savedValue === 'true';

    const toggle = document.getElementById('shortcutToggle');
    if (toggle) {
        const slider = toggle.parentElement.querySelector('.slider');
        toggle.checked = keyboardShortcutsEnabled;

        toggle.addEventListener('pointerdown', () => {
            if (toggle.checked && slider) {
                slider.classList.add('no-animation');
            }
        });

        toggle.addEventListener('change', () => {
            setKeyboardShortcutsEnabled(toggle.checked);
            if (toggle.checked && slider) {
                requestAnimationFrame(() => {
                    slider.classList.remove('no-animation');
                });
            }
            toggle.blur();
        });
    }
}

initKeyboardShortcutToggle();

function playAudio() {
    const text = document.getElementById("term").innerText;

    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US"; 

    speechSynthesis.speak(utterance);
}

function openModal() {
    document.getElementById("editModal").classList.add("show");
}

function closeModal() {
    document.getElementById("editModal").classList.remove("show");
}

document.addEventListener("keydown", (event) => {
    if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
        return;
    }

    const shortcuts = {
        " ": () => {
            event.preventDefault();
            flipCard();
        },
        "1": () => document.getElementById("forgotBtn").click(),
        "2": () => document.getElementById("hardBtn").click(),
        "3": () => document.getElementById("goodBtn").click(),
        "4": () => document.getElementById("easyBtn").click(),
        "w": () => document.getElementById("forgotBtn").click(),
        "a": () => document.getElementById("hardBtn").click(),
        "d": () => document.getElementById("goodBtn").click(),
        "s": () => document.getElementById("easyBtn").click(),
        "e": openModal,
        "esc": closeModal,
        "f": playAudio,
    };

    if (!keyboardShortcutsEnabled) {
        return;
    }

    const action = shortcuts[event.key.toLowerCase()] || shortcuts[event.key];
    if (action) action();
});