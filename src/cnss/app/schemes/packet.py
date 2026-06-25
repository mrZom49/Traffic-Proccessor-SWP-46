from pydantic import BaseModel


class Packet(BaseModel):
    timestamp: str
    total_packets: int = 0
    total_bytes: int = 0
    incoming_packets: int = 0
    outgoing_packets: int = 0
    incoming_bytes: int = 0
    outgoing_bytes: int = 0
    packets_per_second: float
    bytes_per_second: float
    tcp_packets: int
    udp_packets: int
    icmp_packets: int
    other_packets: int
    status: str
