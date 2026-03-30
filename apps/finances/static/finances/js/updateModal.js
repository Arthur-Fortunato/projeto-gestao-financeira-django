const modal = document.getElementById("modal-overlay");
const closeBtn = document.getElementById("close-modal");
const title = document.getElementById("modal-title");
const amount = document.getElementById("modal-amount");
const category = document.getElementById("modal-category");
const date = document.getElementById("modal-date");
const fixed = document.getElementById("modal-fixed");
const notes = document.getElementById("modal-notes");
const objectId = document.getElementById("modal-object-id");
const objectType = document.getElementById("modal-object-type");

document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        modal.classList.remove("hidden");
        objectId.value = btn.dataset.id;
        objectType.value = btn.dataset.type;
        title.value = btn.dataset.title;
        amount.value = btn.dataset.amount;
        category.value = btn.dataset.category;
        date.value = btn.dataset.date;
        fixed.checked = btn.dataset.fixed === "True";
        notes.value = btn.dataset.notes;
    });
});

closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
});

modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.add("hidden");
    }
});