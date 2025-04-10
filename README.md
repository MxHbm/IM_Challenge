# IM_Challenge
Git Repo for cracking the IM Challenge

# Optimization of Inspection Routes in the District Heating Network of Dresden

This project was developed as part of the **IM Challenge** at Technische Universität Dresden. It focuses on optimizing maintenance and inspection routes in Dresden's urban district heating network.

## 📘 Project Description

The goal is to develop and analyze mathematical models and heuristic algorithms for efficiently planning inspection routes for service teams of SachsenEnergie AG. The project considers real-world constraints such as:

- Fixed time windows for certain tasks (Main Tasks)
- Limited working time per day
- Maximizing the collected profit through completed tasks

## 🧩 Problem Definition

We distinguish between two problem scenarios:

- **Flexi**: No fixed main tasks (pure Multi-Period Team Orienteering Problem, MP-TOP)
- **Operative**: Includes fixed-time main tasks (Multi-Period Team Orienteering Problem with Time Windows, MP-TOPTW)

Both are variants of the Team Orienteering Problem (TOP), solved using exact and heuristic methods.

## 🛠️ Applied Methods

- **Mathematical Models** using Gurobi (Mixed Integer Programming)
- **Constructive Heuristics** (Greedy algorithm with parameter tuning)
- **Metaheuristics**:
  - Iterated Local Search (ILS)
  - Simulated Annealing Iterated Local Search (SAILS)
  - Iterated Simulated Annealing Local Search (ISALS)

## ⚙️ Features

- Multi-period scheduling with multiple service teams
- Time windows and maximum working time constraints
- Start solutions generated via customizable greedy heuristics
- Multi-layered local search with neighborhood operators:
  - Swap, Insert, Replace, Two-Edge-Exchange
- Analysis of search strategies (First vs. Best Improvement, Adaptive behavior)

## 📊 Results Summary

- MIP solutions become infeasible for large instances (long runtimes, poor optimality gap)
- Heuristic and metaheuristic approaches deliver high-quality solutions within minutes
- ISALS outperforms other methods on larger planning horizons

## 📁 Repository Structure

```text
├── data/                   # Test instances (optional/examples)
├── models/                # Mathematical model implementations
├── heuristics/            # Heuristic and metaheuristic algorithms
├── analysis/              # Result evaluation scripts
├── figures/               # Visualizations (gap, profit trends, etc.)
├── README.md              # This file
└── report/                # PDF report (project documentation)

## 📝 Future Work

- Include additional or real-world instances
- Perform deeper parameter tuning, especially for the Flexi scenario
- Explore alternative objective functions (e.g., minimization of idle or waiting time)
- Implement and compare additional metaheuristics (e.g., NSGA-II, Large Neighborhood Search)
- Develop a user interface or visualization tool for the route schedules

## 👥 Authors

**Max Hubmann**  
Student of Industrial Engineering  
Technische Universität Dresden

**Niklas Wolfrum**  
Student of Industrial Engineering  
Technische Universität Dresden
