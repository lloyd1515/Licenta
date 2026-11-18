"""Genereaza notite_curs_main.md: main.c explicat linie cu linie, in ordinea executiei,
cu fragmente exacte din ESP-IDF (header, .c) si din bibliotecile inchise (objdump).
Rulare: bash unelte/genereaza_curs.sh"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snip import IDF, DOCS, read, src, snippet, whole  # noqa: E402

DIS, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
PAS = os.path.join(HERE, "..", "pas_cu_pas")
MAIN = os.path.join(PAS, "main", "main.c")
KCONF = os.path.join(PAS, "main", "Kconfig.projbuild")
LOG = os.path.join(PAS, "output", "07_main_nou.log")
WIFI_RST = os.path.join(DOCS, "wifi.rst")
M = "pas_cu_pas/main/main.c"
JL = "pas_cu_pas/output/07_main_nou.log"


def dis(name):
    return os.path.join(DIS, name + ".txt")


DOC, SEC, SUB = [], [0], [0]


def text(s):
    DOC.append(s.strip("\n") + "\n")


def section(title, lines=None):
    SEC[0] += 1
    SUB[0] = 0
    DOC.append("---\n\n## %d. %s\n" % (SEC[0], title) + ("\n`main.c`: %s\n" % lines if lines else ""))


def snip(title, label, path, ranges, marks, numbered=True, intro=None):
    SUB[0] += 1
    DOC.append(snippet("%d.%d %s" % (SEC[0], SUB[0], title), label, path, ranges, marks, numbered, intro))


# ---------------------------------------------------------------- inceput
text("""
# Notițe de curs – `main.c` de la zero, în ordinea execuției

11 Nov 2026 · ESP-IDF v5.1.7 · Cod: `pas_cu_pas/main/main.c` (107 linii) · Jurnal: `pas_cu_pas/output/07_main_nou.log`

Aceste notițe înlocuiesc toate notițele de curs anterioare (pașii 1–3 și header-ele).

## Cum citești notițele

- Secțiunile urmează **ordinea în care rulează programul**: pornirea plăcii, `app_main`, apoi funcțiile pe care le apelează driverul.
- Pentru fiecare linie din `main.c`: ce face, ce rol are, de unde vine informația.
- Pentru fiecare funcție ESP-IDF coborâm cât se poate de jos: header (`.h`), cod deschis (`.c`), apoi instrucțiuni mașină din bibliotecile închise (`.a`), până la regiștrii hardware.
- Toate fragmentele sunt copiate exact din fișiere de scriptul `unelte/gen_curs.py`. Numărul din stânga = linia din fișier. `...` = linii omise.
- Text marcat = important. `[n]` = explicația n de sub fragment.
- `IDF` = `~/esp/esp-idf/components`.

### Trei feluri de cod

| Fel | Unde | Ce vedem |
|---|---|---|
| Header `.h` | `IDF/*/include/` | **Contractul**: ce face funcția, parametrii, erorile. |
| Cod deschis `.c` | `IDF/*/` | **Implementarea**, linie cu linie. |
| Cod închis `.a` | `IDF/esp_wifi/lib/esp32/` (`libnet80211.a`, `libpp.a`, `libphy.a`) | Doar numele funcțiilor și instrucțiunile mașină (`objdump`). |

### Cum citești instrucțiunile mașină Xtensa (ESP32)

| Instrucțiune | Ce face |
|---|---|
| `l32r a8, ...` | Încarcă în registrul `a8` o constantă din tabelul de deasupra funcției („literal pool”). |
| `callx8 a8` | Apelează funcția de la adresa din `a8`. Linia `R_XTENSA_ASM_EXPAND nume` arată care funcție. |
| `l32i` / `s32i` | Citește / scrie 4 octeți din memorie. `l8ui` / `s8i` = 1 octet. |
| `memw` | Barieră: scrierile anterioare ajung în memorie înainte de continuare. |
| `beqz a10, X` | Sare la `X` dacă `a10 == 0`. |
| `a10`, `a11`, ... | Primul, al doilea, ... argument al funcției apelate. Rezultatul revine în `a10`. |
| `a2`, `a3`, ... | În funcția curentă: primul, al doilea, ... argument primit. Rezultatul pleacă în `a2`. |

### Harta execuției

```
pornire placă ──► cpu_start: memoria .bss = 0 (variabilele static din main.c)
              ──► main_task ──► app_main()                         secțiunile 3–16
                                  ├─ pornește Wi-Fi, IP, evenimente
                                  ├─ înregistrează on_event și on_csi
                                  └─ return  (main_task se șterge)
task sys_evt   ──► on_event(STA_START)  ──► esp_wifi_connect()        secțiunea 17
task sys_evt   ──► on_event(GOT_IP)     ──► start_ping()              secțiunile 18–19
task ping      ──► ping la 20 ms ──► telefonul răspunde
task Wi-Fi     ──► fiecare răspuns ──► hardware calculează CSI ──► on_csi(info)   secțiunile 20–22
```

### Task-urile (fire de execuție FreeRTOS)

