import React from 'react';
import moment from 'moment';
import PaymentForm from './PaymentForm';
import './styles.css';

export default function CheckoutModal({ isOpen, onClose, cart, onPaid }) {
  if (!isOpen) return null;

  const item = cart.items[0];
  const deliveryDate = moment().add(3, 'days').format('ddd, D MMM');

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2>Checkout</h2>
          <div className="modal-close" onClick={onClose}>
            ✕ Close
          </div>
        </div>

        <div className="order-summary">
          <img className="product-image" src={item.imageUrl} />
          <div className="product-info">
            <h3>{item.name}</h3>
            <p className="price">
              ₹{item.price.toLocaleString('en-IN')} × {item.quantity}
            </p>
            <p className="delivery">
              <img
                className="icon"
                src="/icons/truck.svg"
                alt=""
                aria-hidden="true"
              />
              Arrives by {deliveryDate}
            </p>
          </div>
        </div>

        <PaymentForm total={cart.total} onPaid={onPaid} />

        <p className="terms">
          By paying you agree to our Terms of Sale and Refund Policy.
          Payments are processed securely.
        </p>
      </div>
    </div>
  );
}
