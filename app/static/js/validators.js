// Função para formatar e validar CPF
function formatCPF(input) {
    let value = input.value.replace(/\D/g, '');

    if (value.length > 11) {
        value = value.slice(0, 11);
    }

    if (value.length > 9) {
        value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{2}).*/, '$1.$2.$3-$4');
    } else if (value.length > 6) {
        value = value.replace(/^(\d{3})(\d{3})(\d{3}).*/, '$1.$2.$3');
    } else if (value.length > 3) {
        value = value.replace(/^(\d{3})(\d{3}).*/, '$1.$2');
    }

    input.value = value;
}

// Função para validar CPF
function validateCPF(cpf) {
    cpf = cpf.replace(/[^\d]/g, '');

    if (cpf.length !== 11) return false;

    // Verifica CPFs com números repetidos
    if (/^(\d)\1{10}$/.test(cpf)) return false;

    // Validação do primeiro dígito verificador
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let digit = 11 - (sum % 11);
    if (digit >= 10) digit = 0;
    if (digit !== parseInt(cpf.charAt(9))) return false;

    // Validação do segundo dígito verificador
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    digit = 11 - (sum % 11);
    if (digit >= 10) digit = 0;
    if (digit !== parseInt(cpf.charAt(10))) return false;

    return true;
}

// Função para formatar telefone
function formatPhone(input) {
    let value = input.value.replace(/\D/g, '');

    if (value.length > 11) {
        value = value.slice(0, 11);
    }

    if (value.length > 10) {
        value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
    } else if (value.length > 6) {
        value = value.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, '($1) $2-$3');
    } else if (value.length > 2) {
        value = value.replace(/^(\d{2})(\d{0,5}).*/, '($1) $2');
    }

    input.value = value;
}

// Função para validar telefone
function validatePhone(phone) {
    phone = phone.replace(/\D/g, '');
    return phone.length >= 10 && phone.length <= 11;
}

// Event listeners para os campos
document.addEventListener('DOMContentLoaded', function() {
    const cpfInput = document.getElementById('cpf');
    const telefoneInput = document.getElementById('telefone');

    if (cpfInput) {
        cpfInput.addEventListener('input', function() {
            formatCPF(this);
        });

        cpfInput.addEventListener('blur', function() {
            const cpf = this.value.replace(/\D/g, '');
            if (cpf && !validateCPF(cpf)) {
                alert('CPF inválido! Por favor, verifique.');
                this.value = '';
                this.focus();
            }
        });
    }

    if (telefoneInput) {
        telefoneInput.addEventListener('input', function() {
            formatPhone(this);
        });

        telefoneInput.addEventListener('blur', function() {
            const phone = this.value.replace(/\D/g, '');
            if (phone && !validatePhone(phone)) {
                alert('Telefone inválido! Por favor, verifique.');
                this.value = '';
                this.focus();
            }
        });
    }
});


estadoSelect.addEventListener('change', async function () {
    const estadoId = this.value;

    if (!estadoId) return;

    try {
        const response = await fetch(`/municipios/${estadoId}`);
        const data = await response.json();

        console.log(data);

        municipioSelect.innerHTML = '';

        if (data.success) {
            data.municipios.forEach(municipio => {
                const option = document.createElement('option');
                option.value = municipio.id;
                option.textContent = municipio.nome;
                municipioSelect.appendChild(option);
            });
        } else {
            municipioSelect.innerHTML = '<option value="">Nenhum município encontrado</option>';
        }
    } catch (error) {
        console.error('Erro ao buscar municípios:', error);
    }
});

