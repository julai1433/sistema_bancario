# Sistema Bancario - Simulación de Deadlock Concurrente

Actividad 4.1: Simulación de un Sistema Bancario Concurrente
**Due:** November 14, 2025 9:59 PM
**Tema:** Programación Concurrente

## Descripción

Sistema bancario simplificado que demuestra la ocurrencia y prevención de **deadlocks** en sistemas concurrentes. El sistema implementa dos fases:

- **Fase 1 (Deadlock-Prone):** Adquisición naive de locks que puede causar deadlock
- **Fase 2 (Deadlock-Free):** Adquisición ordenada de locks que previene deadlock

### El Desafío del Deadlock

Cuando dos hilos intentan realizar transferencias opuestas simultáneamente:

```
Hilo 1: transferir(Cuenta X, Cuenta Y, 100)
Hilo 2: transferir(Cuenta Y, Cuenta X, 50)

→ Hilo 1 bloquea X, espera Y
→ Hilo 2 bloquea Y, espera X
→ DEADLOCK (espera circular)
```

## Características

- ✅ Sistema bancario thread-safe con cuentas y transferencias
- ✅ Fase 1: Implementación deadlock-prone (con trigger de `sleep`)
- ✅ Fase 2: Implementación deadlock-free (lock ordering)
- ✅ Menú interactivo para ejecutar simulaciones
- ✅ Logging detallado con output colorizado
- ✅ Configuración editable (JSON)
- ✅ Tests unitarios e integración (pytest)
- ✅ Métricas de simulación

## Estructura del Proyecto

```
sistema_bancario/
├── src/
│   ├── models/          # Account, Transaction
│   ├── banks/           # Bank, Phase1Bank, Phase2Bank
│   ├── simulation/      # Simulator, Metrics
│   ├── ui/              # Interactive Menu, Colors
│   ├── utils/           # Logger, ConfigLoader
│   └── main.py          # Entry point
├── tests/               # Unit & integration tests
├── config/              # Configuration files
├── logs/                # Generated logs
└── requirements.txt
```

## Instalación

### 1. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar el programa interactivo

```bash
python -m src.main
```

### Menú Principal

```
1. Run Phase 1 (Deadlock-Prone)
2. Run Phase 2 (Deadlock-Free)
3. Run Both Phases (Comparison)
4. Show Current Configuration
5. Load Configuration File
6. Exit
```

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Solo unit tests
pytest tests/unit/

# Verbose
pytest -v
```

## Configuración

Edita `config/config.json` para modificar:

- **accounts**: Cantidad y saldo inicial de cuentas
- **transfers**: Transferencias a ejecutar concurrentemente
- **simulation.thread_delay_seconds**: Delay entre locks (Phase 1)
- **simulation.deadlock_timeout_seconds**: Timeout para detectar deadlock
- **simulation.verbose_logging**: Nivel de detalle del logging

## Análisis del Deadlock (Coffman Conditions)

### Fase 1 cumple las 4 condiciones:

1. **Exclusión Mutua:** Los locks son mutuamente exclusivos
2. **Hold and Wait:** Un hilo retiene un lock mientras espera otro
3. **No Preemption:** Los locks no se pueden quitar forzosamente
4. **Circular Wait:** Hilo-1 espera recurso de Hilo-2 y viceversa

### Fase 2 rompe la Circular Wait:

- **Estrategia:** Adquisición de locks en **orden global** (por ID ascendente)
- **Resultado:** Sin espera circular → Sin deadlock

## Logs

Los logs se guardan automáticamente en `logs/simulation_YYYYMMDD_HHMMSS.log`

Ejemplo de output:

```
[Thread-1] 🔵 INFO Starting transfer: Account-1 → Account-2 ($100.00)
[Thread-1] 🔒 Acquired lock on Account-1
[Thread-1] ⏳ Waiting for lock on Account-2...
[Thread-1] 🔒 Acquired lock on Account-2
[Thread-1] 🟢 SUCCESS Transfer completed
```

## Para el Reporte Técnico

Ver `docs/coffman_analysis.md` para:
- Análisis detallado de las condiciones de Coffman
- Diagramas de asignación de recursos
- Justificación de la estrategia de prevención

## Objetivos del Proyecto

✅ Implementar exclusión mutua para recursos individuales (Account)
✅ Diseñar transacciones que requieren múltiples locks
✅ Provocar deliberadamente un deadlock (Phase 1)
✅ Prevenir el deadlock rompiendo circular wait (Phase 2)

## Tecnologías

- **Python 3.10+**
- **threading:** Concurrencia con locks
- **pytest:** Testing framework
- **colorama:** Output colorizado
- **Type hints:** Código type-safe

## Autores

Proyecto desarrollado para el curso de Tecnologías de Programación
Maestría en Sistemas Computacionales - Instituto Tecnológico de Morelia
