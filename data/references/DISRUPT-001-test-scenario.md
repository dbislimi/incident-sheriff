# Scénario de test — DISRUPT-001

Ce document décrit le comportement à vérifier pour préparer la génération d'un test. Il sert de référence humaine d'évaluation et ne doit pas être fourni au modèle lors de cette évaluation.

## Situation

Le vol AF123, de CDG à FCO, prévu le 3 novembre 2026 à 10 h UTC, est annulé. La liste des alternatives contient AF456, sur le même trajet, prévu le même jour à 14 h UTC avec deux places disponibles. Pour ce scénario, AF456 est la seule alternative fournie.

## Comportement attendu

Selon les règles métier, AF456 est éligible : le départ et l'arrivée correspondent, son départ est postérieur à celui d'AF123 et il reste au moins une place. Le moteur doit donc proposer AF456.

## Vérification observable

Appeler `findAlternative` avec AF123 et une liste contenant AF456. Vérifier que le `std::optional<Flight>` retourné contient un vol, puis que son `id` vaut `AF456`. L'interface est déclarée dans `cpp/rebooking.hpp`.

Le ticket rapporte qu'aucune alternative n'a été proposée. Les logs indiquent un rejet par le filtre, mais ne prouvent ni la condition exacte de rejet ni la fonction responsable. Le rejet des vols ayant exactement deux places est le défaut pédagogique choisi pour le moteur C++ ; il ne doit pas être présenté comme une cause établie par les logs.
