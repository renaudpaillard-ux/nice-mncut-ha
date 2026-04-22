# Intégration Nice MNCUT pour Home Assistant

🇬🇧 [Read in English](README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue)

Cette intégration permet de piloter une centrale d’alarme **Nice MNCUT** directement depuis Home Assistant, via une connexion WebSocket locale (sans cloud).

---

## 🎯 Contexte du projet

Ce projet a été développé dans un cadre personnel de domotique, avec les objectifs suivants :

- intégration propre dans Home Assistant
- communication locale (pas de dépendance cloud)
- remontée d’état en temps réel
- interface utilisateur exploitable au quotidien

Il met en œuvre :
- communication WebSocket temps réel
- architecture Home Assistant (config flow, entités, services)
- gestion d’état et des anomalies

---

## ✨ Fonctionnalités

- 🔒 Armement / désarmement / mode partiel
- 📡 Mise à jour temps réel (`local_push`)
- 🔋 Suivi du niveau de batterie
- ⚡ État de l’alimentation secteur
- 🚨 Détection sabotage / capteurs / contacts
- ⏱️ Décompte du délai de sortie
- 🛠️ Service de réinitialisation des anomalies

---

## 📦 Installation

### Via HACS (recommandé)

1. Ouvrir **HACS → Intégrations**
2. Ajouter le dépôt en tant que dépôt personnalisé
3. Installer **Nice MNCUT**
4. Redémarrer Home Assistant

### Manuel

Copier `custom_components/nice_mncut` dans `/config/custom_components/`

---

## ⚙️ Configuration

1. Aller dans **Paramètres → Appareils et services**
2. Ajouter l’intégration **Nice MNCUT**
3. Renseigner l’adresse IP et le code PIN

---

## 🖥️ Exemple de dashboard

- Version simple : `examples/dashboard_simple.yaml`
- Version avancée : `examples/dashboard_premium.yaml`

---

## 💼 Objectif

Ce dépôt sert également de démonstration technique :

- développement d’intégration Home Assistant
- communication réseau temps réel
- structuration d’un projet open source
- distribution via HACS

---

## 📄 Licence

MIT License
