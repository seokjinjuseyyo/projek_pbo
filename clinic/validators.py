"""Validasi input domain agar service dapat fokus mengatur alur bisnis."""

import math

from . import db
from .models import Medicine


def required(data, key, limit=4000):
    value = str(data.get(key, '')).strip()
    if not value or len(value) > limit:
        raise ValueError(f'{key.replace("_", " ").capitalize()} wajib diisi (maks. {limit} karakter).')
    return value


def number(data, key, minimum, maximum, integer=False):
    try:
        value = float(data.get(key, ''))
    except (ValueError, TypeError):
        raise ValueError(f'{key} harus berupa angka.')
    if not math.isfinite(value) or not minimum <= value <= maximum or (integer and not value.is_integer()):
        raise ValueError(f'{key} harus antara {minimum} dan {maximum}.')
    return int(value) if integer else value


class NursingAssessmentValidator:
    RANGES = {
        'systolic': (40, 300, True),
        'diastolic': (20, 200, True),
        'temperature': (30, 45, False),
        'weight': (1, 500, False),
        'height': (30, 250, False),
        'pulse': (20, 250, True),
        'respiration': (1, 100, True),
        'spo2': (1, 100, True),
        'pain': (0, 10, True),
    }

    @classmethod
    def validate(cls, data):
        values = {
            key: number(data, key, minimum, maximum, integer)
            for key, (minimum, maximum, integer) in cls.RANGES.items()
        }
        values['complaint'] = required(data, 'complaint')
        values['notes'] = data.get('notes', '')[:4000]
        return values


class DoctorExaminationValidator:
    @staticmethod
    def validate(data):
        fields = {key: required(data, key) for key in ('anamnesis', 'physical', 'diagnosis')}
        for key in ('assessment', 'secondary', 'icd10', 'treatment', 'notes',
                    'recommendation', 'followup', 'laboratory'):
            fields[key] = str(data.get(key, ''))[:4000]
        fields['treatment_fee'] = number(data, 'treatment_fee', 0, 100000000, True)
        return fields


class PrescriptionValidator:
    @staticmethod
    def validate(items):
        validated = []
        seen = set()
        for item in items:
            medicine = db.session.get(Medicine, number(item, 'medicine_id', 1, 1000000, True))
            if not medicine or medicine.id in seen:
                raise ValueError('Obat tidak valid atau duplikat. Gabungkan jumlahnya.')
            seen.add(medicine.id)
            validated.append({
                'medicine': medicine,
                'quantity': number(item, 'quantity', 1, 10000, True),
                'price': medicine.price,
                **{key: required(item, key, 80) for key in ('dosage', 'frequency', 'duration', 'timing')},
                'instruction': str(item.get('instruction', ''))[:300],
            })
        return validated
