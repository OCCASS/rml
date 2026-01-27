(() => {
  const cartRoot = document.querySelector('.cart');
  if (!cartRoot) {
    return;
  }

  const formatter = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });

  const formatCurrency = (value) => `${formatter.format(Number(value || 0))}₽`;

  const getCookie = (name) => {
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (const cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(`${name}=`)) {
        return decodeURIComponent(trimmed.slice(name.length + 1));
      }
    }
    return null;
  };

  const csrfToken =
    getCookie('csrftoken') || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';

  const updateCartCount = (value) => {
    document.querySelectorAll('[data-cart-count]').forEach((node) => {
      node.textContent = value;
    });
  };

  const updateSummary = (totalAmount) => {
    const summary = document.querySelector('[data-cart-total]');
    if (summary) {
      summary.textContent = formatCurrency(totalAmount);
    }
  };

  const ensureEmptyState = () => {
    if (document.querySelector('.cart__item')) {
      return;
    }
    document.querySelector('.cart__items')?.remove();
    document.querySelector('.cart__summary')?.remove();
    if (!document.querySelector('.cart__empty')) {
      const empty = document.createElement('p');
      empty.className = 'cart__empty';
      empty.textContent = 'Корзина пока пуста.';
      cartRoot.appendChild(empty);
    }
  };

  const setItemLoading = (item, loading) => {
    item.dataset.loading = loading ? '1' : '';
    item.querySelectorAll('[data-quantity-action]').forEach((button) => {
      button.disabled = loading;
    });
  };

  const sendRequest = async (url, params = {}) => {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new URLSearchParams({ ...params, csrfmiddlewaretoken: csrfToken }),
    });
    if (!response.ok) {
      throw new Error('Request failed');
    }
    return response.json();
  };

  const applyResponse = (item, data) => {
    if (data?.cart) {
      updateSummary(data.cart.total_amount);
      updateCartCount(data.cart.total_quantity);
    }

    if (data?.removed) {
      item.remove();
      ensureEmptyState();
      return;
    }

    if (data?.item) {
      const quantityNode = item.querySelector('[data-quantity]');
      const totalNode = item.querySelector('[data-item-total]');
      if (quantityNode) {
        quantityNode.textContent = data.item.quantity;
      }
      if (totalNode) {
        totalNode.textContent = formatCurrency(data.item.total_price);
      }
    }
  };

  cartRoot.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-quantity-action]');
    if (!button) {
      return;
    }
    const item = button.closest('[data-item]');
    if (!item || item.dataset.loading === '1') {
      return;
    }

    const action = button.dataset.quantityAction;
    const quantityNode = item.querySelector('[data-quantity]');
    const currentQuantity = Number(quantityNode?.textContent || 0);
    const nextQuantity = action === 'increase' ? currentQuantity + 1 : currentQuantity - 1;

    const addUrl = item.dataset.addUrl;
    const removeUrl = item.dataset.removeUrl;

    setItemLoading(item, true);
    try {
      let data;
      if (nextQuantity <= 0) {
        data = await sendRequest(removeUrl);
      } else {
        data = await sendRequest(addUrl, { quantity: String(nextQuantity), replace: '1' });
      }
      applyResponse(item, data);
    } catch (error) {
      console.error(error);
      alert('Не удалось обновить корзину. Попробуйте еще раз.');
    } finally {
      if (document.body.contains(item)) {
        setItemLoading(item, false);
      }
    }
  });
})();
