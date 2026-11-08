# Référence humaine — DISRUPT-002

- Catégorie attendue : `Unknown` ; un timeout n'établit pas à lui seul un problème réseau.
- Sévérité : 3, car une recherche de réaffectation identifiée est bloquée ; aucun impact plus large n'est établi.
- Faits : une recherche a expiré après 10 000 ms et n'a pas renvoyé d'alternative.
- Hypothèses possibles : dépendance lente, surcharge ou problème réseau. Aucune n'est démontrée.
- Résultat attendu : fournir des alternatives si la recherche aboutit ou une erreur claire si elle échoue, sans conclure à l'absence d'alternative.
- Informations manquantes : traces de la dépendance, durée des étapes, fonction en cause et étendue de l'incident.
