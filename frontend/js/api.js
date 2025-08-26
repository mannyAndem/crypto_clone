import { API_CONFIG, MOCK_DATA } from './config.js';

// ============================================
// API FUNCTIONS (Mock implementations)
// ============================================
export async function fetchCampaignDetail(contractAddress) {
    // Mock API call - replace with real endpoint
    // const response = await fetch(`${API_CONFIG.CAMPAIGN_DETAIL}/${contractAddress}?sequence=1`);
    // return await response.json();

    // Return mock data for now
    return new Promise(resolve => {
        setTimeout(() => resolve(MOCK_DATA.campaign), 500);
    });
}

export async function fetchEscrowTransactions(escrowPublicKey) {
    // Mock API call - replace with real endpoint
    // const response = await fetch(`${API_CONFIG.ESCROW_TRANSACTIONS}/${escrowPublicKey}`);
    // return await response.json();

    return new Promise(resolve => {
        setTimeout(() => resolve(MOCK_DATA.transactions), 300);
    });
}

export async function fetchEscrowBalance(escrowPublicKey, currentSOLPrice) {
    // Mock API call - replace with real endpoint
    // const response = await fetch(`${API_CONFIG.ESCROW_BALANCE}?wallet=${escrowPublicKey}`);
    // return await response.json();

    return new Promise(resolve => {
        // Simulate slight variations in balance for live effect
        const mockBalance = { ...MOCK_DATA.escrowBalance };
        mockBalance.data.balanceSOL += (Math.random() - 0.5) * 0.001;
        mockBalance.data.balanceUSD = mockBalance.data.balanceSOL * currentSOLPrice;
        setTimeout(() => resolve(mockBalance), 200);
    });
}

export async function fetchPairData(tokenAddress) {
    // Mock API call - replace with real endpoint
    // const response = await fetch(`${API_CONFIG.DEXSCREENER_API}/${tokenAddress}`);
    // return await response.json();

    return new Promise(resolve => {
        setTimeout(() => resolve({ pairs: [] }), 400);
    });
}
