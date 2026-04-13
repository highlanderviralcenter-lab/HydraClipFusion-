"""
Detecção de hardware - V2
"""

import subprocess
import os

class HardwareDetector:
    def __init__(self):
        self.info = self._detect_all()

    def _detect_all(self):
        return {
            'cpu': self._detect_cpu(),
            'gpu': self._detect_gpu(),
            'ram_gb': self._detect_ram(),
            'encoder': self._detect_encoder(),
            'vaapi': self._check_vaapi(),
        }

    def _detect_cpu(self):
        try:
            with open('/proc/cpuinfo') as f:
                lines = f.readlines()
            model, cores = "", 0
            for line in lines:
                if 'model name' in line and not model:
                    model = line.split(':')[1].strip()
                if 'processor' in line:
                    cores += 1
            return {'model': model, 'cores': cores}
        except:
            return {'model': 'i5-6200U', 'cores': 4}

    def _detect_gpu(self):
        gpu_info = {'intel': False, 'nvidia': False}
        try:
            r = subprocess.run(['lspci'], capture_output=True, text=True)
            if 'HD Graphics' in r.stdout or 'UHD' in r.stdout:
                gpu_info['intel'] = True
        except: pass
        return gpu_info

    def _detect_ram(self):
        try:
            with open('/proc/meminfo') as f:
                line = f.readline()
            kb = int(line.split()[1])
            return round(kb / 1024 / 1024, 1)
        except:
            return 8.0

    def _detect_encoder(self):
        return 'h264_vaapi' if self._check_vaapi()['disponivel'] else 'libx264'

    def _check_vaapi(self):
        try:
            r = subprocess.run(['vainfo'], capture_output=True, text=True)
            return {'disponivel': 'VAEntrypointEncSlice' in r.stdout}
        except:
            return {'disponivel': False}

    def get_status_string(self):
        enc = 'VA-API' if self.info['vaapi']['disponivel'] else 'CPU'
        return f"{enc} | {self.info['cpu']['model']} | {self.info['ram_gb']}GB"

def check_system():
    print("🔍 Verificando sistema...")
    hw = HardwareDetector()
    print(f"   CPU: {hw.info['cpu']['model']}")
    print(f"   RAM: {hw.info['ram_gb']}GB")
    print(f"   GPU Intel: {'✅' if hw.info['gpu']['intel'] else '❌'}")
    print(f"   VA-API: {'✅' if hw.info['vaapi']['disponivel'] else '❌'}")
    print("✅ Sistema pronto!")
