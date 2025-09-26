(function () {
  const CONFIG = window.APP_CONFIG || {};
  const form = document.getElementById("spam-form");
  const emailTextArea = document.getElementById("email-text");
  const resultDiv = document.getElementById("result");
  const statusLabel = document.getElementById("status-label");
  const thresholdHint = document.getElementById("threshold-hint");
  const submitBtn = document.getElementById("submit-btn");
  const spinner = document.getElementById("loading-spinner");
  const clearBtn = document.getElementById("clear-btn");

  const SPAM_KEYWORDS = new Set([
    "free",
    "win",
    "winner",
    "lottery",
    "prize",
    "credit",
    "loan",
    "urgent",
    "verify",
    "income",
    "investment",
    "bitcoin",
    "cash",
    "offer",
    "discount",
    "click",
    "limited",
    "guaranteed",
    "money",
    "bonus",
    "reward",
    "secret",
    "deal",
    "sale",
    "promo",
    "gift",
    "trial",
    "subscription",
  ]);

  const HAM_KEYWORDS = new Set([
    "team",
    "meeting",
    "review",
    "report",
    "reminder",
    "doctor",
    "appointment",
    "thanks",
    "thank",
    "appreciate",
    "invoice",
    "schedule",
    "project",
    "update",
    "attached",
    "attachment",
    "quarterly",
    "minutes",
    "agenda",
    "customer",
    "support",
    "order",
    "purchase",
    "ship",
    "shipping",
    "delivery",
    "family",
    "tomorrow",
    "today",
    "note",
    "kind",
    "regards",
    "please",
    "manager",
    "follow",
    "confirm",
    "team",
    "summary",
    "budget",
    "meeting",
    "client",
    "review",
  ]);

  const BASE_THRESHOLD = CONFIG.spamThreshold ?? 0.7;
  const OFFLINE_BOOST = CONFIG.offlineBoost || {
    spamHit: 0.07,
    hamHit: 0.1,
    maxSpamBoost: 0.28,
    maxHamReduction: 0.5,
  };

  const tokenize = (text) => text.toLowerCase().match(/[a-z0-9']+/g) || [];

  const classifyOffline = (text) => {
    const tokens = tokenize(text);
    const uniqueTokens = new Set(tokens);

    let spamHits = 0;
    let hamHits = 0;

    uniqueTokens.forEach((token) => {
      if (SPAM_KEYWORDS.has(token)) spamHits += 1;
      if (HAM_KEYWORDS.has(token)) hamHits += 1;
    });

    const rawProbability =
      0.55 + spamHits * OFFLINE_BOOST.spamHit - hamHits * OFFLINE_BOOST.hamHit;
    const adjustedSpamBoost = Math.min(
      OFFLINE_BOOST.maxSpamBoost,
      spamHits * OFFLINE_BOOST.spamHit
    );
    const adjustedHamReduction = Math.min(
      OFFLINE_BOOST.maxHamReduction,
      hamHits * OFFLINE_BOOST.hamHit
    );

    let probability = rawProbability + adjustedSpamBoost - adjustedHamReduction;
    probability = Math.max(0, Math.min(1, probability));

    return {
      success: true,
      probability,
      raw_probability: Math.max(0, Math.min(1, rawProbability)),
      probability_adjustment: probability - rawProbability,
      spam_keyword_hits: spamHits,
      ham_keyword_hits: hamHits,
      threshold: BASE_THRESHOLD,
      is_spam: probability >= BASE_THRESHOLD,
      message:
        probability >= BASE_THRESHOLD
          ? "🚨 Spam detected!"
          : "✅ This email looks legitimate.",
      offline: true,
    };
  };

  const classify = async (text) => {
    const trimmed = text.trim();
    if (!trimmed) {
      throw new Error("Email text is required.");
    }

    if (CONFIG.apiBaseUrl) {
      const apiUrl = CONFIG.apiBaseUrl.replace(/\/$/, "") + "/predict";
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_text: trimmed }),
      });

      const rawText = await response.text();
      let data = null;

      if (rawText) {
        try {
          data = JSON.parse(rawText);
        } catch (err) {
          console.warn(
            "Failed to parse JSON, falling back to offline classifier.",
            err
          );
        }
      }

      if (data && response.ok && data.success) {
        return data;
      }

      console.warn(
        "Remote API unavailable, using offline heuristic classifier."
      );
    }

    return classifyOffline(trimmed);
  };

  const setLoading = (isLoading) => {
    submitBtn.disabled = isLoading;
    spinner.classList.toggle("d-none", !isLoading);
    statusLabel.textContent = isLoading ? "Analysing…" : "Ready";
  };

  const displayResult = (payload, isError = false) => {
    const {
      message,
      probability,
      is_spam,
      threshold,
      offline,
      probability_adjustment,
      spam_keyword_hits,
      ham_keyword_hits,
    } = payload;
    const probabilityText =
      typeof probability === "number"
        ? `<div class="mt-2 small text-muted">Confidence of spam: ${(
            probability * 100
          ).toFixed(1)}%</div>`
        : "";
    const thresholdText =
      typeof threshold === "number"
        ? `<div class="mt-1 small text-muted">Spam threshold: ${(
            threshold * 100
          ).toFixed(0)}%</div>`
        : "";
    const adjustmentText =
      typeof probability_adjustment === "number"
        ? `<div class="mt-1 small text-muted">Adjustment applied: ${(
            probability_adjustment * 100
          ).toFixed(1)} pts</div>`
        : "";
    const keywordText = offline
      ? `<div class="mt-1 small text-muted">Keyword hits → Spam: ${
          spam_keyword_hits ?? 0
        }, Legitimate: ${ham_keyword_hits ?? 0}</div>`
      : "";

    resultDiv.innerHTML = `${
      message || "Unexpected response."
    }${probabilityText}${thresholdText}${adjustmentText}${keywordText}`;
    resultDiv.className = `result show ${
      isError ? "spam" : is_spam ? "spam" : "not-spam"
    }`;
  };

  thresholdHint.textContent = `Flags spam when confidence ≥ ${(
    BASE_THRESHOLD * 100
  ).toFixed(0)}%`;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    form.classList.add("was-validated");
    if (!form.checkValidity()) {
      return;
    }

    setLoading(true);
    resultDiv.className = "result";
    resultDiv.textContent = "";

    try {
      const data = await classify(emailTextArea.value);
      displayResult(data);
    } catch (error) {
      displayResult(
        {
          message: `Error: ${error.message}`,
          is_spam: true,
        },
        true
      );
    } finally {
      setLoading(false);
    }
  });

  clearBtn.addEventListener("click", () => {
    emailTextArea.value = "";
    resultDiv.className = "result";
    resultDiv.textContent = "";
    form.classList.remove("was-validated");
    statusLabel.textContent = "Ready";
  });
})();
