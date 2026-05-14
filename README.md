# envpatch

> Python utility to diff and merge .env files across environments without leaking secrets

---

## Installation

```bash
npm install -g envpatch
```

Or use it directly with npx:

```bash
npx envpatch
```

---

## Usage

Compare two `.env` files and see what changed — without exposing secret values:

```bash
# Diff two env files
npx envpatch diff .env.staging .env.production

# Merge changes from one env into another
npx envpatch merge .env.example .env.local --output .env.merged
```

**Example output:**

```
~ DATABASE_URL   [value changed]
+ NEW_FEATURE_FLAG
- DEPRECATED_KEY
= API_VERSION    [unchanged]
```

Keys are shown, but secret values are masked by default. Use `--reveal` only in safe contexts.

---

## Options

| Flag | Description |
|------|-------------|
| `--reveal` | Show actual values in diff output |
| `--output` | Write merged result to a file |
| `--quiet` | Suppress unchanged keys from output |

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## License

[MIT](LICENSE)