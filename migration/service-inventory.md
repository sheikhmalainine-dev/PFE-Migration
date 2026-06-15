# Inventaire des services CNASS — Plan de migration

> Ce fichier liste **tous les services informatiques de la CNASS** dans le périmètre de la migration vers Kubernetes.
> Il est le **point de départ** du plan de migration : sans inventaire complet, pas de stratégie réaliste.
> Mise à jour : au fur et à mesure que les informations sont collectées auprès de l'équipe IT CNASS.

---

## 1. Vue d'ensemble

| ID | Service | Type | Criticité | Stratégie | Vague | Statut |
|---|---|---|---|---|---|---|
| SRV-001 | _exemple : Gestion des assurés_ | Web app | Haute | Replatform | 1 | À évaluer |
| SRV-002 | _exemple : Traitement des remboursements_ | Batch | Haute | Refactor | 2 | À évaluer |
| SRV-003 | _exemple : Interface employeurs_ | Web app | Moyenne | Rehost | 1 | À évaluer |
| SRV-004 | _exemple : Reporting interne_ | Web app | Basse | Rehost | 3 | À évaluer |
| SRV-005 | _exemple : Base de données centrale_ | Base de données | Haute | Retain | — | Hors périmètre |
| ... | _à compléter_ | | | | | |

**Légende des statuts :**
- `À évaluer` — service identifié, audit pas encore fait
- `Évalué` — audit fait, stratégie choisie
- `En PoC` — migration en cours sur l'environnement de test
- `Migré` — en production sur Kubernetes
- `Retiré` — décommissionné
- `Hors périmètre` — restera sur l'infrastructure legacy

---

## 2. Stratégies de migration — les 6R adaptés à la conteneurisation

| Stratégie | En clair | Quand l'utiliser |
|---|---|---|
| **Rehost** | Conteneuriser l'application telle quelle (image Docker de l'existant) | Application simple, peu de dépendances, pas de gros refactoring nécessaire |
| **Replatform** | Conteneuriser + adaptations mineures (externaliser la config, ajouter des healthchecks, logs vers stdout) | La majorité des cas — bon compromis effort / bénéfice |
| **Refactor** | Réécrire l'application en cloud-native (12-factor, microservices, stateless) | Application stratégique, dette technique élevée, besoin de scalabilité |
| **Repurchase** | Remplacer par une solution SaaS ou un produit du marché | L'application est commune (CRM, ticketing, etc.) et un produit existant fait mieux |
| **Retire** | Décommissionner | L'application n'est plus utilisée ou redondante avec une autre |
| **Retain** | Garder sur l'infrastructure legacy | Base de données critique, application difficile à conteneuriser (Active Directory, etc.) |

---

## 3. Fiche détaillée par service

> Pour chaque service du tableau §1, copier le modèle ci-dessous et le remplir.

### Modèle — à dupliquer

```markdown
### [SRV-XXX] Nom du service

**Description :** Une phrase expliquant ce que fait le service et qui l'utilise.

**Responsable côté CNASS :** Nom du référent / équipe propriétaire.

#### Caractéristiques techniques
- **Type :** Web app / API / Batch / Service Windows / Base de données / Autre
- **Stack :** Langage, framework, version (ex : .NET 4.7, Java 8, PHP 7.4)
- **OS actuel :** Windows Server XXXX / Linux XXX
- **Hébergement actuel :** Nom de la VM, ressources allouées (vCPU, RAM, disque)

#### Dépendances
- **Bases de données :** lesquelles, où
- **Services internes :** lesquels appelle-t-il, lesquels l'appellent
- **APIs / systèmes externes :** lesquels

#### Criticité et usage
- **Criticité métier :** Haute / Moyenne / Basse
- **Utilisateurs :** combien, quel profil (interne / externe / public)
- **Horaires d'usage :** 24/7 / heures ouvrées / batch nocturne
- **Tolérance à l'indisponibilité :** quelques minutes / quelques heures / une journée

#### Décision de migration
- **Stratégie choisie :** Rehost / Replatform / Refactor / Repurchase / Retire / Retain
- **Justification :** pourquoi cette stratégie
- **Vague de migration :** 1 (pilote) / 2 (essentiels) / 3 (reste)
- **Effort estimé :** Faible (< 1 semaine) / Moyen (1–4 semaines) / Élevé (> 1 mois)

#### Risques et points de vigilance
- ...
- ...

#### Notes
- ...
```

