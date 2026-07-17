Pour étudier les **decorators en Python**, commencez par réviser les bases des **fonctions** et des **lambda functions**. Voici les points clés :

### Concepts fondamentaux
- **Decorators** : Fonctions qui modifient le comportement d'autres fonctions sans les modifier directement.
- **Wrappers** : Fonctions internes créées par les decorators pour encapsuler le code.

### Erreurs courantes
- Ne pas comprendre l'ordre d'exécution des décorateurs (la fonction décorée est appelée après le décorateur).
- Utiliser des décorateurs sans maîtriser les **fonctions imbriquées**.

### Exercice pratique
Créez un décorateur qui mesure et affiche le temps d'exécution d'une fonction. Par exemple :
```python
import time
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.log(time.time() - start)
        print(f"Temps d'exécution : {end} secondes")
        return result
    return wrapper

@timer
def example():
    time.sleep(1)

example()
```

Commencez par ces bases pour mieux saisir les décorateurs !