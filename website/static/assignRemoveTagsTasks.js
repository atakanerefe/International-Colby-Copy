document.addEventListener('DOMContentLoaded', function() {
  let isSubmitting = false; // Flag to prevent multiple submissions

  document.getElementById('submitAssignOrRemove').addEventListener('click', function(event) {
      if (isSubmitting) return; // Prevent multiple submissions
      isSubmitting = true;
      event.preventDefault(); // Prevent the default form submission

      // Get selected student emails
      const selectedEmails = Array.from(document.querySelectorAll('.row-checkbox:checked'))
          .map(checkbox => checkbox.closest('tr').querySelector('td:nth-child(5)').textContent.trim());

      // Get the tag or task name from the input field
      const itemName = document.getElementById('assignOrRemoveItemName').value;

      // Get the type (Task or Tag) from the dropdown
      const itemType = document.getElementById('tagOrTask').value;

      // Get the action (Assign or Remove) from the dropdown
      const actionType = document.getElementById('assignRemoveToggle').value;

      // Set the value of the hidden input fields
      document.getElementById('selectedStudentEmailsInput').value = selectedEmails.join(',');

      // Optionally, you can prevent form submission if no emails are selected
      if (selectedEmails.length === 0) {
          alert('Please select at least one student.');
          isSubmitting = false;
          return;
      }

      // Prepare the data to be sent
      const formData = new FormData();
      formData.append('selectedStudentEmailsInput', selectedEmails.join(','));
      formData.append('itemName', itemName);
      formData.append('itemType', itemType);
      formData.append('actionType', actionType);

      // Send the AJAX request
      fetch(updateTagsTasksUrl, {
          method: 'POST',
          body: formData,
      })
      .then(response => response.json())
      .then(data => {
          console.log('Response data:', data); // Log the response data
          if (data.success) {
              alert('Item updated successfully.');
          } else {
              alert('Failed to update item.');
          }
          isSubmitting = false; // Reset the flag
      })
      .catch(error => {
          console.error('Error:', error); // Log the error details
          alert('An error occurred while updating tags/tasks.');
          isSubmitting = false; // Reset the flag
      });
  });
});