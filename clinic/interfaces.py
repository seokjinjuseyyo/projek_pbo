"""Kontrak kecil untuk dependency yang memang memiliki lebih dari satu implementasi."""

from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Kontrak strategi penanggung tagihan.

    Implementasi harus menerima total non-negatif dan mengembalikan tuple
    ``(coverage, payable)`` berupa angka non-negatif dengan jumlah sama dengan
    total. Cara transaksi (Tunai, Transfer, QRIS, atau Debit) bukan bagian dari
    kontrak ini.
    """

    @abstractmethod
    def amounts(self, total):
        """Mengembalikan ``(tanggungan, jumlah yang dibayar pasien)``."""


class PaymentProcessorResolver(ABC):
    """Kontrak untuk memilih processor berdasarkan data appointment."""

    @abstractmethod
    def resolve(self, appointment):
        """Mengembalikan sebuah ``PaymentProcessor`` untuk appointment."""
