// JavaScript for "Select All" functionality
document.getElementById('selectAll').addEventListener('click', function () {
  const checkboxes = document.querySelectorAll('.row-checkbox');
  checkboxes.forEach(checkbox => checkbox.checked = this.checked);
});

document.getElementById('resetFilters').addEventListener('click', function () {
  // Reset task filter
  document.getElementById('taskFilter').value = '';
  document.getElementById('editTaskButton').disabled = true;
  document.getElementById('removeTaskButton').disabled = true;

  // Reset labels filter
  document.getElementById('labelsDropdown').value = '';
  document.getElementById('removeLabelButton').disabled = true;

  // Reset search inputs
  document.getElementById('searchInput').value = '';
  document.getElementById('searchDropdown').value = '';

  // Show all rows
  document.querySelectorAll('tbody tr').forEach(row => {
      row.style.display = '';
  });
});




// Enable/disable "Remove Label" button based on selection
document.getElementById('labelsDropdown').addEventListener('change', function () {
  const selectedTask = this.value;
  document.getElementById('removeLabelButton').disabled = !selectedTask;
});

// Enable/disable "Remove Task" button based on selection
document.getElementById('taskFilter').addEventListener('change', function () {
      const selectedTask = this.value;
      document.getElementById('removeTaskButton').disabled = !selectedTask;
  });

  function applyFilters() {
      const searchBy = document.getElementById('searchDropdown').value.toLowerCase();
      const searchValue = document.getElementById('searchInput').value.toLowerCase();
      const selectedLabel = document.getElementById('labelsDropdown').value.toLowerCase();
      const rows = document.querySelectorAll('tbody tr');
  
      rows.forEach(row => {
          let matchesSearch = true;
          let matchesLabel = true;
  
          // Apply search filter
          if (searchBy && searchValue) {
              let cellValue;
              switch (searchBy) {
                  case 'name':
                      cellValue = row.children[2].textContent.toLowerCase();
                      break;
                  case 'lastname':
                      cellValue = row.children[3].textContent.toLowerCase();
                      break;
                  case 'email':
                      cellValue = row.children[4].textContent.toLowerCase();
                      break;
                  case 'id':
                      cellValue = row.children[1].textContent.toLowerCase();
                      break;
              }
              matchesSearch = cellValue ? cellValue.includes(searchValue) : false;
          }
  
          // Apply label filter
          if (selectedLabel) {
              const labels = row.querySelectorAll('.badge');
              matchesLabel = Array.from(labels).some(label => label.textContent.toLowerCase() === selectedLabel);
          }
  
          // Show row only if it matches both filters
          row.style.display = matchesSearch && matchesLabel ? '' : 'none';
      });
  }
  
  // Event listeners for filters
      document.getElementById('searchInput').addEventListener('input', applyFilters);
      document.getElementById('labelsDropdown').addEventListener('change', applyFilters);