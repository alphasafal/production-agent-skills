const db = require("./knex");

async function findCustomerByEmail(email) {
  return db("customers")
    .select("id", "name", "email", "created_at")
    .where({ email })
    .first();
}

module.exports = { findCustomerByEmail };
