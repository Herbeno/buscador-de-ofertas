(function () {
  const form = document.getElementById("form");
  const input = document.getElementById("q");
  const btn = document.getElementById("btn");
  const err = document.getElementById("err");
  const hint = document.getElementById("hint");
  const stats = document.getElementById("stats");
  const statsLine = document.getElementById("statsLine");
  const results = document.getElementById("results");
  const dealsEl = document.getElementById("deals");
  const othersEl = document.getElementById("others");

  const money = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });

  function showErr(msg) {
    err.textContent = msg;
    err.hidden = false;
  }

  function clearErr() {
    err.hidden = true;
    err.textContent = "";
  }

  function setLoading(loading) {
    btn.disabled = loading;
    hint.hidden = !loading;
    if (loading) {
      hint.textContent = "Isso pode levar alguns segundos enquanto a página do Mercado Livre carrega.";
    }
  }

  function clearResults() {
    dealsEl.innerHTML = "";
    othersEl.innerHTML = "";
    stats.hidden = true;
    results.hidden = true;
  }

  function appendItems(ul, items, emptyText) {
    if (!items.length) {
      const p = document.createElement("p");
      p.className = "empty-msg";
      p.textContent = emptyText;
      ul.appendChild(p);
      return;
    }
    for (const row of items) {
      const li = document.createElement("li");
      const wrap = document.createElement("div");
      wrap.className = "item-row";

      const link = document.createElement("a");
      link.className = "item-title";
      link.href = row.link || "#";
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = row.titulo || "(sem título)";

      const price = document.createElement("span");
      price.className = "item-price";
      const n = Number(row.preco);
      price.textContent = Number.isFinite(n) ? money.format(n) : "—";

      wrap.appendChild(link);
      wrap.appendChild(price);
      li.appendChild(wrap);
      ul.appendChild(li);
    }
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    clearErr();
    clearResults();

    const q = input.value.trim();
    if (!q) return;

    setLoading(true);
    try {
      const url = "/search?item=" + encodeURIComponent(q);
      const res = await fetch(url);
      const data = await res.json();

      if (!res.ok) {
        showErr("Não foi possível completar a busca. Tente de novo.");
        return;
      }

      if (data.error) {
        showErr(data.error);
        return;
      }

      const st = data.stats || {};
      const total = st.total_found ?? "—";
      const valid = st.valid_items ?? "—";
      const med = st.median_price;
      const medStr =
        typeof med === "number" && Number.isFinite(med) ? money.format(med) : "—";

      statsLine.textContent =
        String(total) +
        " anúncios coletados · " +
        String(valid) +
        " depois do filtro · mediana " +
        medStr;
      stats.hidden = false;

      const dealRows = data.deals || [];
      const otherRows = data.others || [];

      appendItems(dealsEl, dealRows, "Nenhum item nesta faixa.");
      appendItems(othersEl, otherRows, "Nenhum outro item listado.");

      results.hidden = false;
    } catch {
      showErr("Falha de rede ou resposta inválida. Verifique se a API está rodando.");
    } finally {
      setLoading(false);
    }
  });
})();
