// Função para carregar os dados do formulário do db
async function loadFormulario() {
    try {
        const response = await fetch('/getDataForm', {
            method: 'GET'
        });
        const data = await response.json();

        let empresaBox = document.getElementById('empresa-box');
        empresaBox.innerHTML = "";  

        data.forEach(item => {
            let col = document.createElement('div');
            col.classList.add('col-md-4', 'mb-3');

            let card = document.createElement('div');
            card.classList.add('card', 'p-3', 'shadow-sm');

            let nomeEmpresa = item.empresa || "Empresa não informada";

            let link = document.createElement('a');
            link.href = `/empresa?nome=${encodeURIComponent(nomeEmpresa)}`; // Redireciona para a página de empresa com o nome na query string
            link.classList.add('stretched-link');
            link.textContent = nomeEmpresa;

            let cardBody = document.createElement('div');
            cardBody.classList.add('card-body');
            cardBody.appendChild(link);

            card.appendChild(cardBody);
            col.appendChild(card);
            empresaBox.appendChild(col);
        });

    } catch (error) {
        console.error('Erro ao carregar os dados do formulário:', error);
    }
}

window.onload = loadFormulario;

function mostrarMensagem() {
    const mensagemDiv = document.getElementById('mensagem');
    alert('Alterações salvas com sucesso!');
    mensagemDiv.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function() {
    const crewSelect = document.getElementById('crewSelect');
    const crewSelectionForm = document.getElementById('crewSelectionForm');
    const crewModal = document.getElementById('crewModal');

    let formId = null; 
    let email = null; 

    // Função para carregar os crews
    function loadCrews() {
        fetch('/LoadCrews')
            .then(response => response.json())
            .then(data => {
                crewSelect.innerHTML = '<option value="">Selecione um Crew</option>'; 
                data.forEach(crew => {
                    const option = document.createElement('option');
                    option.value = crew; 
                    option.textContent = crew; 
                    crewSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Erro ao carregar crews:', error);
                crewSelect.innerHTML = '<option value="">Erro ao carregar crews</option>';
            });
    }


    const buttons = document.querySelectorAll('.btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            formId = this.getAttribute('data-form-id');
            email = this.getAttribute('data-email');

            // Exibe o modal e carrega os crews
            const modal = new bootstrap.Modal(crewModal);
            modal.show();
        });
    });

    // Carrega os crews quando o modal é aberto
    crewModal.addEventListener('show.bs.modal', loadCrews);

    crewSelectionForm.addEventListener('submit', function(event) {
        event.preventDefault(); 
    
        const selectedCrew = crewSelect.value;
    
        if (selectedCrew && formId && email) {
            // Coletar as perguntas dinamicamente pelo atributo name
            const respostas = {};
            const perguntas = document.querySelectorAll('[name^="pergunta"]'); // Seleciona elementos cujo name começa com "pergunta"
            
            console.log('Perguntas encontradas:', perguntas);
            console.log('Crew selecionado:', selectedCrew);
    
            perguntas.forEach(pergunta => {
                if (pergunta.value) { // Verifica se a resposta foi preenchida
                    respostas[pergunta.name] = pergunta.value; 
                }
            });
    
            console.log('Respostas coletadas:', respostas);
    
            if (Object.keys(respostas).length > 0) { // Só envia se tiver respostas válidas
                fetch(`/enviar_crew/${formId}/${email}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        respostas: respostas,
                        crew_name: selectedCrew  
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.redirect_to) {
                            window.location.href = data.redirect_to; 
                        } else {
                            const statusElement = document.getElementById(`status-${formId}`);
                            if (statusElement) {
                                statusElement.innerHTML = '<span class="enviado">Crew Executado</span>';
                            }
                        }
                    } else {
                        alert('Erro ao enviar para o crew.');
                    }
                })
                .catch(error => console.error('Erro:', error));
    
                // Fecha o modal após enviar
                const modal = bootstrap.Modal.getInstance(crewModal);
                modal.hide();
            } else {
                alert('Preencha pelo menos uma pergunta antes de enviar.');
                
            }
        } else {
            alert('Por favor, selecione um Crew e tente novamente.');
            
        }
    });
    crewModal.addEventListener('hidden.bs.modal', function() {
        window.location.reload();
    });
});    