| Task | Prioritate | Ce rulează din codul nostru | Cine îl creează |
|---|---|---|---|
| `main` | 1 | `app_main` | pornirea ESP-IDF (`app_startup.c`) |
| `sys_evt` | 20 (`ESP_TASK_PRIO_MAX - 5` = 25 − 5) | `on_event` | `esp_event_loop_create_default` |
| `tiT` | 18 (`CONFIG_LWIP_TCPIP_TASK_PRIO`) | – (stiva IP, DHCP) | `esp_netif_init` |
| Wi-Fi | 23 | `on_csi` | `esp_wifi_init` |
| `ping` | 2 | – (ping-urile) | `esp_ping_new_session` |
""")

snip("Tot fișierul `main.c`", M, MAIN, whole(MAIN), [], intro="Fișierul complet, ca referință. Explicațiile pe linii sunt în secțiunile următoare.")

# ---------------------------------------------------------------- 1. pornirea
section("Înainte de `app_main`: pornirea plăcii")
text("""
Placa nu începe cu `app_main`. Mai întâi rulează codul ROM, bootloader-ul și codul de pornire ESP-IDF. Acesta pregătește memoria, pornește FreeRTOS și creează task-ul `main`.
""")
snip("Memoria `.bss` devine 0", "IDF/esp_system/port/cpu_start.c", src("esp_system/port/cpu_start.c"), [(348, 349)], [
    ("Clear BSS", "Clear BSS", "`.bss` = zona de memorie pentru variabilele globale și `static` fără valoare inițială."),
    ("memset(&_bss_start", "memset(&_bss_start, 0", "Toată zona devine 0. De aceea `packets`, `rssi_total`, `second_start_us` și `amplitude_total[]` din `main.c` încep de la 0."),
])
snip("Cine creează task-ul `main`", "IDF/freertos/app_startup.c", src("freertos/app_startup.c"), [(83, 85)], [
    ("xTaskCreatePinnedToCore(main_task", 'xTaskCreatePinnedToCore(main_task, "main"', "Un task FreeRTOS cu numele `main`. El va rula funcția `main_task`."),
    ("ESP_TASK_MAIN_STACK", "ESP_TASK_MAIN_STACK", "Stiva: 3584 (`CONFIG_ESP_MAIN_TASK_STACK_SIZE`) + 512 = 4096 de octeți. Variabilele locale din `app_main` (`wifi_init`, `hotspot`) stau aici."),
    ("ESP_TASK_MAIN_PRIO", "ESP_TASK_MAIN_PRIO", "Prioritatea 1 (`ESP_TASK_PRIO_MIN + 1`): foarte mică."),
])
snip("`main_task` apelează `app_main`", "IDF/freertos/app_startup.c", src("freertos/app_startup.c"), [(158, 158), (206, 210)], [
    ("static void main_task", "main_task", "Funcția task-ului `main`."),
    ("Calling app_main()", '"Calling app_main()"', "Prima linie a noastră din jurnal: `I (539) main_task: Calling app_main()`."),
    ("extern void app_main", "extern void app_main(void)", "`extern` = funcția este definită în alt fișier: `main.c`. Numele trebuie să fie exact `app_main`."),
    ("app_main();", "app_main();", "**Aici începe codul nostru.**"),
    ("Returned from app_main", '"Returned from app_main()"', "Apare după ce `app_main` se termină (linia 29 din jurnal)."),
    ("vTaskDelete(NULL)", "vTaskDelete(NULL)", "Task-ul `main` se șterge singur. Programul continuă în celelalte task-uri."),
])

# ---------------------------------------------------------------- 2. compilare
section("Începutul fișierului: `#include`, `TAG`, variabilele `static`", "liniile 1–18")
text("""
Aceste linii nu „rulează” ca instrucțiuni. Compilatorul le folosește când construiește programul. Variabilele există în memorie de la pornire (secțiunea 1).
""")
snip("Header-ele", M, MAIN, [(1, 10)], [
    ("// CSI pe ESP32", "// CSI pe ESP32", "Comentariu: compilatorul îl ignoră."),
    ("esp_log.h", '"esp_log.h"', "`#include` copiază textul header-ului aici. De aici vin `ESP_LOGI` și nivelurile jurnalului (secțiunea 3)."),
    ("esp_wifi.h", '"esp_wifi.h"', "Toate funcțiile `esp_wifi_*` și tipurile `wifi_*` (prin `esp_wifi_types.h`)."),
    ("esp_event.h", '"esp_event.h"', "Bucla de evenimente: `esp_event_*`, `esp_event_base_t`."),
    ("nvs_flash.h", '"nvs_flash.h"', "`nvs_flash_init`: memoria flash pentru setări."),
    ("esp_netif.h", '"esp_netif.h"', "Interfața de rețea: `esp_netif_*`, `IP_EVENT`, `IPSTR`."),
    ("esp_mac.h", '"esp_mac.h"', "`MACSTR`, `MAC2STR`. În versiunea finală nu le mai folosim. Linia a rămas din etapa 4."),
    ("esp_timer.h", '"esp_timer.h"', "`esp_timer_get_time`: ceasul în microsecunde (secțiunea 22)."),
    ("ping/ping_sock.h", '"ping/ping_sock.h"', "Ping-ul din lwIP: `esp_ping_*` (secțiunea 19)."),
    ("<math.h>", "<math.h>", "Biblioteca standard C: `sqrtf`. `< >` = header de sistem, `\" \"` = header de proiect sau ESP-IDF."),
])
snip("`TAG` și sumele", M, MAIN, [(12, 18)], [
    ("static const char *TAG", "static", "`static` în afara funcțiilor: variabila este vizibilă doar în `main.c`."),
    ("static const char *TAG", "const char *TAG", "Un pointer la un text constant. Textul `\"CSI\"` stă în memoria flash."),
    ("static const char *TAG", '"CSI"', "Eticheta din jurnal: `I (539) CSI: ...`."),
    ("static int     packets;", "packets", "Câte CSI au venit în secunda curentă. Crește în `on_csi`, revine la 0 o dată pe secundă."),
    ("static int     rssi_total;", "rssi_total", "Suma RSSI din secunda curentă. Împărțită la `packets` = RSSI mediu."),
    ("static int64_t second_start_us;", "int64_t second_start_us", "Momentul de început al secundei curente, în µs. `int64_t` = întreg cu semn pe 64 de biți, ca ceasul."),
    ("static float   amplitude_total[53];", "amplitude_total[53]", "53 de sume `float`, una pentru fiecare k de la −26 la +26. k = −26 → poziția 0, k = +26 → poziția 52."),
])
text("""
De ce `static` pentru sume: o variabilă locală dispare la `return`. `on_csi` este apelată de 50 de ori pe secundă. Sumele trebuie să rămână între apeluri. Doar `on_csi` (task-ul Wi-Fi) le folosește, deci nu avem nevoie de mutex.
""")

# ---------------------------------------------------------------- 3. ESP_LOGI
section("Prima linie din `app_main`: `ESP_LOGI`", "liniile 84–85")
snip("Codul nostru", M, MAIN, [(84, 85)], [
    ("void app_main(void)", "void app_main(void)", "Fără parametri, fără rezultat. Numele este cerut de `main_task` (1.3)."),
    ("ESP_LOGI(TAG", "ESP_LOGI(TAG, \"Salut! app_main a pornit.\")", "Scrie linia 2 din jurnal: `I (539) CSI: Salut! app_main a pornit.`"),
])
LOGH = src("log/include/esp_log.h")
snip("`ESP_LOGI` este un macro", "IDF/log/include/esp_log.h", LOGH, [(342, 342)], [
    ("define ESP_LOGI", "ESP_LOG_LEVEL_LOCAL(ESP_LOG_INFO", "Compilatorul înlocuiește `ESP_LOGI(...)` cu acest text. Adaugă nivelul `ESP_LOG_INFO`."),
])
snip("Nivelurile", "IDF/log/include/esp_log.h", LOGH, [(24, 31)], [
    ("ESP_LOG_NONE", "ESP_LOG_NONE", "0 = nimic."),
    ("ESP_LOG_INFO", "ESP_LOG_INFO", "3 = informații. `CONFIG_LOG_DEFAULT_LEVEL=3` în `sdkconfig`: liniile INFO apar."),
    ("ESP_LOG_DEBUG", "ESP_LOG_DEBUG", "4 = depanare. Nu apar la noi."),
])
snip("Filtrul la compilare", "IDF/log/include/esp_log.h", LOGH, [(431, 433)], [
    ("LOG_LOCAL_LEVEL >= level", "if ( LOG_LOCAL_LEVEL >= level )", "Dacă nivelul maxim permis este mai mic, compilatorul elimină tot apelul."),
])
snip("Ce scrie de fapt: `esp_log_write` cu un format", "IDF/log/include/esp_log.h", LOGH, [(282, 282), (408, 415)], [
    ("define LOG_FORMAT", 'LOG_COLOR_ ## letter #letter " (%" PRIu32 ") %s: " format', "Formatul liniei: culoare, litera (`I`), `(timp)`, `TAG:`, apoi textul nostru. Exact `I (539) CSI: Salut!...`."),
    ("define LOG_FORMAT", 'LOG_RESET_COLOR "\\n"', "La final: culoarea normală și sfârșitul liniei. De aici vin `[0m` din jurnalul brut."),
    ("#if CONFIG_LOG_TIMESTAMP_SOURCE_RTOS", "CONFIG_LOG_TIMESTAMP_SOURCE_RTOS", "Varianta aleasă în `sdkconfig`: timpul vine de la FreeRTOS."),
    ("else                                { esp_log_write(ESP_LOG_INFO", "esp_log_write(ESP_LOG_INFO,       tag, LOG_FORMAT(I, format), esp_log_timestamp(), tag", "Pentru INFO: `esp_log_write` primește formatul, timpul (`esp_log_timestamp`) și `TAG`."),
])
snip("Timpul din paranteză", "IDF/log/log_freertos.c", src("log/log_freertos.c"), [(99, 110)], [
    ("TickType_t tick_count", "xTaskGetTickCount()", "Numărul de tick-uri FreeRTOS de la pornire."),
    ("return base + tick_count", "tick_count * (1000 / configTICK_RATE_HZ)", "Tick-uri × 10 ms (100 Hz) = milisecunde. De aceea timpii din jurnal se termină des în 9 sau 0."),
])
snip("`esp_log_write` → `vprintf` → portul serial", "IDF/log/log.c", src("log/log.c"), [(66, 66), (184, 208)], [
    ("s_log_print_func = &vprintf", "&vprintf", "Implicit, jurnalul folosește `vprintf` din biblioteca C. Ieșirea standard este UART0 = cablul USB."),
    ("esp_log_impl_lock_timeout", "esp_log_impl_lock_timeout()", "Un singur task scrie la un moment dat. Liniile nu se amestecă."),
    ("should_output", "should_output(level, level_for_tag)", "A doua verificare a nivelului, la rulare."),
    ("(*s_log_print_func)", "(*s_log_print_func)(format, args)", "Scrie textul. La 115200 baud, o linie de 80 de caractere durează cam 7 ms."),
])

# ---------------------------------------------------------------- 4. ESP_ERROR_CHECK
section("`ESP_ERROR_CHECK` – învelește aproape fiecare apel", "liniile 88–106")
text("""
Funcțiile ESP-IDF întorc `esp_err_t`: `ESP_OK` (0) sau un cod de eroare. `ESP_ERROR_CHECK` verifică rezultatul.
""")
snip("`ESP_ERROR_CHECK`", "IDF/esp_common/include/esp_err.h", src("esp_common/include/esp_err.h"), [(116, 123)], [
    ("esp_err_t err_rc_ = (x)", "esp_err_t err_rc_ = (x)", "Rulează apelul o singură dată și păstrează rezultatul."),
    ("unlikely", "err_rc_ != ESP_OK", "Verifică eroarea. `unlikely` spune compilatorului: cazul este rar."),
    ("_esp_error_check_failed", "_esp_error_check_failed(err_rc_, __FILE__, __LINE__,", "Afișează codul, fișierul și linia. Apoi `abort()`: placa repornește."),
    ("#x", "#x", "`#x` = textul apelului. Mesajul arată exact ce linie din `main.c` a eșuat."),
])
text("""
Linia 91 (`esp_netif_create_default_wifi_sta`) nu are `ESP_ERROR_CHECK`. Funcția nu întoarce `esp_err_t`. La eroare, ea oprește singură programul (secțiunea 8).
""")

# ---------------------------------------------------------------- 5. nvs
section("`nvs_flash_init()` – memoria pentru setări", "linia 88")
snip("Header", "IDF/nvs_flash/include/nvs_flash.h", src("nvs_flash/include/nvs_flash.h"), [(35, 39), (55, 58), (65, 65)], [
    ("labeled", 'labeled "nvs"', "Funcția caută partiția cu numele `nvs` din tabelul de partiții al memoriei flash."),
    ("ESP_ERR_NVS_NO_FREE_PAGES", "ESP_ERR_NVS_NO_FREE_PAGES", "Partiția este plină. Soluția obișnuită: `nvs_flash_erase()`, apoi din nou `init`."),
    ("ESP_ERR_NOT_FOUND", "ESP_ERR_NOT_FOUND", "Tabelul de partiții nu are partiția `nvs`."),
])
snip("Implementare", "IDF/nvs_flash/src/nvs_api.cpp", src("nvs_flash/src/nvs_api.cpp"), [(128, 129), (160, 163)], [
    ("#else", "#else // CONFIG_NVS_ENCRYPTION", "Proiectul nu are criptare NVS. Rulează doar ramura de mai jos."),
    ("nvs_flash_init_partition", "nvs_flash_init_partition(NVS_DEFAULT_PART_NAME)", "Tot lucrul real: inițializează partiția `\"nvs\"`."),
])
text("""
**Rol în program:** driverul Wi-Fi salvează în `nvs` calibrarea radio și setările (`config NVS flash: enabled`, linia 6 din jurnal). Fără `nvs_flash_init`, `esp_wifi_init` eșuează.
""")

# ---------------------------------------------------------------- 6. netif
section("`esp_netif_init()` – stiva TCP/IP", "linia 89")
snip("Header", "IDF/esp_netif/include/esp_netif.h", src("esp_netif/include/esp_netif.h"), [(31, 40)], [
    ("@brief", "Initialize the underlying TCP/IP stack", "Pornește stiva TCP/IP (lwIP)."),
    ("exactly once", "exactly once", "Un singur apel, la pornirea aplicației."),
])
snip("Implementare", "IDF/esp_netif/lwip/esp_netif_lwip.c", src("esp_netif/lwip/esp_netif_lwip.c"), [(533, 547)], [
    ("sys_sem_new", "sys_sem_new(&init_sem, 0)", "Creează un semafor închis. Funcția va aștepta la el."),
    ("tcpip_init(", "tcpip_init(tcpip_init_done, &init_sem)", "lwIP pornește task-ul `tiT`. La final, `tcpip_init_done` deschide semaforul."),
    ("sys_sem_wait", "sys_sem_wait(&init_sem)", "`app_main` așteaptă aici până când stiva IP este gata."),
])
snip("Numele task-ului lwIP", "IDF/lwip/port/include/lwipopts.h", src("lwip/port/include/lwipopts.h"), [(810, 810)], [
    ("TCPIP_THREAD_NAME", '"tiT"', "Task-ul care procesează pachetele IP (DHCP, ICMP) se numește `tiT`."),
])

# ---------------------------------------------------------------- 7. event loop
section("`esp_event_loop_create_default()` – bucla de evenimente", "linia 90")
snip("Header", "IDF/esp_event/include/esp_event.h", src("esp_event/include/esp_event.h"), [(60, 70)], [
    ("Create default event loop", "Create default event loop", "Bucla folosită de driverul Wi-Fi și de stiva IP."),
    ("ESP_ERR_INVALID_STATE", "ESP_ERR_INVALID_STATE", "Al doilea apel eșuează. Bucla implicită există o singură dată."),
])
snip("Implementare", "IDF/esp_event/default_event_loop.c", src("esp_event/default_event_loop.c"), [(94, 115)], [
    ("if (s_default_loop)", "if (s_default_loop)", "Dacă bucla există deja, întoarce eroare."),
    (".queue_size", "CONFIG_ESP_SYSTEM_EVENT_QUEUE_SIZE", "Coada are 32 de locuri. Evenimentele așteaptă aici."),
    (".task_name", '"sys_evt"', "Numele task-ului care va apela `on_event`."),
    (".task_priority", "ESP_TASKD_EVENT_PRIO", "Prioritate `ESP_TASK_PRIO_MAX - 5` = 25 − 5 = 20: mai mică decât task-ul Wi-Fi (23)."),
    (".task_core_id", ".task_core_id = 0", "Task-ul rulează pe nucleul 0, ca task-ul Wi-Fi."),
    ("esp_event_loop_create(", "esp_event_loop_create(&loop_args, &s_default_loop)", "Creează coada și task-ul. Salvează bucla în `s_default_loop`."),
])

# ---------------------------------------------------------------- 8. netif sta
section("`esp_netif_create_default_wifi_sta()` – legătura Wi-Fi ↔ IP", "linia 91")
snip("Header", "IDF/esp_wifi/include/esp_wifi_default.h", src("esp_wifi/include/esp_wifi_default.h"), [(85, 95)], [
    ("this API aborts", "this API aborts", "Funcția nu întoarce erori. La eroare, oprește programul. De aceea nu are `ESP_ERROR_CHECK`."),
    ("attaches the netif", "attaches the netif to wifi", "Leagă interfața IP de driverul Wi-Fi."),
    ("registers wifi handlers", "registers wifi handlers to the default event loop", "Înregistrează funcțiile ESP-IDF pentru evenimente. De aici vine linia `sta ip:` din jurnal."),
    ("needs to be created prior", "default event loop needs to be created prior", "Bucla de evenimente trebuie creată înainte: ordinea liniilor 90 și 91 contează."),
])
snip("Implementare", "IDF/esp_wifi/src/wifi_default.c", src("esp_wifi/src/wifi_default.c"), [(385, 393)], [
    ("ESP_NETIF_DEFAULT_WIFI_STA", "ESP_NETIF_DEFAULT_WIFI_STA()", "Setările implicite pentru stație: client DHCP pornit."),
    ("esp_netif_new", "esp_netif_new(&cfg)", "Creează interfața de rețea."),
    ("assert(netif)", "assert(netif)", "Acesta este „abort” din header."),
    ("attach_wifi_station", "esp_netif_attach_wifi_station(netif)", "Pachetele primite prin Wi-Fi ajung la stiva IP prin această legătură."),
    ("set_default_wifi_sta_handlers", "esp_wifi_set_default_wifi_sta_handlers()", "Reacțiile ESP-IDF la conectare, deconectare și IP."),
])

# ---------------------------------------------------------------- 9. wifi init
section("`WIFI_INIT_CONFIG_DEFAULT()` și `esp_wifi_init()` – driverul Wi-Fi", "liniile 92–93")
snip("Codul nostru", M, MAIN, [(92, 93)], [
    ("wifi_init_config_t wifi_init", "wifi_init_config_t wifi_init", "Variabilă locală pe stiva lui `app_main`. Driverul copiază setările, deci poate dispărea după `return`."),
    ("WIFI_INIT_CONFIG_DEFAULT()", "WIFI_INIT_CONFIG_DEFAULT()", "Macro: completează toate câmpurile cu valori din `sdkconfig`."),
    ("esp_wifi_init(&wifi_init)", "&wifi_init", "Trimitem adresa structurii, nu o copie."),
])
WH = src("esp_wifi/include/esp_wifi.h")
snip("`WIFI_INIT_CONFIG_DEFAULT` și `WIFI_CSI_ENABLED`", "IDF/esp_wifi/include/esp_wifi.h", WH, [(146, 150), (283, 287), (294, 294), (298, 298), (307, 308)], [
    ("#if CONFIG_ESP_WIFI_CSI_ENABLED", "CONFIG_ESP_WIFI_CSI_ENABLED", "Vine din `sdkconfig.defaults` al proiectului. Fără el, CSI nu există în driver."),
    ("define WIFI_CSI_ENABLED         1", "WIFI_CSI_ENABLED         1", "Cu opțiunea activă, macro-ul devine 1."),
    ("define WIFI_CSI_ENABLED         0", "WIFI_CSI_ENABLED         0", "Fără opțiune: 0. Atunci `esp_wifi_set_csi` întoarce `ESP_FAIL` (secțiunea 16)."),
    ("static_rx_buf_num", "CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM", "Bufferele RX fixe. Jurnal, linia 13: `static rx buffer num: 10`."),
    ("dynamic_rx_buf_num", "CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM", "Bufferele RX dinamice. Jurnal, linia 14: `dynamic rx buffer num: 32`."),
    (".csi_enable", ".csi_enable = WIFI_CSI_ENABLED", "Câmpul care spune driverului: „CSI este permis”."),
    (".nvs_enable", ".nvs_enable = WIFI_NVS_ENABLED", "Jurnal, linia 6: `config NVS flash: enabled`."),
    (".magic", ".magic = WIFI_INIT_CONFIG_MAGIC", "Un număr fix de verificare. Driverul refuză o structură greșită."),
])
snip("`esp_wifi_init` – header", "IDF/esp_wifi/include/esp_wifi.h", WH, [(310, 322), (329, 329)], [
    ("Allocate resource", "Allocate resource for WiFi driver", "Alocă memoria driverului: structuri de control și buffere RX/TX."),
    ("starts WiFi task", "This WiFi also starts WiFi task", "Aici apare task-ul Wi-Fi (`prio:23`, jurnal linia 3). El va apela `on_csi`."),
    ("Always use WIFI_INIT_CONFIG_DEFAULT", "Always use WIFI_INIT_CONFIG_DEFAULT", "Nu completa structura de mână."),
    ("can point to a temporary", "can point to a temporary variable", "Confirmă: `wifi_init` poate fi variabilă locală."),
])
snip("`esp_wifi_init` – partea deschisă", "IDF/esp_wifi/src/wifi_init.c", src("esp_wifi/src/wifi_init.c"), [(305, 309), (328, 332), (384, 386), (395, 403), (450, 450)], [
    ("if (s_wifi_inited)", "if (s_wifi_inited)", "Al doilea apel nu face nimic și întoarce `ESP_OK`."),
    ("esp_wifi_set_sleep_min_active_time", "esp_wifi_set_sleep_min_active_time", "Timpii pentru economia de energie (legătura cu `pm start`, jurnal linia 36)."),
    ("coex_init", "coex_init()", "Doar cu coexistență Wi-Fi/Bluetooth. La noi opțiunea este oprită."),
    ("esp_wifi_init_internal", "esp_wifi_init_internal(config)", "De aici începe codul închis din `libnet80211.a`. El creează task-ul Wi-Fi."),
    ("esp_phy_modem_init", "esp_phy_modem_init()", "Pregătește partea radio (PHY)."),
    ("s_wifi_inited = true", "s_wifi_inited = true", "Marchează driverul ca pornit."),
])
snip("Urma în jurnal", JL, LOG, [(3, 3), (6, 6), (13, 14)], [
    ("wifi driver task", "prio:23", "Task-ul Wi-Fi, prioritatea 23, pe nucleul 0."),
    ("config NVS flash", "enabled", "`.nvs_enable` din macro."),
    ("static rx buffer num", "10", "`static_rx_buf_num`."),
    ("dynamic rx buffer num", "32", "`dynamic_rx_buf_num`."),
])

# ---------------------------------------------------------------- 10. handler register
section("`esp_event_handler_register()` – înregistrăm `on_event`", "liniile 96–97")
snip("Codul nostru", M, MAIN, [(96, 97)], [
    ("WIFI_EVENT, ESP_EVENT_ANY_ID", "WIFI_EVENT, ESP_EVENT_ANY_ID", "Toate evenimentele Wi-Fi. Filtrăm noi, în `on_event`."),
    ("IP_EVENT, IP_EVENT_STA_GOT_IP", "IP_EVENT, IP_EVENT_STA_GOT_IP", "Din familia IP, doar „am primit IP”."),
    ("IP_EVENT, IP_EVENT_STA_GOT_IP", "on_event, NULL", "Aceeași funcție pentru ambele. `NULL` = argumentul `arg` din `on_event`."),
])
snip("Ce este o „familie” de evenimente", "IDF/esp_event/include/esp_event_base.h", src("esp_event/include/esp_event_base.h"), [(15, 19), (29, 29)], [
    ("ESP_EVENT_DECLARE_BASE", "extern esp_event_base_t const id", "Declarația: o variabilă globală constantă."),
    ("ESP_EVENT_DEFINE_BASE", "esp_event_base_t const id = #id", "Definiția: valoarea este textul numelui. `WIFI_EVENT` = pointer la textul `\"WIFI_EVENT\"`."),
    ("typedef const char*", "const char*", "O familie = un pointer la text. Două familii diferite au adrese diferite."),
    ("ESP_EVENT_ANY_ID", "-1", "−1 = toate evenimentele familiei."),
])
snip("Unde este definită `WIFI_EVENT`", "IDF/esp_wifi/src/wifi_init.c", src("esp_wifi/src/wifi_init.c"), [(47, 47)], [
    ("ESP_EVENT_DEFINE_BASE(WIFI_EVENT)", "ESP_EVENT_DEFINE_BASE(WIFI_EVENT)", "O singură definiție în tot programul. În `on_event`, `base == WIFI_EVENT` compară adrese, nu texte."),
])
snip("Header", "IDF/esp_event/include/esp_event.h", src("esp_event/include/esp_event.h"), [(109, 111), (123, 129), (137, 138)], [
    ("event_base the base", "event_base", "Familia: `WIFI_EVENT` sau `IP_EVENT`."),
    ("event_id the ID", "event_id", "Evenimentul exact, sau `ESP_EVENT_ANY_ID`."),
    ("event_handler the handler", "event_handler", "Funcția noastră, `on_event`."),
    ("event_handler_arg data", "event_handler_arg", "Pointerul nostru (`NULL`), trimis neschimbat lui `on_event`."),
    ("does not maintain a copy", "does not maintain a copy", "Biblioteca păstrează doar adresa."),
])
snip("Implementare", "IDF/esp_event/default_event_loop.c", src("esp_event/default_event_loop.c"), [(13, 13), (17, 26)], [
    ("static esp_event_loop_handle_t", "s_default_loop = NULL", "Bucla implicită. La început este `NULL`."),
    ("return ESP_ERR_INVALID_STATE", "ESP_ERR_INVALID_STATE", "Fără linia 90 înainte, înregistrarea eșuează."),
    ("esp_event_handler_register_with", "esp_event_handler_register_with(s_default_loop", "Adaugă `on_event` în lista buclei implicite."),
])
text("""
**De ce înainte de `esp_wifi_start`:** `start` trimite evenimentul `WIFI_EVENT_STA_START`. Dacă `on_event` nu este încă în listă, evenimentul se pierde. Atunci nimeni nu apelează `esp_wifi_connect`.
""")

# ---------------------------------------------------------------- 11. hotspot config
section("`wifi_config_t hotspot` – numele rețelei și parola", "liniile 98–99")
snip("Codul nostru", M, MAIN, [(98, 99)], [
    ("wifi_config_t hotspot", "wifi_config_t hotspot", "Variabilă locală în `app_main`."),
    ("wifi_config_t hotspot", "{.sta = {", "Inițializare cu nume de câmpuri: completăm doar `.sta.ssid` și `.sta.password`. Restul devine 0."),
    (".ssid = CONFIG_CSI_WIFI_SSID", "CONFIG_CSI_WIFI_SSID", "Un macro de text, creat din `Kconfig.projbuild`."),
    (".password = CONFIG_CSI_WIFI_PASSWORD", "CONFIG_CSI_WIFI_PASSWORD", "Parola, tot din configurare. Nu apare în cod."),
])
snip("De unde vin `CONFIG_CSI_WIFI_*`", "pas_cu_pas/main/Kconfig.projbuild", KCONF, whole(KCONF), [
    ("config CSI_WIFI_SSID", "CSI_WIFI_SSID", "Opțiunea devine macro-ul `CONFIG_CSI_WIFI_SSID` în `sdkconfig.h`."),
    ('default ""', 'default ""', "Implicit gol. Valoarea reală vine din `~/esp/csi-node/wifi.defaults`, în afara repo-ului (vezi `ruleaza.sh`)."),
])
TY = src("esp_wifi/include/esp_wifi_types.h")
snip("`wifi_config_t` este un `union`", "IDF/esp_wifi/include/esp_wifi_types.h", TY, [(371, 375)], [
    ("typedef union", "union", "`union` = câmpurile ocupă aceeași memorie. Folosim una dintre ele."),
    ("wifi_sta_config_t sta", "sta", "Noi folosim `.sta`: setările pentru stație."),
])
snip("Primele câmpuri din `wifi_sta_config_t`", "IDF/esp_wifi/include/esp_wifi_types.h", TY, [(319, 323)], [
    ("uint8_t ssid[32]", "ssid[32]", "Maximum 32 de octeți."),
    ("uint8_t password[64]", "password[64]", "Maximum 64 de octeți."),
    ("scan_method", "scan_method", "Câmpurile următoare rămân 0 = valori implicite."),
])

# ---------------------------------------------------------------- 12-14. mode, config, start
section("`esp_wifi_set_mode(WIFI_MODE_STA)`", "linia 100")
snip("Modurile posibile", "IDF/esp_wifi/include/esp_wifi_types.h", TY, [(20, 27)], [
    ("WIFI_MODE_NULL = 0", "WIFI_MODE_NULL = 0", "Radioul oprit."),
    ("WIFI_MODE_STA,", "WIFI_MODE_STA", "1 = stație (client). Alegerea noastră."),
    ("WIFI_MODE_AP,", "WIFI_MODE_AP", "2 = punct de acces (placa ar fi hotspot)."),
])
snip("Header", "IDF/esp_wifi/include/esp_wifi.h", WH, [(345, 347), (357, 357)], [
    ("default mode is station", "The default mode is station mode", "Fără apel, placa ar fi tot stație. Apelul face codul explicit."),
])

section("`esp_wifi_set_config(WIFI_IF_STA, &hotspot)`", "linia 101")
snip("Header", "IDF/esp_wifi/include/esp_wifi.h", WH, [(898, 898), (903, 906), (919, 919)], [
    ("stored in NVS", "stored in NVS", "SSID-ul și parola se salvează în partiția `nvs` (secțiunea 5)."),
    ("@param     interface", "interface", "`WIFI_IF_STA`: setările sunt pentru stație."),
    ("@param     conf", "conf", "Adresa lui `hotspot`. Driverul copiază datele (`memcpy`, vezi tabelul din secțiunea 14)."),
])
text("""
Jurnal, linia 24: `Password length matches WPA2 standards`. Driverul a verificat lungimea parolei. Parola nu apare în jurnal.
""")

section("`esp_wifi_start()` – și cum lucrează toate funcțiile `esp_wifi_*`", "linia 102")
snip("Header", "IDF/esp_wifi/include/esp_wifi.h", WH, [(371, 373), (386, 386)], [
    ("If mode is WIFI_MODE_STA", "creates station control block and starts station", "Creează structura stației și pornește radioul."),
])
snip("`esp_wifi_start` – instrucțiuni mașină", "libnet80211.a (objdump)", dis("esp_wifi_start"), whole(dis("esp_wifi_start")), [
    ("00003001", "00003001", "Constanta `0x3001` = `ESP_ERR_WIFI_NOT_INIT`."),
    ("R_XTENSA_32  wifi_start_process", "wifi_start_process", "Adresa funcției care face lucrul real. Este pusă într-un mesaj, nu apelată direct."),
    ("ASM_EXPAND wifi_init_completed", "wifi_init_completed", "Verificare: a rulat `esp_wifi_init`?"),
    ("beqz.n  a10", "beqz.n  a10", "Dacă nu: iese cu `0x3001`."),
    ("l32i    a2, a2, 0x178", "0x178", "Apel prin tabelul `g_osi_funcs_p`: alocă un mesaj de 24 de octeți (`a10 = 24`)."),
    ("movi    a2, 0x101", "0x101", "Dacă alocarea eșuează: `ESP_ERR_NO_MEM`."),
    ("s32i.n  a2, a10, 4", "s32i.n  a2, a10, 4", "Scrie în mesaj adresa lui `wifi_start_process`."),
    ("ASM_EXPAND ieee80211_ioctl", "ieee80211_ioctl", "Trimite mesajul task-ului Wi-Fi."),
], numbered=False)
ioctl = read(dis("ieee80211_ioctl"))
keep = [i + 1 for i, l in enumerate(ioctl) if "ASM_EXPAND" in l]
snip("`ieee80211_ioctl` (doar liniile cu apeluri)", "libnet80211.a (objdump)", dis("ieee80211_ioctl"), [(k, k) for k in keep], [
    ("current_task_is_wifi_task", "current_task_is_wifi_task", "Cine cere? Dacă este chiar task-ul Wi-Fi, mesajul se execută direct."),
    ("wifi_api_lock", "wifi_api_lock", "Blochează API-ul: două task-uri nu pot schimba driverul simultan."),
    ("pp_post", "pp_post", "Pune mesajul în coada task-ului Wi-Fi."),
    ("ieee80211_ioctl_process", "ieee80211_ioctl_process", "Aici se execută mesajul: se apelează funcția din el."),
], numbered=False)
text("""
**Același tipar** (verificat cu `objdump`) la toate funcțiile `esp_wifi_*` din `main.c`:

