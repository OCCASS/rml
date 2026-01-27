(() => {
  const input = document.querySelector('input[name="phone"]');
  if (!input) {
    return;
  }

  const normalizeDigits = (value) => {
    const digits = String(value || '').replace(/\D/g, '');
    if (!digits) {
      return '';
    }
    let normalized = digits;
    if (digits[0] === '8') {
      normalized = `7${digits.slice(1)}`;
    } else if (digits[0] === '9') {
      normalized = `7${digits}`;
    }
    return normalized.slice(0, 11);
  };

  const formatPhone = (digits) => {
    if (!digits) {
      return '';
    }
    const rest = digits.slice(1);
    if (!rest) {
      return '+7';
    }
    if (rest.length < 3) {
      return `+7 ${rest}`;
    }
    let formatted = `+7 (${rest.slice(0, 3)}`;
    if (rest.length === 3) {
      return formatted;
    }
    formatted += `) ${rest.slice(3, 6)}`;
    if (rest.length <= 6) {
      return formatted;
    }
    formatted += `-${rest.slice(6, 8)}`;
    if (rest.length <= 8) {
      return formatted;
    }
    return `${formatted}-${rest.slice(8, 10)}`;
  };

  const applyMask = () => {
    const normalized = normalizeDigits(input.value);
    input.value = formatPhone(normalized);
    input.dataset.raw = normalized;
  };

  input.addEventListener('input', applyMask);
  input.addEventListener('paste', () => {
    setTimeout(applyMask, 0);
  });
  input.addEventListener('blur', () => {
    const normalized = normalizeDigits(input.value);
    if (!normalized) {
      input.value = '';
      input.dataset.raw = '';
      return;
    }
    input.value = formatPhone(normalized);
    input.dataset.raw = normalized;
  });

  applyMask();
})();
