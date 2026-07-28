## Description

A clear and concise description of what this PR does.

Use this section for review hints, explanations, or discussion points.

- **Summary of changes:**
- **Reasoning / motivation:**
- **Additional context:**

---

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor / code cleanup
- [ ] Performance improvement
- [ ] CI / tooling change
- [ ] Documentation update
- [ ] Security fix

---

## Related Issues

Closes #

---

## Backend Checklist

- [ ] Models: migrations created and reviewed (`makemigrations` + `migrate`)
- [ ] Serializers: input validation is correct; no sensitive fields exposed
- [ ] Views: correct permission classes applied (`IsAdmin`, `IsShopOwner`, `IsShopOwnerOrAdmin`)
- [ ] URLs: new endpoints registered in `urls.py`
- [ ] All responses use `APIResponse` wrapper
- [ ] No raw SQL or unfiltered querysets exposed to unauthenticated users
- [ ] `manage.py check` passes locally

---

## Screenshots

> **Required for frontend/UI changes.** Paste screenshots or a screen recording showing the visual changes.
> Delete this section for backend-only changes.

---