| Funcție | Funcția pusă în mesaj |
|---|---|
| `esp_wifi_set_mode` | `wifi_set_mode_process` |
| `esp_wifi_set_config` | `wifi_set_config_process` (înainte: `memcpy` al setărilor) |
| `esp_wifi_start` | `wifi_start_process` |
| `esp_wifi_connect` | `wifi_connect_process` |
| `esp_wifi_set_csi` | `wifi_set_csi` (secțiunea 16) |

**Concluzie:** funcțiile `esp_wifi_*` nu lucrează direct cu radioul. Ele trimit „bilețele” task-ului Wi-Fi. De aceea `app_main` se termină în 290 ms. Jurnal, linia 27: `mode : sta (fc:e8:c0:e1:1e:d0)` = adresa MAC a plăcii.
""")

# ---------------------------------------------------------------- 15. csi_rx_cb
section("`esp_wifi_set_csi_rx_cb(on_csi, NULL)` – înregistrăm `on_csi`", "linia 105")
snip("Header și tipul `wifi_csi_cb_t`", "IDF/esp_wifi/include/esp_wifi.h", WH, [(1117, 1125), (1129, 1134), (1141, 1141)], [
    ("@param ctx context argument, passed to esp_wifi_set_csi_rx_cb", "ctx", "Primul parametru al lui `on_csi`: pointerul dat la înregistrare (`NULL`)."),
    ("@param data CSI data", "deallocated after callback function returns", "După `return` din `on_csi`, memoria `info` dispare."),
    ("typedef void", "void (* wifi_csi_cb_t)(void *ctx, wifi_csi_info_t *data)", "Forma obligatorie a lui `on_csi`. De aceea are parametrul `ctx`, deși nu îl folosim."),
    ("@param cb", "cb", "Funcția noastră: `on_csi`."),
    ("@param ctx context argument, passed to callback", "ctx", "Valoarea trimisă înapoi la fiecare apel: `NULL`."),
])
snip("`esp_wifi_set_csi_rx_cb` – instrucțiuni mașină", "libnet80211.a (objdump)", dis("esp_wifi_set_csi_rx_cb"), whole(dis("esp_wifi_set_csi_rx_cb")), [
    ("R_XTENSA_32", "wifi_init_completed", "Literal pool: adresele funcțiilor apelate."),
    ("ASM_EXPAND  wifi_init_completed", "wifi_init_completed", "Apel: a rulat `esp_wifi_init`?"),
    ("beqz.n", "beqz.n  a10", "Dacă nu, iese cu `0x3001` = `ESP_ERR_WIFI_NOT_INIT`."),
    ("mov.n   a11, a3", "a11, a3", "`cb` (`a2`) și `ctx` (`a3`) trec mai departe neschimbate."),
    ("ASM_EXPAND ic_register_csi_rx_cb", "ic_register_csi_rx_cb", "Apel direct, fără mesaj și fără coadă."),
    ("movi.n  a8, 0", "movi.n  a8, 0", "Rezultat 0 = `ESP_OK`."),
], numbered=False)
snip("`wdev_set_csi_rx_cb` (apelată de `ic_register_csi_rx_cb`)", "libpp.a (objdump)", dis("wdev_set_csi_rx_cb"), whole(dis("wdev_set_csi_rx_cb")), [
    ("0: R_XTENSA_32", "g_wdev_csi_rx", "Variabila globală pentru adresa lui `on_csi`."),
    ("4: R_XTENSA_32", "g_wdev_csi_rx_ctx", "Variabila globală pentru `ctx`."),
    ("s32i.n  a2, a8, 0", "s32i.n  a2, a8, 0", "Scrie `on_csi` în `g_wdev_csi_rx`. Atât face „înregistrarea”."),
    ("s32i.n  a3, a8, 0", "s32i.n  a3, a8, 0", "Scrie `NULL` în `g_wdev_csi_rx_ctx`."),
], numbered=False)

# ---------------------------------------------------------------- 16/17. set_csi
section("`esp_wifi_set_csi(true)` – până la registrul de control", "linia 106")
snip("Header", "IDF/esp_wifi/include/esp_wifi.h", WH, [(1157, 1159), (1162, 1165), (1167, 1167)], [
    ("@param en", "true - enable", "`true` pornește măsurarea CSI."),
    ("ESP_ERR_WIFI_NOT_STARTED", "or promiscuous mode is not enabled", "Header-ul cere modul promiscuu. În practică nu este obligatoriu: noi nu îl pornim și funcția întoarce `ESP_OK`."),
])
snip("`esp_wifi_set_csi` – instrucțiuni mașină", "libnet80211.a (objdump)", dis("esp_wifi_set_csi"), whole(dis("esp_wifi_set_csi")), [
    ("00003001", "00003001", "`0x3001` = `ESP_ERR_WIFI_NOT_INIT`."),
    ("00003002", "00003002", "`0x3002` = `ESP_ERR_WIFI_NOT_STARTED`."),
    ("R_XTENSA_32  wifi_set_csi", "wifi_set_csi", "Funcția care va face lucrul real, pusă în mesaj."),
    ("ASM_EXPAND wifi_init_completed", "wifi_init_completed", "Prima verificare: a rulat `esp_wifi_init`?"),
    ("l8ui    a2, a8, 237", "l8ui    a2, a8, 237", "Citește un câmp de stare din `g_ic`. Dacă driverul nu a pornit: `0x3002`."),
    ("ASM_EXPAND config_get_wifi_csi_enable", "config_get_wifi_csi_enable", "Verifică `.csi_enable` din secțiunea 9."),
    ("movi.n  a2, -1", "movi.n  a2, -1", "CSI neactivat în `sdkconfig`: `ESP_FAIL` (−1)."),
    ("l32i    a2, a2, 0x178", "0x178", "Alocă un mesaj de 24 de octeți."),
    ("movi    a2, 0x101", "0x101", "Fără memorie: `ESP_ERR_NO_MEM`."),
    ("s32i    a2, a10, 4", "s32i    a2, a10, 4", "Scrie în mesaj adresa `wifi_set_csi`."),
    ("s8i     a3, a10, 8", "s8i     a3, a10, 8", "Scrie în mesaj parametrul nostru `en` (`true`)."),
    ("ASM_EXPAND ieee80211_ioctl", "ieee80211_ioctl", "Trimite mesajul. Task-ul Wi-Fi va apela `wifi_set_csi(mesaj)`."),
], numbered=False)
snip("`wifi_set_csi` → `ic_set_csi`", "libnet80211.a + libpp.a (objdump)", dis("wifi_set_csi"), whole(dis("wifi_set_csi")), [
    ("l8ui    a9, a2, 8", "l8ui    a9, a2, 8", "Citește octetul 8 din mesaj: `en`."),
    ("moveqz", "moveqz  a10, a8, a9", "Transformă `en` în 0 sau 1."),
    ("ASM_EXPAND ic_set_csi", "ic_set_csi", "Coboară în `libpp.a`."),
], numbered=False)
snip("`ic_set_csi` → `hal_mac_set_csi`", "libpp.a (objdump)", dis("ic_set_csi"), whole(dis("ic_set_csi")), [
    ("ASM_EXPAND  hal_mac_set_csi", "hal_mac_set_csi", "`hal_` = stratul care atinge hardware-ul direct."),
], numbered=False)
snip("`hal_mac_set_csi` – registrul de control", "libpp.a (objdump)", dis("hal_mac_set_csi"), whole(dis("hal_mac_set_csi")), [
    ("3ff7309c", "3ff7309c", "Adresa registrului, în zona perifericului Wi-Fi MAC. Nedocumentat public."),
    ("ff7fffff", "ff7fffff", "Masca pentru oprire: toți biții 1, în afară de bitul 23."),
    ("ASM_EXPAND  config_get_wifi_csi_enable", "config_get_wifi_csi_enable", "Încă o verificare a opțiunii din `sdkconfig`."),
    ("beqz.n  a3", "beqz.n  a3", "`a3` = `en`. Dacă este 0, sare la ramura de oprire."),
    ("slli    a9, a9, 23", "slli    a9, a9, 23", "`a9 = 1 << 23` = `0x00800000`: bitul de control al CSI."),
    ("l32i.n  a2, a8, 0", "l32i.n  a2, a8, 0", "Citește registrul."),
    ("or      a2, a2, a9", "or      a2, a2, a9", "Pune bitul 23 pe 1. Ceilalți biți rămân la fel."),
    ("s32i.n  a2, a8, 0", "s32i.n  a2, a8, 0", "Scrie registrul înapoi. **Din acest moment, hardware-ul calculează CSI la fiecare cadru OFDM.**"),
    ("and     a9, a9, a2", "and     a9, a9, a2", "Ramura `false`: șterge bitul 23."),
], numbered=False)
text("""
```
esp_wifi_set_csi(true)                 libnet80211.a   (task main)
  └─ ieee80211_ioctl → pp_post ─────►  coada task-ului Wi-Fi
                                       wifi_set_csi(mesaj)        (task Wi-Fi)
                                         └─ ic_set_csi            libpp.a
                                              └─ hal_mac_set_csi  libpp.a
                                                   registrul 0x3FF7309C, bitul 23 = 1
```

