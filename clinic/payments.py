"""Strategi penanggung pembayaran dan resolver yang dapat diperluas."""

from .interfaces import PaymentProcessor, PaymentProcessorResolver


def _validated_total(total):
    if isinstance(total, bool) or not isinstance(total, (int, float)) or total < 0:
        raise ValueError('Total tagihan harus berupa angka non-negatif.')
    return total


class GeneralPayment(PaymentProcessor):
    def amounts(self, total):
        total = _validated_total(total)
        return 0, total


class BPJSPayment(PaymentProcessor):
    def amounts(self, total):
        total = _validated_total(total)
        return total, 0


class PaymentProcessorRegistry(PaymentProcessorResolver):
    """Registry sederhana; strategi baru dapat didaftarkan tanpa mengubah billing."""

    def __init__(self, selector=None):
        self._selector = selector or self._default_selector
        self._processor_types = {}

    @staticmethod
    def _default_selector(appointment):
        return 'bpjs' if appointment.insurance else 'general'

    def register(self, coverage_type, processor_type):
        if not isinstance(processor_type, type) or not issubclass(processor_type, PaymentProcessor):
            raise TypeError('Processor harus mengimplementasikan PaymentProcessor.')
        self._processor_types[coverage_type] = processor_type
        return self

    def resolve(self, appointment):
        coverage_type = self._selector(appointment)
        try:
            processor_type = self._processor_types[coverage_type]
        except KeyError as error:
            raise ValueError('Jenis penanggung pembayaran tidak didukung.') from error
        return processor_type()


def create_default_payment_resolver():
    return (PaymentProcessorRegistry()
            .register('general', GeneralPayment)
            .register('bpjs', BPJSPayment))
