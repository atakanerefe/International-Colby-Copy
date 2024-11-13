// This function fetches students who have the selected task and their progress
function fetchStudents(taskName) {
    fetch(`/get_students_by_task?task=${taskName}`)
        .then(response => response.json())
        .then(data => {
            const students = data.students;

            // Clear previous student cards
            const studentCardsContainer = document.getElementById('studentCardsContainer');
            studentCardsContainer.innerHTML = '';

            // For each student, display the student's progress
            students.forEach(student => {
                const studentEmail = student.email;
                const studentProgress = student.progress;

                // Calculate progress text (e.g., 3/5 subtasks completed)
                const progressText = `${studentProgress.completed}/${studentProgress.total}`;

                // Create the card for each student
                const studentCard = `
                <div class="col-12 mb-3 text-center card" style="background: #C7D9E0;">
                    <a href="javascript:fetchTasks('${studentEmail}')" class="card-body d-flex justify-content-between align-items-center">
                        <div class="card-body d-flex justify-content-between align-items-center">
                            <div class="me-3">
                                <h5 class="card-title">${studentEmail}</h5>
                            </div>
                            <div class="flex-grow-1 mx-2 position-relative">
                                <div class="progress" role="progressbar" aria-label="Progress for ${studentEmail}" aria-valuenow="${studentProgress.percent}" aria-valuemin="0" aria-valuemax="100">
                                    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: ${studentProgress.percent}%">
                                        <span class="progress-text">${progressText}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="ms-3">
                                <i class="fa-solid fa-envelope" style="font-size: 24px; cursor: pointer;" title="Message"></i>
                            </div>
                        </div>
                    </a>
                </div>
            `;
                studentCardsContainer.innerHTML += studentCard;
            });
        })
        .catch(error => {
            console.error('Error fetching student progress:', error);
        });
}