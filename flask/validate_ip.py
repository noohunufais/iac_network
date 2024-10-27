import ipaddress

def check_ip(ip:str) -> bool:
	try:
		ipaddress.ip_address(ip)
		return True 
	except Exception as e:
		return False
	
