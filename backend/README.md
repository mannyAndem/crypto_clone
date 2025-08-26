# **Crypto Clone Backend API: Solana Campaign Management**

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-5.5.3-green.svg)](https://docs.celeryq.dev/en/stable/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-6.0-dc382d.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-20.10-0db7ed.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
This repository provides the robust backend API for a cryptocurrency crowdfunding platform, meticulously engineered to interface with the Solana blockchain. It manages campaign lifecycles, delivers real-time data, and ensures persistent data storage, all built on FastAPI for high performance and scalability.

## Features
*   **Solana Blockchain Integration**: Connects to the Solana network for fetching transaction data, monitoring wallet balances, and retrieving token information seamlessly.
*   **Campaign Management**: Offers comprehensive API endpoints for creating, retrieving, and managing cryptocurrency campaigns, including dynamic QR code generation for payments.
*   **Real-time Capabilities**: Utilizes WebSockets for instant data updates, transaction monitoring, and broadcasting key events to connected clients.
*   **RESTful API**: Engineered with FastAPI to provide efficient and well-defined API endpoints, featuring automatic interactive documentation for developer convenience.
*   **Asynchronous Task Processing**: Leverages Celery with Redis as a message broker for handling background tasks, such as periodic price updates and continuous transaction monitoring, ensuring the primary application remains responsive.
*   **PostgreSQL Database**: Employs SQLAlchemy with `asyncpg` for asynchronous interaction with a PostgreSQL database, storing critical campaign, token cache, and transaction data reliably.
*   **Containerized Deployment**: Includes Docker support for simplified setup and consistent deployment across diverse development and production environments.

## Getting Started
To get this project up and running locally, follow the steps below.

### Installation
⚙️ **Prerequisites**:
Before you begin, ensure you have the following installed:
*   [Docker](https://docs.docker.com/get-docker/) (recommended for containerized setup)
*   [Python 3.11](https://www.python.org/downloads/)
*   [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer)

1.  ⬇️ **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/crypto_clone.git
    cd crypto_clone/backend # Adjust if your main directory is different
    ```

### Environment Variables
Create a `.env` file in the project's root directory and populate it with the following required variables.

*   `DATABASE_URL`: Connection string for your PostgreSQL database.
    *   Example: `postgresql+asyncpg://user:password@host:port/database_name`
*   `SOLANA_RPC_URL`: The URL for the Solana RPC endpoint.
    *   Example: `https://api.mainnet-beta.solana.com`
*   `WALLET`: A Solana wallet address used by the backend for specific operations (e.g., as a default escrow).
    *   Example: `9o24Px7asSDJ1ZLyQhZd7vehm9kX4VuTeJh7VGryjXkm`
*   `REDIS_URL`: The URL for your Redis instance, used by Celery as a broker and result backend.
    *   Example: `redis://localhost:6379/0`

### Local Setup (without Docker)
If you prefer to run the application directly on your machine:

1.  📦 **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  🚀 **Start the FastAPI Application**:
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ```
3.  🔄 **Start Celery Worker (in a separate terminal)**:
    ```bash
    celery -A src.services worker --loglevel=info -P solo
    ```
    *Note: `-P solo` is for development. For production, consider `gevent` or `eventlet`.*
4.  ⏰ **Start Celery Beat for Scheduled Tasks (in another separate terminal)**:
    ```bash
    celery -A src.services beat --loglevel=info
    ```

### Dockerized Setup (Recommended)
For a containerized setup using Docker:

1.  🐳 **Build the Docker Image**:
    ```bash
    docker build -t crypto-clone-backend .
    ```
2.  ▶️ **Run the Docker Container**:
    Link to your PostgreSQL and Redis containers or external services. A `docker-compose.yml` file is highly recommended for a full setup.
    ```bash
    docker run -p 8000:8000 --env-file ./.env crypto-clone-backend
    ```

## Usage
Once the server is running, you can interact with the API via `http://localhost:8000`.

### Basic API Interaction
You can use `curl` or a tool like Postman/Insomnia to test the endpoints.

**Health Check**:
```bash
curl http://localhost:8000/api/health
```

**Create a Campaign**:
```bash
curl -X POST \
  http://localhost:8000/api/campaigns \
  -H 'Content-Type: application/json' \
  -d '{
    "contract_address": "5LKmh8SLt4FkbddUhLHWP1ufsvdcBAovkH1Gyaw5pump",
    "goal_amount": 100.00,
    "expires_at": "2025-12-31T23:59:59Z",
    "description": "Support the Karen meme coin!",
    "social_twitter": "https://x.com/karen_token",
    "social_website": "https://karen.meme"
  }'
```

**Get Campaign Details**:
```bash
curl http://localhost:8000/api/campaign-detail/5LKmh8SLt4FkbddUhLHWP1ufsvdcBAovkH1Gyaw5pump
```

**Get Escrow Balance**:
```bash
curl "http://localhost:8000/api/escrow-balance?wallet=9o24Px7asSDJ1ZLyQhZd7vehm9kX4VuTeJh7VGryjXkm"
```

### WebSocket Connection
To connect to the real-time WebSocket server for updates:

```javascript
// Example using JavaScript in a browser or Node.js
const socket = new WebSocket('ws://localhost:8000/ws'); // Note: Websockets are commented out in src/websocket_events.py, this assumes they are enabled or you implement a compatible endpoint.

socket.onopen = (event) => {
    console.log('WebSocket connection opened:', event);
    // You might send a message to subscribe to specific updates, e.g., for a campaign
    // socket.send(JSON.stringify({ type: 'subscribe', campaign_id: 'some_id' }));
};

socket.onmessage = (event) => {
    console.log('Received message:', event.data);
    // Process real-time updates, e.g., new transactions, price changes
};

socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event);
};

socket.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

## API Documentation

### Base URL
`http://localhost:8000/api`

### Endpoints
#### POST /api/campaigns
Creates a new cryptocurrency campaign. The backend automatically fetches token metadata based on the provided contract address.

**Request**:
```json
{
  "contract_address": "string",
  "goal_amount": 100.0,
  "expires_at": "2025-12-31T23:59:59Z",
  "social_twitter": "string | null",
  "social_website": "string | null",
  "description": "string | null"
}
```

**Response**:
```json
{
  "success": true,
  "campaign_id": "cmp_karen123",
  "escrow_address": "9o24Px7asSDJ1ZLyQhZd7vehm9kX4VuTeJh7VGryjXkm",
  "error": null,
  "campaign": null
}
```

**Errors**:
- `400 Bad Request`: Unable to fetch token metadata for the provided contract address.
- `500 Internal Server Error`: Unexpected error during campaign creation.

#### GET /api/campaign-detail/{contract_address}
Retrieves detailed information about a specific campaign using its token's contract address.

**Request**:
Path Parameter: `contract_address` (string) - The token contract address associated with the campaign.

**Response**:
```json
{
  "success": true,
  "campaign_id": null,
  "escrow_address": null,
  "error": null,
  "campaign": {
    "id": "string (UUID)",
    "name": "string",
    "symbol": "string",
    "contract_address": "string",
    "image_url": "string | null",
    "wallet_address": "string",
    "goal_amount": 100.0,
    "status": "string",
    "created_at": "2025-08-25T10:30:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "campaign_type": "string | null",
    "social_twitter": "string | null",
    "social_website": "string | null",
    "description": "string | null",
    "current_balance": 50.5,
    "contributor_count": 5,
    "token_launchpad": "string | null",
    "token_source": "string | null",
    "liquidity": "string",
    "market_cap": "string",
    "price_usd": "string",
    "volume_24h": "string"
  }
}
```

**Errors**:
- `404 Not Found`: Campaign not found for the given contract address.
- `500 Internal Server Error`: Unexpected error retrieving campaign details.

#### GET /api/escrow-transactions/{wallet_address}
Fetches all transactions associated with a given escrow wallet address, providing details on contributions.

**Request**:
Path Parameter: `wallet_address` (string) - The Solana wallet address functioning as an escrow.

**Response**:
```json
{
  "transactionCount": 2,
  "contributors": [
    "ContributorWalletAddress1",
    "ContributorWalletAddress2"
  ],
  "transactions": [
    {
      "signature": "TransactionSignature1",
      "amount": 0.5,
      "from": "ContributorWalletAddress1",
      "timestamp": 1678886400
    },
    {
      "signature": "TransactionSignature2",
      "amount": 1.2,
      "from": "ContributorWalletAddress2",
      "timestamp": 1678886000
    }
  ]
}
```

**Errors**:
- `404 Not Found`: Campaign not found for the specified wallet address.
- `500 Internal Server Error`: Unexpected error retrieving escrow transactions.

#### GET /api/escrow-balance
Retrieves the current SOL and USD balance of an escrow wallet, along with transaction statistics.

**Request**:
Query Parameter: `wallet` (string, required) - The escrow Solana wallet address.

**Response**:
```json
{
  "success": true,
  "data": {
    "address": "EscrowWalletAddress",
    "balanceSOL": 2.75,
    "balanceUSD": 500.25,
    "transactionCount": 10,
    "recentTransactions": [
      {
        "signature": "RecentSignature1",
        "amount": 0.1,
        "from": "RecentSender1",
        "timestamp": 1678972800
      },
      {
        "signature": "RecentSignature2",
        "amount": 0.2,
        "from": "RecentSender2",
        "timestamp": 1678972700
      }
    ]
  }
}
```

**Errors**:
- `500 Internal Server Error`: Unexpected error fetching escrow balance or transaction data.

#### GET /api/campaigns/{campaign_id}/qr
Generates a Solana Pay QR code for a specific campaign, optionally including a predefined amount.

**Request**:
Path Parameter: `campaign_id` (string) - The unique identifier of the campaign.
Query Parameter: `amount` (float, optional) - The amount of SOL to request in the QR code.

**Response**:
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA... (base64 encoded PNG)",
  "solana_pay_uri": "solana:EscrowWalletAddress?amount=1.5",
  "escrow_address": "EscrowWalletAddress"
}
```

**Errors**:
- `404 Not Found`: Campaign not found for the provided campaign ID.
- `500 Internal Server Error`: Unexpected error during QR code generation.

#### GET /api/token/{contract_address}
Retrieves information about a specific token by its contract address, utilizing a cache for performance.

**Request**:
Path Parameter: `contract_address` (string) - The contract address of the token.

**Response**:
```json
{
  "status": "success",
  "data": {
    "contract_address": "TokenContractAddress",
    "name": "Token Name",
    "symbol": "TKN",
    "decimals": 9,
    "price_usd": 0.05,
    "total_supply": "1000000000",
    "holders_count": 12345
  }
}
```

**Errors**:
- `404 Not Found`: Token not found for the provided contract address.
- `500 Internal Server Error`: Unexpected error fetching token information.

#### GET /api/health
Performs a health check on the API, database connection, and Solana RPC service.

**Request**:
No parameters.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-25T10:30:00.123456+00:00",
  "sol_price": 180.0,
  "monitored_campaigns": 5
}
```

**Errors**:
- `503 Service Unavailable`: Health check failed due to issues with the database, Solana RPC, or other services.
  ```json
  {
    "status": "unhealthy",
    "error": "Database connection failed"
  }
  ```

## Technologies Used
| Technology         | Description                                     | Link                                         |
| :----------------- | :---------------------------------------------- | :------------------------------------------- |
| **Python**         | Primary programming language                    | [python.org](https://www.python.org/)        |
| **FastAPI**        | High-performance web framework for APIs         | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| **SQLAlchemy**     | SQL toolkit and Object-Relational Mapper (ORM)  | [sqlalchemy.org](https://www.sqlalchemy.org/) |
| **PostgreSQL**     | Robust open-source relational database          | [postgresql.org](https://www.postgresql.org/) |
| **Celery**         | Distributed task queue for asynchronous tasks   | [docs.celeryq.dev](https://docs.celeryq.dev/) |
| **Redis**          | In-memory data structure store, used as Celery broker | [redis.io](https://redis.io/)                |
| **Solana (SDK)**   | Blockchain for high-performance decentralized apps | [solana.com](https://solana.com/)            |
| **Docker**         | Containerization platform                       | [docker.com](https://www.docker.com/)        |
| **Uvicorn**        | ASGI server for Python web applications         | [www.uvicorn.org](https://www.uvicorn.org/)  |
| **Pydantic**       | Data validation and settings management         | [docs.pydantic.dev](https://docs.pydantic.dev/)|
| **Aiohttp**        | Asynchronous HTTP client/server for Python      | [docs.aiohttp.org](https://docs.aiohttp.org/)|

## Contributing Guidelines
We welcome contributions to the Crypto Clone Backend API! To contribute:

1.  🍴 **Fork** the repository to your GitHub account.
2.  🌿 **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name`.
3.  ✍️ **Implement** your changes, ensuring they align with existing coding standards.
4.  🧪 **Write tests** to cover your new features or bug fixes.
5.  ✉️ **Commit** your changes with a clear and descriptive message.
6.  ⬆️ **Push** your branch to your forked repository.
7.  🤝 **Open a Pull Request** to the `main` branch of the original repository, providing a detailed explanation of your changes.

## License Information
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
*   **Your Name**
    *   LinkedIn: [YourLinkedInProfile](https://www.linkedin.com/in/yourprofile)
    *   Twitter: [YourTwitterHandle](https://twitter.com/yourhandle)
    *   Portfolio: [YourPortfolioWebsite](https://www.yourportfolio.com)

---

[![Readme was generated by Dokugen](https://img.shields.io/badge/Readme%20was%20generated%20by-Dokugen-brightgreen)](https://www.npmjs.com/package/dokugen)