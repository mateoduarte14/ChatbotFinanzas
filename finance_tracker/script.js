document.addEventListener('DOMContentLoaded', function () {
    const transactionTypeSelect = document.getElementById('transactionType');
    const amountInput = document.getElementById('amount');
    const categoryInput = document.getElementById('category');
    const addTransactionButton = document.getElementById('addTransaction');
    const transactionList = document.getElementById('transactionList');
    const reportChartCanvas = document.getElementById('reportChart');

    let transactions = [];

    addTransactionButton.addEventListener('click', function () {
        const type = transactionTypeSelect.value;
        const amount = parseFloat(amountInput.value);
        const category = categoryInput.value;

        if (isNaN(amount) || category === '') {
            alert('Please enter a valid amount and category.');
            return;
        }

        const transaction = {
            type: type,
            amount: amount,
            category: category
        };

        transactions.push(transaction);
        renderTransaction(transaction);
        amountInput.value = '';
        categoryInput.value = '';
        renderChart();
    });

    function renderTransaction(transaction) {
        const listItem = document.createElement('li');
        listItem.textContent = `${transaction.type}: ${transaction.amount} (${transaction.category})`;
        transactionList.appendChild(listItem);
    }

    function renderChart() {
        // Placeholder for chart rendering logic
        console.log('Rendering chart...');
    }
});
