document.addEventListener('DOMContentLoaded', function() {
    const tasksContainer = document.getElementById('tasks-list');
    const agentsContainer = document.getElementById('agents-list');
    const crewsContainer = document.getElementById('crews-list');
    const agentSelect = document.getElementById('agent_task');

    // Função para carregar agentes
    function loadAgents() {
        fetch('/LoadAgents')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Agentes:', data);
                agentsContainer.innerHTML = '';
                agentSelect.innerHTML = '<option value="" disabled selected>Escolha um agente</option>';

                if (data && data.length) {
                    data.forEach(agent => {
                        const listItem = document.createElement('li');
                        listItem.textContent = agent.name; 
                        listItem.classList.add('clickable');
                        listItem.addEventListener('click', () => showAgentModal(agent));
                        agentsContainer.appendChild(listItem);

                        const option = document.createElement('option');
                        option.value = agent.id; 
                        option.textContent = agent.name; 
                        agentSelect.appendChild(option);
                    });
                } else {
                    agentsContainer.innerHTML = 'Nenhum agente encontrado.';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar agentes:', error);
                agentsContainer.innerHTML = 'Erro ao carregar agentes';
            });
    }

    // Função para carregar tarefas
    function loadTasks() {
        fetch('/LoadTasks')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Tarefas:', data);
                tasksContainer.innerHTML = '';

                if (data && data.length) {
                    data.forEach(task => {
                        const listItem = document.createElement('li');
                        listItem.textContent = task.name;
                        listItem.classList.add('clickable');
                        listItem.addEventListener('click', () => showTaskModal(task));
                        tasksContainer.appendChild(listItem);
                    });
                } else {
                    tasksContainer.innerHTML = 'Nenhuma tarefa encontrada.';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar tarefas:', error);
                tasksContainer.innerHTML = 'Erro ao carregar tarefas';
            });
    }

    // Função para carregar crews
    function loadCrews() {
        fetch('/LoadCrews')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Crews:', data);
                crewsContainer.innerHTML = '';

                if (data && data.length) {
                    data.forEach(crew => {
                        const listItem = document.createElement('li');
                        listItem.textContent = crew;
                        listItem.classList.add('clickable');
                        listItem.addEventListener('click', () => window.location.href = `/crew?name=${encodeURIComponent(crew)}`);
                        crewsContainer.appendChild(listItem);
                    });
                } else {
                    crewsContainer.innerHTML = 'Nenhuma crew encontrada.';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar crews:', error);
                crewsContainer.innerHTML = 'Erro ao carregar crews';
            });
    }

    // Função para exibir modal de agente
    function showAgentModal(agent) {
        const modalTitle = document.getElementById('agentsModalLabel');
        const modalBody = document.querySelector('#agentsModal .modal-body');
        
        modalTitle.textContent = `Informações do Agente: ${agent.name || 'N/A'}`;
        modalBody.innerHTML = `
            <p><strong>Nome:</strong> ${agent.name || 'N/A'}</p>
            <p><strong>Papel:</strong> ${agent.role || 'N/A'}</p>
            <p><strong>História:</strong> ${agent.backstory || 'N/A'}</p>
            <p><strong>Objetivo:</strong> ${agent.goal || 'N/A'}</p>
        `;

        const modal = new bootstrap.Modal(document.getElementById('agentsModal'));
        modal.show();
    }

    // Função para exibir modal de tarefa
    function showTaskModal(task) {
        const modalTitle = document.getElementById('tasksModalLabel');
        const modalBody = document.querySelector('#tasksModal .modal-body');

        modalTitle.textContent = `Informações da Tarefa: ${task.name || 'N/A'}`;
        modalBody.innerHTML = `
            <p><strong>Nome:</strong> ${task.name || 'N/A'}</p>
            <p><strong>Descrição:</strong> ${task.description || 'N/A'}</p>
            <p><strong>Resultado Esperado:</strong> ${task.expected_output || 'N/A'}</p>
            <p><strong>Agente Responsável:</strong> ${task.agent_task || 'N/A'}</p>
        `;

        const modal = new bootstrap.Modal(document.getElementById('tasksModal'));
        modal.show();
    }

    loadAgents();
    loadTasks();
    loadCrews();

    const tasksModal = document.getElementById('tasksModal');
    tasksModal.addEventListener('show.bs.modal', function () {
        agentSelect.innerHTML = '<option value="" disabled selected>Escolha um agente</option>'; 
        loadAgents(); 
    });

    // Salvar agent
    document.getElementById('create-agent-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const data = {
            name_agent: document.getElementById('name_agent').value,
            role_agent: document.getElementById('role_agent').value,
            backstory_agent: document.getElementById('backstory_agent').value,
            goal_agent: document.getElementById('goal_agent').value
        };

        console.log('Dados do agente:', data);

        const response = await fetch('/SaveAgent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        alert(result.message);
        loadAgents(); 
        document.getElementById('create-agent-form').reset();
    });

    // Salvar task
    document.getElementById('create-task-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Obter o nome do agente a partir do texto da opção selecionada
        const selectedAgentName = agentSelect.options[agentSelect.selectedIndex].text;
        
        const data = {
            name_task: document.getElementById('task_name').value,
            description_task: document.getElementById('task_description').value,
            expected_output_task: document.getElementById('task_expected_output').value,
            agent_task: selectedAgentName // Envia o nome do agente
        };

        console.log('Dados da tarefa:', data);

        const response = await fetch('/SaveTask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        alert(result.message);
        loadTasks();
        document.getElementById('create-task-form').reset();
    });


});


