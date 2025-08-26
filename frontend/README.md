# DexVault Frontend Documentation

This document provides an overview of the DexVault frontend application, its purpose, technical stack, and current implementation status. It is intended for new frontend engineers joining the team to quickly get up to speed.

## 1. Project Overview

DexVault is a community-driven platform designed to crowdfund Dexscreener listings for Solana memecoins. The application allows users to view ongoing campaigns, contribute funds (SOL) to specific campaigns, and track the progress towards the listing goal.

**Key Features:**
*   **Campaign Display:** Shows details of individual memecoin campaigns, including token name, logo, contract address, official links (Twitter, Website), and funding progress.
*   **Real-time Funding Tracking:** Monitors campaign balances in real-time using on-chain Solana data and current SOL pricing.
*   **Contribution Mechanism:** Provides an escrow wallet address and QR code for users to send SOL contributions.
*   **Contribution History:** Displays a list of recent contributions to a campaign.
*   **Campaign Statistics:** Shows various stats like contributor count, top contributor, average contribution, and campaign duration.
*   **Refunds:** If a campaign fails to reach its funding goal, contributors can claim full refunds.
*   **Tips & Extra Contributions:** Funds contributed beyond the goal are treated as tips for platform maintenance.
*   **Responsive Design:** Optimized for various screen sizes (mobile-first approach).
*   **Dark/Light Mode:** User-selectable theme preference, saved to local storage.

## 2. Technologies Used

*   **HTML5:** Structure of the web pages.
*   **Tailwind CSS:** Utility-first CSS framework for styling.
*   **JavaScript (ES6+):** Core logic, DOM manipulation, API interactions, and real-time updates.
*   **Solana Blockchain:** For on-chain transactions and data.
*   **Pump.Fun:** Platform for memecoin creation and initial liquidity.

## 3. Frontend Structure

The frontend is a single-page application primarily driven by `index.html` and JavaScript modules.

```
frontend/
├── dexvault-new-logo.jpg  // Project logo
├── index.html             // Main HTML file
└── js/                    // JavaScript modules
    ├── api.js             // Handles API calls to the backend
    ├── config.js          // Configuration settings (e.g., API endpoints)
    ├── main.js            // Main application logic, routing, and initialization
    ├── render.js          // Functions responsible for rendering UI components
    ├── theme.js           // Dark/light mode toggle logic
    └── utils.js           // Utility functions (e.g., copy to clipboard, date formatting)
```

## 4. Getting Started

To run the frontend locally:

1.  **Save `index.html`:** Ensure `index.html` and the `js/` directory are in the `frontend/` folder.
2.  **Open in Browser:**
    *   Directly open `file:///path/to/frontend/index.html#/coin/YOUR_CONTRACT_ADDRESS` in your browser.
    *   Alternatively, serve with a simple HTTP server (e.g., `python -m http.server 8000` from the `frontend/` directory) and navigate to `http://localhost:8000/coin/YOUR_CONTRACT_ADDRESS`.

The application expects URLs in the format `/coin/{contractAddress}`. The `contractAddress` is extracted from the URL hash and used to fetch campaign data.

## 5. Key Integration Points

The frontend interacts with a backend API to fetch campaign details and escrow transactions.

*   **`js/config.js`:** Contains `API_CONFIG` URLs that need to be replaced with actual backend endpoints.
*   **`js/api.js`:** Contains functions like `fetchCampaignDetail` and `fetchEscrowTransactions` which currently use `MOCK_DATA`. These need to be updated to make real API calls.

## 6. Implementation Status / To Be Implemented

The current `index.html` includes a comprehensive set of instructions for further implementation. Here's a summary of what needs to be addressed:

*   **Backend Integration:**
    *   Replace `API_CONFIG` URLs in `js/config.js` with actual backend endpoints.
    *   Remove `MOCK_DATA` and mock implementations in `js/api.js`.
    *   Uncomment and implement real API calls in `fetchCampaignDetail`, `fetchEscrowTransactions`, and other relevant data fetching functions.
*   **Error Handling:** Add robust error handling for network failures and API response issues across the application.
*   **QR Code Generation:** Integrate a proper QR code library (e.g., `qrcode.js`) for dynamic QR code generation based on the escrow address. The current implementation uses a placeholder `div`.
*   **Campaign Creation:** The "Create Campaign" link (`/create-campaign`) is present in the header but its functionality is not yet implemented. This will require a new page/component and backend integration.
*   **Search Functionality:** The search bar is present but currently non-functional. Implementation will involve backend search API integration and UI updates to display search results.
*   **Mobile Menu:** The mobile menu toggle button is present, but the actual mobile navigation overlay/sidebar needs to be implemented.
*   **"How It Works" and "Team" Pages:** Links are present, but the content for these pages needs to be created.

## 7. Important Notes for Frontend Developers

*   **Code Structure:** The JavaScript is organized into modules (`js/` directory) for better maintainability.
*   **Styling:** Tailwind CSS is used for all styling. Familiarity with Tailwind is essential. Custom styles are defined in the `<style>` block within `index.html`.
*   **Routing:** Simple client-side routing is handled by `main.js` using URL hashes (e.g., `#/coin/{contractAddress}`).
*   **Polling:** Escrow balance updates every 10 seconds. Polling is paused when the tab is not visible to optimize performance.
*   **Solana Integration:** Understanding Solana wallet interactions and on-chain data fetching will be crucial for future enhancements.
*   **Error States:** Implement clear visual feedback for loading states, error messages, and empty data scenarios.
