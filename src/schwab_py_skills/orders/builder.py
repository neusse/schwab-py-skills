"""Fluent Schwab order builder adapted from Schwab_EZ_Orders."""

from __future__ import annotations

from decimal import Decimal, ROUND_DOWN
from typing import Any

from .schemas import (
    AssetType,
    ComplexOrderStrategy,
    Duration,
    OrderAction,
    OrderLeg,
    OrderPricing,
    OrderStrategy,
    Session,
)


class ValidationError(ValueError):
    """Raised when an order cannot be built safely."""


def _enum(value: Any, enum_type: type) -> Any:
    if isinstance(value, enum_type):
        return value
    return enum_type(str(value).upper().replace("-", "_"))


class OrderBuilder:
    """Fluent builder for Schwab-compatible order JSON."""

    def __init__(self) -> None:
        self.legs: list[OrderLeg] = []
        self.order_type: OrderPricing | None = None
        self.price: str | None = None
        self.stop_price: str | None = None
        self.duration = Duration.DAY
        self.session = Session.NORMAL
        self.order_strategy = OrderStrategy.SINGLE
        self.complex_order_strategy = ComplexOrderStrategy.NONE
        self.child_orders: list[OrderBuilder] = []
        self.stop_price_link_basis: str | None = None
        self.stop_price_link_type: str | None = None
        self.stop_price_offset: float | None = None
        self.warnings: list[str] = []

    def buy(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.BUY, symbol, 0, AssetType.EQUITY)

    def sell(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.SELL, symbol, 0, AssetType.EQUITY)

    def sell_short(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.SELL_SHORT, symbol, 0, AssetType.EQUITY)

    def buy_to_cover(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.BUY_TO_COVER, symbol, 0, AssetType.EQUITY)

    def buy_to_open(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.BUY_TO_OPEN, symbol, 0, AssetType.OPTION)

    def sell_to_close(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.SELL_TO_CLOSE, symbol, 0, AssetType.OPTION)

    def sell_to_open(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.SELL_TO_OPEN, symbol, 0, AssetType.OPTION)

    def buy_to_close(self, symbol: str) -> "OrderBuilder":
        return self.with_leg(OrderAction.BUY_TO_CLOSE, symbol, 0, AssetType.OPTION)

    def with_leg(
        self,
        action: OrderAction | str,
        symbol: str,
        quantity: int,
        asset_type: AssetType | str = AssetType.EQUITY,
    ) -> "OrderBuilder":
        self.legs.append(
            OrderLeg(
                instruction=_enum(action, OrderAction),
                symbol=symbol.upper(),
                quantity=quantity,
                asset_type=_enum(asset_type, AssetType),
            )
        )
        return self

    def shares(self, quantity: int) -> "OrderBuilder":
        return self._set_quantity(quantity, "shares")

    def contracts(self, quantity: int) -> "OrderBuilder":
        return self._set_quantity(quantity, "contracts")

    def market(self) -> "OrderBuilder":
        self.order_type = OrderPricing.MARKET
        self.price = None
        return self

    def limit(self, price: float) -> "OrderBuilder":
        self.order_type = OrderPricing.LIMIT
        self.price = self._format_price(price)
        return self

    def stop(self, stop_price: float) -> "OrderBuilder":
        self.order_type = OrderPricing.STOP
        self.stop_price = self._format_price(stop_price)
        return self

    def stop_limit(self, stop_price: float, limit_price: float) -> "OrderBuilder":
        self.order_type = OrderPricing.STOP_LIMIT
        self.stop_price = self._format_price(stop_price)
        self.price = self._format_price(limit_price)
        return self

    def trailing_stop(
        self, offset: float, offset_type: str = "VALUE", basis: str = "BID"
    ) -> "OrderBuilder":
        self.order_type = OrderPricing.TRAILING_STOP
        self.stop_price_link_basis = basis
        self.stop_price_link_type = offset_type
        self.stop_price_offset = offset
        return self

    def net_debit(self, price: float) -> "OrderBuilder":
        self.order_type = OrderPricing.NET_DEBIT
        self.price = self._format_price(price)
        return self

    def net_credit(self, price: float) -> "OrderBuilder":
        self.order_type = OrderPricing.NET_CREDIT
        self.price = self._format_price(price)
        return self

    def net_zero(self) -> "OrderBuilder":
        self.order_type = OrderPricing.NET_ZERO
        self.price = "0.00"
        return self

    def day(self) -> "OrderBuilder":
        self.duration = Duration.DAY
        return self

    def gtc(self) -> "OrderBuilder":
        self.duration = Duration.GOOD_TILL_CANCEL
        return self

    def ioc(self) -> "OrderBuilder":
        self.duration = Duration.IMMEDIATE_OR_CANCEL
        return self

    def fok(self) -> "OrderBuilder":
        self.duration = Duration.FILL_OR_KILL
        return self

    def vertical_spread(self) -> "OrderBuilder":
        self.complex_order_strategy = ComplexOrderStrategy.VERTICAL
        return self

    def iron_condor_strategy(self) -> "OrderBuilder":
        self.complex_order_strategy = ComplexOrderStrategy.IRON_CONDOR
        return self

    def straddle_strategy(self) -> "OrderBuilder":
        self.complex_order_strategy = ComplexOrderStrategy.STRADDLE
        return self

    def strangle_strategy(self) -> "OrderBuilder":
        self.complex_order_strategy = ComplexOrderStrategy.STRANGLE
        return self

    def one_triggers_other(self, child: "OrderBuilder") -> "OrderBuilder":
        self.order_strategy = OrderStrategy.TRIGGER
        self.child_orders.append(child)
        return self

    def one_cancels_other(self, other: "OrderBuilder") -> "OrderBuilder":
        self.order_strategy = OrderStrategy.OCO
        self.child_orders.append(other)
        return self

    def build(self) -> dict[str, Any]:
        self._validate()
        order: dict[str, Any] = {
            "session": self.session.value,
            "duration": self.duration.value,
            "orderType": (self.order_type or OrderPricing.MARKET).value,
            "orderStrategyType": self.order_strategy.value,
            "orderLegCollection": [
                {
                    "instruction": leg.instruction.value,
                    "quantity": leg.quantity,
                    "instrument": {
                        "symbol": leg.symbol,
                        "assetType": leg.asset_type.value,
                    },
                }
                for leg in self.legs
            ],
        }
        if self.complex_order_strategy != ComplexOrderStrategy.NONE:
            order["complexOrderStrategyType"] = self.complex_order_strategy.value
        if self.price is not None:
            order["price"] = self.price
        if self.stop_price is not None:
            order["stopPrice"] = self.stop_price
        if self.stop_price_link_basis is not None:
            order["stopPriceLinkBasis"] = self.stop_price_link_basis
        if self.stop_price_link_type is not None:
            order["stopPriceLinkType"] = self.stop_price_link_type
        if self.stop_price_offset is not None:
            order["stopPriceOffset"] = self.stop_price_offset
        if self.child_orders:
            order["childOrderStrategies"] = [child.build() for child in self.child_orders]
        return order

    def _set_quantity(self, quantity: int, unit: str) -> "OrderBuilder":
        if not self.legs:
            raise ValidationError(f"Must choose an action before setting {unit}")
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        self.legs[-1].quantity = quantity
        if unit == "shares" and quantity > 1000:
            self.warnings.append(f"Large equity order: {quantity} shares")
        if unit == "contracts" and quantity > 10:
            self.warnings.append(f"Large option order: {quantity} contracts")
        return self

    def _validate(self) -> None:
        if not self.legs:
            raise ValidationError("Order must have at least one leg")
        for leg in self.legs:
            if leg.quantity <= 0:
                raise ValidationError(f"Invalid quantity for {leg.symbol}: {leg.quantity}")
        if self.order_type in {OrderPricing.LIMIT, OrderPricing.NET_DEBIT, OrderPricing.NET_CREDIT}:
            if self.price is None:
                raise ValidationError(f"{self.order_type.value} orders require a price")
        if self.order_type == OrderPricing.STOP and self.stop_price is None:
            raise ValidationError("STOP orders require a stop price")
        if self.order_type == OrderPricing.STOP_LIMIT:
            if self.stop_price is None or self.price is None:
                raise ValidationError("STOP_LIMIT orders require stop and limit prices")
        if self.order_type == OrderPricing.TRAILING_STOP and self.stop_price_offset is None:
            raise ValidationError("TRAILING_STOP orders require an offset")

    @staticmethod
    def _format_price(price: float) -> str:
        if price <= 0:
            raise ValidationError("Price must be positive")
        precision = Decimal("0.0001") if abs(price) < 1 else Decimal("0.01")
        return str(Decimal(str(price)).quantize(precision, rounding=ROUND_DOWN))
