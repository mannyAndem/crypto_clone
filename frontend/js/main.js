import { getContractAddressFromURL, updateCurrentTime } from "./utils.js";
import {
  fetchCampaignDetail,
  fetchEscrowTransactions,
  fetchEscrowBalance,
  fetchCampaignQr,
} from "./api.js";
import {
  renderCampaignHeader,
  renderProgress,
  renderContributions,
  renderCampaignStats,
  renderEscrowWallet,
} from "./render.js";
import { initTheme, toggleTheme } from "./theme.js";
import { MOCK_DATA } from "./config.js";

// ============================================
// GLOBAL STATE
// ============================================
let currentCampaign = MOCK_DATA.campaign.campaign;
let currentContractAddress = "KTtNxsFzGJBUDCLT5c6k3zKtRacQ2LLzivZ3CdCbonk";
let currentWalletAddress = "FuXL5ZYZc6YBGkRxWQ98k1f64QSGWXtLwNN2Dj5f3XYf";
// let currentContractAddress = MOCK_DATA.campaign.campaign.contract_address;
let currentSOLPrice = 180; // Mock SOL price
let pollingInterval = null;

// ============================================
// MAIN FUNCTIONS
// ============================================
async function loadCampaignData() {
  try {
    const contractAddress = currentContractAddress;
    if (!contractAddress) {
      throw new Error("No contract address found in URL");
    }

    currentContractAddress = contractAddress;

    // Fetch campaign details
    const campaignData = await fetchCampaignDetail(contractAddress);
    // const campaignData = MOCK_DATA.campaign; // Replace with fetchCampaignDetail(contractAddress) when backend is ready
    console.log("Loaded campaign data:", campaignData);
    if (!campaignData.success) {
      throw new Error("Failed to load campaign data");
    }

    const qr = await fetchCampaignQr(campaignData.campaign_id);
    currentCampaign = campaignData;
    // Fetch transactions

    // const transactionsData = MOCK_DATA.transactions;
    const transactionsData = await fetchEscrowTransactions(
      currentWalletAddress
    );

    // Render all components
    renderCampaignHeader(campaignData.campaign);
    renderProgress(campaignData.campaign, currentSOLPrice);
    renderContributions(transactionsData);
    renderCampaignStats(
      campaignData.campaign,
      transactionsData,
      currentSOLPrice
    );
    renderEscrowWallet(campaignData.campaign, qr);

    // Show main content, hide loading
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("mainContent").classList.remove("hidden");

    // Start polling for balance updates
    startPolling();
  } catch (error) {
    console.error("Error loading campaign data:", error);
    document.getElementById("loadingState").innerHTML = `
            <div class="text-center">
                <div class="text-red-600 dark:text-red-400 text-lg mb-4">Error loading campaign</div>
                <p class="text-gray-600 dark:text-gray-400">${error.message}</p>
                <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                    Retry
                </button>
            </div>
        `;
  }
}

async function updateEscrowBalance() {
  if (!currentCampaign) return;

  try {
    // const balanceData = await fetchEscrowBalance(currentWalletAddress);
    const balanceData = currentCampaign.campaign.current_balance;
    if (balanceData.success) {
      // Update current balance in campaign object
      // currentCampaign.current_balance = balanceData.data.balanceUSD;

      // Re-render progress
      renderProgress(currentCampaign.campaign, currentSOLPrice);
    }
  } catch (error) {
    console.error("Error updating escrow balance:", error);
  }
}

function startPolling() {
  // Poll escrow balance every 10 seconds
  pollingInterval = setInterval(updateEscrowBalance, 10000000000000); //Fix later
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}

async function refreshContributions() {
  if (!currentCampaign) return;

  try {
    const transactionsData = await fetchEscrowTransactions(
      currentWalletAddress
    );
    console.log(transactionsData);
    renderContributions(transactionsData);
    renderCampaignStats(currentCampaign, transactionsData, currentSOLPrice);
  } catch (error) {
    console.error("Error refreshing contributions:", error);
  }
}

// ============================================
// INITIALIZATION
// ============================================
function init() {
  // Initialize theme
  initTheme();

  // Update current time immediately and then every second
  updateCurrentTime();
  setInterval(updateCurrentTime, 1000);

  // Load campaign data
  loadCampaignData();
}

// ============================================
// EVENT LISTENERS
// ============================================
document.addEventListener("DOMContentLoaded", init);

// Theme toggle event listeners
document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("themeToggle");
  const mobileThemeToggle = document.getElementById("mobileThemeToggle");

  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }

  if (mobileThemeToggle) {
    mobileThemeToggle.addEventListener("click", toggleTheme);
  }
});

// Clean up polling when page is unloaded
window.addEventListener("beforeunload", stopPolling);

// Handle visibility change to pause/resume polling
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    stopPolling();
  } else if (currentCampaign) {
    startPolling();
  }
});

// Expose functions to global scope for onclick attributes in HTML
window.copyToClipboard = (elementId) => {
  const element = document.getElementById(elementId);
  const text = element.textContent || element.value;
  navigator.clipboard.writeText(text).then(() => {
    const originalText = element.textContent;
    element.textContent = "Copied!";
    setTimeout(() => {
      element.textContent = originalText;
    }, 1000);
  });
};
window.openExplorer = () => {
  const escrowAddress = document.getElementById("escrowAddress").textContent;
  window.open(`https://solscan.io/account/${escrowAddress}`, "_blank");
};
window.refreshContributions = refreshContributions;
