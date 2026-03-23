import backend
import asyncio
from java import static_proxy, jarray, jint, method, jvoid
from java.lang import String

class ProxyControl(static_proxy()):
    @method(jvoid, [String, jint, String])
    def start_proxy(self, p_host: str, p_port: int, p_dcip: str):
        # Reset stop event before starting (needed after stop_proxy was called)
        backend.STOP_EVENT.clear()

        cmd = ["--host", p_host, "--port", str(p_port)]
        dcips = p_dcip.strip().split("\n")
        for d in dcips:
            d = d.strip()
            if not d:
                continue
            # Support both "DC:IP" and plain "IP" formats.
            # If user entered just an IP, auto-detect the DC number from the known map.
            if ":" not in d:
                dc_found = None
                for ip, (dc_id, is_media) in backend._IP_TO_DC.items():
                    if ip == d and not is_media:
                        dc_found = dc_id
                        break
                if dc_found is not None:
                    d = f"{dc_found}:{d}"
                    print(f"[main] Auto-detected DC{dc_found} for IP {d.split(':', 1)[1]}")
                else:
                    print(f"[main] WARNING: Cannot auto-detect DC for '{d}', skipping. Use format DC:IP (e.g. 2:149.154.167.50)")
                    continue
            cmd.append("--dc-ip")
            cmd.append(d)

        print(f"[main] Starting proxy with args: {cmd}")
        backend.main(cmd)

    @method(jvoid, [])
    def stop_proxy(self):
        # Only set the event — do NOT call .clear() here.
        # The asyncio loop needs to observe the set state before we clear it.
        # STOP_EVENT is cleared at the top of start_proxy() on next launch.
        print("[main] Signalling proxy to stop...")
        backend.STOP_EVENT.set()
