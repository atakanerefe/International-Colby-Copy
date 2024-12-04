// This function gets the task selected in the dropdown menu and passes it into the fetchStudents function
function handleTaskSelection() {
    const taskFilter = document.getElementById('taskFilter');
    const selectedTask = taskFilter.value;
    console.log("this is a selected task: ", selectedTask)

    if (selectedTask) {
        // Call the fetchStudents function with the selected task
        fetchStudentsNew(selectedTask);
    } else {
        console.log("No task selected");
    }
}


// NEW VERSION OF FETCHSTUDENTS
// after selecting a task from admin home page
// This function fetches students who have the selected task and their progress
function fetchStudentsNew(taskName) {
    console.log("we're in :D ")
    changeTaskName(taskName);

    console.log("we're suoer in :D ")

    fetch(`/get_students_by_task?task=${taskName}`)
        .then(response => response.json())
        .then(data => {
            const students = data.students;
            console.log("data: ", data)
            console.log("students: ", students)

            // Clear previous student cards
            const studentCardsContainer = document.getElementById('tableBody');
            studentCardsContainer.innerHTML = '';

            // For each student, display the student's progress
            students.forEach(student => {
                const studentEmail = student.email;
                const studentProgress = student.progress;
                const studentID = student.id; 
                const fullName = student.name; 
                console.log("this is the fullname: ", fullName)
                // split the full name based on a space (assuming one word names)
                const [firstName, lastName] = fullName.split(' ');
                const progressText = `${studentProgress.completed}/${studentProgress.total}`;
                
                // const labelsHtml = student.tags.map(tag => `<span class="badge ${tag.html_class} m-1">${tag.name}</span>`).join('');
// <td>${labelsHtml}</td>
                // Create table row
                const tableRow = `
                    <tr>
                        <td><input type="checkbox" class="row-checkbox" /></td>
                        <td>${studentID}</td>
                        <td>${firstName}</td>
                        <td>${lastName}</td>
                        <td>${studentEmail}</td>
                        <td>${lastName}</td>
                        
                        <td>
                            <a href="/admin/view_student_progress?email=${encodeURIComponent(studentEmail)}&task_name=${encodeURIComponent(taskName)}">${progressText}</a>
                        </td>
                    </tr>
                `;

                // Append row to the table body
                tableBody.innerHTML += tableRow;

            });
        })
        .catch(error => {
            console.error('Error fetching student progress:', error);
        });
}

// This function fetches students who have the selected task and their progress
function fetchStudents(taskName) {

    changeTaskName(taskName);

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
                // Create the card for each student
                const studentCard = `
                <div class="col-12 mb-3 text-center card" style="background: #C7D9E0;">
                    <a href="/admin/view_student_progress?email=${encodeURIComponent(studentEmail)}&task_name=${encodeURIComponent(taskName)}" class="card-body d-flex justify-content-between align-items-center">
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

function changeTaskName(taskName) {
    
    document.getElementById('welcome-message').innerText = taskName;
}

// Fetches all task data for the user email and displays corresponding task.html
function fetchTasks(userEmail) {
    fetch(`/get_tasks_by_email?email=${userEmail}`)
        .then(response => response.json())
        .then(data => {
            const tasks = data.tasks;

            // Clear previous task cards
            const studentCardsContainer = document.getElementById('studentCardsContainer');
            studentCardsContainer.innerHTML = '';

            // For each task, we need to display the task info and progress
            tasks.forEach(task => {
                const taskName = task.title;
                const taskProgress = task.progress;

                const progressText = `${taskProgress.completed}/${taskProgress.total}`;

                // Show the student's email when tasks are fetched
                changeTaskName(userEmail);

                // Create the card for each task
                const taskCard = `
                    <div class="col-12 mb-3 text-center card" style="background: #C7D9E0;">
                        <a href="/admin/view_student_progress?email=${encodeURIComponent(userEmail)}&task_name=${encodeURIComponent(taskName)}" class="card-body d-flex justify-content-between align-items-center">
                            <div class="card-body d-flex justify-content-between align-items-center">
                                <div class="me-3">
                                    <h5 class="card-title">${taskName}</h5>
                                </div>
                                <div class="flex-grow-1 mx-2 position-relative">
                                    <div class="progress" role="progressbar" aria-label="Progress for ${taskName}" aria-valuenow="${taskProgress.percent}" aria-valuemin="0" aria-valuemax="100">
                                        <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: ${taskProgress.percent}%">
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
                studentCardsContainer.innerHTML += taskCard;
            });
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
        });
}