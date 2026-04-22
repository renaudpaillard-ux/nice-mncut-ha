# Intégration Nice MNCUT pour Home Assistant

🇬🇧 [Read in English](README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue)

Cette intégration permet de piloter une centrale d'alarme **Nice MNCUT** directement depuis Home Assistant, via une connexion WebSocket locale (sans cloud).

---

## 🎯 Contexte du projet

Ce projet a été développé dans un cadre personnel de domotique, avec les objectifs suivants :

- intégration propre dans Home Assistant
- communication locale (pas de dépendance cloud)
- remontée d'état en temps réel
- interface utilisateur exploitable au quotidien

Il met en œuvre :
- communication WebSocket temps réel
- architecture Home Assistant (config flow, entités, services)
- gestion d'état et des anomalies

---

## ✨ Fonctionnalités

- 🔒 Armement / désarmement / mode partiel
- 📡 Mise à jour temps réel (`local_push`)
- 🔋 Suivi du niveau de batterie
- ⚡ État de l'alimentation secteur
- 🚨 Détection sabotage / capteurs / contacts
- ⏱️ Décompte du délai de sortie
- 🛠️ Service de réinitialisation des anomalies
- 🌐 Multi-langue : Anglais & Français

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

- Version simple : `examples/dashboard_simple.yaml`
- Version avancée : `examples/dashboard_premium.yaml`

---

## Entités

| Entité                                          | Type           | Description                      |
| ----------------------------------------------- | -------------- | -------------------------------- |
| `alarm_control_panel.nice_mncut`                | Panneau alarme | Contrôle principal armement      |
| `binary_sensor.nice_mncut_batterie_faible`      | Capteur binaire | Alerte batterie faible           |
| `binary_sensor.nice_mncut_alimentation_secteur` | Capteur binaire | Alimentation secteur OK          |
| `binary_sensor.nice_mncut_sabotage`             | Capteur binaire | Alerte sabotage / effraction     |
| `binary_sensor.nice_mncut_contact_ouvert`       | Capteur binaire | Contact ouvert détecté           |
| `binary_sensor.nice_mncut_capteur_declenche`    | Capteur binaire | Capteur de mouvement déclenché   |
| `binary_sensor.nice_mncut_panique`              | Capteur binaire | Alarme panique                   |
| `binary_sensor.nice_mncut_mode_maintenance`     | Capteur binaire | Mode maintenance                 |
| `sensor.nice_mncut_etat_brut`                   | Capteur        | Code état brut de la centrale    |
| `sensor.nice_mncut_zones_armees`                | Capteur        | Nombre de zones armées           |
| `sensor.nice_mncut_niveau_batterie`             | Capteur        | Niveau de batterie (%)           |
| `sensor.nice_mncut_delai_de_sortie`             | Capteur        | Décompte du délai de sortie (s)  |

---

## Services

### `nice_mncut.clear_anomalies`

Acquitte les anomalies (sabotage, contact ouvert, etc.) pour permettre le réarmement.

| Champ   | Requis | Défaut   | Description                  |
| ------- | ------ | -------- | ---------------------------- |
| `areas` | Non    | `123456` | Identifiants des zones à acquitter |

Exemple :

```yaml
service: nice_mncut.clear_anomalies
data:
  areas: "123456"
```

---

## États supportés

| État HA       | Description                        |
| ------------- | ---------------------------------- |
| `disarmed`    | Centrale désarmée                  |
| `arming`      | Délai de sortie en cours           |
| `armed_away`  | Armement total (toutes les zones)  |
| `armed_home`  | Armement partiel (mode présence)   |
| `disarming`   | Désarmement en cours               |
| `unavailable` | Centrale injoignable               |

---

## Dépannage

**L'intégration ne se connecte pas :**

- Vérifier l'adresse IP et que le port 4012 est ouvert
- Consulter les logs HA : `Paramètres → Système → Journaux`, filtrer par `nice_mncut`

**Impossible de réarmer après une anomalie :**

- Utiliser d'abord le service `nice_mncut.clear_anomalies`

---

## 💼 Objectif

Ce dépôt sert également de démonstration technique :

- développement d'intégration Home Assistant
- communication réseau temps réel
- structuration d'un projet open source
- distribution via HACS

---

## 🤝 Contribuer

Les issues et contributions sont les bienvenues !

---

## ⚠️ Avertissement

Non affilié à Nice S.p.A.

---

## 📄 Licence

MIT License
