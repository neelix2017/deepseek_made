import socketserver
import dnslib
import socket
import re
# Google's DNS server for fallback
GOOGLE_DNS = "8.8.8.8"
GOOGLE_DNS_PORT = 53
PRINT_LOG = False







# Local DNS mappings (custom domain to IP mappings)
LOCAL_DNS_MAPPINGS = {
    "v720.naxclow.com.": "192.168.0.111",  # Map example.local to a local IP
    "v720.p2p.naxclow.com.": "127.0.0.1",          # Map test.local to another local IP
    "googleadservices.com.":"127.0.0.1",
    "ads.*.":"127.0.0.1"
}






















def match(query, pattern):
    return re.match(pattern, query) is not None


class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global PRINT_LOG
        # Unpack the request into query data and client socket
        query_data, client_socket = self.request
        request = dnslib.DNSRecord.parse(query_data)

        # Log the incoming query
        query_name = str(request.q.qname)
        if PRINT_LOG:print(f"Incoming DNS query: {query_name}")

        # Check if the query is in the local DNS mappings
        _l = list(filter(lambda v: match(query_name, v), LOCAL_DNS_MAPPINGS))
        if (len(_l)>0):
            # Create a response with the local IP address
            response = request.reply()
            response.add_answer(
                dnslib.RR(
                    rname=query_name,
                    rtype=dnslib.QTYPE.A,
                    rclass=dnslib.CLASS.IN,
                    ttl=300,  # Time-to-live in seconds
                    rdata=dnslib.A(LOCAL_DNS_MAPPINGS[_l[0]]),
                )
            )
            if PRINT_LOG:print(f"Resolved locally: {query_name} -> {LOCAL_DNS_MAPPINGS[_l[0]]}")
        else:
            # Forward the query to Google DNS
            try:
                # Create a UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(query_data, (GOOGLE_DNS, GOOGLE_DNS_PORT))
                google_response, _ = sock.recvfrom(1024)
                sock.close()

                # Parse Google's response
                google_response_record = dnslib.DNSRecord.parse(google_response)
                if PRINT_LOG:print(f"Forwarded to Google DNS: {query_name}")
                response = google_response_record
            except Exception as e:
                if PRINT_LOG:print(f"Error forwarding to Google DNS: {e}")
                # If there's an error, send a SERVFAIL response
                response = request.reply()
                response.header.rcode = dnslib.RCODE.SERVFAIL

        # Send the response back to the client
        client_socket.sendto(response.pack(), self.client_address)

if __name__ == "__main__":
    # Define the DNS server address and port
    HOST, PORT = "0.0.0.0", 53

    # Create the DNS server
    with socketserver.UDPServer((HOST, PORT), DNSHandler) as server:
        print(f"Local DNS server started on {HOST}:{PORT}")
        print(f"Local mappings: {LOCAL_DNS_MAPPINGS}")
        server.serve_forever()
