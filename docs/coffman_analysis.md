# Análisis de Deadlock - Condiciones de Coffman

## Introducción

Este documento analiza cómo la implementación de **Fase 1** del sistema bancario cumple con las **4 Condiciones de Coffman** para que ocurra un deadlock, y cómo la **Fase 2** rompe una de estas condiciones para prevenir el deadlock.

---

## Las 4 Condiciones de Coffman

Para que ocurra un deadlock, deben cumplirse **simultáneamente** las siguientes 4 condiciones:

1. **Mutual Exclusion (Exclusión Mutua)**
2. **Hold and Wait (Retención y Espera)**
3. **No Preemption (No Apropiación)**
4. **Circular Wait (Espera Circular)**

---

## Fase 1: Análisis del Deadlock

### Escenario de Deadlock

Consideremos el siguiente escenario con transferencias opuestas:

```
Hilo-1: transferir(Account-1, Account-2, $100)
Hilo-2: transferir(Account-2, Account-1, $50)
```

### Condición 1: Mutual Exclusion (Exclusión Mutua) ✓

**Definición:** Un recurso solo puede ser utilizado por un proceso a la vez.

**En nuestro sistema:**
- Cada cuenta tiene un `threading.Lock()` asociado
- Solo un hilo puede adquirir el lock de una cuenta a la vez
- Mientras un hilo tiene el lock, otros hilos deben esperar

**Código relevante (Account):**
```python
class Account:
    def __init__(self, account_id: int, initial_balance: float):
        self.lock = threading.Lock()  # Lock exclusivo
```

**Código relevante (Phase1Bank):**
```python
from_account.lock.acquire()  # Solo un hilo puede adquirirlo
```

✓ **Cumple la condición**

---

### Condición 2: Hold and Wait (Retención y Espera) ✓

**Definición:** Un proceso retiene al menos un recurso mientras espera adquirir recursos adicionales.

**En nuestro sistema:**
- Hilo-1 adquiere lock de Account-1
- Mientras **retiene** ese lock, **espera** adquirir lock de Account-2
- Hilo-2 hace lo opuesto

**Código relevante (Phase1Bank):**
```python
from_account.lock.acquire()  # Adquiere primer lock
try:
    # RETIENE el lock de from_account
    time.sleep(self.thread_delay)  # Aumenta ventana de deadlock

    to_account.lock.acquire()  # ESPERA por segundo lock
    # ...
```

✓ **Cumple la condición**

---

### Condición 3: No Preemption (No Apropiación) ✓

**Definición:** Los recursos no pueden ser quitados forzosamente de un proceso; deben ser liberados voluntariamente.

**En nuestro sistema:**
- Los `threading.Lock()` en Python no pueden ser "arrebatados" de un hilo
- Un lock solo se libera cuando el hilo llama a `.release()`
- No existe mecanismo para forzar la liberación

**Comportamiento de threading.Lock:**
```python
# No existe lock.force_release() o similar
# El lock DEBE ser liberado voluntariamente
from_account.lock.release()  # Liberación voluntaria
```

✓ **Cumple la condición**

---

### Condición 4: Circular Wait (Espera Circular) ✓

**Definición:** Existe un ciclo de procesos donde cada uno espera un recurso retenido por el siguiente en el ciclo.

**En nuestro sistema (el problema clave):**

```
Hilo-1:
  1. Adquiere lock(Account-1) ✓
  2. Espera lock(Account-2) ⏳ (retenido por Hilo-2)

Hilo-2:
  1. Adquiere lock(Account-2) ✓
  2. Espera lock(Account-1) ⏳ (retenido por Hilo-1)
```

**Diagrama de espera circular:**

```
    Hilo-1 ----espera----> Account-2
       ^                      |
       |                   retenido
    retenido                  |
       |                      v
    Account-1 <---espera---- Hilo-2
```

**Código Phase1Bank que permite esto:**
```python
def transfer(self, from_account_id, to_account_id, amount):
    # Adquiere locks en ORDEN DE LLEGADA (no ordenado)
    from_account.lock.acquire()  # Puede ser cualquier cuenta
    to_account.lock.acquire()    # Puede crear ciclo
```

✓ **Cumple la condición**

---

## Resultado: DEADLOCK

Como las **4 condiciones se cumplen simultáneamente**, el deadlock es posible y ocurre con alta probabilidad cuando hay transferencias opuestas concurrentes.

**Síntomas del deadlock:**
- El programa se congela
- Los hilos quedan esperando indefinidamente
- Timeout se activa (en nuestro caso: 10 segundos)

---

## Fase 2: Prevención del Deadlock

### Estrategia: Romper la Espera Circular

La Fase 2 previene el deadlock **rompiendo la Condición 4: Circular Wait**.

### Implementación: Global Lock Ordering

