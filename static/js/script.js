document.getElementById('analyze-btn').addEventListener('click', async () => {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p>Analyzing stocks...</p>';

    try {
        const response = await fetch('/analyze');
        const data = await response.json();

        if (data.length > 0) {
            resultsDiv.innerHTML = data.map(stock => `
                <div class="stock-card">
                    <h3>${stock.Name} (${stock.Ticker})</h3>
                    <p><strong>Price Change:</strong> ${stock['Price Change (%)']}%</p>
                    <p><strong>Volume:</strong> ${stock.Volume}</p>
                    <p><strong>Close Price:</strong> $${stock['Close Price']}</p>
                    <p><strong>RSI:</strong> ${stock.RSI}</p>
                    <p><strong>P/E Ratio:</strong> ${stock['P/E Ratio']}</p>
                    <p><strong>Dividend Yield:</strong> ${stock['Dividend Yield (%)']}%</p>
                </div>
            `).join('');
        } else {
            resultsDiv.innerHTML = '<p>No profitable stocks found.</p>';
        }
    } catch (error) {
        resultsDiv.innerHTML = '<p>Error fetching data. Please try again.</p>';
        console.error(error);
    }
});