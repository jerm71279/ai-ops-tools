#!/usr/bin/env python3
"""
Subnet Allocation Helper for Customer Network Registry

Manages the allocation of 10.54.x.x/24 subnet blocks to customers.
Each customer receives 4 consecutive /24 subnets in the registry,
but only the first /24 is configured on their MikroTik router.

Allocation Pattern:
- Customer 1: 10.54.0.0/24 - 10.54.3.0/24 (configure: 10.54.0.0/24)
- Customer 2: 10.54.4.0/24 - 10.54.7.0/24 (configure: 10.54.4.0/24)
- Customer 3: 10.54.8.0/24 - 10.54.11.0/24 (configure: 10.54.8.0/24)
- etc.
"""

import csv
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import ipaddress


class SubnetAllocator:
    """Manages subnet allocation for customer deployments"""

    # Constants for allocation scheme
    BASE_NETWORK = "10.54.0.0"
    BLOCK_SIZE = 4  # Number of /24 subnets per customer block

    def __init__(self, registry_path: str = "CUSTOMER_SUBNET_TRACKER.csv"):
        """Initialize the subnet allocator

        Args:
            registry_path: Path to the CSV registry file
        """
        self.registry_path = Path(registry_path)

    def get_allocated_blocks(self) -> List[Tuple[int, int]]:
        """Get list of already allocated subnet blocks

        Returns:
            List of tuples (start_third_octet, end_third_octet)
        """
        allocated = []

        if not self.registry_path.exists():
            return allocated

        with open(self.registry_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                block = row.get('Allocated Subnet Block', '')
                if block and '-' in block:
                    # Parse "10.54.0.0/24 - 10.54.3.0/24"
                    start, end = block.split(' - ')
                    start_octets = start.split('/')[ 0].split('.')
                    end_octets = end.split('/')[0].split('.')

                    start_third = int(start_octets[2])
                    end_third = int(end_octets[2])

                    allocated.append((start_third, end_third))

        return sorted(allocated)

    def get_next_available_block(self) -> Tuple[str, str, str]:
        """Get the next available subnet block for allocation

        Returns:
            Tuple of (block_range, configured_subnet, gateway_ip)
            Example: ("10.54.4.0/24 - 10.54.7.0/24", "10.54.4.0/24", "10.54.4.1")
        """
        allocated_blocks = self.get_allocated_blocks()

        # Find the next available starting octet
        if not allocated_blocks:
            # First customer
            next_start = 0
        else:
            # Get the highest ending octet and add 1
            last_end = max(end for _, end in allocated_blocks)
            next_start = last_end + 1

        # Calculate the block range
        block_start = next_start
        block_end = next_start + self.BLOCK_SIZE - 1

        # Validate we haven't exceeded the /16 space (0-255 for third octet)
        if block_end > 255:
            raise ValueError(f"Subnet exhaustion: Cannot allocate block starting at 10.54.{next_start}.0/24")

        # Format the results
        block_range = f"10.54.{block_start}.0/24 - 10.54.{block_end}.0/24"
        configured_subnet = f"10.54.{block_start}.0/24"
        gateway_ip = f"10.54.{block_start}.1"
        dhcp_start = f"10.54.{block_start}.100"
        dhcp_end = f"10.54.{block_start}.200"

        return block_range, configured_subnet, gateway_ip, dhcp_start, dhcp_end

    def allocate_block(self, customer_id: str, customer_name: str,
                      wan_ip: str, wan_gateway: str, location: str,
                      circuit_id: str, notes: str = "") -> dict:
        """Allocate a new subnet block for a customer

        Args:
            customer_id: Customer ID
            customer_name: Customer name
            wan_ip: WAN IP address with CIDR (e.g., "142.190.216.66/30")
            wan_gateway: WAN gateway IP
            location: Physical location
            circuit_id: Circuit ID
            notes: Additional notes

        Returns:
            Dictionary with allocation details
        """
        from datetime import date

        # Get next available block
        block_range, configured_subnet, gateway_ip, dhcp_start, dhcp_end = self.get_next_available_block()

        # Format DHCP range
        dhcp_range = f"{dhcp_start}-{dhcp_end.split('.')[-1]}"

        # Create the allocation record
        allocation = {
            'customer_id': customer_id,
            'customer_name': customer_name,
            'allocated_block': block_range,
            'configured_subnet': configured_subnet,
            'gateway': gateway_ip,
            'dhcp_range': dhcp_range,
            'wan_ip': wan_ip,
            'wan_gateway': wan_gateway,
            'location': location,
            'circuit_id': circuit_id,
            'date_assigned': str(date.today()),
            'status': 'Active',
            'notes': notes or f"4x /24 block allocation, configured: {configured_subnet}"
        }

        # Add to registry
        self._add_to_registry(allocation)

        return allocation

    def _add_to_registry(self, allocation: dict):
        """Add allocation to the CSV registry

        Args:
            allocation: Dictionary with allocation details
        """
        # Ensure file exists with headers
        if not self.registry_path.exists():
            with open(self.registry_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Customer ID', 'Customer Name', 'Allocated Subnet Block',
                    'Configured LAN Subnet', 'LAN Gateway', 'DHCP Range',
                    'WAN IP', 'WAN Gateway', 'Location', 'Circuit ID',
                    'Date Assigned', 'Status', 'Notes'
                ])

        # Append the new allocation
        with open(self.registry_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                allocation['customer_id'],
                allocation['customer_name'],
                allocation['allocated_block'],
                allocation['configured_subnet'],
                allocation['gateway'],
                allocation['dhcp_range'],
                allocation['wan_ip'],
                allocation['wan_gateway'],
                allocation['location'],
                allocation['circuit_id'],
                allocation['date_assigned'],
                allocation['status'],
                allocation['notes']
            ])

    def show_allocation_summary(self):
        """Display summary of current allocations"""
        allocated = self.get_allocated_blocks()

        print("=" * 80)
        print("CUSTOMER SUBNET ALLOCATION SUMMARY")
        print("=" * 80)
        print(f"Base Network: {self.BASE_NETWORK}/16")
        print(f"Block Size: {self.BLOCK_SIZE} x /24 subnets per customer")
        print(f"Total Allocated Blocks: {len(allocated)}")
        print()

        if allocated:
            print("Allocated Ranges:")
            for start, end in allocated:
                print(f"  • 10.54.{start}.0/24 - 10.54.{end}.0/24")
            print()

        try:
            next_block = self.get_next_available_block()
            print(f"Next Available Block: {next_block[0]}")
            print(f"  Configured Subnet: {next_block[1]}")
            print(f"  Gateway: {next_block[2]}")
            print(f"  DHCP Range: {next_block[3]}-{next_block[4].split('.')[-1]}")
        except ValueError as e:
            print(f"⚠️  {e}")

        print("=" * 80)


