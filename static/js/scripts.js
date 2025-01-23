// Vai pra página inicial
document.querySelector('a[href="#home"]').addEventListener('click', function() {
    document.getElementById('home').style.display = 'block';
    document.getElementById('respostas-empresa').style.display = 'none';
});



const TOKEN = "eyJhbGciOiJSUzI1NiJ9.eyJyb2xlcyI6W10sImV4cCI6NDM2MzQ5ODg4NSwidXNlcm5hbWUiOiJhcGkubWF4Z3JvdzlkMGU2NmRlM2M4NCIsImlhdCI6MTczMTA3MzYxMH0.G3qTqP3Z6PLgsl-3O4mrBjq7ak8Cc5WCXQjoldjNUYnRKZFGiPpWcfMhtsP4aQRVgHsHZo1b25nnib-2JLoZFnhef2oiRgvCdMJcAJ1Ca9EjHzfKYJqrpgOIRfVJ8_Vi-o5heIUoJ8TZfCshKJfNkdPLJxWQUVR3VULWvSe8EE1eaMoet2ZtEGi-llxhZJTHjg3sluFZ_YdJToZASe4n5ekfmMHS_HDdXQrWvb8uqdAeCgtUy_9jtSij1tdkQXBUKgxMZbACK_PNT9DULHUVYsFQj6bL_nB5C6O4rz0HAdobOlQH369rYu-W4GpkJADJce2LPdk9YA-i9fPpa2ZGkfadCYbfYRyn7t8KPUYWy-aHwnSitsnd5JO6-QEE69Lp5VOsEjtMh-1b5sdA4ZK7Eu_TxubCKTSdmutJF46dNpxlHMxvLIx3JcHDSiWybgQNgch_J1BpyguEgDBxx7Ar_s42v4H5yUc4y36UooaeHiSp8VTfCtK7TM6Kfn9SBB1zV9UxYlQUMKVR_D8CzYDys_snAjpp_sk7ZYgIYm7bhchljghc8_ox7pQBIJ4tKTlZTJ8jWOB1mEPQ20KUHyjgO66s5LqOqdlYvHXQbaSisZG833xmpm58TzH9BJeIPeHaUvr2Q1Xk_uhwIFF4_pJ_qkJAYfn7P8Q5_YMa2LwJFqE";
// eyJhbGciOiJSUzI1NiJ9.eyJyb2xlcyI6W10sImV4cCI6NDM2MzQ5ODg4NSwidXNlcm5hbWUiOiJhcGkubWF4Z3JvdzlkMGU2NmRlM2M4NCIsImlhdCI6MTczMTA3MzYxMH0.G3qTqP3Z6PLgsl-3O4mrBjq7ak8Cc5WCXQjoldjNUYnRKZFGiPpWcfMhtsP4aQRVgHsHZo1b25nnib-2JLoZFnhef2oiRgvCdMJcAJ1Ca9EjHzfKYJqrpgOIRfVJ8_Vi-o5heIUoJ8TZfCshKJfNkdPLJxWQUVR3VULWvSe8EE1eaMoet2ZtEGi-llxhZJTHjg3sluFZ_YdJToZASe4n5ekfmMHS_HDdXQrWvb8uqdAeCgtUy_9jtSij1tdkQXBUKgxMZbACK_PNT9DULHUVYsFQj6bL_nB5C6O4rz0HAdobOlQH369rYu-W4GpkJADJce2LPdk9YA-i9fPpa2ZGkfadCYbfYRyn7t8KPUYWy-aHwnSitsnd5JO6-QEE69Lp5VOsEjtMh-1b5sdA4ZK7Eu_TxubCKTSdmutJF46dNpxlHMxvLIx3JcHDSiWybgQNgch_J1BpyguEgDBxx7Ar_s42v4H5yUc4y36UooaeHiSp8VTfCtK7TM6Kfn9SBB1zV9UxYlQUMKVR_D8CzYDys_snAjpp_sk7ZYgIYm7bhchljghc8_ox7pQBIJ4tKTlZTJ8jWOB1mEPQ20KUHyjgO66s5LqOqdlYvHXQbaSisZG833xmpm58TzH9BJeIPeHaUvr2Q1Xk_uhwIFF4_pJ_qkJAYfn7P8Q5_YMa2LwJFqE

async function enviarSurvey(id_survey) {
    try {
        const response = await fetch('/add_survey', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id_survey: id_survey })
        });

        const result = await response.json();
        alert(result.success || result.error);
        console.log(result)
        window.location.reload();
    } catch (error) {
        alert('Erro ao enviar o Survey ID: ' + error.message);
    }
}

