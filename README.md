# PFE — Migration de la CNASS vers Kubernetes

> Migration complète de l'infrastructure de la **Caisse Nationale d'Assurance Santé (CNASS)** d'un environnement legacy KVM / Windows Server vers une architecture conteneurisée orchestrée par Kubernetes.

**État :** 🔧 En cours · **Soutenance :** Juillet 2026 · **Auteur :** Sheikh — Master, dernière année

---

## 1. Contexte

Ce projet constitue le **Projet de Fin d'Études (PFE)** d'un Master en informatique, réalisé dans le cadre d'un stage DevOps / SRE à la **CNASS**.

L'infrastructure actuelle de la CNASS repose sur :
- des hyperviseurs **KVM** hébergeant des **machines virtuelles Windows Server**,
- un provisionnement **manuel**, sans automatisation,
- une **observabilité limitée** (peu de métriques, pas de tableaux de bord centralisés),
- **aucune couche d'orchestration** entre les serveurs.

L'équipe IT de la CNASS n'étant **pas spécialiste des technologies cloud-native**, ce projet doit accomplir deux missions à la fois :

1. **Démontrer techniquement** qu'une architecture conteneurisée est viable et supérieure sur des critères mesurables.
2. **Communiquer clairement** — en langage simple, avec des chiffres et des schémas — aux décideurs qui ne lisent pas la documentation Kubernetes.

---

## 2. Problématique

L'infrastructure actuelle présente trois douleurs concrètes :

- **Empreinte lourde** — chaque application nécessite une VM complète, consommant de la RAM et du CPU disproportionnés par rapport à la charge réelle.
- **Reprise lente** — en cas de panne d'un service, la récupération est manuelle et le **MTTR** (temps moyen de rétablissement) est élevé.
- **Pas d'élasticité** — les pics de charge sont absorbés par du surdimensionnement, jamais par de la mise à l'échelle automatique.

Ce projet teste l'hypothèse qu'une architecture basée sur **Kubernetes (K3s)** — choisi pour sa faible empreinte — résout ces trois douleurs, sans nécessiter l'adoption d'un cloud public ni l'investissement dans des plateformes propriétaires coûteuses.

---

## 3. Objectifs

- Produire un **plan de migration complet** que la CNASS pourra exécuter après la fin du stage (évaluation → PoC → pilote → déploiement progressif).
- Construire un **laboratoire reproductible** comparant l'environnement legacy KVM, Docker et K3s sur le même matériel.
- Exécuter trois scénarios de test sur chaque environnement et collecter des **métriques quantitatives**.
- Rédiger le **rapport académique** et préparer la **soutenance**.

---

## 4. Approche — un cadre de migration validé par une PoC

Ce projet n'est **pas seulement** une comparaison entre environnements. La comparaison est le **chapitre de justification** d'un travail plus large : la définition d'un cadre de migration applicable à l'ensemble des services CNASS.

```
┌─────────────────────────────────────────────────────────────┐
│  Inventaire des services CNASS  →  Stratégie de migration   │
│                          │                                  │
│                          ▼                                  │
│            Preuve de concept (PoC) sur services pilotes     │
│                          │                                  │
│                          ▼                                  │
│        Plan de déploiement par vagues (post-PFE)            │
└─────────────────────────────────────────────────────────────┘
```

### Les trois scénarios de la PoC

| Scénario | Mesure | Pourquoi c'est important |
|---|---|---|
| **1. Empreinte au repos** | RAM / CPU à vide | Coût de base par environnement |
| **2. Crash / MTTR** | Temps entre la panne et le rétablissement | Résilience sans intervention humaine |
| **3. Charge en rafale + autoscaling** | Taux d'erreur HTTP, latence, réaction de la mise à l'échelle | Comportement sous trafic réel |

Une **API Flask** instrumentée avec des métriques Prometheus — et dotée d'endpoints provoquant intentionnellement des fuites mémoire et de la charge CPU — est utilisée comme charge de travail dans tous les scénarios. Les comparaisons sont ainsi équivalentes.

L'observabilité est centralisée sur une **VM observateur** dédiée, exécutant Prometheus + Grafana, qui scrape les exporters spécifiques à chaque environnement (`windows_exporter`, `node_exporter`, `cAdvisor`, métriques kubelet) et génère la charge avec **k6**.

---

## 5. Architecture du laboratoire

```
                    ┌────────────────────────────────┐
                    │   VM Observateur               │
                    │   Prometheus · Grafana · k6    │◀── charge + scrape
                    └────────────────────────────────┘
                                    ▲
                ┌───────────────────┼───────────────────┐
                │                   │                   │
        ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
        │ KVM legacy    │   │ Hôte Docker   │   │ Cluster K3s   │
        │ VM Win Server │   │ Ubuntu 24     │   │ Talos / K3s   │
        │ + API Flask   │   │ + API Flask   │   │ + API Flask   │
        └───────────────┘   └───────────────┘   └───────────────┘
                          un seul hôte physique
```

Schémas détaillés : [`docs/diagrams/`](docs/diagrams/)

---

## 6. Structure du dépôt

