document.addEventListener("DOMContentLoaded", () => {
    const tagOrTaskToggle = document.getElementById('tagOrTask');
    const filterType = document.getElementById('assignOrRemoveItemName');
    const taskFilter = document.getElementById('taskFilter');
    const tagFilter = document.getElementById('tagFilter');

    // Populate the taskFilter dropdown on page load
    populateTaskFilter(taskFilter);
    populateTagFilter(tagFilter);

    // Event listener for the first dropdown
    tagOrTaskToggle.addEventListener('change', () => {
        const selectedValue = tagOrTaskToggle.value;

        // Fetch options based on the selection
        if (selectedValue === 'Task') {
            fetchOptions('/get_tasks')
                .then(tasks => {
                    console.log('Fetched tasks:', tasks);
                    populateDropdown(filterType, tasks, '-- Select Task --');
                })
                
        } else if (selectedValue === 'Tag') {
            fetchOptions('/get_tags')
                .then(tags => populateDropdown(filterType, tags, '-- Select Tag --'));
        } else {
            // Clear the second dropdown if no valid selection
            clearDropdown(filterType, '-- select task or tag --');
        }
    });
});

// Function to fetch options dynamically
function fetchOptions(endpoint) {
    return fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            console.log('Fetched data:', data);  // Check if 'tasks' exists
            console.log('Fetched tasks:', data.tasks);
            if (data.tasks) {
                return data.tasks;
            } else {
                console.error('No tasks found');
                return [];
            }
        })
        .catch(error => {
            console.error('Error fetching options:', error);
            return [];
        });
}

// Function to populate the dropdown with options
function populateDropdown(dropdown, options, defaultOptionText) {
    clearDropdown(dropdown, defaultOptionText);

    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.title; // Use value or name as the option's value
        optionElement.textContent = option.title; // Use text or name as the option's display text
        dropdown.appendChild(optionElement);
    });
}

// Function to clear a dropdown and add a default option
function clearDropdown(dropdown, defaultOptionText) {
    dropdown.innerHTML = ''; // Clear existing options
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = defaultOptionText;
    defaultOption.selected = true;
    dropdown.appendChild(defaultOption);
}

// Function to populate the taskFilter dropdown
function populateTaskFilter(taskFilter) {
    fetchOptions('/get_tasks')
        .then(tasks => populateDropdown(taskFilter, tasks, '-- Filter by Task --'))
        .catch(error => console.error('Error populating task filter:', error));
}

// Function to populate the tagFilter dropdown
function populateTagFilter(tagFilter) {
    fetchOptions('/get_tags')
        .then(tags => populateDropdown(tagFilter, tags, '-- Filter by Tag --'))
        .catch(error => console.error('Error populating tag filter:', error));
}