---

## 4. Exemple rempli — pour référence

### [SRV-001] Gestion des assurés

**Description :** Application web permettant aux agents CNASS de créer, modifier et consulter les dossiers des assurés sociaux.

**Responsable côté CNASS :** _à compléter_

#### Caractéristiques techniques
- **Type :** Web app
- **Stack :** _à compléter (ex : ASP.NET MVC 5, C#, .NET Framework 4.7)_
- **OS actuel :** _à compléter (ex : Windows Server 2016)_
- **Hébergement actuel :** _à compléter (ex : VM "srv-assures-01", 4 vCPU, 8 GB RAM, 100 GB disque)_

#### Dépendances
- **Bases de données :** _à compléter_
- **Services internes :** _à compléter_
- **APIs externes :** _à compléter_

#### Criticité et usage
- **Criticité métier :** Haute
- **Utilisateurs :** _à compléter_ agents internes
- **Horaires d'usage :** heures ouvrées
- **Tolérance à l'indisponibilité :** quelques heures

#### Décision de migration
- **Stratégie choisie :** _à confirmer après audit — probablement Replatform_
- **Justification :** _à compléter_
- **Vague de migration :** _à définir_
- **Effort estimé :** _à estimer_

#### Risques et points de vigilance
- Application .NET classique — nécessitera Windows containers ou portage vers .NET 6+
- Couplage probable avec la base de données centrale

#### Notes
- À discuter avec le responsable applicatif lors de l'audit.

---

## 5. Questions à poser à l'équipe IT CNASS

> Checklist à remplir progressivement, en discutant avec les responsables applicatifs et l'équipe infrastructure.

### Inventaire de base
- [ ] Quelle est la liste exhaustive des applications hébergées sur l'infrastructure KVM ?
- [ ] Pour chacune, quel est le serveur (VM) qui l'héberge ?
- [ ] Quelle est la taille (vCPU, RAM, disque) de chaque VM ?
- [ ] Qui est le référent métier de chaque application ?
- [ ] Quelles applications sont encore activement utilisées ? (Repérer celles à retirer.)

### Technique
- [ ] Pour chaque app : langage, framework, version
- [ ] OS : Windows ou Linux, quelle version
- [ ] Mode de déploiement actuel (manuel, script, MSI, etc.)
- [ ] Logs : où sont-ils écrits ? Comment sont-ils consultés ?
- [ ] Configuration : dans des fichiers ? Hardcodée ? Variables d'environnement ?

### Dépendances et données
- [ ] Quelles bases de données existent ? Sur quel SGBD ?
- [ ] Quelle application utilise quelle base ?
- [ ] Y a-t-il des fichiers partagés (uploads, documents) ? Où sont-ils stockés ?
- [ ] Y a-t-il des intégrations avec des systèmes externes (banques, sécurité sociale, etc.) ?

### Opérationnel
- [ ] Quelle est la criticité de chaque application pour la CNASS ?
- [ ] Combien d'utilisateurs simultanés en pic ?
- [ ] Y a-t-il des batchs nocturnes ? Quels sont leurs horaires ?
- [ ] Quelles sont les plages de maintenance acceptables ?

### Sécurité et conformité
- [ ] Y a-t-il des contraintes réglementaires (santé, données personnelles) ?
- [ ] Quelle est la politique de sauvegarde actuelle ?
- [ ] Y a-t-il un plan de reprise d'activité (PRA) ?

---

## 6. Prochaines actions

1. **Cette semaine :** lister au moins 5 services principaux dans le tableau §1 (même partiellement).
2. **Semaine suivante :** prendre rendez-vous avec un référent applicatif pour remplir la fiche détaillée du premier service prioritaire.
3. **À terme :** une fois l'inventaire complet, écrire `migration/strategy.md` qui consolide les stratégies en un plan unifié.

---

*Dernière mise à jour : 2026-06-13*