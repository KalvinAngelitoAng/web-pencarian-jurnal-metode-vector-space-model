document.getElementById('searchForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const query = document.getElementById('query').value;

    fetch('http://127.0.0.1:5000/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query })
    })
    .then(res => res.json())
    .then(data => {
        const { results, search_time, total_journals } = data;
        document.getElementById('searchTime').textContent = `Waktu pencarian: ${search_time} detik`;
        document.getElementById('totalJournals').textContent = `Jumlah Total Jurnal (Realtime): ${total_journals}`;

        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';
        const labels = [];
        const scores = [];

        results.forEach(result => {
            const card = document.createElement('div');
            card.className = 'card mb-2';
            card.innerHTML = `
                <div class="card-body">
                    <h5>${result.title}</h5>
                    <p><strong>Jurnal:</strong> ${result.journal_name}</p>
                    <p><strong>Institusi:</strong> ${result.institution}</p>
                    <p><strong>Skor Kemiripan:</strong> ${result.score}</p>
                    <a href="${result.url}" target="_blank">Kunjungi</a>
                </div>
            `;
            resultsDiv.appendChild(card);

            labels.push(result.title);
            scores.push(result.score);
        });

        const ctx = document.getElementById('accuracyChart').getContext('2d');
        if (window.chartInstance) window.chartInstance.destroy();
        window.chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: scores,
                    backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: {
                        display: true,
                        text: 'Skor Kecocokan Judul'
                    }
                }
            }
        });
    });
});

function updateTotalJournals() {
    fetch('http://127.0.0.1:5000/total_journals')
        .then(res => res.json())
        .then(data => {
            document.getElementById('totalJournals').textContent = `Jumlah Total Jurnal (Realtime): ${data.total_journals}`;
        });
}

updateTotalJournals();
setInterval(updateTotalJournals, 5000);