**Principio:** Todos los hilos adquieren los locks en el **mismo orden global** (por ID ascendente).

**Código Phase2Bank:**
```python
def transfer(self, from_account_id, to_account_id, amount):
    # Ordenar cuentas por ID ANTES de adquirir locks
    first, second = self._get_ordered_accounts(from_account, to_account)

    first.lock.acquire()   # Siempre el de menor ID primero
    try:
        second.lock.acquire()  # Luego el de mayor ID
        # ...
    finally:
        second.lock.release()
    finally:
        first.lock.release()

@staticmethod
def _get_ordered_accounts(acc1, acc2):
    if acc1.id < acc2.id:
        return (acc1, acc2)
    else:
        return (acc2, acc1)
```

### ¿Por qué esto previene el deadlock?

**Mismo escenario, ahora con orden global:**

```
Hilo-1: transferir(Account-1, Account-2, $100)
  → Ordena: (1, 2)
  → Adquiere: lock(1), luego lock(2)

Hilo-2: transferir(Account-2, Account-1, $50)
  → Ordena: (1, 2)  ← ¡Mismo orden!
  → Adquiere: lock(1), luego lock(2)
```

**Resultado:**
- Ambos hilos intentan adquirir lock(Account-1) primero
- Uno lo consigue (ej: Hilo-1)
- El otro espera (Hilo-2)
- Hilo-1 completa: adquiere lock(2), hace transfer, libera ambos
- Hilo-2 ahora puede adquirir lock(1), luego lock(2), completar

**No hay ciclo:**
```
Hilo-1: espera nada (ya tiene lock-1)
Hilo-2: espera lock-1 (retenido por Hilo-1)

→ Espera LINEAL, no circular
→ Hilo-1 eventualmente libera
→ Hilo-2 puede proceder
```

---

## Verificación de Condiciones en Fase 2

| Condición | Fase 1 | Fase 2 | Impacto |
|-----------|--------|--------|---------|
| 1. Mutual Exclusion | ✓ Cumple | ✓ Cumple | Sin cambio |
| 2. Hold and Wait | ✓ Cumple | ✓ Cumple | Sin cambio |
| 3. No Preemption | ✓ Cumple | ✓ Cumple | Sin cambio |
| 4. Circular Wait | ✓ Cumple | ❌ **ROTA** | **Deadlock eliminado** |

**Conclusión:** Al romper una sola condición (Circular Wait), el deadlock se vuelve **imposible**, aunque las otras 3 condiciones sigan presentes.

---

## Demostración Experimental

### Fase 1: Deadlock Observado
```
$ python -m src.main
> 1 (Run Phase 1)

[Output]
[Thread-1] Acquired lock on Account-1
[Thread-2] Acquired lock on Account-2
[Thread-1] Waiting for lock on Account-2...
[Thread-2] Waiting for lock on Account-1...
...
DEADLOCK DETECTED - Simulation timed out after 10s
```

### Fase 2: Sin Deadlock
```
$ python -m src.main
> 2 (Run Phase 2)

[Output]
[Thread-1] Acquired lock on Account-1
[Thread-1] Acquired lock on Account-2
[Thread-1] Transfer completed
[Thread-2] Acquired lock on Account-1
[Thread-2] Acquired lock on Account-2
[Thread-2] Transfer completed
✓ Simulation completed successfully!
```

---

## Conclusiones

1. **Fase 1 cumple las 4 Condiciones de Coffman → Deadlock posible**
   - Especialmente con el `sleep(0.01)` que aumenta la ventana vulnerable

2. **Fase 2 rompe Circular Wait → Deadlock imposible**
   - Orden global garantiza espera lineal, no circular

3. **El orden global es suficiente**
   - No necesitamos cambiar las otras 3 condiciones
   - Romper una sola condición es suficiente para prevenir deadlock

4. **Trade-off de la solución:**
   - ✅ Ventaja: Deadlock imposible
   - ⚠️ Desventaja: Posible reducción de concurrencia (más espera secuencial)
   - En la práctica, el overhead es mínimo para sistemas pequeños

---

## Gráfico de Asignación de Recursos

*Para el reporte técnico, incluir un diagrama tipo Resource Allocation Graph (RAG) mostrando:*
- **Fase 1:** Ciclo entre procesos y recursos
- **Fase 2:** Grafo acíclico (DAG)

**Herramientas sugeridas:** draw.io, Lucidchart, o diagramas ASCII

**Ejemplo ASCII del ciclo (Fase 1):**
```
    P1 ----→ R2
    ↑         ↓
    |         |
    R1 ←---- P2
```

**Ejemplo sin ciclo (Fase 2):**
```
P1 → R1 → P2
     ↓
     R2
```

---

**Documento generado para el reporte técnico de Actividad 4.1**
