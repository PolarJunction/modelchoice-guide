export function calculateSavings(monthlySpend) {
  const parsed = Number(monthlySpend);
  const monthly = Number.isFinite(parsed) ? Math.min(Math.max(parsed, 0), 100000) : 0;
  const monthlySaving = monthly * 0.05;
  return {
    monthly,
    monthlySaving,
    annualSaving: monthlySaving * 12,
    discountedTotal: monthly - monthlySaving,
  };
}

export function formatUsd(value) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

if (typeof document !== "undefined") {
  const input = document.querySelector("#monthly-spend");
  const monthlySaving = document.querySelector("#monthly-saving");
  const annualSaving = document.querySelector("#annual-saving");
  const discountedTotal = document.querySelector("#discounted-total");

  const update = () => {
    const result = calculateSavings(input.value);
    monthlySaving.textContent = formatUsd(result.monthlySaving);
    annualSaving.textContent = formatUsd(result.annualSaving);
    discountedTotal.textContent = formatUsd(result.discountedTotal);
  };

  input.addEventListener("input", update);
  update();
}
