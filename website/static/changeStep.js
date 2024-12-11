function incrementStep(){
    var activeStep = document.getElementById('active-step-data');
    var number = parseInt(activeStep.getAttribute('value'), 10);
    activeStep.setAttribute('value', number + 1);
    changeStep(1);
}

function decrementStep(){
    var activeStep = document.getElementById('active-step-data');
    var number = parseInt(activeStep.getAttribute('value'), 10);
    activeStep.setAttribute('value', number - 1);
    changeStep(-1);
}

// handles the step tracker functionality
function changeStep(change){
    const steps = JSON.parse(document.getElementById('steps-data').value);
    const activeStep = parseInt(document.getElementById('active-step-data').value, 10);

    // change the highlighted step
    current_highlight = document.getElementById(`step-${activeStep-change}`);
    current_highlight.className = 'list-group-item';

    next_highlight = document.getElementById(`step-${activeStep}`);
    next_highlight.className = 'list-group-item active';

    // update what buttons are visible
    prev_button = document.getElementById(`previous-btn`);
    next_button = document.getElementById(`next-btn`);
    submit_button = document.getElementById(`submit-btn`);

    if (activeStep == steps.length){
        if (steps.length > 1){
            next_button.style.display = 'none';
            prev_button.style.display = 'block';
            submit_button.style.display = 'block';
        } else {
            next_button.style.display = 'none';
            prev_button.style.display = 'none';
            submit_button.style.display = 'block';
        }
    } else if (activeStep == 1){
        next_button.style.display = 'block';
        prev_button.style.display = 'none';
        submit_button.style.display = 'none';
    } else {
        next_button.style.display = 'block';
        prev_button.style.display = 'block';
        submit_button.style.display = 'none';
    }

    // change the step card
    step = steps[activeStep-1];
    console.log(step['subtask_id'])
    card = document.getElementById('step-card');
    card.querySelector('.card-header').innerText = `Step ${activeStep}`;
    card.querySelector('.card-title').innerText = `${step['title']}`;
    card.querySelector('.card-text').innerText = `${step['content']}`;
}