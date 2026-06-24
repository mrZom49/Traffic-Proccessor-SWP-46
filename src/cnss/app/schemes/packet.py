from pydantic import BaseModel


class Packet(BaseModel):
    timestamp: str
    total_packets: int
    total_bytes: int
    packets_per_second: float
    bytes_per_second: float
    tcp_packets: int
    udp_packets: int
    icmp_packets: int
    other_packets: int
    status: str
