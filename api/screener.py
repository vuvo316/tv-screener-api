from http.server import BaseHTTPRequestHandler
from tradingview_screener import Query, Column
import json

# Vercel requires a class inheriting from BaseHTTPRequestHandler or an ASGI/WSGI app


class handler(BaseHTTPRequestHandler):

    # This function handles all GET requests to the webhook URL
    def do_GET(self):

        # --- Stock Filtering Logic ---
        try:
            # Example Query: Top 50 Stocks by Volume > 1M and Change > 5%
            n_rows, df = (Query()
                          .select('ticker', 'name', 'close', 'volume', 'change', 'relative_volume_10d_calc')
                          .where(
                Column('change') > 5,
                Column('volume') > 1000000
            )
                .order_by('volume', ascending=False)
                .limit(50)
                .get_scanner_data())

            # Convert the DataFrame to a list of dictionaries (JSON format)
            stock_list = df.to_dict('records')
            response_body = json.dumps(stock_list, indent=2)

            # --- Send the HTTP Response ---
            self.send_response(200)  # Success status code
            self.send_header('Content-Type', 'application/json')
            # IMPORTANT: Allows cross-origin calls (like from Opal)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_body.encode('utf-8'))

        except Exception as e:
            # Send a 500 error response if the script fails
            error_message = {"error": f"An error occurred: {e}"}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_message).encode('utf-8'))
