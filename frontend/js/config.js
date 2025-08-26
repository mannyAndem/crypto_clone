// ============================================
// CONFIGURATION - Update these URLs for your backend
// ============================================
export const API_CONFIG = {
    // Replace these with your actual backend endpoints
    CAMPAIGN_DETAIL: 'https://your-backend.com/api/campaign-detail',
    ESCROW_TRANSACTIONS: 'https://your-backend.com/api/escrow-transactions',
    ESCROW_BALANCE: 'https://your-backend.com/api/escrow-balance',
    DEXSCREENER_API: 'https://api.dexscreener.com/latest/dex/pairs/solana'
};

// ============================================
// MOCK DATA - Remove when connecting real backend
// ============================================
export const MOCK_DATA = {
    campaign: {
        "success": true,
        "campaign": {
            "id": "80b7d045-3cb6-4fb5-b871-f5f0e1d5244b",
            "name": "Karen",
            "symbol": "Karen",
            "contract_address": "5LKmh8SLt4FkbddUhLHWP1ufsvdcBAovkH1Gyaw5pump",
            "image_url": "https://dd.dexscreener.com/ds-data/tokens/solana/5LKmh8SLt4FkbddUhLHWP1ufsvdcBAovkH1Gyaw5pump.png",
            "wallet_address": "9o24Px7asSDJ1ZLyQhZd7vehm9kX4VuTeJh7VGryjXkm",
            "goal_amount": 115,
            "status": "active",
            "created_at": "2025-08-19T01:50:24.242682+00:00",
            "expires_at": "2025-08-19T17:50:22.982+00:00",
            "campaign_type": "DEX_10X_BOOST",
            "social_twitter": "https://x.com/i/communities/1957556044743201260",
            "social_website": "https://spongebob.fandom.com/wiki/Karen_Plankton",
            "description": null,
            "current_balance": 52.7632830374,
            "contributor_count": 5,
            "token_launchpad": "pumpswap",
            "token_source": "dexscreener",
            "liquidity": "11086.4",
            "market_cap": "9194",
            "price_usd": "0.000009195",
            "volume_24h": "226917.14"
        }
    },
    transactions: {
        "transactionCount": 4,
        "contributors": [
            "9AXqJW8tchVG3vKEFYzmNeA6Q5C93LDGwGegsF9HZso3",
            "5LJomLnyjdTVMoPD53K8CNGGBEs5F4uKvtkYXUqobd7",
            "DCqnywenZsFrMYxYiPNLq8fS6444VqG24XjMJ6ZcNgQp",
            "2NZZikek5mvW6UnScb2Ce5pBbA1h4khaBuhNfcru7mZg"
        ],
        "transactions": [
            {
                "signature": "4NdZVz9mG2YH51p6uTdQsVRdLA4J23uyATXNjMG235JnGV8UZyyUWnwUuC7hC16x2E4guez9C29yGzjW6pUUvJGh",
                "amount": 0.26982774,
                "from": "9AXqJW8tchVG3vKEFYzmNeA6Q5C93LDGwGegsF9HZso3",
                "timestamp": 1724035680
            },
            {
                "signature": "5JnGV8UZyyUWnwUuC7hC16x2E4guez9C29yGzjW6pUUvJGh4NdZVz9mG2YH51p6uTdQsVRdLA4J23uyATXNjMG235",
                "amount": 0.0068,
                "from": "5LJomLnyjdTVMoPD53K8CNGGBEs5F4uKvtkYXUqobd7",
                "timestamp": 1724034520
            },
            {
                "signature": "6pUUvJGh4NdZVz9mG2YH51p6uTdQsVRdLA4J23uyATXNjMG235JnGV8UZyyUWnwUuC7hC16x2E4guez9C29yGzjW",
                "amount": 0.0109,
                "from": "DCqnywenZsFrMYxYiPNLq8fS6444VqG24XjMJ6ZcNgQp",
                "timestamp": 1724033320
            },
            {
                "signature": "7hC16x2E4guez9C29yGzjW6pUUvJGh4NdZVz9mG2YH51p6uTdQsVRdLA4J23uyATXNjMG235JnGV8UZyyUWnwUuC",
                "amount": 0.0055,
                "from": "2NZZikek5mvW6UnScb2Ce5pBbA1h4khaBuhNfcru7mZg",
                "timestamp": 1724032680
            }
        ]
    },
    escrowBalance: {
        "success": true,
        "data": {
            "address": "9o24Px7asSDJ1ZLyQhZd7vehm9kX4VuTeJh7VGryjXkm",
            "balanceSOL": 0.293047948,
            "balanceUSD": 52.62555050184,
            "transactionCount": 5,
            "recentTransactions": [
                {
                    "signature": "617szgPyKfquqwSRdPUYUnUTMQgYGJMXqtgGvCFMxxsNSJ6f98si3N7nUEdN2YzCJLpDBA6kXW3kspkdyTHRPZzu",
                    "amount": 0,
                    "timestamp": 1724035560,
                    "status": "confirmed"
                }
            ]
        }
    }
};
