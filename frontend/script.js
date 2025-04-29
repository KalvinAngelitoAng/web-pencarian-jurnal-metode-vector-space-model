document.getElementById('searchForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const query = document.getElementById('query').value;
  const resultsDiv = document.getElementById('results');
  const timeDiv = document.getElementById('searchTime');

  fetch('http://127.0.0.1:5000/search', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query: query})
  })
  .then(response => response.json())
  .then(data => {
      resultsDiv.innerHTML = '';
      timeDiv.innerHTML = `Waktu pencarian: ${data.search_time} detik`;
      //kalvin disini :3
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
      }
  });
});
