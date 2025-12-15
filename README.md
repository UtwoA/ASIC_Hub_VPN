# ASIC Hub VPN

**ASIC Hub VPN** — это веб-интерфейс для управления вашими RPi и ASIC через WireGuard VPN. Проект позволяет централизованно отслеживать состояние ваших устройств (Online/Offline) и переходить на их страницы через единый хаб, доступный только по VPN.

---

## Особенности

- Централизованный веб-хаб для всех ASIC и RPi
- Индикаторы Online/Offline для каждого устройства
- Доступ только через VPN (WireGuard)
- Автозапуск через Docker и Docker Compose
- Простое масштабирование на любое количество устройств

---

## Структура проекта

```
/asic_hub/
├── app.py             # Flask-приложение
├── Dockerfile         # Docker образ
├── docker-compose.yml # Поднятие сервиса
├── requirements.txt   # Python зависимости
└── .env               # Переменные окружения (VPS_IP)
```

---

## Установка и развёртывание

### 1. Установка WireGuard на VPS

```bash
apt update
apt install -y wireguard iptables-persistent
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-wireguard.conf
sysctl --system
```

### 2. Настройка WireGuard сервера

Создайте файл `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address = 10.50.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>

# RPi1
[Peer]
PublicKey = <RPI1_PUBLIC_KEY>
AllowedIPs = 10.50.0.10/32

# RPi2
[Peer]
PublicKey = <RPI2_PUBLIC_KEY>
AllowedIPs = 10.50.0.11/32
```

Запуск сервиса:

```bash
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
wg show
```

### 3. Настройка RPi

На каждой RPi создаём `/etc/wireguard/wg0.conf`:

```ini
[Interface]
PrivateKey = <RPI_PRIVATE_KEY>
Address = 10.50.0.10/32
MTU = 1420

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <VPS_PUBLIC_IP>:51820
AllowedIPs = 10.50.0.0/24
PersistentKeepalive = 25
```

Запуск:

```bash
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
```

Проверка соединения:

```bash
ping 10.50.0.10  # с VPS
ping 10.50.0.1   # с RPi
```

---

### 4. Развёртывание ASIC Hub через Docker

1. Клонируем репозиторий:

```bash
git clone <URL_репозитория> /opt/asic_hub
cd /opt/asic_hub
```

2. Создаём `.env`:

```
VPS_IP=10.50.0.1
```

3. Собираем и запускаем контейнер:

```bash
docker-compose build
docker-compose up -d
```

4. Открываем веб-интерфейс в браузере:

```
http://10.50.0.1:5000
```

---

## Настройка устройств в Hub

Список ASIC/RPi настраивается в `app.py`:

```python
devices = [
    {"name": "RPi1 ASIC100", "url": f"http://{VPS_IP}:18081"},
    {"name": "RPi1 ASIC101", "url": f"http://{VPS_IP}:18080"},
    {"name": "RPi2 ASIC100", "url": f"http://{VPS_IP}:28080"},
    {"name": "RPi2 ASIC101", "url": f"http://{VPS_IP}:28081"},
    {"name": "RPi2 ASIC102", "url": f"http://{VPS_IP}:28082"},
    {"name": "RPi2 ASIC104", "url": f"http://{VPS_IP}:28083"},
]
```

Каждый ASIC отображается с **бейджиком Online/Offline**, автоматически обновляемым при загрузке страницы.

---

## Примечания

- Контейнер автоматически перезапускается после рестарта VPS (`restart: unless-stopped`)
- Можно масштабировать, добавляя новые устройства в список `devices`
- Для публичного доступа через интернет рекомендуется использовать **Nginx/Traefik + HTTPS**

---

## Лицензия

MIT License
