(function () {
  var toggle = document.querySelector('[data-sidebar-toggle]');
  var backdrop = document.querySelector('[data-sidebar-backdrop]');

  function setOpen(open) {
    document.body.classList.toggle('sidebar-open', open);
    if (toggle) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    if (backdrop) {
      backdrop.hidden = !open;
    }
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      setOpen(!document.body.classList.contains('sidebar-open'));
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', function () {
      setOpen(false);
    });
  }

  function getOpenModal() {
    return document.querySelector('[data-modal]:not([hidden])');
  }

  function closeModal(modal) {
    if (!modal) {
      return;
    }
    modal.hidden = true;
    document.body.classList.remove('modal-open');
    var search = modal.querySelector('[data-student-search]');
    if (search) {
      search.value = '';
      filterStudents(modal, '');
    }
  }

  function openModal(modal) {
    if (!modal) {
      return;
    }
    modal.hidden = false;
    document.body.classList.add('modal-open');
    var search = modal.querySelector('[data-student-search]');
    if (search) {
      search.focus();
      return;
    }
    var firstField = modal.querySelector('input:not([type="hidden"]), select, textarea');
    if (firstField) {
      firstField.focus();
    }
  }

  document.querySelectorAll('[data-modal][data-modal-open-on-load]').forEach(function (modal) {
    openModal(modal);
  });

  function filterStudents(modal, query) {
    var needle = (query || '').trim().toLowerCase();
    var items = modal.querySelectorAll('[data-student-item]');
    var visibleCount = 0;

    items.forEach(function (item) {
      var haystack = (item.getAttribute('data-search') || '').toLowerCase();
      var match = !needle || haystack.indexOf(needle) !== -1;
      item.hidden = !match;
      if (match) {
        visibleCount += 1;
      }
    });

    var empty = modal.querySelector('[data-student-empty]');
    if (empty) {
      empty.hidden = visibleCount > 0 || items.length === 0;
    }
  }

  document.querySelectorAll('[data-modal-open]').forEach(function (trigger) {
    trigger.addEventListener('click', function () {
      openModal(document.getElementById(trigger.getAttribute('data-modal-open')));
    });
  });

  document.querySelectorAll('[data-modal]').forEach(function (modal) {
    modal.querySelectorAll('[data-modal-close]').forEach(function (closer) {
      closer.addEventListener('click', function () {
        closeModal(modal);
      });
    });

    var search = modal.querySelector('[data-student-search]');
    if (search) {
      search.addEventListener('input', function () {
        filterStudents(modal, search.value);
      });
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') {
      return;
    }
    var openModalEl = getOpenModal();
    if (openModalEl) {
      closeModal(openModalEl);
      return;
    }
    setOpen(false);
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 860) {
      setOpen(false);
    }
  });

  function isInteractiveTarget(target) {
    return Boolean(
      target.closest('a, button, input, select, textarea, label, [data-no-row-nav]')
    );
  }

  function goToHref(href) {
    if (href) {
      window.location.href = href;
    }
  }

  document.querySelectorAll('[data-row-href]').forEach(function (row) {
    row.addEventListener('click', function (event) {
      if (isInteractiveTarget(event.target)) {
        return;
      }
      // Nested clickable rows (e.g. group inside course) should not trigger the parent.
      var nested = event.target.closest('[data-row-href]');
      if (nested && nested !== row) {
        return;
      }
      event.stopPropagation();
      goToHref(row.getAttribute('data-row-href'));
    });

    row.addEventListener('keydown', function (event) {
      if (event.key !== 'Enter' && event.key !== ' ') {
        return;
      }
      if (isInteractiveTarget(event.target)) {
        return;
      }
      var nested = event.target.closest('[data-row-href]');
      if (nested && nested !== row) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      goToHref(row.getAttribute('data-row-href'));
    });
  });
})();
