import { API_CONFIG, MOCK_DATA } from "./config.js";

// ============================================
// API FUNCTIONS (Mock implementations)
// ============================================
export async function fetchCampaignDetail(contractAddress) {
  // Mock API call - replace with real endpoint
  try {
    const response = await fetch(
      `${API_CONFIG.CAMPAIGN_DETAIL}/${contractAddress}`,
      { headers: { "ngrok-skip-browser-warning": 69420 } }
    );
    console.log(response);
    let data = await response.json();
    console.log(data);
    return data;
  } catch (error) {
    console.error(error);
  }

  //   if (response?.ok) {
  //     const data = await response.json();
  //     console.log(data);
  //     return data;
  //   } else {
  //     console.error("Error: failed to fetch campaign detail");
  //     return null;
  //   }

  // Return mock data for now
  // return new Promise(resolve => {
  //     setTimeout(() => resolve(MOCK_DATA.campaign), 500);
  // });
}
export async function createCampaign(campaign) {
  // Mock API call - replace with real endpoint
  try {
    const response = await fetch(API_CONFIG.CAMPAIGNS, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(campaign),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    console.log("Campaign created successfully!");
    return await response.json(); // parse JSON response
  } catch (error) {
    console.error("Error:", error);
  }

  // Return mock data for now
  // return new Promise(resolve => {
  //     setTimeout(() => resolve(MOCK_DATA.campaign), 500);
  // });
}

export async function fetchEscrowTransactions(escrowPublicKey) {
  // Mock API call - replace with real endpoint
  // const response = await fetch(`${API_CONFIG.ESCROW_TRANSACTIONS}/${escrowPublicKey}`);
  // return await response.json();

  try {
    const response = await fetch(
      `${API_CONFIG.ESCROW_TRANSACTIONS}/${escrowPublicKey}`,
      { headers: { "ngrok-skip-browser-warning": 69420 } }
    );
    console.log(response);
    let data = await response.json();
    console.log(data);
    return data;
  } catch (error) {
    console.error(error);
  }

  // return new Promise((resolve) => {
  //   setTimeout(() => resolve(MOCK_DATA.transactions), 300);
  // });
}

export async function fetchEscrowBalance(escrowPublicKey, currentSOLPrice) {
  // Mock API call - replace with real endpoint
  // const response = await fetch(`${API_CONFIG.ESCROW_BALANCE}?wallet=${escrowPublicKey}`);
  // return await response.json();
  try {
    const response = await fetch(
      `${API_CONFIG.ESCROW_BALANCE}/${escrowPublicKey}`,
      { headers: { "ngrok-skip-browser-warning": 69420 } }
    );
    let data = await response.json();
    console.log("escrow balance;", data);
    return data;
  } catch (error) {
    console.error(error);
  }

  return new Promise((resolve) => {
    // Simulate slight variations in balance for live effect
    const mockBalance = { ...MOCK_DATA.escrowBalance };
    mockBalance.data.balanceSOL += (Math.random() - 0.5) * 0.001;
    mockBalance.data.balanceUSD = mockBalance.data.balanceSOL * currentSOLPrice;
    setTimeout(() => resolve(mockBalance), 200);
  });
}

export async function fetchCampaignQr(campaignId) {
  try {
    const response = await fetch(
      `${API_CONFIG.BASE}/campaigns/${campaignId}/qr`,
      {
        headers: { "ngrok-skip-browser-warning": 69420 },
      }
    );
    let data = await response.json();
    console.log(data);
    return data;
  } catch (error) {
    console.error(error);
  }

  return new Promise((resolve) => {
    // Simulate slight variations in balance for live effect
    const mockBalance = { ...MOCK_DATA.escrowBalance };
    mockBalance.data.balanceSOL += (Math.random() - 0.5) * 0.001;
    mockBalance.data.balanceUSD = mockBalance.data.balanceSOL * currentSOLPrice;
    setTimeout(() => resolve(mockBalance), 200);
  });
}
export async function fetchSolPrice() {
  try {
    const response = await fetch(
      `https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd`
    );
    let data = await response.json();
    console.log(data);
    return data.solana.usd;
  } catch (error) {
    console.error(error);
  }
}

export async function fetchPairData(tokenAddress) {
  // Mock API call - replace with real endpoint
  // const response = await fetch(`${API_CONFIG.DEXSCREENER_API}/${tokenAddress}`);
  // return await response.json();

  return new Promise((resolve) => {
    setTimeout(() => resolve({ pairs: [] }), 400);
  });
}
