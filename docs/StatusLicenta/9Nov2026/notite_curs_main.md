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

### 0.1 Tot fișierul `main.c`

Sursa: `pas_cu_pas/main/main.c`

Fișierul complet, ca referință. Explicațiile pe linii sunt în secțiunile următoare.

<pre>
  1 | // CSI pe ESP32: conectare la hotspot, ping regulat, amplitudinea pe sub-frecvente
  2 | #include &quot;esp_log.h&quot;            // ESP_LOGI
  3 | #include &quot;esp_wifi.h&quot;           // esp_wifi_*
  4 | #include &quot;esp_event.h&quot;          // bucla de evenimente
  5 | #include &quot;nvs_flash.h&quot;          // memoria pentru setarile Wi-Fi
  6 | #include &quot;esp_netif.h&quot;          // adresa IP
  7 | #include &quot;esp_mac.h&quot;            // MACSTR
  8 | #include &quot;esp_timer.h&quot;          // ceasul in microsecunde
  9 | #include &quot;ping/ping_sock.h&quot;     // esp_ping_*
 10 | #include &lt;math.h&gt;               // sqrtf
 11 | 
 12 | static const char *TAG = &quot;CSI&quot;;
 13 | 
 14 | // sumele pentru secunda curenta
 15 | static int     packets;                 // cate CSI au venit
 16 | static int     rssi_total;
 17 | static int64_t second_start_us;
 18 | static float   amplitude_total[53];     // pe fiecare sub-frecventa k, la pozitia k + 26
 19 | 
 20 | // amplitudinea sub-frecventei k (-26..26): 2 octeti, intai Q, apoi I
 21 | static float amplitude(const int8_t *csi, int k) {
 22 |     int index = k &gt;= 0 ? k : 64 + k;
 23 |     int q = csi[2 * index];
 24 |     int i = csi[2 * index + 1];
 25 |     return sqrtf(i * i + q * q);
 26 | }
 27 | 
 28 | // media pe sub-frecventa k, in secunda curenta
 29 | static float average(int k) {
 30 |     return amplitude_total[k + 26] / packets;
 31 | }
 32 | 
 33 | // driverul Wi-Fi apeleaza aceasta functie la fiecare CSI masurat
 34 | static void on_csi(void *ctx, wifi_csi_info_t *info) {
 35 |     if (info-&gt;len &lt; 128) return;        // avem nevoie de tot blocul LLTF
 36 |     for (int k = -26; k &lt;= 26; k++) {
 37 |         if (k == 0 || k == 1) continue; // 0 = fara semnal, +1 = poate fi invalid
 38 |         amplitude_total[k + 26] += amplitude(info-&gt;buf, k);
 39 |     }
 40 |     packets++;
 41 |     rssi_total += info-&gt;rx_ctrl.rssi;
 42 | 
 43 |     int64_t now = esp_timer_get_time();
 44 |     if (now - second_start_us &gt;= 1000000) {
 45 |         ESP_LOGI(TAG, &quot;%3d CSI/s  rssi=%4d&quot;, packets, rssi_total / packets);
 46 |         float all = 0;
 47 |         for (int k = -26; k &lt;= 26; k++) if (k != 0 &amp;&amp; k != 1) all += average(k);
 48 |         ESP_LOGI(TAG, &quot;A_medie=%5.1f  A[-20]=%5.1f A[-7]=%5.1f A[+7]=%5.1f A[+20]=%5.1f&quot;,
 49 |                  all / 51, average(-20), average(-7), average(7), average(20));
 50 |         printf(&quot;SPEC&quot;);
 51 |         for (int k = -26; k &lt;= 26; k++) if (k != 0 &amp;&amp; k != 1) printf(&quot; %.0f&quot;, average(k));
 52 |         printf(&quot;\n&quot;);
 53 |         for (int k = 0; k &lt; 53; k++) amplitude_total[k] = 0;
 54 |         packets = 0;
 55 |         rssi_total = 0;
 56 |         second_start_us = now;
 57 |     }
 58 | }
 59 | 
 60 | // ping la telefon (gateway) la fiecare 20 ms: fiecare raspuns aduce un CSI
 61 | static void start_ping(esp_ip4_addr_t gateway) {
 62 |     esp_ping_config_t ping = ESP_PING_DEFAULT_CONFIG();
 63 |     ping.target_addr.type = IPADDR_TYPE_V4;
 64 |     ping.target_addr.u_addr.ip4.addr = gateway.addr;
 65 |     ping.count = ESP_PING_COUNT_INFINITE;
 66 |     ping.interval_ms = 20;
 67 |     esp_ping_handle_t session;
 68 |     ESP_ERROR_CHECK(esp_ping_new_session(&amp;ping, NULL, &amp;session));
 69 |     ESP_ERROR_CHECK(esp_ping_start(session));
 70 | }
 71 | 
 72 | // driverul ne anunta aici: &quot;am pornit&quot;, &quot;m-am deconectat&quot;, &quot;am primit IP&quot;
 73 | static void on_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
 74 |     if (base == WIFI_EVENT &amp;&amp; (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)) {
 75 |         esp_wifi_connect();
 76 |     } else if (base == IP_EVENT &amp;&amp; id == IP_EVENT_STA_GOT_IP) {
 77 |         ip_event_got_ip_t *got_ip = data;
 78 |         ESP_LOGI(TAG, &quot;Conectat. IP &quot; IPSTR &quot;, gateway &quot; IPSTR,
 79 |                  IP2STR(&amp;got_ip-&gt;ip_info.ip), IP2STR(&amp;got_ip-&gt;ip_info.gw));
 80 |         start_ping(got_ip-&gt;ip_info.gw);
 81 |     }
 82 | }
 83 | 
 84 | void app_main(void) {
 85 |     ESP_LOGI(TAG, &quot;Salut! app_main a pornit.&quot;);
 86 | 
 87 |     // 1. pornim Wi-Fi-ul
 88 |     ESP_ERROR_CHECK(nvs_flash_init());
 89 |     ESP_ERROR_CHECK(esp_netif_init());
 90 |     ESP_ERROR_CHECK(esp_event_loop_create_default());
 91 |     esp_netif_create_default_wifi_sta();
 92 |     wifi_init_config_t wifi_init = WIFI_INIT_CONFIG_DEFAULT();
 93 |     ESP_ERROR_CHECK(esp_wifi_init(&amp;wifi_init));
 94 | 
 95 |     // 2. ne conectam la hotspot
 96 |     ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_event, NULL));
 97 |     ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_event, NULL));
 98 |     wifi_config_t hotspot = {.sta = {.ssid = CONFIG_CSI_WIFI_SSID,
 99 |                                      .password = CONFIG_CSI_WIFI_PASSWORD}};
100 |     ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
101 |     ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &amp;hotspot));
102 |     ESP_ERROR_CHECK(esp_wifi_start());
103 | 
104 |     // 3. cerem CSI
105 |     ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(on_csi, NULL));
106 |     ESP_ERROR_CHECK(esp_wifi_set_csi(true));
107 | }
</pre>


---

## 1. Înainte de `app_main`: pornirea plăcii

Placa nu începe cu `app_main`. Mai întâi rulează codul ROM, bootloader-ul și codul de pornire ESP-IDF. Acesta pregătește memoria, pornește FreeRTOS și creează task-ul `main`.

### 1.1 Memoria `.bss` devine 0

Sursa: `IDF/esp_system/port/cpu_start.c`

<pre>
348 |     //<mark>Clear BSS</mark>. Please do not attempt to do any complex stuff (like early logging) before this.  [1]
349 |     <mark>memset(&amp;_bss_start, 0</mark>, (&amp;_bss_end - &amp;_bss_start) * sizeof(_bss_start));  [2]
</pre>

1. `.bss` = zona de memorie pentru variabilele globale și `static` fără valoare inițială.
2. Toată zona devine 0. De aceea `packets`, `rssi_total`, `second_start_us` și `amplitude_total[]` din `main.c` încep de la 0.

### 1.2 Cine creează task-ul `main`

Sursa: `IDF/freertos/app_startup.c`

<pre>
83 |     BaseType_t res = <mark>xTaskCreatePinnedToCore(main_task, &quot;main&quot;</mark>,  [1]
84 |                                              <mark>ESP_TASK_MAIN_STACK</mark>, NULL,  [2]
85 |                                              <mark>ESP_TASK_MAIN_PRIO</mark>, NULL, ESP_TASK_MAIN_CORE);  [3]
</pre>

1. Un task FreeRTOS cu numele `main`. El va rula funcția `main_task`.
2. Stiva: 3584 (`CONFIG_ESP_MAIN_TASK_STACK_SIZE`) + 512 = 4096 de octeți. Variabilele locale din `app_main` (`wifi_init`, `hotspot`) stau aici.
3. Prioritatea 1 (`ESP_TASK_PRIO_MIN + 1`): foarte mică.

### 1.3 `main_task` apelează `app_main`

Sursa: `IDF/freertos/app_startup.c`

<pre>
158 | static void <mark>main_task</mark>(void* args)  [1]
    | ...
206 |     ESP_LOGI(MAIN_TAG, <mark>&quot;Calling app_main()&quot;</mark>);  [2]
207 |     <mark>extern void app_main(void)</mark>;  [3]
208 |     <mark>app_main();</mark>  [4]
209 |     ESP_LOGI(MAIN_TAG, <mark>&quot;Returned from app_main()&quot;</mark>);  [5]
210 |     <mark>vTaskDelete(NULL)</mark>;  [6]
</pre>

1. Funcția task-ului `main`.
2. Prima linie a noastră din jurnal: `I (539) main_task: Calling app_main()`.
3. `extern` = funcția este definită în alt fișier: `main.c`. Numele trebuie să fie exact `app_main`.
4. **Aici începe codul nostru.**
5. Apare după ce `app_main` se termină (linia 29 din jurnal).
6. Task-ul `main` se șterge singur. Programul continuă în celelalte task-uri.

---

## 2. Începutul fișierului: `#include`, `TAG`, variabilele `static`

`main.c`: liniile 1–18

Aceste linii nu „rulează” ca instrucțiuni. Compilatorul le folosește când construiește programul. Variabilele există în memorie de la pornire (secțiunea 1).

### 2.1 Header-ele

Sursa: `pas_cu_pas/main/main.c`

<pre>
 1 | <mark>// CSI pe ESP32</mark>: conectare la hotspot, ping regulat, amplitudinea pe sub-frecvente  [1]
 2 | #include <mark>&quot;esp_log.h&quot;</mark>            // ESP_LOGI  [2]
 3 | #include <mark>&quot;esp_wifi.h&quot;</mark>           // esp_wifi_*  [3]
 4 | #include <mark>&quot;esp_event.h&quot;</mark>          // bucla de evenimente  [4]
 5 | #include <mark>&quot;nvs_flash.h&quot;</mark>          // memoria pentru setarile Wi-Fi  [5]
 6 | #include <mark>&quot;esp_netif.h&quot;</mark>          // adresa IP  [6]
 7 | #include <mark>&quot;esp_mac.h&quot;</mark>            // MACSTR  [7]
 8 | #include <mark>&quot;esp_timer.h&quot;</mark>          // ceasul in microsecunde  [8]
 9 | #include <mark>&quot;ping/ping_sock.h&quot;</mark>     // esp_ping_*  [9]
10 | #include <mark>&lt;math.h&gt;</mark>               // sqrtf  [10]
</pre>

1. Comentariu: compilatorul îl ignoră.
2. `#include` copiază textul header-ului aici. De aici vin `ESP_LOGI` și nivelurile jurnalului (secțiunea 3).
3. Toate funcțiile `esp_wifi_*` și tipurile `wifi_*` (prin `esp_wifi_types.h`).
4. Bucla de evenimente: `esp_event_*`, `esp_event_base_t`.
5. `nvs_flash_init`: memoria flash pentru setări.
6. Interfața de rețea: `esp_netif_*`, `IP_EVENT`, `IPSTR`.
7. `MACSTR`, `MAC2STR`. În versiunea finală nu le mai folosim. Linia a rămas din etapa 4.
8. `esp_timer_get_time`: ceasul în microsecunde (secțiunea 22).
9. Ping-ul din lwIP: `esp_ping_*` (secțiunea 19).
10. Biblioteca standard C: `sqrtf`. `< >` = header de sistem, `" "` = header de proiect sau ESP-IDF.

### 2.2 `TAG` și sumele

Sursa: `pas_cu_pas/main/main.c`

<pre>
12 | <mark>static</mark> <mark>const char *TAG</mark> = <mark>&quot;CSI&quot;</mark>;  [1] [2] [3]
13 | 
14 | // sumele pentru secunda curenta
15 | static int     <mark>packets</mark>;                 // cate CSI au venit  [4]
16 | static int     <mark>rssi_total</mark>;  [5]
17 | static <mark>int64_t second_start_us</mark>;  [6]
18 | static float   <mark>amplitude_total[53]</mark>;     // pe fiecare sub-frecventa k, la pozitia k + 26  [7]
</pre>

1. `static` în afara funcțiilor: variabila este vizibilă doar în `main.c`.
2. Un pointer la un text constant. Textul `"CSI"` stă în memoria flash.
3. Eticheta din jurnal: `I (539) CSI: ...`.
4. Câte CSI au venit în secunda curentă. Crește în `on_csi`, revine la 0 o dată pe secundă.
5. Suma RSSI din secunda curentă. Împărțită la `packets` = RSSI mediu.
6. Momentul de început al secundei curente, în µs. `int64_t` = întreg cu semn pe 64 de biți, ca ceasul.
7. 53 de sume `float`, una pentru fiecare k de la −26 la +26. k = −26 → poziția 0, k = +26 → poziția 52.

De ce `static` pentru sume: o variabilă locală dispare la `return`. `on_csi` este apelată de 50 de ori pe secundă. Sumele trebuie să rămână între apeluri. Doar `on_csi` (task-ul Wi-Fi) le folosește, deci nu avem nevoie de mutex.

---

## 3. Prima linie din `app_main`: `ESP_LOGI`

`main.c`: liniile 84–85

### 3.1 Codul nostru

Sursa: `pas_cu_pas/main/main.c`

