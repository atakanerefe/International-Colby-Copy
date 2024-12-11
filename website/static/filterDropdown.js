document.addEventListener("DOMContentLoaded", () => {
    const tasks = [
        {% for task in tasks %}
        { value: "{{ task.title }}", label: "{{ task.title }}" },
        {% endfor %}
    ];

    const tags = [
        // Example tags; replace with actual tag data
        { value: "tag1", label: "Tag 1" },
        { value: "tag2", label: "Tag 2" },
    ];

    // Function to update the second dropdown
    window.updateFilterOptions = () => {
        const toggle = document.getElementById('tagOrTaskToggle');
        const filterType = document.getElementById('filterType');
        const selectedValue = toggle.value;

        // Clear existing options in the second dropdown
        filterType.innerHTML = '<option value="" selected>-- Select --</option>';

        let options = [];
        if (selectedValue === "task") {
            options = tasks;
        } else if (selectedValue === "tag") {
            options = tags;
        }

        // Add the filtered options to the second dropdown
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.value;
            opt.textContent = option.label;
            filterType.appendChild(opt);
        });
    };
});
