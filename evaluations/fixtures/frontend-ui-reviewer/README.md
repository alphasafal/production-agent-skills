# checkout-modal

New one-step checkout for the storefront. The cart page opens
`CheckoutModal` over the product listing; the customer pays without leaving
the page.

## Files

| File | What it is |
|---|---|
| `CheckoutModal.jsx` | The dialog: order summary for the first cart item, delivery estimate, payment form, terms |
| `PaymentForm.jsx` | Card details form; calls `chargeCard` from `./api` and hands the receipt to `onPaid` |
| `styles.css` | Styles for both components; design tokens live in `:root` |

`./api` is not included. `chargeCard(payload)` resolves with a receipt or
rejects with an error; a charge takes 1-4 seconds on a normal connection.

## Usage

```jsx
<CheckoutModal
  isOpen={showCheckout}
  onClose={() => setShowCheckout(false)}
  cart={cart}            // { items: [{ name, imageUrl, price, quantity }], total }
  onPaid={(receipt) => router.push(`/orders/${receipt.orderId}`)}
/>
```

Most storefront traffic is mobile (about 70%, median viewport 390px wide).
The rest of the app uses React 18 and is bundled with Vite.
