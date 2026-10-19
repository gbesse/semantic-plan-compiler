# Semantic Plan Compiler

[English](README.en.md) · [Español](README.es.md)

**Compiler des décisions fermées en calculs exacts, questions ciblées, revue humaine et tables SQLite traçables.**

Un contrat JSON déclare les colonnes nécessaires, les choix autorisés et les dépendances. Le compilateur valide le graphe, calcule les montants en code, partage les questions identiques et regroupe celles qui utilisent exactement le même contexte. Un changement de ligne ou de politique invalide le travail concerné ; une confiance insuffisante bloque les décisions dépendantes.

## Essayer sans clé

Python 3.11+ ; la démo utilise un fournisseur fictif explicite.

```sh
git clone https://github.com/gbesse/semantic-plan-compiler
cd semantic-plan-compiler
python3 -m semantic_plan serve --lang fr
```

Ouvrir `http://127.0.0.1:8774/?lang=fr`. Les deux exécuteurs fonctionnent réellement sur quatre demandes synthétiques : le naïf fait un appel par cellule sémantique active, sans cache ni regroupement ; le compilé partage les contextes et les questions communes. Les nombres ne sont pas des animations.

| Passage du fournisseur fictif | Appels | Questions |
| ----------------------------- | -----: | --------: |
| Naïf exécuté                  |     15 |        15 |
| Compilé, premier passage      |      4 |         6 |
| Même entrée, cache chaud      |      0 |         0 |
| Un message modifié            |      2 |         3 |
| Nouvelle version de politique |      4 |         6 |
| Confiance fictive 0,6         |      2 |         4 |

Le dernier cas exige la revue et bloque les quatre routes dépendantes ; aucune route n’est silencieusement inventée. Les traces exposent les colonnes envoyées et les questions exactes. Le SQL affiché est réellement exécuté sur les décisions matérialisées. L’export JSON contient les deux plans, les résultats, la provenance et le contrat d’entrée.

![Plan](docs/preview-fr.png)

```sh
python3 -m semantic_plan demo --lang fr
python3 -m semantic_plan run semantic_plan/examples/fr.json .local/decisions.sqlite
python3 -m semantic_plan plan contrat.json
python3 -m semantic_plan query .local/decisions.sqlite requete.sql
```

Créer `.local/` avant de choisir ce chemin. `run` utilise le fournisseur fictif ; `live` est la commande payante explicite. `pip install .` fournit aussi `semantic-plan`. UI, erreurs, contrats et exemples FR/EN/ES ; le compilateur ne traduit pas les données utilisateur.

## Contrats et cache

Deux types de nœuds dans cette alpha : `subtract`, soustraction exacte de deux colonnes entières, et `choice`, choix fermé avec instructions et descriptions. Les dépendances forment un DAG ; `when` conditionne une décision à un choix parent déclaré. Champs inconnus, cycles, colonnes manquantes et types incohérents sont refusés.

Le plan fourni calcule `amount_due`, classe le sujet, réutilise ce jugement pour `topic_copy`, classe l’urgence et choisit une route uniquement pour les demandes de facture. `customer_tier` est envoyé seulement à la route ; `unused_private_note` n’est jamais envoyé. Les réponses partagées gardent une provenance par ligne.

Une entrée de cache correspond à **la requête entière** : fournisseur, modèle épinglé, version de politique, état projeté et lot complet de questions. Modifier une question invalide aussi ses sœurs du même lot : un modèle pourrait dépendre de leur présence. Les fournisseurs fictifs et réels ont des espaces distincts ; aucun résultat fictif ne devient un résultat Jev réel. Le seuil de revue est réappliqué localement, sans prétendre être calibré. Les réponses erronées ou mal formées ne sont pas cachées.

Les budgets bornent tentatives d’appel, questions envoyées et caractères de requête. Les tokens sont rapportés **après réponse**, pas prédits comme une garantie. Une erreur fournisseur peut avoir été facturée : `usage_complete: false` le signale. Les réponses déjà valides peuvent être mises en cache avant un épuisement de budget ; le rapport conserve les cellules non décidées. Pas de relance automatique.

Tables SQLite `runs`, `decisions`, `cache` ; les valeurs exactes sont stockées comme texte pour éviter un débordement entier SQLite. `query` est en lecture seule, avec fonctions autorisées, borne d’instructions et limite de lignes. La base contient les décisions et leurs contextes projetés ; elle doit être traitée comme une donnée locale privée.

## Appeler Jev explicitement

```sh
pip install .
mkdir -p .local
# Fournir TYPESAFE_API_KEY dans l’environnement ; ne jamais la mettre dans le contrat.
python3 -m semantic_plan live semantic_plan/examples/fr.json .local/live.sqlite
```

Endpoint fixe `https://api.typesafe.ai/v1/systemone`, modèle `jev-1.13.0`, TLS vérifié, timeout 30 s, aucune redirection ou relance. La CLI limite ce passage à quatre appels et six questions. Un contrat plus grand peut rester à revoir ; la bibliothèque `execute` expose les budgets. [Documentation TypeSafe](https://docs.typesafe.ai/primitives/choice). Aucun appel payant depuis l’interface.

[L’essai réel](docs/live-jev-evidence.json) sur les quatre demandes synthétiques françaises a terminé avec **quatre appels, six questions, 1 768 tokens d’entrée et 228 de sortie**. Cela valide l’intégration et la matérialisation, pas une qualité de classification générale. Aucun benchmark naïf/compressé Jev sur corpus humain n’a été effectué. Projet indépendant, sans affiliation à TypeSafe AI.

## Existant et limites

[LOTUS](https://lotus-ai.readthedocs.io/en/latest/core_concepts.html) et [Palimpzest](https://github.com/mitdbg/palimpzest) proposent déjà des opérateurs sémantiques et des optimisations. Ce projet est un **petit compilateur de contrats fermés vérifiables**, pas leur remplacement ni un backend intégré validé. L’intérêt est la chaîne contrat → contexte exact → budget → abstention → provenance SQL, avec un exemple installable.

Le cache, les sous-expressions communes et les lots réutilisent des jugements ; ils ne conservent pas des échantillons stochastiques indépendants. Les résultats équivalents des deux plans sont vérifiés avec le fournisseur fictif seulement. Réduire le nombre d’appels ne prouve ni qualité identique, ni gain de latence, ni supériorité SOTA. Seuil 0,8 illustratif, sans calibration humaine. Pas de génération libre, jointure sémantique générale, distillation, agent outillé ou déploiement de production.

## Vérifier

```sh
python3 -m unittest discover -s tests -v
npm ci
npx playwright install chromium
npm run test:browser
npm run format:check
```

Dix-sept tests : graphe, budgets, cache complet et namespaces, invalidation par ligne/politique/lot, erreur fournisseur, grande arithmétique exacte, revue et SQL en lecture seule. Le naïf fait quinze vrais appels au fournisseur fictif et produit les mêmes valeurs/catégories que le compilé sur cet exercice. Navigateur FR/EN/ES : cinq modes, SQL, export, protection de `.env` et mobile. CI Python 3.11/3.12 et roue hors sources. MIT ; alpha publique.
