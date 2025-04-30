document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const query = document.getElementById('query').value;
    const resultsDiv = document.getElementById('results');
    const timeDiv = document.getElementById('searchTime');

    fetch('http://127.0.0.1:5000/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        resultsDiv.innerHTML = '';
        timeDiv.innerHTML = `Waktu pencarian: ${data.search_time} detik`;

        if (data.results.length === 0) {
            resultsDiv.innerHTML = '<p>Tidak ada hasil ditemukan.</p>';
        } else {
            data.results.forEach(journal => {
                const div = document.createElement('div');
                div.className = 'card mb-3 p-3';
                div.innerHTML = `
                    <h5>${journal.title}</h5>
                    <p><strong>${journal.journal_name}</strong> - <em>${journal.institution}</em></p>
                    <p>Skor Kemiripan: ${journal.score}</p>
                    <a href="${journal.url}" target="_blank">Buka Artikel</a>
                `;
                resultsDiv.appendChild(div);
            });

            // Update chart
            const labels = data.results.map((item, index) => `${index + 1}. ${item.title.slice(0, 30)}...`);
            const scores = data.results.map(item => item.score);

            if (window.myChart) {
                window.myChart.destroy();
            }

            const ctx = document.getElementById('accuracyChart').getContext('2d');
            window.myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Skor Kemiripan',
                        data: scores,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 1
                        }
                    }
                }
            });
        }
    });
});
