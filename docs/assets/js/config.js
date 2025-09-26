window.APP_CONFIG = Object.assign(
  {
    apiBaseUrl: null,
    spamThreshold: 0.7,
    offlineBoost: {
      spamHit: 0.07,
      hamHit: 0.1,
      maxSpamBoost: 0.28,
      maxHamReduction: 0.5,
    },
  },
  window.APP_CONFIG || {}
);