document.getElementById('form-add-survey').addEventListener('submit', function(event) {
    event.preventDefault();
    const idSurveyInput = document.getElementById('id_survey').value;

    enviarSurvey(idSurveyInput);

    document.getElementById('id_survey').value = '';
});



document.getElementById('enviar-banco').addEventListener('click', function() {
    getData();
    alert('Dados enviados com sucesso!');
});

let surveyIds = []; 

async function carregarSurveys() {
    try {
        const response = await fetch('/get_surveys');
        const surveys = await response.json();

        surveyIds = surveys.map(survey => survey.id_survey);
        console.log("Survey IDs carregados:", surveyIds);
    } catch (error) {
        console.error('Erro ao carregar surveys:', error);
    }
}


window.onload = async function() {
    await carregarSurveys();
    loadRespostas();
    const urlParams = new URLSearchParams(window.location.hash.replace('#respostas?', ''));
    const empresa = urlParams.get('empresa');

    if (empresa) {
        loadRespostasPorEmpresa(empresa); 
        document.getElementById('home').style.display = 'none'; 
        document.getElementById('respostas-empresa').style.display = 'block';  
    }
}

// Função para carregar as respostas dos questionários
async function loadRespostas() {
    const tableBody = document.querySelector("#tabela-respostas tbody");
    tableBody.innerHTML = "";

    const empresaRespostasMap = new Map(); // Armazena empresas e suas respectivas respostas

    try {
        const promises = surveyIds.map(async (id_survey) => {
            const response = await fetch(`https://acesso.evolutto.com.br/api/v1/questionarios/${id_survey}/respostas?include=questionario,questionario_resposta,produto,contrato,organizacao`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${TOKEN}`
                }
            });
            return response.json();
        });

        const results = await Promise.all(promises);

        results.forEach(data => {
            let resultado_data = data.result.data;

                resultado_data['data']['respostas'].forEach(resposta => {
                    let email = resposta['respondido_por']['emails'][0]['email'];
                    let cell = resposta['questionario_resposta']['data']['resposta'];
    
                    let produto = resposta['produto']['data']?.nome || "Trilha não informada";
                    let empresa = resposta['respondido_por']?.nome || "Empresa não informada";
    
                    let respostaTexto = '';
                    if (typeof cell === 'object' && cell !== null) {
                        respostaTexto = Object.entries(cell)
                            .map(([, resposta], index) => `${index + 1}: ${resposta} \n`)
                            .join('\n');
                    } else {
                        respostaTexto = cell;
                    }

                // Adiciona as respostas ao mapa da empresa
                if (!empresaRespostasMap.has(empresa)) {
                    empresaRespostasMap.set(empresa, []);
                }
                empresaRespostasMap.get(empresa).push({ email, respostas: respostaTexto, produto });
            });
        });

        // Cria as linhas da tabela agrupando por empresa
        empresaRespostasMap.forEach((respostas, empresa) => {
            let row = document.createElement('tr');
            let empresaCell = document.createElement('td');

            empresaCell.innerHTML = `<a href="#respostas-empresa" class="empresa-link" data-empresa="${empresa}">${empresa}</a>`;
            row.appendChild(empresaCell);
            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Erro ao carregar as respostas:', error);
    }
}

document.addEventListener('click', function (event) {
    if (event.target.classList.contains('empresa-link')) {
        event.preventDefault(); 

        const empresa = event.target.dataset.empresa;
        if (empresa) {
            loadRespostasPorEmpresa(empresa);  // Carrega as respostas da empresa
            window.location.hash = 'respostas-empresa';  
            document.getElementById('home').style.display = 'none';  
            document.getElementById('respostas-empresa').style.display = 'block';  
        }
    }
});

async function loadRespostasPorEmpresa(empresa) {
    const respostasContainer = document.getElementById('respostas-empresa');
    respostasContainer.innerHTML = "";

    try {
        const promises = surveyIds.map(async (id_survey) => {
            const response = await fetch(`https://acesso.evolutto.com.br/api/v1/questionarios/${id_survey}/respostas?include=questionario,questionario_resposta,produto,contrato,organizacao`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${TOKEN}`
                }
            });
            return response.json();
        });

        const results = await Promise.all(promises);
        let respostasFiltradas = [];

        results.forEach(data => {
            let resultado_data = data.result.data;

            resultado_data['data']['respostas'].forEach(resposta => {
                let nomeEmpresa = resposta['respondido_por']?.nome || "Empresa não informada";

                if (nomeEmpresa === empresa) {
                    let email = resposta['respondido_por']['emails'][0]['email'];
                    let cell = resposta['questionario_resposta']['data']['resposta'];
                    let produto = resposta['produto']['data']?.nome || "Trilha não informada";
                    let respostaTexto = '';
                    if (typeof cell === 'object' && cell !== null) {
                        respostaTexto = Object.entries(cell)
                            .map(([, resposta], index) => `${index + 1}: ${resposta} <br>`)
                            .join('<br>');
                    } else {
                        respostaTexto = cell;
                    }

                    respostasFiltradas.push({ email, respostaTexto, produto });
                }
            });
        });

        // Exibe as respostas filtradas na página
        respostasFiltradas.forEach(resposta => {
            let respostaDiv = document.createElement('div');
            respostaDiv.innerHTML = `
                <div class="resposta-card" style="border: 1px solid #e0e0e0; padding: 15px; margin-bottom: 10px; border-radius: 8px; background-color: #e0e0e0;">
                <h3 style="color: #803EF6; font-size: 14px;">Produto: <span style="color: #333333;">${resposta.produto}</span></h3>    
                <p style="color: #803EF6; font-size: 16px; margin-bottom: 10px;">Email: <span style="color: #333333;">${resposta.email}</span></p>
                    <p style="color: #803EF6; font-size: 14px; line-height: 1.5;">Respostas:<br> 
                        <span style="color: #333333;">${resposta.respostaTexto}</span>
                    </p>
                </div>
            `;
            respostasContainer.appendChild(respostaDiv);
        });
        

    } catch (error) {
        console.error('Erro ao carregar as respostas da empresa:', error);
    }
}


