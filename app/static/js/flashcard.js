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

    fetch('/tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('Audio request failed');
        }
        return response.arrayBuffer();
    })
    .then((buffer) => {
        const blob = new Blob([buffer], { type: 'audio/mpeg' });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
        audio.addEventListener('ended', () => URL.revokeObjectURL(url));
    })
    .catch((error) => {
        console.error('Audio playback error:', error);
    });
}

function openModal() {
    document.getElementById("editModal").classList.add("show");
}

function closeModal() {
    document.getElementById("editModal").classList.remove("show");
}

function resetImageDeleteState() {
    const fileInput = document.querySelector('form.edit-form input[type="file"][name="front_image"]');
    const deleteFlag = document.getElementById('deleteImageFlag');
    const preview = document.querySelector('.current-image-preview');

    if (fileInput) {
        fileInput.value = '';
    }

    if (deleteFlag) {
        deleteFlag.value = '1';
    }

    if (preview) {
        preview.remove();
    }
}

document.addEventListener('click', (event) => {
    const deleteButton = event.target.closest('.delete-image');
    if (!deleteButton) return;

    event.preventDefault();
    resetImageDeleteState();
});

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