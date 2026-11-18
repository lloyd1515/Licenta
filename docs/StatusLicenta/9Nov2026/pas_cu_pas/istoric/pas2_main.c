// Pasul 2: placa se conecteaza la hotspot si afiseaza de la cine vine fiecare CSI
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"   // nou: stiva IP (adresa IP, DHCP)
#include "esp_log.h"
#include "esp_mac.h"     // nou: MACSTR si MAC2STR, pentru afisarea unei adrese MAC
#include "nvs_flash.h"

static const char *TAG = "PAS2";
static int count = 0;

// Driverul Wi-Fi apeleaza aceasta functie la fiecare cadru primit
static void on_csi(void *ctx, wifi_csi_info_t *info) {
    if (count < 20) {
        // nou: info->mac = cei 6 octeti ai adresei MAC a celui care a trimis cadrul
        // MACSTR = sablonul "%02x:%02x:...", MAC2STR = cei 6 octeti, pe rand
        ESP_LOGI(TAG, "CSI #%d  len=%u  rssi=%d  de la " MACSTR,
                 count, info->len, info->rx_ctrl.rssi, MAC2STR(info->mac));
    }
    count++;
}

// nou: driverul anunta aici evenimentele: "am pornit", "m-am deconectat", "am primit IP"
//   arg  = pointerul dat la inregistrare (aici NULL, nu il folosim)
//   base = familia evenimentului: WIFI_EVENT (radio) sau IP_EVENT (retea IP)
//   id   = evenimentul exact din familie, de exemplu WIFI_EVENT_STA_START
//   data = detaliile evenimentului; tipul depinde de id (pentru GOT_IP: ip_event_got_ip_t)
static void on_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    // STA_START: radioul a pornit. STA_DISCONNECTED: placa a pierdut reteaua.
    // In ambele cazuri cerem conectarea (din nou).
    if (base == WIFI_EVENT && (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)) {
        esp_wifi_connect();  // porneste auth -> assoc -> run; rezultatul vine tot ca eveniment
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        // got = detaliile evenimentului GOT_IP
        //   got->ip_info.ip = adresa IP a placii (data de DHCP)
        //   got->ip_info.gw = gateway-ul, adica adresa telefonului
        ip_event_got_ip_t *got = data;
        // IPSTR = sablonul "%d.%d.%d.%d", IP2STR = cele 4 numere ale adresei
        ESP_LOGI(TAG, "Conectat. IP " IPSTR ", gateway " IPSTR, IP2STR(&got->ip_info.ip), IP2STR(&got->ip_info.gw));
    }
}

void app_main(void) {
    // 1. Pornim Wi-Fi-ul si reteaua IP
    // nou: ESP_ERROR_CHECK(x) = daca x nu intoarce ESP_OK, afiseaza eroarea si reporneste placa
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());           // nou: porneste stiva TCP/IP (lwIP)
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();         // nou: leaga Wi-Fi-ul de stiva IP si porneste clientul DHCP
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    // nou: esp_event_handler_register(familie, eveniment, functie, arg)
    //   familie   = WIFI_EVENT sau IP_EVENT
    //   eveniment = un id anume, sau ESP_EVENT_ANY_ID pentru toate din familie
    //   functie   = on_event, apelata la fiecare eveniment ales
    //   arg       = pointer trimis neschimbat catre on_event (aici NULL)
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_event, NULL));

    // 2. Ne conectam la hotspot (fara mod promiscuu)
    // nou: sta = setarile de statie: numele retelei (ssid) si parola
    //   valorile vin din Kconfig.projbuild; cele reale sunt in ~/esp/csi-node/wifi.defaults
    wifi_config_t sta = {.sta = {.ssid = CONFIG_CSI_WIFI_SSID, .password = CONFIG_CSI_WIFI_PASSWORD}};
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    // nou: esp_wifi_set_config(interfata, setari)
    //   interfata = WIFI_IF_STA (placa este client); WIFI_IF_AP ar fi punct de acces
    //   setari    = &sta, adresa structurii de mai sus
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta));
    ESP_ERROR_CHECK(esp_wifi_start());           // trimite evenimentul WIFI_EVENT_STA_START

    // 3. Cerem CSI: inregistram on_csi, apoi pornim masurarea
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(on_csi, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
}
