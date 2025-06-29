// Função para formatar e validar CPF
function formatCPF(input) {
  let value = input.value.replace(/\D/g, "");

  if (value.length > 11) {
    value = value.slice(0, 11);
  }

  if (value.length > 9) {
    value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{2}).*/, "$1.$2.$3-$4");
  } else if (value.length > 6) {
    value = value.replace(/^(\d{3})(\d{3})(\d{3}).*/, "$1.$2.$3");
  } else if (value.length > 3) {
    value = value.replace(/^(\d{3})(\d{3}).*/, "$1.$2");
  }

  input.value = value;
}

// Função para validar CPF
function validateCPF(cpf) {
  cpf = cpf.replace(/[^\d]/g, "");

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

// Função para formatar telefone (mais flexível)
function formatPhone(input) {
  let value = input.value.replace(/\D/g, "");

  // Remove zeros à esquerda do DDD
  if (value.length > 2 && value.startsWith("0")) {
    value = value.substring(1);
  }

  if (value.length > 11) {
    value = value.slice(0, 11);
  }

  // Formata baseado no número de dígitos
  if (value.length === 11) {
    // Celular: (61) 99244-5034
    value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
  } else if (value.length === 10) {
    // Fixo: (61) 3244-5034
    value = value.replace(/^(\d{2})(\d{4})(\d{4}).*/, "($1) $2-$3");
  } else if (value.length > 2) {
    // Formato parcial
    value = value.replace(/^(\d{2})(\d{0,5}).*/, "($1) $2");
  }

  input.value = value;
}

// Função para validar telefone (mais rigorosa)
function validatePhone(phone) {
  phone = phone.replace(/\D/g, "");

  // Remove zeros à esquerda do DDD
  if (phone.length > 2 && phone.startsWith("0")) {
    phone = phone.substring(1);
  }

  // Aceita números de 10 ou 11 dígitos
  if (phone.length < 10 || phone.length > 11) return false;

  // DDD deve estar entre 11 e 99
  const ddd = parseInt(phone.substring(0, 2));
  if (ddd < 11 || ddd > 99) return false;

  // Lista de DDDs válidos no Brasil (atualizada)
  const validDDDs = [
    11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35,
    37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62, 63, 64,
    65, 66, 67, 68, 69, 71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87, 88,
    89, 91, 92, 93, 94, 95, 96, 97, 98, 99,
  ];

  if (!validDDDs.includes(ddd)) return false;

  // Para números de 11 dígitos, verifica se o terceiro dígito é 8 ou 9
  if (phone.length === 11) {
    const terceiroDigito = parseInt(phone.charAt(2));
    if (terceiroDigito !== 8 && terceiroDigito !== 9) return false;
  }

  // Para números de 10 dígitos, verifica se o terceiro dígito é 2, 3, 4, 5, 6, 7
  if (phone.length === 10) {
    const terceiroDigito = parseInt(phone.charAt(2));
    if (terceiroDigito < 2 || terceiroDigito > 7) return false;
  }

  return true;
}

// Função para normalizar telefone (remove formatação)
function normalizePhone(phone) {
  let normalized = phone.replace(/\D/g, "");

  // Remove zeros à esquerda do DDD
  if (normalized.length > 2 && normalized.startsWith("0")) {
    normalized = normalized.substring(1);
  }

  return normalized;
}

// Event listeners para os campos
document.addEventListener("DOMContentLoaded", function () {
  const cpfInput = document.getElementById("cpf");
  const telefoneInput = document.getElementById("telefone");

  if (cpfInput) {
    cpfInput.addEventListener("input", function () {
      formatCPF(this);
    });

    cpfInput.addEventListener("blur", function () {
      const cpf = this.value.replace(/\D/g, "");
      if (cpf && !validateCPF(cpf)) {
        alert("CPF inválido! Por favor, verifique.");
        this.value = "";
        this.focus();
      }
    });
  }

  if (telefoneInput) {
    telefoneInput.addEventListener("input", function () {
      formatPhone(this);
    });

    telefoneInput.addEventListener("blur", function () {
      const phone = normalizePhone(this.value);
      if (phone && !validatePhone(phone)) {
        alert(
          "Telefone inválido! Use o formato (DDD) XXXXX-XXXX para celular ou (DDD) XXXX-XXXX para fixo.\n\nDDDs válidos: 11-99 (exceto 20, 23, 25, 26, 29, 30, 36, 39, 40, 50, 52, 56-60, 70, 72, 76, 78, 80, 90)"
        );
        this.value = "";
        this.focus();
      }
    });
  }
});

// Função para carregar municípios baseado no estado selecionado
document.addEventListener("DOMContentLoaded", function () {
  const estadoSelect = document.getElementById("estado");
  const municipioSelect = document.getElementById("municipio");

  if (estadoSelect && municipioSelect) {
    estadoSelect.addEventListener("change", async function () {
      const estadoId = this.value;

      if (!estadoId) {
        municipioSelect.innerHTML =
          '<option value="">Selecione um estado primeiro</option>';
        return;
      }

      try {
        const response = await fetch(`/get_municipios/${estadoId}`);
        const data = await response.json();

        municipioSelect.innerHTML =
          '<option value="">Selecione o município</option>';

        if (data && data.length > 0) {
          data.forEach((municipio) => {
            const option = document.createElement("option");
            option.value = municipio.id;
            option.textContent = municipio.nome;
            municipioSelect.appendChild(option);
          });
        } else {
          municipioSelect.innerHTML =
            '<option value="">Nenhum município encontrado</option>';
        }
      } catch (error) {
        console.error("Erro ao buscar municípios:", error);
        municipioSelect.innerHTML =
          '<option value="">Erro ao carregar municípios</option>';
      }
    });
  }
});

// Função para validar formulário completo
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;

  let isValid = true;
  const errors = [];

  // Validar CPF
  const cpfInput = form.querySelector("#cpf");
  if (cpfInput && cpfInput.value) {
    const cpf = cpfInput.value.replace(/\D/g, "");
    if (!validateCPF(cpf)) {
      errors.push("CPF inválido");
      isValid = false;
    }
  }

  // Validar telefone
  const telefoneInput = form.querySelector("#telefone");
  if (telefoneInput && telefoneInput.value) {
    const phone = normalizePhone(telefoneInput.value);
    if (!validatePhone(phone)) {
      errors.push("Telefone inválido");
      isValid = false;
    }
  }

  // Validar campos obrigatórios
  const requiredFields = form.querySelectorAll("[required]");
  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      const label = field.previousElementSibling?.textContent || field.name;
      errors.push(`${label} é obrigatório`);
      isValid = false;
    }
  });

  if (!isValid) {
    alert("Por favor, corrija os seguintes erros:\n" + errors.join("\n"));
  }

  return isValid;
}
