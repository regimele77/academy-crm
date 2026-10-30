(function () {
  var form = document.getElementById("login-form");
  if (!form) return;

  var email = document.getElementById("email");
  var password = document.getElementById("password");
  var emailError = document.getElementById("email-error");
  var passwordError = document.getElementById("password-error");
  var toggle = form.querySelector(".password-toggle");
  var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function setError(field, input, errorEl, message) {
    var hasError = Boolean(message);
    field.classList.toggle("has-error", hasError);
    input.setAttribute("aria-invalid", hasError ? "true" : "false");

    if (hasError) {
      errorEl.hidden = false;
      errorEl.textContent = message;
      input.setAttribute("aria-describedby", errorEl.id);
      return;
    }

    errorEl.hidden = true;
    errorEl.textContent = "";
    input.removeAttribute("aria-describedby");
  }

  function validateEmail() {
    var value = email.value.trim();
    var message = "";

    if (!value) {
      message = "Enter your work email.";
    } else if (!emailPattern.test(value)) {
      message = "Enter a valid email address.";
    }

    setError(email.closest(".field"), email, emailError, message);
    return !message;
  }

  function validatePassword() {
    var value = password.value;
    var message = "";

    if (!value) {
      message = "Enter your password.";
    } else if (value.length < 8) {
      message = "Password must be at least 8 characters.";
    }

    setError(password.closest(".field"), password, passwordError, message);
    return !message;
  }

  email.addEventListener("blur", validateEmail);
  password.addEventListener("blur", validatePassword);

  email.addEventListener("input", function () {
    if (email.closest(".field").classList.contains("has-error")) {
      validateEmail();
    }
  });

  password.addEventListener("input", function () {
    if (password.closest(".field").classList.contains("has-error")) {
      validatePassword();
    }
  });

  form.addEventListener("submit", function (event) {
    var emailOk = validateEmail();
    var passwordOk = validatePassword();

    if (!emailOk || !passwordOk) {
      event.preventDefault();
      (emailOk ? password : email).focus();
    }
  });

  if (toggle && password) {
    toggle.addEventListener("click", function () {
      var showing = password.type === "text";
      var nextShowing = !showing;

      password.type = nextShowing ? "text" : "password";
      toggle.setAttribute("aria-pressed", nextShowing ? "true" : "false");
      toggle.querySelector(".sr-only").textContent = nextShowing
        ? toggle.getAttribute("data-hide-label")
        : toggle.getAttribute("data-show-label");
    });
  }
})();
