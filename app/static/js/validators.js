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

// Função para formatar telefone (padrão: (12)912345678)
function formatPhone(input) {
  let value = input.value.replace(/\D/g, "");

  if (value.length > 11) {
    value = value.slice(0, 11);
  }

  if (value.length > 7) {
    value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1)$2-$3");
  } else if (value.length > 2) {
    value = value.replace(/^(\d{2})(\d{0,5}).*/, "($1)$2");
  }

  input.value = value;
}

// Função para validar telefone (padrão: (12)912345678)
function validatePhone(phone) {
  phone = phone.replace(/\D/g, "");

  // Deve ter exatamente 11 dígitos
  if (phone.length !== 11) return false;

  // DDD deve estar entre 11 e 99
  const ddd = parseInt(phone.substring(0, 2));
  if (ddd < 11 || ddd > 99) return false;

  // Deve começar com 9 após o DDD
  if (phone.charAt(2) !== "9") return false;

  return true;
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
      const phone = this.value.replace(/\D/g, "");
      if (phone && !validatePhone(phone)) {
        alert("Telefone inválido! Deve seguir o padrão (12)912345678");
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
