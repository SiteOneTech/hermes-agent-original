# Auto Investment Club

> **Sistema autónomo de inversión — el Club.**
> Capital inicial: ~$1,944 USD
> Objetivo: generar ingresos diarios recurrentes vía trading algorítmico.

## Filosofía

No es un robot trader monolítico. Es un **club de inversión** con miembros
especializados que trabajan en paralelo, coordinados por Paimon como PM/CIO.
Cada miembro tiene un rol, herramientas limitadas a su dominio, y reporta al
PM que consolida, decide y ejecuta.

## Stack

| Componente | Tecnología | Costo |
|---|---|---|
| Broker / Data | Alpaca Markets (Algo Trader Plus) | $99/mes |
| Datos macro | FRED API (Federal Reserve) | Gratis |
| Técnicos precomputados | Alpha Vantage | Gratis (5 calls/min) |
| Orquestación | Paimon / Hermes cron jobs + delegate_task | $0 |
| Dashboard web | FastAPI + React (Vite) simple | $0 (localhost) |
| Base de datos | PostgreSQL (existente content ops) | $0 |
| Credenciales | Infisical (Amón) | $0 |
| Despliegue | Localhost en openclaw-miami | $0 |

## APIs gratuitas integradas

### FRED API (Federal Reserve Economic Data)
- **Endpoint:** `https://api.stlouisfed.org/fred/`
- **Auth:** API key gratuita (solicitar en fred.stlouisfed.org)
- **Series clave:**
  - `FEDFUNDS` — Tasa de fondos federales
  - `CPIAUCSL` — CPI (inflación)
  - `UNRATE` — Tasa de desempleo
  - `GDPC1` — GDP real
  - `DGS10` — Treasury 10yr yield
  - `DGS2` — Treasury 2yr yield (yield curve)
  - `SP500` — S&P 500 level
  - `T10YIE` — 10yr breakeven inflation (expectativas)
  - `VIXCLS` — VIX (volatilidad)
- **Rol en el Club:** El Analista Macro consulta FRED cada día pre-market
  para establecer el régimen de mercado (risk-on / risk-off / neutral).

### Alpha Vantage
- **Endpoint:** `https://www.alphavantage.co/query`
- **Auth:** API key gratuita (solicitar en alphavantage.co)
- **Funcionalidades:**
  - `TIME_SERIES_DAILY` — Precios históricos diarios
  - `SMA`, `EMA`, `RSI`, `MACD` — Indicadores técnicos precomputados
  - `OVERVIEW` — Fundamentales de empresa (P/E, revenue, market cap)
  - `CURRENCY_EXCHANGE_RATE` — Forex pairs
  - `DIGITAL_CURRENCY_DAILY` — Crypto histórico
- **Rate limit:** 5 calls/minuto, 500 calls/día
- **Rol en el Club:** Complemento de datos cuando Alpaca no cubre algo
  (ej. indicadores técnicos históricos antes de estar suscripto, o
  fundamentales rápidos sin llamar a otra API).

## Arquitectura del Club

```
                    ┌──────────────────┐
                    │     JEAN         │ (dueño — recibe reportes, da órdenes)
                    │  (usuario/humano)│
                    └────────┬─────────┘
                             │ Telegram / Workspace UI
                    ┌────────▼─────────┐
                    │  PAIMON (PM/CIO) │ coordina, decide, reporta
                    │  Hermes agent    │
                    └──┬────┬────┬─────┘
                       │    │    │
          ┌────────────┘    │    └──────────────┐
          ▼                 ▼                    ▼
   ┌──────────────┐  ┌──────────────┐   ┌──────────────┐
   │ Analista     │  │ Analista     │   │ Analista     │
   │ Fundamental  │  │ Técnico      │   │ Macro        │
   │ (subagente)  │  │ (subagente)  │   │ (subagente)  │
   └──────┬───────┘  └──────┬───────┘   └──────┬───────┘
          │                 │                   │
          └────────┬────────┘───────────────────┘
                   │
          ┌────────▼────────┐
          │  Risk Manager   │ ← define size, stops, diversificación
          │  (subagente)    │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │  Trader Ejecutor│ ← conecta con Alpaca API
          │  (código)       │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │    Alpaca API   │ → órdenes reales / paper
          └─────────────────┘
```

## Ciclo operativo diario

### Pre-Market (08:30 - 09:00 ET)
1. **Cron job** dispara sesión de pre-market
2. Analista Macro → consulta FRED (Fed rates, CPI, yield curve)
3. Analista Macro → determina régimen: RISK-ON / RISK-OFF / NEUTRAL
4. PM consolida régimen + revisa posiciones abiertas
5. PM decide: ¿nuevas entradas hoy? ¿ajustar stops?

