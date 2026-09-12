# Security Review Checklist

Check each against the actual diff — don't mark clear unless verified.

## Input handling
- [ ] User-controlled input reaching a SQL query is parameterized, not
      string-concatenated (SQL injection).
- [ ] User-controlled input rendered into HTML is escaped or the framework's
      auto-escaping isn't bypassed (`dangerouslySetInnerHTML`, `| safe`,
      `Markup()`, raw template interpolation) (XSS).
- [ ] User-controlled input used in a shell command, file path, or
      deserialization call is validated/sanitized (command injection, path
      traversal, insecure deserialization).
- [ ] File uploads validate type/size and don't trust client-provided
      content-type or filename.

## AuthN/AuthZ
- [ ] New endpoints/routes actually enforce the authentication/authorization
      check — verify the middleware/decorator is present, don't assume from
      a similar existing route.
- [ ] Object-level authorization is checked (a user can't access another
      user's resource by guessing/incrementing an ID — IDOR).
- [ ] Privilege checks happen server-side, not only in client-side UI logic.

## Secrets and sensitive data
- [ ] No hard-coded credentials, API keys, or tokens in the diff.
- [ ] Sensitive data (passwords, tokens, PII) isn't logged.
- [ ] New secrets are read from the existing secrets-management mechanism,
      not a new ad-hoc env var pattern.

## Dependencies
- [ ] New third-party dependency is from a maintained, reputable source —
      flag as LIKELY RISK if unfamiliar and security-sensitive (auth,
      crypto, parsing).

## Cryptography
- [ ] No custom crypto implementation in place of a vetted library.
- [ ] Passwords are hashed with a modern algorithm (bcrypt/argon2/scrypt),
      never plain hashing (MD5/SHA*) or plaintext.