<pre>
84 | <mark>void app_main(void)</mark> {  [1]
85 |     <mark>ESP_LOGI(TAG, &quot;Salut! app_main a pornit.&quot;)</mark>;  [2]
</pre>

1. Fără parametri, fără rezultat. Numele este cerut de `main_task` (1.3).
2. Scrie linia 2 din jurnal: `I (539) CSI: Salut! app_main a pornit.`

### 3.2 `ESP_LOGI` este un macro

Sursa: `IDF/log/include/esp_log.h`

<pre>
342 | #define ESP_LOGI( tag, format, ... ) <mark>ESP_LOG_LEVEL_LOCAL(ESP_LOG_INFO</mark>,    tag, format, ##__VA_ARGS__)  [1]
</pre>

1. Compilatorul înlocuiește `ESP_LOGI(...)` cu acest text. Adaugă nivelul `ESP_LOG_INFO`.

### 3.3 Nivelurile

Sursa: `IDF/log/include/esp_log.h`

<pre>
24 | typedef enum {
25 |     <mark>ESP_LOG_NONE</mark>,       /*!&lt; No log output */  [1]
26 |     ESP_LOG_ERROR,      /*!&lt; Critical errors, software module can not recover on its own */
27 |     ESP_LOG_WARN,       /*!&lt; Error conditions from which recovery measures have been taken */
28 |     <mark>ESP_LOG_INFO</mark>,       /*!&lt; Information messages which describe normal flow of events */  [2]
29 |     <mark>ESP_LOG_DEBUG</mark>,      /*!&lt; Extra information which is not necessary for normal use (values, pointers, sizes, etc). */  [3]
30 |     ESP_LOG_VERBOSE     /*!&lt; Bigger chunks of debugging information, or frequent messages which can potentially flood the output. */
31 | } esp_log_level_t;
</pre>

1. 0 = nimic.
2. 3 = informații. `CONFIG_LOG_DEFAULT_LEVEL=3` în `sdkconfig`: liniile INFO apar.
3. 4 = depanare. Nu apar la noi.

### 3.4 Filtrul la compilare

Sursa: `IDF/log/include/esp_log.h`

<pre>
431 | #define ESP_LOG_LEVEL_LOCAL(level, tag, format, ...) do {               \
432 |         <mark>if ( LOG_LOCAL_LEVEL &gt;= level )</mark> ESP_LOG_LEVEL(level, tag, format, ##__VA_ARGS__); \  [1]
433 |     } while(0)
</pre>

1. Dacă nivelul maxim permis este mai mic, compilatorul elimină tot apelul.

### 3.5 Ce scrie de fapt: `esp_log_write` cu un format

Sursa: `IDF/log/include/esp_log.h`

<pre>
282 | #define LOG_FORMAT(letter, format)  <mark>LOG_COLOR_ ## letter #letter &quot; (%&quot; PRIu32 &quot;) %s: &quot; format</mark> <mark>LOG_RESET_COLOR &quot;\n&quot;</mark>  [1] [2]
    | ...
408 | #if <mark>CONFIG_LOG_TIMESTAMP_SOURCE_RTOS</mark>  [3]
409 | #define ESP_LOG_LEVEL(level, tag, format, ...) do {                     \
410 |         if (level==ESP_LOG_ERROR )          { esp_log_write(ESP_LOG_ERROR,      tag, LOG_FORMAT(E, format), esp_log_timestamp(), tag, ##__VA_ARGS__); } \
411 |         else if (level==ESP_LOG_WARN )      { esp_log_write(ESP_LOG_WARN,       tag, LOG_FORMAT(W, format), esp_log_timestamp(), tag, ##__VA_ARGS__); } \
412 |         else if (level==ESP_LOG_DEBUG )     { esp_log_write(ESP_LOG_DEBUG,      tag, LOG_FORMAT(D, format), esp_log_timestamp(), tag, ##__VA_ARGS__); } \
413 |         else if (level==ESP_LOG_VERBOSE )   { esp_log_write(ESP_LOG_VERBOSE,    tag, LOG_FORMAT(V, format), esp_log_timestamp(), tag, ##__VA_ARGS__); } \
414 |         else                                { <mark>esp_log_write(ESP_LOG_INFO,       tag, LOG_FORMAT(I, format), esp_log_timestamp(), tag</mark>, ##__VA_ARGS__); } \  [4]
415 |     } while(0)
</pre>

1. Formatul liniei: culoare, litera (`I`), `(timp)`, `TAG:`, apoi textul nostru. Exact `I (539) CSI: Salut!...`.
2. La final: culoarea normală și sfârșitul liniei. De aici vin `[0m` din jurnalul brut.
3. Varianta aleasă în `sdkconfig`: timpul vine de la FreeRTOS.
4. Pentru INFO: `esp_log_write` primește formatul, timpul (`esp_log_timestamp`) și `TAG`.

### 3.6 Timpul din paranteză

Sursa: `IDF/log/log_freertos.c`

<pre>
 99 | uint32_t esp_log_timestamp(void)
100 | {
101 |     if (unlikely(xTaskGetSchedulerState() == taskSCHEDULER_NOT_STARTED)) {
102 |         return esp_log_early_timestamp();
103 |     }
104 |     static uint32_t base = 0;
105 |     if (base == 0 &amp;&amp; xPortGetCoreID() == 0) {
106 |         base = esp_log_early_timestamp();
107 |     }
108 |     TickType_t tick_count = xPortInIsrContext() ? xTaskGetTickCountFromISR() : <mark>xTaskGetTickCount()</mark>;  [1]
109 |     return base + <mark>tick_count * (1000 / configTICK_RATE_HZ)</mark>;  [2]
110 | }
</pre>

1. Numărul de tick-uri FreeRTOS de la pornire.
2. Tick-uri × 10 ms (100 Hz) = milisecunde. De aceea timpii din jurnal se termină des în 9 sau 0.

### 3.7 `esp_log_write` → `vprintf` → portul serial

Sursa: `IDF/log/log.c`

<pre>
 66 | static vprintf_like_t s_log_print_func = <mark>&amp;vprintf</mark>;  [1]
    | ...
184 | void esp_log_writev(esp_log_level_t level,
185 |                    const char *tag,
186 |                    const char *format,
187 |                    va_list args)
188 | {
189 |     if (!<mark>esp_log_impl_lock_timeout()</mark>) {  [2]
190 |         return;
191 |     }
192 |     esp_log_level_t level_for_tag = s_log_level_get_and_unlock(tag);
193 |     if (!<mark>should_output(level, level_for_tag)</mark>) {  [3]
194 |         return;
195 |     }
196 | 
197 |     <mark>(*s_log_print_func)(format, args)</mark>;  [4]
198 | 
199 | }
200 | 
201 | void esp_log_write(esp_log_level_t level,
202 |                    const char *tag,
203 |                    const char *format, ...)
204 | {
205 |     va_list list;
206 |     va_start(list, format);
207 |     esp_log_writev(level, tag, format, list);
208 |     va_end(list);
</pre>

1. Implicit, jurnalul folosește `vprintf` din biblioteca C. Ieșirea standard este UART0 = cablul USB.
2. Un singur task scrie la un moment dat. Liniile nu se amestecă.
3. A doua verificare a nivelului, la rulare.
4. Scrie textul. La 115200 baud, o linie de 80 de caractere durează cam 7 ms.

---

## 4. `ESP_ERROR_CHECK` – învelește aproape fiecare apel

`main.c`: liniile 88–106

Funcțiile ESP-IDF întorc `esp_err_t`: `ESP_OK` (0) sau un cod de eroare. `ESP_ERROR_CHECK` verifică rezultatul.

### 4.1 `ESP_ERROR_CHECK`

Sursa: `IDF/esp_common/include/esp_err.h`

<pre>
116 | #else
117 | #define ESP_ERROR_CHECK(x) do {                                         \
118 |         <mark>esp_err_t err_rc_ = (x)</mark>;                                        \  [1]
119 |         if (unlikely(<mark>err_rc_ != ESP_OK</mark>)) {                              \  [2]
120 |             <mark>_esp_error_check_failed(err_rc_, __FILE__, __LINE__,</mark>        \  [3]
121 |                                     __ASSERT_FUNC, <mark>#x</mark>);                 \  [4]
122 |         }                                                               \
123 |     } while(0)
</pre>

1. Rulează apelul o singură dată și păstrează rezultatul.
2. Verifică eroarea. `unlikely` spune compilatorului: cazul este rar.
3. Afișează codul, fișierul și linia. Apoi `abort()`: placa repornește.
4. `#x` = textul apelului. Mesajul arată exact ce linie din `main.c` a eșuat.

Linia 91 (`esp_netif_create_default_wifi_sta`) nu are `ESP_ERROR_CHECK`. Funcția nu întoarce `esp_err_t`. La eroare, ea oprește singură programul (secțiunea 8).

---

## 5. `nvs_flash_init()` – memoria pentru setări

`main.c`: linia 88

### 5.1 Header

Sursa: `IDF/nvs_flash/include/nvs_flash.h`

<pre>
35 | /**
36 |  * @brief Initialize the default NVS partition.
37 |  *
38 |  * This API initialises the default NVS partition. The default NVS partition
39 |  * is the one that is <mark>labeled &quot;nvs&quot;</mark> in the partition table.  [1]
   | ...
55 |  *      - ESP_OK if storage was successfully initialized.
56 |  *      - <mark>ESP_ERR_NVS_NO_FREE_PAGES</mark> if the NVS storage contains no empty pages  [2]
57 |  *        (which may happen if NVS partition was truncated)
58 |  *      - <mark>ESP_ERR_NOT_FOUND</mark> if no partition with label &quot;nvs&quot; is found in the partition table  [3]
   | ...
65 | esp_err_t nvs_flash_init(void);
</pre>

1. Funcția caută partiția cu numele `nvs` din tabelul de partiții al memoriei flash.
2. Partiția este plină. Soluția obișnuită: `nvs_flash_erase()`, apoi din nou `init`.
3. Tabelul de partiții nu are partiția `nvs`.

### 5.2 Implementare

Sursa: `IDF/nvs_flash/src/nvs_api.cpp`

<pre>
128 | extern &quot;C&quot; esp_err_t nvs_flash_init(void)
129 | {
    | ...
160 | <mark>#else // CONFIG_NVS_ENCRYPTION</mark>  [1]
161 |     return <mark>nvs_flash_init_partition(NVS_DEFAULT_PART_NAME)</mark>;  [2]
162 | #endif
163 | }
</pre>

1. Proiectul nu are criptare NVS. Rulează doar ramura de mai jos.
2. Tot lucrul real: inițializează partiția `"nvs"`.

**Rol în program:** driverul Wi-Fi salvează în `nvs` calibrarea radio și setările (`config NVS flash: enabled`, linia 6 din jurnal). Fără `nvs_flash_init`, `esp_wifi_init` eșuează.

---

## 6. `esp_netif_init()` – stiva TCP/IP

`main.c`: linia 89

### 6.1 Header

Sursa: `IDF/esp_netif/include/esp_netif.h`

<pre>
31 | /**
32 |  * @brief  <mark>Initialize the underlying TCP/IP stack</mark>  [1]
33 |  *
34 |  * @return
35 |  *         - ESP_OK on success
36 |  *         - ESP_FAIL if initializing failed
37 | 
38 |  * @note This function should be called <mark>exactly once</mark> from application code, when the application starts up.  [2]
39 |  */
40 | esp_err_t esp_netif_init(void);
</pre>

1. Pornește stiva TCP/IP (lwIP).
2. Un singur apel, la pornirea aplicației.

### 6.2 Implementare

Sursa: `IDF/esp_netif/lwip/esp_netif_lwip.c`

<pre>
533 |         sys_sem_t init_sem;
534 |         if (<mark>sys_sem_new(&amp;init_sem, 0)</mark> != ERR_OK) {  [1]
535 |             ESP_LOGE(TAG, &quot;esp netif cannot create tcpip_init semaphore&quot;);
536 |             return ESP_FAIL;
537 |         }
538 | #if LWIP_TCPIP_CORE_LOCKING
539 |         /* TCPIP thread is not initialized yet,
540 |          * pretend that the calling thread is holder
541 |          * to correctly set up the TCPIP task */
542 |         sys_thread_tcpip(LWIP_CORE_LOCK_MARK_HOLDER);
543 | #endif
544 |         <mark>tcpip_init(tcpip_init_done, &amp;init_sem)</mark>;  [2]
545 |         <mark>sys_sem_wait(&amp;init_sem)</mark>;  [3]
546 |         sys_sem_free(&amp;init_sem);
547 |         ESP_LOGD(TAG, &quot;LwIP stack has been initialized&quot;);
</pre>

1. Creează un semafor închis. Funcția va aștepta la el.
2. lwIP pornește task-ul `tiT`. La final, `tcpip_init_done` deschide semaforul.
3. `app_main` așteaptă aici până când stiva IP este gata.

### 6.3 Numele task-ului lwIP

Sursa: `IDF/lwip/port/include/lwipopts.h`

<pre>
810 | #define TCPIP_THREAD_NAME              <mark>&quot;tiT&quot;</mark>  [1]
</pre>

1. Task-ul care procesează pachetele IP (DHCP, ICMP) se numește `tiT`.

---

## 7. `esp_event_loop_create_default()` – bucla de evenimente

`main.c`: linia 90

### 7.1 Header

Sursa: `IDF/esp_event/include/esp_event.h`

<pre>
60 | /**
61 |  * @brief <mark>Create default event loop</mark>  [1]
62 |  *
63 |  * @return
64 |  *  - ESP_OK: Success
65 |  *  - ESP_ERR_NO_MEM: Cannot allocate memory for event loops list
66 |  *  - <mark>ESP_ERR_INVALID_STATE</mark>: Default event loop has already been created  [2]
67 |  *  - ESP_FAIL: Failed to create task loop
68 |  *  - Others: Fail
69 |  */
70 | esp_err_t esp_event_loop_create_default(void);
</pre>

1. Bucla folosită de driverul Wi-Fi și de stiva IP.
2. Al doilea apel eșuează. Bucla implicită există o singură dată.

### 7.2 Implementare

Sursa: `IDF/esp_event/default_event_loop.c`

<pre>
 94 | esp_err_t esp_event_loop_create_default(void)
 95 | {
 96 |     <mark>if (s_default_loop)</mark> {  [1]
 97 |         return ESP_ERR_INVALID_STATE;
 98 |     }
 99 | 
100 |     esp_event_loop_args_t loop_args = {
101 |         .queue_size = <mark>CONFIG_ESP_SYSTEM_EVENT_QUEUE_SIZE</mark>,  [2]
102 |         .task_name = <mark>&quot;sys_evt&quot;</mark>,  [3]
103 |         .task_stack_size = ESP_TASKD_EVENT_STACK,
104 |         .task_priority = <mark>ESP_TASKD_EVENT_PRIO</mark>,  [4]
105 |         <mark>.task_core_id = 0</mark>  [5]
106 |     };
107 | 
108 |     esp_err_t err;
109 | 
110 |     err = <mark>esp_event_loop_create(&amp;loop_args, &amp;s_default_loop)</mark>;  [6]
111 |     if (err != ESP_OK) {
112 |         return err;
113 |     }
114 | 
115 |     return ESP_OK;
</pre>

1. Dacă bucla există deja, întoarce eroare.
2. Coada are 32 de locuri. Evenimentele așteaptă aici.
3. Numele task-ului care va apela `on_event`.
4. Prioritate `ESP_TASK_PRIO_MAX - 5` = 25 − 5 = 20: mai mică decât task-ul Wi-Fi (23).
5. Task-ul rulează pe nucleul 0, ca task-ul Wi-Fi.
6. Creează coada și task-ul. Salvează bucla în `s_default_loop`.

---

## 8. `esp_netif_create_default_wifi_sta()` – legătura Wi-Fi ↔ IP

`main.c`: linia 91

### 8.1 Header

Sursa: `IDF/esp_wifi/include/esp_wifi_default.h`

<pre>
85 | /**
86 |  * @brief Creates default WIFI STA. In case of any init error <mark>this API aborts</mark>.  [1]
87 |  *
88 |  * @note The API creates esp_netif object with default WiFi station config,
89 |  * <mark>attaches the netif to wifi</mark> and <mark>registers wifi handlers to the default event loop</mark>.  [2] [3]
90 |  * This API uses assert() to check for potential errors, so it could abort the program.
91 |  * (Note that the <mark>default event loop needs to be created prior</mark> to calling this API)  [4]
92 |  *
93 |  * @return pointer to esp-netif instance
94 |  */
95 | esp_netif_t* esp_netif_create_default_wifi_sta(void);
</pre>

1. Funcția nu întoarce erori. La eroare, oprește programul. De aceea nu are `ESP_ERROR_CHECK`.
2. Leagă interfața IP de driverul Wi-Fi.
3. Înregistrează funcțiile ESP-IDF pentru evenimente. De aici vine linia `sta ip:` din jurnal.
4. Bucla de evenimente trebuie creată înainte: ordinea liniilor 90 și 91 contează.

### 8.2 Implementare

Sursa: `IDF/esp_wifi/src/wifi_default.c`

<pre>
385 | esp_netif_t* esp_netif_create_default_wifi_sta(void)
386 | {
387 |     esp_netif_config_t cfg = <mark>ESP_NETIF_DEFAULT_WIFI_STA()</mark>;  [1]
388 |     esp_netif_t *netif = <mark>esp_netif_new(&amp;cfg)</mark>;  [2]
389 |     <mark>assert(netif)</mark>;  [3]
390 |     ESP_ERROR_CHECK(<mark>esp_netif_attach_wifi_station(netif)</mark>);  [4]
391 |     ESP_ERROR_CHECK(<mark>esp_wifi_set_default_wifi_sta_handlers()</mark>);  [5]
392 |     return netif;
393 | }
</pre>

1. Setările implicite pentru stație: client DHCP pornit.
2. Creează interfața de rețea.
3. Acesta este „abort” din header.
4. Pachetele primite prin Wi-Fi ajung la stiva IP prin această legătură.
5. Reacțiile ESP-IDF la conectare, deconectare și IP.

---

## 9. `WIFI_INIT_CONFIG_DEFAULT()` și `esp_wifi_init()` – driverul Wi-Fi

`main.c`: liniile 92–93

### 9.1 Codul nostru

Sursa: `pas_cu_pas/main/main.c`

<pre>
92 |     <mark>wifi_init_config_t wifi_init</mark> = <mark>WIFI_INIT_CONFIG_DEFAULT()</mark>;  [1] [2]
93 |     ESP_ERROR_CHECK(esp_wifi_init(<mark>&amp;wifi_init</mark>));  [3]
</pre>

1. Variabilă locală pe stiva lui `app_main`. Driverul copiază setările, deci poate dispărea după `return`.
2. Macro: completează toate câmpurile cu valori din `sdkconfig`.
3. Trimitem adresa structurii, nu o copie.

### 9.2 `WIFI_INIT_CONFIG_DEFAULT` și `WIFI_CSI_ENABLED`

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
146 | #if <mark>CONFIG_ESP_WIFI_CSI_ENABLED</mark>  [1]
147 | #define <mark>WIFI_CSI_ENABLED         1</mark>  [2]
148 | #else
149 | #define <mark>WIFI_CSI_ENABLED         0</mark>  [3]
150 | #endif
    | ...
283 | #define WIFI_INIT_CONFIG_DEFAULT() { \
284 |     .osi_funcs = &amp;g_wifi_osi_funcs, \
285 |     .wpa_crypto_funcs = g_wifi_default_wpa_crypto_funcs, \
286 |     .static_rx_buf_num = <mark>CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM</mark>,\  [4]
287 |     .dynamic_rx_buf_num = <mark>CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM</mark>,\  [5]
    | ...
294 |     <mark>.csi_enable = WIFI_CSI_ENABLED</mark>,\  [6]
    | ...
298 |     <mark>.nvs_enable = WIFI_NVS_ENABLED</mark>,\  [7]
    | ...
307 |     <mark>.magic = WIFI_INIT_CONFIG_MAGIC</mark>\  [8]
308 | }
</pre>

1. Vine din `sdkconfig.defaults` al proiectului. Fără el, CSI nu există în driver.
2. Cu opțiunea activă, macro-ul devine 1.
3. Fără opțiune: 0. Atunci `esp_wifi_set_csi` întoarce `ESP_FAIL` (secțiunea 16).
4. Bufferele RX fixe. Jurnal, linia 13: `static rx buffer num: 10`.
5. Bufferele RX dinamice. Jurnal, linia 14: `dynamic rx buffer num: 32`.
6. Câmpul care spune driverului: „CSI este permis”.
7. Jurnal, linia 6: `config NVS flash: enabled`.
8. Un număr fix de verificare. Driverul refuză o structură greșită.

### 9.3 `esp_wifi_init` – header

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
310 | /**
311 |   * @brief  Initialize WiFi
312 |   *         <mark>Allocate resource for WiFi driver</mark>, such as WiFi control structure, RX/TX buffer,  [1]
313 |   *         WiFi NVS structure etc. <mark>This WiFi also starts WiFi task</mark>  [2]
314 |   *
315 |   * @attention 1. This API must be called before all other WiFi API can be called
316 |   * @attention 2. <mark>Always use WIFI_INIT_CONFIG_DEFAULT</mark> macro to initialize the configuration to default values, this can  [3]
317 |   *               guarantee all the fields get correct value when more fields are added into wifi_init_config_t
318 |   *               in future release. If you want to set your own initial values, overwrite the default values
319 |   *               which are set by WIFI_INIT_CONFIG_DEFAULT. Please be notified that the field &#x27;magic&#x27; of
320 |   *               wifi_init_config_t should always be WIFI_INIT_CONFIG_MAGIC!
321 |   *
322 |   * @param  config pointer to WiFi initialized configuration structure; <mark>can point to a temporary variable</mark>.  [4]
    | ...
329 | esp_err_t esp_wifi_init(const wifi_init_config_t *config);
</pre>

1. Alocă memoria driverului: structuri de control și buffere RX/TX.
2. Aici apare task-ul Wi-Fi (`prio:23`, jurnal linia 3). El va apela `on_csi`.
3. Nu completa structura de mână.
4. Confirmă: `wifi_init` poate fi variabilă locală.

### 9.4 `esp_wifi_init` – partea deschisă

Sursa: `IDF/esp_wifi/src/wifi_init.c`

<pre>
305 | esp_err_t esp_wifi_init(const wifi_init_config_t *config)
306 | {
307 |     <mark>if (s_wifi_inited)</mark> {  [1]
308 |         return ESP_OK;
309 |     }
    | ...
328 |     uint32_t min_active_time_us = CONFIG_ESP_WIFI_SLP_DEFAULT_MIN_ACTIVE_TIME * 1000;
329 |     <mark>esp_wifi_set_sleep_min_active_time</mark>(min_active_time_us);  [2]
330 | 
331 |     uint32_t keep_alive_time_us = CONFIG_ESP_WIFI_SLP_DEFAULT_MAX_ACTIVE_TIME * 1000 * 1000;
332 |     esp_wifi_set_keep_alive_time(keep_alive_time_us);
    | ...
384 | #if CONFIG_SW_COEXIST_ENABLE || CONFIG_EXTERNAL_COEX_ENABLE
385 |     <mark>coex_init()</mark>;  [3]
386 | #endif
    | ...
395 | #endif
396 |     result = <mark>esp_wifi_init_internal(config)</mark>;  [4]
397 |     if (result == ESP_OK) {
398 | #if CONFIG_MAC_BB_PD
399 |         esp_mac_bb_pd_mem_init();
400 |         esp_wifi_mac_pd_mem_init();
401 | #endif
402 |         <mark>esp_phy_modem_init()</mark>;  [5]
403 | #if CONFIG_ESP_WIFI_ENHANCED_LIGHT_SLEEP
    | ...
450 |     <mark>s_wifi_inited = true</mark>;  [6]
</pre>

1. Al doilea apel nu face nimic și întoarce `ESP_OK`.
2. Timpii pentru economia de energie (legătura cu `pm start`, jurnal linia 36).
3. Doar cu coexistență Wi-Fi/Bluetooth. La noi opțiunea este oprită.
4. De aici începe codul închis din `libnet80211.a`. El creează task-ul Wi-Fi.
5. Pregătește partea radio (PHY).
6. Marchează driverul ca pornit.

### 9.5 Urma în jurnal

Sursa: `pas_cu_pas/output/07_main_nou.log`

<pre>
 3 | I (579) wifi:wifi driver task: 3ffbfccc, <mark>prio:23</mark>, stack:6656, core=0  [1]
   | ...
 6 | I (589) wifi:config NVS flash: <mark>enabled</mark>  [2]
   | ...
13 | I (619) wifi:Init static rx buffer num: <mark>10</mark>  [3]
14 | I (619) wifi:Init dynamic rx buffer num: <mark>32</mark>  [4]
</pre>

1. Task-ul Wi-Fi, prioritatea 23, pe nucleul 0.
2. `.nvs_enable` din macro.
3. `static_rx_buf_num`.
4. `dynamic_rx_buf_num`.

---

## 10. `esp_event_handler_register()` – înregistrăm `on_event`

`main.c`: liniile 96–97

### 10.1 Codul nostru

Sursa: `pas_cu_pas/main/main.c`

<pre>
96 |     ESP_ERROR_CHECK(esp_event_handler_register(<mark>WIFI_EVENT, ESP_EVENT_ANY_ID</mark>, on_event, NULL));  [1]
97 |     ESP_ERROR_CHECK(esp_event_handler_register(<mark>IP_EVENT, IP_EVENT_STA_GOT_IP</mark>, <mark>on_event, NULL</mark>));  [2] [3]
</pre>

1. Toate evenimentele Wi-Fi. Filtrăm noi, în `on_event`.
2. Din familia IP, doar „am primit IP”.
3. Aceeași funcție pentru ambele. `NULL` = argumentul `arg` din `on_event`.

### 10.2 Ce este o „familie” de evenimente

Sursa: `IDF/esp_event/include/esp_event_base.h`

<pre>
15 | #define ESP_EVENT_DECLARE_BASE(id) <mark>extern esp_event_base_t const id</mark>  [1]
16 | #define ESP_EVENT_DEFINE_BASE(id) <mark>esp_event_base_t const id = #id</mark>  [2]
17 | 
18 | // Event loop library types
19 | typedef <mark>const char*</mark>  esp_event_base_t; /**&lt; unique pointer to a subsystem that exposes events */  [3]
   | ...
29 | #define ESP_EVENT_ANY_ID       <mark>-1</mark>               /**&lt; register handler for any event id */  [4]
</pre>

1. Declarația: o variabilă globală constantă.
2. Definiția: valoarea este textul numelui. `WIFI_EVENT` = pointer la textul `"WIFI_EVENT"`.
3. O familie = un pointer la text. Două familii diferite au adrese diferite.
4. −1 = toate evenimentele familiei.

### 10.3 Unde este definită `WIFI_EVENT`

Sursa: `IDF/esp_wifi/src/wifi_init.c`

<pre>
47 | <mark>ESP_EVENT_DEFINE_BASE(WIFI_EVENT)</mark>;  [1]
</pre>

1. O singură definiție în tot programul. În `on_event`, `base == WIFI_EVENT` compară adrese, nu texte.

### 10.4 Header

Sursa: `IDF/esp_event/include/esp_event.h`

<pre>
109 | /**
110 |  * @brief Register an event handler to the system event loop (legacy).
111 |  *
    | ...
123 |  * @param[in] <mark>event_base</mark> the base ID of the event to register the handler for  [1]
124 |  * @param[in] <mark>event_id</mark> the ID of the event to register the handler for  [2]
125 |  * @param[in] <mark>event_handler</mark> the handler function which gets called when the event is dispatched  [3]
126 |  * @param[in] <mark>event_handler_arg</mark> data, aside from event data, that is passed to the handler when it is called  [4]
127 |  *
128 |  * @note the event loop library <mark>does not maintain a copy</mark> of event_handler_arg, therefore the user should  [5]
129 |  * ensure that event_handler_arg still points to a valid location by the time the handler gets called
    | ...
137 | esp_err_t esp_event_handler_register(esp_event_base_t event_base,
138 |                                      int32_t event_id,
</pre>

1. Familia: `WIFI_EVENT` sau `IP_EVENT`.
2. Evenimentul exact, sau `ESP_EVENT_ANY_ID`.
3. Funcția noastră, `on_event`.
4. Pointerul nostru (`NULL`), trimis neschimbat lui `on_event`.
5. Biblioteca păstrează doar adresa.

### 10.5 Implementare

Sursa: `IDF/esp_event/default_event_loop.c`

<pre>
13 | static esp_event_loop_handle_t <mark>s_default_loop = NULL</mark>;  [1]
   | ...
17 | esp_err_t esp_event_handler_register(esp_event_base_t event_base, int32_t event_id,
18 |         esp_event_handler_t event_handler, void* event_handler_arg)
19 | {
20 |     if (s_default_loop == NULL) {
21 |         return <mark>ESP_ERR_INVALID_STATE</mark>;  [2]
22 |     }
23 | 
24 |     return <mark>esp_event_handler_register_with(s_default_loop</mark>, event_base, event_id,  [3]
25 |             event_handler, event_handler_arg);
26 | }
</pre>

1. Bucla implicită. La început este `NULL`.
2. Fără linia 90 înainte, înregistrarea eșuează.
3. Adaugă `on_event` în lista buclei implicite.

**De ce înainte de `esp_wifi_start`:** `start` trimite evenimentul `WIFI_EVENT_STA_START`. Dacă `on_event` nu este încă în listă, evenimentul se pierde. Atunci nimeni nu apelează `esp_wifi_connect`.

---

## 11. `wifi_config_t hotspot` – numele rețelei și parola

`main.c`: liniile 98–99

### 11.1 Codul nostru

Sursa: `pas_cu_pas/main/main.c`

<pre>
98 |     <mark>wifi_config_t hotspot</mark> = <mark>{.sta = {</mark>.ssid = <mark>CONFIG_CSI_WIFI_SSID</mark>,  [1] [2] [3]
99 |                                      .password = <mark>CONFIG_CSI_WIFI_PASSWORD</mark>}};  [4]
</pre>

1. Variabilă locală în `app_main`.
2. Inițializare cu nume de câmpuri: completăm doar `.sta.ssid` și `.sta.password`. Restul devine 0.
3. Un macro de text, creat din `Kconfig.projbuild`.
4. Parola, tot din configurare. Nu apare în cod.

### 11.2 De unde vin `CONFIG_CSI_WIFI_*`

Sursa: `pas_cu_pas/main/Kconfig.projbuild`

<pre>
1 | menu &quot;Pas cu pas&quot;
2 |     config <mark>CSI_WIFI_SSID</mark>  [1]
3 |         string &quot;Wi-Fi SSID&quot;
4 |         <mark>default &quot;&quot;</mark>  [2]
5 |     config CSI_WIFI_PASSWORD
6 |         string &quot;Wi-Fi password&quot;
7 |         default &quot;&quot;
8 | endmenu
</pre>

1. Opțiunea devine macro-ul `CONFIG_CSI_WIFI_SSID` în `sdkconfig.h`.
2. Implicit gol. Valoarea reală vine din `~/esp/csi-node/wifi.defaults`, în afara repo-ului (vezi `ruleaza.sh`).

### 11.3 `wifi_config_t` este un `union`

Sursa: `IDF/esp_wifi/include/esp_wifi_types.h`

<pre>
371 | typedef <mark>union</mark> {  [1]
372 |     wifi_ap_config_t  ap;  /**&lt; configuration of AP */
373 |     wifi_<mark>sta</mark>_config_t sta; /**&lt; configuration of STA */  [2]
374 |     wifi_nan_config_t nan; /**&lt; configuration of NAN */
375 | } wifi_config_t;
</pre>

1. `union` = câmpurile ocupă aceeași memorie. Folosim una dintre ele.
2. Noi folosim `.sta`: setările pentru stație.

### 11.4 Primele câmpuri din `wifi_sta_config_t`

Sursa: `IDF/esp_wifi/include/esp_wifi_types.h`

<pre>
319 | /** @brief STA configuration settings for the device */
320 | typedef struct {
321 |     uint8_t <mark>ssid[32]</mark>;                         /**&lt; SSID of target AP. */  [1]
322 |     uint8_t <mark>password[64]</mark>;                     /**&lt; Password of target AP. */  [2]
323 |     wifi_<mark>scan_method</mark>_t scan_method;           /**&lt; do all channel scan or fast scan */  [3]
</pre>

1. Maximum 32 de octeți.
2. Maximum 64 de octeți.
3. Câmpurile următoare rămân 0 = valori implicite.

---

## 12. `esp_wifi_set_mode(WIFI_MODE_STA)`

`main.c`: linia 100

### 12.1 Modurile posibile

Sursa: `IDF/esp_wifi/include/esp_wifi_types.h`

<pre>
20 | typedef enum {
21 |     <mark>WIFI_MODE_NULL = 0</mark>,  /**&lt; null mode */  [1]
22 |     <mark>WIFI_MODE_STA</mark>,       /**&lt; WiFi station mode */  [2]
23 |     <mark>WIFI_MODE_AP</mark>,        /**&lt; WiFi soft-AP mode */  [3]
24 |     WIFI_MODE_APSTA,     /**&lt; WiFi station + soft-AP mode */
25 |     WIFI_MODE_NAN,       /**&lt; WiFi NAN mode */
26 |     WIFI_MODE_MAX
27 | } wifi_mode_t;
</pre>

1. Radioul oprit.
2. 1 = stație (client). Alegerea noastră.
3. 2 = punct de acces (placa ar fi hotspot).

### 12.2 Header

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
345 |   *
346 |   *            Set the WiFi operating mode as station, soft-AP, station+soft-AP or NAN.
347 |   *            <mark>The default mode is station mode</mark>.  [1]
    | ...
357 | esp_err_t esp_wifi_set_mode(wifi_mode_t mode);
</pre>

1. Fără apel, placa ar fi tot stație. Apelul face codul explicit.

---

## 13. `esp_wifi_set_config(WIFI_IF_STA, &hotspot)`

`main.c`: linia 101

### 13.1 Header

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
898 |   *
    | ...
903 |   * @attention 4. The configuration will be <mark>stored in NVS</mark> for station and soft-AP  [1]
904 |   *
905 |   * @param     <mark>interface</mark>  interface  [2]
906 |   * @param     <mark>conf</mark>  station, soft-AP or NAN configuration  [3]
    | ...
919 | esp_err_t esp_wifi_set_config(wifi_interface_t interface, wifi_config_t *conf);
</pre>

1. SSID-ul și parola se salvează în partiția `nvs` (secțiunea 5).
2. `WIFI_IF_STA`: setările sunt pentru stație.
3. Adresa lui `hotspot`. Driverul copiază datele (`memcpy`, vezi tabelul din secțiunea 14).

Jurnal, linia 24: `Password length matches WPA2 standards`. Driverul a verificat lungimea parolei. Parola nu apare în jurnal.

---

## 14. `esp_wifi_start()` – și cum lucrează toate funcțiile `esp_wifi_*`

`main.c`: linia 102

### 14.1 Header

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
371 | /**
372 |   * @brief  Start WiFi according to current configuration
373 |   *         If mode is WIFI_MODE_STA, it <mark>creates station control block and starts station</mark>  [1]
    | ...
386 | esp_err_t esp_wifi_start(void);
</pre>

1. Creează structura stației și pornește radioul.

### 14.2 `esp_wifi_start` – instrucțiuni mașină

Sursa: `libnet80211.a (objdump)`

<pre>
   0:   <mark>00003001</mark>  [1]
        ...
                        4: R_XTENSA_32  g_osi_funcs_p
                        8: R_XTENSA_32  <mark>wifi_start_process</mark>  [2]
                        c: R_XTENSA_32  wifi_init_completed
                        10: R_XTENSA_32 ieee80211_ioctl
  --
  14:   004136          entry   a1, 32
  17:   fffd81          l32r    a8, c &lt;esp_wifi_start-0x8&gt; (0 &lt;esp_wifi_start-0x14&gt;)
                        17: R_XTENSA_ASM_EXPAND <mark>wifi_init_completed</mark>  [3]
  1a:   0008e0          callx8  a8
  1d:   fff821          l32r    a2, 0 &lt;esp_wifi_start-0x14&gt; (3001 &lt;esp_wifi_stop+0x2f91&gt;)
  20:   aaac            <mark>beqz.n  a10</mark>, 4e &lt;esp_wifi_start+0x3a&gt;  [4]
  22:   18a0a2          movi    a10, 24
  25:   fff721          l32r    a2, 4 &lt;esp_wifi_start-0x10&gt; (0 &lt;esp_wifi_start-0x14&gt;)
  28:   002222          l32i    a2, a2, 0
  2b:   5e2222          l32i    a2, a2, <mark>0x178</mark>  [5]
  2e:   0002e0          callx8  a2
  31:   01a122          movi    a2, <mark>0x101</mark>  [6]
  34:   6a9c            beqz.n  a10, 4e &lt;esp_wifi_start+0x3a&gt;
  36:   fff421          l32r    a2, 8 &lt;esp_wifi_start-0xc&gt; (0 &lt;esp_wifi_start-0x14&gt;)
  39:   1a29            <mark>s32i.n  a2, a10, 4</mark>  [7]
  3b:   120c            movi.n  a2, 1
  3d:   004a22          s8i     a2, a10, 0
  40:   0020c0          memw
  43:   0020c0          memw
  46:   fff281          l32r    a8, 10 &lt;esp_wifi_start-0x4&gt; (0 &lt;esp_wifi_start-0x14&gt;)
                        46: R_XTENSA_ASM_EXPAND <mark>ieee80211_ioctl</mark>  [8]
  49:   0008e0          callx8  a8
  4c:   0a2d            mov.n   a2, a10
  4e:   f01d            retw.n
</pre>

1. Constanta `0x3001` = `ESP_ERR_WIFI_NOT_INIT`.
2. Adresa funcției care face lucrul real. Este pusă într-un mesaj, nu apelată direct.
3. Verificare: a rulat `esp_wifi_init`?
4. Dacă nu: iese cu `0x3001`.
5. Apel prin tabelul `g_osi_funcs_p`: alocă un mesaj de 24 de octeți (`a10 = 24`).
6. Dacă alocarea eșuează: `ESP_ERR_NO_MEM`.
7. Scrie în mesaj adresa lui `wifi_start_process`.
8. Trimite mesajul task-ului Wi-Fi.

### 14.3 `ieee80211_ioctl` (doar liniile cu apeluri)

Sursa: `libnet80211.a (objdump)`

<pre>
                        79: R_XTENSA_ASM_EXPAND <mark>current_task_is_wifi_task</mark>  [1]
...
                        de: R_XTENSA_ASM_EXPAND wifi_log
...
                        f6: R_XTENSA_ASM_EXPAND <mark>wifi_api_lock</mark>  [2]
...
                        104: R_XTENSA_ASM_EXPAND        wifi_get_init_state
...
                        127: R_XTENSA_ASM_EXPAND        wifi_api_unlock
...
                        144: R_XTENSA_ASM_EXPAND        wifi_is_stop_in_progress
...
                        166: R_XTENSA_ASM_EXPAND        wifi_api_unlock
...
                        184: R_XTENSA_ASM_EXPAND        <mark>pp_post</mark>  [3]
...
                        19a: R_XTENSA_ASM_EXPAND        wifi_log
...
                        1a0: R_XTENSA_ASM_EXPAND        wifi_api_unlock
...
                        1bc: R_XTENSA_ASM_EXPAND        wifi_api_unlock
...
                        1e6: R_XTENSA_ASM_EXPAND        <mark>ieee80211_ioctl_process</mark>  [4]
</pre>

1. Cine cere? Dacă este chiar task-ul Wi-Fi, mesajul se execută direct.
2. Blochează API-ul: două task-uri nu pot schimba driverul simultan.
3. Pune mesajul în coada task-ului Wi-Fi.
4. Aici se execută mesajul: se apelează funcția din el.

**Același tipar** (verificat cu `objdump`) la toate funcțiile `esp_wifi_*` din `main.c`:

| Funcție | Funcția pusă în mesaj |
|---|---|
| `esp_wifi_set_mode` | `wifi_set_mode_process` |
| `esp_wifi_set_config` | `wifi_set_config_process` (înainte: `memcpy` al setărilor) |
| `esp_wifi_start` | `wifi_start_process` |
| `esp_wifi_connect` | `wifi_connect_process` |
| `esp_wifi_set_csi` | `wifi_set_csi` (secțiunea 16) |

**Concluzie:** funcțiile `esp_wifi_*` nu lucrează direct cu radioul. Ele trimit „bilețele” task-ului Wi-Fi. De aceea `app_main` se termină în 290 ms. Jurnal, linia 27: `mode : sta (fc:e8:c0:e1:1e:d0)` = adresa MAC a plăcii.

---

## 15. `esp_wifi_set_csi_rx_cb(on_csi, NULL)` – înregistrăm `on_csi`

`main.c`: linia 105

### 15.1 Header și tipul `wifi_csi_cb_t`

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
1117 |   * @brief The RX callback function of Channel State Information(CSI)  data.
1118 |   *
1119 |   *        Each time a CSI data is received, the callback function will be called.
1120 |   *
1121 |   * @param <mark>ctx</mark> context argument, passed to esp_wifi_set_csi_rx_cb() when registering callback function.  [1]
1122 |   * @param data CSI data received. The memory that it points to will be <mark>deallocated after callback function returns</mark>.  [2]
1123 |   *
1124 |   */
1125 | typedef <mark>void (* wifi_csi_cb_t)(void *ctx, wifi_csi_info_t *data)</mark>;  [3]
     | ...
1129 |   * @brief Register the RX callback function of CSI data.
1130 |   *
1131 |   *        Each time a CSI data is received, the callback function will be called.
1132 |   *
1133 |   * @param <mark>cb</mark>  callback  [4]
1134 |   * @param <mark>ctx</mark> context argument, passed to callback function  [5]
     | ...
1141 | esp_err_t esp_wifi_set_csi_rx_cb(wifi_csi_cb_t cb, void *ctx);
</pre>

1. Primul parametru al lui `on_csi`: pointerul dat la înregistrare (`NULL`).
2. După `return` din `on_csi`, memoria `info` dispare.
3. Forma obligatorie a lui `on_csi`. De aceea are parametrul `ctx`, deși nu îl folosim.
4. Funcția noastră: `on_csi`.
5. Valoarea trimisă înapoi la fiecare apel: `NULL`.

### 15.2 `esp_wifi_set_csi_rx_cb` – instrucțiuni mașină

Sursa: `libnet80211.a (objdump)`

<pre>
   0:   00003001
        ...
                        4: R_XTENSA_32  <mark>wifi_init_completed</mark>  [1]
                        8: R_XTENSA_32  ic_register_csi_rx_cb
  --
   c:   004136          entry   a1, 32
   f:   fffd81          l32r    a8, 4 &lt;esp_wifi_set_csi_rx_cb-0x8&gt; (0 &lt;esp_wifi_set_csi_rx_cb-0xc&gt;)
                        f: R_XTENSA_ASM_EXPAND  <mark>wifi_init_completed</mark>  [2]
  12:   0008e0          callx8  a8
  15:   fffa81          l32r    a8, 0 &lt;esp_wifi_set_csi_rx_cb-0xc&gt; (3001 &lt;esp_wifi_stop+0x2f91&gt;)
  18:   aa8c            <mark>beqz.n  a10</mark>, 26 &lt;esp_wifi_set_csi_rx_cb+0x1a&gt;  [3]
  1a:   03bd            mov.n   <mark>a11, a3</mark>  [4]
  1c:   02ad            mov.n   a10, a2
  1e:   fffa81          l32r    a8, 8 &lt;esp_wifi_set_csi_rx_cb-0x4&gt; (0 &lt;esp_wifi_set_csi_rx_cb-0xc&gt;)
                        1e: R_XTENSA_ASM_EXPAND <mark>ic_register_csi_rx_cb</mark>  [5]
  21:   0008e0          callx8  a8
  24:   080c            <mark>movi.n  a8, 0</mark>  [6]
  26:   082d            mov.n   a2, a8
  28:   f01d            retw.n
</pre>

1. Literal pool: adresele funcțiilor apelate.
2. Apel: a rulat `esp_wifi_init`?
3. Dacă nu, iese cu `0x3001` = `ESP_ERR_WIFI_NOT_INIT`.
4. `cb` (`a2`) și `ctx` (`a3`) trec mai departe neschimbate.
5. Apel direct, fără mesaj și fără coadă.
6. Rezultat 0 = `ESP_OK`.

### 15.3 `wdev_set_csi_rx_cb` (apelată de `ic_register_csi_rx_cb`)

Sursa: `libpp.a (objdump)`

<pre>
        ...
                        0: R_XTENSA_32  <mark>g_wdev_csi_rx</mark>  [1]
                        4: R_XTENSA_32  <mark>g_wdev_csi_rx_ctx</mark>  [2]
  --
   8:   004136          entry   a1, 32
   b:   fffd81          l32r    a8, 0 &lt;wdev_set_csi_rx_cb-0x8&gt; (0 &lt;wdev_set_csi_rx_cb-0x8&gt;)
   e:   0829            <mark>s32i.n  a2, a8, 0</mark>  [3]
  10:   020c            movi.n  a2, 0
  12:   fffc81          l32r    a8, 4 &lt;wdev_set_csi_rx_cb-0x4&gt; (0 &lt;wdev_set_csi_rx_cb-0x8&gt;)
  15:   0839            <mark>s32i.n  a3, a8, 0</mark>  [4]
  17:   0020c0          memw
  1a:   f01d            retw.n
</pre>

1. Variabila globală pentru adresa lui `on_csi`.
2. Variabila globală pentru `ctx`.
3. Scrie `on_csi` în `g_wdev_csi_rx`. Atât face „înregistrarea”.
4. Scrie `NULL` în `g_wdev_csi_rx_ctx`.

---

## 16. `esp_wifi_set_csi(true)` – până la registrul de control

`main.c`: linia 106

### 16.1 Header

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
1157 |   * @brief Enable or disable CSI
1158 |   *
1159 |   * @param en <mark>true - enable</mark>, false - disable  [1]
     | ...
1162 |   *    - ESP_OK: succeed
1163 |   *    - ESP_ERR_WIFI_NOT_INIT: WiFi is not initialized by esp_wifi_init
1164 |   *    - ESP_ERR_WIFI_NOT_STARTED: WiFi is not started by esp_wifi_start <mark>or promiscuous mode is not enabled</mark>  [2]
1165 |   *    - ESP_ERR_INVALID_ARG: invalid argument
     | ...
1167 | esp_err_t esp_wifi_set_csi(bool en);
</pre>

1. `true` pornește măsurarea CSI.
2. Header-ul cere modul promiscuu. În practică nu este obligatoriu: noi nu îl pornim și funcția întoarce `ESP_OK`.

### 16.2 `esp_wifi_set_csi` – instrucțiuni mașină

Sursa: `libnet80211.a (objdump)`

<pre>
   0:   <mark>00003001</mark>  [1]
   4:   <mark>00003002</mark>  [2]
        ...
                        8: R_XTENSA_32  g_ic
                        c: R_XTENSA_32  .rodata_wlog_error.49
                        10: R_XTENSA_32 g_osi_funcs_p
                        14: R_XTENSA_32 <mark>wifi_set_csi</mark>  [3]
                        18: R_XTENSA_32 wifi_init_completed
                        1c: R_XTENSA_32 config_get_wifi_csi_enable
                        20: R_XTENSA_32 wifi_log
                        24: R_XTENSA_32 ieee80211_ioctl
  --
  28:   004136          entry   a1, 32
  2b:   fffb81          l32r    a8, 18 &lt;esp_wifi_set_csi-0x10&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
                        2b: R_XTENSA_ASM_EXPAND <mark>wifi_init_completed</mark>  [4]
  2e:   0008e0          callx8  a8
  31:   743020          extui   a3, a2, 0, 8
  34:   fff321          l32r    a2, 0 &lt;esp_wifi_set_csi-0x28&gt; (3001 &lt;esp_wifi_stop+0x2f91&gt;)
  37:   05fa16          beqz    a10, 9a &lt;esp_wifi_set_csi+0x72&gt;
  3a:   fff381          l32r    a8, 8 &lt;esp_wifi_set_csi-0x20&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
  3d:   01d882          addmi   a8, a8, 0x100
  40:   ed0822          <mark>l8ui    a2, a8, 237</mark>  [5]
  43:   0822f6          bgeui   a2, 2, 4f &lt;esp_wifi_set_csi+0x27&gt;
  46:   ef0882          l8ui    a8, a8, 239
  49:   ffee21          l32r    a2, 4 &lt;esp_wifi_set_csi-0x24&gt; (3002 &lt;esp_wifi_stop+0x2f92&gt;)
  4c:   04a816          beqz    a8, 9a &lt;esp_wifi_set_csi+0x72&gt;
  4f:   fff381          l32r    a8, 1c &lt;esp_wifi_set_csi-0xc&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
                        4f: R_XTENSA_ASM_EXPAND <mark>config_get_wifi_csi_enable</mark>  [6]
  52:   0008e0          callx8  a8
  55:   3adc            bnez.n  a10, 6c &lt;esp_wifi_set_csi+0x44&gt;
  57:   1c0c            movi.n  a12, 1
  59:   ffecd1          l32r    a13, c &lt;esp_wifi_set_csi-0x1c&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
  5c:   2b0c            movi.n  a11, 2
  5e:   0cad            mov.n   a10, a12
  60:   fff081          l32r    a8, 20 &lt;esp_wifi_set_csi-0x8&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
                        60: R_XTENSA_ASM_EXPAND wifi_log
  63:   0008e0          callx8  a8
  66:   f27c            <mark>movi.n  a2, -1</mark>  [7]
  68:   000b86          j       9a &lt;esp_wifi_set_csi+0x72&gt;
  6b:   00              .byte 00
  6c:   ffe921          l32r    a2, 10 &lt;esp_wifi_set_csi-0x18&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
  6f:   8a1c            movi.n  a10, 24
  71:   0228            l32i.n  a2, a2, 0
  73:   5e2222          l32i    a2, a2, <mark>0x178</mark>  [8]
  76:   0002e0          callx8  a2
  79:   01a122          movi    a2, <mark>0x101</mark>  [9]
  7c:   aa9c            beqz.n  a10, 9a &lt;esp_wifi_set_csi+0x72&gt;
  7e:   ffe521          l32r    a2, 14 &lt;esp_wifi_set_csi-0x14&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
  81:   016a22          <mark>s32i    a2, a10, 4</mark>  [10]
  84:   222c            movi.n  a2, 34
  86:   004a22          s8i     a2, a10, 0
  89:   084a32          <mark>s8i     a3, a10, 8</mark>  [11]
  8c:   0020c0          memw
  8f:   0020c0          memw
  92:   ffe481          l32r    a8, 24 &lt;esp_wifi_set_csi-0x4&gt; (0 &lt;esp_wifi_set_csi-0x28&gt;)
                        92: R_XTENSA_ASM_EXPAND <mark>ieee80211_ioctl</mark>  [12]
  95:   0008e0          callx8  a8
  98:   0a2d            mov.n   a2, a10
  9a:   f01d            retw.n
</pre>

1. `0x3001` = `ESP_ERR_WIFI_NOT_INIT`.
2. `0x3002` = `ESP_ERR_WIFI_NOT_STARTED`.
3. Funcția care va face lucrul real, pusă în mesaj.
4. Prima verificare: a rulat `esp_wifi_init`?
5. Citește un câmp de stare din `g_ic`. Dacă driverul nu a pornit: `0x3002`.
6. Verifică `.csi_enable` din secțiunea 9.
7. CSI neactivat în `sdkconfig`: `ESP_FAIL` (−1).
8. Alocă un mesaj de 24 de octeți.
9. Fără memorie: `ESP_ERR_NO_MEM`.
10. Scrie în mesaj adresa `wifi_set_csi`.
11. Scrie în mesaj parametrul nostru `en` (`true`).
12. Trimite mesajul. Task-ul Wi-Fi va apela `wifi_set_csi(mesaj)`.

### 16.3 `wifi_set_csi` → `ic_set_csi`

Sursa: `libnet80211.a + libpp.a (objdump)`

<pre>
   0:   00000000
                        0: R_XTENSA_32  ic_set_csi
  --
   4:   004136          entry   a1, 32
   7:   080292          <mark>l8ui    a9, a2, 8</mark>  [1]
   a:   080c            movi.n  a8, 0
   c:   01a0a2          movi    a10, 1
   f:   83a890          <mark>moveqz  a10, a8, a9</mark>  [2]
  12:   fffb81          l32r    a8, 0 &lt;wifi_set_csi-0x4&gt; (0 &lt;wifi_set_csi-0x4&gt;)
                        12: R_XTENSA_ASM_EXPAND <mark>ic_set_csi</mark>  [3]
  15:   0008e0          callx8  a8
  18:   0a2d            mov.n   a2, a10
  1a:   f01d            retw.n
</pre>

1. Citește octetul 8 din mesaj: `en`.
2. Transformă `en` în 0 sau 1.
3. Coboară în `libpp.a`.

### 16.4 `ic_set_csi` → `hal_mac_set_csi`

Sursa: `libpp.a (objdump)`

<pre>
   0:   00000000
                        0: R_XTENSA_32  hal_mac_set_csi
  --
   4:   004136          entry   a1, 32
   7:   74a020          extui   a10, a2, 0, 8
   a:   fffd81          l32r    a8, 0 &lt;ic_set_csi-0x4&gt; (0 &lt;ic_set_csi-0x4&gt;)
                        a: R_XTENSA_ASM_EXPAND  <mark>hal_mac_set_csi</mark>  [1]
   d:   0008e0          callx8  a8
  10:   0a2d            mov.n   a2, a10
  12:   f01d            retw.n
</pre>

1. `hal_` = stratul care atinge hardware-ul direct.

### 16.5 `hal_mac_set_csi` – registrul de control

Sursa: `libpp.a (objdump)`

<pre>
   0:   <mark>3ff7309c</mark>  [1]
   4:   <mark>ff7fffff</mark>  [2]
   8:   00000000
                        8: R_XTENSA_32  config_get_wifi_csi_enable
  --
   c:   004136          entry   a1, 32
   f:   fffe81          l32r    a8, 8 &lt;hal_mac_set_csi-0x4&gt; (0 &lt;hal_mac_set_csi-0xc&gt;)
                        f: R_XTENSA_ASM_EXPAND  <mark>config_get_wifi_csi_enable</mark>  [3]
  12:   0008e0          callx8  a8
  15:   743020          extui   a3, a2, 0, 8
  18:   f27c            movi.n  a2, -1
  1a:   2abc            beqz.n  a10, 50 &lt;hal_mac_set_csi+0x44&gt;
  1c:   fff981          l32r    a8, 0 &lt;hal_mac_set_csi-0xc&gt; (3ff7309c &lt;mac_txrx_init+0x3ff73034&gt;)
  1f:   939c            <mark>beqz.n  a3</mark>, 3c &lt;hal_mac_set_csi+0x30&gt;  [4]
  21:   190c            movi.n  a9, 1
  23:   019990          <mark>slli    a9, a9, 23</mark>  [5]
  26:   0020c0          memw
  29:   0828            <mark>l32i.n  a2, a8, 0</mark>  [6]
  2b:   202290          <mark>or      a2, a2, a9</mark>  [7]
  2e:   0020c0          memw
  31:   0829            <mark>s32i.n  a2, a8, 0</mark>  [8]
  33:   020c            movi.n  a2, 0
  35:   0020c0          memw
  38:   000506          j       50 &lt;hal_mac_set_csi+0x44&gt;
  3b:   00              .byte 00
  3c:   0020c0          memw
  3f:   0898            l32i.n  a9, a8, 0
  41:   fff021          l32r    a2, 4 &lt;hal_mac_set_csi-0x8&gt; (ff7fffff &lt;mac_txrx_init+0xff7fff97&gt;)
  44:   109920          <mark>and     a9, a9, a2</mark>  [9]
  47:   202330          or      a2, a3, a3
  4a:   0020c0          memw
  4d:   006892          s32i    a9, a8, 0
  50:   0020c0          memw
  53:   f01d            retw.n
</pre>

1. Adresa registrului, în zona perifericului Wi-Fi MAC. Nedocumentat public.
2. Masca pentru oprire: toți biții 1, în afară de bitul 23.
3. Încă o verificare a opțiunii din `sdkconfig`.
4. `a3` = `en`. Dacă este 0, sare la ramura de oprire.
5. `a9 = 1 << 23` = `0x00800000`: bitul de control al CSI.
6. Citește registrul.
7. Pune bitul 23 pe 1. Ceilalți biți rămân la fel.
8. Scrie registrul înapoi. **Din acest moment, hardware-ul calculează CSI la fiecare cadru OFDM.**
9. Ramura `false`: șterge bitul 23.

```
esp_wifi_set_csi(true)                 libnet80211.a   (task main)
  └─ ieee80211_ioctl → pp_post ─────►  coada task-ului Wi-Fi
                                       wifi_set_csi(mesaj)        (task Wi-Fi)
                                         └─ ic_set_csi            libpp.a
                                              └─ hal_mac_set_csi  libpp.a
                                                   registrul 0x3FF7309C, bitul 23 = 1
```

După linia 106, `app_main` ajunge la `}` (linia 107) și se termină. Jurnal, linia 29: `main_task: Returned from app_main()`. Restul programului rulează în task-urile `sys_evt`, `tiT`, Wi-Fi și `ping`.

---

## 17. Evenimentul `STA_START` → `on_event` → `esp_wifi_connect()`

`main.c`: liniile 72–75

`esp_wifi_start` (linia 102) face driverul să trimită `WIFI_EVENT_STA_START` în bucla de evenimente. Task-ul `sys_evt` scoate evenimentul din coadă și apelează fiecare funcție înregistrată.

### 17.1 Cum apelează bucla funcția noastră

Sursa: `IDF/esp_event/esp_event.c`

<pre>
117 | static void <mark>handler_execute</mark>(esp_event_loop_instance_t* loop, esp_event_handler_node_t *handler, esp_event_post_instance_t post)  [1]
    | ...
137 |     <mark>(*(handler-&gt;handler_ctx-&gt;handler))</mark>(handler-&gt;<mark>handler_ctx-&gt;arg, post.base, post.id, data_ptr</mark>);  [2] [3]
138 | #else
139 |     (*(handler-&gt;handler_ctx-&gt;handler))(handler-&gt;handler_ctx-&gt;arg, post.base, post.id, post.data);
140 | #endif
</pre>

1. Rulează în task-ul `sys_evt`, pentru fiecare funcție din listă.
2. Apel prin pointer: aceasta este adresa lui `on_event`.
3. Cei 4 parametri ai lui `on_event`: `arg` (`NULL`), `base`, `id`, `data`.

### 17.2 `on_event`, prima ramură

Sursa: `pas_cu_pas/main/main.c`

<pre>
72 | // driverul ne anunta aici: &quot;am pornit&quot;, &quot;m-am deconectat&quot;, &quot;am primit IP&quot;
73 | static void on_event(<mark>void *arg</mark>, <mark>esp_event_base_t base</mark>, <mark>int32_t id</mark>, <mark>void *data</mark>) {  [1] [2] [3] [4]
74 |     if (<mark>base == WIFI_EVENT</mark> &amp;&amp; (<mark>id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED</mark>)) {  [5] [6]
75 |         <mark>esp_wifi_connect();</mark>  [7]
</pre>

1. `arg` = `NULL` de la înregistrare. Nu îl folosim.
2. Familia: pointer la `"WIFI_EVENT"` sau la `"IP_EVENT"`.
3. Numărul evenimentului din familie.
4. Datele evenimentului. Tipul depinde de eveniment.
5. Comparăm adrese (secțiunea 10).
6. Radioul a pornit sau am pierdut rețeaua: în ambele cazuri ne conectăm.
7. Cere conectarea. Fără `ESP_ERROR_CHECK`: o eroare aici nu trebuie să repornească placa.

### 17.3 Numerele evenimentelor Wi-Fi

Sursa: `IDF/esp_wifi/include/esp_wifi_types.h`

<pre>
870 | typedef enum {
871 |     WIFI_EVENT_WIFI_READY <mark>= 0</mark>,           /**&lt; WiFi ready */  [1]
872 |     WIFI_EVENT_SCAN_DONE,                /**&lt; Finished scanning AP */
873 |     <mark>WIFI_EVENT_STA_START</mark>,                /**&lt; Station start */  [2]
874 |     WIFI_EVENT_STA_STOP,                 /**&lt; Station stop */
875 |     <mark>WIFI_EVENT_STA_CONNECTED</mark>,            /**&lt; Station connected to AP */  [3]
876 |     <mark>WIFI_EVENT_STA_DISCONNECTED</mark>,         /**&lt; Station disconnected from AP */  [4]
877 |     WIFI_EVENT_STA_AUTHMODE_CHANGE,      /**&lt; the auth mode of AP connected by device&#x27;s station changed */
</pre>

1. Numerotarea începe de la 0.
2. 2 = stația a pornit.
3. 4 = conectat. Nu îl folosim.
4. 5 = rețea pierdută.

### 17.4 `esp_wifi_connect` – header

Sursa: `IDF/esp_wifi/include/esp_wifi.h`

<pre>
418 |   *
    | ...
424 |   * @attention 4. This API attempts to connect to an Access Point (AP) <mark>only once</mark>. To enable reconnection in case of a connection failure, please use  [1]
425 |   *               the &#x27;failure_retry_cnt&#x27; feature in the &#x27;wifi_sta_config_t&#x27;. Users are suggested to <mark>implement reconnection logic in their application</mark>  [2]
426 |   *               for scenarios where the specified AP does not exist, or reconnection is desired after the device has received a disconnect event.
    | ...
436 | esp_err_t esp_wifi_connect(void);
</pre>

1. O singură încercare. De aceea reacționăm și la `STA_DISCONNECTED`.
2. Reconectarea este sarcina aplicației: ramura din linia 74.

### 17.5 Conectarea în jurnal

Sursa: `pas_cu_pas/output/07_main_nou.log`

<pre>
31 | I (839) wifi:state: <mark>init -&gt; auth</mark> (b0)  [1]
32 | I (849) wifi:state: <mark>auth -&gt; assoc</mark> (0)  [2]
33 | I (899) wifi:state: <mark>assoc -&gt; run</mark> (10)  [3]
34 | I (929) wifi:connected with zaqmlp, aid = 8, <mark>channel 11</mark>, BW20, <mark>bssid = f6:2b:8c:e2:21:ac</mark>  [4] [5]
35 | I (929) wifi:security: WPA2-PSK, <mark>phy: bgn</mark>, rssi: -48  [6]
36 | I (929) wifi:<mark>pm start, type: 1</mark>  [7]
</pre>

1. Autentificare 802.11.
2. Asociere: placa primește un număr (`aid`).
3. Cheile WPA2 sunt gata. Conexiunea merge.
4. Placa a găsit hotspot-ul pe canalul 11.
5. Adresa MAC a hotspot-ului. O vom vedea ca sursă a CSI.
6. Hotspot-ul acceptă 802.11b, g și n.
7. Economia de energie a pornit. Ping-urile țin totuși placa trează.

---

## 18. Evenimentul `IP_EVENT_STA_GOT_IP` → `on_event`

`main.c`: liniile 76–79

După conectare, clientul DHCP (în task-ul `tiT`) cere o adresă de la telefon. Când o primește, stiva IP trimite `IP_EVENT_STA_GOT_IP`.

### 18.1 Cine trimite evenimentul

Sursa: `IDF/esp_netif/lwip/esp_netif_lwip.c`

<pre>
1270 | static void <mark>esp_netif_internal_dhcpc_cb</mark>(struct netif *netif)  [1]
     | ...
1290 |             <mark>ip_event_got_ip_t evt</mark> = {  [2]
1291 |                     .esp_netif = esp_netif,
1292 |                     .ip_changed = false,
1293 |             };
     | ...
1297 |             <mark>ip4_addr_set(&amp;ip_info-&gt;ip</mark>, ip_2_ip4(&amp;netif-&gt;ip_addr));  [3]
1298 |             ip4_addr_set(&amp;ip_info-&gt;netmask, ip_2_ip4(&amp;netif-&gt;netmask));
1299 |             <mark>ip4_addr_set(&amp;ip_info-&gt;gw</mark>, ip_2_ip4(&amp;netif-&gt;gw));  [4]
     | ...
1305 | 
1306 |             <mark>memcpy(&amp;evt.ip_info, ip_info</mark>, sizeof(esp_netif_ip_info_t));  [5]
1307 |             memcpy(ip_info_old, ip_info, sizeof(esp_netif_ip_info_t));
1308 |             ESP_LOGD(TAG, &quot;if%p ip changed=%d&quot;, esp_netif, evt.ip_changed);
1309 |             ret = <mark>esp_event_post(IP_EVENT, evt_id, &amp;evt, sizeof(evt), 0)</mark>;  [6]
</pre>

1. Funcția apelată când DHCP termină.
2. Structura pe care o primim în `data`.
3. Copiază adresa primită de la DHCP.
4. Copiază gateway-ul: telefonul.
5. Pune adresele în eveniment.
6. Trimite evenimentul. Bucla copiază `evt`, deci `data` din `on_event` rămâne valid în timpul apelului.

### 18.2 Tipurile primite

Sursa: `IDF/esp_netif/include/esp_netif_types.h`

<pre>
 95 | typedef enum {
 96 |     <mark>IP_EVENT_STA_GOT_IP</mark>,               /*!&lt; station got IP from connected AP */  [1]
    | ...
111 | typedef struct {
112 |     esp_<mark>ip</mark>4_addr_t ip;      /**&lt; Interface IPV4 address */  [2]
113 |     esp_ip4_addr_t netmask; /**&lt; Interface IPV4 netmask */
114 |     esp_ip4_addr_t <mark>gw</mark>;      /**&lt; Interface IPV4 gateway address */  [3]
115 | } esp_netif_ip_info_t;
    | ...
128 | typedef struct {
129 |     esp_netif_t *esp_netif;          /*!&lt; Pointer to corresponding esp-netif object */
130 |     esp_netif_<mark>ip_info</mark>_t ip_info;     /*!&lt; IP address, netmask, gatway IP address */  [4]
131 |     bool ip_changed;                 /*!&lt; Whether the assigned IP has changed or not */
132 | } ip_event_got_ip_t;
</pre>

1. Valoarea 0 în familia `IP_EVENT`. De aceea verificăm și `base`: `WIFI_EVENT_WIFI_READY` are tot 0.
2. Adresa plăcii.
3. Gateway-ul: ținta ping-ului.
4. Cele 3 adrese, într-un câmp.

### 18.3 O adresă IPv4 = un număr pe 32 de biți

Sursa: `IDF/esp_netif/include/esp_netif_ip_addr.h`

<pre>
111 | struct esp_ip4_addr {
112 |     <mark>uint32_t addr</mark>;  /*!&lt; IPv4 address */  [1]
113 | };
114 | 
115 | typedef struct esp_ip4_addr esp_ip4_addr_t;
</pre>

1. Cei 4 octeți ai adresei, într-un singur `uint32_t`.

### 18.4 `on_event`, a doua ramură

Sursa: `pas_cu_pas/main/main.c`

<pre>
76 |     } else if (<mark>base == IP_EVENT &amp;&amp; id == IP_EVENT_STA_GOT_IP</mark>) {  [1]
77 |         <mark>ip_event_got_ip_t *got_ip = data</mark>;  [2]
78 |         ESP_LOGI(TAG, &quot;Conectat. IP &quot; <mark>IPSTR</mark> &quot;, gateway &quot; IPSTR,  [3]
79 |                  <mark>IP2STR(&amp;got_ip-&gt;ip_info.ip)</mark>, IP2STR(&amp;got_ip-&gt;ip_info.gw));  [4]
80 |         <mark>start_ping(got_ip-&gt;ip_info.gw)</mark>;  [5]
</pre>

1. Familia IP și evenimentul „am primit IP”.
2. `data` este `void *`. Îl citim ca `ip_event_got_ip_t *`.
3. Macro: șablonul `"%d.%d.%d.%d"`.
4. Macro: cele 4 numere ale adresei, ca 4 argumente.
5. Pornim ping-ul către telefon. Abia acum avem adresa lui.

### 18.5 `IPSTR` și `IP2STR`

Sursa: `IDF/esp_netif/include/esp_netif_ip_addr.h`

<pre>
42 | #define IPSTR <mark>&quot;%d.%d.%d.%d&quot;</mark>  [1]
   | ...
55 | #define IP2STR(ipaddr) <mark>esp_ip4_addr1_16(ipaddr)</mark>, \  [2]
56 |     esp_ip4_addr2_16(ipaddr), \
57 |     esp_ip4_addr3_16(ipaddr), \
58 |     esp_ip4_addr4_16(ipaddr)
</pre>

1. Șablonul unei adrese IPv4.
2. Primul octet. Următoarele 3 linii dau ceilalți octeți.

### 18.6 În jurnal

Sursa: `pas_cu_pas/output/07_main_nou.log`

<pre>
41 | I (1939) esp_netif_handlers: <mark>sta ip: 10.136.19.115</mark>, mask: 255.255.255.0, gw: 10.136.19.245  [1]
42 | I (1939) CSI: Conectat. IP 10.136.19.115, <mark>gateway 10.136.19.245</mark>  [2]
</pre>

1. Linia scrisă de funcțiile ESP-IDF înregistrate în secțiunea 8.
2. Linia noastră. Gateway-ul este telefonul.

---

## 19. `start_ping()` – ping la telefon la fiecare 20 ms

`main.c`: liniile 60–70

### 19.1 Codul nostru

Sursa: `pas_cu_pas/main/main.c`

<pre>
60 | // ping la telefon (gateway) la fiecare 20 ms: fiecare raspuns aduce un CSI
61 | static void start_ping(<mark>esp_ip4_addr_t gateway</mark>) {  [1]
62 |     esp_ping_config_t ping = <mark>ESP_PING_DEFAULT_CONFIG()</mark>;  [2]
63 |     ping.target_addr.type = <mark>IPADDR_TYPE_V4</mark>;  [3]
64 |     ping.target_addr.u_addr.ip4.addr = <mark>gateway.addr</mark>;  [4]
65 |     ping.count = <mark>ESP_PING_COUNT_INFINITE</mark>;  [5]
66 |     ping.interval_ms = <mark>20</mark>;  [6]
67 |     <mark>esp_ping_handle_t session</mark>;  [7]
68 |     ESP_ERROR_CHECK(esp_ping_new_session(<mark>&amp;ping, NULL, &amp;session</mark>));  [8]
69 |     ESP_ERROR_CHECK(<mark>esp_ping_start(session)</mark>);  [9]
70 | }
</pre>

1. Parametrul: o copie a adresei gateway-ului.
2. Setările implicite (19.2). Schimbăm doar 4 câmpuri.
3. `ip_addr_t` poate fi IPv4 sau IPv6. Alegem IPv4.
4. Copiem cei 32 de biți ai adresei.
5. 0 = fără sfârșit.
6. Un ping la 20 ms = 50 pe secundă.
7. Un pointer la sesiune, completat de funcția următoare.
8. Setările, fără callback-uri (`NULL`), și unde scrie sesiunea.
9. Pornește ping-urile și se întoarce imediat.

### 19.2 `ESP_PING_DEFAULT_CONFIG` și câmpurile

Sursa: `IDF/lwip/include/apps/ping/ping_sock.h`

<pre>
58 |     uint32_t <mark>count</mark>;           /*!&lt; A &quot;ping&quot; session contains count procedures */  [1]
59 |     uint32_t <mark>interval_ms</mark>;     /*!&lt; Milliseconds between each ping procedure */  [2]
   | ...
64 |     ip_addr_t <mark>target_addr</mark>;    /*!&lt; Target IP address, either IPv4 or IPv6 */  [3]
   | ...
66 |     uint32_t <mark>task_prio</mark>;       /*!&lt; Priority of internal ping task */  [4]
   | ...
74 | #define ESP_PING_DEFAULT_CONFIG()        \
75 |     {                                    \
76 |         <mark>.count = 5</mark>,                      \  [5]
77 |         <mark>.interval_ms = 1000</mark>,             \  [6]
78 |         <mark>.timeout_ms = 1000</mark>,              \  [7]
79 |         <mark>.data_size = 64</mark>,                 \  [8]
80 |         .tos = 0,                        \
81 |         .ttl = IP_DEFAULT_TTL,           \
82 |         .target_addr = *(IP_ANY_TYPE),   \
83 |         .task_stack_size = ESP_TASK_PING_STACK,         \
84 |         <mark>.task_prio = 2</mark>,                  \  [9]
85 |         .interface = 0,\
86 |     }
87 | 
88 | #define ESP_PING_COUNT_INFINITE <mark>(0)</mark> /*!&lt; Set ping count to zero will ping target infinitely */  [10]
</pre>

1. Câte ping-uri are o sesiune.
2. Pauza dintre două ping-uri.
3. Ținta: IPv4 sau IPv6.
4. Prioritatea task-ului `ping`.
5. Implicit: 5 ping-uri. Noi: infinit.
6. Implicit: unul pe secundă. Noi: 20 ms.
7. Cât așteaptă un răspuns. Nu l-am schimbat.
8. 64 de octeți de date în fiecare ping.
9. Prioritate mică (Wi-Fi are 23).
10. Valoarea specială 0 = fără sfârșit.

### 19.3 `esp_ping_new_session` – implementare

Sursa: `IDF/lwip/apps/ping/ping_sock.c`

<pre>
238 | esp_err_t esp_ping_new_session(const esp_ping_config_t *config, const esp_ping_callbacks_t *cbs, esp_ping_handle_t *hdl_out)
239 | {
240 |     esp_err_t ret = ESP_FAIL;
241 |     esp_ping_t *ep = NULL;
242 |     ESP_GOTO_ON_FALSE(config, ESP_ERR_INVALID_ARG, err, TAG, &quot;ping config can&#x27;t be null&quot;);
243 |     ESP_GOTO_ON_FALSE(hdl_out, ESP_ERR_INVALID_ARG, err, TAG, &quot;ping handle can&#x27;t be null&quot;);
244 | 
245 |     ep = <mark>mem_calloc(1, sizeof(esp_ping_t))</mark>;  [1]
246 |     ESP_GOTO_ON_FALSE(ep, ESP_ERR_NO_MEM, err, TAG, &quot;no memory for esp_ping object&quot;);
247 | 
248 |     /* set INIT flag, so that ping task won&#x27;t exit (must set before create ping task) */
249 |     ep-&gt;flags |= PING_FLAGS_INIT;
250 | 
251 |     /* create ping thread */
252 |     BaseType_t xReturned = <mark>xTaskCreate(esp_ping_thread, &quot;ping&quot;</mark>, config-&gt;task_stack_size, ep,  [2]
253 |                                        config-&gt;task_prio, &amp;ep-&gt;ping_task_hdl);
254 |     ESP_GOTO_ON_FALSE(xReturned == pdTRUE, ESP_ERR_NO_MEM, err, TAG, &quot;create ping task failed&quot;);
255 | 
256 |     /* callback functions */
257 |     <mark>if (cbs)</mark> {  [3]
258 |         ep-&gt;cb_args = cbs-&gt;cb_args;
259 |         ep-&gt;on_ping_end = cbs-&gt;on_ping_end;
260 |         ep-&gt;on_ping_timeout = cbs-&gt;on_ping_timeout;
261 |         ep-&gt;on_ping_success = cbs-&gt;on_ping_success;
262 |     }
263 |     /* set parameters for ping */
264 |     ep-&gt;recv_addr = config-&gt;target_addr;
265 |     <mark>ep-&gt;count = config-&gt;count</mark>;  [4]
266 |     ep-&gt;interval_ms = config-&gt;interval_ms;
267 |     ep-&gt;icmp_pkt_size = sizeof(struct icmp_echo_hdr) + config-&gt;data_size;
268 |     ep-&gt;packet_hdr = mem_calloc(1, ep-&gt;icmp_pkt_size);
    | ...
285 |     ) {
286 |         ep-&gt;sock = socket(AF_INET, <mark>SOCK_RAW, IP_PROTO_ICMP</mark>);  [5]
287 |     }
    | ...
306 |     struct timeval timeout;
307 |     timeout.tv_sec = config-&gt;timeout_ms / 1000;
308 |     timeout.tv_usec = (config-&gt;timeout_ms % 1000) * 1000;
309 |     /* set receive timeout */
310 |     setsockopt(ep-&gt;sock, SOL_SOCKET, <mark>SO_RCVTIMEO</mark>, &amp;timeout, sizeof(timeout));  [6]
</pre>

1. Alocă structura sesiunii. `esp_ping_handle_t` este un pointer la ea.
2. Creează task-ul `ping`. El trimite și primește.
3. Noi am dat `NULL`: task-ul nu apelează nicio funcție a noastră.
4. Copiază setările noastre în sesiune.
5. Socket „brut” ICMP: ping-ul nu folosește UDP sau TCP.
6. Așteptarea unui răspuns are limită: `timeout_ms`.

### 19.4 `esp_ping_start` – implementare

Sursa: `IDF/lwip/apps/ping/ping_sock.c`

<pre>
366 | esp_err_t esp_ping_start(esp_ping_handle_t hdl)
367 | {
368 |     esp_err_t ret = ESP_OK;
369 |     esp_ping_t *ep = (esp_ping_t *)hdl;
370 |     ESP_GOTO_ON_FALSE(ep, ESP_ERR_INVALID_ARG, err, TAG, &quot;ping handle can&#x27;t be null&quot;);
371 |     <mark>ep-&gt;flags |= PING_FLAGS_START</mark>;  [1]
372 |     <mark>xTaskNotifyGive(ep-&gt;ping_task_hdl)</mark>;  [2]
373 |     return ESP_OK;
374 | err:
375 |     return ret;
376 | }
</pre>

1. Pune steagul „pornit”.
2. Trezește task-ul `ping`. Apoi funcția se întoarce imediat.

### 19.5 Bucla task-ului `ping`

Sursa: `IDF/lwip/apps/ping/ping_sock.c`

<pre>
186 |     while (1) {
187 |         /* wait for ping start signal */
188 |         if (<mark>ulTaskNotifyTake</mark>(pdTRUE, pdMS_TO_TICKS(PING_CHECK_START_TIMEOUT_MS))) {  [1]
189 |             /* initialize runtime statistics */
190 |             ep-&gt;packet_hdr-&gt;seqno = 0;
191 |             ep-&gt;transmitted = 0;
192 |             ep-&gt;received = 0;
193 |             ep-&gt;total_time_ms = 0;
194 | 
195 |             last_wake = xTaskGetTickCount();
196 |             while ((ep-&gt;flags &amp; PING_FLAGS_START) &amp;&amp; (<mark>(ep-&gt;count == 0)</mark> || (ep-&gt;packet_hdr-&gt;seqno &lt; ep-&gt;count))) {  [2]
197 |                 <mark>esp_ping_send(ep)</mark>;  [3]
198 |                 gettimeofday(&amp;start_time, NULL);
199 |                 recv_ret = <mark>esp_ping_receive(ep)</mark>;  [4]
200 |                 gettimeofday(&amp;end_time, NULL);
201 |                 ep-&gt;elapsed_time_ms = PING_TIME_DIFF_MS(end_time, start_time);
202 |                 ep-&gt;total_time_ms += ep-&gt;elapsed_time_ms;
203 |                 if (recv_ret &gt;= 0) {
204 |                     <mark>if (ep-&gt;on_ping_success)</mark> {  [5]
205 |                         ep-&gt;on_ping_success((esp_ping_handle_t)ep, ep-&gt;cb_args);
206 |                     }
207 |                 } else {
208 |                     if (ep-&gt;on_ping_timeout) {
209 |                         ep-&gt;on_ping_timeout((esp_ping_handle_t)ep, ep-&gt;cb_args);
210 |                     }
211 |                 }
212 |                 if (pdMS_TO_TICKS(ep-&gt;interval_ms)) {
213 |                     <mark>vTaskDelayUntil(&amp;last_wake, pdMS_TO_TICKS(ep-&gt;interval_ms))</mark>; // to get a more accurate delay  [6]
214 |                 }
215 |             }
</pre>

1. Task-ul doarme aici până la `esp_ping_start`.
2. `count == 0`: bucla nu se termină niciodată.
3. Trimite cererea ICMP echo către telefon.
4. Așteaptă răspunsul. **Răspunsul vine ca un cadru OFDM de la hotspot → hardware-ul calculează un CSI.**
5. Nu avem callback-uri: nu se întâmplă nimic aici.
6. Așteaptă până la următorul ping. `pdMS_TO_TICKS(20)` = 2 tick-uri (100 Hz).

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

---

## 20. Un răspuns ajunge: driverul apelează `on_csi`

Fiecare cadru OFDM primit are la început un „model de test” cunoscut: LLTF. Hardware-ul compară ce a primit cu ce trebuia să primească. Rezultatul, pe fiecare sub-frecvență, este CSI. Codul din `libpp.a` copiază rezultatul și apelează `on_csi`.

### 20.1 `wdev_csi_rx_process` – de la hardware la `on_csi`

Sursa: `libpp.a (objdump)`

Offset-urile scrise (28, 34, 40, 44, 48) corespund exact câmpurilor din `wifi_csi_info_t` (20.2). Aceasta confirmă interpretarea.

<pre>
        ...
                        0: R_XTENSA_32  <mark>g_wdev_csi_rx</mark>  [1]
                        4: R_XTENSA_32  g_osi_funcs_p
                        8: R_XTENSA_32  wDevCtrl
                        c: R_XTENSA_32  <mark>g_wdev_csi_rx_ctx</mark>  [2]
                        10: R_XTENSA_32 memcpy
                        14: R_XTENSA_32 memset
                        18: R_XTENSA_32 memcpy
                        1c: R_XTENSA_32 memcpy
                        20: R_XTENSA_32 wDev_GetNoiseFloor
...
  38:   0688            <mark>l32i.n  a8, a6, 0</mark>  [3]
  3a:   0f6816          <mark>beqz    a8</mark>, 134 &lt;wdev_csi_rx_process+0x110&gt;  [4]
  3d:   0a4c            <mark>movi.n  a10, 64</mark>  [5]
  3f:   fff161          l32r    a6, 4 &lt;wdev_csi_rx_process-0x20&gt; (0 &lt;wdev_csi_rx_process-0x24&gt;)
  42:   0688            l32i.n  a8, a6, 0
  44:   5b2882          l32i    a8, a8, 0x16c
  47:   0020c0          memw
  4a:   0008e0          callx8  a8
...
  54:   1ccaa2          addi    a10, a10, <mark>28</mark>  [6]
...
  5c:   b5ab            addi.n  a11, <mark>a5, 10</mark>  [7]
...
  72:   b54b            addi.n  a11, <mark>a5, 4</mark>  [8]
  74:   22c6a2          addi    a10, <mark>a6, 34</mark>  [9]
...
  82:   cc1c            <mark>movi.n  a12, 28</mark>  [10]
...
                        a8: R_XTENSA_ASM_EXPAND <mark>wDev_GetNoiseFloor</mark>  [11]
  ab:   0008e0          callx8  a8
  ae:   190c            movi.n  a9, 1
  b0:   0846a2          <mark>s8i     a10, a6, 8</mark>  [12]
...
  bd:   b629            s32i.n  a2, <mark>a6, 44</mark>  [13]
  bf:   0128            l32i.n  a2, a1, 0
  c1:   185622          s16i    a2, <mark>a6, 48</mark>  [14]
...
  cc:   2846b2          s8i     a11, <mark>a6, 40</mark>  [15]
...
 114:   06bd            mov.n   a11, a6
 116:   ffba31          l32r    a3, 0 &lt;wdev_csi_rx_process-0x24&gt; (0 &lt;wdev_csi_rx_process-0x24&gt;)
 119:   0328            <mark>l32i.n  a2, a3, 0</mark>  [16]
 11b:   ffbc31          l32r    a3, c &lt;wdev_csi_rx_process-0x18&gt; (0 &lt;wdev_csi_rx_process-0x24&gt;)
 11e:   03a8            <mark>l32i.n  a10, a3, 0</mark>  [17]
 120:   0020c0          memw
 123:   0002e0          <mark>callx8  a2</mark>  [18]
 126:   06ad            mov.n   a10, a6
 128:   ffb731          l32r    a3, 4 &lt;wdev_csi_rx_process-0x20&gt; (0 &lt;wdev_csi_rx_process-0x24&gt;)
 12b:   002322          l32i    a2, a3, 0
 12e:   2c2222          l32i    a2, a2, <mark>176</mark>  [19]
 131:   0002e0          <mark>callx8  a2</mark>  [20]
 134:   f01d            retw.n

</pre>

1. Adresa lui `on_csi`, salvată în secțiunea 15.
2. `ctx`, salvat în secțiunea 15.
3. Citește `g_wdev_csi_rx`.
4. Nicio funcție înregistrată? Atunci iese imediat.
5. Alocă 64 de octeți pentru `wifi_csi_info_t`.
6. `info->mac` este la octetul 28, după `rx_ctrl`.
7. Copiază 6 octeți din antetul 802.11, de la poziția 10: adresa sursei.
8. De la poziția 4: adresa destinației.
9. ... în `info->dmac` (octetul 34).
10. Copiază 28 de octeți: tot `rx_ctrl` (rssi, sig_mode, canal...).
11. Citește zgomotul de fond al radioului.
12. Îl scrie în `rx_ctrl.noise_floor`.
13. `info->buf` (octetul 44): adresa datelor CSI.
14. `info->len` (octetul 48).
15. `info->first_word_invalid` (octetul 40).
16. `a2` = `g_wdev_csi_rx` = `on_csi`.
17. `a10` = primul argument = `ctx` (`NULL`). `a11` = `info`.
18. **Aici rulează `on_csi(ctx, info)`, în task-ul Wi-Fi.**
19. Funcția de eliberare din `g_osi_funcs_p`.
20. Eliberează `info`. După `return` din `on_csi`, `info` nu mai există.

### 20.2 Structura primită: `wifi_csi_info_t`

Sursa: `IDF/esp_wifi/include/esp_wifi_types.h`

<pre>
589 | typedef struct {
590 |     <mark>wifi_pkt_rx_ctrl_t rx_ctrl</mark>;/**&lt; received packet radio metadata header of the CSI data */  [1]
591 |     uint8_t <mark>mac[6]</mark>;            /**&lt; source MAC address of the CSI data */  [2]
592 |     uint8_t dmac[6];           /**&lt; destination MAC address of the CSI data */
593 |     bool <mark>first_word_invalid</mark>;   /**&lt; first four bytes of the CSI data is invalid or not, true indicates the first four bytes is invalid due to hardware limition */  [3]
594 |     <mark>int8_t *buf</mark>;               /**&lt; valid buffer of CSI data */  [4]
595 |     <mark>uint16_t len</mark>;              /**&lt; valid length of CSI data */  [5]
596 |     uint8_t *hdr;              /**&lt; header of the wifi packet */
597 |     uint8_t *payload;          /**&lt; payload of the wifi packet */
598 |     uint16_t payload_len;      /**&lt; payload len of the wifi packet */
599 |     uint16_t rx_seq;           /**&lt; rx sequence number of the wifi packet */
600 | } wifi_csi_info_t;
</pre>

1. Datele radio ale cadrului (20.3). Primii 28 de octeți.
2. Cine a trimis cadrul: hotspot-ul (`f6:2b:8c:e2:21:ac`).
3. Primii 4 octeți din `buf` pot fi invalizi (defect hardware).
4. Octeții CSI, cu semn: Q, I, Q, I, ...
5. Numărul de octeți din `buf`: 128 (doar LLTF), 256 sau 384.

### 20.3 `rx_ctrl.rssi`

Sursa: `IDF/esp_wifi/include/esp_wifi_types.h`

<pre>
463 | /** @brief Received packet radio metadata header, this is the common header at the beginning of all promiscuous mode RX callback buffers */
464 | typedef struct {
465 |     <mark>signed rssi:8</mark>;                /**&lt; Received Signal Strength Indicator(RSSI) of packet. unit: dBm */  [1]
466 |     unsigned rate:5;              /**&lt; PHY rate encoding of the packet. Only valid for non HT(11bg) packet */
467 |     unsigned :1;                  /**&lt; reserved */
468 |     unsigned <mark>sig_mode</mark>:2;          /**&lt; Protocol of the reveived packet, 0: non HT(11bg) packet; 1: HT(11n) packet; 3: VHT(11ac) packet */  [2]
</pre>

1. Câmp de 8 biți cu semn: puterea cadrului, în dBm (de exemplu −55).
2. 0 = 802.11b/g, 1 = 802.11n (HT). De aici depinde `len`.

### 20.4 Ghidul oficial: `on_csi` rulează în task-ul Wi-Fi

Sursa: `~/esp/esp-idf/docs/en/api-guides/wifi.rst`

<pre>
2273 |     The CSI receiving callback function <mark>runs from Wi-Fi task</mark>. So, <mark>do not do lengthy operations</mark> in the callback function. Instead, post necessary data to a queue and handle it from a lower priority task. Because station does not receive any packet when it is disconnected and only receives packets from AP when it is connected, it is suggested to enable sniffer mode to receive more CSI data by calling :cpp:func:`esp_wifi_set_promiscuous()`.  [1] [2]
</pre>

1. Confirmă 20.1.
2. `on_csi` trebuie să fie scurtă. Altfel, task-ul Wi-Fi pierde cadre.

---

## 21. `on_csi` linie cu linie – amplitudinea

`main.c`: liniile 20–41

### 21.1 Formatul lui `info->buf` (ghidul oficial)

Sursa: `~/esp/esp-idf/docs/en/api-guides/wifi.rst`

<pre>
2214 |     Channel state information (CSI) refers to the channel information of a Wi-Fi connection. In {IDF_TARGET_NAME}, this information consists of channel frequency responses of sub-carriers and is estimated when packets are received from the transmitter. Each channel frequency response of sub-carrier is recorded by two bytes of signed characters. <mark>The first one is imaginary part and the second one is real part</mark>. There are up to three fields of channel frequency responses according to the type of received packet. They are legacy long training field (LLTF), high throughput LTF (HT-LTF), and space time block code HT-LTF (STBC-HT-LTF). For different types of packets which are received on channels with different state, the sub-carrier index and total bytes of signed characters of CSI are shown in the following table.  [1]
     | ...
2225 |     | sub-carrier | LLTF               | <mark>0~31, -32~-1</mark>| 0~31, -32~-1| 0~31, -32~-1|   0~63   |   0~63   | 0~63 |     0~63    |     0~63    |  -64~-1  |  -64~-1  | -64~-1 |    -64~-1   |    -64~-1   |  [2]
     | ...
2241 |         - The CSI data corresponding to each Long Training Field (LTF) type is stored in a buffer starting from the buf field. Each item is stored as two bytes: imaginary part followed by real part. The order of each item is the same as the sub-carrier in the table. <mark>The order of LTF is: LLTF, HT-LTF, STBC-HT-LTF</mark>. However, all 3 LTFs may not be present, depending on the channel and packet information (see above).  [3]
2242 |         - If first_word_invalid field of :cpp:type:`wifi_csi_info_t` is true, it means that the <mark>first four bytes of CSI data is invalid</mark> due to a hardware limitation in {IDF_TARGET_NAME}.  [4]
</pre>

1. Fiecare sub-frecvență: 2 octeți, întâi Q (imaginar), apoi I (real).
2. Ordinea intrărilor LLTF la 20 MHz: 0…31, apoi −32…−1. De aici `64 + k` pentru k negativ.
3. LLTF este mereu primul. Primii 128 de octeți sunt LLTF, oricare ar fi `len`.
4. Primii 4 octeți = intrările 0 și +1. De aceea le sărim.

### 21.2 `on_csi`: verificarea și suma pe sub-frecvențe

Sursa: `pas_cu_pas/main/main.c`

<pre>
33 | // driverul Wi-Fi apeleaza aceasta functie la fiecare CSI masurat
34 | static void on_csi(<mark>void *ctx</mark>, <mark>wifi_csi_info_t *info</mark>) {  [1] [2]
35 |     if (<mark>info-&gt;len &lt; 128</mark>) return;        // avem nevoie de tot blocul LLTF  [3]
36 |     for (int <mark>k = -26; k &lt;= 26</mark>; k++) {  [4]
37 |         if (<mark>k == 0</mark> || <mark>k == 1</mark>) continue; // 0 = fara semnal, +1 = poate fi invalid  [5] [6]
38 |         <mark>amplitude_total[k + 26]</mark> += <mark>amplitude(info-&gt;buf, k)</mark>;  [7] [8]
39 |     }
40 |     <mark>packets++</mark>;  [9]
41 |     rssi_total += <mark>info-&gt;rx_ctrl.rssi</mark>;  [10]
</pre>

1. `ctx` = `NULL`. Este cerut de forma `wifi_csi_cb_t`.
2. Măsurătoarea. Există doar până la `return`.
3. Avem nevoie de tot blocul LLTF: 64 de intrări × 2 octeți. Altfel ignorăm cadrul.
4. Sub-frecvențele active LLTF: −26 … +26 (53 de valori).
5. k = 0 = centrul (DC): fără semnal.
6. k = +1 = în primii 4 octeți, poate fi invalid. Rămân 51 de sub-frecvențe.
7. Poziția în vectorul nostru: k = −26 → 0, k = +26 → 52.
8. Amplitudinea sub-frecvenței k în acest cadru (21.3).
9. Încă un CSI în secunda curentă.
10. Puterea cadrului (20.3), adunată pentru medie.

### 21.3 `amplitude()`: din 2 octeți în amplitudine

Sursa: `pas_cu_pas/main/main.c`

<pre>
20 | // amplitudinea sub-frecventei k (-26..26): 2 octeti, intai Q, apoi I
21 | static float amplitude(<mark>const int8_t *csi</mark>, int k) {  [1]
22 |     int index = <mark>k &gt;= 0 ? k : 64 + k</mark>;  [2]
23 |     int q = <mark>csi[2 * index]</mark>;  [3]
24 |     int i = <mark>csi[2 * index + 1]</mark>;  [4]
25 |     return <mark>sqrtf(i * i + q * q)</mark>;  [5]
26 | }
</pre>

1. `info->buf`. `const` = funcția doar citește.
2. Intrarea din `buf`. Exemplu: k = −20 → 44. k = +7 → 7.
3. Octetul par al intrării = Q. Pentru k = −20: `buf[88]`.
4. Octetul impar = I. Pentru k = −20: `buf[89]`.
5. A = √(I² + Q²): lungimea săgeții (I, Q). `i * i` se calculează în `int`, apoi `sqrtf` în `float`.

**Exemplu numeric:** dacă `buf[88] = 12` (Q) și `buf[89] = −16` (I), atunci A = √(256 + 144) = √400 = 20.

`buf` are tipul `int8_t`: fiecare valoare este între −128 și +127. Deci A este cel mult √(2 × 128²) ≈ 181.

---

## 22. O dată pe secundă: mediile și cele 3 linii din jurnal

`main.c`: liniile 28–31, 43–57

### 22.1 Ceasul și testul „a trecut o secundă?”

Sursa: `pas_cu_pas/main/main.c`

<pre>
43 |     int64_t now = <mark>esp_timer_get_time()</mark>;  [1]
44 |     if (<mark>now - second_start_us &gt;= 1000000</mark>) {  [2]
</pre>

1. Microsecunde de la pornire (22.2).
2. Au trecut 1 000 000 µs = 1 s? La primul CSI, `second_start_us` este 0, deci prima linie are un singur cadru.

### 22.2 `esp_timer_get_time` – header

Sursa: `IDF/esp_timer/include/esp_timer.h`

<pre>
215 | /**
216 |  * @brief Get time in <mark>microseconds since boot</mark>  [1]
217 |  * @return number of microseconds since underlying timer has been started
218 |  */
219 | <mark>int64_t</mark> esp_timer_get_time(void);  [2]
</pre>

1. Microsecunde de la pornirea plăcii.
2. 64 de biți: nu se resetează practic niciodată (~292 000 de ani).

### 22.3 `esp_timer_get_time` – implementare: un numărător hardware

Sursa: `IDF/esp_timer/src/esp_timer_impl_lac.c`

<pre>
 50 | #define COUNT_LO_REG    (<mark>TIMG_LACTLO_REG(LACT_MODULE)</mark>)  [1]
 51 | #define COUNT_HI_REG    (<mark>TIMG_LACTHI_REG(LACT_MODULE)</mark>)  [2]
 52 | #define UPDATE_REG      (<mark>TIMG_LACTUPDATE_REG(LACT_MODULE)</mark>)  [3]
    | ...
 93 | 
 94 | uint64_t IRAM_ATTR esp_timer_impl_get_counter_reg(void)
 95 | {
 96 |     uint32_t lo, hi;
 97 |     uint32_t lo_start = REG_READ(COUNT_LO_REG);
 98 |     uint32_t div = REG_GET_FIELD(CONFIG_REG, TIMG_LACT_DIVIDER);
 99 |     /* The peripheral doesn&#x27;t have a bit to indicate that the update is done, so we poll the
100 |      * lower 32 bit part of the counter until it changes, or a timeout expires.
101 |      */
102 |     <mark>REG_WRITE(UPDATE_REG, 1)</mark>;  [4]
103 |     do {
104 |         lo = <mark>REG_READ(COUNT_LO_REG)</mark>;  [5]
105 |     } while (lo == lo_start &amp;&amp; div-- &gt; 0);
106 | 
107 |     /* Since this function is called without a critical section, verify that LO and HI
108 |      * registers are consistent. That is, if an interrupt happens between reading LO and
109 |      * HI registers, and esp_timer_impl_get_time is called from an ISR, then try to
110 |      * detect this by the change in LO register value, and re-read both registers.
111 |      */
112 |     do {
113 |         lo_start = lo;
114 |         hi = <mark>REG_READ(COUNT_HI_REG)</mark>;  [6]
115 |         lo = REG_READ(COUNT_LO_REG);
116 |     } while (lo != lo_start);
117 | 
118 |     timer_64b_reg_t result = {
119 |         .lo = lo,
120 |         .hi = hi
121 |     };
122 |     return result.val;
123 | }
124 | 
125 | int64_t IRAM_ATTR esp_timer_impl_get_time(void)
126 | {
127 |     return esp_timer_impl_get_counter_reg() <mark>/ LACT_TICKS_PER_US</mark>;  [7]
128 | }
129 | 
130 | int64_t esp_timer_get_time(void) __attribute__((<mark>alias(&quot;esp_timer_impl_get_time&quot;)</mark>));  [8]
</pre>

1. Registrul cu cei 32 de biți de jos ai numărătorului.
2. Registrul cu cei 32 de biți de sus.
3. Scrierea aici copiază numărătorul în registrele LO/HI.
4. Cere o copie nouă a numărătorului.
5. Citește partea de jos până când se schimbă: copia este gata.
6. Citește partea de sus. Bucla verifică dacă LO nu s-a schimbat între timp.
7. Numărătorul crește de 2 ori pe µs. Împărțit la 2 = microsecunde.
8. `esp_timer_get_time` este doar alt nume pentru funcția de deasupra.

### 22.4 Adresa registrelor

Sursa: `IDF/soc/esp32/include/soc/timer_group_reg.h`

<pre>
 34 | #define REG_TIMG_BASE(i)       (<mark>DR_REG_TIMERGROUP0_BASE + i*0x1000</mark>)  [1]
    | ...
485 | #define TIMG_LACTLO_REG(i)          (REG_TIMG_BASE(i) <mark>+ 0x0078</mark>)  [2]
    | ...
493 | #define TIMG_LACTHI_REG(i)          (REG_TIMG_BASE(i) <mark>+ 0x007c</mark>)  [3]
</pre>

1. Timer Group 0 începe la `0x3FF5F000` (`reg_base.h:43`). `LACT_MODULE = 0`.
2. LO = `0x3FF5F078`.
3. HI = `0x3FF5F07C`.

### 22.5 `average()` și prima linie: `CSI/s` și RSSI

Sursa: `pas_cu_pas/main/main.c`

<pre>
28 | // media pe sub-frecventa k, in secunda curenta
29 | static float <mark>average(int k)</mark> {  [1]
30 |     return <mark>amplitude_total[k + 26] / packets</mark>;  [2]
31 | }
   | ...
45 |         ESP_LOGI(TAG, &quot;<mark>%3d CSI/s</mark>  rssi=%4d&quot;, packets, <mark>rssi_total / packets</mark>);  [3] [4]
</pre>

1. Media amplitudinii pe sub-frecvența k în secunda curentă.
2. Suma / numărul de cadre. `packets` este mereu ≥ 1 aici.
3. Câte CSI în ultima secundă, pe 3 caractere.
4. RSSI mediu. Împărțire întreagă: zecimalele se pierd.

### 22.6 A doua linie: `A_medie` și 4 sub-frecvențe

Sursa: `pas_cu_pas/main/main.c`

<pre>
46 |         <mark>float all = 0</mark>;  [1]
47 |         for (int k = -26; k &lt;= 26; k++) <mark>if (k != 0 &amp;&amp; k != 1)</mark> all += average(k);  [2]
48 |         ESP_LOGI(TAG, &quot;A_medie=%5.1f  A[-20]=%5.1f A[-7]=%5.1f A[+7]=%5.1f A[+20]=%5.1f&quot;,
49 |                  <mark>all / 51</mark>, <mark>average(-20), average(-7), average(7), average(20)</mark>);  [3] [4]
</pre>

1. Suma mediilor pe cele 51 de sub-frecvențe.
2. Aceleași 51 de sub-frecvențe ca în suma din `on_csi`.
3. `A_medie`: o singură valoare pentru tot canalul.
4. 4 sub-frecvențe: două la margini, două aproape de centru.

### 22.7 A treia linie: `SPEC`, apoi o secundă nouă

Sursa: `pas_cu_pas/main/main.c`

<pre>
50 |         <mark>printf(&quot;SPEC&quot;)</mark>;  [1]
51 |         for (int k = -26; k &lt;= 26; k++) if (k != 0 &amp;&amp; k != 1) printf(<mark>&quot; %.0f&quot;</mark>, average(k));  [2]
52 |         <mark>printf(&quot;\n&quot;)</mark>;  [3]
53 |         for (int k = 0; <mark>k &lt; 53</mark>; k++) amplitude_total[k] = 0;  [4]
54 |         <mark>packets = 0</mark>;  [5]
55 |         rssi_total = 0;
56 |         <mark>second_start_us = now</mark>;  [6]
57 |     }
</pre>

1. `printf`, nu `ESP_LOGI`: fără literă, timp și `TAG`. `grafic.py` caută liniile care încep cu `SPEC`.
2. Fiecare medie, fără zecimale, după un spațiu. 51 de numere.
3. Sfârșitul liniei.
4. Toate cele 53 de sume devin 0 (și pozițiile pentru k = 0 și +1, nefolosite).
5. Secunda nouă începe de la zero.
6. Momentul de început al secundei noi.

### 22.8 Rezultatul în jurnal

Sursa: `pas_cu_pas/output/07_main_nou.log`

<pre>
43 | I (1949) CSI:   <mark>1 CSI/s</mark>  rssi= -49  [1]
44 | I (1949) CSI: A_medie= 21.6  A[-20]=  9.5 A[-7]= 20.2 A[+7]= 28.8 A[+20]= 27.7
45 | SPEC 17 15 13 11 10 9 9 11 13 16 19 21 23 24 26 25 25 24 22 20 18 16 15 16 17 19 28 29 30 31 30 29 27 26 24 22 22 21 21 22 24 25 26 27 28 28 27 26 25 24 23
46 | I (2959) CSI:  <mark>51 CSI/s</mark>  rssi= -55  [2]
   | ...
49 | I (3959) CSI:  50 CSI/s  rssi= -64
50 | I (3959) CSI: A_medie= 22.2  <mark>A[-20]=  8.8</mark> A[-7]= 22.0 <mark>A[+7]= 31.1</mark> A[+20]= 28.4  [3] [4]
51 | <mark>SPEC 17 16 14</mark> 12 10 9 9 10 12 15 17 20 22 24 26 26 26 25 24 22 20 18 16 16 18 19 29 31 32 32 32 31 29 28 25 23 22 21 21 22 23 25 27 28 28 29 28 27 26 25 24  [5]
</pre>

1. Prima linie are un singur cadru (`second_start_us` era 0). O ignorăm.
2. Rata reală: 50–51 CSI/s, cât ping-uri trimitem.
3. Marginea din stânga: slabă.
4. Aproape de centru, dreapta: puternică. Forma spectrului = „amprenta” canalului.
5. Primele valori: k = −26, −25, −24, ... Ultimele: k = +24, +25, +26.

Linia 47 din jurnal are caractere greșite (`����`). Cablul USB a pierdut câțiva octeți. Placa a trimis textul corect. `grafic.py` ignoră liniile care nu au formatul așteptat.

---

## 23. De ce amplitudinea nu are unități fixe

### 23.1 Setările CSI implicite

Sursa: `IDF/esp_wifi/include/esp_wifi_types.h`

<pre>
574 |     bool lltf_en;           /**&lt; enable to receive legacy long training field(lltf) data. Default enabled */
575 |     bool htltf_en;          /**&lt; enable to receive HT long training field(htltf) data. Default enabled */
576 |     bool stbc_htltf2_en;    /**&lt; enable to receive space time block code HT long training field(stbc-htltf2) data. Default enabled */
577 |     bool ltf_merge_en;      /**&lt; enable to generate htlft data by averaging lltf and ht_ltf data when receiving HT packet. Otherwise, use ht_ltf data directly. Default enabled */
578 |     bool channel_filter_en; /**&lt; enable to turn on channel filter to <mark>smooth adjacent sub-carrier</mark>. Disable it to keep independence of adjacent sub-carrier. Default enabled */  [1]
579 |     bool manu_scale;        /**&lt; manually scale the CSI data by left shifting or <mark>automatically scale the CSI data</mark>. If set true, please set the shift bits. false: automatically. true: manually. <mark>Default false</mark> */  [2] [3]
580 |     uint8_t shift;          /**&lt; manually left shift bits of the scale of the CSI data. The range of the left shift bits is 0~15 */
581 |     bool dump_ack_en;       /**&lt; enable to dump 802.11 ACK frame, default disabled */
582 | } wifi_csi_config_t;
</pre>

1. Implicit, sub-frecvențele vecine sunt netezite.
2. Implicit, chipul scalează automat valorile CSI.
3. Noi nu apelăm `esp_wifi_set_csi_config`, deci scalarea automată este activă.

### 23.2 Unde ar ajunge `esp_wifi_set_csi_config`: `ic_csi_set_config`

Sursa: `libpp.a (objdump)`

Nu apelăm această funcție. O arătăm ca să vezi unde ajung setările CSI. Legătura octet → câmp este dedusă din ordinea câmpurilor din `wifi_csi_config_t`.

<pre>
   0:   <mark>3ff730f8</mark>  [1]
   4:   <mark>3ff730fc</mark>  [2]
   8:   dfffffff
        ...
                        c: R_XTENSA_32  phy_chan_dump_cfg
                        10: R_XTENSA_32 phy_chan_filt_set
  --
  14:   004136          entry   a1, 32
  17:   0202e2          l8ui    a14, <mark>a2, 2</mark>  [3]
  1a:   0102d2          l8ui    a13, <mark>a2, 1</mark>  [4]
  1d:   0002c2          l8ui    a12, <mark>a2, 0</mark>  [5]
  20:   0602b2          l8ui    a11, <mark>a2, 6</mark>  [6]
  23:   0502a2          l8ui    a10, <mark>a2, 5</mark>  [7]
  26:   fff981          l32r    a8, c &lt;ic_csi_set_config-0x8&gt; (0 &lt;ic_csi_set_config-0x14&gt;)
                        26: R_XTENSA_ASM_EXPAND <mark>phy_chan_dump_cfg</mark>  [8]
  29:   0008e0          callx8  a8
  2c:   0302b2          l8ui    a11, <mark>a2, 3</mark>  [9]
  2f:   0402a2          l8ui    a10, <mark>a2, 4</mark>  [10]
  32:   fff781          l32r    a8, 10 &lt;ic_csi_set_config-0x4&gt; (0 &lt;ic_csi_set_config-0x14&gt;)
                        32: R_XTENSA_ASM_EXPAND <mark>phy_chan_filt_set</mark>  [11]
  35:   0008e0          callx8  a8
  38:   070282          l8ui    a8, <mark>a2, 7</mark>  [12]
  3b:   fff121          l32r    a2, 0 &lt;ic_csi_set_config-0x14&gt; (3ff730f8 &lt;ic_set_vif+0x3ff73090&gt;)
  3e:   68ac            beqz.n  a8, 68 &lt;ic_csi_set_config+0x54&gt;
  40:   180c            movi.n  a8, 1
  42:   018830          <mark>slli    a8, a8, 29</mark>  [13]
  45:   0020c0          memw
  48:   0298            l32i.n  a9, a2, 0
  4a:   209980          or      a9, a9, a8
  4d:   0020c0          memw
  50:   0299            s32i.n  a9, a2, 0
  52:   ffec91          l32r    a9, 4 &lt;ic_csi_set_config-0x10&gt; (3ff730fc &lt;ic_set_vif+0x3ff73094&gt;)
  55:   0020c0          memw
  58:   0928            l32i.n  a2, a9, 0
  5a:   202280          or      a2, a2, a8
  5d:   0020c0          memw
  60:   0929            s32i.n  a2, a9, 0
  62:   0020c0          memw
  65:   0007c6          j       88 &lt;ic_csi_set_config+0x74&gt;
  68:   0020c0          memw
  6b:   0288            l32i.n  a8, a2, 0
  6d:   ffe691          l32r    a9, 8 &lt;ic_csi_set_config-0xc&gt; (dfffffff &lt;ic_set_vif+0xdfffff97&gt;)
  70:   108890          and     a8, a8, a9
  73:   0020c0          memw
  76:   0289            s32i.n  a8, a2, 0
  78:   ffe381          l32r    a8, 4 &lt;ic_csi_set_config-0x10&gt; (3ff730fc &lt;ic_set_vif+0x3ff73094&gt;)
  7b:   0020c0          memw
  7e:   0828            l32i.n  a2, a8, 0
  80:   102290          and     a2, a2, a9
  83:   0020c0          memw
  86:   0829            s32i.n  a2, a8, 0
  88:   020c            movi.n  a2, 0
  8a:   0020c0          memw
  8d:   f01d            retw.n
</pre>

1. Primul registru de configurare CSI.
2. Al doilea registru de configurare CSI.
3. Octetul 2 din config = `stbc_htltf2_en`.
4. Octetul 1 = `htltf_en`.
5. Octetul 0 = `lltf_en`.
6. Octetul 6 = `shift`.
7. Octetul 5 = `manu_scale`.
8. Radioul (`libphy.a`) primește ce LTF-uri salvează și cum scalează valorile.
9. Octetul 3 = `ltf_merge_en`.
10. Octetul 4 = `channel_filter_en`.
11. Filtrul de canal se setează în radio.
12. Octetul 7 = `dump_ack_en`.
13. `dump_ack_en` controlează bitul 29, în ambii regiștri.

**Concluzie:** chipul are control automat al amplificării (AGC) și scalează CSI automat. Când semnalul scade, chipul amplifică mai mult. Deci:

- Nu compara `A_medie` între momente diferite.
- Compară RSSI (este calibrat, în dBm).
- Compară **forma** spectrului, de exemplu `A[-20] / A[+20]`. Scalarea comună se anulează în raport.

---

## 24. Rezumat

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
