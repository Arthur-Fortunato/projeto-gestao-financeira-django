const modal = document.getElementById("modal-overlay");
const closeBtn = document.getElementById("close-modal");
const modalTitle = document.getElementById("modal-title");
const historyList = document.getElementById("history-list");

document.querySelectorAll(".open-history").forEach((button) => {
  button.addEventListener("click", async () => {
    const goalId = button.dataset.goalId;
    const goalTitle = button.dataset.goalTitle;
    modalTitle.textContent = `Histórico: ${goalTitle}`;
    const response = await fetch(`./${goalId}/history/`);
    const entries = await response.json();
    historyList.innerHTML = entries.length
      ? entries
          .map(
            (entry) => `
            <li>
                <strong>${entry.date}</strong> - ${entry.amount >= 0 ? "+" : ""}R$ ${entry.amount}
                ${entry.note ? `- ${entry.note}` : ""}
            </li>
        `,
          )
          .join("")
      : "<li>Nenhuma movimentação.</li>";
    modal.classList.remove("hidden");
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