După linia 106, `app_main` ajunge la `}` (linia 107) și se termină. Jurnal, linia 29: `main_task: Returned from app_main()`. Restul programului rulează în task-urile `sys_evt`, `tiT`, Wi-Fi și `ping`.
""")

# ---------------------------------------------------------------- 18. on_event STA_START
section("Evenimentul `STA_START` → `on_event` → `esp_wifi_connect()`", "liniile 72–75")
text("""
`esp_wifi_start` (linia 102) face driverul să trimită `WIFI_EVENT_STA_START` în bucla de evenimente. Task-ul `sys_evt` scoate evenimentul din coadă și apelează fiecare funcție înregistrată.
""")
snip("Cum apelează bucla funcția noastră", "IDF/esp_event/esp_event.c", src("esp_event/esp_event.c"), [(117, 117), (137, 140)], [
    ("static void handler_execute", "handler_execute", "Rulează în task-ul `sys_evt`, pentru fiecare funcție din listă."),
    ("(*(handler->handler_ctx->handler))(handler->handler_ctx->arg, post.base, post.id, data_ptr)", "(*(handler->handler_ctx->handler))", "Apel prin pointer: aceasta este adresa lui `on_event`."),
    ("(*(handler->handler_ctx->handler))(handler->handler_ctx->arg, post.base, post.id, data_ptr)", "handler_ctx->arg, post.base, post.id, data_ptr", "Cei 4 parametri ai lui `on_event`: `arg` (`NULL`), `base`, `id`, `data`."),
])
snip("`on_event`, prima ramură", M, MAIN, [(72, 75)], [
    ("static void on_event", "void *arg", "`arg` = `NULL` de la înregistrare. Nu îl folosim."),
    ("static void on_event", "esp_event_base_t base", "Familia: pointer la `\"WIFI_EVENT\"` sau la `\"IP_EVENT\"`."),
    ("static void on_event", "int32_t id", "Numărul evenimentului din familie."),
    ("static void on_event", "void *data", "Datele evenimentului. Tipul depinde de eveniment."),
    ("if (base == WIFI_EVENT", "base == WIFI_EVENT", "Comparăm adrese (secțiunea 10)."),
    ("if (base == WIFI_EVENT", "id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED", "Radioul a pornit sau am pierdut rețeaua: în ambele cazuri ne conectăm."),
    ("esp_wifi_connect();", "esp_wifi_connect();", "Cere conectarea. Fără `ESP_ERROR_CHECK`: o eroare aici nu trebuie să repornească placa."),
])
snip("Numerele evenimentelor Wi-Fi", "IDF/esp_wifi/include/esp_wifi_types.h", TY, [(870, 877)], [
    ("WIFI_EVENT_WIFI_READY = 0", "= 0", "Numerotarea începe de la 0."),
    ("WIFI_EVENT_STA_START,", "WIFI_EVENT_STA_START", "2 = stația a pornit."),
    ("WIFI_EVENT_STA_CONNECTED,", "WIFI_EVENT_STA_CONNECTED", "4 = conectat. Nu îl folosim."),
    ("WIFI_EVENT_STA_DISCONNECTED,", "WIFI_EVENT_STA_DISCONNECTED", "5 = rețea pierdută."),
])
snip("`esp_wifi_connect` – header", "IDF/esp_wifi/include/esp_wifi.h", WH, [(418, 418), (424, 426), (436, 436)], [
    ("only once", "only once", "O singură încercare. De aceea reacționăm și la `STA_DISCONNECTED`."),
    ("reconnection logic", "implement reconnection logic in their application", "Reconectarea este sarcina aplicației: ramura din linia 74."),
])
snip("Conectarea în jurnal", JL, LOG, [(31, 36)], [
    ("init -> auth", "init -> auth", "Autentificare 802.11."),
    ("auth -> assoc", "auth -> assoc", "Asociere: placa primește un număr (`aid`)."),
    ("assoc -> run", "assoc -> run", "Cheile WPA2 sunt gata. Conexiunea merge."),
    ("connected with", "channel 11", "Placa a găsit hotspot-ul pe canalul 11."),
    ("connected with", "bssid = f6:2b:8c:e2:21:ac", "Adresa MAC a hotspot-ului. O vom vedea ca sursă a CSI."),
    ("security:", "phy: bgn", "Hotspot-ul acceptă 802.11b, g și n."),
    ("pm start", "pm start, type: 1", "Economia de energie a pornit. Ping-urile țin totuși placa trează."),
])

# ---------------------------------------------------------------- 19. GOT_IP
section("Evenimentul `IP_EVENT_STA_GOT_IP` → `on_event`", "liniile 76–79")
text("""
După conectare, clientul DHCP (în task-ul `tiT`) cere o adresă de la telefon. Când o primește, stiva IP trimite `IP_EVENT_STA_GOT_IP`.
""")
snip("Cine trimite evenimentul", "IDF/esp_netif/lwip/esp_netif_lwip.c", src("esp_netif/lwip/esp_netif_lwip.c"), [(1270, 1270), (1290, 1293), (1297, 1299), (1305, 1309)], [
    ("esp_netif_internal_dhcpc_cb", "esp_netif_internal_dhcpc_cb", "Funcția apelată când DHCP termină."),
    ("ip_event_got_ip_t evt", "ip_event_got_ip_t evt", "Structura pe care o primim în `data`."),
    ("ip4_addr_set(&ip_info->ip", "ip4_addr_set(&ip_info->ip", "Copiază adresa primită de la DHCP."),
    ("ip4_addr_set(&ip_info->gw", "ip4_addr_set(&ip_info->gw", "Copiază gateway-ul: telefonul."),
    ("memcpy(&evt.ip_info", "memcpy(&evt.ip_info, ip_info", "Pune adresele în eveniment."),
    ("esp_event_post(IP_EVENT", "esp_event_post(IP_EVENT, evt_id, &evt, sizeof(evt), 0)", "Trimite evenimentul. Bucla copiază `evt`, deci `data` din `on_event` rămâne valid în timpul apelului."),
])
NT = src("esp_netif/include/esp_netif_types.h")
snip("Tipurile primite", "IDF/esp_netif/include/esp_netif_types.h", NT, [(95, 96), (111, 115), (128, 132)], [
    ("IP_EVENT_STA_GOT_IP,", "IP_EVENT_STA_GOT_IP", "Valoarea 0 în familia `IP_EVENT`. De aceea verificăm și `base`: `WIFI_EVENT_WIFI_READY` are tot 0."),
    ("esp_ip4_addr_t ip;", "ip", "Adresa plăcii."),
    ("esp_ip4_addr_t gw;", "gw", "Gateway-ul: ținta ping-ului."),
    ("esp_netif_ip_info_t ip_info;", "ip_info", "Cele 3 adrese, într-un câmp."),
])
snip("O adresă IPv4 = un număr pe 32 de biți", "IDF/esp_netif/include/esp_netif_ip_addr.h", src("esp_netif/include/esp_netif_ip_addr.h"), [(111, 115)], [
    ("uint32_t addr;", "uint32_t addr", "Cei 4 octeți ai adresei, într-un singur `uint32_t`."),
])
snip("`on_event`, a doua ramură", M, MAIN, [(76, 80)], [
    ("} else if (base == IP_EVENT", "base == IP_EVENT && id == IP_EVENT_STA_GOT_IP", "Familia IP și evenimentul „am primit IP”."),
    ("ip_event_got_ip_t *got_ip = data;", "ip_event_got_ip_t *got_ip = data", "`data` este `void *`. Îl citim ca `ip_event_got_ip_t *`."),
    ('ESP_LOGI(TAG, "Conectat.', "IPSTR", "Macro: șablonul `\"%d.%d.%d.%d\"`."),
    ("IP2STR(&got_ip->ip_info.ip)", "IP2STR(&got_ip->ip_info.ip)", "Macro: cele 4 numere ale adresei, ca 4 argumente."),
    ("start_ping(got_ip->ip_info.gw)", "start_ping(got_ip->ip_info.gw)", "Pornim ping-ul către telefon. Abia acum avem adresa lui."),
])
snip("`IPSTR` și `IP2STR`", "IDF/esp_netif/include/esp_netif_ip_addr.h", src("esp_netif/include/esp_netif_ip_addr.h"), [(42, 42), (55, 58)], [
    ("IPSTR", '"%d.%d.%d.%d"', "Șablonul unei adrese IPv4."),
    ("IP2STR", "esp_ip4_addr1_16(ipaddr)", "Primul octet. Următoarele 3 linii dau ceilalți octeți."),
])
snip("În jurnal", JL, LOG, [(41, 42)], [
    ("esp_netif_handlers", "sta ip: 10.136.19.115", "Linia scrisă de funcțiile ESP-IDF înregistrate în secțiunea 8."),
    ("CSI: Conectat", "gateway 10.136.19.245", "Linia noastră. Gateway-ul este telefonul."),
])

# ---------------------------------------------------------------- 20. start_ping
section("`start_ping()` – ping la telefon la fiecare 20 ms", "liniile 60–70")
snip("Codul nostru", M, MAIN, [(60, 70)], [
    ("static void start_ping", "esp_ip4_addr_t gateway", "Parametrul: o copie a adresei gateway-ului."),
    ("ESP_PING_DEFAULT_CONFIG()", "ESP_PING_DEFAULT_CONFIG()", "Setările implicite (19.2). Schimbăm doar 4 câmpuri."),
    ("target_addr.type", "IPADDR_TYPE_V4", "`ip_addr_t` poate fi IPv4 sau IPv6. Alegem IPv4."),
    ("u_addr.ip4.addr = gateway.addr", "gateway.addr", "Copiem cei 32 de biți ai adresei."),
    ("ping.count", "ESP_PING_COUNT_INFINITE", "0 = fără sfârșit."),
    ("ping.interval_ms", "20", "Un ping la 20 ms = 50 pe secundă."),
    ("esp_ping_handle_t session", "esp_ping_handle_t session", "Un pointer la sesiune, completat de funcția următoare."),
    ("esp_ping_new_session", "&ping, NULL, &session", "Setările, fără callback-uri (`NULL`), și unde scrie sesiunea."),
    ("esp_ping_start", "esp_ping_start(session)", "Pornește ping-urile și se întoarce imediat."),
])
PS_H = src("lwip/include/apps/ping/ping_sock.h")
PS_C = src("lwip/apps/ping/ping_sock.c")
snip("`ESP_PING_DEFAULT_CONFIG` și câmpurile", "IDF/lwip/include/apps/ping/ping_sock.h", PS_H, [(58, 59), (64, 64), (66, 66), (74, 88)], [
    ("uint32_t count;", "count", "Câte ping-uri are o sesiune."),
    ("uint32_t interval_ms;", "interval_ms", "Pauza dintre două ping-uri."),
    ("ip_addr_t target_addr;", "target_addr", "Ținta: IPv4 sau IPv6."),
    ("uint32_t task_prio;", "task_prio", "Prioritatea task-ului `ping`."),
    (".count = 5", ".count = 5", "Implicit: 5 ping-uri. Noi: infinit."),
    (".interval_ms = 1000", ".interval_ms = 1000", "Implicit: unul pe secundă. Noi: 20 ms."),
    (".timeout_ms = 1000", ".timeout_ms = 1000", "Cât așteaptă un răspuns. Nu l-am schimbat."),
    (".data_size = 64", ".data_size = 64", "64 de octeți de date în fiecare ping."),
    (".task_prio = 2", ".task_prio = 2", "Prioritate mică (Wi-Fi are 23)."),
    ("ESP_PING_COUNT_INFINITE", "(0)", "Valoarea specială 0 = fără sfârșit."),
])
snip("`esp_ping_new_session` – implementare", "IDF/lwip/apps/ping/ping_sock.c", PS_C, [(238, 268), (285, 287), (306, 310)], [
    ("mem_calloc(1, sizeof(esp_ping_t))", "mem_calloc(1, sizeof(esp_ping_t))", "Alocă structura sesiunii. `esp_ping_handle_t` este un pointer la ea."),
    ("xTaskCreate(esp_ping_thread", 'xTaskCreate(esp_ping_thread, "ping"', "Creează task-ul `ping`. El trimite și primește."),
    ("if (cbs)", "if (cbs)", "Noi am dat `NULL`: task-ul nu apelează nicio funcție a noastră."),
    ("ep->count = config->count", "ep->count = config->count", "Copiază setările noastre în sesiune."),
    ("socket(AF_INET, SOCK_RAW, IP_PROTO_ICMP)", "SOCK_RAW, IP_PROTO_ICMP", "Socket „brut” ICMP: ping-ul nu folosește UDP sau TCP."),
    ("SO_RCVTIMEO", "SO_RCVTIMEO", "Așteptarea unui răspuns are limită: `timeout_ms`."),
])
snip("`esp_ping_start` – implementare", "IDF/lwip/apps/ping/ping_sock.c", PS_C, [(366, 376)], [
    ("PING_FLAGS_START", "ep->flags |= PING_FLAGS_START", "Pune steagul „pornit”."),
    ("xTaskNotifyGive", "xTaskNotifyGive(ep->ping_task_hdl)", "Trezește task-ul `ping`. Apoi funcția se întoarce imediat."),
])
snip("Bucla task-ului `ping`", "IDF/lwip/apps/ping/ping_sock.c", PS_C, [(186, 215)], [
    ("ulTaskNotifyTake", "ulTaskNotifyTake", "Task-ul doarme aici până la `esp_ping_start`."),
    ("ep->count == 0", "(ep->count == 0)", "`count == 0`: bucla nu se termină niciodată."),
    ("esp_ping_send(ep)", "esp_ping_send(ep)", "Trimite cererea ICMP echo către telefon."),
    ("recv_ret = esp_ping_receive(ep)", "esp_ping_receive(ep)", "Așteaptă răspunsul. **Răspunsul vine ca un cadru OFDM de la hotspot → hardware-ul calculează un CSI.**"),
    ("if (ep->on_ping_success)", "if (ep->on_ping_success)", "Nu avem callback-uri: nu se întâmplă nimic aici."),
    ("vTaskDelayUntil", "vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(ep->interval_ms))", "Așteaptă până la următorul ping. `pdMS_TO_TICKS(20)` = 2 tick-uri (100 Hz)."),
])
text("""
```
task ping (prio 2)     task tiT (lwIP)     task Wi-Fi (prio 23)          telefonul
  esp_ping_send  ───►  pachet ICMP  ───►   cadru Wi-Fi  ─────────────►   primește ping-ul
                                                                         trimite răspunsul
                                           cadru OFDM/HT  ◄────────────   (ICMP echo reply)
                                           hardware: CSI din LLTF
                                           wdev_csi_rx_process
                                             └─ on_csi(NULL, info)
  esp_ping_receive ◄── răspuns ICMP ◄────  pachetul merge mai departe la IP
  vTaskDelayUntil (până la 20 ms)
```

