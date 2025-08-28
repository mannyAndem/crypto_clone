import {
  truncateAddress,
  formatTimestamp,
  formatDateTime,
  calculateTimeLeft,
  copyToClipboard,
} from "./utils.js";

// ============================================
// RENDERING FUNCTIONS
// ============================================
export function renderCampaignHeader(campaign) {
  document.getElementById("tokenName").textContent = campaign.name;
  document.getElementById("tokenImage").src = campaign.image_url;
  document.getElementById("tokenImage").alt = `${campaign.name} Logo`;

  // Update time left
  const timeLeft = calculateTimeLeft(campaign.expires_at);
  document.getElementById("timeLeft").textContent = timeLeft;

  // Update social links
  document.getElementById("twitterLink").href = campaign.social_twitter || "#";
  document.getElementById("websiteLink").href = campaign.social_website || "#";

  // Update contract address
  document.getElementById("contractAddress").textContent =
    campaign.contract_address;

  // Update Pump.Fun link
  document.getElementById(
    "pumpFunLink"
  ).href = `https://pump.fun/coin/${campaign.contract_address}`;
}

export function renderProgress(campaign, currentSOLPrice) {
  const goalAmount = campaign.goal_amount;
  const currentAmount = campaign.current_balance;
  const neededAmount = Math.max(0, goalAmount - currentAmount);
  const percentFunded = Math.min(100, (currentAmount / goalAmount) * 100);

  console.log("campaign inside escrow", campaign);
  document.getElementById("campaign_type").textContent = campaign.campaign_type;

  // Update progress text
  document.getElementById("progressText").textContent = `${Math.round(
    currentAmount
  )} / ${goalAmount}`;
  document.getElementById("neededAmount").textContent = `${Math.round(
    neededAmount
  )} needed`;
  document.getElementById(
    "livePrice"
  ).textContent = `Live: ${currentSOLPrice}/SOL`;
  document.getElementById("solAmount").textContent = `${(
    currentAmount / currentSOLPrice
  ).toFixed(4)} SOL`;
  document.getElementById("percentFunded").textContent = `${Math.round(
    percentFunded
  )}% funded`;

  // Update progress bar
  document.getElementById("progressBar").style.width = `${percentFunded}%`;

  // Update last updated time
  const now = new Date();
  const timeString = now.toTimeString().substring(0, 8);
  document.getElementById("lastUpdated").textContent = timeString;
}

export function renderContributions(transactions) {
  const container = document.getElementById("contributionsList");
  container.innerHTML = "";

  transactions.transactions.forEach((tx) => {
    const contributionElement = document.createElement("div");
    contributionElement.className =
      "bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4";

    contributionElement.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                    <span class="text-gray-700 dark:text-gray-300 font-mono text-sm">${truncateAddress(
                      tx.from
                    )}</span>
                    <button onclick="copyToClipboard(this)" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300">
                        <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                    </button>
                </div>
                <div class="text-right">
                    <div class="text-gray-900 dark:text-white font-semibold">${tx.amount.toFixed(
                      4
                    )} SOL</div>
                    <div class="text-gray-500 dark:text-gray-400 text-xs">${formatTimestamp(
                      tx.timestamp
                    )}</div>
                </div>
            </div>
            <div class="flex space-x-2">
                <a href="https://solscan.io/tx/${
                  tx.signature
                }" target="_blank" class="inline-flex items-center px-2 py-1 text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors">
                    <svg class="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                    Transaction
                </a>
                <a href="https://solscan.io/account/${
                  tx.from
                }" target="_blank" class="inline-flex items-center px-2 py-1 text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors">
                    <svg class="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                    Wallet
                </a>
            </div>
        `;

    container.appendChild(contributionElement);
  });
}

export function renderCampaignStats(campaign, transactions, currentSOLPrice) {
  document.getElementById("contributorCount").textContent =
    campaign.contributor_count;
  document.getElementById("contributionCount").textContent =
    transactions.transactionCount;

  // Calculate top contributor and contribution
  let topContribution = 0;
  let topContributor = "";
  transactions.transactions.forEach((tx) => {
    if (tx.amount > topContribution) {
      topContribution = tx.amount;
      topContributor = tx.from;
    }
  });

  document.getElementById("topContributor").textContent = truncateAddress(
    topContributor,
    5,
    6
  );
  document.getElementById(
    "topContribution"
  ).textContent = `${topContribution.toFixed(2)} SOL`;

  // Calculate average contribution
  const totalAmount = transactions.transactions.reduce(
    (sum, tx) => sum + tx.amount,
    0
  );
  const avgContribution =
    transactions.transactionCount > 0
      ? totalAmount / transactions.transactionCount
      : 0;
  document.getElementById("avgContribution").textContent = (
    avgContribution * currentSOLPrice
  ).toFixed(2);

  // Format dates
  document.getElementById("campaignCreated").textContent = formatDateTime(
    campaign.created_at
  );
  document.getElementById("expiresAt").textContent = formatDateTime(
    campaign.expires_at
  );

  // Calculate funding speed
  const now = new Date();
  const created = new Date(campaign.created_at);
  const hoursElapsed = Math.max(1, (now - created) / (1000 * 60 * 60));
  const fundingPerHour = campaign.current_balance / hoursElapsed;
  const txPerHour = transactions.transactionCount / hoursElapsed;

  document.getElementById("fundingSpeed").textContent = `${Math.round(
    fundingPerHour
  )}/h (${txPerHour.toFixed(1)} tx/h)`;
}

export function renderEscrowWallet(campaign, qr) {
  const escrowAddress = campaign.wallet_address;
  document.getElementById("escrowAddress").textContent = escrowAddress;

  // Generate QR code (simplified representation)
  generateQRCode(qr);
}

function generateQRCode(qr) {
  // Simplified QR code generation - in production, use a QR code library
  const qrContainer = document.getElementById("qrCode");
  qrContainer.innerHTML = `
        <div class="w-32 h-32 bg-white flex items-center justify-center relative">
            <img src="${qr.qr_code}"
        </div>
    `;
  //   qrContainer.innerHTML = `
  //         <div class="w-32 h-32 bg-white flex items-center justify-center relative">
  //             <div class="absolute inset-2 bg-black opacity-90"></div>
  //             <div class="absolute inset-4 bg-white"></div>
  //             <div class="absolute inset-6 bg-black opacity-80"></div>
  //             <div class="absolute inset-8 bg-white"></div>
  //             <div class="relative z-10 text-black text-xs font-mono text-center px-1">
  //                 ...
  //             </div>
  //         </div>
  //     `;
}
