from dhanhq import dhanhq
import time

from dhanhq import dhanhq
import time

client_id = '1101888504'
access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzM3ODY2NDU0LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMTg4ODUwNCJ9.0LojGRMn5H6x_JGGwpdFcChYhHnvC-Th71dwJ0WY9FqYkV1XAXGZupOjsD0dK-Ih8PEmK1vu0e7zxr07RaGh4g'

other_dhan_accounts = [
	('1103819003', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzM3ODY2NTI1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzgxOTAwMyJ9.tX5b_DxHBqLmtBVfTGaTdwSJsb-a_8qyV0HHSZPoND6DDUCLpaPh3w4ZL4GFFQqzAjF8q5kpPQItc-UVjbM9Bg'),
  ('1104769064', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzM3MjkzODcyLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNDc2OTA2NCJ9.0KLIXpeWVdl8SiRBhlcyTOeinDGk62ukEopOKUWXBesBxedgF0c0kk6h1Acay4ASDwfbOxl2NVULY0JnEcRi5g'),
]

main_dhan = dhanhq(client_id, access_token)

def copy_order(order_details, multiplier, dhan_client):
    """Copies the order to another Dhan account with a quantity multiplier."""
    try:
        if 'quantity' in order_details:
            new_qty = int(order_details['quantity'] * multiplier)
            order_details['quantity'] = new_qty

        # Ensure required fields exist
        required_fields = ['symbol', 'transactionType', 'price', 'orderType', 'quantity']
        for field in required_fields:
            if field not in order_details:
                raise ValueError(f"Missing required field: {field}")

        # Place the order
        response = dhan_client.place_order(**order_details)
        print(f"Order placed on other account: {response}")
    except Exception as e:
        print(f"Error placing order on other account: {e}")

def monitor_orders():
    """Monitor changes in order book and copy orders."""
    while True:
        try:
            orders = main_dhan.get_order_list()
            for order in orders:
                if isinstance(order, dict) and 'status' in order:
                    if order['status'] == 'modified':
                        print(f"Order Modified: {order}")
                        for client_id, access_token in other_dhan_accounts:
                            other_dhan = dhanhq(client_id, access_token)
                            copy_order(order, 2, other_dhan)
                    elif order['status'] == 'cancelled':
                        print(f"Order Cancelled: {order}")
                    elif order['status'] == 'placed':
                        print(f"Order Placed: {order}")
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(5)  # Adjust polling interval as needed

if __name__ == "__main__":
    try:
        monitor_orders()
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
