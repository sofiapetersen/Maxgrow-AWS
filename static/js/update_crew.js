document.getElementById('edit-crew-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const nameCrew = document.getElementById('name-crew').value;
    const quantityAgents = document.getElementById('quantity_agents').value;
    const quantityTasks = document.getElementById('quantity_tasks').value;
    
    const selectedAgents = [...document.querySelectorAll('#agents-list input:checked')].map(agent => agent.id.split('-')[1]);
    const selectedTasks = [...document.querySelectorAll('#tasks-list input:checked')].map(task => task.id.split('-')[1]);


    fetch('/updateCrew', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name_crew: nameCrew,
            agents_crew: selectedAgents,
            tasks_crew: selectedTasks,
            agent_count: quantityAgents,
            task_count: quantityTasks,
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data); 
        if (data.success) {
            window.location.href = '/crew_manager'; // Redirecionar após sucesso
        } else {
            alert(data.error);
        }
    })
    .catch(error => console.error('Erro:', error));
});
