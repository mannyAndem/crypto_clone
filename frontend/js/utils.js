// ============================================
// UTILITY FUNCTIONS
// ============================================
export function getContractAddressFromURL() {
    const hash = window.location.hash;
    const match = hash.match(/\/coin\/([^\/]+)/);
    return match ? match[1] : null;
}

export function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'UTC'
    }) + ' UTC';
}

export function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

export function calculateTimeLeft(expiresAt) {
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diff = expiry - now;

    if (diff <= 0) return "Expired";

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    return `${hours}h ${minutes}m left`;
}

export function truncateAddress(address, startChars = 5, endChars = 5) {
    if (!address) return '';
    if (address.length <= startChars + endChars) return address;
    return `${address.substring(0, startChars)}...${address.substring(address.length - endChars)}`;
}

export function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent || element.value;
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary feedback
        const originalText = element.textContent;
        element.textContent = 'Copied!';
        setTimeout(() => {
            element.textContent = originalText;
        }, 1000);
    });
}

export function openExplorer() {
    const escrowAddress = document.getElementById('escrowAddress').textContent;
    window.open(`https://solscan.io/account/${escrowAddress}`, '_blank');
}

export function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toISOString().replace('T', ' ').substring(0, 19) + ' GMT';
    document.getElementById('currentTime').textContent = timeString;
}
