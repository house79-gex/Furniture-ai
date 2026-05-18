# Rendere il repository privato (GitHub)

## Da browser

1. Apri https://github.com/house79-gex/Furniture-ai/settings
2. Scorri fino a **Danger Zone**
3. **Change repository visibility** → **Make private**
4. Conferma digitando `house79-gex/Furniture-ai`

## Da GitHub CLI

```powershell
gh auth login
gh repo edit house79-gex/Furniture-ai --visibility private --accept-visibility-change-consequences
```

## Dopo il passaggio a privato

- I collaboratori vanno aggiunti in **Settings → Collaborators**
- I clone locali con HTTPS continuano a funzionare se sei autenticato
- Per uso solo personale non serve altro
