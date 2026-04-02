from __future__ import annotations

from abc import ABC, abstractmethod


class ServoHardwareAdapter(ABC):
    @abstractmethod
    def write_angle(self, channel: int, angle: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict[str, object]:
        raise NotImplementedError


class NoOpServoAdapter(ServoHardwareAdapter):
    def __init__(self) -> None:
        self._last_write: dict[str, int] | None = None

    def write_angle(self, channel: int, angle: int) -> None:
        self._last_write = {"channel": channel, "angle": angle}

    def health(self) -> dict[str, object]:
        return {"adapter": "noop", "ready": True, "last_write": self._last_write}


class PCA9685ServoAdapter(ServoHardwareAdapter):
    def __init__(self, i2c_bus: int, i2c_address: int, pwm_frequency: int) -> None:
        self._i2c_bus = i2c_bus
        self._i2c_address = i2c_address
        self._pwm_frequency = pwm_frequency
        self._last_write: dict[str, int] | None = None
        try:
            import smbus2  # type: ignore

            self._bus = smbus2.SMBus(i2c_bus)
            self._ready = True
        except Exception as exc:
            self._bus = None
            self._ready = False
            self._error = str(exc)
            return

        # MODE1 reset + prescale setup (pca9685 common flow)
        self._write_reg(0x00, 0x00)
        prescale = int(round(25000000.0 / (4096 * pwm_frequency)) - 1)
        old_mode = self._read_reg(0x00)
        self._write_reg(0x00, (old_mode & 0x7F) | 0x10)
        self._write_reg(0xFE, prescale)
        self._write_reg(0x00, old_mode)
        self._write_reg(0x00, old_mode | 0xA1)

    def _write_reg(self, reg: int, value: int) -> None:
        if self._bus:
            self._bus.write_byte_data(self._i2c_address, reg, value)

    def _read_reg(self, reg: int) -> int:
        if not self._bus:
            return 0
        return int(self._bus.read_byte_data(self._i2c_address, reg))

    def write_angle(self, channel: int, angle: int) -> None:
        if not self._ready:
            raise RuntimeError("pca9685 adapter unavailable")
        pulse_us = int(500 + (angle / 180.0) * 2000)
        ticks = int(pulse_us * 4096 * self._pwm_frequency / 1_000_000)
        base = 0x06 + (4 * channel)
        self._write_reg(base, 0)
        self._write_reg(base + 1, 0)
        self._write_reg(base + 2, ticks & 0xFF)
        self._write_reg(base + 3, (ticks >> 8) & 0x0F)
        self._last_write = {"channel": channel, "angle": angle}

    def health(self) -> dict[str, object]:
        info = {
            "adapter": "pca9685",
            "ready": self._ready,
            "i2c_bus": self._i2c_bus,
            "i2c_address": hex(self._i2c_address),
            "pwm_frequency": self._pwm_frequency,
            "last_write": self._last_write,
        }
        if not self._ready:
            info["error"] = getattr(self, "_error", "unknown")
        return info