CSI vine din **răspuns**, nu din cererea noastră. Placa măsoară doar ce primește. Fără ping (etapa 4), hotspot-ul tace și nu avem CSI.
""")

# ---------------------------------------------------------------- 21. CSI path
section("Un răspuns ajunge: driverul apelează `on_csi`")
text("""
Fiecare cadru OFDM primit are la început un „model de test” cunoscut: LLTF. Hardware-ul compară ce a primit cu ce trebuia să primească. Rezultatul, pe fiecare sub-frecvență, este CSI. Codul din `libpp.a` copiază rezultatul și apelează `on_csi`.
""")
wd = read(dis("wdev_csi_rx_process"))


def find(s):
    return next(i + 1 for i, l in enumerate(wd) if s in l)


snip("`wdev_csi_rx_process` – de la hardware la `on_csi`", "libpp.a (objdump)", dis("wdev_csi_rx_process"),
     [(1, 10), (find("l32i.n  a8, a6, 0"), find("callx8  a8")),
      (find("addi    a10, a10, 28"), find("addi    a10, a10, 28")),
      (find("addi.n  a11, a5, 10"), find("addi.n  a11, a5, 10")),
      (find("addi.n  a11, a5, 4"), find("addi    a10, a6, 34")),
      (find("movi.n  a12, 28"), find("movi.n  a12, 28")),
      (find("ASM_EXPAND wDev_GetNoiseFloor"), find("s8i     a10, a6, 8")),
      (find("s32i.n  a2, a6, 44"), find("s16i    a2, a6, 48")),
      (find("s8i     a11, a6, 40"), find("s8i     a11, a6, 40")),
      (find("mov.n   a11, a6"), len(wd))], [
        ("0: R_XTENSA_32", "g_wdev_csi_rx", "Adresa lui `on_csi`, salvată în secțiunea 15."),
        ("c: R_XTENSA_32", "g_wdev_csi_rx_ctx", "`ctx`, salvat în secțiunea 15."),
        ("l32i.n  a8, a6, 0", "l32i.n  a8, a6, 0", "Citește `g_wdev_csi_rx`."),
        ("beqz    a8", "beqz    a8", "Nicio funcție înregistrată? Atunci iese imediat."),
        ("movi.n  a10, 64", "movi.n  a10, 64", "Alocă 64 de octeți pentru `wifi_csi_info_t`."),
        ("addi    a10, a10, 28", "28", "`info->mac` este la octetul 28, după `rx_ctrl`."),
        ("addi.n  a11, a5, 10", "a5, 10", "Copiază 6 octeți din antetul 802.11, de la poziția 10: adresa sursei."),
        ("addi.n  a11, a5, 4", "a5, 4", "De la poziția 4: adresa destinației."),
        ("addi    a10, a6, 34", "a6, 34", "... în `info->dmac` (octetul 34)."),
        ("movi.n  a12, 28", "movi.n  a12, 28", "Copiază 28 de octeți: tot `rx_ctrl` (rssi, sig_mode, canal...)."),
        ("ASM_EXPAND wDev_GetNoiseFloor", "wDev_GetNoiseFloor", "Citește zgomotul de fond al radioului."),
        ("s8i     a10, a6, 8", "s8i     a10, a6, 8", "Îl scrie în `rx_ctrl.noise_floor`."),
        ("s32i.n  a2, a6, 44", "a6, 44", "`info->buf` (octetul 44): adresa datelor CSI."),
        ("s16i    a2, a6, 48", "a6, 48", "`info->len` (octetul 48)."),
        ("s8i     a11, a6, 40", "a6, 40", "`info->first_word_invalid` (octetul 40)."),
        ("l32i.n  a2, a3, 0", "l32i.n  a2, a3, 0", "`a2` = `g_wdev_csi_rx` = `on_csi`."),
        ("l32i.n  a10, a3, 0", "l32i.n  a10, a3, 0", "`a10` = primul argument = `ctx` (`NULL`). `a11` = `info`."),
        ("callx8  a2", "callx8  a2", "**Aici rulează `on_csi(ctx, info)`, în task-ul Wi-Fi.**"),
        ("l32i    a2, a2, 176", "176", "Funcția de eliberare din `g_osi_funcs_p`."),
        ("callx8  a2", "callx8  a2", "Eliberează `info`. După `return` din `on_csi`, `info` nu mai există."),
    ], numbered=False,
    intro="Offset-urile scrise (28, 34, 40, 44, 48) corespund exact câmpurilor din `wifi_csi_info_t` (20.2). Aceasta confirmă interpretarea.")
snip("Structura primită: `wifi_csi_info_t`", "IDF/esp_wifi/include/esp_wifi_types.h", TY, [(589, 600)], [
    ("rx_ctrl", "wifi_pkt_rx_ctrl_t rx_ctrl", "Datele radio ale cadrului (20.3). Primii 28 de octeți."),
    ("uint8_t mac[6]", "mac[6]", "Cine a trimis cadrul: hotspot-ul (`f6:2b:8c:e2:21:ac`)."),
    ("first_word_invalid", "first_word_invalid", "Primii 4 octeți din `buf` pot fi invalizi (defect hardware)."),
    ("int8_t *buf", "int8_t *buf", "Octeții CSI, cu semn: Q, I, Q, I, ..."),
    ("uint16_t len", "uint16_t len", "Numărul de octeți din `buf`: 128 (doar LLTF), 256 sau 384."),
])
snip("`rx_ctrl.rssi`", "IDF/esp_wifi/include/esp_wifi_types.h", TY, [(463, 468)], [
    ("signed rssi:8", "signed rssi:8", "Câmp de 8 biți cu semn: puterea cadrului, în dBm (de exemplu −55)."),
    ("unsigned sig_mode:2", "sig_mode", "0 = 802.11b/g, 1 = 802.11n (HT). De aici depinde `len`."),
])
snip("Ghidul oficial: `on_csi` rulează în task-ul Wi-Fi", "~/esp/esp-idf/docs/en/api-guides/wifi.rst", WIFI_RST, [(2273, 2273)], [
    ("runs from Wi-Fi task", "runs from Wi-Fi task", "Confirmă 20.1."),
    ("do not do lengthy operations", "do not do lengthy operations", "`on_csi` trebuie să fie scurtă. Altfel, task-ul Wi-Fi pierde cadre."),
])

# ---------------------------------------------------------------- 22. on_csi + amplitude
section("`on_csi` linie cu linie – amplitudinea", "liniile 20–41")
snip("Formatul lui `info->buf` (ghidul oficial)", "~/esp/esp-idf/docs/en/api-guides/wifi.rst", WIFI_RST, [(2214, 2214), (2225, 2225), (2241, 2242)], [
    ("first one is imaginary", "The first one is imaginary part and the second one is real part", "Fiecare sub-frecvență: 2 octeți, întâi Q (imaginar), apoi I (real)."),
    ("| sub-carrier | LLTF", "0~31, -32~-1", "Ordinea intrărilor LLTF la 20 MHz: 0…31, apoi −32…−1. De aici `64 + k` pentru k negativ."),
    ("The order of LTF is", "The order of LTF is: LLTF, HT-LTF, STBC-HT-LTF", "LLTF este mereu primul. Primii 128 de octeți sunt LLTF, oricare ar fi `len`."),
    ("first_word_invalid", "first four bytes of CSI data is invalid", "Primii 4 octeți = intrările 0 și +1. De aceea le sărim."),
])
snip("`on_csi`: verificarea și suma pe sub-frecvențe", M, MAIN, [(33, 41)], [
    ("static void on_csi", "void *ctx", "`ctx` = `NULL`. Este cerut de forma `wifi_csi_cb_t`."),
    ("static void on_csi", "wifi_csi_info_t *info", "Măsurătoarea. Există doar până la `return`."),
    ("if (info->len < 128) return;", "info->len < 128", "Avem nevoie de tot blocul LLTF: 64 de intrări × 2 octeți. Altfel ignorăm cadrul."),
    ("for (int k = -26; k <= 26; k++)", "k = -26; k <= 26", "Sub-frecvențele active LLTF: −26 … +26 (53 de valori)."),
    ("if (k == 0 || k == 1) continue;", "k == 0", "k = 0 = centrul (DC): fără semnal."),
    ("if (k == 0 || k == 1) continue;", "k == 1", "k = +1 = în primii 4 octeți, poate fi invalid. Rămân 51 de sub-frecvențe."),
    ("amplitude_total[k + 26] += amplitude(info->buf, k);", "amplitude_total[k + 26]", "Poziția în vectorul nostru: k = −26 → 0, k = +26 → 52."),
    ("amplitude_total[k + 26] += amplitude(info->buf, k);", "amplitude(info->buf, k)", "Amplitudinea sub-frecvenței k în acest cadru (21.3)."),
    ("packets++;", "packets++", "Încă un CSI în secunda curentă."),
    ("rssi_total += info->rx_ctrl.rssi;", "info->rx_ctrl.rssi", "Puterea cadrului (20.3), adunată pentru medie."),
])
snip("`amplitude()`: din 2 octeți în amplitudine", M, MAIN, [(20, 26)], [
    ("static float amplitude", "const int8_t *csi", "`info->buf`. `const` = funcția doar citește."),
    ("int index = k >= 0 ? k : 64 + k;", "k >= 0 ? k : 64 + k", "Intrarea din `buf`. Exemplu: k = −20 → 44. k = +7 → 7."),
    ("int q = csi[2 * index];", "csi[2 * index]", "Octetul par al intrării = Q. Pentru k = −20: `buf[88]`."),
    ("int i = csi[2 * index + 1];", "csi[2 * index + 1]", "Octetul impar = I. Pentru k = −20: `buf[89]`."),
    ("return sqrtf(i * i + q * q);", "sqrtf(i * i + q * q)", "A = √(I² + Q²): lungimea săgeții (I, Q). `i * i` se calculează în `int`, apoi `sqrtf` în `float`."),
])
text("""
**Exemplu numeric:** dacă `buf[88] = 12` (Q) și `buf[89] = −16` (I), atunci A = √(256 + 144) = √400 = 20.

