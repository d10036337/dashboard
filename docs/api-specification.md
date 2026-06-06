# API Specifications

Base URL: `/api/v1`

## Phase 1 Implemented Endpoints

### `GET /health`

Returns service status.

Response:

```json
{
  "status": "ok",
  "service": "Taiwan Tradovate (TTX Trader)",
  "environment": "development"
}
```

## Planned REST API

### Contracts

`GET /contracts`

Returns near-month supported TAIFEX contracts for TXF, MXF, TMF, TE, and TF.

### Historical Market Data

`GET /market/history?symbol=TXF&interval=1m`

Supported intervals: `1m`, `5m`, `15m`, `60m`, `1d`.

Response:

```json
[
  {
    "time": "2026-06-06T01:00:00Z",
    "open": 22000,
    "high": 22025,
    "low": 21990,
    "close": 22010,
    "volume": 1200
  }
]
```

Redis cache keys:

- `market:{symbol}:1m`
- `market:{symbol}:5m`
- `market:{symbol}:15m`
- `market:{symbol}:60m`
- `market:{symbol}:1d`

Aggregation rules:

- Open: first candle open.
- High: highest high.
- Low: lowest low.
- Close: last candle close.
- Volume: summed volume.

### Orders

- `GET /orders`
- `POST /orders`
- `PATCH /orders/{id}`
- `DELETE /orders/{id}`

Order create request:

```json
{
  "symbol": "TXF",
  "side": "buy",
  "price": 22000,
  "quantity": 1,
  "stop_loss_price": 21970,
  "take_profit_price": 22050,
  "atm_template_id": null
}
```

### Positions

- `GET /positions`
- `POST /positions/flatten`
- `POST /positions/reverse`

### Executions

`GET /executions`

### Account

`GET /account`

### ATM Templates

- `GET /atm-templates`
- `POST /atm-templates`
- `PATCH /atm-templates/{id}`
- `DELETE /atm-templates/{id}`

ATM create request:

```json
{
  "name": "Scalp",
  "stop_loss_ticks": 10,
  "take_profit_ticks": 20
}
```

## Planned WebSocket API

### `GET /ws/market/{symbol}`

Tick payload:

```json
{
  "type": "tick",
  "price": 22000,
  "volume": 5,
  "timestamp": "2026-06-06T01:00:00.000Z"
}
```

Bid/ask payload:

```json
{
  "type": "bidask",
  "bid_price": [21999, 21998],
  "bid_volume": [20, 15],
  "ask_price": [22000, 22001],
  "ask_volume": [12, 18]
}
```

### Event Names

- `market_tick`
- `market_bidask`
- `order_update`
- `execution_update`
- `position_update`
- `account_update`
- `pnl_update`
