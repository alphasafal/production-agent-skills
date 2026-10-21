import React, { useState } from 'react';
import _ from 'lodash';
import { chargeCard } from './api';

const EMPTY = { name: '', email: '', card: '', expiry: '', cvc: '' };

export default function PaymentForm({ total, onPaid }) {
  const [form, setForm] = useState(EMPTY);
  const [saveCard, setSaveCard] = useState(false);
  const [error, setError] = useState(null);

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handlePay() {
    setError(null);
    try {
      const receipt = await chargeCard({
        ...form,
        card: _.trim(form.card),
        amount: total,
        saveCard,
      });
      onPaid(receipt);
    } catch (err) {
      setForm(EMPTY);
      setError('Payment failed. Please try again.');
    }
  }

  return (
    <form className="payment-form" onSubmit={(e) => e.preventDefault()}>
      <input
        type="text"
        placeholder="Name on card"
        value={form.name}
        onChange={update('name')}
      />
      <input
        type="email"
        placeholder="Email for receipt"
        value={form.email}
        onChange={update('email')}
      />
      <input
        type="text"
        placeholder="Card number"
        value={form.card}
        onChange={update('card')}
      />
      <div className="row">
        <input
          type="text"
          placeholder="MM/YY"
          value={form.expiry}
          onChange={update('expiry')}
        />
        <input
          type="text"
          placeholder="CVC"
          value={form.cvc}
          onChange={update('cvc')}
        />
      </div>

      <div className="checkbox-row">
        <input
          id="save-card"
          type="checkbox"
          checked={saveCard}
          onChange={(e) => setSaveCard(e.target.checked)}
        />
        <label htmlFor="save-card">Save this card for faster checkout</label>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="pay-button" onClick={handlePay}>
        Pay ₹{total.toLocaleString('en-IN')}
      </div>
    </form>
  );
}