def main():
    """CLI interface for subnet allocator"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Subnet Allocation Helper for Customer Networks"
    )
    parser.add_argument(
        'command',
        choices=['next', 'allocate', 'summary'],
        help='Command to execute'
    )
    parser.add_argument('--customer-id', help='Customer ID')
    parser.add_argument('--customer-name', help='Customer name')
    parser.add_argument('--wan-ip', help='WAN IP with CIDR (e.g., 1.2.3.4/30)')
    parser.add_argument('--wan-gateway', help='WAN gateway IP')
    parser.add_argument('--location', help='Physical location')
    parser.add_argument('--circuit-id', help='Circuit ID')
    parser.add_argument('--notes', help='Additional notes', default='')
    parser.add_argument(
        '--registry',
        default='CUSTOMER_SUBNET_TRACKER.csv',
        help='Path to registry CSV file'
    )

    args = parser.parse_args()

    allocator = SubnetAllocator(args.registry)

    if args.command == 'summary':
        allocator.show_allocation_summary()

    elif args.command == 'next':
        try:
            block_range, subnet, gateway, dhcp_start, dhcp_end = allocator.get_next_available_block()
            print("Next Available Allocation:")
            print(f"  Block Range: {block_range}")
            print(f"  Configured Subnet: {subnet}")
            print(f"  Gateway: {gateway}")
            print(f"  DHCP Range: {dhcp_start}-{dhcp_end.split('.')[-1]}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == 'allocate':
        # Validate required arguments
        required = ['customer_id', 'customer_name', 'wan_ip', 'wan_gateway',
                   'location', 'circuit_id']
        missing = [arg for arg in required if not getattr(args, arg.replace('-', '_'))]

        if missing:
            print(f"Error: Missing required arguments: {', '.join(missing)}")
            sys.exit(1)

        try:
            allocation = allocator.allocate_block(
                customer_id=args.customer_id,
                customer_name=args.customer_name,
                wan_ip=args.wan_ip,
                wan_gateway=args.wan_gateway,
                location=args.location,
                circuit_id=args.circuit_id,
                notes=args.notes
            )

            print("✅ Subnet Block Allocated Successfully!")
            print()
            print(f"Customer: {allocation['customer_name']} (ID: {allocation['customer_id']})")
            print(f"Allocated Block: {allocation['allocated_block']}")
            print(f"Configured Subnet: {allocation['configured_subnet']}")
            print(f"Gateway: {allocation['gateway']}")
            print(f"DHCP Range: {allocation['dhcp_range']}")
            print()
            print(f"Registry updated: {args.registry}")

        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
