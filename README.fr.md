# Nice MNCUT — Intégration Home Assistant

![Preview](assets/dashboard_premium.png)

🇬🇧 [Read in English](README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue)

Cette intégration permet de piloter une centrale d'alarme **Nice MNCUT** directement depuis Home Assistant, via une connexion WebSocket locale (sans cloud).

---

## 🎯 Contexte du projet

Ce dépôt repose sur un vrai projet personnel de domotique et sert aussi à démontrer un travail d'intégration solide autour de :

- l'architecture d'une intégration personnalisée Home Assistant
- une communication locale sans dépendance cloud
- la gestion d'état en temps réel via WebSocket
- des dashboards utilisables au quotidien et une distribution via HACS

---

## 🧠 Contexte technique

Cette intégration a été développée à la suite d'une phase de rétro-ingénierie du système Nice MNCUT.

Le travail a notamment consisté à :

- analyser les communications WebSocket entre l'interface web et la centrale
- inspecter le code de l'application web de l'alarme
- identifier les formats de messages et les transitions d'état
- reconstruire une couche de communication fiable pour Home Assistant

Cette approche a permis de construire une intégration entièrement locale et temps réel, sans dépendre d'une API officielle ni d'un service cloud.

---

## ✨ Fonctionnalités

- 🔒 Armement / désarmement / armement partiel via Home Assistant
- 📡 Mises à jour d'état en temps réel via WebSocket (`local_push`)
- 🔋 Suivi du niveau de batterie (%)
- ⚡ État de l'alimentation secteur
- 🚨 Détection de sabotage, contact ouvert et capteur déclenché
- ⏱️ Décompte du délai de sortie
- 🛠️ Service d'acquittement des anomalies (`clear_anomalies`)
- 🌐 Multi-langue : anglais et français

---

## 📋 Prérequis

- Home Assistant **2023.1 ou supérieur**
- Centrale d'alarme Nice MNCUT accessible sur le réseau local
- Port WebSocket **4012** accessible depuis Home Assistant

---

## 📦 Installation

### Via HACS (recommandé)

1. Ouvrir **HACS → Intégrations**
2. Cliquer sur les trois points (en haut à droite) → **Dépôts personnalisés**
3. Ajouter l'URL de ce dépôt et sélectionner la catégorie **Intégration**
4. Rechercher **Nice MNCUT** et installer
5. Redémarrer Home Assistant

### Manuel

Copier `custom_components/nice_mncut` dans `/config/custom_components/` et redémarrer Home Assistant.

---

## ⚙️ Configuration

1. Aller dans **Paramètres → Appareils et services → Ajouter une intégration**
2. Rechercher **Nice MNCUT**
3. Renseigner :
   - **Adresse IP** de la centrale MNCUT
   - **Code PIN**

---

## 🖥️ Exemples de dashboard

- [Simple : `examples/dashboard_simple.yaml`](examples/dashboard_simple.yaml)
- [Premium : `examples/dashboard_premium.yaml`](examples/dashboard_premium.yaml)

### 🧩 Dashboard simple

![Dashboard simple](assets/dashboard_simple.png)

### ✨ Dashboard premium

![Dashboard premium](assets/dashboard_premium.png)
![Dashboard premium - Armé](assets/dashboard_premium_armed.png)
![Dashboard premium - Contact ouvert](assets/dashboard_premium_opened_contact.png)

---

## Entités

| Entité                                          | Type            | Description                     |
| ----------------------------------------------- | --------------- | ------------------------------- |
| `alarm_control_panel.nice_mncut`                | Panneau alarme  | Contrôle principal armement     |
| `binary_sensor.nice_mncut_batterie_faible`      | Capteur binaire | Alerte batterie faible          |
| `binary_sensor.nice_mncut_alimentation_secteur` | Capteur binaire | Alimentation secteur OK         |
| `binary_sensor.nice_mncut_sabotage`             | Capteur binaire | Alerte sabotage / effraction    |
| `binary_sensor.nice_mncut_contact_ouvert`       | Capteur binaire | Contact ouvert détecté          |
| `binary_sensor.nice_mncut_capteur_declenche`    | Capteur binaire | Capteur de mouvement déclenché  |
| `binary_sensor.nice_mncut_panique`              | Capteur binaire | Alarme panique                  |
| `binary_sensor.nice_mncut_mode_maintenance`     | Capteur binaire | Mode maintenance                |
| `sensor.nice_mncut_etat_brut`                   | Capteur         | Code état brut de la centrale   |
| `sensor.nice_mncut_zones_armees`                | Capteur         | Nombre de zones armées          |
| `sensor.nice_mncut_niveau_batterie`             | Capteur         | Niveau de batterie (%)          |
| `sensor.nice_mncut_delai_de_sortie`             | Capteur         | Décompte du délai de sortie (s) |

---

## Services

### `nice_mncut.clear_anomalies`

Acquitte les anomalies (sabotage, contact ouvert, etc.) pour permettre le réarmement.

| Champ   | Requis | Défaut   | Description                        |
| ------- | ------ | -------- | ---------------------------------- |
| `areas` | Non    | `123456` | Identifiants des zones à acquitter |

Exemple :

```yaml
service: nice_mncut.clear_anomalies
data:
  areas: "123456"
```

---

## États supportés

| État HA       | Description                       |
| ------------- | --------------------------------- |
| `disarmed`    | Centrale désarmée                 |
| `arming`      | Délai de sortie en cours          |
| `armed_away`  | Armement total (toutes les zones) |
| `armed_home`  | Armement partiel (mode présence)  |
| `disarming`   | Désarmement en cours              |
| `unavailable` | Centrale injoignable              |

---

## Dépannage

**L'intégration ne se connecte pas :**

- Vérifier l'adresse IP et que le port 4012 est ouvert
- Consulter les logs HA : `Paramètres → Système → Journaux`, filtrer par `nice_mncut`

**Impossible de réarmer après une anomalie :**

- Utiliser d'abord le service `nice_mncut.clear_anomalies`

---

## 🧰 Workflow d'ingénierie

Ce projet reflète également un workflow de développement moderne, construit autour de VS Code, de la rétro-ingénierie et d'outils de codage assisté par IA comme Codex et Claude Code.

Ces outils ont permis d'accélérer l'implémentation, l'analyse du protocole, la documentation et les cycles d'itération, tandis que la compréhension du système, les choix d'architecture, la validation et les décisions techniques finales sont restés sous le contrôle de l'auteur.

---

## 🤝 Contribuer

Les issues et contributions sont les bienvenues !

---

## ⚠️ Avertissement

Non affilié à Nice S.p.A.

---

## 📄 Licence

MIT License