`buf` are tipul `int8_t`: fiecare valoare este între −128 și +127. Deci A este cel mult √(2 × 128²) ≈ 181.
""")

# ---------------------------------------------------------------- 23. o data pe secunda
section("O dată pe secundă: mediile și cele 3 linii din jurnal", "liniile 28–31, 43–57")
snip("Ceasul și testul „a trecut o secundă?”", M, MAIN, [(43, 44)], [
    ("int64_t now = esp_timer_get_time();", "esp_timer_get_time()", "Microsecunde de la pornire (22.2)."),
    ("if (now - second_start_us >= 1000000)", "now - second_start_us >= 1000000", "Au trecut 1 000 000 µs = 1 s? La primul CSI, `second_start_us` este 0, deci prima linie are un singur cadru."),
])
snip("`esp_timer_get_time` – header", "IDF/esp_timer/include/esp_timer.h", src("esp_timer/include/esp_timer.h"), [(215, 219)], [
    ("@brief Get time in microseconds", "microseconds since boot", "Microsecunde de la pornirea plăcii."),
    ("int64_t esp_timer_get_time", "int64_t", "64 de biți: nu se resetează practic niciodată (~292 000 de ani)."),
])
LAC = src("esp_timer/src/esp_timer_impl_lac.c")
snip("`esp_timer_get_time` – implementare: un numărător hardware", "IDF/esp_timer/src/esp_timer_impl_lac.c", LAC, [(50, 52), (93, 130)], [
    ("define COUNT_LO_REG", "TIMG_LACTLO_REG(LACT_MODULE)", "Registrul cu cei 32 de biți de jos ai numărătorului."),
    ("define COUNT_HI_REG", "TIMG_LACTHI_REG(LACT_MODULE)", "Registrul cu cei 32 de biți de sus."),
    ("define UPDATE_REG", "TIMG_LACTUPDATE_REG(LACT_MODULE)", "Scrierea aici copiază numărătorul în registrele LO/HI."),
    ("REG_WRITE(UPDATE_REG, 1)", "REG_WRITE(UPDATE_REG, 1)", "Cere o copie nouă a numărătorului."),
    ("lo = REG_READ(COUNT_LO_REG);", "REG_READ(COUNT_LO_REG)", "Citește partea de jos până când se schimbă: copia este gata."),
    ("hi = REG_READ(COUNT_HI_REG);", "REG_READ(COUNT_HI_REG)", "Citește partea de sus. Bucla verifică dacă LO nu s-a schimbat între timp."),
    ("return esp_timer_impl_get_counter_reg() / LACT_TICKS_PER_US", "/ LACT_TICKS_PER_US", "Numărătorul crește de 2 ori pe µs. Împărțit la 2 = microsecunde."),
    ('__attribute__((alias("esp_timer_impl_get_time")))', 'alias("esp_timer_impl_get_time")', "`esp_timer_get_time` este doar alt nume pentru funcția de deasupra."),
])
snip("Adresa registrelor", "IDF/soc/esp32/include/soc/timer_group_reg.h", src("soc/esp32/include/soc/timer_group_reg.h"), [(34, 34), (485, 485), (493, 493)], [
    ("define REG_TIMG_BASE", "DR_REG_TIMERGROUP0_BASE + i*0x1000", "Timer Group 0 începe la `0x3FF5F000` (`reg_base.h:43`). `LACT_MODULE = 0`."),
    ("define TIMG_LACTLO_REG", "+ 0x0078", "LO = `0x3FF5F078`."),
    ("define TIMG_LACTHI_REG", "+ 0x007c", "HI = `0x3FF5F07C`."),
])
snip("`average()` și prima linie: `CSI/s` și RSSI", M, MAIN, [(28, 31), (45, 45)], [
    ("static float average(int k)", "average(int k)", "Media amplitudinii pe sub-frecvența k în secunda curentă."),
    ("return amplitude_total[k + 26] / packets;", "amplitude_total[k + 26] / packets", "Suma / numărul de cadre. `packets` este mereu ≥ 1 aici."),
    ('"%3d CSI/s  rssi=%4d"', "%3d CSI/s", "Câte CSI în ultima secundă, pe 3 caractere."),
    ('"%3d CSI/s  rssi=%4d"', "rssi_total / packets", "RSSI mediu. Împărțire întreagă: zecimalele se pierd."),
])
snip("A doua linie: `A_medie` și 4 sub-frecvențe", M, MAIN, [(46, 49)], [
    ("float all = 0;", "float all = 0", "Suma mediilor pe cele 51 de sub-frecvențe."),
    ("all += average(k);", "if (k != 0 && k != 1)", "Aceleași 51 de sub-frecvențe ca în suma din `on_csi`."),
    ("all / 51, average(-20)", "all / 51", "`A_medie`: o singură valoare pentru tot canalul."),
    ("all / 51, average(-20)", "average(-20), average(-7), average(7), average(20)", "4 sub-frecvențe: două la margini, două aproape de centru."),
])
snip("A treia linie: `SPEC`, apoi o secundă nouă", M, MAIN, [(50, 57)], [
    ('printf("SPEC");', 'printf("SPEC")', "`printf`, nu `ESP_LOGI`: fără literă, timp și `TAG`. `grafic.py` caută liniile care încep cu `SPEC`."),
    ('printf(" %.0f", average(k));', '" %.0f"', "Fiecare medie, fără zecimale, după un spațiu. 51 de numere."),
    ('printf("\\n");', 'printf("\\n")', "Sfârșitul liniei."),
    ("amplitude_total[k] = 0;", "k < 53", "Toate cele 53 de sume devin 0 (și pozițiile pentru k = 0 și +1, nefolosite)."),
    ("packets = 0;", "packets = 0", "Secunda nouă începe de la zero."),
    ("second_start_us = now;", "second_start_us = now", "Momentul de început al secundei noi."),
])
snip("Rezultatul în jurnal", JL, LOG, [(43, 46), (49, 51)], [
    ("1 CSI/s", "1 CSI/s", "Prima linie are un singur cadru (`second_start_us` era 0). O ignorăm."),
    ("51 CSI/s", "51 CSI/s", "Rata reală: 50–51 CSI/s, cât ping-uri trimitem."),
    ("A_medie= 22.2", "A[-20]=  8.8", "Marginea din stânga: slabă."),
    ("A_medie= 22.2", "A[+7]= 31.1", "Aproape de centru, dreapta: puternică. Forma spectrului = „amprenta” canalului."),
    ("SPEC 17 16 14", "SPEC 17 16 14", "Primele valori: k = −26, −25, −24, ... Ultimele: k = +24, +25, +26."),
])
text("""
Linia 47 din jurnal are caractere greșite (`����`). Cablul USB a pierdut câțiva octeți. Placa a trimis textul corect. `grafic.py` ignoră liniile care nu au formatul așteptat.
""")

# ---------------------------------------------------------------- 24. absolut
section("De ce amplitudinea nu are unități fixe")
snip("Setările CSI implicite", "IDF/esp_wifi/include/esp_wifi_types.h", TY, [(574, 582)], [
    ("channel_filter_en", "smooth adjacent sub-carrier", "Implicit, sub-frecvențele vecine sunt netezite."),
    ("manu_scale", "automatically scale the CSI data", "Implicit, chipul scalează automat valorile CSI."),
    ("manu_scale", "Default false", "Noi nu apelăm `esp_wifi_set_csi_config`, deci scalarea automată este activă."),
])
snip("Unde ar ajunge `esp_wifi_set_csi_config`: `ic_csi_set_config`", "libpp.a (objdump)", dis("ic_csi_set_config"), whole(dis("ic_csi_set_config")), [
    ("3ff730f8", "3ff730f8", "Primul registru de configurare CSI."),
    ("3ff730fc", "3ff730fc", "Al doilea registru de configurare CSI."),
    ("l8ui    a14, a2, 2", "a2, 2", "Octetul 2 din config = `stbc_htltf2_en`."),
    ("l8ui    a13, a2, 1", "a2, 1", "Octetul 1 = `htltf_en`."),
    ("l8ui    a12, a2, 0", "a2, 0", "Octetul 0 = `lltf_en`."),
    ("l8ui    a11, a2, 6", "a2, 6", "Octetul 6 = `shift`."),
    ("l8ui    a10, a2, 5", "a2, 5", "Octetul 5 = `manu_scale`."),
    ("ASM_EXPAND phy_chan_dump_cfg", "phy_chan_dump_cfg", "Radioul (`libphy.a`) primește ce LTF-uri salvează și cum scalează valorile."),
    ("l8ui    a11, a2, 3", "a2, 3", "Octetul 3 = `ltf_merge_en`."),
    ("l8ui    a10, a2, 4", "a2, 4", "Octetul 4 = `channel_filter_en`."),
    ("ASM_EXPAND phy_chan_filt_set", "phy_chan_filt_set", "Filtrul de canal se setează în radio."),
    ("l8ui    a8, a2, 7", "a2, 7", "Octetul 7 = `dump_ack_en`."),
    ("slli    a8, a8, 29", "slli    a8, a8, 29", "`dump_ack_en` controlează bitul 29, în ambii regiștri."),
], numbered=False,
    intro="Nu apelăm această funcție. O arătăm ca să vezi unde ajung setările CSI. Legătura octet → câmp este dedusă din ordinea câmpurilor din `wifi_csi_config_t`.")
text("""
**Concluzie:** chipul are control automat al amplificării (AGC) și scalează CSI automat. Când semnalul scade, chipul amplifică mai mult. Deci:

