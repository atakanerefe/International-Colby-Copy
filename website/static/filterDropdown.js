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
                    populateDropdown(filterType, selectedValue, tasks, '-- Select Task --');
                })
                
        } else if (selectedValue === 'Tag') {
            fetchOptions('/get_tags')
            .then(tags => {
                console.log('Fetched tags:', tags);
                populateDropdown(filterType, selectedValue, tags, '-- Select Tag --');
            })
        } else {
            // Clear the second dropdown if no valid selection
            clearDropdown(filterType, '-- Select Task or Tag --');
        }
    });
});

// Function to fetch options dynamically
function fetchOptions(endpoint) {
    if (endpoint == "/get_tags"){
        return fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            if (data.tags) {
                return data.tags.sort((a, b) => a.name.localeCompare(b.name));
            } else {
                console.error('No tags found');
                return [];
            }
        })
        .catch(error => {
            console.error('Error fetching options:', error);
            return [];
        });
    }
    else {
        return fetch(endpoint)
        .then(response => response.json())
        .then(data => {
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
}

// Function to populate the dropdown with options
function populateDropdown(dropdown, dropdownName, options, defaultOptionText) {
    clearDropdown(dropdown, defaultOptionText);

    options.forEach(option => {
        const optionElement = document.createElement('option');
        if (dropdownName == "taskFilter" || dropdownName == "Task"){
            optionElement.value = option.title; 
            optionElement.textContent = option.title;
        }
        else if(dropdownName == "tagFilter" || dropdownName == "Tag"){    
            optionElement.value = option.name; 
            optionElement.textContent = option.name; 
        }
        else{
            console.log('Error fetching options:');
        }
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
        .then(tasks => populateDropdown(taskFilter, taskFilter.id, tasks, '-- Filter by Task --'))
        .catch(error => console.error('Error populating task filter:', error));
}

// Function to populate the tagFilter dropdown
function populateTagFilter(tagFilter) {
    fetchOptions('/get_tags')
        .then(tags => {
            console.log('Fetched tags populate:', tags);
            populateDropdown(tagFilter, tagFilter.id, tags, '-- Filter by Tag --')
        })
        .catch(error => console.error('Error populating tag filter:', error));
}