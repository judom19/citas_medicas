const searchInput = document.getElementById('searchInput');
const rows = document.querySelectorAll('tbody tr');

searchInput.addEventListener('keyup', function () {
    const searchText = searchInput.value.toLowerCase();
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchText)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});