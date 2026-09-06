(() => {
  const form = document.getElementById("fit-form");
  if (!form) return;

  const input = form.querySelector("#amount");
  const status = document.getElementById("fit-status");
  const cards = [...document.querySelectorAll(".tier-card[data-minimum]")];

  const parseAmount = (raw) => {
    const cleaned = String(raw || "").replace(/[$,\s]/g, "");
    if (!cleaned) return null;
    const value = Number(cleaned);
    return Number.isFinite(value) ? value : null;
  };

  const pickTier = (amount) => {
    const eligible = cards.filter((card) => amount >= Number(card.dataset.minimum));
    if (!eligible.length) return cards[0] || null;
    return eligible[eligible.length - 1];
  };

  const paint = (slug) => {
    cards.forEach((card) => {
      card.classList.toggle("is-highlighted", slug !== null && card.dataset.tier === slug);
    });
    document.querySelectorAll(".compare-table th, .compare-table td").forEach((cell) => {
      if (cell.classList.contains("metal-bronze") || cell.classList.contains("metal-silver")
        || cell.classList.contains("metal-gold") || cell.classList.contains("metal-platinum")) {
        const metal = [...cell.classList].find((cls) => cls.startsWith("metal-"));
        const map = { "metal-bronze": "bronze", "metal-silver": "silver", "metal-gold": "gold", "metal-platinum": "platinum" };
        cell.classList.toggle("is-highlighted", slug !== null && map[metal] === slug);
      }
    });
    // Body cells: highlight by column index
    const headerCells = [...document.querySelectorAll(".compare-table thead th")];
    const slugByIndex = headerCells.map((th) => {
      const metal = [...th.classList].find((cls) => cls.startsWith("metal-"));
      return metal ? metal.replace("metal-", "") : null;
    });
    document.querySelectorAll(".compare-table tbody tr").forEach((row) => {
      [...row.children].forEach((cell, index) => {
        if (index === 0) return;
        cell.classList.toggle("is-highlighted", slug !== null && slugByIndex[index] === slug);
      });
    });
  };

  const update = () => {
    const amount = parseAmount(input.value);
    if (amount === null) {
      if (status && !status.dataset.server) {
        status.textContent = "Enter an amount to highlight the highest tier whose minimum you meet.";
      }
      return;
    }
    const card = pickTier(amount);
    if (!card) return;
    paint(card.dataset.tier);
    const formatted = amount.toLocaleString("en-US", { maximumFractionDigits: 0 });
    const minimum = Number(card.dataset.minimum).toLocaleString("en-US");
    if (status) {
      status.innerHTML = `A $${formatted} commitment illustratively maps to <strong>${card.querySelector(".tier-metal").textContent}</strong> (minimum $${minimum}). This is not advice.`;
    }
  };

  input.addEventListener("input", update);
  form.addEventListener("submit", () => {
    // Allow the GET request so the URL stays shareable.
  });
})();
