# Référence humaine — DISRUPT-001

- Catégorie attendue : `BusinessLogic`.
- Sévérité : 3, car une demande de réaffectation est bloquée ; aucun impact plus large n'est établi.
- Faits : AF123 est annulé ; AF456 assure le même trajet plus tard avec deux places ; les logs indiquent son rejet par le filtre et un résultat sans alternative.
- Hypothèse : le filtre d'éligibilité applique incorrectement une condition. Les logs ne précisent ni la condition exacte ni la fonction C++ responsable.
- Résultat attendu : proposer AF456.
- Informations manquantes : condition précise de rejet, nom de la fonction et étendue de l'impact.
- Piste de défaut pour l'étape C++ : une condition rejette à tort les vols ayant deux places. Ce choix pédagogique n'est pas prouvé par les logs.
