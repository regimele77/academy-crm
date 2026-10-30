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

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      setOpen(false);
    }
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 860) {
      setOpen(false);
    }
  });
})();

(function () {
  document.querySelectorAll('[data-profile-dropzone]').forEach(function (zone) {
    var input = zone.querySelector('[data-profile-input]');
    var preview = zone.querySelector('[data-profile-preview]');
    var filename = zone.querySelector('[data-profile-filename]');
    if (!input || !preview) {
      return;
    }

    function setImageIn(container, selectors, src) {
      if (!container) {
        return;
      }
      var img = container.querySelector(selectors.image);
      var initials = container.querySelector(selectors.initials);
      if (!img) {
        img = document.createElement('img');
        Object.keys(selectors.attrs || {}).forEach(function (key) {
          img.setAttribute(key, selectors.attrs[key]);
        });
        container.innerHTML = '';
        container.appendChild(img);
      }
      if (initials) {
        initials.remove();
      }
      img.src = src;
    }

    function setPreview(file) {
      if (!file || !file.type || file.type.indexOf('image/') !== 0) {
        return;
      }
      if (filename) {
        filename.textContent = file.name;
      }

      var reader = new FileReader();
      reader.onload = function () {
        setImageIn(preview, {
          image: '[data-profile-preview-image]',
          initials: '[data-profile-preview-initials]',
          attrs: {
            'data-profile-preview-image': '',
            alt: 'Selected profile picture',
          },
        }, reader.result);

        var heroTrigger = document.querySelector('.profile-avatar-trigger');
        if (!heroTrigger) {
          return;
        }
        var heroImg = heroTrigger.querySelector('[data-profile-hero-image]');
        var heroInitials = heroTrigger.querySelector('[data-profile-hero-initials]');
        if (!heroImg) {
          heroImg = document.createElement('img');
          heroImg.className = 'profile-avatar profile-avatar-image';
          heroImg.setAttribute('data-profile-hero-image', '');
          heroImg.alt = '';
          heroImg.width = 64;
          heroImg.height = 64;
          if (heroInitials) {
            heroInitials.replaceWith(heroImg);
          } else {
            heroTrigger.insertBefore(heroImg, heroTrigger.firstChild);
          }
        }
        heroImg.src = reader.result;
      };
      reader.readAsDataURL(file);
    }

    input.addEventListener('change', function () {
      if (input.files && input.files[0]) {
        setPreview(input.files[0]);
      }
    });

    ['dragenter', 'dragover'].forEach(function (eventName) {
      zone.addEventListener(eventName, function (event) {
        event.preventDefault();
        event.stopPropagation();
        zone.classList.add('is-dragover');
      });
    });

    ['dragleave', 'drop'].forEach(function (eventName) {
      zone.addEventListener(eventName, function (event) {
        event.preventDefault();
        event.stopPropagation();
        zone.classList.remove('is-dragover');
      });
    });

    zone.addEventListener('drop', function (event) {
      var files = event.dataTransfer && event.dataTransfer.files;
      if (!files || !files.length) {
        return;
      }
      var file = files[0];
      try {
        var transfer = new DataTransfer();
        transfer.items.add(file);
        input.files = transfer.files;
      } catch (err) {
        // Preview still updates even if assigning files is blocked.
      }
      setPreview(file);
    });
  });
})();
