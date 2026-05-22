const dateLabels = JSON.parse(
    document.getElementById("dateLabels").textContent,
  );
const incomesSeries = JSON.parse(
    document.getElementById("incomeSeries").textContent,
  );
const expensesSeries = JSON.parse(
    document.getElementById("expenseSeries").textContent,
  );
const categoryLabels = JSON.parse(
    document.getElementById("categoryLabels").textContent,
  );
const categoryTotals = JSON.parse(
    document.getElementById("categoryTotals").textContent,
  );
const categoryTypes = JSON.parse(
    document.getElementById("categoryTypes").textContent,
  );

  new Chart(document.getElementById("timelineChart"), {
    type: "line",
    data: {
      labels: dateLabels,
      datasets: [
        {
          label: "Receitas",
          data: incomesSeries,
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.18)",
          fill: true,
          tension: 0.3,
        },
        {
          label: "Despesas",
          data: expensesSeries,
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.18)",
          fill: true,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "top" },
        tooltip: { mode: "index", intersect: false },
      },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true },
      },
    },
  });

  const colors = categoryTypes.map((type) => type === "income" ? "#10b981" : "#ef4444");

  new Chart(document.getElementById("categoryChart"), {
    type: "doughnut",
    data: {
      labels: categoryLabels,
      datasets: [
        {
          data: categoryTotals,
          backgroundColor: colors,
          borderColor: "#ffffff",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
    },
  });