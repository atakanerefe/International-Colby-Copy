document.addEventListener("DOMContentLoaded", () => {
    // Call the function when the page loads
    const studentName = document.getElementById('tagsContainer').getAttribute('studentName');
    fetchTagsForStudent(studentName); // or any student's name dynamically
});

// This function fetches the tags for a student
function fetchTagsForStudent(studentName) {
    // console.log("we're in :D ")

    fetch(`/get_tags_for_student?student=${studentName}`)
        .then(response => response.json())
        .then(data => {
            const tags = data.tags;
            // console.log("tags: ", tags)

            // Clear previous tags
            const tagsContainer = document.getElementById('tagsContainer');
            tagsContainer.innerHTML = '<h5 class="card-title mb-0">Your tags:</h5>';
            
            // Dynamically create and append the tags as <span> elements
            tags.forEach(tag => {
                const tagElement = document.createElement('span');
                tagElement.classList.add('badge', tag.html_class, 'm-1');
                tagElement.textContent = tag.name;

                // Append the tag element to the container
                tagsContainer.appendChild(tagElement);
            });

        })
        .catch(error => {
            console.error('Error fetching student progress:', error);
        });
}