// Função para buscar os dados no db da Evolutto
async function getData() {
    try {
        const promises = surveyIds.map(async (id_survey) => {
            const response = await fetch(`https://acesso.evolutto.com.br/api/v1/questionarios/${id_survey}/respostas?include=questionario,questionario_resposta,produto,contrato,organizacao`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${TOKEN}`
                }
            });
            return response.json();
        });

        const results = await Promise.all(promises);

        let rows = [];
        let emailSurveySet = new Set(); 

        results.forEach((data, index) => {
            let resultado_data = data.result.data;
            let current_survey_id = surveyIds[index];

            resultado_data['data']['respostas'].forEach(resposta => {
                let cell = resposta['questionario_resposta']['data']['resposta'];
                let email = resposta['respondido_por']['emails'][0]['email'];
                let empresa = resposta['respondido_por'].nome;
                let id_survey = current_survey_id;

                // Verifica se (email, id_survey) já foi adicionado
                let emailSurveyKey = `${email}-${id_survey}`;
                if (!emailSurveySet.has(emailSurveyKey)) {
                    emailSurveySet.add(emailSurveyKey); 

                    let row = {
                        email: email,
                        respostas: cell,
                        empresa: empresa,
                        surveyId: id_survey 
                    };
                    rows.push(row);
                }
            });
        });

        // Verifica se (email, id_survey) já existem no db
        let existingEmailSurveyPairs = await checkExistingEmailSurveyPairs(rows);
        let newRows = rows.filter(row => {
            let emailSurveyKey = `${row.email}-${row.surveyId}`;
            return !existingEmailSurveyPairs.includes(emailSurveyKey);
        });

        console.log("Dados a serem enviados:", newRows);

        // Envia os dados para o db
        postDataForm(newRows);

    } catch (error) {
        console.error('Erro ao buscar os dados:', error);
    }
}

// Função para verificar se os emails com id_survey já existem
async function checkExistingEmailSurveyPairs(rows) {
    try {
        const emailSurveyPairs = rows.map(row => ({
            email: row.email,
            id_survey: row.surveyId
        }));
        console.log("Pares de email e id_survey enviados para verificação:", emailSurveyPairs); // Log para verificação

        const response = await fetch('/CheckEmailSurvey', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailSurveyPairs)
        });

        if (!response.ok) {
            console.error('Erro na resposta da verificação de emails:', await response.text());
            return [];
        }

        const data = await response.json();
        return data.existingEmailSurveyPairs || [];
    } catch (error) {
        console.error('Erro ao verificar os pares (email, id_survey) existentes:', error);
        return [];
    }
}



// Função para enviar os dados para o banco 
function postDataForm(rows) {
    fetch('/SaveDataForm', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(rows)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Dados enviados para o banco:', data);
    })
    .catch(error => {
        console.error('Erro ao enviar os dados para o banco:', error);
    });
}


