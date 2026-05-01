# umqttsimple.py - Reliable version (from community + fixes)
import usocket as socket
import ustruct as struct
from ubinascii import hexlify
from utime import sleep_ms, ticks_ms, ticks_diff

class MQTTClient:

    def __init__(self, client_id, server, port=1883, user=None, password=None, keepalive=60):
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.keepalive = keepalive
        self.pid = 0
        self.last_ping = ticks_ms()

    def _send(self, data):
        self.sock.send(data)

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect(socket.getaddrinfo(self.server, self.port)[0][-1])

        # Proper MQTT Connect Packet
        protocol_name = b"MQTT"
        connect_flags = 0x02  # Clean Session
        keepalive = self.keepalive

        packet = bytearray([0x10, 0x00])  # Fixed header

        # Variable header
        packet.extend(struct.pack("!H", len(protocol_name)))
        packet.extend(protocol_name)
        packet.extend(b"\x04")            # Protocol level 4 (MQTT 3.1.1)
        packet.extend([connect_flags])
        packet.extend(struct.pack("!H", keepalive))

        # Payload - Client ID
        packet.extend(struct.pack("!H", len(self.client_id)))
        packet.extend(self.client_id.encode())

        # Update length
        packet[1] = len(packet) - 2

        self._send(packet)
        self.last_ping = ticks_ms()
        print("MQTT Connected to", self.server)
        return True

    def publish(self, topic, msg, retain=False, qos=0):
        self._ping()
        topic = topic.encode('utf-8')
        msg = msg.encode('utf-8') if isinstance(msg, str) else msg

        header = 0x30 | (qos << 1) | (1 if retain else 0)
        packet = bytearray([header, 0x00])

        packet.extend(struct.pack("!H", len(topic)))
        packet.extend(topic)
        packet.extend(msg)

        packet[1] = len(packet) - 2
        self._send(packet)
        print("Published to", topic, ":", msg)

    def _ping(self):
        if ticks_diff(ticks_ms(), self.last_ping) > (self.keepalive * 1000) // 2:
            self.sock.send(b"\xc0\x00")   # PINGREQ
            self.last_ping = ticks_ms()