### Intraday (09:30 - 16:00 ET)
1. **Cada 30 min:** watchdog de precios de posiciones abiertas
2. Si una posición viola stop-loss o take-profit → ejecución automática
3. Si hay señal de entrada validada por analistas → ejecución
4. PM monitorea todo, no interviene salvo excepción

### Post-Close (16:30 - 17:00 ET)
1. **Cron job** dispara sesión de cierre
2. Trader ejecutor reporta: qué se ejecutó, fills, fees
3. Analistas reportan: señales del día, candidatos nuevos
4. Risk manager reporta: drawdown, exposición, slots
5. PM consolida: reporte diario en Telegram

### Semanal (Domingos)
1. Research round completo: analistas proponen 5-10 candidatos
2. PM selecciona top 3-5 para la semana entrante
3. Paper trading de los nuevos candidatos
4. Performance review: qué estrategias ganaron/perdieron

## Estrategias iniciales

| Estrategia | Activos | Frecuencia | Risk | Slot de capital |
|---|---|---|---|---|
| **Value Swing** | Equities (blue chips) | Semanal | Medio | 40% (~$778) |
| **Momentum** | ETFs sectoriales (QQQ, XLF, XLE) | Diario | Alto | 25% (~$486) |
| **Macro Hedge** | ETFs (GLD, TLT, SHY) | Semanal | Bajo | 20% (~$389) |
| **Crypto Swing** | BTC, ETH, SOL (paper → live) | Diario | Alto | 15% (~$291) |

Cada estrategia tiene su propio slot de capital, stops independientes, y
puede pausarse individualmente sin afectar las demás.

## Risk Management

- **Por operación:** máximo 2-5% del slot de la estrategia
- **Por día:** stop-loss global si drawdown > 2% del capital total
- **Por semana:** si una estrategia pierde 3 días seguidos → se pausa automáticamente
- **Max posiciones abiertas:** 10 total (sumando todas las estrategias)
- **Solo live después de 2 semanas en paper trading exitoso**

## Dashboard web

App simple (FastAPI backend + React) en localhost para:
- Ver portfolio: posiciones abiertas, PnL, slots
- Ver historial de trades (cerrados)
- Ver reportes diarios/semanales
- Kill switch por estrategia
- Logs de decisiones de agentes

No expuesto a internet — solo accesible vía Tailscale.

## Pipeline de datos

```
FRED API ──► cron diario ──► tabla macro_data (PostgreSQL)
Alpha Vantage ──► cron diario ──► tabla technical_data (PostgreSQL)
Alpaca API ──► en vivo ──► tabla positions, trades (PostgreSQL)
```

## Plan de implementación (fases)

### Fase 1 — Fundación (semana 1)
1. [ ] Registrar API keys: Alpaca ($99), FRED (gratis), Alpha Vantage (gratis)
2. [ ] Guardar en Infisical (Amón)
3. [ ] Setup DB: tablas `macro_data`, `technical_data`, `positions`, `trades`, `decisions`
4. [ ] Conectar Alpaca SDK (paper trading primero)
5. [ ] Script de data pipeline: macro + técnicos
6. [ ] Tests de conexión a Alpaca (paper)

### Fase 2 — Analistas (semana 1-2)
7. [ ] Skill de Analista Macro con acceso a FRED
8. [ ] Skill de Analista Técnico con indicadores
9. [ ] Skill de Analista Fundamental con data Alpaca/Alpha Vantage
10. [ ] Skills de Risk Manager (reglas de position sizing, stops)
11. [ ] Tests unitarios de cada analista

### Fase 3 — Ciclo operativo (semana 2)
12. [ ] Cron job pre-market (8:30 ET)
13. [ ] Cron job post-close (16:30 ET)
14. [ ] Watchdog intraday (cada 30 min)
15. [ ] Ciclo de research semanal
16. [ ] Paper trading completo (2 semanas de validación)

### Fase 4 — Dashboard (semana 2-3)
17. [ ] Backend FastAPI para datos del club
18. [ ] Frontend React: portfolio view
19. [ ] Frontend: historial de trades
20. [ ] Frontend: kill switches por estrategia

### Fase 5 — Live (semana 3+)
21. [ ] Conectar a Alpaca live (real money)
22. [ ] Monitoreo 24/7 con alertas en Telegram
23. [ ] Iteración de estrategias basada en performance real

## Costos mensuales

| Concepto | Costo |
|---|---|
| Alpaca Algo Trader Plus | $99 |
| APIs gratuitas (FRED, Alpha Vantage) | $0 |
| Infraestructura (localhost) | $0 |
| **Total** | **$99/mes** |

Objetivo de ingresos: cubrir los $99/mes + margen operativo.
Con $1,944 de capital, un retorno diario del 0.2-0.5% ($4-10/día)
cubre el costo holgadamente.
