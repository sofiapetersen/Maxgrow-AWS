document.addEventListener('DOMContentLoaded', function () {
    const agentContainer = document.getElementById('agents-list');
    const taskContainer = document.getElementById('tasks-list');

    // Carregar agentes do banco de dados
    fetch('/LoadAgents')
        .then(response => response.json())
        .then(agents => {
            agents.forEach(agent => {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = agent.name; // Presumindo que agent tem uma propriedade 'name'
                checkbox.id = `agent-${agent.name}`;
                
                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.innerText = agent.name; // Acesse a propriedade 'name' do objeto agent
                
                const div = document.createElement('div');
                div.appendChild(checkbox);
                div.appendChild(label);
                agentContainer.appendChild(div);
            });
        })
        .catch(error => console.error('Erro ao carregar agentes:', error));

    // Carregar tarefas do banco de dados
    fetch('/LoadTasks')
        .then(response => response.json())
        .then(tasks => {
            tasks.forEach(task => {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = task.name; // Presumindo que task tem uma propriedade 'name'
                checkbox.id = `task-${task.name}`;
                
                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.innerText = task.name; // Acesse a propriedade 'name' do objeto task
                
                const div = document.createElement('div');
                div.appendChild(checkbox);
                div.appendChild(label);
                taskContainer.appendChild(div);
            });
        })
        .catch(error => console.error('Erro ao carregar tarefas:', error));

    // Lidar com o envio do formulário
    document.getElementById('create-crew-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const selectedAgents = Array.from(document.querySelectorAll('#agents-list input[type="checkbox"]:checked'))
            .map(checkbox => checkbox.value);

        const selectedTasks = Array.from(document.querySelectorAll('#tasks-list input[type="checkbox"]:checked'))
            .map(checkbox => checkbox.value);

        const nameCrew = document.getElementById('name-crew').value;
        const selectedLLM = document.getElementById('llm-crew').value;
        const agentCount = selectedAgents.length;
        const taskCount = selectedTasks.length;

        const crewData = {
            name_crew: nameCrew,
            agents_crew: selectedAgents,
            tasks_crew: selectedTasks,
            agent_count: agentCount,
            task_count: taskCount,
            llm_crew: selectedLLM
        };

        fetch('/SaveCrew', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(crewData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Crew salvo com sucesso!');
                window.location.href = '/crew_manager';
            } else {
                alert('Erro ao salvar o crew: ' + (data.error || 'Erro desconhecido.'));
            }
        })
        .catch(error => console.error('Erro ao salvar crew:', error));
    });

    document.getElementById('create-crew-form').reset();
});
