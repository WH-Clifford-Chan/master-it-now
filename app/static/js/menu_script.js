/* ---------------- MENU TOGGLE ---------------- */
document.querySelectorAll(".menu-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();

        document.querySelectorAll(".menu-dropdown")
            .forEach(m => m.classList.add("hidden"));

        btn.parentElement.querySelector(".menu-dropdown")
            .classList.toggle("hidden");
    });
});

document.addEventListener("click", () => {
    document.querySelectorAll(".menu-dropdown")
        .forEach(m => m.classList.add("hidden"));
});


/* ---------------- INLINE RENAME ---------------- */
document.querySelectorAll(".rename-btn").forEach(btn => {
    btn.addEventListener("click", () => {

        const id = btn.dataset.id;

        const titleEl = document.querySelector(
            `.set-title[data-id="${id}"]`
        );

        const oldName = titleEl.textContent.trim();

        const input = document.createElement("input");
        input.type = "text";
        input.value = oldName;
        input.className = "rename-inline-input";

        titleEl.replaceWith(input);
        input.focus();

        const save = async () => {
            const newName = input.value.trim();
            if (!newName) return;

            await fetch(`/sets/rename/${id}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ name: newName })
            });

            const h3 = document.createElement("h3");
            h3.className = "set-title";
            h3.dataset.id = id;
            h3.textContent = newName;

            input.replaceWith(h3);
        };

        input.addEventListener("blur", save);
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") input.blur();
            if (e.key === "Escape") input.replaceWith(titleEl);
        });

    });
});


/* ---------------- DELETE ---------------- */
document.querySelectorAll(".delete-btn").forEach(btn => {
    btn.addEventListener("click", async () => {

        const id = btn.dataset.id;
        const card = btn.closest(".cards-item");

        const response = await fetch(`/sets/delete/${id}`, {
            method: "POST"
        });

        if (!response.ok) {
            alert("{{ _('Unable to delete set. Please try again.') }}");
            return;
        }

        card.style.transition = "0.2s ease";
        card.style.opacity = "0";
        card.style.transform = "scale(0.95)";

        setTimeout(() => card.remove(), 200);
    });
});
