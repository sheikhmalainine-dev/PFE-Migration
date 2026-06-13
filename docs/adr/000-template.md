# ADR-XXX — [Titre court de la décision]

> **Comment utiliser ce modèle :**
> 1. Copier ce fichier dans `docs/adr/` en le renommant `XXX-titre-court.md` (ex : `001-choix-de-k3s.md`).
> 2. Incrémenter le numéro à chaque nouvel ADR (001, 002, 003…).
> 3. Remplir les sections ci-dessous. Garder court — un ADR fait idéalement **une page**.
> 4. Une fois écrit et acté, un ADR ne se **modifie plus**. Pour changer la décision, créer un nouvel ADR qui remplace l'ancien (`Statut: Remplacé par ADR-XXX`).

---

## Métadonnées

- **Statut :** Proposé | Accepté | Remplacé par ADR-YYY | Déprécié
- **Date :** AAAA-MM-JJ
- **Décideur(s) :** Sheikh
- **Catégorie :** Infrastructure | Orchestration | Réseau | Stockage | Observabilité | Sécurité | Outillage

---

## Contexte

Décrire en 3–5 phrases :
- Quel est le problème à résoudre ?
- Pourquoi faut-il prendre une décision maintenant ?
- Quelles sont les contraintes (techniques, budgétaires, humaines, calendrier) ?

---

## Options considérées

Lister **2 à 4 options** réalistes, avec pour chacune :

### Option A — [nom]
- **Description :** une phrase.
- **Avantages :** points forts pertinents.
- **Inconvénients :** points faibles, coûts cachés.

### Option B — [nom]
- **Description :**
- **Avantages :**
- **Inconvénients :**

### Option C — [nom]
- **Description :**
- **Avantages :**
- **Inconvénients :**

---

## Décision

**L'option retenue est : [nom de l'option].**

(Une ou deux phrases, pas plus.)

---

## Raisons

Pourquoi cette option et pas les autres ? Lister les critères de décision pondérés :

- Critère 1 (ex : empreinte mémoire) → l'option choisie est la meilleure parce que…
- Critère 2 (ex : compatibilité avec l'écosystème K8s) → …
- Critère 3 (ex : facilité d'exploitation pour l'équipe CNASS) → …

---

## Conséquences

### Positives
- ...
- ...

### Négatives ou compromis acceptés
- ...
- ...

### Risques à surveiller
- ...
- ...

---

## Références

- Documentation officielle : [lien]
- Benchmark / article comparatif : [lien]
- Discussion interne / ticket : [lien]

---

# Exemple rempli — à consulter pour référence

> Voici à quoi ressemble un ADR concret, pour comprendre le niveau de détail attendu.

---

## ADR-001 — Choix de K3s comme orchestrateur de conteneurs

**Statut :** Accepté
**Date :** 2026-06-10
**Décideur(s) :** Sheikh
**Catégorie :** Orchestration

### Contexte

La CNASS dispose d'un matériel modeste (serveurs avec 16 à 32 GB de RAM par nœud). L'équipe IT n'a pas d'expertise Kubernetes. Il faut un orchestrateur de conteneurs qui :
- consomme peu de ressources,
- s'installe et se maintient simplement,
- reste compatible avec l'écosystème Kubernetes standard pour ne pas s'enfermer.

### Options considérées

**Option A — Kubernetes standard (kubeadm)**
- Description : la distribution Kubernetes de référence.
- Avantages : standard de l'industrie, documentation abondante, écosystème complet.
- Inconvénients : empreinte mémoire élevée (~2 GB par nœud rien que pour le control-plane), installation et maintenance complexes.

**Option B — K3s**
- Description : distribution Kubernetes légère par Rancher, certifiée CNCF.
- Avantages : binaire unique de ~70 MB, empreinte mémoire ~512 MB, installation en une commande, 100% compatible API K8s.
- Inconvénients : moins de notoriété auprès des décideurs, certains composants remplacés (containerd au lieu de Docker, sqlite par défaut).

**Option C — OpenShift**
- Description : plateforme Kubernetes enrichie par Red Hat.
- Avantages : fonctionnalités avancées (CI/CD intégrée, console web, RBAC fin).
- Inconvénients : licence payante, empreinte ressource très élevée, complexité.

### Décision

**L'option retenue est K3s.**

### Raisons

- **Empreinte mémoire** → K3s utilise ~75% de RAM en moins que kubeadm, critique sur le matériel CNASS.
- **Simplicité d'exploitation** → installation en une commande, l'équipe IT non-spécialiste peut maintenir le cluster.
- **Compatibilité K8s** → l'API est identique, aucun risque de verrouillage technologique (on peut migrer vers kubeadm plus tard sans réécrire les manifestes).
- **Coût** → gratuit et open source, contrairement à OpenShift.

### Conséquences

**Positives :**
- Démarrage rapide du PoC.
- Faible coût d'infrastructure.
- Courbe d'apprentissage douce pour l'équipe CNASS.

**Compromis acceptés :**
- Stockage par défaut en SQLite (acceptable pour le PoC, à remplacer par etcd ou PostgreSQL en production si le cluster grandit).
- containerd au lieu de Docker (transparent pour les utilisateurs, mais à mentionner dans la documentation).

**Risques à surveiller :**
- Si la CNASS adopte massivement K3s, prévoir une montée vers etcd embarqué (mode HA) dès qu'on dépasse 3 nœuds.
- Vérifier que tous les outils tiers utilisés (Argo CD, Cilium, Longhorn) supportent K3s — confirmé pour ces trois.

### Références

- Documentation officielle K3s : https://docs.k3s.io
- Comparaison K3s vs k8s : article CNCF
- ADR-002 — Choix de Talos comme OS pour les nœuds K3s

---

*Modèle créé le : 2026-06-13*