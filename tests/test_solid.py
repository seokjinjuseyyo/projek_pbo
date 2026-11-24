from types import SimpleNamespace

import pytest

from clinic.interfaces import PaymentProcessor, PaymentProcessorResolver
from clinic.payments import BPJSPayment, GeneralPayment, PaymentProcessorRegistry
from clinic.services import BillingService


@pytest.mark.parametrize('processor_type', [GeneralPayment, BPJSPayment])
def test_payment_processors_follow_the_same_contract(processor_type):
    processor: PaymentProcessor = processor_type()
    coverage, payable = processor.amounts(125_000)

    assert coverage >= 0
    assert payable >= 0
    assert coverage + payable == 125_000


def test_payment_registry_is_open_for_an_additional_strategy():
    class CorporatePayment(PaymentProcessor):
        def amounts(self, total):
            return total // 2, total - total // 2

    registry = PaymentProcessorRegistry(selector=lambda appointment: appointment.coverage_type)
    registry.register('corporate', CorporatePayment)

    processor = registry.resolve(SimpleNamespace(coverage_type='corporate'))
    assert isinstance(processor, PaymentProcessor)
    assert processor.amounts(100_000) == (50_000, 50_000)


def test_billing_service_depends_on_payment_resolver_contract():
    class StubResolver(PaymentProcessorResolver):
        def __init__(self):
            self.received = None

        def resolve(self, appointment):
            self.received = appointment
            return GeneralPayment()

    appointment = SimpleNamespace(insurance=False)
    resolver = StubResolver()
    service = BillingService(resolver)

    assert service._amounts(appointment, 80_000) == (0, 80_000)
    assert resolver.received is appointment


def test_payment_interfaces_remain_small_and_specific():
    assert PaymentProcessor.__abstractmethods__ == frozenset({'amounts'})
    assert PaymentProcessorResolver.__abstractmethods__ == frozenset({'resolve'})