- Nu compara `A_medie` între momente diferite.
- Compară RSSI (este calibrat, în dBm).
- Compară **forma** spectrului, de exemplu `A[-20] / A[+20]`. Scalarea comună se anulează în raport.
""")

# ---------------------------------------------------------------- 25. rezumat
section("Rezumat")
text("""
### Drumul unei măsurători

```
telefonul răspunde la ping (cadru OFDM)
  └─ hardware Wi-Fi: bitul 23 din 0x3FF7309C = 1  →  calculează CSI din LLTF
       └─ libpp.a: wdev_csi_rx_process  (task Wi-Fi, prioritate 23)
            ├─ completează wifi_csi_info_t: rx_ctrl, mac, buf, len
            └─ g_wdev_csi_rx(NULL, info)  =  on_csi(NULL, info)          main.c:34
                 ├─ amplitude(): buf[2·index] = Q, buf[2·index+1] = I    main.c:21
                 ├─ adună în amplitude_total[k + 26], packets, rssi_total
                 └─ o dată pe secundă (esp_timer_get_time, registrul 0x3FF5F078):
                      ESP_LOGI → esp_log_write → vprintf → UART0 → cablul USB → PC
```

### De reținut

1. `app_main` rulează în task-ul `main` și se termină după 290 ms. Programul continuă în alte task-uri.
2. Variabilele `static` sunt 0 de la pornire: codul de pornire șterge zona `.bss`.
3. `ESP_LOGI` este un macro. Formatul `I (timp) TAG: text` vine din `LOG_FORMAT`. Timpul vine din tick-urile FreeRTOS.
4. Ordinea din `app_main` contează: `nvs` → `netif` → bucla de evenimente → interfața stației → driverul → înregistrarea `on_event` → `start`.
5. Funcțiile `esp_wifi_*` trimit mesaje task-ului Wi-Fi prin `ieee80211_ioctl`. Ele nu ating direct radioul.
6. `esp_wifi_set_csi_rx_cb` doar salvează adresa lui `on_csi` în `g_wdev_csi_rx`.
7. `esp_wifi_set_csi(true)` ajunge la `hal_mac_set_csi`: bitul 23 din registrul `0x3FF7309C`.
8. `on_event` rulează în task-ul `sys_evt`. Bucla o apelează prin pointer, cu `arg`, `base`, `id`, `data`.
9. CSI vine din **răspunsurile** hotspot-ului. Ping-ul la 20 ms le face regulate: 50 CSI/s.
10. `on_csi` rulează în task-ul Wi-Fi. `info` dispare după `return`. Funcția trebuie să fie scurtă.
11. `buf`: întâi LLTF, 2 octeți pe sub-frecvență (Q, apoi I), ordinea 0…31, −32…−1. De aici `64 + k`.
12. `amplitude_total[k + 26]` este indexul nostru. `64 + k` este indexul driverului. Nu le confunda.
13. Amplitudinea nu are unități fixe (scalare automată, AGC). Compară RSSI și forma spectrului.
14. Observațiile din codul închis (secțiunile 14–16, 20, 23) sunt deduse din instrucțiunile mașină. Espressif nu le documentează.

### Comenzi pentru verificare

```bash
B=$(ls -d ~/.espressif/tools/xtensa-esp32-elf/*/xtensa-esp32-elf/bin)
L=~/esp/esp-idf/components/esp_wifi/lib/esp32
$B/xtensa-esp32-elf-nm -g --defined-only $L/libnet80211.a | grep -w "T esp_wifi_set_csi"   # în ce bibliotecă?
$B/xtensa-esp32-elf-objdump -dr $L/libpp.a | grep -n "<hal_mac_set_csi>:" -A30           # instrucțiunile
bash unelte/genereaza_curs.sh                                                          # regenerează aceste notițe
```
""")

out = "\n".join(DOC)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(out)
print("ok", OUT, SEC[0], "sectiuni")
