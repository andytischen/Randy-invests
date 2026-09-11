(() => {
  const form = document.getElementById("fit-form");
  if (form) {
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
      const headerCells = [...document.querySelectorAll(".compare-table thead th")];
      const slugByIndex = headerCells.map((th) => {
        const metal = [...th.classList].find((cls) => cls.startsWith("metal-"));
        return metal ? metal.replace("metal-", "") : null;
      });
      headerCells.forEach((th, index) => {
        th.classList.toggle("is-highlighted", slug !== null && slugByIndex[index] === slug);
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
      if (amount === null) return;
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
  }

  document.querySelectorAll("[data-copy]").forEach((node) => {
    node.addEventListener("click", async () => {
      const text = node.textContent.trim();
      try {
        await navigator.clipboard.writeText(text);
        node.dataset.copied = "true";
      } catch {
        /* clipboard may be unavailable; the URL is still visible */
      }
    });
  });
})();
