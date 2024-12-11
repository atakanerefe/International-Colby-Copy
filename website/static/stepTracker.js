// javascript function that tracks the value of active step in steps.html and updates the content accordingly
//
function stepTracker() {
    // Get the active step
    const activeStep = document.querySelector('.step.active');
    // Get the active step number
    const activeStepNumber = activeStep.dataset.stepNumber;
    // Get the step content
    const stepContent = document.querySelector(`.step-content[data-step-number="${activeStepNumber}"]`);
    // Get the step content title
    const stepContentTitle = stepContent.querySelector('.step-content-title');
    // Get the step content description
    const stepContentDescription = stepContent.querySelector('.step-content-description');
    // Get the step content image
    const stepContentImage = stepContent.querySelector('.step-content-image');
    // Get the step content button
    const stepContentButton = stepContent.querySelector('.step-content-button');

    // Update the step content based on the active step
    switch (activeStepNumber) {
        case '1':
            stepContentTitle.textContent = 'Step 1: Introduction';
            stepContentDescription.textContent = 'Welcome to the course! In this step, you will learn about the course objectives and structure.';
            stepContentImage.src = 'images/step1.jpg';
            stepContentButton.href = 'step1.html';
            break;
        case '2':
            stepContentTitle.textContent = 'Step 2: Getting Started';
            stepContentDescription.textContent = 'In this step, you will learn how to set up your development environment and get started with the course.';
            stepContentImage.src = 'images/step2.jpg';
            stepContentButton.href = 'step2.html';
            break;
        case '3':
            stepContentTitle.textContent = 'Step 3: Building Your First Project';
            stepContentDescription.textContent = 'In this step, you will build your first project and learn the basics of web development.';
            stepContentImage.src = 'images/step3.jpg';
            stepContentButton.href = 'step3.html';
            break;
        case '4':
            stepContentTitle.textContent = 'Step 4: Advanced Topics';
            stepContentDescription.textContent = 'In this step, you will explore advanced topics in web development and build a more complex project.';
            stepContentImage.src = 'images/step4.jpg';
            stepContentButton.href = 'step4.html';
            break;
        case '5':
            stepContentTitle.textContent = 'Step 5: Final Project';
            stepContentDescription.textContent = 'In this step, you will';
            stepContentImage.src = 'images/step5.jpg';
            stepContentButton.href = 'step5.html';
            break;
        default:
            stepContentTitle.textContent = 'Step 1: Introduction';
            stepContentDescription.textContent = 'Welcome to the course! In this step, you will learn about the course objectives and structure.';
            stepContentImage.src = 'images/step1.jpg';
            stepContentButton.href = 'step1.html';
            break;
    }
}
            