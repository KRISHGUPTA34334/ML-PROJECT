let leads = [];

document.querySelectorAll(".company-name a").forEach(el => {
  leads.push({
    company: el.textContent.trim(),
    website: el.href
  });
});

chrome.storage.local.set({ leads });
