function addStep(stepList) {
    const newStep = stepList.firstElementChild.cloneNode(true);

    // Clear input fields in the new step
    newStep.querySelectorAll("input, textarea").forEach(input => input.value = "");

    // Determine the subtask index dynamically
    const subtaskIndex = Array.from(stepList.closest('li').parentElement.children).indexOf(stepList.closest('li'));

    // Update the step index dynamically
    const stepIndex = stepList.children.length;

    // Ensure unique names for step_title and step_content fields
    newStep.querySelector("input[name^='step_title']").name = `step_title[${subtaskIndex}][${stepIndex}]`;
    newStep.querySelector("textarea[name^='step_content']").name = `step_content[${subtaskIndex}][${stepIndex}]`;

    stepList.appendChild(newStep);

    // Update the labels with numbering
    updateLabels();
}

function deleteStep(stepList) {
    if (stepList.children.length > 1) {
        stepList.removeChild(stepList.lastElementChild);
    }

    // Update the labels with numbering
    updateLabels();
}

function addSubtask() {
    const subtaskList = document.getElementById("subtask-list");
    const newSubtask = subtaskList.firstElementChild.cloneNode(true);

    // Clear input fields in the new subtask
    newSubtask.querySelectorAll("input, textarea").forEach(input => input.value = "");

    const stepList = newSubtask.querySelector(".step-list");
    stepList.innerHTML = ""; // Clear all existing steps

    // Create a fresh, blank step for the new subtask
    const subtaskIndex = subtaskList.children.length;
    const initialStep = document.createElement("li");
    initialStep.className = "list-group-item";
    initialStep.innerHTML = `
        <div class="form-group fs-5 mb-4">
            <label>Step Title:</label>
            <input type="text" name="step_title[${subtaskIndex}][0]" class="form-control" placeholder="Enter step title">
        </div>
        <div class="form-group mb-3">
            <label>Step Content:</label>
            <textarea name="step_content[${subtaskIndex}][0]" class="form-control" rows="3" placeholder="Enter step content"></textarea>
        </div>
    `;
    stepList.appendChild(initialStep);


    // Update buttons to call addStep and deleteStep with the specific step list
    newSubtask.querySelector(".add-step-btn").onclick = () => addStep(stepList);
    newSubtask.querySelector(".delete-step-btn").onclick = () => deleteStep(stepList);

    subtaskList.appendChild(newSubtask);

    // Update the labels with numbering
    updateLabels();
}



function deleteSubtask() {
    const subtaskList = document.getElementById("subtask-list");

    if (subtaskList.children.length > 1) {
        subtaskList.removeChild(subtaskList.lastElementChild);
    }

    // Update the labels with numbering
    updateLabels();
}

function updateLabels() {
    const subtaskList = document.querySelectorAll("#subtask-list > li");
    
    // Loop through each subtask to update its label
    subtaskList.forEach((subtask, subtaskIndex) => {
        // Update the sub-task title label
        const subtaskLabel = subtask.querySelector("label");
        subtaskLabel.textContent = `${subtaskIndex + 1}. Sub-Task Title:`;

        // Loop through each step in the current subtask to update step labels
        const steps = subtask.querySelectorAll(".step-list > li");
        steps.forEach((step, stepIndex) => {
            const stepLabel = step.querySelector("label");
            stepLabel.textContent = `${subtaskIndex + 1}.${stepIndex + 1} Step Title:`;
        });
    });
}

// Initial check on page load
document.addEventListener('DOMContentLoaded', () => {
    updateDeleteSubtaskButton();
    document.querySelectorAll('.step-list').forEach(updateDeleteStepButton);
    updateLabels();  // Call updateLabels initially to ensure numbering is set on load
});
