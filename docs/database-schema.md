# Database Schema

Phase 1 scaffolds Alembic and SQLAlchemy metadata. The following schema is the planned authoritative relational model for trading persistence in later phases.

## `orders`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Internal order identifier. |
| `symbol` | VARCHAR(32) | Not null, indexed | TAIFEX product or contract symbol. |
| `side` | VARCHAR(8) | Not null | `buy` or `sell`. |
| `price` | NUMERIC(18, 4) | Nullable | Limit/stop price where applicable. |
| `quantity` | INTEGER | Not null | Order quantity. |
| `status` | VARCHAR(32) | Not null, indexed | Working, filled, canceled, rejected, etc. |
| `created_at` | TIMESTAMPTZ | Not null | Creation timestamp. |
| `updated_at` | TIMESTAMPTZ | Not null | Last update timestamp. |

## `executions`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Internal execution identifier. |
| `order_id` | UUID | Foreign key to `orders.id` | Filled order. |
| `fill_price` | NUMERIC(18, 4) | Not null | Execution price. |
| `fill_quantity` | INTEGER | Not null | Filled quantity. |
| `fill_time` | TIMESTAMPTZ | Not null, indexed | Broker execution timestamp. |

## `positions`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Internal position identifier. |
| `symbol` | VARCHAR(32) | Unique, not null | Position symbol. |
| `quantity` | INTEGER | Not null | Net position quantity. |
| `average_price` | NUMERIC(18, 4) | Not null | Average entry price. |
| `realized_pnl` | NUMERIC(18, 4) | Not null | Realized profit and loss. |
| `unrealized_pnl` | NUMERIC(18, 4) | Not null | Mark-to-market profit and loss. |

## `atm_templates`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary key | Template identifier. |
| `name` | VARCHAR(128) | Unique, not null | Template name. |
| `stop_loss_ticks` | INTEGER | Not null | Stop loss offset in ticks. |
| `take_profit_ticks` | INTEGER | Not null | Take profit offset in ticks. |

## Default ATM Templates

| Name | Stop Loss Ticks | Take Profit Ticks |
| --- | ---: | ---: |
| Scalp | 10 | 20 |
| Trend | 30 | 90 |
| Breakout | 20 | 60 |