```
cnass-migration/
├── README.md                  ← tu es ici
├── INSTRUCTIONS.md            Source de vérité du contexte (lue à chaque session)
├── INVENTORY.md               Liste vivante des VMs, IPs, outils, statuts
│
├── migration/                 Le cœur du projet — plan de migration complet
│   ├── service-inventory.md     Inventaire des services CNASS à migrer
│   ├── assessment.md            Audit de containerisation par service
│   ├── strategy.md              Stratégie par service : rehost / refactor / rebuild / retire
│   ├── phasing.md               Plan de déploiement par vagues
│   ├── risks.md                 Registre des risques et atténuations
│   └── runbooks/                Procédures réutilisables (migration d'une app Windows, etc.)
│
├── infra/                     Infrastructure as Code
│   ├── terraform/               Provisionnement des VMs
│   ├── talos/                   Configurations Talos
│   └── k3s/                     Scripts d'installation K3s
│
├── apps/                      La charge de travail (PoC)
│   ├── flask-api/               Application Flask instrumentée
│   └── manifests/               Manifestes Kubernetes
│       └── argocd/              Définitions GitOps
│
├── observability/             Pile de monitoring
│   ├── prometheus/              Configurations de scrape par environnement
│   ├── grafana/                 Tableaux de bord (export JSON)
│   └── exporters/               Notes sur windows_exporter, node_exporter, cAdvisor
│
├── lab/                       Protocoles de test
│   ├── scenario-1-idle/         protocol.md + commandes
│   ├── scenario-2-crash/
│   └── scenario-3-burst/        inclut les scripts k6
│
├── results/                   Preuves brutes
│   ├── scenario-1-idle/         Captures Grafana, exports CSV, datés
│   ├── scenario-2-crash/
│   └── scenario-3-burst/
│
├── docs/                      Décisions et visuels
│   ├── adr/                     Architecture Decision Records (un fichier par décision)
│   └── diagrams/                Sources (draw.io / excalidraw) + exports
│
└── rapport/                   Le mémoire final (en français)
    ├── chapitres/               Un fichier markdown par chapitre
    └── figures/                 Images intégrées dans le rapport
```

**Le dossier central est `migration/`** — c'est là que vit le plan de migration complet. La PoC (`lab/` + `results/`) fournit les preuves chiffrées qui alimentent ce plan. Le rapport (`rapport/`) consolide l'ensemble pour le jury.

---

## 7. Comment naviguer dans ce dépôt

| Tu veux… | Ouvre |
|---|---|
| Comprendre le projet en un coup d'œil | ce README |
| Voir le contexte complet (scope, conventions, état) | [`INSTRUCTIONS.md`](INSTRUCTIONS.md) |
| Voir l'état actuel de l'infrastructure | [`INVENTORY.md`](INVENTORY.md) |
| Consulter le plan de migration des services CNASS | [`migration/`](migration/) |
| Reconstruire le laboratoire à partir de zéro | [`infra/README.md`](infra/) |
| Comprendre pourquoi tel outil a été choisi | [`docs/adr/`](docs/adr/) |
| Exécuter un scénario de test précis | [`lab/scenario-N-.../protocol.md`](lab/) |
| Voir les résultats mesurés et les captures Grafana | [`results/`](results/) |
| Lire le rapport final | [`rapport/chapitres/`](rapport/) |

---

## 8. Démarrage rapide — reconstruire le laboratoire

> Prérequis : un hôte physique avec KVM activé, Terraform ≥ 1.9, kubectl, accès SSH configuré.

```bash
# 1. Provisionner les VMs (legacy, docker, nœuds K3s, observateur)
cd infra/terraform
terraform init && terraform apply

# 2. Bootstrap du cluster K3s
cd ../k3s
./install.sh

# 3. Déployer la charge de travail et la pile d'observabilité
kubectl apply -k ../../apps/manifests/
kubectl apply -k ../../observability/

# 4. Vérifier que tout est opérationnel
kubectl get pods -A
# Ouvrir Grafana sur http://<ip-observateur>:3000
```

Instructions détaillées étape par étape dans [`infra/README.md`](infra/).

---

## 9. Stack technique

**Infrastructure :** Proxmox · KVM · Talos Linux · Ubuntu Server 24
**Orchestration :** K3s · Argo CD
**Réseau & stockage :** Cilium · MetalLB · Longhorn / Rook-Ceph
**IaC & automatisation :** Terraform (provider Proxmox) · GitHub Actions
**Observabilité :** Prometheus · Grafana · k6 · OpenTelemetry Collector
**Sauvegarde :** Velero
**Charge de travail :** Python · Flask · prometheus-client

Chaque choix est justifié dans un ADR dédié dans [`docs/adr/`](docs/adr/).

---

## 10. État du projet

- [x] Architecture définie, structure du dépôt en place
- [x] VM observateur déployée (Prometheus + Grafana)
- [x] API Flask instrumentée et conteneurisée
- [ ] Inventaire des services CNASS (`migration/service-inventory.md`)
- [ ] Scénario 1 — empreinte au repos — mesures complétées
- [ ] Scénario 2 — crash / MTTR — mesures complétées
- [ ] Scénario 3 — charge en rafale — mesures complétées
- [ ] Plan de migration finalisé
- [ ] Brouillon du rapport envoyé au maître de stage
- [ ] Diapositives de soutenance

L'avancement détaillé est suivi en parallèle dans le tableau de bord PFE Tracker.

---

## 11. Contexte académique

Ce travail est soumis comme mémoire de fin d'études du Master, en accomplissement partiel des exigences du diplôme. La version publique de ce dépôt présente le travail de manière non-confidentielle ; la version complète, incluant les données sensibles internes à la CNASS, n'est partagée qu'avec le maître de stage, le jury et l'établissement.

**Auteur :** Sheikh
**Maître de stage :** _à compléter_
**Encadrant académique :** _à compléter_
**Établissement :** _à compléter_
**Année universitaire :** 2025–2026

---

## Licence

Ce dépôt est publié à des fins académiques et de démonstration. Réutilisation avec attribution.