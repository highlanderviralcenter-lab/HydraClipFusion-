cat > /usr/local/bin/clipfusion-monitor.sh <<'EOF'
#!/usr/bin/env bash
watch -n 1 '
echo "================ CLIPFUSION MONITOR ================"
echo
echo "[TEMPERATURA]"
sensors 2>/dev/null | egrep "Core 0|Core 1|Package id 0|Tctl|temp1" || echo "sensors sem leitura útil"
echo
echo "[CLOCK CPU]"
grep "cpu MHz" /proc/cpuinfo | nl
echo
echo "[GOVERNOR / FREQ INFO]"
cpupower frequency-info 2>/dev/null | egrep "current CPU frequency|The governor|boost state support|boost state" || true
echo
echo "[THROTTLING]"
grep . /sys/devices/system/cpu/cpu*/thermal_throttle/* 2>/dev/null || echo "sem contador disponível"
echo
echo "[LOAD]"
uptime
echo
echo "[MEMÓRIA / SWAP / ZRAM]"
free -h
echo
swapon --show
echo
echo "[TURBO / PSTATE]"
cat /sys/devices/system/cpu/intel_pstate/status 2>/dev/null || true
cat /sys/devices/system/cpu/intel_pstate/max_perf_pct 2>/dev/null || true
echo
echo "[TOP PROCESSOS]"
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head
echo
echo "===================================================="
'
EOF

chmod +x /usr/local/bin/clipfusion-monitor.sh
