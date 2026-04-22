---
name: frontend-dashboard
description: Start and manage the React/Vite frontend dashboard for the Omission project. Use when the user asks to open the dashboard, view the UI, or interact with the frontend presentation layer.
---

# Frontend Dashboard Management

The Omission project features a professional React/Vite web dashboard that visualizes the analytical outputs (HTML figures and markdown reports) located in D:\drive\outputs\oglo-8figs and D:\drive\progress-report\.

## 1. Dashboard Location
The source code and configuration for the dashboard are located at:
D:\drive\omission\dashboard

## 2. How to Start the Dashboard
When requested to open or start the dashboard, execute the following commands in the terminal (or run as a background shell command):

`powershell
cd D:\drive\omission\dashboard
npm install
npm run dev
`

To run it in the background using the CLI agent tools, set is_background: true when calling 
un_shell_command for the 
pm run dev step.
