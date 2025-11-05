# sistema_bancario

Actividad 4.1: Simulación de un Sistema Bancario Concurrente
Due November 14, 2025 9:59 PM
•
Closes November 21, 2025 9:59 PM
Actividad de Aprendizaje
•
Tema 4 - Programación Concurrente
Instructions
Descripción

Se implementará un sistema bancario simplificado que maneja Cuentas y Transferencias. El sistema consiste en un Banco que gestiona un conjunto de N cuentas bancarias. Múltiples hilos (simulando "Transacciones" o "Cajeros") ejecutarán transferencias de dinero entre dos cuentas de forma concurrente.

Una transferencia transferir(Cuenta A, Cuenta B, monto) debe ser atómica: debe restar el monto de la Cuenta A y sumarlo a la Cuenta B sin que ninguna otra transacción interfiera en medio. Para lograr esto, una transacción debe adquirir el lock de ambas cuentas (la de origen y la de destino) antes de proceder.

El Desafío (El Deadlock): El problema surge cuando dos hilos intentan realizar transferencias opuestas simultáneamente:

Hilo 1: transferir(Cuenta X, Cuenta Y, 100)
Hilo 2: transferir(Cuenta Y, Cuenta X, 50)
El Hilo 1 podría bloquear la Cuenta X y luego intentar bloquear la Cuenta Y. Al mismo tiempo, el Hilo 2 podría bloquear la Cuenta Y e intentar bloquear la Cuenta X. Esto crea una espera circular, resultando en un interbloqueo (Deadlock)donde el programa se congela.



Objetivo General

Diseñar e implementar un sistema concurrente robusto que maneje múltiples recursos bloqueables, demostrando la capacidad de provocar, identificar y prevenir interbloqueos (Deadlocks) mediante la aplicación de protocolos de adquisición de recursos.

Objetivos Específicos:

Implementar la exclusión mutua para un recurso individual (Cuenta).
Diseñar una transacción que requiera la adquisición de múltiples locks.
Provocar deliberadamente un interbloqueo (Fase 1) y demostrar que se entiende por qué ocurre, relacionándolo con las 4 condiciones de Coffman.
Refactorizar el diseño (Fase 2) para prevenir el interbloqueo, rompiendo una de las 4 condiciones (específicamente, la espera circular).
Entregables

Código Fuente (Python o Java):
Fase 1 (Versión "Ingenua" / Rota): La implementación que adquiere los locks en un orden arbitrario (ej. lock(A) y luego lock(B)) y que es susceptible a deadlocks. El código debe incluir un "gatillo" (ej. un sleepcorto entre la adquisición de los dos locks) para hacer que el deadlock sea más probable y reproducible.
Fase 2 (Versión "Corregida" / Prevención): La implementación robusta que previene el deadlock.
Video-Demostración (Formato MP4, máx. 5 min):
Fase 1: Ejecutar el código y demostrar el congelamiento del programa. El estudiante debe narrar, viendo la salida de la consola, "Como ven, el Hilo 1 bloqueó A y espera por B, y el Hilo 2 bloqueó B y espera por A. El programa está muerto".
Fase 2: Ejecutar el código corregido (con las mismas transferencias opuestas y concurrentes) y demostrar que la simulación se completa exitosamente sin congelarse.
Reporte Técnico:
Análisis del Deadlock:
Explicar cómo la implementación de la Fase 1 cumple las 4 condiciones de Coffman (Exclusión Mutua, Retención y Espera, No Apropiación, Espera Circular).
Incluir un gráfico de asignación de recursos (simple, hecho en draw.io o similar) que modele el estado de deadlock de su programa.
Diseño de la Prevención:
Describir la estrategia de prevención implementada. (La solución canónica es romper la espera circular imponiendo un orden global en la adquisición de locks. Por ejemplo, siempre bloquear primero la cuenta con el ID numérico más bajo).
Justificar por qué esta estrategia rompe la condición de espera circular y garantiza que el deadlock es imposible.

---
*This project is being initialized with Claude Code.*
