// ═══════════════════════════════════════════════════════════
// GyanUday University — UX Enhancements JavaScript
// ═══════════════════════════════════════════════════════════

// ─────────────────────────────────────────────
// DARK MODE TOGGLE
// ─────────────────────────────────────────────
class DarkModeToggle {
  constructor() {
    this.STORAGE_KEY = 'gyan-uday-dark-mode';
    this.init();
  }

  init() {
    this.loadTheme();
    this.createToggleButton();
    this.observeSystemTheme();
  }

  loadTheme() {
    const saved = localStorage.getItem(this.STORAGE_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (saved !== null) {
      this.setTheme(saved === 'true');
    } else {
      this.setTheme(prefersDark);
    }
  }

  setTheme(isDark) {
    if (isDark) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem(this.STORAGE_KEY, isDark);
  }

  toggle() {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem(this.STORAGE_KEY, isDark);
  }

  observeSystemTheme() {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (localStorage.getItem(this.STORAGE_KEY) === null) {
        this.setTheme(e.matches);
      }
    });
  }

  createToggleButton() {
    const btn = document.createElement('button');
    btn.id = 'dark-mode-toggle';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      </svg>
    `;
    btn.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 999;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: 1px solid var(--color-border);
      background: var(--color-surface);
      color: var(--color-text);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    `;
    
    btn.addEventListener('mouseenter', () => {
      btn.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
      btn.style.transform = 'scale(1.1)';
    });
    
    btn.addEventListener('mouseleave', () => {
      btn.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
      btn.style.transform = 'scale(1)';
    });
    
    btn.addEventListener('click', () => this.toggle());
    document.body.appendChild(btn);
  }
}

// ─────────────────────────────────────────────
// TOAST NOTIFICATION SYSTEM
// ─────────────────────────────────────────────
class ToastManager {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    this.container = document.createElement('div');
    this.container.className = 'toast-container';
    document.body.appendChild(this.container);
  }

  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };

    toast.innerHTML = `
      <div class="toast-icon">${icons[type] || '•'}</div>
      <div class="toast-message">${message}</div>
      <button class="toast-close" aria-label="Close notification">×</button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => this.remove(toast));

    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => this.remove(toast), duration);
    }

    return toast;
  }

  remove(toast) {
    toast.style.animation = 'fadeOut 0.2s ease-out';
    setTimeout(() => toast.remove(), 200);
  }

  success(message, duration) {
    return this.show(message, 'success', duration);
  }

  error(message, duration) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration) {
    return this.show(message, 'info', duration);
  }
}

// ─────────────────────────────────────────────
// FORM VALIDATION
// ─────────────────────────────────────────────
class FormValidator {
  constructor(form) {
    this.form = form;
    this.errors = {};
    this.init();
  }

  init() {
    this.form.addEventListener('submit', (e) => this.validate(e));
    
    // Real-time validation
    const inputs = this.form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      input.addEventListener('blur', () => this.validateField(input));
    });
  }

  validate(e) {
    e.preventDefault();
    this.errors = {};
    
    const formData = new FormData(this.form);
    let isValid = true;

    formData.forEach((value, name) => {
      const input = this.form.elements[name];
      if (!this.validateField(input)) {
        isValid = false;
      }
    });

    if (isValid) {
      this.form.submit();
    }
  }

  validateField(input) {
    const group = input.closest('.form-group');
    const error = group ? group.querySelector('.form-error') : null;
    let isValid = true;
    let message = '';

    if (input.required && !input.value.trim()) {
      isValid = false;
      message = `${input.name} is required`;
    } else if (input.type === 'email' && !this.isValidEmail(input.value)) {
      isValid = false;
      message = 'Please enter a valid email';
    } else if (input.type === 'url' && !this.isValidUrl(input.value)) {
      isValid = false;
      message = 'Please enter a valid URL';
    } else if (input.minLength && input.value.length < input.minLength) {
      isValid = false;
      message = `Minimum ${input.minLength} characters required`;
    } else if (input.pattern && !new RegExp(input.pattern).test(input.value)) {
      isValid = false;
      message = 'Invalid format';
    }

    if (!isValid) {
      input.classList.add('is-invalid');
      if (error) error.textContent = message;
    } else {
      input.classList.remove('is-invalid');
      if (error) error.textContent = '';
    }

    return isValid;
  }

  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }
}

// ─────────────────────────────────────────────
// DROPDOWN MENU
// ─────────────────────────────────────────────
class DropdownMenu {
  constructor(trigger, menu) {
    this.trigger = trigger;
    this.menu = menu;
    this.init();
  }

  init() {
    this.trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggle();
    });

    document.addEventListener('click', () => this.close());
    
    this.menu.addEventListener('click', (e) => {
      if (e.target.classList.contains('dropdown-item')) {
        this.close();
      }
    });
  }

  toggle() {
    this.menu.classList.toggle('active');
  }

  open() {
    this.menu.classList.add('active');
  }

  close() {
    this.menu.classList.remove('active');
  }
}

// ─────────────────────────────────────────────
// MODAL DIALOG
// ─────────────────────────────────────────────
class Modal {
  constructor(modalElement) {
    this.modal = modalElement;
    this.overlay = modalElement.closest('.modal-overlay');
    this.init();
  }

  init() {
    const closeBtn = this.modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }

    if (this.overlay) {
      this.overlay.addEventListener('click', (e) => {
        if (e.target === this.overlay) this.close();
      });
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });
  }

  open() {
    if (this.overlay) this.overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  close() {
    if (this.overlay) this.overlay.style.display = 'none';
    document.body.style.overflow = '';
  }

  isOpen() {
    return this.overlay && this.overlay.style.display === 'flex';
  }
}

// ─────────────────────────────────────────────
// SEARCH FUNCTIONALITY
// ─────────────────────────────────────────────
class TableSearch {
  constructor(tableSelector, searchSelector) {
    this.table = document.querySelector(tableSelector);
    this.search = document.querySelector(searchSelector);
    this.rows = [];
    this.init();
  }

  init() {
    if (!this.table || !this.search) return;

    this.rows = Array.from(this.table.querySelectorAll('tbody tr'));
    this.search.addEventListener('input', (e) => this.filterRows(e.target.value));
  }

  filterRows(query) {
    const term = query.toLowerCase();

    this.rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(term) ? '' : 'none';
    });

    // Show empty state if no results
    const visibleRows = this.rows.filter(row => row.style.display !== 'none');
    if (visibleRows.length === 0) {
      this.showEmptyState();
    } else {
      this.hideEmptyState();
    }
  }

  showEmptyState() {
    let emptyState = this.table.querySelector('.empty-state-row');
    if (!emptyState) {
      emptyState = document.createElement('tr');
      emptyState.className = 'empty-state-row';
      emptyState.innerHTML = `
        <td colspan="100%" style="text-align: center; padding: 40px;">
          <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <div class="empty-state-title">No results found</div>
            <div class="empty-state-text">Try adjusting your search criteria</div>
          </div>
        </td>
      `;
      this.table.querySelector('tbody').appendChild(emptyState);
    }
  }

  hideEmptyState() {
    const emptyState = this.table.querySelector('.empty-state-row');
    if (emptyState) emptyState.remove();
  }
}

// ─────────────────────────────────────────────
// LAZY LOADING IMAGES
// ─────────────────────────────────────────────
class LazyLoadImages {
  constructor() {
    this.init();
  }

  init() {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            observer.unobserve(img);
          }
        });
      });

      document.querySelectorAll('img.lazy').forEach(img => observer.observe(img));
    }
  }
}

// ─────────────────────────────────────────────
// KEYBOARD SHORTCUTS
// ─────────────────────────────────────────────
class KeyboardShortcuts {
  constructor() {
    this.shortcuts = {
      'ctrl+k': () => this.focusSearch(),
      'ctrl+shift+p': () => this.togglePalette(),
      'escape': () => this.closeModals(),
    };
    this.init();
  }

  init() {
    document.addEventListener('keydown', (e) => {
      const key = this.getKeyCombo(e);
      if (this.shortcuts[key]) {
        e.preventDefault();
        this.shortcuts[key]();
      }
    });
  }

  getKeyCombo(e) {
    let key = e.key.toLowerCase();
    if (e.ctrlKey) key = 'ctrl+' + key;
    if (e.shiftKey) key = 'shift+' + key;
    if (e.altKey) key = 'alt+' + key;
    return key;
  }

  focusSearch() {
    const search = document.querySelector('.search-box input');
    if (search) search.focus();
  }

  togglePalette() {
    console.log('Command palette opened');
  }

  closeModals() {
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      if (overlay.style.display === 'flex') {
        overlay.style.display = 'none';
      }
    });
  }
}

// ─────────────────────────────────────────────
// EXPORT DATA
// ─────────────────────────────────────────────
class DataExport {
  static exportToCSV(tableSelector, filename = 'export.csv') {
    const table = document.querySelector(tableSelector);
    if (!table) return;

    let csv = [];
    
    // Headers
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    csv.push(headers.join(','));

    // Rows
    table.querySelectorAll('tbody tr').forEach(row => {
      const cells = Array.from(row.querySelectorAll('td')).map(td => {
        const text = td.textContent.trim();
        return `"${text.replace(/"/g, '""')}"`;
      });
      csv.push(cells.join(','));
    });

    this.downloadFile(csv.join('\n'), filename, 'text/csv');
  }

  static downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  }
}

// ─────────────────────────────────────────────
// INITIALIZATION
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Initialize dark mode
  new DarkModeToggle();

  // Initialize toast system (globally available)
  window.toast = new ToastManager();

  // Initialize form validators
  document.querySelectorAll('form').forEach(form => {
    if (form.dataset.validate !== 'false') {
      new FormValidator(form);
    }
  });

  // Initialize keyboard shortcuts
  new KeyboardShortcuts();

  // Initialize lazy loading
  new LazyLoadImages();

  // Initialize dropdowns
  document.querySelectorAll('.dropdown-menu').forEach(menu => {
    const trigger = menu.previousElementSibling;
    if (trigger) new DropdownMenu(trigger, menu);
  });

  // Initialize modals
  document.querySelectorAll('.modal').forEach(modal => {
    new Modal(modal);
  });

  // Make toast globally available
  console.log('✓ GyanUday UX Enhancements loaded');
});
